"""
The main chess driver is responsible for handling user input and displaying the current game state.
"""
import pygame as p
from pygame import Color, Rect, Surface
from pygame.time import Clock

from typing import Dict, List, Tuple

from Chess.chess_ai import ChessAI, RandomChessAI, GreedyChessAI, MinimaxChessAI, NegamaxChessAI, \
    NegamaxAlphaBetaChessAI
from Chess.engine import GameState, Move
from Chess.utils.constants import WIDTH, HEIGHT, DIMENSION, SQ_SIZE, MAX_FPS, NO_VALUE, IMAGES, \
    LIGHT_SQUARE_COLOR, DARK_SQUARE_COLOR, SELECTED_HIGHLIGHT_COLOR, MOVE_HIGHLIGHT_COLOR, \
    CHECK_HIGHLIGHT_COLOR, FONT, FONT_SIZE, FONT_COLOR, FONT_SHADOW


def load_images() -> None:
    """
    Initialize a global dictionary of images for chess pieces.

    Returns:
        None
    """
    pieces: List[str] = ["wp", "wR", "wN", "wB", "wQ", "wK", "bp", "bR", "bN", "bB", "bQ", "bK"]
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("Chess/images/pieces/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))


def draw_game_state(screen: Surface, game_state: GameState,
                    valid_moves: Dict[str, Move], selected: Tuple[int, int]) -> None:
    """
    Visualizes a game state.

    Arguments:
        screen (Surface): The screen to draw the game state on.
        game_state (GameState): The game state to draw.
        valid_moves (Dict[str, Move]): A dictionary of valid moves the player can make.
        selected (Tuple[int, int]):  The current selected tile.

    Returns:
        None
    """
    __draw_board(screen=screen)
    __highlight_tiles(screen=screen, game_state=game_state, valid_moves=valid_moves, selected=selected)
    __draw_pieces(screen=screen, board=game_state.board)


def __draw_board(screen: Surface) -> None:
    """
    Visualizes a board.

    Arguments:
        screen (Surface): The screen to draw the board on.
    """
    colors: Tuple[Color, Color] = (LIGHT_SQUARE_COLOR, DARK_SQUARE_COLOR)
    for row in range(DIMENSION):
        for col in range(DIMENSION):
            color = colors[(row + col) % 2]
            p.draw.rect(screen, color, p.Rect(col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def __draw_pieces(screen: Surface, board: List[List[str]]) -> None:
    """
    Visualizes the pieces on a board.

    Arguments:
        screen (Surface): The screen to draw the pieces on.
        board (List[List[str]]: The board to draw the pieces from.

    Returns:
        None
    """
    for row in range(DIMENSION):
        for col in range(DIMENSION):
            piece: str = board[row][col]
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def __highlight_tiles(screen: Surface, game_state: GameState,
                      valid_moves: Dict[str, Move], selected: Tuple[int, int]) -> None:
    """
    Highlights a selected piece's valid moves.

    Arguments:
        screen (Surface): The screen to draw the game state on.
        game_state (GameState): The game state to draw.
        valid_moves (Dict[str, Move]): A dictionary of valid moves the player can make.
        selected (Tuple[int, int]):  The current selected tile.

    Returns:
        None
    """
    if selected != (NO_VALUE, NO_VALUE):
        row: int = selected[0]
        col: int = selected[1]
        if game_state.board[row][col][0] == (game_state.white_to_move and "w" or "b"):
            # highlight the selected square
            selected_highlight: Surface = p.Surface((SQ_SIZE, SQ_SIZE))
            # alpha can be from 0 to 255
            selected_highlight.set_alpha(31)
            selected_highlight.fill(SELECTED_HIGHLIGHT_COLOR)
            screen.blit(selected_highlight, p.Rect(col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE))
            # highlight possible moves
            move_highlight: Surface = p.Surface((SQ_SIZE, SQ_SIZE))
            move_highlight.set_alpha(100)
            move_highlight.fill(MOVE_HIGHLIGHT_COLOR)
            for move in valid_moves.values():
                if move.start_row == row and move.start_col == col:
                    screen.blit(move_highlight, (move.end_col * SQ_SIZE, move.end_row * SQ_SIZE))
    # Highlight the king when a player is in check.
    if game_state.in_check:
        if game_state.white_to_move:
            king_row = game_state.white_king_location[0]
            king_col = game_state.white_king_location[1]
        else:
            king_row = game_state.black_king_location[0]
            king_col = game_state.black_king_location[1]
        check_highlight: Surface = p.Surface((SQ_SIZE, SQ_SIZE))
        check_highlight.set_alpha(100)
        color = CHECK_HIGHLIGHT_COLOR
        check_highlight.fill(color)
        screen.blit(check_highlight, p.Rect(king_col * SQ_SIZE, king_row * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def draw_text(screen: Surface, text: str) -> None:
    """
    Draws text on the screen.

    Args:
        screen (Surface): The screen to draw text on.
        text (str): The text to draw.

    Returns:
        None
    """
    font = p.font.SysFont(FONT, FONT_SIZE, True, False)
    text_object = font.render(text, False, FONT_SHADOW)
    text_location = p.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH / 2 - text_object.get_width() / 2,
                                                     HEIGHT / 2 - text_object.get_height() / 2)
    screen.blit(text_object, text_location)
    text_object = font.render(text, False, FONT_COLOR)
    screen.blit(text_object, text_location.move(FONT_SIZE / 16, FONT_SIZE / 16))


def animate_move(move: Move, screen: Surface, board: List[List[str]], clock: Clock) -> None:
    """
    Animates a chess move.

    Arguments:
        move (Move): The move to animate.
        screen (Surface): The screen to animate on.
        board (List[List[str]]: The board to draw pieces from.
        clock (Clock): A pygame clock to track frames.

    Returns:
        None
    """
    colors: Tuple[Color, Color] = (LIGHT_SQUARE_COLOR, DARK_SQUARE_COLOR)
    delta_row: int = move.end_row - move.start_row
    delta_col: int = move.end_col - move.start_col
    frames_per_square: int = 5
    frame_count: int = (abs(delta_row) + abs(delta_col)) * frames_per_square
    for frame in range(frame_count + 1):
        frame_row: float = move.start_row + delta_row * frame / frame_count
        frame_col: float = move.start_col + delta_col * frame / frame_count
        __draw_board(screen=screen)
        __draw_pieces(screen=screen, board=board)
        color = colors[(move.end_row + move.end_col) % 2]
        end_tile: Rect = p.Rect(move.end_col * SQ_SIZE, move.end_row * SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, end_tile)
        # Make sure to draw the captured piece
        if move.piece_captured != "--":
            screen.blit(IMAGES[move.piece_captured], end_tile)
        screen.blit(IMAGES[move.piece_moved], p.Rect(frame_col * SQ_SIZE, frame_row * SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(60)


def main() -> None:
    """
    Run a game of chess and display the starting board.

    Returns:
        None
    """
    p.init()
    p.display.set_caption('Chess')
    screen: Surface = p.display.set_mode((WIDTH, HEIGHT))
    clock: Clock = p.time.Clock()
    screen.fill(p.Color("white"))

    load_images()
    game_state: GameState = GameState()
    valid_moves: Dict[str, Move] = game_state.generate_valid_moves()
    ai: ChessAI = NegamaxAlphaBetaChessAI(game_state=game_state)

    move_made: bool = False
    game_over: bool = False
    animate: bool = True
    # True if a human is playing white, False is an AI is playing white
    player_one: bool = True
    # True if a human is playing black, False is an AI is playing black
    player_two: bool = False

    # PyGame main loop which will keep track of events
    running: bool = True
    # keeps track of the tile last selected by the player (row, col)
    selected: Tuple[int, int] = (NO_VALUE, NO_VALUE)
    # keeps track of the tiles clicked by the player to make a move (two tuples [(row, col), (row, col)])
    clicks: List[Tuple[int, int]] = []

    while running:
        is_human_turn: bool = (game_state.white_to_move and player_one) or (not game_state.white_to_move and player_two)
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            elif e.type == p.MOUSEBUTTONDOWN:
                if not game_over and is_human_turn:
                    # location is a tuple (x, y)
                    location: tuple = p.mouse.get_pos()
                    col: int = int(location[0] // SQ_SIZE)
                    row: int = int(location[1] // SQ_SIZE)
                    if selected == (row, col):
                        selected = (NO_VALUE, NO_VALUE)
                        clicks = []
                    else:
                        selected = (row, col)
                        clicks.append((row, col))
                    if len(clicks) >= 2:
                        if game_state.board[clicks[0][0]][clicks[0][1]] == "--":
                            clicks.pop(0)
                            continue
                        move: Move = Move(start=clicks[0], end=clicks[1], board=game_state.board)
                        if str(move.move_id) in valid_moves.keys():
                            # Use the move from valid moves in case of an en passant
                            move = valid_moves[str(move.move_id)]
                            print(move.get_chess_notation())
                            game_state.make_move(move=move)
                            animate = True
                            move_made = True
                            selected = (NO_VALUE, NO_VALUE)
                            clicks = []
                        if not move_made:
                            clicks = [selected]
            elif e.type == p.KEYDOWN:
                # undo a move
                if e.key == p.K_z:
                    game_state.undo_move()
                    if player_one ^ player_two:
                        game_state.undo_move()
                    valid_moves = game_state.generate_valid_moves()
                    selected = (NO_VALUE, NO_VALUE)
                    clicks = []
                    move_made = True
                    game_over = False
                    animate = False
                # restart the game
                elif e.key == p.K_r:
                    game_state = GameState()
                    valid_moves = game_state.generate_valid_moves()
                    ai = NegamaxAlphaBetaChessAI(game_state=game_state)
                    selected = (NO_VALUE, NO_VALUE)
                    clicks = []
                    move_made = False
                    game_over = False

        # AI playing
        if not game_over and not is_human_turn:
            ai_move: Move = ai.find_move()
            game_state.make_move(move=ai_move)
            move_made = True
            animate = True

        if move_made:
            if animate:
                animate_move(move=game_state.move_log[-1], screen=screen, board=game_state.board, clock=clock)
            valid_moves = game_state.generate_valid_moves()
            move_made = False
        draw_game_state(screen=screen, game_state=game_state, valid_moves=valid_moves, selected=selected)
        clock.tick(MAX_FPS)
        if game_state.checkmate or game_state.stalemate:
            game_over = True
            if game_state.stalemate:
                draw_text(screen=screen, text="Stalemate")
            else:
                if game_state.white_to_move:
                    draw_text(screen=screen, text="Black Wins by Checkmate")
                else:
                    draw_text(screen=screen, text="White Wins by Checkmate")
        p.display.flip()


if __name__ == "__main__":
    main()
