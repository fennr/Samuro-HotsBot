class Team:

    def __init__(self, id, name, leader, members=1, points=0):
        self.id = id
        self.name = name
        self.leader = leader
        self.members = members
        self.points = points

    def __repr__(self):
        return f'Team({self.name}, id: {self.id})'

    def __str__(self):
        return f"Team(id={self.id}, name={self.name}, leader={self.leader}, members={self.members}, points={self.points})"

    def __eq__(self, other):
        if type(self) == type(other):
            return (self.id == other.id) or (self.name == other.name) or (self.leader == other.leader)