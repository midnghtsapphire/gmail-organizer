import unittest
from pathlib import Path


class TestCopilotInstructions(unittest.TestCase):
    def test_copilot_instructions_include_s2m_revvel_guidance(self):
        instructions = Path('.github/copilot-instructions.md')
        self.assertTrue(instructions.exists())
        text = instructions.read_text(encoding='utf-8').lower()
        self.assertIn('s2m', text)
        self.assertIn('revvel', text)


if __name__ == '__main__':
    unittest.main()
