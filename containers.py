from dependency_injector import containers, providers
from discord.ext import commands

from Cogs.Maincog import MainCog
from Implementation.ApiClient import ApiClient
from Implementation.DbHandler import DbHandler
from Implementation.LoggingHandler import LoggingHandler
from Services.BotService import BotService


class Container(containers.DeclarativeContainer):
    config = providers.Configuration()

    logger = providers.Singleton(
        LoggingHandler,
        log_level=config.LOG_LEVEL
    )

    api_client = providers.Singleton(
        ApiClient,
        logger=logger
    )

    db_handler = providers.Singleton(
        DbHandler,
        logger=logger,
        mongo_uri=config.MONGO_URI,
        mongo_db_name=config.MONGO_DBNAME
    )

    bot = providers.Singleton(
        commands.Bot,
        command_prefix=config.PREFIX,
        help_command=None
    )

    main_cog = providers.Singleton(
        MainCog,
        logger=logger,
        discord_bot=bot,
        db_handler=db_handler,
        api_client=api_client,
    )

    service = providers.Factory(
        BotService,
        logger=logger,
        bot=bot,
        main_cog=main_cog,
        discord_token=config.DISCORD_TOKEN
    )
