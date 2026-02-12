import os
import json
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

class SecretsManager:
    def __init__(self, password=None):
        self.password = password or os.getenv('SECRET_MANAGER_PASSWORD', 'default_local_password')
        self.secrets_file = os.path.join(os.path.dirname(__file__), '..', 'secrets.enc')
        self.key = self._derive_key()
        
    def _derive_key(self):
        """Derive a key from the password using PBKDF2"""
        salt = b'stocksteward_default_salt_2026'  # In production, use a random salt
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.password.encode()))
        return key
    
    def _get_fernet(self):
        return Fernet(self.key)
    
    def store_secrets(self, secrets_dict):
        """Encrypt and store secrets to file"""
        fernet = self._get_fernet()
        encrypted_data = fernet.encrypt(json.dumps(secrets_dict).encode())
        
        with open(self.secrets_file, 'wb') as f:
            f.write(encrypted_data)
    
    def load_secrets(self):
        """Load and decrypt secrets from file"""
        if not os.path.exists(self.secrets_file):
            return {}
        
        try:
            with open(self.secrets_file, 'rb') as f:
                encrypted_data = f.read()
            
            fernet = self._get_fernet()
            decrypted_data = fernet.decrypt(encrypted_data)
            return json.loads(decrypted_data.decode())
        except Exception as e:
            print(f"Error loading secrets: {e}")
            return {}
    
    def get_secret(self, key, default=None):
        """Get a specific secret value"""
        secrets = self.load_secrets()
        return secrets.get(key, default)
    
    def set_secret(self, key, value):
        """Set a specific secret value"""
        secrets = self.load_secrets()
        secrets[key] = value
        self.store_secrets(secrets)

# Global instance
secrets_manager = SecretsManager()

if __name__ == "__main__":
    # Example usage
    # secrets_manager.set_secret("GROQ_API_KEY", "your_encrypted_key_here")
    # api_key = secrets_manager.get_secret("GROQ_API_KEY")
    pass