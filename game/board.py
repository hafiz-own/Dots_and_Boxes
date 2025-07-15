from game.player import Player


class Board:
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.h_lines = [[False for _ in range(cols - 1)] for _ in range(rows)]
        self.v_lines = [[False for _ in range(cols)] for _ in range(rows - 1)]
        self.boxes = [[None for _ in range(cols - 1)] for _ in range(rows - 1)]

    def draw_horizontal(self, row: int, col: int, player: Player):
        """User gave coordinates like they are on the same row, so we got to draw a horizontal line for them"""
        if self.h_lines[row][col]:
            return False
        self.h_lines[row][col] = True
        return True

    def draw_vertical(self, row: int, col: int, player: Player):
        if self.v_lines[row][col]:
            return False
        self.v_lines[row][col] = True
        return True

    def is_full(self):
        # A board is only truly full when every possible line has been drawn
        for row in self.h_lines:
            if False in row:
                return False
        for col in self.v_lines:
            if False in col:
                return False
        return True

    def check_boxes(self, player: Player):
        box_made = False
        for r in range(self.rows - 1):
            for c in range(self.cols - 1):
                if self.boxes[r][c] is None and self.h_lines[r][c] and self.v_lines[r][c] and self.h_lines[r + 1][c] and \
                        self.v_lines[r][c + 1]:
                    """Box just got occupied"""
                    self.boxes[r][c] = player.symbol
                    player.score += 1
                    player.moves += 1
                    box_made = True
        return box_made

    def reset(self):
        self.__init__(rows=self.rows, cols=self.cols)

    def get_available_moves(self):
        moves = []
        for r in range(self.rows):
            for c in range(self.cols - 1):
                if not self.h_lines[r][c]:
                    moves.append(("h", r, c))
        for r in range(self.rows - 1):
            for c in range(self.cols):
                if not self.v_lines[r][c]:
                    moves.append(("v", r, c))
        return moves

    def make_move_simulated(self, move, symbol):
        direction, r, c = move
        completed_box = []

        if direction == "h":
            self.h_lines[r][c] = True
        else:
            self.v_lines[r][c] = True

        completed_boxes = self.check_and_fill_boxes(symbol)
        return len(completed_boxes) > 0  # True if box was completed

    def undo_move(self, move):
        direction, r, c = move
        if direction == "h":
            self.h_lines[r][c] = False
        else:
            self.v_lines[r][c] = False

        undone = []
        for row in range(self.rows - 1):
            for col in range(self.cols - 1):
                if self.boxes[row][col] is not None and not self.is_box_completed(row, col):
                    undone.append((row, col))
                    self.boxes[row][col] = None
        return undone

    def is_box_completed(self, r, c):
        return self.h_lines[r][c] and self.v_lines[r][c] and \
            self.h_lines[r + 1][c] and self.v_lines[r][c + 1]

    def check_and_fill_boxes(self, symbol):
        completed = []
        for r in range(self.rows - 1):
            for c in range(self.cols - 1):
                if self.boxes[r][c] is None and self.h_lines[r][c] and self.v_lines[r][c] and self.h_lines[r + 1][c] and \
                        self.v_lines[r][c + 1]:
                    self.boxes[r][c] = symbol
                    completed.append((r, c))
        return completed

    def evaluate(self, ai_symbol):
        ai_score = 0
        opponent_score = 0
        for row in self.boxes:
            for symbol in row:
                if symbol == ai_symbol:
                    ai_score += 1
                elif symbol is not None and symbol != ai_symbol:
                    opponent_score += 1
        return ai_score - opponent_score

    def clone(self):
        new = Board(self.rows, self.cols)
        # copy h_lines
        new.h_lines = [row.copy() for row in self.h_lines]
        # copy v_lines
        new.v_lines = [row.copy() for row in self.v_lines]
        # copy boxes
        new.boxes = [row.copy() for row in self.boxes]
        return new
