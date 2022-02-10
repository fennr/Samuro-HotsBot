

class Player:

    def __init__(self, btag, discord, mmr, league, division, winrate):
        self.btag = btag.replace(' ', '')
        self.discord = discord.replace(' ', '')
        self.mmr = mmr.replace(' ', '')
        self.league = league.replace(' ', '')
        self.division = division
        self.winrate = winrate.replace(' ', '')

    def __repr__(self):
        return f'Player({self.btag})'

    def __str__(self):
        return self.btag

    def __eq__(self, player2):
        if self.btag == player2.btag:
            return True
        else:
            return False