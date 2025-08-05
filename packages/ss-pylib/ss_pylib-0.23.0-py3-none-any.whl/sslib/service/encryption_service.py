import base64
import hashlib
import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from sslib.service.base_service import BaseService


class EncryptionService(BaseService):
    def __init__(self, secret_key: str):
        super().__init__(name='EncryptionService')
        self._secret_key = hashlib.sha256(secret_key.encode()).digest()
        self._cipher = AESGCM(self._secret_key)

    def encrypt(self, plain_src: str) -> str:
        try:
            nonce = os.urandom(12)
            encrypted = self._cipher.encrypt(nonce, plain_src.encode(), None)
            return base64.b32encode(nonce + encrypted).decode().rstrip('=')
        except Exception as e:
            raise ValueError(f'암호화 실패: {e}') from e

    def decrypt(self, enc_src: str) -> str:
        try:
            padding = '=' * ((8 - len(enc_src) % 8) % 8)
            combined = base64.b32decode(enc_src + padding)
            nonce, encrypted = combined[:12], combined[12:]
            return self._cipher.decrypt(nonce, encrypted, None).decode()
        except Exception as e:
            raise ValueError(f'복호화 실패: {e}') from e
