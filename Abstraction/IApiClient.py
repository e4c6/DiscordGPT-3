#  e4c6 ~ 2021

from abc import ABCMeta, abstractmethod
from typing import Tuple


class ApiClientInterface(metaclass=ABCMeta):

    @abstractmethod
    async def complete(self, prompt: Tuple[str], length: int, api_key: str, language: str, temperature: float) -> str:
        raise NotImplementedError

    @abstractmethod
    async def answer(self, question: Tuple[str], length: int, api_key: str, language: str, temperature: float) -> str:
        raise NotImplementedError

    @abstractmethod
    async def song(self, song_name: Tuple[str], user_name, length: int, api_key: str, language: str,
                   temperature: float) -> str:
        raise NotImplementedError

    @abstractmethod
    async def headline(self, prompt: Tuple[str], length: int, api_key: str, language: str, temperature: float) -> str:
        raise NotImplementedError

    @abstractmethod
    async def sentiment(self, prompt: Tuple[str], api_key: str, language: str) -> str:
        raise NotImplementedError

    @abstractmethod
    async def emojify(self, prompt: Tuple[str], length: int, api_key: str, language: str, temperature: float) -> str:
        raise NotImplementedError

    @abstractmethod
    async def sarcastic_answer(self, prompt: Tuple[str], length: int, api_key: str, language: str,
                               temperature: float) -> str:
        raise NotImplementedError

    @abstractmethod
    async def foulmouth_answer(self, prompt: Tuple[str], length: int, api_key: str, language: str,
                               temperature: float) -> str:
        raise NotImplementedError
