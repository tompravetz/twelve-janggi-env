from piece import Piece, PieceType, Owner


class Board:
    def __init__(self):
        self.grid = [
            [None, None, None],
            [None, None, None],
            [None, None, None],
            [None, None, None]
        ]
        self.hands = {
            Owner.P0: [],
            Owner.P1: []
        }
        self.king_in_territory = None

    def __repr__(self):
        SHORT = {
            PieceType.MINISTER: "Mi",
            PieceType.GENERAL: "Ge",
            PieceType.KING: "Ki",
            PieceType.MAN: "Ma",
            PieceType.FEUDAL_LORD: "FL",
        }
        rows = []
        for row in reversed(range(4)):
            cells = []
            for cell in self.grid[row]:
                if cell is None:
                    cells.append(" . ")
                else:
                    cells.append(f"{cell.owner.value}{SHORT[cell.piece_type]}")
            rows.append(" ".join(cells))
        rows.append(f"P0 hand: {self.hands[Owner.P0]}")
        rows.append(f"P1 hand: {self.hands[Owner.P1]}")
        return "\n".join(rows)

    def setup(self):
        self.grid[0][0] = Piece(owner=Owner.P0, piece_type=PieceType.MINISTER)
        self.grid[0][1] = Piece(owner=Owner.P0, piece_type=PieceType.KING)
        self.grid[0][2] = Piece(owner=Owner.P0, piece_type=PieceType.GENERAL)
        self.grid[1][1] = Piece(owner=Owner.P0, piece_type=PieceType.MAN)
        self.grid[2][1] = Piece(owner=Owner.P1, piece_type=PieceType.MAN)
        self.grid[3][0] = Piece(owner=Owner.P1, piece_type=PieceType.GENERAL)
        self.grid[3][1] = Piece(owner=Owner.P1, piece_type=PieceType.KING)
        self.grid[3][2] = Piece(owner=Owner.P1, piece_type=PieceType.MINISTER)

    def get_legal_moves(self, row, col):
        piece = self.grid[row][col]
        if piece is None:
            return []
        legal_moves = []
        for move in piece.get_moves():
            new_row = row + move[0]
            new_col = col + move[1]
            if 0 <= new_row <= 3 and 0 <= new_col <= 2:
                destination = self.grid[new_row][new_col]
                if destination is None or destination.owner != piece.owner:
                    legal_moves.append((new_row, new_col))
        return legal_moves

    def get_legal_drops(self, owner):
        legal_drops = []
        for row_idx in range(4):
            for col_idx in range(3):
                cell = self.grid[row_idx][col_idx]
                if cell is None:
                    if owner == Owner.P0 and row_idx == 3:
                        continue
                    if owner == Owner.P1 and row_idx == 0:
                        continue
                    for piece_type in self.hands[owner]:
                        legal_drops.append((row_idx, col_idx, piece_type))
        return legal_drops

    def make_move(self, from_row, from_col, to_row, to_col):
        piece = self.grid[from_row][from_col]
        destination = self.grid[to_row][to_col]

        if destination is not None:
            captured_type = PieceType.MAN if destination.piece_type == PieceType.FEUDAL_LORD else destination.piece_type
            self.hands[piece.owner].append(captured_type)

        self.grid[to_row][to_col] = piece
        self.grid[from_row][from_col] = None

        if piece.piece_type == PieceType.MAN:
            if piece.owner == Owner.P0 and to_row == 3:
                self.grid[to_row][to_col].piece_type = PieceType.FEUDAL_LORD
            elif piece.owner == Owner.P1 and to_row == 0:
                self.grid[to_row][to_col].piece_type = PieceType.FEUDAL_LORD

    def drop_piece(self, owner, piece_type, row, col):
        if self.grid[row][col] is not None:
            return False
        if owner == Owner.P0 and row == 3:
            return False
        if owner == Owner.P1 and row == 0:
            return False
        self.grid[row][col] = Piece(owner=owner, piece_type=piece_type)
        self.hands[owner].remove(piece_type)
        return True

    def check_winner(self, to_row, to_col):
        # Check if a previously marched king is still in enemy territory
        if self.king_in_territory is not None:
            owner = self.king_in_territory
            enemy_territory = 3 if owner == Owner.P0 else 0
            for col in range(3):
                cell = self.grid[enemy_territory][col]
                if cell is not None and cell.piece_type == PieceType.KING and cell.owner == owner:
                    return owner
            self.king_in_territory = None

        # Check if a king was captured
        remaining_kings = []
        for row in self.grid:
            for cell in row:
                if cell is not None and cell.piece_type == PieceType.KING:
                    remaining_kings.append(cell.owner)
        if len(remaining_kings) == 1:
            return remaining_kings[0]

        # Check if a king just marched into enemy territory
        piece = self.grid[to_row][to_col]
        if piece is not None and piece.piece_type == PieceType.KING:
            if piece.owner == Owner.P0 and to_row == 3:
                self.king_in_territory = Owner.P0
            elif piece.owner == Owner.P1 and to_row == 0:
                self.king_in_territory = Owner.P1

        return None