# Discord GPT-3 Bot

This bot communicates with OpenAI API to provide users with Q&A, completion, sentiment analysis, emojification and
various other functions.

![Behold, GPT-3!](https://media3.giphy.com/media/YrOpuf4j4Z5NnoHmgl/giphy.gif)

Main features:

* Q&A
* Completion
* Emojification
* Sentiment Analysis
* Sarcastic Q&A
* Foulmouth Q&A
* Song Generation (lyrics)
* Headline Generation

It also features:

* per user temperature/language settings
* owner controlled server-wide response length limit
* built-in customizable allowance system so the server owners can limit user activity.
* built-in vip system so the server owners can exclude members from allowance system.

If you enjoy this bot consider donating via BTC address: 14ozvJYfChmiXwqhfzH4yCqcYR7gzwfVYT

[Click here](https://top.gg/bot/783391906309865483) to add it to your server.

Note: You need a GPT-3 beta API key to be able to use this bot. See [here](https://beta.openai.com/) for details.

# Standalone Installation

* Tested with Python 3.8
* A Mongo DB instance is required

Set the following environment variables and run ``python3 bot.py``:

* `DISCORD_TOKEN=<YOUR BOT API TOKEN>`
* `MONGO_DBUSER=<MONGO DATABASE USER>`
* `MONGO_DBPASS=<MONGO DATABASE USER PASSWORD>`
* `MONGO_HOST=<MONGO DATABASE HOST IP>`
* `MONGO_PORT=<MONGO DATABASE HOST PORT>`
* `MONGO_DBNAME=<MONGO DATABASE NAME>`

# Docker Installation

* Edit `DISCORD_TOKEN` variable inside [docker-compose.override.yml](docker-compose.override.yml)
    * Optional: Change mongo root user/pw/port values

run ``docker-compose -f docker-compose.yml -f docker-compose.override.yml up -d`` inside the directory.
