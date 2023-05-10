"""
The engine is responsible for storing all information for the current game state, and determining valid moves.
The engine will also keep a backlog of moves made.
"""
from copy import copy
from typing import Callable, Dict, List, Tuple
from Chess.utils.pieces import get_rank_file
from Chess.utils.constants import NO_VALUE


class Move:
    """
    Represents a move in Chess.

    Attributes:
        start_row (int):
            The row where the piece is moving from.
        start_col (int): The column where the piece is moving from.
        end_row (int): The row where the piece is moving to.
        end_col (int): The column where the piece is moving to.
        piece_moved (str): The piece that was moved.
        piece_captured (str): The piece that was captured, if any piece was captured (otherwise "--")
        is_pawn_promotion (bool): Whether this move resulted in a pawn promotion.
        is_en_passant (bool): Whether this move is an en passant move.
        is_castle (bool): Whether is move is a castle move.
        move_id (int): A unique ID for a move based on tile coordinates.
    """

    def __init__(self, start: Tuple[int, int], end: Tuple[int, int], board: List[List[str]],
                 is_en_passant: bool = False, is_castle: bool = False):
        self.start_row: int = start[0]
        self.start_col: int = start[1]
        self.end_row: int = end[0]
        self.end_col: int = end[1]
        self.piece_moved: str = board[self.start_row][self.start_col]
        self.piece_captured: str = board[self.end_row][self.end_col]
        self.is_pawn_promotion: bool = ((self.piece_moved == "wp" and self.end_row == 0) or
                                        (self.piece_moved == "bp" and self.end_row == 7))
        self.is_en_passant: bool = is_en_passant
        if self.is_en_passant:
            self.piece_captured = "wp" if self.piece_moved == "bp" else "bp"
        self.is_castle = is_castle
        self.move_id: int = self.start_row * 1000 + self.start_col * 100 + self.end_row * 10 + self.end_col

    def __eq__(self, other) -> bool:
        """
        Overrides equals method
        """
        if isinstance(other, Move):
            return self.move_id == other.move_id
        return False

    def get_chess_notation(self) -> str:
        """
        Returns the squares that a piece moved from and to (e.g., "B1C3" means
        a piece moved from square B1 to C3).

        Returns:
            str: A string representation of a move.
        """
        return get_rank_file(row=self.start_row, col=self.start_col) + get_rank_file(row=self.end_row, col=self.end_col)


class CastleRights:
    """
    Represents the castling rights of a game.

    Attributes:
        wks (bool): White king side castling right
        bks (bool): Black king side castling right
        wqs (bool): White queen side castling right
        bqs (bool): Black queen side castling right
    """

    def __init__(self, wks: bool, bks: bool, wqs: bool, bqs: bool):
        self.wks: bool = wks
        self.bks: bool = bks
        self.wqs: bool = wqs
        self.bqs: bool = bqs


class GameState:
    """
    Represents a state of a game of chess.

    Attributes:
        board (List[List[str]): A standard 8x8 chess board represented by a 2D array. The board is
            populated by chess pieces represented by strings.
        white_to_move (bool): Whether it is white's turn to move (false implies black's turn to move)
        valid_moves (Dict[str, Move]): A dictionary of valid moves that can be made.
        move_log (List[Move]): A backlog of previous moves.
        move_functions (Dict[str, Callable]): A dictionary of move functions for all chess pieces.
        white_king_location (Tuple[int, int]): The coordinates of the white king.
        black_king_location (Tuple[int, int]): The coordinates of the black king.
        checkmate (bool): Whether the current player is in checkmate.
        stalemate (bool): Whether the game is in stalemate.
        in_check (bool): Whether the current player is in check.
        pins (List[Tuple[int, int, int, unt]]): A list of pinned pieces and the direction they are pinned from
            (e.g., (3, 2, 0, 1) means the piece on tile (3, 2) is pinned from the right direction but not vertically).
        checks (List[Tuple[int, int, int, unt]]): A list of checking pieces and the tile they are checking.
            (e.g. (3, 2, 5, 1) means the piece on tile (3, 2) is checking the tile (5, 1)).
        en_passant_possible (Tuple[int, int]): The tile in which an en passant move is possible, if such a move
            exists. Otherwise, this attribute defaults to (NO_VALUE, NO_VALUE), indicating no such move exists.
        current_castling_rights (CastleRights): The current castling rights of both players.
        castle_rights_log (List[CastleRights]): A backlog of previous castling rights.
    """

    def __init__(self):
        self.board: List[List[str]] = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"],
        ]
        self.white_to_move: bool = True
        self.valid_moves: Dict[str, Move] = {}
        self.move_log: List[Move] = []
        self.move_functions: Dict[str, Callable] = {
            "p": self.__get_pawn_moves,
            "R": self.__get_rook_moves,
            "N": self.__get_knight_moves,
            "B": self.__get_bishop_moves,
            "Q": self.__get_queen_moves,
            "K": self.__get_king_moves,
        }
        self.white_king_location: Tuple[int, int] = (7, 4)
        self.black_king_location: Tuple[int, int] = (0, 4)
        self.checkmate: bool = False
        self.stalemate: bool = False
        self.in_check: bool = False
        self.pins: List[Tuple[int, int, int, int]] = []
        self.checks: List[Tuple[int, int, int, int]] = []
        # coordinates of the tile where a pawn would move in an en passant
        self.en_passant_possible: Tuple[int, int] = (NO_VALUE, NO_VALUE)
        self.current_castling_rights: CastleRights = CastleRights(True, True, True, True)
        # self.current_castling_rights: CastleRights = CastleRights(False, False, False, False)
        self.castle_rights_log: List[CastleRights] = [copy(self.current_castling_rights)]

    def make_move(self, move: Move) -> None:
        """
        Makes a move. Will not consider castling, en passant, or pawn promotion.

        Parameters:
            move (Move): The move to make.

        Returns:
            None
        """
        self.board[move.start_row][move.start_col] = "--"
        self.board[move.end_row][move.end_col] = move.piece_moved
        self.move_log.append(move)
        self.white_to_move = not self.white_to_move
        if move.piece_moved == "wK":
            self.white_king_location = (move.end_row, move.end_col)
        elif move.piece_moved == "bK":
            self.black_king_location = (move.end_row, move.end_col)
        # pawn promotion
        if move.is_pawn_promotion:
            self.board[move.end_row][move.end_col] = move.piece_moved[0] + "Q"
        # en passant
        if move.is_en_passant:
            self.board[move.start_row][move.end_col] = "--"
        if move.piece_moved[1] == "p" and abs(move.end_row - move.start_row) == 2:
            self.en_passant_possible = ((move.start_row + move.end_row) // 2, move.end_col)
        else:
            self.en_passant_possible = (NO_VALUE, NO_VALUE)
        # castling rights
        # need to move rooks for castle
        if move.is_castle:
            # king side castle
            if move.end_col - move.start_col == 2:
                self.board[move.end_row][move.end_col - 1] = self.board[move.end_row][move.end_col + 1]
                self.board[move.end_row][move.end_col + 1] = "--"
            # queen side castle
            else:
                self.board[move.end_row][move.end_col + 1] = self.board[move.end_row][move.end_col - 2]
                self.board[move.end_row][move.end_col - 2] = "--"

        self.__update_castle_rights(move=move)
        self.castle_rights_log.append(copy(self.current_castling_rights))
        self.checkmate = False
        self.stalemate = False

    def undo_move(self) -> None:
        """
        Undoes the last move.

        Returns:
             None
        """
        if len(self.move_log) == 0:
            print("No moves to undo!")
            return
        move: Move = self.move_log.pop()
        self.board[move.start_row][move.start_col] = move.piece_moved
        self.board[move.end_row][move.end_col] = move.piece_captured
        self.white_to_move = not self.white_to_move
        if move.piece_moved == "wK":
            self.white_king_location = (move.start_row, move.start_col)
        elif move.piece_moved == "bK":
            self.black_king_location = (move.start_row, move.start_col)
        # en passant
        if move.is_en_passant:
            self.board[move.end_row][move.end_col] = "--"
            self.board[move.start_row][move.end_col] = move.piece_captured
            self.en_passant_possible = (move.end_row, move.end_col)
        # remove en passant possibility when a pawn moves two spaces
        if move.piece_moved[1] == "p" and abs(move.end_row - move.start_row) == 2:
            self.en_passant_possible = (NO_VALUE, NO_VALUE)
        self.generate_valid_moves()
        # castling rights
        self.castle_rights_log.pop()
        self.current_castling_rights = copy(self.castle_rights_log[-1])
        if move.is_castle:
            # king side castle
            if move.end_col - move.start_col == 2:
                self.board[move.end_row][move.end_col + 1] = self.board[move.end_row][move.end_col - 1]
                self.board[move.end_row][move.end_col - 1] = "--"
            # queen side castle
            else:
                self.board[move.end_row][move.end_col - 2] = self.board[move.end_row][move.end_col + 1]
                self.board[move.end_row][move.end_col + 1] = "--"
        self.checkmate = False
        self.stalemate = False

    def generate_valid_moves(self) -> Dict[str, Move]:
        """
        Generates all legal chess moves.

        Returns:
             (Dict[str, Move]): A dictionary of valid moves.
        """
        temp_en_passant_possible: Tuple[int, int] = self.en_passant_possible
        temp_current_castling_rights: CastleRights = copy(self.current_castling_rights)
        moves: Dict[str, Move] = {}
        self.in_check, self.pins, self.checks = self.__check_for_pins_and_checks()
        if self.white_to_move:
            king_row = self.white_king_location[0]
            king_col = self.white_king_location[1]
        else:
            king_row = self.black_king_location[0]
            king_col = self.black_king_location[1]
        if self.in_check:
            # If there is only one piece checking the king, we have the option of capturing it.
            if len(self.checks) == 1:
                moves = self.__get_all_possible_moves()
                check: Tuple[int, int, int, int] = self.checks[0]
                check_row: int = check[0]
                check_col: int = check[1]
                piece_checking: str = self.board[check_row][check_col]
                valid_tiles: List[Tuple[int, int]] = []
                # If the piece is a knight, it must be captured or the king must move
                # since knights can hop over other pieces.
                if piece_checking[1] == "N":
                    valid_tiles = [(check_row, check_col)]
                else:
                    for i in range(1, len(self.board)):
                        valid_row = king_row + check[2] * i
                        valid_col = king_col + check[3] * i
                        # if not (0 <= valid_row < len(self.board) and 0 <= valid_col < len(self.board[0])):
                        #     continue
                        valid_tile: Tuple[int, int] = (valid_row, valid_col)
                        valid_tiles.append(valid_tile)
                        if valid_tile[0] == check_row and valid_tile[1] == check_col:
                            break
                # Eliminate moves that don't block check or move the king out of check.
                for key in list(moves.keys()):
                    move: Move = moves[key]
                    if move.piece_moved[1] != "K":
                        if not (move.end_row, move.end_col) in valid_tiles:
                            del moves[key]
            # The king is being checked by two different pieces, so it has to move.
            # Capturing one piece still means the king is under attack by another.
            # It is not possible to block a second piece by capturing another, since
            # that would imply the first piece was already blocking the second, or
            # the second is a knight which can hop over pieces.
            else:
                self.__get_king_moves(row=king_row, col=king_col, moves=moves)
        # We are not in check so all possible moves are valid
        else:
            moves = self.__get_all_possible_moves()
        if self.white_to_move:
            self.__get_castle_moves(row=self.white_king_location[0],
                                    col=self.white_king_location[1], moves=moves)
        else:
            self.__get_castle_moves(row=self.black_king_location[0],
                                    col=self.black_king_location[1], moves=moves)
        self.en_passant_possible = temp_en_passant_possible
        self.current_castling_rights = temp_current_castling_rights
        if len(moves) == 0:
            if self.in_check:
                self.checkmate = True
            else:
                self.stalemate = True
        else:
            self.checkmate = False
            self.stalemate = False
        self.valid_moves = moves
        return moves

    def in_check(self) -> bool:
        """
        Determines if the current player is in check (i.e. their king is under attack).

        Returns:
            (bool): Whether the current player is in check.
        """
        if self.white_to_move:
            return self.tile_under_attack(row=self.white_king_location[0], col=self.white_king_location[1])
        else:
            return self.tile_under_attack(row=self.black_king_location[0], col=self.black_king_location[1])

    def tile_under_attack(self, row: int, col: int) -> bool:
        """
        Determines if a tile is under attack.

        Arguments:
            row (int): The row the tile is located on.
            col (int): The col the tile is located on.

        Returns:
            (bool): Whether the tile is under attack.
        """
        self.white_to_move = not self.white_to_move
        opponent_moves: Dict[str, Move] = self.__get_all_possible_moves()
        self.white_to_move = not self.white_to_move
        for move in opponent_moves.values():
            if move.end_row == row and move.end_col == col:
                return True
        return False

    def __get_all_possible_moves(self) -> Dict[str, Move]:
        """
        Gets all possible moves the current player can make without considering check.

        Returns:
            Dict[str, Move: A set of possible moves.
        """
        moves: Dict[str, Move] = {}
        for row in range(len(self.board)):
            for col in range(len(self.board[row])):
                turn: str = self.board[row][col][0]
                if (turn == "w" and self.white_to_move) or (turn == "b" and not self.white_to_move):
                    piece: str = self.board[row][col][1]
                    self.move_functions[piece](row, col, moves)
        return moves

    def __get_pawn_moves(self, row: int, col: int, moves: Dict[str, Move]) -> None:
        """
        Updates a move set with all possible pawn moves on a given tile.

        Arguments:
            row (int): The row the pawn is located on.
            col (int): The column the pawn is located on.
            moves (Dict[str, Move): The set of moves to update.

        Returns:
            None
        """
        piece_pinned: bool = False
        pin_direction: Tuple[int, int] = (NO_VALUE, NO_VALUE)
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        direction: int = self.white_to_move and -1 or 1
        start_row: int = self.white_to_move and 6 or 1
        enemy: str = self.white_to_move and "b" or "w"
        if self.white_to_move:
            direction: int = -1
            start_row: int = 6
            enemy: str = "b"
            king_row: int = self.white_king_location[0]
            king_col: int = self.white_king_location[1]
        else:
            direction: int = 1
            start_row: int = 1
            enemy: str = "w"
            king_row: int = self.black_king_location[0]
            king_col: int = self.black_king_location[1]

        if self.board[row + direction][col] == "--":
            if not piece_pinned or pin_direction == (direction, 0):
                # Pawns can move one space forward.
                move: Move = Move(start=(row, col), end=(row + direction, col), board=self.board)
                moves[str(move.move_id)] = move
                # A pawn can move two spaces on its first move.
                if row == start_row and self.board[row + 2 * direction][col] == "--":
                    move: Move = Move(start=(row, col), end=(row + 2 * direction, col), board=self.board)
                    moves[str(move.move_id)] = move
        # pawns can capture diagonally one space in the direction of the opponent from the left of right.
        left_right: Tuple[int, int] = (-1, 1)
        for lr in left_right:
            if not piece_pinned or pin_direction == (direction, lr):
                # capture
                if 0 <= col + lr < len(self.board) and self.board[row + direction][col + lr][0] == enemy:
                    move: Move = Move(start=(row, col), end=(row + direction, col + lr), board=self.board)
                    moves[str(move.move_id)] = move
                # en passant
                elif (row + direction, col + lr) == self.en_passant_possible:
                    attacking_piece: bool = False
                    blocking_piece: bool = False
                    range_offset: int = lr > 0 and 1 or 0
                    if king_row == row:
                        if king_col < col:
                            inside_range: range = range(king_col + 1, col - 1 + range_offset)
                            outside_range: range = range(col + 1 + range_offset, len(self.board))
                        else:
                            inside_range: range = range(king_col - 1, col + range_offset, -1)
                            outside_range: range = range(col - 2 + range_offset, -1, -1)
                        for c in inside_range:
                            if self.board[row][c] != "--":
                                blocking_piece = True
                        for c in outside_range:
                            tile: str = self.board[row][c]
                            if tile[0] == enemy and (tile[1] == "R" or tile[1] == "Q"):
                                attacking_piece = True
                            elif tile != "--":
                                blocking_piece = True
                    if not attacking_piece or blocking_piece:
                        move: Move = Move(start=(row, col), end=(row + direction, col + lr),
                                          board=self.board, is_en_passant=True)
                        moves[str(move.move_id)] = move

    def __get_rook_moves(self, row: int, col: int, moves: Dict[str, Move]) -> None:
        """
        Updates a move set with all possible rook moves on a given tile.

        Arguments:
            row (int): The row the rook is located on.
            col (int): The column the rook is located on.
            moves (Dict[str, Move): The set of moves to update.

        Returns:
            None
        """
        directions: List[Tuple[int, int]] = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        self.__get_moves_from_directions(row=row, col=col, moves=moves, directions=directions)

    def __get_knight_moves(self, row: int, col: int, moves: Dict[str, Move]) -> None:
        """
        Updates a move set with all possible knight moves on a given tile.

        Arguments:
            row (int): The row the knight is located on.
            col (int): The column the knight is located on.
            moves (Dict[str, Move): The set of moves to update.

        Returns:
            None
        """
        tiles: List[Tuple[int, int]] = [
            (row - 1, col + 2), (row - 2, col + 1), (row - 2, col - 1), (row - 1, col - 2),
            (row + 1, col - 2), (row + 2, col - 1), (row + 2, col + 1), (row + 1, col + 2)
        ]
        self.__get_moves_from_tiles(row=row, col=col, moves=moves, tiles=tiles)

    def __get_bishop_moves(self, row: int, col: int, moves: Dict[str, Move]) -> None:
        """
        Updates a move set with all possible bishop moves on a given tile.

        Arguments:
            row (int): The row the bishop is located on.
            col (int): The column the bishop is located on.
            moves (Dict[str, Move): The set of moves to update.

        Returns:
            None
        """
        directions: List[Tuple[int, int]] = [(-1, 1), (-1, -1), (1, -1), (1, 1)]
        self.__get_moves_from_directions(row=row, col=col, moves=moves, directions=directions)

    def __get_queen_moves(self, row: int, col: int, moves: Dict[str, Move]) -> None:
        """
        Updates a move set with all possible queen moves on a given tile.

        Arguments:
            row (int): The row the queen is located on.
            col (int): The column the queen is located on.
            moves (Dict[str, Move): The set of moves to update.

        Returns:
            None
        """
        self.__get_rook_moves(row=row, col=col, moves=moves)
        self.__get_bishop_moves(row=row, col=col, moves=moves)

    def __get_king_moves(self, row: int, col: int, moves: Dict[str, Move]) -> None:
        """
        Updates a move set with all possible king moves on a given tile.

        Arguments:
            row (int): The row the king is located on.
            col (int): The column the king is located on.
            moves (Dict[str, Move): The set of moves to update.

        Returns:
            None
        """
        tiles: List[Tuple[int, int]] = [
            (row, col + 1), (row - 1, col + 1), (row - 1, col), (row - 1, col - 1),
            (row, col - 1), (row + 1, col - 1), (row + 1, col), (row + 1, col + 1)
        ]
        ally: str = self.white_to_move and "w" or "b"
        for tile in tiles:
            t_row: int = tile[0]
            t_col: int = tile[1]
            if 0 <= t_row < len(self.board) and 0 <= t_col < len(self.board[0]):
                end_piece: str = self.board[t_row][t_col]
                if end_piece[0] != ally:
                    if ally == "w":
                        self.white_king_location = (t_row, t_col)
                    else:
                        self.black_king_location = (t_row, t_col)
                    in_check, pins, checks = self.__check_for_pins_and_checks()
                    if not in_check:
                        move: Move = Move(start=(row, col), end=(t_row, t_col), board=self.board)
                        moves[str(move.move_id)] = move
                    if ally == "w":
                        self.white_king_location = (row, col)
                    else:
                        self.black_king_location = (row, col)

    def __get_castle_moves(self, row: int, col: int, moves: Dict[str, Move]) -> None:
        """
        Updates a move set with all possible castling moves for a king.

        Arguments:
            row (int): The row the piece is located on.
            col (int): The column the piece is located on.
            moves (Dict[str, Move]): The set of moves to update.
        """
        # can't castle when in check
        if self.tile_under_attack(row=row, col=col):
            return
        if (self.white_to_move and self.current_castling_rights.wks) or \
                (not self.white_to_move and self.current_castling_rights.bks):
            self.__get_king_side_castle_moves(row=row, col=col, moves=moves)
        if (self.white_to_move and self.current_castling_rights.wqs) or \
                (not self.white_to_move and self.current_castling_rights.bqs):
            self.__get_queen_side_castle_moves(row=row, col=col, moves=moves)

    def __get_king_side_castle_moves(self, row: int, col: int, moves: Dict[str, Move]) -> None:
        """
        Updates a move set with all possible castling moves on the king's side for a king.

        Arguments:
            row (int): The row the piece is located on.
            col (int): The column the piece is located on.
            moves (Dict[str, Move]): The set of moves to update.

        Returns:
            None
        """
        if self.board[row][col + 1] == "--" and self.board[row][col + 2] == "--":
            if not self.tile_under_attack(row=row, col=col + 1) and not self.tile_under_attack(row=row, col=col + 2):
                move: Move = Move(start=(row, col), end=(row, col + 2), board=self.board, is_castle=True)
                moves[str(move.move_id)] = move

    def __get_queen_side_castle_moves(self, row: int, col: int, moves: Dict[str, Move]) -> None:
        """
        Updates a move set with all possible castling moves on the king's side for a king.

        Arguments:
            row (int): The row the piece is located on.
            col (int): The column the piece is located on.
            moves (Dict[str, Move]): The set of moves to update.

        Returns:
            None
        """
        if self.board[row][col - 1] == "--" and self.board[row][col - 2] == "--" and self.board[row][col - 3] == "--":
            if not self.tile_under_attack(row=row, col=col - 1) and not self.tile_under_attack(row=row, col=col - 2):
                move: Move = Move(start=(row, col), end=(row, col - 2), board=self.board, is_castle=True)
                moves[str(move.move_id)] = move

    def __get_moves_from_tiles(self, row: int, col: int, moves: Dict[str, Move], tiles: List[Tuple[int, int]]) -> None:
        """
        Updates a move set with all possible moves from a list of tiles. Assumes that all empty spaces
        in the tile list are valid move, and all enemy pieces in the tile list can be captured directly.

        Arguments:
            row (int): The row the piece is located on.
            col (int): The column the piece is located on.
            moves (Dict[str, Move): The set of moves to update.
            tiles (List[Tuple[int, int]]): The list of tiles to update from.

        Returns:
            None
        """
        piece_pinned: bool = False
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piece_pinned = True
                self.pins.remove(self.pins[i])
                break

        enemy: str = self.white_to_move and "b" or "w"
        for tile in tiles:
            t_row: int = tile[0]
            t_col: int = tile[1]
            if 0 <= t_row < len(self.board) and 0 <= t_col < len(self.board[0]):
                if not piece_pinned:
                    if self.board[t_row][t_col] == "--":
                        move: Move = Move(start=(row, col), end=(t_row, t_col), board=self.board)
                        moves[str(move.move_id)] = move
                    elif self.board[t_row][t_col][0] == enemy:
                        move: Move = Move(start=(row, col), end=(t_row, t_col), board=self.board)
                        moves[str(move.move_id)] = move

    def __get_moves_from_directions(self, row: int, col: int, moves: Dict[str, Move],
                                    directions: List[Tuple[int, int]]) -> None:
        """
        Updates a move set with all possible moves from a list of directions. Each direction should be a tuple of
        size two indicating the row step and column step to move (e.g. (1, 2) means generate moves by moving down by
        1 and right by 2). Assumes that all empty spaces found are valid moves, and all enemy pieces found can be
        captured directly.

        Arguments:
            row (int): The row the piece is located on.
            col (int): The column the piece is located on.
            moves (Dict[str, Move): The set of moves to update.
            directions (List[Tuple[int, int]]): The list of directions to update from.

        Returns:
            None
        """
        piece_pinned: bool = False
        pin_direction: Tuple[int, int] = (NO_VALUE, NO_VALUE)
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                # Can't remove queens from pin on rook moves. Remove it on bishop moves.
                if self.board[row][col][1] == "R":
                    self.pins.remove(self.pins[i])
                break
        enemy: str = self.white_to_move and "b" or "w"
        length: int = max(len(self.board), len(self.board[0]))
        for d in directions:
            for i in range(1, length):
                end_row: int = row + d[0] * i
                end_col: int = col + d[1] * i
                if 0 <= end_row < len(self.board) and 0 <= end_col < len(self.board[0]):
                    if not piece_pinned or pin_direction == d or pin_direction == (-d[0], -d[1]):
                        end_piece: str = self.board[end_row][end_col]
                        if end_piece == "--":
                            move: Move = Move(start=(row, col), end=(end_row, end_col), board=self.board)
                            moves[str(move.move_id)] = move
                        elif end_piece[0] == enemy:
                            move: Move = Move(start=(row, col), end=(end_row, end_col), board=self.board)
                            moves[str(move.move_id)] = move
                            break
                        else:
                            break
                else:
                    break

    def __check_for_pins_and_checks(self) -> (bool, List[Tuple[int, int, int, int]], List[Tuple[int, int, int, int]]):
        """
        Determines if the current player is in check, which of their pieces are pinned,
        and what enemy pieces are placing the current player in check.

        Returns:
            (bool, List[Tuple[int, int, int, int]], List[Tuple[int, int, int, int]]):
                bool: Whether the current player is in check.
                List[Tuple[int, int, int, int]]: A list of moves representing the current player's pinned pieces.
                List[Tuple[int, int, int, int]]: A list of moves representing which opposing pieces are placing
                    the current player in check.
        """
        in_check: bool = False
        pins: List[Tuple[int, int, int, int]] = []
        checks: List[Tuple[int, int, int, int]] = []
        if self.white_to_move:
            ally: str = "w"
            enemy: str = "b"
            start_row = self.white_king_location[0]
            start_col = self.white_king_location[1]
        else:
            ally: str = "b"
            enemy: str = "w"
            start_row = self.black_king_location[0]
            start_col = self.black_king_location[1]

        directions: List[Tuple[int, int]] = [(-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
        for j in range(len(directions)):
            d: Tuple[int, int] = directions[j]
            possible_pin: Tuple[int, int, int, int] = (NO_VALUE, NO_VALUE, NO_VALUE, NO_VALUE)
            for i in range(1, len(self.board)):
                end_row: int = start_row + d[0] * i
                end_col: int = start_col + d[1] * i
                if 0 <= end_row < len(self.board) and 0 <= end_col < len(self.board[0]):
                    end_piece: str = self.board[end_row][end_col]
                    # first allied piece found in this direction could be a pin
                    if end_piece[0] == ally and end_piece[1] != "K":
                        if possible_pin == (NO_VALUE, NO_VALUE, NO_VALUE, NO_VALUE):
                            possible_pin = (end_row, end_col, d[0], d[1])
                        # second allied piece found in this direction means
                        # the first one isn't pinned, so stop searching
                        else:
                            break
                    elif end_piece[0] == enemy:
                        piece_type: str = end_piece[1]
                        if (0 <= j <= 3 and piece_type == "R") or \
                                (4 <= j <= 7 and piece_type == "B") or \
                                (i == 1 and piece_type == "p" and
                                 ((enemy == "w" and 6 <= j <= 7) or (enemy == "b" and 4 <= j <= 5))) or \
                                (piece_type == "Q") or (i == 1 and piece_type == "K"):
                            # no piece blocking so we're in check
                            if possible_pin == (NO_VALUE, NO_VALUE, NO_VALUE, NO_VALUE):
                                in_check = True
                                checks.append((end_row, end_col, d[0], d[1]))
                                # break
                            # piece is blocking so it is pinned
                            else:
                                pins.append(possible_pin)
                                break
                        # opposing piece is not applying check
                        else:
                            break
        # knights can hop over pieces, so we must calculate their checks separately
        knight_moves: List[Tuple[int, int]] = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]
        for move in knight_moves:
            end_row: int = start_row + move[0]
            end_col: int = start_col + move[1]
            if 0 <= end_row < len(self.board) and 0 <= end_col < len(self.board[0]):
                end_piece: str = self.board[end_row][end_col]
                if end_piece[0] == enemy and end_piece[1] == "N":
                    in_check = True
                    checks.append((end_row, end_col, move[0], move[1]))
        return in_check, pins, checks

    def __update_castle_rights(self, move: Move) -> None:
        """
        Updates the current castling rights given a move.

        Arguments:
            move (Move): The move to update castling rights with.

        Returns:
            None
        """
        if move.piece_moved == "wK":
            self.current_castling_rights.wks = False
            self.current_castling_rights.wqs = False
        elif move.piece_moved == "bK":
            self.current_castling_rights.bks = False
            self.current_castling_rights.bqs = False
        elif move.piece_moved == "wR":
            if move.start_row == 7:
                if move.start_col == 0:
                    self.current_castling_rights.wqs = False
                elif move.start_col == 7:
                    self.current_castling_rights.wks = False
        elif move.piece_moved == "bR":
            if move.start_row == 0:
                if move.start_col == 0:
                    self.current_castling_rights.bqs = False
                elif move.start_col == 7:
                    self.current_castling_rights.bks = False
        # if a rook is captured
        if move.piece_captured == 'wR':
            if move.end_row == 7:
                if move.end_col == 0:
                    self.current_castling_rights.wqs = False
                elif move.end_col == 7:
                    self.current_castling_rights.wks = False
        elif move.piece_captured == 'bR':
            if move.end_row == 0:
                if move.end_col == 0:
                    self.current_castling_rights.bqs = False
                elif move.end_col == 7:
                    self.current_castling_rights.bks = False
