import json
import yaml
import os
import sys
from typing import TypeVar, Callable

from disnake.ext import commands
from discord.ext import commands

from utils.exceptions import *

T = TypeVar("T")


def is_owner() -> Callable[[T], T]:
    """
    Проверка что пользователь является создателем бота
    """

    async def predicate(context: commands.Context) -> bool:
        print(context.author.id)
        if not os.path.isfile("config.yaml"):
            sys.exit("'config.yaml' not found! Please add it and try again.")
        else:
            with open("config.yaml") as file:
                data = yaml.load(file, Loader=yaml.FullLoader)
            try:
                if context.author.id not in data["owners"]:
                    raise UserNotOwner
            except UserNotOwner as e:
                print(e)
            return True

    return commands.check(predicate)


def is_admin() -> Callable[[T], T]:
    """
    Проверка что пользователь является администратором бота
    """
    async def predicate(context: commands.Context) -> bool:
        if not os.path.isfile("config.yaml"):
            sys.exit("'config.yaml' not found! Please add it and try again.")
        else:
            with open("config.yaml") as file:
                data = yaml.load(file, Loader=yaml.FullLoader)
            try:
                if context.author.id not in data["admins"]:
                    raise UserNotAdmin
            except UserNotAdmin as e:
                print(e)
            return True

    return commands.check(predicate)


def is_samuro_dev() -> Callable[[T], T]:
    '''
    Проверка налачия роли Samuro_dev
    '''
    async def predicate(context: commands.Context) -> bool:
        good_roles = [
             946480695218429952,  # Samuro_dev
             880865537058545686  # test
        ]
        flag = False
        for role in context.author.roles:
            if role.id in good_roles:
                flag = True
        try:
            if not flag:
                raise UserNotAdmin
        except UserNotAdmin as e:
            print(e)
        return flag
    return commands.check(predicate)

def is_lead() -> Callable[[T], T]:
    """
    Проверка наличия роли ведущего
    """
    async def predicate(context: commands.Context) -> bool:
        good_roles = [
             703884580041785344,  # Создатель
             703884637755408466,  # Админ
             946480695218429952,  # Samuro_dev
             789084039180451840,  # Ведущий
             880865537058545686  # test
        ]
        flag = False
        for role in context.author.roles:
            if role.id in good_roles:
                flag = True
        try:
            if not flag:
                raise UserNotAdmin
        except UserNotAdmin as e:
            print(e)
        return flag
    return commands.check(predicate)


def not_blacklisted() -> Callable[[T], T]:
    """
    Проверка что пользователь не находится в черном списке
    """

    async def predicate(context: commands.Context) -> bool:
        with open("blacklist.json") as file:
            data = json.load(file)
        if context.author.id in data["ids"]:
            await context.send('Вам недоступна данная команда')
            raise UserBlacklisted
        return True

    return commands.check(predicate)