import regex
import re

api_secrets_data = [
    {
        "Domain": "Social Media",
        "Provider": "Meta",
        "Secret type": "facebook_access_token",
        "Regex": r"EAACEdEose0cBA[0-9A-Za-z]+",
        "Risks": "D,M",
    },
    {
        "Domain": "Communication",
        "Provider": "Slack",
        "Secret type": "slack_api_token",
        "Regex": r"xox[p|b|o|a]-[0-9]{12}-[0-9]{12}-[0-9]{12}-[a-z0-9]{32}",
        "Risks": "D,M",
    },
    {
        "Domain": "Communication",
        "Provider": "Slack",
        "Secret type": "slack_incoming_webhook_url",
        "Regex": r"https:\/\/hooks.slack.com\/services\/[A-Za-z0-9+\/]{44,46}",
        "Risks": "D,M",
    },
    {
        "Domain": "Communication",
        "Provider": "Sendinblue",
        "Secret type": "sendinblue_api_key",
        "Regex": r"xkeysib-[a-f0-9]{64}-[a-zA-Z0-9]{16}",
        "Risks": "D,M",
    },
    {
        "Domain": "IaaS",
        "Provider": "Alibaba Cloud",
        "Secret type": "alibaba_cloud_access_key_id",
        "Regex": r"LTAI[a-zA-Z0-9]{20}",
        "Risks": "D,F",
    },
    {
        "Domain": "IaaS",
        "Provider": "Amazon Web Services (AWS)",
        "Secret type": "aws_access_key_id",
        "Regex": r"AKIA[0-9A-Z]{16}",
        "Risks": "D,F",
    },
    {
        "Domain": "IaaS",
        "Provider": "Tencent Cloud",
        "Secret type": "tencent_cloud_secret_id",
        "Regex": r"AKID[0-9a-zA-Z]{32}",
        "Risks": "D,F",
    },
    {
        "Domain": "SaaS",
        "Provider": "Google",
        "Secret type": "google_api_key",
        "Regex": r"AIza[0-9A-Za-z\-_]{35}",
        "Risks": "D,F",
    },
    {
        "Domain": "SaaS",
        "Provider": "Google",
        "Secret type": "google_oauth_client_id",
        "Regex": r"[0-9]{11,13}-[a-z0-9]{32}\.apps\.googleusercontent\.com",
        "Risks": "D,F",
    },
    {
        "Domain": "SaaS",
        "Provider": "Google",
        "Secret type": "google_oauth_client_secret",
        "Regex": r"GOCSPX-[a-zA-Z0-9]{28}",
        "Risks": "D,F",
    },
    {
        "Domain": "Payment",
        "Provider": "Midtrans",
        "Secret type": "midtrans_sandbox_server_key",
        "Regex": r"SB-Mid-server-[0-9a-zA-Z_-]{24}",
        "Risks": "D,F",
    },
    {
        "Domain": "Payment",
        "Provider": "Flutterwave",
        "Secret type": "flutterwave_live_secret_key",
        "Regex": r"FLWPUBK_TEST-[0-9a-f]{32}-X",
        "Risks": "D,F",
    },
    {
        "Domain": "Payment",
        "Provider": "Flutterwave",
        "Secret type": "flutterwave_test_api_secret_key",
        "Regex": r"FLWSECK_TEST-[0-9a-f]{32}-X",
        "Risks": "D,F",
    },
    {
        "Domain": "Payment",
        "Provider": "Stripe",
        "Secret type": "stripe_live_secret_key",
        "Regex": r"sk_live_[0-9a-zA-Z]{24}",
        "Risks": "D,F",
    },
    {
        "Domain": "Payment",
        "Provider": "Stripe",
        "Secret type": "stripe_test_secret_key",
        "Regex": r"sk_test_[0-9a-zA-Z]{24}",
        "Risks": "D,F",
    },
    {
        "Domain": "EC",
        "Provider": "eBay",
        "Secret type": "ebay_production_client_id",
        "Regex": r"[a-zA-Z0-9_\-]{8}-[a-zA-Z0-9_\-]{8}PRD-[a-z0-9]{9}-[a-z0-9]{8}",
        "Risks": "D",
    },
    {
        "Domain": "DevOps",
        "Provider": "GitHub",
        "Secret type": "github_personal_access_token",
        "Regex": r"ghp_[0-9a-zA-Z]{36}",
        "Risks": "D",
    },
    {
        "Domain": "DevOps",
        "Provider": "GitHub",
        "Secret type": "github_oauth_access_token",
        "Regex": r"gho_[0-9a-zA-Z]{36}",
        "Risks": "D",
    },

    # {   "Secret type": "email",
    #     "Regex": r'''(?<=^|[\b\s@,?!;:)(’".\p{Han}<])([^\b\s@?!;,:)(’"<]+@[^\b\s@!?;,/]*[^\b\s@?!;,/:)(’">.]\.\p{L}\w{1,})(?=$|[\b\s@,?!;:)(’".\p{Han}>])'''

        
    # }
]

email_secrets_data = [
    {   "Secret type": "email",
        "Regex": r'''(?<=^|[\b\s@,?!;:)(’".\p{Han}<])([^\b\s@?!;,:)(’"<]+@[^\b\s@!?;,/]*[^\b\s@?!;,/:)(’">.]\.\p{L}\w{1,})(?=$|[\b\s@,?!;:)(’".\p{Han}>])'''

        
    }

]

class SecretSearcher:
    def __init__(self):
        self.api_secrets_data = api_secrets_data
        self.email_secrets_data = email_secrets_data

        
    def search(self, text, secrets_data=None):
        results = []
        try:
            for secret in secrets_data:
                if secret["Secret type"] == "email":
                    pattern = regex.compile(secret["Regex"], regex.UNICODE)
                else:
                    pattern = re.compile(secret["Regex"])
                for match in pattern.finditer(text):
                    results.append({
                        "secret_type": secret["Secret type"],
                        "match": match.group(),
                        "start": match.start(),
                        "end": match.end()
                    })
        except Exception as e:
            print(f"Error searching secrets: {e}")
        return results