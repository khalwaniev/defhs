# Bounded model selection

Selected exactly one model: **Qwen/Qwen3-14B**, immutable HF revision
`40c069824f4251a91eefaf281ebe4c544efd3e18`, Apache-2.0, public and ungated.
Use NF4 double quantization, FP16 compute, non-thinking and the old fixed prompt.
No model sweep was run. Claude API access is not needed.

The independent [MMLU-ProX paper, Table 6](https://arxiv.org/html/2503.10497v2)
reports Hindi five-shot accuracy of **53.7** for Qwen3-14B versus **47.0** for
Qwen3-8B in their non-thinking rows. These are Hindi reasoning/knowledge results,
not emotion classification and not results for this quantization or prompt.
The [Qwen3 technical report, Tables 16/18](https://arxiv.org/html/2505.09388v1)
also reports non-thinking MMMLU 72.6 vs 66.9 and Multi-IF 72.9 vs 69.2; both
benchmark suites include Hindi. This supports a stronger linguistic challenger,
not a prediction of DEFHS gain.

Only one larger alternative was examined for feasibility: official Qwen3-32B-AWQ
(public revision `0499c3ac83fdef8810b907a23894ba91e95eddd8`). Its [model card](https://huggingface.co/Qwen/Qwen3-32B-AWQ)
and [official speed table](https://github.com/QwenLM/Qwen3/blob/main/docs/source/getting_started/speed_benchmark.md)
show a larger 4-bit resident footprint and an AWQ deployment path. The reported
32B speed/memory benchmark is not a dual-T4 measurement. Its stronger Hindi
benchmark does not remove the endgame integration risk of changing quantization
backends. Choose 14B to reuse the demonstrated historical NF4/Transformers stack
with ample expected dual-T4 memory margin. This is a deadline/access tradeoff,
not a claim that 14B is the strongest possible open model.

The chosen snapshot contains approximately **29.55 GB** of files. The runner
requires **34 GiB free cache disk**. A storage calculation puts NF4 weights plus
unquantized embeddings/output projection around **10 GB combined**; KV cache,
activations and CUDA workspace add overhead. It is sharded across two T4s with
a 13 GiB per-device load budget, batch 4 and 512-token padded inputs. Actual peaks
and throughput remain unmeasured until Kaggle runs the pilot. The
[Transformers bitsandbytes documentation](https://huggingface.co/docs/transformers/v4.57.0/en/quantization/bitsandbytes)
lists hardware support for NF4 on GPUs older than T4. Do not describe that
compatibility statement as a completed experiment.

Pinned inference packages: transformers 4.57.1, accelerate 1.11.0, bitsandbytes
0.48.1, huggingface-hub 0.36.0 and safetensors 0.6.2. Host PyTorch/CUDA versions
are recorded by the pilot. Checkpoint file hashes and repeated pilot labels are
recorded; exact behavior across future GPU/library changes is not promised.

The repository's prior live rules audit permits externally available pretrained
models subject to reasonable access/reproducibility. This public Apache-2.0
snapshot uses no new labeled external dataset. The transcripts stay in the
private Kaggle compute job. The [competition rules](https://www.kaggle.com/competitions/dataverse-detecting-emotions-from-hindi-speech/rules)
and the prior `RS-DEFHS-STRONG-LLM-SEMANTIC-001/RETURN_TO_SS.md` remain the recorded
competition-policy sources; no new authenticated account-status claim is made.
