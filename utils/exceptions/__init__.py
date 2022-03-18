from .hots_exceptions import *


class UserBlacklisted(Exception):
    """
    Thrown when a user is attempting something, but is blacklisted.
    """

    def __init__(self, message="User is blacklisted!"):
        self.message = message
        super().__init__(self.message)


class UserNotOwner(Exception):
    """
    Thrown when a user is attempting something, but is not an owner of the bot.
    """

    def __init__(self, message="Данная команда доступна только *fenrir#5455*"):
        self.message = message
        super().__init__(self.message)


class UserNotAdmin(Exception):
    """
    Thrown when a user is attempting something, but is not an owner of the bot.
    """

    def __init__(self, message="Данная команда доступна только администратору"):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message
