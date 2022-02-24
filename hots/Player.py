
class Player:

    def __init__(self, btag, id, guild_id, mmr, league, division, team=None):
        self.btag = btag
        self.id = id
        self.guild_id = guild_id
        self.mmr = mmr
        self.league = league
        self.division = division
        self.team = team

    def __repr__(self):
        return f'Player({self.btag}, mmr: {self.mmr})'

    def __str__(self):
        return self.btag

    def __eq__(self, other):
        if type(self) == type(other):
            return (self.btag == other.btag) or (self.id == other.id)
        else:
            return self.mmr == other
