import unittest
from pathlib import Path

COPILOT_INSTRUCTIONS_PATH = Path('.github/copilot-instructions.md')


class TestCopilotInstructions(unittest.TestCase):
    def test_copilot_instructions_include_s2m_revvel_guidance(self):
        self.assertTrue(COPILOT_INSTRUCTIONS_PATH.exists())
        text = COPILOT_INSTRUCTIONS_PATH.read_text(encoding='utf-8').lower()
        self.assertIn('s2m', text)
        self.assertIn('revvel', text)


if __name__ == '__main__':
    unittest.main()
