from dataclasses import dataclass

from .accounts import Account
from .config import Config
from typing import Tuple
# from .cards import Card

# Card = tuple[int | str, str]


@dataclass
class GameContext:
    account: Account
    config: Config
    # Optional second player (2-player mode). Persisted on the shared context so
    # the alternate player survives across games. None for single-player.
    alternate_account: Account | None = None