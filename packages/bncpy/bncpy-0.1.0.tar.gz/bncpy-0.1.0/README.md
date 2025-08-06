# Benjamin and Charlotte Game

## Installation

```bash
pip install bnc
```

## Usage

```bash
from bnc import Board, Game, Player

# Create a board with custom settings
board = Board(code_length=4, num_of_colors=6, num_of_guesses=10)

# Create players
player1 = Player("Jae", board)

# Create and start a game
game = Game([player1], secret_code="1234")

# Make a guess
game.submit_guess(player1, "1234")
```
