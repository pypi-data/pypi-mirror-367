import logging

from .board import Board

logger = logging.getLogger(__name__)


class Player:
    def __init__(self, name: str, board: Board) -> None:
        self.name = name
        self._board = board

    @property
    def board(self):
        return self._board

    @property
    def game_over(self):
        return self._board.game_over

    @property
    def game_won(self):
        return self._board.game_won

    def set_secret_code_to_board(self, secret_code: str | None) -> None:
        self._board.secret_code = secret_code

    def make_guess(self, guess: str) -> None:
        if self.game_over:
            logger.info("%s has no more guesses.", self.name)
            return
        self._board.evaluate_guess(self._board.current_board_row_index, guess)
