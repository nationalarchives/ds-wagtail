import os
from allauth.mfa.adapter import DefaultMFAAdapter
from cryptography.fernet import Fernet
from django.conf import settings

class EncryptedMFAAdapter(DefaultMFAAdapter):
    """Extend allauth default MFA adapter to encrypt and decrypt MFA secrets before storing them in the database."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not hasattr(settings, "MFA_ENCRYPTION_KEY"):
            raise ValueError("MFA_ENCRYPTION_KEY must be set in Django settings for EncryptedMFAAdapter to work.")
        self.fernet = Fernet(settings.MFA_ENCRYPTION_KEY)
        

    def encrypt(self, text: str) -> str:
        """Encrypt MFA secrets such as the TOTP key before storing them in the database."""
        if not text:
            return text
        
        return self.fernet.encrypt(text.encode()).decode()
    
    def decrypt(self, encrypted_text: str) -> str:
        """Decrypt secrets such as the TOTP key when retrieving them from the database."""
        if not encrypted_text:
            return encrypted_text
        
        return self.fernet.decrypt(encrypted_text.encode()).decode()