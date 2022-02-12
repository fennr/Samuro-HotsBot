import json
import yaml
import os
import sys
from typing import TypeVar, Callable

from disnake.ext import commands

from exceptions import *

T = TypeVar("T")


def is_owner() -> Callable[[T], T]:
    """
    This is a custom check to see if the user executing the command is an owner of the bot.
    """

    async def predicate(context: commands.Context) -> bool:
        print(context.author.id)
        if not os.path.isfile("config.yaml"):
            sys.exit("'config.yaml' not found! Please add it and try again.")
        else:
            with open("config.yaml") as file:
                data = yaml.load(file, Loader=yaml.FullLoader)
            print(data["owners"])
            if context.author.id not in data["owners"]:
                await context.send("Данная команда доступна только *fenrir#5455*")
                raise UserNotOwner
            return True

    return commands.check(predicate)


def is_admin() -> Callable[[T], T]:
    """
    This is a custom check to see if the user executing the command is an owner of the bot.
    """
    async def predicate(context: commands.Context) -> bool:
        if not os.path.isfile("config.yaml"):
            sys.exit("'config.yaml' not found! Please add it and try again.")
        else:
            with open("config.yaml") as file:
                data = yaml.load(file, Loader=yaml.FullLoader)
            print(context.author.id)
            print(data["admins"])
            if context.author.id not in data["admins"]:
                await context.send('Данная команда доступна только администратору')
                raise UserNotAdmin
            return True

    return commands.check(predicate)


def not_blacklisted() -> Callable[[T], T]:
    """
    This is a custom check to see if the user executing the command is blacklisted.
    """

    async def predicate(context: commands.Context) -> bool:
        with open("blacklist.json") as file:
            data = json.load(file)
        if context.author.id in data["ids"]:
            await context.send('Вам недоступна данная команда')
            raise UserBlacklisted
        return True

    return commands.check(predicate)