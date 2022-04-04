from typing import TypeVar, Callable

from disnake.ext import commands
from discord.ext import commands

from utils.exceptions import *
from utils.classes.Const import config

T = TypeVar("T")


def is_owner() -> Callable[[T], T]:
    """
    Проверка что пользователь является создателем бота
    """

    async def predicate(context: commands.Context) -> bool:
        print(context.author.id)
        try:
            if context.author.id not in config.owners:
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
        try:
            if context.author.id not in config.admins:
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
             959144584720580618,  # Samuro_dev
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
             959144584720580618,  # Samuro_dev
             789084039180451840,  # Ведущий
             880865537058545686,   # test
             960164733699362817,  # Генератор ивентов
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
