#  e4c6 ~ 2021

import asyncio

import discord
from discord.ext import commands

from Errors import CreditExhaustedError, EmptyPromptError, NotAdminError
from Helpers import user_parse
from Helpers.Emojis import thumbs_up, complete
from Helpers.Messages import help_message
from Helpers.Wrappers import check_setup
from Implementation.ApiClient import ApiClient
from Implementation.DbHandler import DbHandler
from Implementation.LoggingHandler import LoggingHandler
from Prompts import language_map


class MainCog(commands.Cog):
    def __init__(self,
                 discord_bot: commands.Bot,
                 db_handler: DbHandler,
                 api_client: ApiClient,
                 logger: LoggingHandler
                 ):
        self.__logger = logger.get_logger("main_cog")
        self.__bot = discord_bot
        self.__db = db_handler
        self.__api = api_client

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """
        From: https://gist.github.com/EvieePy/7822af90858ef65012ea500bcecf1612
        """

        if hasattr(ctx.command, 'on_error'):
            return
        cog = ctx.cog
        if cog:
            if cog._get_overridden_method(cog.cog_command_error) is not None:
                return
        ignored = (commands.CommandNotFound,)
        error = getattr(error, 'original', error)
        if isinstance(error, ignored):
            return
        if isinstance(error, commands.DisabledCommand):
            await ctx.send(f'{ctx.command} has been disabled.')
        elif isinstance(error, commands.NoPrivateMessage):
            try:
                await ctx.author.send(f'{ctx.command} can not be used in Private Messages.')
            except discord.HTTPException:
                pass
        elif isinstance(error, commands.PrivateMessageOnly):
            try:
                await ctx.author.send(f'{ctx.command} can only be used in Private Messages.')
            except discord.HTTPException:
                pass

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        owner_id = guild.owner_id
        guild_id = guild.id
        guild_name = guild.name
        if not self.__db.find_server(guild_id):
            self.__db.add_server({
                "server_id": guild_id,
                "server_name": guild_name,
                "owner_id": owner_id,
                "api_token": None,
                "response_length": 100,
                "daily_allowance": 100,
                "vips": [owner_id],
                "users": []
            })
        else:
            self.__db.update_server_name_id(guild_id, guild_name, owner_id)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        guild_id = guild.id
        self.__db.delete_server(guild_id)

    async def cog_before_invoke(self, ctx):
        await ctx.message.add_reaction(thumbs_up)

    async def cog_after_invoke(self, ctx):
        await ctx.message.remove_reaction(thumbs_up, self.__bot.user)
        await ctx.message.add_reaction(complete)

    async def check_server_token(self, ctx):
        guild_id = ctx.guild.id
        return self.__db.check_server_token(guild_id)

    @staticmethod
    async def prompt_setup(ctx):
        await ctx.send("Owner of this server hasn't configured the bot yet. If you're the owner, send this bot a DM "
                       "with command !setup.")

    @staticmethod
    async def empty_warning(ctx):
        await ctx.send("Hey, no empty prompts!")

    @staticmethod
    async def openai_down_warning(ctx):
        await ctx.send("OpenAI seems to be down. This sometimes happen and is usually resolved within minutes.")

    @staticmethod
    async def credit_warning(ctx):
        user_id, user_name = user_parse(ctx)
        await ctx.send("{}, your daily allowance is over. :cry:".format(user_name))

    @staticmethod
    async def not_admin_warning(ctx):
        user_id, user_name = user_parse(ctx)
        await ctx.send("{}, this command is only usable by admins.".format(user_name))

    @commands.command()
    async def help(self, ctx):
        await ctx.send(help_message)

    @commands.command()
    @commands.dm_only()
    async def setup(self, ctx):
        user_id, user_name = user_parse(ctx)
        owned_servers = self.__db.find_owned_servers(user_id)
        if not len(owned_servers) > 0:
            await ctx.send("You don't seem to own any servers that i'm on. If you think this is a mistake, kick the "
                           "bot and add it again.")
            return

        def check_token(m):
            return m.channel == ctx.channel

        owned_server = owned_servers[0]

        if len(owned_servers) > 1:
            message = ""
            for serv in owned_servers:
                message += "[" + str((owned_servers.index(serv) + 1)) + "]"
                message += "server name:" + serv["server_name"]
                message += ", server id:" + serv["server_id"]
                message += "\n"

            await ctx.send("I noticed that you're an admin on multiple servers. Please choose which server "
                           "you'd like to setup."
                           "{}".format(message)
                           )
            try:
                msg = await self.__bot.wait_for("message", check=check_token, timeout=60)
                choice = int(msg.content)
                owned_server = owned_servers[choice]
            except asyncio.TimeoutError:
                await ctx.send("Timeout has been reached. You can try again with !setup.")
                return
            except (TypeError, ValueError):
                await ctx.send("Invalid value. Please select a number. (e.g. '1') You can try again with !setup.")
                return

        await ctx.send("Important note: For this bot to function and process requests, it has to save your api key in "
                       "a database. This means that if the bad guys somehow access it, they can use your token and "
                       "even cause incurring charges. We cannot be held responsible for that and suggest you to host "
                       "on your own. You can do so by visiting the public repo on github("
                       "github.com/e4c6/DiscordGPT-3). If that's not a concern for "
                       "you, feel free to proceed. If you ever doubt something is going fishy, you should quickly "
                       "regenerate your api token through the developer portal on beta.openai.com.")

        server_id, server_name = owned_server["server_id"], owned_server["server_name"]
        await ctx.send("Hi {}, i see that you're the owner of {}. Now please send me your OpenAI api key within 60 "
                       "seconds. (and "
                       "nothing else).\nIt should be visible to you on https://beta.openai.com/account/api-keys.".format(
            user_name, server_name))

        try:
            msg = await self.__bot.wait_for("message", check=check_token, timeout=60)
        except asyncio.TimeoutError:
            await ctx.send("Timeout has been reached. You can try again with !setup.")
            return

        if not msg.content[0:3] == "sk-":
            await ctx.send("Your api token should start with the characters sk-. You can restart this process when "
                           "you find it.")
            return

        if len(msg.content) > 50:
            await ctx.send("Your key seems abnormally long... You can restart this process when "
                           "you find the right key.")
            return

        self.__db.set_server_token(server_id, msg.content)
        await ctx.send("Successfully set the token, enjoy! If you like this bot, please consider donating via "
                       " BTC address: 14ozvJYfChmiXwqhfzH4yCqcYR7gzwfVYT")

    @commands.command()
    @commands.guild_only()
    async def config(self, ctx):
        user_id, user_name = user_parse(ctx)
        guild_id = ctx.guild.id
        owner_id, vips, _, length, allowance = self.__db.get_server_settings(guild_id)
        if user_id != owner_id:
            raise NotAdminError
        length_str = "# Length: {}\n".format(length)
        allowance_str = "# Allowance: {}\n".format(allowance)
        vips_str = """# Vips\n"""
        for i in range(len(vips)):
            vips_str += "{} - {}\n".format(i + 1, vips[i])
        vips_str += "Note: Owners are automatically assigned a vip role."
        return await ctx.send(length_str + allowance_str + vips_str)

    @commands.command()
    @commands.guild_only()
    async def allowance(self, ctx, allowance: int):
        user_id, user_name = user_parse(ctx)
        guild_id = ctx.guild.id
        owner_id, vips, _, length, old_allowance = self.__db.get_server_settings(guild_id)
        if user_id != owner_id:
            raise NotAdminError
        self.__db.update_server_allowance(guild_id, allowance)
        return await ctx.send("Successfully updated member allowance to {}".format(allowance))

    @commands.command()
    @commands.guild_only()
    async def length(self, ctx, length: int):
        user_id, user_name = user_parse(ctx)
        guild_id = ctx.guild.id
        owner_id, vips, _, old_length, allowance = self.__db.get_server_settings(guild_id)
        if user_id != owner_id:
            raise NotAdminError
        self.__db.update_server_length(guild_id, length)
        return await ctx.send("Successfully updated response length to {}".format(length))

    @commands.command()
    @commands.guild_only()
    async def vip(self, ctx, *, member: discord.Member):
        user_id, user_name = user_parse(ctx)
        guild_id = ctx.guild.id
        owner_id, vips, _, length, allowance = self.__db.get_server_settings(guild_id)
        if user_id != owner_id:
            raise NotAdminError
        member_id, member_name = member.id, member.display_name
        self.__db.add_vip(guild_id, member_id)
        return await ctx.send("Successfully added {} to vips.".format(member_name))

    @commands.command()
    @commands.guild_only()
    async def remove_vip(self, ctx, *, member: discord.Member):
        user_id, user_name = user_parse(ctx)
        guild_id = ctx.guild.id
        owner_id, vips, _, length, allowance = self.__db.get_server_settings(guild_id)
        if user_id != owner_id:
            raise NotAdminError
        member_id, member_name = member.id, member.display_name
        self.__db.remove_vip(guild_id, member_id)
        return await ctx.send("Successfully removed {} from vips.".format(member_name))

    @commands.command()
    @commands.guild_only()
    async def credit(self, ctx):
        user_id, user_name = user_parse(ctx)
        guild_id = ctx.guild.id
        today_usage, _, _ = self.__db.get_user_settings(guild_id, user_id)
        _, _, _, _, allowance = self.__db.get_server_settings(guild_id)
        return await ctx.send("{}, your remaining daily allowance is: {}.".format(user_name, allowance - today_usage))

    @commands.command()
    @commands.guild_only()
    async def settings(self, ctx):
        user_id, user_name = user_parse(ctx)
        guild_id = ctx.guild.id
        _, language, temperature = self.__db.get_user_settings(guild_id, user_id)
        return await ctx.send(
            "{}, your language is set to: {} and temperature is set to: {}".format(user_name, language, temperature))

    @commands.command()
    @commands.guild_only()
    async def language(self, ctx, lang: str):
        user_id, user_name = user_parse(ctx)
        guild_id = ctx.guild.id
        possible_languages = list(language_map.keys())
        if lang not in possible_languages:
            return await ctx.send("{}, chosen language must be within: {}".format(user_name, possible_languages))
        today_usage, language, temperature = self.__db.get_user_settings(guild_id, user_id)
        self.__db.update_user_language(guild_id, user_id, lang)
        return await ctx.send(
            "Sucessfully updated your settings, {}. Old language: {}, New language: {}".format(user_name, language,
                                                                                               lang))

    @commands.command()
    @commands.guild_only()
    async def temperature(self, ctx, temp: float):
        user_id, user_name = user_parse(ctx)
        guild_id = ctx.guild.id
        if not 0 <= temp <= 1:
            return await ctx.send("{}, chosen temperature must equal or be within the range of 0 and 1. (e.g. 0.3) "
                                  "You can read more about temperature on "
                                  "https://towardsdatascience.com/how-to-sample-from-language-models-682bceb97277 or "
                                  "https://beta.openai.com/docs/api-reference/create-completion-via-get.".format(
                user_name))
        today_usage, language, temperature = self.__db.get_user_settings(guild_id, user_id)
        self.__db.update_user_temperature(guild_id, user_id, temp)
        return await ctx.send(
            "Sucessfully updated your settings, {}. Old temperature: {}, New temperature: {}".format(user_name,
                                                                                                     temperature,
                                                                                                     temp))

    @commands.command()
    @commands.guild_only()
    @check_setup
    async def answer(self, ctx, *prompt: str):
        usage = len(list("".join(prompt)))
        if usage == 0:
            raise EmptyPromptError
        user_id, user_name = user_parse(ctx)
        guild_id = ctx.guild.id
        today_usage, language, temperature = self.__db.get_user_settings(guild_id, user_id)
        owner_id, vips, token, length, allowance = self.__db.get_server_settings(guild_id)
        if usage + today_usage > allowance and user_id not in vips:
            raise CreditExhaustedError
        answer = await self.__api.answer(prompt, length=length, api_key=token, language=language,
                                         temperature=temperature)
        self.__db.increment_member_usage(guild_id, user_id, usage)
        return await ctx.send(discord.utils.escape_mentions(answer))

    @commands.command()
    @commands.guild_only()
    @check_setup
    async def complete(self, ctx, *prompt: str):
        usage = len(list("".join(prompt)))
        if usage == 0:
            raise EmptyPromptError
        user_id, user_name = user_parse(ctx)
        guild_id = ctx.guild.id
        today_usage, language, temperature = self.__db.get_user_settings(guild_id, user_id)
        owner_id, vips, token, length, allowance = self.__db.get_server_settings(guild_id)
        if usage + today_usage > allowance and user_id not in vips:
            raise CreditExhaustedError
        answer = await self.__api.complete(prompt, length=length, api_key=token, language=language,
                                           temperature=temperature)
        self.__db.increment_member_usage(guild_id, user_id, usage)
        return await ctx.send(discord.utils.escape_mentions(answer))

    @commands.command()
    @commands.guild_only()
    @check_setup
    async def song(self, ctx, *prompt: str):
        usage = len(list("".join(prompt)))
        if usage == 0:
            raise EmptyPromptError
        user_id, user_name = user_parse(ctx)
        guild_id = ctx.guild.id
        today_usage, language, temperature = self.__db.get_user_settings(guild_id, user_id)
        owner_id, vips, token, length, allowance = self.__db.get_server_settings(guild_id)
        if usage + today_usage > allowance and user_id not in vips:
            raise CreditExhaustedError
        answer = await self.__api.song(song_name=prompt, user_name=user_name, length=length, api_key=token,
                                       language=language,
                                       temperature=temperature)
        self.__db.increment_member_usage(guild_id, user_id, usage)
        return await ctx.send(discord.utils.escape_mentions(answer))

    @commands.command()
    @commands.guild_only()
    @check_setup
    async def foulmouth(self, ctx, *prompt: str):
        usage = len(list("".join(prompt)))
        if usage == 0:
            raise EmptyPromptError
        user_id, user_name = user_parse(ctx)
        guild_id = ctx.guild.id
        today_usage, language, temperature = self.__db.get_user_settings(guild_id, user_id)
        owner_id, vips, token, length, allowance = self.__db.get_server_settings(guild_id)
        if usage + today_usage > allowance and user_id not in vips:
            raise CreditExhaustedError
        answer = await self.__api.foulmouth_answer(prompt, length=length, api_key=token, language=language,
                                                   temperature=temperature)
        self.__db.increment_member_usage(guild_id, user_id, usage)
        return await ctx.send(discord.utils.escape_mentions(answer))

    @commands.command()
    @commands.guild_only()
    @check_setup
    async def sentiment(self, ctx, *prompt: str):
        usage = len(list("".join(prompt)))
        if usage == 0:
            raise EmptyPromptError
        user_id, user_name = user_parse(ctx)
        guild_id = ctx.guild.id
        today_usage, language, temperature = self.__db.get_user_settings(guild_id, user_id)
        owner_id, vips, token, length, allowance = self.__db.get_server_settings(guild_id)
        if usage + today_usage > allowance and user_id not in vips:
            raise CreditExhaustedError
        answer = await self.__api.sentiment(prompt, api_key=token, language=language)
        self.__db.increment_member_usage(guild_id, user_id, usage)
        return await ctx.send(discord.utils.escape_mentions(answer))

    @commands.command()
    @commands.guild_only()
    @check_setup
    async def emojify(self, ctx, *prompt: str):
        usage = len(list("".join(prompt)))
        if usage == 0:
            raise EmptyPromptError
        user_id, user_name = user_parse(ctx)
        guild_id = ctx.guild.id
        today_usage, language, temperature = self.__db.get_user_settings(guild_id, user_id)
        owner_id, vips, token, length, allowance = self.__db.get_server_settings(guild_id)
        if usage + today_usage > allowance and user_id not in vips:
            raise CreditExhaustedError
        answer = await self.__api.emojify(prompt, length=length, api_key=token, language=language,
                                          temperature=temperature)
        self.__db.increment_member_usage(guild_id, user_id, usage)
        return await ctx.send(discord.utils.escape_mentions(answer))

    @commands.command()
    @commands.guild_only()
    @check_setup
    async def sarcasm(self, ctx, *prompt: str):
        usage = len(list("".join(prompt)))
        if usage == 0:
            raise EmptyPromptError
        user_id, user_name = user_parse(ctx)
        guild_id = ctx.guild.id
        today_usage, language, temperature = self.__db.get_user_settings(guild_id, user_id)
        owner_id, vips, token, length, allowance = self.__db.get_server_settings(guild_id)
        if usage + today_usage > allowance and user_id not in vips:
            raise CreditExhaustedError
        answer = await self.__api.sarcastic_answer(prompt, length=length, api_key=token, language=language,
                                                   temperature=temperature)
        self.__db.increment_member_usage(guild_id, user_id, usage)
        return await ctx.send(discord.utils.escape_mentions(answer))

    @commands.command()
    @commands.guild_only()
    @check_setup
    async def headline(self, ctx, *prompt: str):
        usage = len(list("".join(prompt)))
        if usage == 0:
            raise EmptyPromptError
        user_id, user_name = user_parse(ctx)
        guild_id = ctx.guild.id
        today_usage, language, temperature = self.__db.get_user_settings(guild_id, user_id)
        owner_id, vips, token, length, allowance = self.__db.get_server_settings(guild_id)
        if usage + today_usage > allowance and user_id not in vips:
            raise CreditExhaustedError
        answer = await self.__api.headline(prompt, length=length, api_key=token, language=language,
                                           temperature=temperature)
        self.__db.increment_member_usage(guild_id, user_id, usage)
        return await ctx.send(discord.utils.escape_mentions(answer))
