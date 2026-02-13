from groq import Groq
import os
import sys

# Add project root to sys.path
sys.path.append(os.getcwd())

from app.utils.secrets_manager import secrets_manager

key = secrets_manager.get_secret('GROQ_API_KEY')
if not key:
    print("GROQ_API_KEY NOT FOUND")
    sys.exit(1)

client = Groq(api_key=key)

try:
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": "Hello, are you active?",
            }
        ],
        model="llama-3.3-70b-versatile",
    )
    print("SUCCESS")
    print(chat_completion.choices[0].message.content)
except Exception as e:
    print(f"FAILED: {e}")
