import logging
from collections import deque
from enum import Enum

from .player import Player

logger = logging.getLogger(__name__)


class GameState(Enum):
    SETUP = 0
    IN_PROGRESS = 1
    FINISHED = 2


class Game:
    POSITION_TEXT = {1: "first", 2: "second", 3: "third"}

    def __init__(
        self,
        players: list[Player],
        secret_code: str | None = None,
    ) -> None:
        if not players:
            raise ValueError("Players cannot be empty")
        self._players = players
        self._winners = deque()
        self._state = GameState.SETUP
        self._has_started = False
        self.set_secret_code_for_all_players(secret_code)

    def set_secret_code_for_all_players(self, secret_code: str | None) -> None:
        for player in self._players:
            player.set_secret_code_to_board(secret_code)

    @property
    def state(self) -> GameState:
        if not self._has_started:
            return GameState.SETUP
        if all(player.game_over for player in self._players):
            return GameState.FINISHED
        return GameState.IN_PROGRESS

    @property
    def players(self) -> list[Player]:
        return self._players

    @property
    def winner(self) -> Player | None:
        if not self._winners:
            return None
        return self._winners[0]

    @property
    def winners(self) -> deque[Player]:
        return self._winners

    def submit_guess(self, player: Player, guess: str) -> None:
        if not self._has_started:
            self._has_started = True
        if player in self._winners:
            logger.info("%s already won the game", player.name)
            return
        if player.game_over:
            logger.info("%s can no longer play.", player.name)
            return

        player.make_guess(guess)

        if player.game_won and player not in self._winners:
            self._winners.append(player)
            position = len(self._winners)
            position_text = self.POSITION_TEXT.get(position, f"{position}th")
            logger.info("%s won the game in %s place!", player.name, position_text)
        elif player.game_over and not player.game_won:
            logger.info("%s has no more guesses.", player.name)
