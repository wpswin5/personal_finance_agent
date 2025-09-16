import base64
import hashlib
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from app.config import get_settings

class EncryptionService:
    """Service for encrypting and decrypting sensitive data like Plaid access tokens."""
    
    def __init__(self):
        self.settings = get_settings()
        self._fernet = self._get_fernet()
    
    def _get_fernet(self) -> Fernet:
        """Generate a Fernet instance from the encryption key."""
        # Use the encryption key from settings
        key = self.settings.ENCRYPTION_KEY.encode()
        print("Found key:", key)
        
        # If the key is not exactly 32 bytes, derive it using PBKDF2
        if len(key) != 32:
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=b'plaid_salt',  # In production, use a random salt stored securely
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(key))
        else:
            key = base64.urlsafe_b64encode(key)
        
        return Fernet(key)
    
    def encrypt(self, plaintext: str) -> str:
        """Encrypt a plaintext string and return base64 encoded ciphertext."""
        if not plaintext:
            return ""
        
        encrypted_data = self._fernet.encrypt(plaintext.encode())
        return base64.urlsafe_b64encode(encrypted_data).decode()
    
    def decrypt(self, ciphertext: str) -> str:
        """Decrypt a base64 encoded ciphertext and return plaintext string."""
        if not ciphertext:
            return ""
        
        try:
            print("Trying to decrypt: ", ciphertext)
            encrypted_data = base64.urlsafe_b64decode(ciphertext.encode())
            decrypted_data = self._fernet.decrypt(encrypted_data)
            return decrypted_data.decode()
        except Exception as e:
            raise ValueError(f"Failed to decrypt data: {str(e)}")

# Global instance
encryption_service = EncryptionService()