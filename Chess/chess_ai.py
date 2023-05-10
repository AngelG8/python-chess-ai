"""
This AI is responsible for calculating, scoring, and making moves as a player would.
"""
import random
from abc import ABC, abstractmethod
from typing import Dict, List
from Chess.engine import Move, GameState
from Chess.utils.pieces import MATERIAL_VALUES, CHECKMATE, STALEMATE, PIECE_POSITION_SCORES
from Chess.utils.constants import MAX_DEPTH


class ChessAI(ABC):
    """
    Represents a chess AI that can play a game of chess.

    Attributes:
        game_state (GameState): The current game state to start this AI from.
    """

    def __init__(self, game_state: GameState):
        self.game_state = game_state

    @abstractmethod
    def find_move(self) -> Move:
        """
        Selects a move to make.

        Returns:
            (Move): A move to make.
        """
        pass

    def score_material(self) -> int:
        """
        Calculates the total material score on the board. A positive score indicates that white has
        the material advantage, while a negative score indicates black has the material advantage.

        Returns:
            (int): The total material score.
        """
        ally: str = self.game_state.white_to_move and "w" or "b"
        enemy: str = self.game_state.white_to_move and "b" or "w"
        score: int = 0
        for row in self.game_state.board:
            for tile in row:
                if tile[0] == ally:
                    score += MATERIAL_VALUES[tile[1]]
                elif tile[0] == enemy:
                    score -= MATERIAL_VALUES[tile[1]]
        return score

    def score_material_piece_table(self) -> int:
        """
        Calculates the total material score on the board weighted by the pieces' corresponding piece tables.
        A positive score indicates that white has the material advantage, while a negative score indicates
        black has the material advantage.

        Returns:
            (int): The total weighted material score.
        """
        total_score: int = 0
        for row in range(len(self.game_state.board)):
            for col in range(len(self.game_state.board[0])):
                piece: str = self.game_state.board[row][col]
                if piece != "--":
                    piece_score: int = 0
                    if piece[1] != "K":
                        piece_score = PIECE_POSITION_SCORES[piece][row][col]
                    if piece[0] == "w":
                        total_score += MATERIAL_VALUES[piece[1]] + piece_score
                    elif piece[0] == "b":
                        total_score -= MATERIAL_VALUES[piece[1]] + piece_score
        return total_score

    def score_board(self) -> int:
        """
        Calculates the total score on the board based on various criteria such as material score.
        A positive score indicates that white has the  advantage, while a negative score indicates
        black has the advantage.

        Returns:
            (int): The total score of the board.
        """
        if self.game_state.checkmate:
            if self.game_state.white_to_move:
                return -CHECKMATE
            else:
                return CHECKMATE
        elif self.game_state.stalemate:
            return STALEMATE
        score: int = self.score_material_piece_table()
        return score


class RandomChessAI(ChessAI):
    """
    Represents a chess AI that makes random moves.
    """

    def find_move(self) -> Move:
        """
        Generates a random move.

        Returns:
            (move): A random move.
        """
        move: Move = random.choice(list(self.game_state.valid_moves.values()))
        return move


class GreedyChessAI(ChessAI):
    """
    Represents a chess AI that makes moves greedily based on material value by looking one move ahead.
    """
    def find_move(self) -> Move:
        """
        Generates a move greedily based on material value using a minimax algorithm.

        Returns:
            (Move): The move that yields the greatest material advantage.
        """
        valid_moves: Dict[str, Move] = self.game_state.valid_moves
        minimax: int = CHECKMATE
        best_moves: List[Move] = []
        for move in valid_moves.values():
            self.game_state.make_move(move=move)
            opponent_moves: Dict[str, Move] = self.game_state.generate_valid_moves()
            if self.game_state.stalemate:
                opponent_max_score = STALEMATE
            elif self.game_state.checkmate:
                opponent_max_score = -CHECKMATE
            else:
                opponent_max_score: int = -CHECKMATE
                for opponent_move in opponent_moves.values():
                    self.game_state.make_move(move=opponent_move)
                    opponent_score: int
                    if self.game_state.checkmate:
                        opponent_score = CHECKMATE
                    elif self.game_state.stalemate:
                        opponent_score = STALEMATE
                    else:
                        opponent_score = -self.score_material()
                    if opponent_score > opponent_max_score:
                        opponent_max_score = opponent_score
                    self.game_state.undo_move()

            if opponent_max_score < minimax:
                minimax = opponent_max_score
                best_moves = [move]
            elif minimax == opponent_max_score:
                best_moves.append(move)
            self.game_state.undo_move()
        best_move: Move = random.choice(best_moves)
        return best_move


class MinimaxChessAI(ChessAI):
    """
    Represents a chess AI that makes moves based on a minimax algorithm.

    Attributes:
        game_state (GameState): The current game state to start this AI from.
        best_moves (List[Move]): A list of the best possible next moves to make.
    """

    def __init__(self, game_state: GameState):
        super().__init__(game_state)
        self.best_moves: List[Move] = []

    def find_move(self) -> Move:
        """
        Generates a move greedily based on material value using a minimax algorithm.

        Returns:
            (Move): The move that yields the greatest material advantage.
        """
        self.best_moves = []
        minimax: int = self.find_move_minimax(valid_moves=self.game_state.generate_valid_moves(),
                                              white_to_move=self.game_state.white_to_move,
                                              depth=MAX_DEPTH)
        return random.choice(self.best_moves)

    def find_move_minimax(self, valid_moves: Dict[str, Move], white_to_move: bool, depth: int) -> int:
        """
        Generates a move greedily based on material value using a minimax algorithm.

        Returns:
            (Move): The move that yields the greatest material advantage.
        """
        if depth <= 0:
            self.score_board()

        if white_to_move:
            max_score: int = -CHECKMATE
            for move in valid_moves.values():
                self.game_state.make_move(move=move)
                next_moves: Dict[str, Move] = self.game_state.generate_valid_moves()
                score = self.find_move_minimax(valid_moves=next_moves, white_to_move=False, depth=depth - 1)
                if score > max_score:
                    max_score = score
                    if depth == MAX_DEPTH:
                        self.best_moves = [move]
                elif score == max_score:
                    if depth == MAX_DEPTH:
                        self.best_moves.append(move)
                self.game_state.undo_move()
            return max_score
        else:
            min_score: int = CHECKMATE
            for move in valid_moves.values():
                self.game_state.make_move(move=move)
                next_moves: Dict[str, Move] = self.game_state.generate_valid_moves()
                score = self.find_move_minimax(valid_moves=next_moves, white_to_move=True, depth=depth - 1)
                if score < min_score:
                    min_score = score
                    if depth == MAX_DEPTH:
                        self.best_moves = [move]
                elif score == min_score:
                    if depth == MAX_DEPTH:
                        self.best_moves.append(move)
                self.game_state.undo_move()
            return min_score


class NegamaxChessAI(ChessAI):
    """
    Represents a chess AI that makes moves based on a negamax algorithm.

    Attributes:
        game_state (GameState): The current game state to start this AI from.
        best_moves (List[Move]): A list of the best possible next moves to make.
    """

    def __init__(self, game_state: GameState):
        super().__init__(game_state)
        self.best_moves: List[Move] = []

    def find_move(self) -> Move:
        """
        Generates a move greedily based on material value using a minimax algorithm.

        Returns:
            (Move): The move that yields the greatest material advantage.
        """
        self.best_moves = []
        minimax: int = self.find_move_negamax(valid_moves=self.game_state.generate_valid_moves(),
                                              white_to_move=self.game_state.white_to_move,
                                              depth=MAX_DEPTH)
        return random.choice(self.best_moves)

    def find_move_negamax(self, valid_moves: Dict[str, Move], white_to_move: bool, depth: int) -> int:
        """
        Generates a move greedily based on material value using a minimax algorithm.

        Returns:
            (Move): The move that yields the greatest material advantage.
        """
        if depth <= 0:
            turn_multiplier: int = white_to_move and 1 or -1
            return turn_multiplier * self.score_board()

        max_score: int = -CHECKMATE
        for move in valid_moves.values():
            self.game_state.make_move(move=move)
            next_moves: Dict[str, Move] = self.game_state.generate_valid_moves()
            score = -self.find_move_negamax(valid_moves=next_moves, white_to_move=not white_to_move, depth=depth - 1)
            if score > max_score:
                max_score = score
                if depth == MAX_DEPTH:
                    self.best_moves = [move]
            elif score == max_score:
                if depth == MAX_DEPTH:
                    self.best_moves.append(move)
            self.game_state.undo_move()
        return max_score


class NegamaxAlphaBetaChessAI(ChessAI):
    """
    Represents a chess AI that makes moves based on a negamax algorithm with alpha beta pruning.

    Attributes:
        game_state (GameState): The current game state to start this AI from.
        best_moves (List[Move]): A list of the best possible next moves to make.
    """

    def __init__(self, game_state: GameState):
        super().__init__(game_state)
        self.best_moves: List[Move] = []

    def find_move(self) -> Move:
        """
        Generates a move greedily based on material value using a minimax algorithm.

        Returns:
            (Move): The move that yields the greatest material advantage.
        """
        self.best_moves = []
        minimax: int = self.find_move_negamax_alpha_beta(valid_moves=self.game_state.generate_valid_moves(),
                                                         white_to_move=self.game_state.white_to_move,
                                                         alpha=-CHECKMATE,
                                                         beta=CHECKMATE,
                                                         depth=MAX_DEPTH)
        return random.choice(self.best_moves)

    def find_move_negamax_alpha_beta(self, valid_moves: Dict[str, Move], alpha: int, beta: int,
                                     white_to_move: bool, depth: int) -> int:
        """
        Generates a move greedily based on material value using a minimax algorithm.

        Returns:
            (Move): The move that yields the greatest material advantage.
        """
        if depth <= 0:
            turn_multiplier: int = white_to_move and 1 or -1
            return turn_multiplier * self.score_board()

        max_score: int = -CHECKMATE
        for move in valid_moves.values():
            self.game_state.make_move(move=move)
            next_moves: Dict[str, Move] = self.game_state.generate_valid_moves()
            score = -self.find_move_negamax_alpha_beta(valid_moves=next_moves,
                                                       alpha=-beta,
                                                       beta=-alpha,
                                                       white_to_move=not white_to_move,
                                                       depth=depth - 1)
            if score > max_score:
                max_score = score
                if depth == MAX_DEPTH:
                    self.best_moves = [move]
            elif score == max_score:
                if depth == MAX_DEPTH:
                    self.best_moves.append(move)
            self.game_state.undo_move()
            if max_score > alpha:
                alpha = max_score
            if alpha >= beta:
                break
        return max_score
