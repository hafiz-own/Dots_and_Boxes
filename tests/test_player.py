import unittest
from game.player import Player

class TestPlayer(unittest.TestCase):
    def setUp(self):
        self.player = Player("Test Player", (255, 0, 0), 'X')

    def test_initial_state(self):
        self.assertEqual(self.player.name, "Test Player")
        self.assertEqual(self.player.color, (255, 0, 0))
        self.assertEqual(self.player.symbol, 'X')
        self.assertEqual(self.player.score, 0)
        self.assertEqual(self.player.moves, 0)

    def test_increment_score(self):
        self.player.increment_score()
        self.assertEqual(self.player.score, 1)
        self.player.increment_score()
        self.assertEqual(self.player.score, 2)

    def test_str_representation(self):
        self.assertEqual(str(self.player), "Player: Test Player, Score: 0")
        self.player.increment_score()
        self.assertEqual(str(self.player), "Player: Test Player, Score: 1")

if __name__ == '__main__':
    unittest.main()