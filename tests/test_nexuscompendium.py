import pytest

from utils.hots import nexuscompendium


class Tests:
    def test_ranked(self):
        try:
            embed = nexuscompendium.ranked()
        except:
            pytest.fail("Ранкед не отвечает")

    def test_sales(self):
        try:
            embed = nexuscompendium.sales()
        except:
            pytest.fail("Скидки не отвечают")

    def test_weekly_rotation(self):
        try:
            embed = nexuscompendium.weekly_rotation()
        except:
            pytest.fail("Ротация сломалась, проверь героев")

