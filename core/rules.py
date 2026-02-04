# core/rules.py
from core.card import SUIT_ORDER

def is_valid_play(cards):
    """Return True if the cards form a valid single, pair, triple, or four-of-a-kind"""
    if not cards:
        return False
    ranks = [c.rank for c in cards]
    return all(r == ranks[0] for r in ranks)

def beats(new_play, last_play):
    """
    Return True if new_play beats last_play according to Tiến Lên rules
    Supports single, pair, triple, four-of-a-kind
    """
    if len(new_play) != len(last_play):
        return False

    # Compare by Tiến Lên rank first, then suit
    new_max = max(new_play, key=lambda c: c.value())
    last_max = max(last_play, key=lambda c: c.value())

    return new_max.value() > last_max.value()
