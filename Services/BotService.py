from discord.ext import commands

from Cogs.Maincog import MainCog
from Implementation.LoggingHandler import LoggingHandler
from Services.BaseService import BaseService


class BotService(BaseService):
    def __init__(self,
                 bot: commands.Bot,
                 main_cog: MainCog,
                 discord_token: str,
                 logger: LoggingHandler) -> None:
        super().__init__(logger)
        self.bot = bot
        self.bot_token = discord_token
        self.bot.add_cog(main_cog)
        self.bot.run(self.bot_token)
