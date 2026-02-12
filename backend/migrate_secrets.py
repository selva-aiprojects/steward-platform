#!/usr/bin/env python3
"""
Migration script to move API keys from .env to encrypted storage
"""

import os
import sys
from pathlib import Path

# Add the backend directory to the path
sys.path.append(str(Path(__file__).parent))

from app.utils.secrets_manager import secrets_manager

def migrate_secrets_to_encrypted_storage():
    print("Migrating API keys to encrypted storage...")
    
    # Read the .env file directly
    env_file_path = '.env'
    secrets_dict = {}
    
    if os.path.exists(env_file_path):
        with open(env_file_path, 'r') as f:
            env_content = f.read()
        
        # Parse the .env file
        for line in env_content.splitlines():
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip().strip('"\'')  # Remove quotes if present
                
                if key == 'GROQ_API_KEY' and value:
                    secrets_dict['GROQ_API_KEY'] = value
                    print("+ GROQ_API_KEY migrated to encrypted storage")
                elif key == 'OPENAI_API_KEY' and value:
                    secrets_dict['OPENAI_API_KEY'] = value
                    print("+ OPENAI_API_KEY migrated to encrypted storage")
                elif key == 'ANTHROPIC_API_KEY' and value:
                    secrets_dict['ANTHROPIC_API_KEY'] = value
                    print("+ ANTHROPIC_API_KEY migrated to encrypted storage")
                elif key == 'HUGGINGFACE_API_KEY' and value:
                    secrets_dict['HUGGINGFACE_API_KEY'] = value
                    print("+ HUGGINGFACE_API_KEY migrated to encrypted storage")
    
    if secrets_dict:
        secrets_manager.store_secrets(secrets_dict)
        print(f"\n+ Successfully stored {len(secrets_dict)} secrets in encrypted storage")
        print("+ Secrets are now stored in 'secrets.enc' file")
        print("! Remember to add 'secrets.enc' to your .gitignore file!")
    else:
        print("No API keys found in .env file to migrate")
    
    # Verify the migration
    print("\nVerifying migration...")
    if secrets_dict.get('GROQ_API_KEY'):
        retrieved_key = secrets_manager.get_secret('GROQ_API_KEY')
        print(f"GROQ_API_KEY retrieved: {'+' if retrieved_key == secrets_dict.get('GROQ_API_KEY') else '?'}")
    
    if secrets_dict.get('OPENAI_API_KEY'):
        retrieved_key = secrets_manager.get_secret('OPENAI_API_KEY')
        print(f"OPENAI_API_KEY retrieved: {'+' if retrieved_key == secrets_dict.get('OPENAI_API_KEY') else '?'}")

if __name__ == "__main__":
    migrate_secrets_to_encrypted_storage()