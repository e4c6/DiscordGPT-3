#  e4c6 ~ 2021

from string import Template
from typing import Tuple

import aiohttp

from Abstraction.IApiClient import ApiClientInterface
from Errors.RequestFailedException import RequestFailedException
from Helpers.Formatters import prep_sentiment
from Helpers.Wrappers import try_catch_log
from Implementation import LoggingHandler
from Prompts import language_map


class ApiClient(ApiClientInterface):
    def __init__(self, logger: LoggingHandler):
        self.__logger = logger.get_logger("openai_client")

    @staticmethod
    def ensure_success(status_code):
        if status_code != 200:
            raise RequestFailedException(status_code)

    @try_catch_log
    async def complete(self, prompt: Tuple[str], length: int, api_key: str, language="EN", temperature=0.5) -> str:
        cue = " ".join(str(x) for x in prompt)
        prompt = Template(language_map[language]["complete"]).substitute(input=cue)
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + api_key
        }
        params = {
            "prompt": prompt,
            "max_tokens": length,
            "temperature": temperature,
            "top_p": 1,
            "n": 1,
            "stream": False,
            "logprobs": None,
            "stop": ["###", "\n"],
            "echo": False
        }
        async with aiohttp.ClientSession() as session:
            async with session.post('https://api.openai.com/v1/engines/davinci/completions', headers=headers,
                                    json=params) as r:
                self.ensure_success(r.status)
                text = await r.json()
                out = text['choices'][0]['text']
                return cue + out

    @try_catch_log
    async def answer(self, question: Tuple[str], length: int, api_key: str, language="EN", temperature=0.5) -> str:
        question = " ".join(str(x) for x in question)
        prompt = Template(language_map[language]["answer"]).substitute(input=question)
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + api_key
        }
        params = {
            'completions': 1,
            'context': prompt,
            'length': length,
            'temperature': temperature,
            'top_p': 1,
            'frequency_penalty': 0,
            'presence_penalty': 0,
            "stream": False,
            'best_of': 1,
            "stop": ["###", "\n"]
        }
        async with aiohttp.ClientSession() as session:
            async with session.post('https://api.openai.com/v1/engines/davinci/generate', headers=headers,
                                    json=params) as r:
                self.ensure_success(r.status)
                text = await r.json()
                out = "".join(text['data'][0]['text'])
                answer = out.split(prompt)[-1].strip()
                result = "Q: {} \nA: {}".format(question, answer)
                return result

    @try_catch_log
    async def song(self, song_name: Tuple[str], user_name: str, length: int, api_key: str, language: str = "EN",
                   temperature: float = 0.5) -> str:
        song_name = " ".join(str(x) for x in song_name)
        prompt = Template(language_map[language]["song"]).substitute(input=song_name, input2=user_name)

        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + api_key
        }
        params = {
            "prompt": prompt,
            "max_tokens": length,
            "temperature": temperature,
            "top_p": 1,
            "n": 1,
            "stream": False,
            "logprobs": None,
            "echo": False
        }
        async with aiohttp.ClientSession() as session:
            async with session.post('https://api.openai.com/v1/engines/davinci/completions', headers=headers,
                                    json=params) as r:
                self.ensure_success(r.status)
                text = await r.json()
                text = text['choices'][0]['text']
                out = prompt + text
                return out

    @try_catch_log
    async def headline(self, prompt: Tuple[str], length: int, api_key: str, language="EN", temperature=0.5) -> str:
        topics = ", ".join(str(x) for x in prompt)
        scaffold = Template(language_map[language]["headline"]).substitute(input=topics)

        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + api_key
        }
        params = {
            "prompt": scaffold,
            "max_tokens": length,
            "temperature": temperature,
            "top_p": 1,
            "n": 1,
            "stream": False,
            "logprobs": None,
            "echo": False,
            'stop': '\n'
        }
        async with aiohttp.ClientSession() as session:
            async with session.post('https://api.openai.com/v1/engines/davinci/completions', headers=headers,
                                    json=params) as r:
                self.ensure_success(r.status)
                text = await r.json()
                text = text['choices'][0]['text']
                result = Template(language_map[language]["headline_out"]).substitute(input=text)
                return result

    @try_catch_log
    async def sentiment(self, prompt: Tuple[str], api_key: str, language="EN") -> str:
        prompt = " ".join(str(x) for x in prompt)
        data = {"documents": language_map[language]["sentiment"],
                "query": Template("$input.").substitute(input=prompt)}
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + api_key
        }
        async with aiohttp.ClientSession() as session:
            async with session.post('https://api.openai.com/v1/engines/davinci/search', headers=headers,
                                    json=data) as r:
                self.ensure_success(r.status)
                results = await r.json()
                results = results["data"]
                sentiment = prep_sentiment(results)
                return sentiment

    @try_catch_log
    async def emojify(self, prompt: Tuple[str], length: int, api_key: str, language="EN", temperature=0.5) -> str:
        topics = " ".join(str(x) for x in prompt)
        scaffold = Template(language_map[language]["emojify"]).substitute(input=topics)

        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + api_key
        }
        params = {
            "prompt": scaffold,
            "max_tokens": length,
            "temperature": temperature,
            "top_p": 1,
            "n": 1,
            "frequency_penalty": 0,
            "presence_penalty": 0,
            "stream": False,
            "logprobs": None,
            "echo": False,
            "stop": "\n"
        }
        async with aiohttp.ClientSession() as session:
            async with session.post('https://api.openai.com/v1/engines/davinci/completions', headers=headers,
                                    json=params) as r:
                self.ensure_success(r.status)
                text = await r.json()
                text = text['choices'][0]['text']
                result = Template("""$input: $input2""").substitute(input=topics, input2=text)
                return result

    @try_catch_log
    async def sarcastic_answer(self, prompt: Tuple[str], length: int, api_key: str, language="EN",
                               temperature=0.5) -> str:
        q = " ".join(str(x) for x in prompt)
        scaffold = Template(language_map[language]["sarcasm"]).substitute(input=q)
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + api_key
        }
        params = {
            "prompt": scaffold,
            "max_tokens": length,
            "temperature": temperature,
            "top_p": 1,
            "n": 1,
            "stream": False,
            "logprobs": None,
            "echo": False,
            "frequency_penalty": 0,
            "presence_penalty": 0,
            "stop": "\n"
        }
        async with aiohttp.ClientSession() as session:
            async with session.post('https://api.openai.com/v1/engines/davinci/completions', headers=headers,
                                    json=params) as r:
                self.ensure_success(r.status)
                text = await r.json()
                text = text['choices'][0]['text']
                out = "Q: {} \n A: {}".format(q, text)
                return out

    @try_catch_log
    async def foulmouth_answer(self, prompt: Tuple[str], length: int, api_key: str, language="EN",
                               temperature=0.5) -> str:
        q = " ".join(str(x) for x in prompt)
        scaffold = Template(language_map[language]["foulmouth"]).substitute(input=q)
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + api_key
        }
        params = {
            "prompt": scaffold,
            "max_tokens": length,
            "temperature": temperature,
            "top_p": 1,
            "n": 1,
            "stream": False,
            "logprobs": None,
            "echo": False,
            "frequency_penalty": 0,
            "presence_penalty": 0,
            "stop": "\n"
        }
        async with aiohttp.ClientSession() as session:
            async with session.post('https://api.openai.com/v1/engines/davinci/completions', headers=headers,
                                    json=params) as r:
                self.ensure_success(r.status)
                text = await r.json()
                text = text['choices'][0]['text']
                out = "Q: {} \n A: {}".format(q, text)
                return out
