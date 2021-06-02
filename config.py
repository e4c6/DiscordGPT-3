import os
from logging import DEBUG

# SECRETS
DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")
MONGO_DBUSER = os.environ.get("MONGO_DBUSER")
MONGO_DBPASS = os.environ.get("MONGO_DBPASS")
MONGO_HOST = os.environ.get("MONGO_HOST")
MONGO_PORT = os.environ.get("MONGO_PORT")
MONGO_DBNAME = os.environ.get("MONGO_DBNAME")
MONGO_URI = "mongodb://{}:{}@{}:{}".format(MONGO_DBUSER, MONGO_DBPASS, MONGO_HOST, MONGO_PORT)

# BOT CONFIGS
PREFIX = "!"

# LOG SETTINGS
LOG_LEVEL = DEBUG
