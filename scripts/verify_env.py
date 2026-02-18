# scripts/verify_env.py
import os
import sys

required_keys = ["GEMINI_API_KEY", "ANTHROPIC_API_KEY"]
missing = [key for key in required_keys if not os.getenv(key)]

if missing:
    print(f"Missing keys: {', '.join(missing)}")
    sys.exit(1)
print("Environment keys present.")
