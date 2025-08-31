import requests
from dotenv import load_dotenv
import os
load_dotenv()




# ---- Request token ----
url = "https://www.linkedin.com/oauth/v2/accessToken"
data = {
    "grant_type": "authorization_code",
    "code": os.getenv('AUTH_CODE'),
    "redirect_uri": os.getenv('REDIRECT_URI'),
    "client_id": os.getenv('CLIENT_ID'),
    "client_secret": os.getenv('CLIENT_SECRET')
}

response = requests.post(url, data=data)

print("Status:", response.status_code)
print("Response:", response.json())
