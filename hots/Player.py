

class Player:

    def __init__(self, btag, discord, guild_id, mmr, league, division, winrate, win=0, lose=0, search=False):
        self.btag = btag.replace(' ', '')
        self.discord = discord
        self.guild_id = guild_id
        self.mmr = mmr
        self.league = league.replace(' ', '')
        self.division = division
        self.win = win
        self.lose = lose
        self.winrate = winrate.replace(' ', '')
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