

class Player:

    def __init__(self, btag, id, guild_id, mmr, league, division, winrate, win=0, lose=0, search=False):
        self.btag = btag
        self.id = id
        self.guild_id = guild_id
        self.mmr = mmr
        self.league = league
        self.division = division
        self.win = win
        self.lose = lose
        self.winrate = winrate
        self.search = search

    def __repr__(self):
        return f'Player({self.btag}, mmr: {self.mmr})'

    def __str__(self):
        return self.btag

    def __eq__(self, player2):
        if self.btag == player2.btag:
            return True
        else:
            return False