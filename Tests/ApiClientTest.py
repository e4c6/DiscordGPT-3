import os

import pytest

from Implementation.ApiClient import ApiClient
from Implementation.LoggingHandler import LoggingHandler, LogLevel

key = os.environ.get("OPENAI_API_KEY")
if key is None:
    raise ValueError("OPENAI_API_KEY environment variable is required")

logger = LoggingHandler(LogLevel.DEBUG)
client = ApiClient(logger)


@pytest.mark.asyncio
async def test_answer():
    answer = await client.answer(question=("is this a test?",), length=5, api_key=key, language="EN",
                                 temperature=0.5)
    assert answer is not None


@pytest.mark.asyncio
async def test_sentiment():
    sentiment = await client.sentiment(prompt=("happy day",), api_key=key, language="EN")
    assert sentiment is not None


@pytest.mark.asyncio
async def test_emojify():
    emoji = await client.emojify(prompt=("test",), length=5, api_key=key, language="EN", temperature=0.5)
    assert emoji is not None


@pytest.mark.asyncio
async def test_sarcastic_answer():
    answer = await client.sarcastic_answer(prompt=("how are you?",), length=5, api_key=key, language="EN",
                                           temperature=0.5)
    assert answer is not None


@pytest.mark.asyncio
async def foulmouth_answer():
    answer = await client.foulmouth_answer(prompt=("how are you?",), length=5, api_key=key, language="EN",
                                           temperature=0.5)
    assert answer is not None


@pytest.mark.asyncio
async def test_headline():
    headline = await client.headline(prompt=("news!",), length=5, api_key=key, language="EN", temperature=0.5)
    assert headline is not None


@pytest.mark.asyncio
async def test_song():
    song = await client.song(song_name=("will i pass?",), user_name="test", length=5, api_key=key, language="EN",
                             temperature=0.5)
    assert song is not None


@pytest.mark.asyncio
async def test_complete():
    completion = await client.complete(prompt=("then i said",), length=5, api_key=key, language="EN",
                                       temperature=0.5)
    assert completion is not None
