#!/usr/bin/env python3
"""
Utility script to update encrypted secrets
"""

import sys
import getpass
from pathlib import Path

# Add the backend directory to the path
sys.path.append(str(Path(__file__).parent))

from app.utils.secrets_manager import secrets_manager

def update_secret():
    print("StockSteward AI - Encrypted Secrets Manager")
    print("=" * 50)
    
    print("\nSelect the secret to update:")
    print("1. GROQ_API_KEY")
    print("2. OPENAI_API_KEY")
    print("3. ANTHROPIC_API_KEY")
    print("4. HUGGINGFACE_API_KEY")
    print("5. Show current secrets (values will be masked)")
    print("6. Exit")
    
    choice = input("\nEnter your choice (1-6): ").strip()
    
    if choice == "6":
        print("Exiting...")
        return
    elif choice == "5":
        print("\nCurrent secrets (masked):")
        all_secrets = secrets_manager.load_secrets()
        for key, value in all_secrets.items():
            if value:
                masked_value = "*" * len(value) if value else ""
                print(f"  {key}: {masked_value}")
            else:
                print(f"  {key}: (not set)")
        input("\nPress Enter to continue...")
        update_secret()
        return
    elif choice in ["1", "2", "3", "4"]:
        secret_map = {
            "1": "GROQ_API_KEY",
            "2": "OPENAI_API_KEY", 
            "3": "ANTHROPIC_API_KEY",
            "4": "HUGGINGFACE_API_KEY"
        }
        
        secret_name = secret_map[choice]
        print(f"\nUpdating {secret_name}")
        
        # Use getpass to hide the input
        new_value = getpass.getpass(f"Enter new value for {secret_name}: ")
        
        if new_value:
            # Update the secret
            secrets_manager.set_secret(secret_name, new_value)
            print(f"\n✓ {secret_name} updated successfully in encrypted storage!")
        else:
            print(f"\n! No value entered for {secret_name}")
    else:
        print("\n! Invalid choice. Please select 1-6")
    
    input("\nPress Enter to continue...")
    update_secret()

if __name__ == "__main__":
    update_secret()