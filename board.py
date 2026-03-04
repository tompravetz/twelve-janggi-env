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
        for row in self.grid:
            cells=  []
            for cell in row:
                if cell is None:
                    cells.append(".")
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
        if piece == None:
            return []
        piece_moves = piece.get_moves()
        legal_moves = []
        for move in piece_moves:
            new_row = row + move[0]
            new_col = col + move[1]
            if 0 <= new_row <= 3 and 0 <= new_col <= 2:
                destination = self.grid[new_row][new_col]
                if destination is None or destination.owner != piece.owner:
                    legal_moves.append((new_row, new_col))
        return legal_moves
    
    def make_move(self, from_row, from_col, to_row, to_col):
        piece = self.grid[from_row][from_col]
        destination = self.grid[to_row][to_col]
        
        # Step 1: handle capture
        if destination is not None:
            if destination.piece_type == PieceType.FEUDAL_LORD:
                self.hands[piece.owner].append(PieceType.MAN)
            else:
                self.hands[piece.owner].append(destination.piece_type)
        self.grid[to_row][to_col] = self.grid[from_row][from_col]
        self.grid[from_row][from_col] = None
        if piece.owner == Owner.P0 and to_row == 3 and piece.piece_type == PieceType.MAN:
            self.grid[to_row][to_col].piece_type = PieceType.FEUDAL_LORD
        if piece.owner == Owner.P1 and to_row == 0 and piece.piece_type == PieceType.MAN:
            self.grid[to_row][to_col].piece_type = PieceType.FEUDAL_LORD
    
    def get_legal_drops(self, owner):
        legal_drops = []
        for row_idx in range(4):        # row_idx = 0, 1, 2, 3
            for col_idx in range(3):    # col_idx = 0, 1, 2
                cell = self.grid[row_idx][col_idx]
                if cell is None:
                    if owner == Owner.P0 and row_idx == 3:
                        continue  # skip enemy territory
                    if owner == Owner.P1 and row_idx == 0:
                        continue  # skip enemy territory
                    for piece in self.hands[owner]:
                        legal_drops.append((row_idx, col_idx, piece))
        return legal_drops

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
        if self.king_in_territory is not None:
            # find that King on the board and check if still in enemy territory
            owner = self.king_in_territory
            enemy_territory = 3 if owner == Owner.P0 else 0
            for col in range(3):
                cell = self.grid[enemy_territory][col]
                if cell is not None and cell.piece_type == PieceType.KING and cell.owner == owner:
                    return owner
        piece = self.grid[to_row][to_col]
        if piece is not None and piece.piece_type == PieceType.KING:
            if piece.owner == Owner.P0 and to_row == 3:
                self.king_in_territory = Owner.P0
            elif piece.owner == Owner.P1 and to_row == 0:
                self.king_in_territory = Owner.P1
        remaining_kings = []
        for row in self.grid:
            for cell in row:
                if cell is not None and cell.piece_type == PieceType.KING:
                    remaining_kings.append(cell.owner)
        # print("remaining kings:", remaining_kings)
        if len(remaining_kings) == 1:
            return remaining_kings[0]
        return None
