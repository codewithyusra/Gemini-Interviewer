from dotenv import load_dotenv
import os
from pathlib import Path

# 1️⃣ Path to your .env file
env_path = Path(__file__).parent / ".env"

# 2️⃣ Load environment variables from .env
load_dotenv(env_path)

# 3️⃣ Try to get key from .env; fallback to hardcoded key
API_KEY = os.getenv("GOOGLE_API_KEY") or "AIzaSyAQiFN5rVAkvRlW5sv64NLF-fTpJx2vqUM"

# 4️⃣ Print key to verify
print("API Key loaded:", API_KEY)

# 5️⃣ Optional: simple check to see if the key is usable (dummy)
if API_KEY.startswith("AIza"):
    print("✅ API Key seems valid format")
else:
    print("❌ API Key missing or invalid")

