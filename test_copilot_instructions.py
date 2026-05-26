import unittest
from pathlib import Path

COPILOT_INSTRUCTIONS_PATH = Path(__file__).resolve().parent / '.github' / 'copilot-instructions.md'


class TestCopilotInstructions(unittest.TestCase):
    def test_copilot_instructions_include_s2m_revvel_guidance(self):
        self.assertTrue(COPILOT_INSTRUCTIONS_PATH.exists())
        text = COPILOT_INSTRUCTIONS_PATH.read_text(encoding='utf-8').lower()
        self.assertIn('s2m', text)
        self.assertIn('revvel', text)
        self.assertIn('one iteration', text)
        self.assertIn('changelog.md', text)
        self.assertIn('deployment_guide.md', text)
        self.assertIn('go_to_market.md', text)
        self.assertIn('brand_guidelines.md', text)
        self.assertIn('security.md', text)
        self.assertIn('research engine outputs', text)
        self.assertIn('assets inventory', text)
        self.assertIn('artifacts inventory', text)
        self.assertIn('extend it instead of replacing it', text)


if __name__ == '__main__':
    unittest.main()
