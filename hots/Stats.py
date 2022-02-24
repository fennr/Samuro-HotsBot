class Stats:

    def __init__(self, id, guild_id, btag, win=0, lose=0, points=0):
        self.btag = btag
        self.id = id
        self.guild_id = guild_id
        self.win = win
        self.lose = lose
        self.points = points

    def __repr__(self):
        return f'PlayerStats({self.btag}, id: {self.id})'

    def __str__(self):
        return f"Stats(id={self.id}, guild_id={self.guild_id}, btag={self.btag} " \
               f"win={self.win}, lose={self.lose}, points={self.points})"

    def __eq__(self, other):
        if type(self) == type(other):
            return (self.btag == other.btag) or (self.id == other.id)
        else:
            return (self.id == other) or (self.btag == other)