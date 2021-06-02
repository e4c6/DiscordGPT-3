from datetime import datetime

import pymongo

import logger


class DBHandler:
    def __init__(self, mongu_uri, mongo_dbname):
        self.__client = pymongo.MongoClient(mongu_uri)
        self.__db = self.__client[mongo_dbname]
        self.__servers = self.__db["gpt3_servers"]
        self.__logger = logger.get_logger("db_handler")

    def check_server_token(self, server_id):
        result = self.__servers.find_one({"server_id": server_id})
        if result is None or result["api_token"] is None:
            return False
        return True

    def find_server(self, server_id):
        return self.__servers.find_one({"server_id": server_id})

    def add_server(self, server):
        try:
            self.__servers.insert_one(server)
        except Exception as e:
            self.__logger.critical("Unable to add server: {}, e: {}".format(server, e))

    def delete_server(self, server_id):
        return self.__servers.delete_one({"server_id": server_id})

    def update_server_name_id(self, server_id, server_name, owner_id):
        return self.__servers.update_one({"server_id": server_id},
                                         {"$set": {"owner_id": owner_id, "server_name": server_name}})

    def find_owned_servers(self, user_id):
        return list(self.__servers.find({"owner_id": user_id}))

    def get_server_settings(self, server_id):
        settings = self.__servers.find_one({"server_id": server_id},
                                           {"owner_id": 1, "vips": 1, "api_token": 1, "response_length": 1,
                                            "daily_allowance": 1})
        return settings["owner_id"], settings["vips"], settings["api_token"], settings["response_length"], settings[
            "daily_allowance"]

    def set_server_token(self, server_id, token):
        return self.__servers.update_one({"server_id": server_id}, {"$set": {"api_token": token}})

    def update_server_allowance(self, server_id, allowance):
        return self.__servers.update_one({"server_id": server_id}, {"$set": {"daily_allowance": allowance}})

    def update_server_length(self, server_id, length):
        return self.__servers.update_one({"server_id": server_id}, {"$set": {"response_length": length}})

    def get_user(self, server_id, user_id):
        user = self.__servers.find_one({"server_id": server_id, "users.id": user_id}, {"users.$": 1})
        if user:
            return user["users"][0]
        user = {
            "id": user_id,
            "usage": {},
            "settings": {
                "language": "EN",
                "temperature": 0.5
            }
        }
        self.add_user(server_id, user)
        return user

    def get_user_settings(self, server_id, user_id):
        today = datetime.today().strftime("%d-%m-%y")
        user = self.get_user(server_id, user_id)
        if today in user["usage"].keys():
            today_usage = user["usage"][today]
        else:
            today_usage = 0
        language = user["settings"]["language"]
        temperature = user["settings"]["temperature"]
        return today_usage, language, temperature

    def add_user(self, server_id, user):
        return self.__servers.update_one({"server_id": server_id}, {"$push": {"users": user}})

    def add_vip(self, server_id, user_id):
        return self.__servers.update_one({"server_id": server_id}, {"$addToSet": {"vips": user_id}})

    def remove_vip(self, server_id, user_id):
        return self.__servers.update_one({"server_id": server_id}, {"$pull": {"vips": user_id}})

    def increment_member_usage(self, server_id, user_id, usage):
        today = datetime.today().strftime("%d-%m-%y")
        return self.__servers.update_one(
            {"server_id": server_id,
             "users":
                 {"$elemMatch":
                     {
                         "id": user_id
                     }
                 }
             },
            {"$inc":
                 {"users.$.usage.{}".format(today): usage}
             }, upsert=True)

    def update_user_language(self, server_id, user_id, lang):
        return self.__servers.update_one(
            {"server_id": server_id,
             "users":
                 {"$elemMatch":
                     {
                         "id": user_id
                     }
                 }
             },
            {"$set":
                 {"users.$.settings.language": lang}
             })

    def update_user_temperature(self, server_id, user_id, temp):
        return self.__servers.update_one(
            {"server_id": server_id,
             "users":
                 {"$elemMatch":
                     {
                         "id": user_id
                     }
                 }
             },
            {"$set":
                 {"users.$.settings.temperature": temp}
             })
