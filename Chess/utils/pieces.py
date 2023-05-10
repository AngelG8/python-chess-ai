from enum import Enum
from typing import Dict

# Dictionaries to express positions in rank file notation
RANKS_TO_ROWS: Dict[str, int] = {"1": 7, "2": 6, "3": 5, "4": 4,
                                 "5": 3, "6": 2, "7": 1, "8": 0}
ROWS_TO_RANKS: Dict[int, str] = {v: k for k, v in RANKS_TO_ROWS.items()}
FILES_TO_COLS: Dict[str, int] = {"A": 0, "B": 1, "C": 2, "D": 3,
                                 "E": 4, "F": 5, "G": 6, "H": 7}
COLS_TO_FILES: Dict[int, str] = {v: k for k, v in FILES_TO_COLS.items()}


def get_rank_file(row: int, col: int) -> str:
    """
    Converts a row, column notation of a square to rank, file notation.

    Parameters:
        row (int): The row of the square.
        col (int): The column of the square.

    Returns:
        str: A rank, file representation of a square (e.g. "A4", "D8", "E5").
    """
    return COLS_TO_FILES[col] + ROWS_TO_RANKS[row]


class Pieces(Enum):
    """
    Contains all available chess pieces and an empty piece to represent an empty square.
    """
    NO_PIECE = 0,
    BLACK_PAWN = 1,
    BLACK_ROOK = 2,
    BLACK_KNIGHT = 3,
    BLACK_BISHOP = 4,
    BLACK_QUEEN = 5,
    BLACK_KING = 6,
    WHITE_PAWN = 7,
    WHITE_ROOK = 8,
    WHITE_KNIGHT = 9,
    WHITE_BISHOP = 10,
    WHITE_QUEEN = 11,
    WHITE_KING = 12


MATERIAL_VALUES: Dict[str, int] = {
    "p": 100,
    "R": 500,
    "N": 320,
    "B": 330,
    "Q": 900,
    "K": 0
}

CHECKMATE = 100000
STALEMATE = 0


PIECE_SQUARE_TABLES_WHITE = {
    "PAWN": [
        [0, 0, 0, 0, 0, 0, 0, 0],
        [50, 50, 50, 50, 50, 50, 50, 50],
        [10, 10, 20, 30, 30, 20, 10, 10],
        [5, 5, 10, 25, 25, 10, 5, 5],
        [0, 0, 0, 20, 20, 0, 0, 0],
        [5, -5, -10, 0, 0, -10, -5, 5],
        [5, 10, 10, -20, -20, 10, 10, 5],
        [0, 0, 0, 0, 0, 0, 0, 0]
    ],
    "KNIGHT": [
        [-50, -40, -30, -30, -30, -30, -40, -50],
        [-40, -20, 0, 0, 0, 0, -20, -40],
        [-30, 0, 10, 15, 15, 10, 0, -30],
        [-30, 5, 15, 20, 20, 15, 5, -30],
        [-30, 0, 15, 20, 20, 15, 0, -30],
        [-30, 5, 10, 15, 15, 10, 5, -30],
        [-40, -20, 0, 5, 5, 0, -20, -40],
        [-50, -40, -30, -30, -30, -30, -40, -50]
    ],
    "BISHOP": [
        [-20, -10, -10, -10, -10, -10, -10, -20],
        [-10, 0, 0, 0, 0, 0, 0, -10],
        [-10, 0, 5, 10, 10, 5, 0, -10],
        [-10, 5, 5, 10, 10, 5, 5, -10],
        [-10, 0, 10, 10, 10, 10, 0, -10],
        [-10, 10, 10, 10, 10, 10, 10, -10],
        [-10, 5, 0, 0, 0, 0, 5, -10],
        [-20, -10, -10, -10, -10, -10, -10, -20]
    ],
    "ROOK": [
        [0, 0, 0, 0, 0, 0, 0, 0],
        [5, 10, 10, 10, 10, 10, 10, 5],
        [-5, 0, 0, 0, 0, 0, 0, -5],
        [-5, 0, 0, 0, 0, 0, 0, -5],
        [-5, 0, 0, 0, 0, 0, 0, -5],
        [-5, 0, 0, 0, 0, 0, 0, -5],
        [-5, 0, 0, 0, 0, 0, 0, -5],
        [0, 0, 0, 5, 5, 0, 0, 0]
    ],
    "QUEEN": [
        [-20, -10, -10, -5, -5, -10, -10, -20],
        [-10, 0, 0, 0, 0, 0, 0, -10],
        [-10, 0, 5, 5, 5, 5, 0, -10],
        [-5, 0, 5, 5, 5, 5, 0, -5],
        [0, 0, 5, 5, 5, 5, 0, -5],
        [-10, 5, 5, 5, 5, 5, 0, -10],
        [-10, 0, 5, 0, 0, 0, 0, -10],
        [-20, -10, -10, -5, -5, -10, -10, -20]
    ],
    "KING_MID": [
        [-30, -40, -40, -50, -50, -40, -40, -30],
        [-30, -40, -40, -50, -50, -40, -40, -30],
        [-30, -40, -40, -50, -50, -40, -40, -30],
        [-30, -40, -40, -50, -50, -40, -40, -30],
        [-20, -30, -30, -40, -40, -30, -30, -20],
        [-10, -20, -20, -20, -20, -20, -20, -10],
        [20, 20, 0, 0, 0, 0, 20, 20],
        [20, 30, 10, 0, 0, 10, 30, 20]
    ],
    "KING_LATE": [
        [-50, -40, -30, -20, -20, -30, -40, -50],
        [-30, -20, -10, 0, 0, -10, -20, -30],
        [-30, -10, 20, 30, 30, 20, -10, -30],
        [-30, -10, 30, 40, 40, 30, -10, -30],
        [-30, -10, 30, 40, 40, 30, -10, -30],
        [-30, -10, 20, 30, 30, 20, -10, -30],
        [-30, -30, 0, 0, 0, 0, -30, -30],
        [-50, -30, -30, -30, -30, -30, -30, -50]
    ]
}

PIECE_POSITION_SCORES = {
    "wp": PIECE_SQUARE_TABLES_WHITE["PAWN"],
    "bp": PIECE_SQUARE_TABLES_WHITE["PAWN"][::-1],
    "wN": PIECE_SQUARE_TABLES_WHITE["KNIGHT"],
    "bN": PIECE_SQUARE_TABLES_WHITE["KNIGHT"][::-1],
    "wB": PIECE_SQUARE_TABLES_WHITE["BISHOP"],
    "bB": PIECE_SQUARE_TABLES_WHITE["BISHOP"][::-1],
    "wR": PIECE_SQUARE_TABLES_WHITE["ROOK"],
    "bR": PIECE_SQUARE_TABLES_WHITE["ROOK"][::-1],
    "wQ": PIECE_SQUARE_TABLES_WHITE["QUEEN"],
    "bQ": PIECE_SQUARE_TABLES_WHITE["QUEEN"][::-1]
}

# Black piece square tables should be mirrored
PIECE_SQUARE_TABLES_BLACK = {}
for PIECE, TABLE in PIECE_SQUARE_TABLES_WHITE.items():
    BLACK_TABLE = TABLE[::-1]
    PIECE_SQUARE_TABLES_BLACK[PIECE] = BLACK_TABLE
