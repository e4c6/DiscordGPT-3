#  e4c6 ~ 2021
from cryptography.fernet import Fernet

from Abstraction.ICryptoHandler import CryptoHandlerInterface


class CryptoHandler(CryptoHandlerInterface):
    def __enter__(self):
        return self

    def generate_key(self) -> bytes:
        return Fernet.generate_key()

    def encrypt(self, message: bytes, key: bytes) -> bytes:
        return Fernet(key).encrypt(message)

    def decrypt(self, token: bytes, key: bytes) -> bytes:
        return Fernet(key).decrypt(token)

    def __exit__(self):
        pass
