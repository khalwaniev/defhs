import importlib.util
import json
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('strong_llm', Path(__file__).resolve().parents[1] / 'scripts/defhs_strong_llm.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class ScientificContractTests(unittest.TestCase):
    def test_abstention_is_false_negative_not_fifth_macro_class(self):
        result = m.metrics(m.CLASSES, ['angry', 'happy', 'neutral', 'unclear'])
        self.assertEqual(result['macro_f1'], .75)
        self.assertEqual(result['per_class']['sad']['recall'], 0)
        self.assertEqual(result['abstentions'], 1)

    def test_corrections_and_breakages_are_paired(self):
        result = m.paired(['angry', 'happy', 'neutral', 'sad'],
                         ['angry', 'sad', 'neutral', 'happy'],
                         ['sad', 'happy', 'sad', 'neutral'])
        self.assertEqual(result, {'corrections': 2, 'breakages': 1, 'wrong_to_other_wrong': 1,
                                 'disagreements': 4, 'old_neutral_sad_errors_corrected': 1,
                                 'new_neutral_sad_breakages': 0})

    def test_only_transcript_reaches_provider(self):
        cfg, prompt, rows = m.load_inputs()
        body = m.request_body('यह एक वाक्य है।', cfg, prompt)
        self.assertEqual(json.loads(body['messages'][0]['content']), {'transcript': 'यह एक वाक्य है।'})
        self.assertTrue(all(set(r) == {'Id', 'transcript'} for r in rows))
        self.assertNotIn('tools', body)
        self.assertEqual(body['model'], 'claude-opus-4-6')

    def test_wrong_model_and_truncation_fail(self):
        response = {'model': 'claude-opus-4-6', 'stop_reason': 'end_turn',
                    'content': [{'type':'text', 'text':'{"label":"sad","sufficient_evidence":false}'}]}
        self.assertEqual(m.validate_answer(response, 'claude-opus-4-6')['label'], 'sad')
        response['stop_reason'] = 'max_tokens'
        with self.assertRaises(RuntimeError): m.validate_answer(response, 'claude-opus-4-6')
        response['stop_reason'] = 'end_turn'; response['model'] = 'another-model'
        with self.assertRaises(RuntimeError): m.validate_answer(response, 'claude-opus-4-6')


if __name__ == '__main__':
    unittest.main()
