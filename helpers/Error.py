class MyException(Exception):
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


class CommandError(MyException):
    pass


class HeroNotFoundError(CommandError):
    def __str__(self):
        if self.message:
            return f'Не найден герой:, {self.message}'
        else:
            return 'Не найден герой'
