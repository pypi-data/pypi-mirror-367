from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os

class QuantumEncryptor:
    def __init__(self):
        self.session_key = None
        self.iv = None
        
    def generate_session_id(self):
        return os.urandom(16).hex()
    
    def _generate_key(self):
        if not self.session_key:
            self.session_key = os.urandom(32)  # AES-256
            self.iv = os.urandom(16)
        return self.session_key, self.iv
        
    def encrypt(self, plaintext):
        key, iv = self._generate_key()
        cipher = Cipher(
            algorithms.AES(key),
            modes.GCM(iv),
            backend=default_backend()
        )
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(plaintext) + encryptor.finalize()
        return iv + encryptor.tag + ciphertext
        
    def decrypt(self, ciphertext):
        key = self.session_key
        iv = ciphertext[:16]
        tag = ciphertext[16:32]
        ciphertext = ciphertext[32:]
        
        cipher = Cipher(
            algorithms.AES(key),
            modes.GCM(iv, tag),
            backend=default_backend()
        )
        decryptor = cipher.decryptor()
        return decryptor.update(ciphertext) + decryptor.finalize()
