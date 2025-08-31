import requests
from dotenv import load_dotenv
import os
load_dotenv()


url = "https://api.linkedin.com/v2/ugcPosts"

headers = {
    "Authorization": f"Bearer {os.getenv('ACCESS_TOKEN')}",
    "Content-Type": "application/json",
    "X-Restli-Protocol-Version": "2.0.0"
}

post_data = {
    "author": os.getenv('PERSON_URN'),
    "lifecycleState": "PUBLISHED",
    "specificContent": {
        "com.linkedin.ugc.ShareContent": {
            "shareCommentary": {
                "text": "🚀 Success! Automated LinkedIn post!"
            },
            "shareMediaCategory": "NONE"
        }
    },
    "visibility": {
        "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
    }
}

response = requests.post(url, headers=headers, json=post_data)

print("Status:", response.status_code)
print("Response:", response.text)
