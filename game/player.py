class Player:
    def __init__(self, name, color, symbol=None):
        self.score = 0
        self.name = name
        self.color = color
        self.symbol = symbol
        self.moves = 0

    def increment_score(self):
        self.score += 1
        return self.score

    def __str__(self):
        return f"Player: {self.name}, Score: {self.score}"
