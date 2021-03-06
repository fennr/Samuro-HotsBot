from typing import TypeVar, Callable
from discord.ext import commands

from utils.exceptions import *
from utils.classes.Const import config

T = TypeVar("T")


def is_owner() -> Callable[[T], T]:
    """
    Проверка что пользователь является создателем бота
    """

    async def predicate(context: commands.Context) -> bool:
        try:
            if context.author.id not in config.owners:
                raise UserNotOwner
        except UserNotOwner as e:
            print(e)
            return False
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
            return False
        return True

    return commands.check(predicate)


def is_samuro_dev() -> Callable[[T], T]:
    '''
    Проверка налачия роли Samuro_dev
    '''
    async def predicate(context: commands.Context) -> bool:
        good_roles = [
             959144584720580618,  # Samuro_dev
             274543866743357442,  # Stalk admin
             880865537058545686,  # test
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
             959144584720580618,  # Samuro_dev
             789084039180451840,  # Ведущий
             880865537058545686,  # test
             274543866743357442,  # Stalk admin
             961241562036174858,  # 5x5 admin
             972888717574414366,  # Букмекер
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
