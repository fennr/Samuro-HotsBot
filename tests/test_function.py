import pytest
from utils.library import hots
from utils.classes.Hero import Hero


class Test:
    good_name = 'Самуро'
    bad_name = 'Cомуро'

    def test_read_hero_from_message(self):
        try:
            hero, embed = hots.read_hero_from_message(((self.bad_name),), author='fenrir#5455', command='hero')
        except:
            pytest.fail('Считывание героя ушло в дамп')
        assert type(hero) is Hero

    def test_find_heroes_list(self):
        hero_list = hots.find_heroes(hero_name=self.bad_name)
        assert hero_list is not []

    def test_find_heroes_types(self):
        hero_list = hots.find_heroes(hero_name=self.bad_name)
        assert type(hero_list[0]) is Hero
