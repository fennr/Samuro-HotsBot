

class Player:

    def __init__(self, btag, discord, mmr, league, division, winrate, win=0, lose=0, search=False):
        self.btag = btag.replace(' ', '')
        self.discord = discord
        self.mmr = ''.join([i for i in mmr if i.isdigit()]).replace(' ', '')
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