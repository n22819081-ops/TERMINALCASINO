from time import sleep
import shutil

from casino.utils import clear_screen, cprint, cinput, display_topbar
from ..constants import *


class BlackjackView:
    """
    Owns all terminal rendering and user input for a Blackjack game.

    Game/round logic should never call cinput/cprint/sleep directly —
    it should ask this class to do it.
    """

    def __init__(self, context) -> None:
        self.context = context

    def display_topbar(self) -> None:
        display_topbar(self.context.account, **BLACKJACK_HEADER_OPTIONS)
        # Also show the 2nd player's balance, in the same format as the primary player
        header_width = max(len(l) for l in BLACKJACK_HEADER.splitlines() if l.strip())
        for p in (getattr(self, "seated", None) or []):
            if p.account is self.context.account:
                continue
            left = f"👤 {p.name}"
            right = f"💰 {p.account.balance}"
            cprint(f"{left}{right.rjust(header_width - len(left))}")

    def render_table(self, players, dealer_hand,
                      active_player_idx: int | None = None,
                      active_hand_idx: int | None = None) -> None:
        clear_screen()
        self.display_topbar()
        # Accept a single Player (back-compat) or a list of Players (2-player).
        if not isinstance(players, (list, tuple)):
            players = [players]
        dealer_hand.print_hand(label="Dealer's Hand")
        cprint("=" * 40)
        # 2-player, one hand each, and it fits: lay the players side by side.
        if len(players) == 2 and all(len(p.hands) == 1 for p in players):
            left = self._hand_block(players[0],
                                    active_player_idx == 0 and active_hand_idx == 0)
            right = self._hand_block(players[1],
                                     active_player_idx == 1 and active_hand_idx == 0)
            left_w = max(len(l) for l in left)
            right_w = max(len(l) for l in right)
            # Fall back to stacked if side-by-side is too wide for THIS terminal.
            try:
                term_w = shutil.get_terminal_size().columns
            except OSError:
                term_w = 100
            if left_w + 4 + right_w <= term_w:
                gap = 4
                for i in range(max(len(left), len(right))):
                    l = left[i] if i < len(left) else ""
                    r = right[i] if i < len(right) else ""
                    cprint(f"{l:<{left_w + gap}}{r}")
                return
        # 1-player (or any split hand): render stacked (back-compat).
        for p_idx, player in enumerate(players):
            num_hands = len(player.hands)
            for idx, hand in enumerate(player.hands):
                is_active = (p_idx == active_player_idx and idx == active_hand_idx)
                label = f"{player.name} - Hand {idx + 1}" if num_hands > 1 else player.name
                hand.print_hand(label=label, is_active=is_active)
                print()

    def _hand_block(self, player, is_active: bool) -> list[str]:
        hand = player.hands[0]
        has_hidden = any(card.hidden for card in hand.cards)
        display_total = "?" if has_hidden else hand.total
        bj_tag = " [BLACKJACK!]" if hand.is_blackjack else ""
        bust_tag = " [BUSTED!]" if hand.is_bust else ""
        header = f"{player.name} | Bet: {hand.bet} | TOTAL: {display_total}{bj_tag}{bust_tag}"
        if is_active:
            header = f" ► {header}  ◄ YOUR TURN"
        lines = [header]
        # Card faces side by side (mirrors print_cards).
        card_str = [card.back if card.hidden else card.front for card in hand.cards]
        card_lines = [card.strip().splitlines() for card in card_str]
        max_height = max(len(cl) for cl in card_lines)
        for cl in card_lines:
            width = len(cl[0])
            cl.extend([" " * width] * (max_height - len(cl)))
        rows = ["  ".join(cl[i] for cl in card_lines) for i in range(max_height)]
        lines.extend(rows)
        if hand.outcome_msg:
            footer = f"OUTCOME: {hand.outcome_msg}"
            if hand.bet_result_str:
                footer += f" ({hand.bet_result_str})"
            lines.append(footer)
        return lines

    def prompt_bet(self, player, error_msg: str = "") -> str:
        clear_screen()
        self.display_topbar()
        if error_msg:
            cprint(error_msg)
        return cinput(f"🤵 : {player.name}, how much would you like to bet? ").strip()

    def show_no_funds(self) -> None:
        clear_screen()
        self.display_topbar()
        cprint(NO_FUNDS_MSG)
        cinput("Press [Enter] to continue.")

    def prompt_action(self, options_str: str) -> str:
        return cinput(options_str).strip().upper()

    def show_invalid_choice(self) -> None:
        cprint(INVALID_CHOICE_MSG)

    def announce(self, message: str, pause: float = 0.8) -> None:
        cprint(message)
        sleep(pause)

    def prompt_play_again(self) -> str:
        cprint(STAY_AT_TABLE_PROMPT)
        return cinput(YES_OR_NO_PROMPT)
