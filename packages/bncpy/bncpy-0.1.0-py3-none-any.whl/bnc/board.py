from collections import Counter
from dataclasses import dataclass

from .utils import (
    check_board_row_index,
    validate_code_input,
    validate_secret_code,
)


@dataclass
class BoardRow:
    guess: list[int]
    bulls: int = 0
    cows: int = 0
    is_filled: bool = False

    @property
    def is_winning_row(self):
        return self.is_filled and self.bulls == len(self.guess)


class Board:
    def __init__(
        self,
        code_length: int = 4,
        num_of_colors: int = 6,
        num_of_guesses: int = 10,
        secret_code: str | None = None,
    ) -> None:
        if code_length < 3:
            raise ValueError(f"code_length must be at least 3, got {code_length}")
        if num_of_colors < 5:
            raise ValueError(f"num_of_colors must be at least 5, got {num_of_colors}")
        if num_of_guesses < 1:
            raise ValueError(f"num_of_guesses must be at least 1, got {num_of_guesses}")

        self._secret_code = secret_code
        self._code_length = code_length
        self._num_of_colors = num_of_colors
        self._num_of_guesses = num_of_guesses
        self._board: list[BoardRow] = self._init_board()
        self._secret_digits: list[int] = []
        self._game_won = False
        self._game_over = False

    def _init_board(self):
        board = []
        for _ in range(self._num_of_guesses):
            board.append(BoardRow([0] * self._code_length))
        return board

    @property
    def board(self):
        return self._board

    @property
    def num_of_guesses(self):
        return self._num_of_guesses

    @property
    def secret_code(self):
        return self._secret_code

    @secret_code.setter
    def secret_code(self, secret_code: str) -> None:
        self._secret_digits = validate_secret_code(
            secret_code, self._code_length, self._num_of_colors
        )
        self._secret_code = secret_code

    @property
    def num_of_colors(self):
        return self._num_of_colors

    @property
    def code_length(self):
        return self._code_length

    @property
    def game_won(self):
        return self._game_won

    @property
    def game_over(self):
        return self._game_over

    @property
    def current_board_row_index(self) -> int:
        for i, row in enumerate(self._board):
            if not row.is_filled:
                return i
        return -1

    def create_new_board(self):
        return Board(
            code_length=self._code_length,
            num_of_colors=self._num_of_colors,
            num_of_guesses=self._num_of_guesses,
            secret_code=self._secret_code,
        )

    def set_board_row(
        self, bulls: int, cows: int, guess_digits: list[int], board_row_index: int
    ):
        self._board[board_row_index] = BoardRow(
            guess=guess_digits, bulls=bulls, cows=cows, is_filled=True
        )

    def calculate_bulls_and_cows(self, guess_digits: list[int]) -> tuple[int, int]:
        if not self._secret_digits:
            raise ValueError(
                "Secret code must be set before calculating bulls and cows"
            )

        bulls_count = 0
        for i in range(len(self._secret_digits)):
            if self._secret_digits[i] == guess_digits[i]:
                bulls_count += 1

        secret_counter = Counter(self._secret_digits)
        guess_counter = Counter(guess_digits)

        total_matches = 0
        for digit in guess_counter:
            if digit in secret_counter:
                total_matches += min(guess_counter[digit], secret_counter[digit])

        cows_count = total_matches - bulls_count
        return bulls_count, cows_count

    def evaluate_guess(self, board_row_index: int, guess: str) -> None:
        if not check_board_row_index(board_row_index, self._num_of_guesses):
            raise ValueError("Row index is out of range")

        guess_digits = validate_code_input(guess, self.code_length, self.num_of_colors)
        bulls_count, cows_count = self.calculate_bulls_and_cows(guess_digits)
        self.set_board_row(bulls_count, cows_count, guess_digits, board_row_index)

        if self._board[board_row_index].is_winning_row:
            self._game_won = True
            self._game_over = True
        elif board_row_index == self._num_of_guesses - 1:
            self._game_over = True
