from collections import namedtuple
from cogs.profile import get_heroesprofile_data, get_player, change_mmr, get_discord_id
from utils.classes.Player import Player

record = dict(btag='Se7eN#22874',
              id=196583204164075520,
              league='Master',
              division=0,
              winrate='50%',
              mmr=2874,
              win=2,
              lose=1,
              search=True,
              guild_id=845658540341592096
              )
nt_record = namedtuple('record', record.keys())(*record.values())

profile = Player(btag='Se7eN#22874', id=196583204164075520, league='Master', mmr=2980, division=0,
                 winrate='50%', win=2, lose=1, search=True, guild_id=845658540341592096)


class Test_profile:

    def test_get_heroesprofile_data(self):
        profile = get_heroesprofile_data('fenrir#2372', 196583204164075520, 845658540341592096)
        assert isinstance(profile, Player)

    def test_get_player(self):
        profile = get_player(nt_record)
        assert isinstance(profile, Player)

    def test_change_mmr(self):
        mmr_plus = change_mmr(profile, 5, plus=True)
        mmr_minus = change_mmr(profile, 5, plus=False)
        assert mmr_plus == 2985 and mmr_minus == 2975

    def test_get_discord_id(self):
        member = '<@!261177857126957056>'
        real_id = 261177857126957056
        id = get_discord_id(member)
        assert id == real_id