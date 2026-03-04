from board import Board
from piece import Owner, Piece, PieceType
class Game:
    def __init__(self):
        self.board = Board()
        self.board.setup()
        self.current_player = Owner.P0
        self.winner = None
    
    def step(self, turn):
        action = turn[0]
        if action == "move":
            from_row, from_col, to_row, to_col = turn[1], turn[2], turn[3], turn[4]
            piece = self.board.grid[from_row][from_col]
            if piece is None or piece.owner != self.current_player:
                return None
            self.board.make_move(from_row, from_col, to_row, to_col)
            result = self.board.check_winner(to_row, to_col)
            if result is not None:
                self.winner = result
        elif action == "drop":
            piece_type, row, col = turn[1], turn[2], turn[3]
            if piece_type not in self.board.hands[self.current_player]:
                return None
            self.board.drop_piece(self.current_player, piece_type, row, col)
            result = self.board.check_winner(row, col)
            if result is not None:
                self.winner = result
        if self.current_player == Owner.P0:
            self.current_player = Owner.P1
        else:
            self.current_player = Owner.P0
        return self.winner
    
    def get_all_legal_actions(self):
        actions = []
        for row_idx in range(4):
            for col_idx in range(3):
                cell = self.board.grid[row_idx][col_idx]
                if cell is not None and cell.owner == self.current_player:
                    # get legal moves for this piece and add to actions
                    # hint: tag each as ("move", from_row, from_col, to_row, to_col)
                    for to_row, to_col in self.board.get_legal_moves(row_idx, col_idx):
                        actions.append(("move", row_idx, col_idx, to_row, to_col))
        # add legal drops
        for drop in self.board.get_legal_drops(self.current_player):
            actions.append(("drop", drop[2], drop[0], drop[1]))
        # return actions
        return actions