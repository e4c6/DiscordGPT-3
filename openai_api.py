from Prompts import language_map
from Errors import *
import aiohttp


def handle_status(status_code):
    if status_code == 429:
        raise TokenExhaustedError
    elif status_code == 400:
        raise TokenInvalidError
    elif status_code == 500:
        raise OpenAIError


# TODO: Remove the need
def serialize_answer(char_list):
    out = ""
    for i in char_list:
        out += i
    return out


# TODO: Fix this monstrosity
def prep_sentiment(results):
    [r.pop("object", None) for r in results]
    scores = [(r["document"], r["score"]) for r in results]
    res = {}
    for score in scores:
        if score[0] == 0:
            res["Pozitif"] = score[1]
        if score[0] == 1:
            res["Negatif"] = score[1]
        if score[0] == 2:
            res["Nötr"] = score[1]
    ns = []
    for k in res.keys():
        ns.append(res[k])
    for k in res.keys():
        if res[k] == max(ns):
            res[k] = str(res[k]) + " ✅"
        else:
            res[k] = str(res[k]) + " :x:"
    out = """
    Sentiment:
    Positive: {}
    Negative: {}
    Neutral: {}
    """.format(res["Pozitif"], res["Negatif"], res["Nötr"])
    return out


class ApiHandler:
    def __init__(self, logger):
        self.__logger = logger

    async def complete(self, prompt, length, api_key, language="EN", temperature=0.5):
        try:
            cue = " ".join(str(x) for x in prompt)
            prompt = language_map[language]["complete"].format(cue)
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
                    if r.status == 200:
                        text = await r.json()
                        out = text['choices'][0]['text']
                        return cue + out
                    else:
                        handle_status(r.status)
        except Exception as e:
            self.__logger.warning("Completion failed with error: {}".format(e))
            return "Something went wrong. Robots too have problems..."

    async def answer(self, question, length, api_key, language="EN", temperature=0.5):
        try:
            question = " ".join(str(x) for x in question)
            prompt = language_map[language]["answer"].format(question)
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
                'frequency_penalty': frequency_penalty,
                'presence_penalty': presence_penalty,
                "stream": False,
                'best_of': 1,
                "stop": ["###", "\n"]
            }
            async with aiohttp.ClientSession() as session:
                async with session.post('https://api.openai.com/v1/engines/davinci/generate', headers=headers,
                                        json=params) as r:
                    if r.status == 200:
                        text = await r.json()
                        out = serialize_answer(text['data'][0]['text'])
                        answer = out.split(prompt)[-1].strip()
                        result = "Q: {} \nA: {}".format(question, answer)
                        return result
                    else:
                        handle_status(r.status)
        except Exception as e:
            self.__logger.warning("Answer failed with error: {}".format(e))
            return "Something went wrong. Robots too have problems..."

    async def song(self, song_name, user_name, length, api_key, language="EN", temperature=0.5):
        try:
            song_name = " ".join(str(x) for x in song_name)
            prompt = language_map[language]["song"].format(song_name, user_name)

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
                    if r.status == 200:
                        text = await r.json()
                        text = text['choices'][0]['text']
                        out = prompt + text
                        return out
                    else:
                        handle_status(r.status)
        except Exception as e:
            self.__logger.warning("Sing failed with error: {}".format(e))
            return "Something went wrong. Robots too have problems..."

    async def headline(self, prompt, length, api_key, language="EN", temperature=0.5):
        try:
            topics = ", ".join(str(x) for x in prompt)
            scaffold = language_map[language]["headline"].format(topics)

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
                    if r.status == 200:
                        text = await r.json()
                        text = text['choices'][0]['text']
                        result = language_map[language]["headline_out"].format(text)
                        return result
                    else:
                        handle_status(r.status)
        except Exception as e:
            self.__logger.warning("Headline failed with error: {}".format(e))
            return "Something went wrong. Robots too have problems..."

    async def sentiment(self, prompt, api_key, language="EN"):
        try:
            prompt = " ".join(str(x) for x in prompt)
            data = {"documents": language_map[language]["sentiment"],
                    "query": "{}.".format(prompt)}
            headers = {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + api_key
            }
            async with aiohttp.ClientSession() as session:
                async with session.post('https://api.openai.com/v1/engines/davinci/search', headers=headers,
                                        json=data) as r:
                    if r.status == 200:
                        results = await r.json()
                        results = results["data"]
                        out = prep_sentiment(results)
                        return out
                    else:
                        handle_status(r.status)
        except Exception as e:
            self.__logger.warning("Sentiment failed with error: {}".format(e))
            return "Something went wrong. Robots too have problems..."

    async def emojify(self, prompt, length, api_key, language="EN", temperature=0.5):
        try:
            topics = " ".join(str(x) for x in prompt)
            scaffold = language_map[language]["emojify"].format(topics)

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
                    if r.status == 200:
                        text = await r.json()
                        text = text['choices'][0]['text']
                        result = """{}: {}""".format(topics, text)
                        return result
                    else:
                        handle_status(r.status)
        except Exception as e:
            self.__logger.warning("Emojify failed with error: {}".format(e))
            return "Something went wrong. Robots too have problems..."

    async def sarcastic_answer(self, prompt, length, api_key, language="EN", temperature=0.5):
        try:
            q = " ".join(str(x) for x in prompt)
            scaffold = language_map[language]["sarcasm"].format(q)
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
                "frequency_penalty": frequency_penalty,
                "presence_penalty": presence_penalty,
                "stop": "\n"
            }
            async with aiohttp.ClientSession() as session:
                async with session.post('https://api.openai.com/v1/engines/davinci/completions', headers=headers,
                                        json=params) as r:
                    if r.status == 200:
                        text = await r.json()
                        text = text['choices'][0]['text']
                        out = "Q: {} \n A: {}".format(q, text)
                        return out
                    else:
                        handle_status(r.status)
        except Exception as e:
            self.__logger.warning("Sarcasm failed with error: {}".format(e))
            return "Something went wrong. Robots too have problems..."

    async def foulmouth_answer(self, prompt, length, api_key, language="EN", temperature=0.5):
        try:
            q = " ".join(str(x) for x in prompt)
            scaffold = language_map[language]["foulmouth"].format(q)
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
                "frequency_penalty": frequency_penalty,
                "presence_penalty": presnece_penalty,
                "stop": "\n"
            }
            async with aiohttp.ClientSession() as session:
                async with session.post('https://api.openai.com/v1/engines/davinci/completions', headers=headers,
                                        json=params) as r:
                    if r.status == 200:
                        text = await r.json()
                        text = text['choices'][0]['text']
                        out = "Q: {} \n A: {}".format(q, text)
                        return out
                    else:
                        handle_status(r.status)
        except Exception as e:
            self.__logger.warning("Foulmouth failed with error: {}".format(e))
            return "Something went wrong. Robots too have problems..."
