import unittest
from game.board import Board
from game.player import Player

class TestBoard(unittest.TestCase):
    def setUp(self):
        self.board = Board(rows=3, cols=3)  # A 3x3 grid of dots means 2x2 boxes
        self.player1 = Player("Player 1", (255, 0, 0), 'X')
        self.player2 = Player("Player 2", (0, 0, 255), 'O')

    def test_initial_state(self):
        # All lines should be False (not drawn)
        for r in range(self.board.rows):
            for c in range(self.board.cols - 1):
                self.assertFalse(self.board.h_lines[r][c])
        for r in range(self.board.rows - 1):
            for c in range(self.board.cols):
                self.assertFalse(self.board.v_lines[r][c])
        # All boxes should be None (not occupied)
        for r in range(self.board.rows - 1):
            for c in range(self.board.cols - 1):
                self.assertIsNone(self.board.boxes[r][c])

    def test_draw_horizontal(self):
        self.assertTrue(self.board.draw_horizontal(0, 0, self.player1))
        self.assertTrue(self.board.h_lines[0][0])
        # Cannot draw same line twice
        self.assertFalse(self.board.draw_horizontal(0, 0, self.player1))

    def test_draw_vertical(self):
        self.assertTrue(self.board.draw_vertical(0, 0, self.player1))
        self.assertTrue(self.board.v_lines[0][0])
        # Cannot draw same line twice
        self.assertFalse(self.board.draw_vertical(0, 0, self.player1))

    def test_check_boxes_no_box(self):
        # Draw lines that don't form a box
        self.board.draw_horizontal(0, 0, self.player1)
        self.board.draw_vertical(0, 0, self.player1)
        self.assertFalse(self.board.check_boxes(self.player1))
        self.assertEqual(self.player1.score, 0)

    def test_check_boxes_one_box(self):
        # Draw lines to form one box (top-left box: 0,0)
        self.board.draw_horizontal(0, 0, self.player1)  # Top line
        self.board.draw_vertical(0, 0, self.player1)    # Left line
        self.board.draw_horizontal(1, 0, self.player1)  # Bottom line
        self.board.draw_vertical(0, 1, self.player1)    # Right line

        self.assertTrue(self.board.check_boxes(self.player1))
        self.assertEqual(self.player1.score, 1)
        self.assertEqual(self.board.boxes[0][0], self.player1.symbol)

    def test_check_boxes_multiple_boxes_same_move(self):
        # Draw a line that completes two boxes (e.g., middle vertical line)
        # Box (0,0) needs h[0][0], v[0][0], h[1][0], v[0][1]
        # Box (0,1) needs h[0][1], v[0][1], h[1][1], v[0][2]

        # Complete box (0,0) except for v[0][1]
        self.board.draw_horizontal(0, 0, self.player1)
        self.board.draw_vertical(0, 0, self.player1)
        self.board.draw_horizontal(1, 0, self.player1)

        # Complete box (0,1) except for v[0][1]
        self.board.draw_horizontal(0, 1, self.player1)
        self.board.draw_horizontal(1, 1, self.player1)
        self.board.draw_vertical(0, 2, self.player1)

        # Now draw the shared line v[0][1] which should complete both boxes
        self.assertTrue(self.board.draw_vertical(0, 1, self.player1))
        self.assertTrue(self.board.check_boxes(self.player1)) # This should return True if any box is made
        self.assertEqual(self.player1.score, 2) # Player should get 2 points
        self.assertEqual(self.board.boxes[0][0], self.player1.symbol)
        self.assertEqual(self.board.boxes[0][1], self.player1.symbol)

    def test_is_full(self):
        self.assertFalse(self.board.is_full())
        # Fill all horizontal lines
        for r in range(self.board.rows):
            for c in range(self.board.cols - 1):
                self.board.draw_horizontal(r, c, self.player1)
        # Fill all vertical lines
        for r in range(self.board.rows - 1):
            for c in range(self.board.cols):
                self.board.draw_vertical(r, c, self.player1)
        self.assertTrue(self.board.is_full())

    def test_reset(self):
        self.board.draw_horizontal(0, 0, self.player1)
        self.board.draw_vertical(0, 0, self.player1)
        self.board.check_boxes(self.player1) # This will update score and boxes
        self.board.reset()
        self.assertFalse(self.board.h_lines[0][0])
        self.assertFalse(self.board.v_lines[0][0])
        self.assertIsNone(self.board.boxes[0][0])
        # Player scores are not reset by board.reset(), which is correct.

    def test_get_available_moves(self):
        initial_moves = self.board.get_available_moves()
        # For a 3x3 dot grid (2x2 boxes):
        # H lines: 3 rows * (3-1) cols = 3 * 2 = 6
        # V lines: (3-1) rows * 3 cols = 2 * 3 = 6
        # Total: 12 moves
        self.assertEqual(len(initial_moves), 12)

        self.board.draw_horizontal(0, 0, self.player1)
        updated_moves = self.board.get_available_moves()
        self.assertEqual(len(updated_moves), 11)
        self.assertNotIn(("h", 0, 0), updated_moves)

    def test_make_move_simulated(self):
        # Simulate a move that completes a box
        self.board.draw_horizontal(0, 0, self.player1)
        self.board.draw_vertical(0, 0, self.player1)
        self.board.draw_horizontal(1, 0, self.player1)

        # This move should complete the box (0,0)
        box_completed = self.board.make_move_simulated(("v", 0, 1), self.player1.symbol)
        self.assertTrue(box_completed)
        self.assertEqual(self.board.boxes[0][0], self.player1.symbol)

        # Simulate a move that does not complete a box
        self.board.reset()
        box_completed = self.board.make_move_simulated(("h", 0, 0), self.player1.symbol)
        self.assertFalse(box_completed)
        self.assertIsNone(self.board.boxes[0][0])

    def test_undo_move(self):
        # Draw a line and then undo it
        self.board.draw_horizontal(0, 0, self.player1)
        self.assertTrue(self.board.h_lines[0][0])
        self.board.undo_move(("h", 0, 0))
        self.assertFalse(self.board.h_lines[0][0])

        # Draw lines to complete a box, then undo the last line and check box is undone
        self.board.draw_horizontal(0, 0, self.player1)
        self.board.draw_vertical(0, 0, self.player1)
        self.board.draw_horizontal(1, 0, self.player1)
        self.board.make_move_simulated(("v", 0, 1), self.player1.symbol) # Completes box
        self.assertEqual(self.board.boxes[0][0], self.player1.symbol)

        undone_boxes = self.board.undo_move(("v", 0, 1))
        self.assertFalse(self.board.v_lines[0][1])
        self.assertIsNone(self.board.boxes[0][0]) # Box should be marked as undone
        self.assertEqual(len(undone_boxes), 1)
        self.assertEqual(undone_boxes[0], (0, 0))

    def test_is_box_completed(self):
        # Not completed
        self.assertFalse(self.board.is_box_completed(0, 0))
        # Partially completed
        self.board.draw_horizontal(0, 0, self.player1)
        self.board.draw_vertical(0, 0, self.player1)
        self.assertFalse(self.board.is_box_completed(0, 0))
        # Fully completed
        self.board.draw_horizontal(1, 0, self.player1)
        self.board.draw_vertical(0, 1, self.player1)
        self.assertTrue(self.board.is_box_completed(0, 0))

    def test_check_and_fill_boxes(self):
        # No boxes to fill initially
        filled = self.board.check_and_fill_boxes(self.player1.symbol)
        self.assertEqual(len(filled), 0)

        # Draw lines to form one box
        self.board.draw_horizontal(0, 0, self.player1)
        self.board.draw_vertical(0, 0, self.player1)
        self.board.draw_horizontal(1, 0, self.player1)
        self.board.draw_vertical(0, 1, self.player1)

        filled = self.board.check_and_fill_boxes(self.player1.symbol)
        self.assertEqual(len(filled), 1)
        self.assertEqual(filled[0], (0, 0))
        self.assertEqual(self.board.boxes[0][0], self.player1.symbol)

    def test_evaluate(self):
        # No boxes filled
        self.assertEqual(self.board.evaluate(self.player1.symbol), 0)

        # Player 1 fills one box
        self.board.draw_horizontal(0, 0, self.player1)
        self.board.draw_vertical(0, 0, self.player1)
        self.board.draw_horizontal(1, 0, self.player1)
        self.board.draw_vertical(0, 1, self.player1)
        self.board.check_and_fill_boxes(self.player1.symbol)
        self.assertEqual(self.board.evaluate(self.player1.symbol), 1)

        # Player 2 fills one box
        self.board.draw_horizontal(0, 1, self.player2)
        self.board.draw_vertical(0, 2, self.player2)
        self.board.draw_horizontal(1, 1, self.player2)
        self.board.draw_vertical(0, 1, self.player2)
        self.board.check_and_fill_boxes(self.player2.symbol)
        self.assertEqual(self.board.evaluate(self.player1.symbol), 0) # 1 for P1, 1 for P2, so 1-1=0

        self.assertEqual(self.board.evaluate(self.player2.symbol), 0) # 1 for P2, 1 for P1, so 1-1=0

if __name__ == '__main__':
    unittest.main()