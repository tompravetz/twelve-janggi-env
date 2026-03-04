from enum import Enum

GENERAL_MOVES = [(1,0),(-1,0),(0,1),(0,-1)]
MINISTER_MOVES = [(1,1),(-1,1),(1,-1),(-1,-1)]
KING_MOVES = [(1,0),(-1,0),(0,1),(0,-1),(1,1),(-1,1),(1,-1),(-1,-1)]

class PieceType(Enum):
    MINISTER = "minister"
    GENERAL = "general"
    KING = "king"
    MAN = "man"
    FEUDAL_LORD = "feudal_lord"

class Owner(Enum):
    P0 = 0
    P1 = 1

class Piece:  
    def __init__(self, owner, piece_type):
        self.owner = owner
        self.piece_type = piece_type
    
    def __repr__(self):
        return f"{self.owner}:{self.piece_type}"
    
    def get_moves(self):
        direction = 1 if self.owner == Owner.P0 else -1
        if self.piece_type == PieceType.GENERAL:
            return GENERAL_MOVES
        elif self.piece_type == PieceType.MINISTER:
            return MINISTER_MOVES
        elif self.piece_type == PieceType.KING:
            return KING_MOVES
        elif self.piece_type == PieceType.MAN:
            return [(direction,0)]
        elif self.piece_type == PieceType.FEUDAL_LORD:
            return [(direction,0),(direction,1),(direction,-1),(0,1),(0,-1),(-direction,0)]
        else:
            return []