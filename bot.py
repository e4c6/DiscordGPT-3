#  e4c6 ~ 2021

import sys

from dependency_injector.wiring import inject, Provide

from Services.BotService import BotService
from containers import Container


@inject
def main(bot_service: BotService = Provide[Container.service]) -> None:
    return


if __name__ == "__main__":
    container = Container()
    container.config.LOG_LEVEL.from_env("LOG_LEVEL", required=True, default="DEBUG")
    container.config.PREFIX.from_env("PREFIX", required=True, default="!")
    container.config.DISCORD_TOKEN.from_env("DISCORD_TOKEN", required=True)
    container.config.MONGO_DBUSER.from_env("MONGO_DBUSER", required=True)
    container.config.MONGO_DBPASS.from_env("MONGO_DBPASS", required=True)
    container.config.MONGO_HOST.from_env("MONGO_HOST", required=True)
    container.config.MONGO_PORT.from_env("MONGO_PORT", required=True)
    container.config.MONGO_DBNAME.from_env("MONGO_DBNAME", required=True)
    container.config.MONGO_URI.from_dict({"MONGO_URI": "mongodb://{}:{}@{}:{}".format(container.config.MONGO_DBUSER,
                                                                                      container.config.MONGO_DBPASS,
                                                                                      container.config.MONGO_HOST,
                                                                                      container.config.MONGO_PORT)})
    container.wire(modules=[sys.modules[__name__]])
    main()

    # Test Instructions:
    # with container.api_client.override(mock.Mock()):
    #     main()  # <-- overridden dependency is injected automatically
