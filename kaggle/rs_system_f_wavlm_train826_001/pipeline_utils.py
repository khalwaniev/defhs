import torch
import torch.nn as nn
import torch.nn.functional as F
from transformers import AutoModel
from transformers.modeling_utils import PreTrainedModel ,PretrainedConfig


class Pooling(nn.Module):
    def __init__(self):
        super().__init__()
    def compute_length_from_mask(self, mask):
        """
        mask: (batch_size, T)
        Assuming that the sampling rate is 16kHz, the frame shift is 20ms
        """
        wav_lens = torch.sum(mask, dim=1) # (batch_size, )
        feat_lens = torch.div(wav_lens-1, 16000*0.02, rounding_mode="floor") + 1
        feat_lens = feat_lens.int().tolist()
        return feat_lens
        
    def forward(self, x, mask):
        raise NotImplementedError
    
class MeanPooling(Pooling):
    def __init__(self):
        super().__init__()
    def forward(self, xs, mask):
        """
        xs: (batch_size, T, feat_dim)
        mask: (batch_size, T)

        => output: (batch_size, feat_dim)
        """
        feat_lens = self.compute_length_from_mask(mask)
        pooled_list = []
        for x, feat_len in zip(xs, feat_lens):
            pooled = torch.mean(x[:feat_len], dim=0) # (feat_dim, )
            pooled_list.append(pooled)
        pooled = torch.stack(pooled_list, dim=0) # (batch_size, feat_dim)
        return pooled
    

class AttentiveStatisticsPooling(Pooling):
    """
    AttentiveStatisticsPooling
    Paper: Attentive Statistics Pooling for Deep Speaker Embedding
    Link: https://arxiv.org/pdf/1803.10963.pdf
    """
    def __init__(self, input_size):
        super().__init__()
        self._indim = input_size
        self.sap_linear = nn.Linear(input_size, input_size)
        self.attention = nn.Parameter(torch.FloatTensor(input_size, 1))
        torch.nn.init.normal_(self.attention, mean=0, std=1)

    def forward(self, xs, mask):
        """
        xs: (batch_size, T, feat_dim)
        mask: (batch_size, T)

        => output: (batch_size, feat_dim*2)
        """
        feat_lens = self.compute_length_from_mask(mask)
        pooled_list = []
        for x, feat_len in zip(xs, feat_lens):
            x = x[:feat_len].unsqueeze(0)
            h = torch.tanh(self.sap_linear(x))
            w = torch.matmul(h, self.attention).squeeze(dim=2)
            w = F.softmax(w, dim=1).view(x.size(0), x.size(1), 1)
            mu = torch.sum(x * w, dim=1)
            rh = torch.sqrt((torch.sum((x**2) * w, dim=1) - mu**2).clamp(min=1e-5))
            x = torch.cat((mu, rh), 1).squeeze(0)
            pooled_list.append(x)
        return torch.stack(pooled_list)



    
class EmotionRegression(nn.Module):
    def __init__(self, *args, **kwargs):
        super(EmotionRegression, self).__init__()
        input_dim = args[0]
        hidden_dim = args[1]
        num_layers = args[2]
        output_dim = args[3]
        p = kwargs.get("dropout", 0.5)

        self.fc=nn.ModuleList([
            nn.Sequential(
                nn.Linear(input_dim, hidden_dim), nn.LayerNorm(hidden_dim), nn.ReLU(), nn.Dropout(p)
            )
        ])
        for lidx in range(num_layers-1):
            self.fc.append(
                nn.Sequential(
                    nn.Linear(hidden_dim, hidden_dim), nn.LayerNorm(hidden_dim), nn.ReLU(), nn.Dropout(p)
                )
            )
        self.out = nn.Sequential(
            nn.Linear(hidden_dim, output_dim)
        )
        
        self.inp_drop = nn.Dropout(p)
    def get_repr(self, x):
        h = self.inp_drop(x)
        for lidx, fc in enumerate(self.fc):
            h=fc(h)
        return h
    
    def forward(self, x):
        h=self.get_repr(x)
        result = self.out(h)
        return result


class SERConfig(PretrainedConfig):
    model_type = "ser"

    def __init__(
        self,
        num_classes: int = 8,
        num_attention_heads = 16,
        num_hidden_layers = 24,
        hidden_size = 1024,
        classifier_hidden_layers = 1,
        classifier_dropout_prob  = 0.5,
        ssl_type= "microsoft/wavlm-large",
        torch_dtype= "float32",
        mean= -8.278621631819787e-05,
        std=0.08485510250851999,
        **kwargs,
    ):
        self.num_classes = num_classes
        self.num_attention_heads = num_attention_heads
        self.num_hidden_layers = num_hidden_layers
        self.hidden_size = hidden_size
        self.classifier_hidden_layers = classifier_hidden_layers
        self.classifier_dropout_prob = classifier_dropout_prob
        self.ssl_type = ssl_type
        self.torch_dtype = torch_dtype
        
        self.mean = mean
        self.std = std
        super().__init__(**kwargs)
        
class SERModel(PreTrainedModel):
    config_class = SERConfig
    
    def __init__(self, config):
        super().__init__(config)
        self.ssl_model = AutoModel.from_pretrained(config.ssl_type)
        self.ssl_model.freeze_feature_encoder()
        
        self.pool_model = AttentiveStatisticsPooling(config.hidden_size)
    
        self.ser_model = EmotionRegression(config.hidden_size*2, 
                                               config.hidden_size, 
                                               config.classifier_hidden_layers, 
                                               config.num_classes, 
                                               dropout=config.classifier_dropout_prob)
        
        
    def forward(self, x, mask):
        ssl = self.ssl_model(x, attention_mask=mask).last_hidden_state

        ssl = self.pool_model(ssl, mask)
        
        pred = self.ser_model(ssl)
        
        return pred
    
