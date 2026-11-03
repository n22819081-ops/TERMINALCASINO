from dataclasses import dataclass

from .utils import cprint, cinput, clear_screen


@dataclass
class GameStats:
    game_name: str
    starting_balance: int
    ending_balance: int = 0
    rounds_played: int = 0
    wins: int = 0
    losses: int = 0
    pushes: int = 0

    @property
    def net(self) -> int:
        return self.ending_balance - self.starting_balance

    @property
    def win_rate(self) -> str:
        if self.rounds_played == 0:
            return "N/A"
        return f"{self.wins / self.rounds_played * 100:.1f}%"


def display_stats(stats: GameStats, player_name: str | None = None, wait: bool = True, clear: bool = True) -> None:
    """Display a post-game session summary."""
    if clear:
        clear_screen()

    net = stats.net
    net_str = f"+{net}" if net > 0 else str(net)

    rows = [
        ("Game", stats.game_name),
        ("Hands Played", str(stats.rounds_played)),
        ("Wins", str(stats.wins)),
        ("Losses", str(stats.losses)),
        ("Pushes", str(stats.pushes)),
        ("Win Rate", stats.win_rate),
        ("", ""),
        ("Starting Balance", str(stats.starting_balance)),
        ("Ending Balance", str(stats.ending_balance)),
        ("Net Profit/Loss", net_str),
    ]
    if player_name is not None:
        rows.insert(0, ("Player", player_name))

    label_width = max(len(r[0]) for r in rows)
    value_width = max(len(r[1]) for r in rows)
    inner_width = label_width + value_width + 7  # padding + colon + spaces
    box_width = inner_width + 2  # borders

    title = " Session Summary "
    side = (inner_width - len(title)) // 2
    top_border = f"┌{'─' * side}{title}{'─' * (inner_width - side - len(title))}┐"
    bot_border = f"└{'─' * inner_width}┘"

    cprint(top_border)
    for label, value in rows:
        if label == "":
            content = " " * inner_width
        else:
            content = f"  {label + ':':<{label_width + 1}}  {value:>{value_width}}  "
        cprint(f"│{content}│")
    cprint(bot_border)

    if wait:
        cprint("")
        cinput("Press Enter to return to menu...")
