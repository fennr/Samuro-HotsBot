from utils.library import base_functions

config = base_functions.get_config()


class HotsException(Exception):
    """Базовый класс для других исключений"""

    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return f'Custom Error, {self.message}'
        else:
            return 'Custom Error'


class CommandError(HotsException):
    pass


class HeroNotFoundError(CommandError):
    def __str__(self):
        if self.message:
            return f'Не найден герой:, {self.message}'
        else:
            return 'Не найден герой'


class WrongTalentLvl(CommandError):
    def __str__(self):
        return "Выбран невозможный уровень таланта"


class LeagueNotFound(CommandError):
    def __str__(self):
        return "Не найдены игры в шторм лиге"
