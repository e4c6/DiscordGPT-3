#  e4c6 ~ 2021

from abc import ABCMeta, abstractmethod


class CryptoHandlerInterface(metaclass=ABCMeta):
    @abstractmethod
    def generate_key(self) -> bytes:
        raise NotImplementedError

    @abstractmethod
    def encrypt(self, message: bytes, key: bytes) -> bytes:
        raise NotImplementedError

    @abstractmethod
    def decrypt(self, token: bytes, key: bytes) -> bytes:
        raise NotImplementedError
