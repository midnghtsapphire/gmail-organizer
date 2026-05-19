import unittest

import gmail_organizer_original as go


class TestGitHubRepositoryLabelMigration(unittest.TestCase):
    def test_owner_repo_label_maps_to_github_dev(self):
        self.assertEqual(
            go.map_old_label_to_new("midnghtsapphire/gmail-organizer"),
            "PROJECTS/GitHub-Dev",
        )

    def test_existing_hierarchy_label_is_not_remapped(self):
        self.assertIsNone(go.map_old_label_to_new("PROJECTS/GitHub-Dev"))


if __name__ == "__main__":
    unittest.main()
