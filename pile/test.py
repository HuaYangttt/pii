import unittest
from hard_c import SecretSearcher

class TestSecretSearcher(unittest.TestCase):

    def setUp(self):
        self.searcher = SecretSearcher()

    def test_github_pat(self):
        text = "Here is a GitHub token: ghp_abcdefghijklmnopqrstuvwxyz0123456789"
        results = self.searcher.search(text)

        self.assertTrue(any("ghp_" in r["match"] for r in results))
        for r in results:
            if "ghp_" in r["match"]:
                self.assertEqual(r["secret_type"], "github_personal_access_token")
                self.assertTrue(r["start"] < r["end"])
    
    def test_aws_key(self):
        text = "AWS Key: AKIA1234567890ABCDEF"
        results = self.searcher.search(text)
        
        self.assertTrue(any("AKIA" in r["match"] for r in results))
        for r in results:
            if "AKIA" in r["match"]:
                self.assertEqual(r["secret_type"], "aws_access_key_id")
                self.assertTrue(r["start"] < r["end"])
    
    def test_no_match(self):
        text = "This is a clean file with no secrets."
        results = self.searcher.search(text)
        self.assertEqual(results, [])

if __name__ == "__main__":
    unittest.main()
