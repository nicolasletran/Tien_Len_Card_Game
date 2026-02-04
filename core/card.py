# core/card.py

RANKS = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]  # 2-10, J=11, Q=12, K=13, A=14
SUITS = ["♠", "♣", "♦", "♥"]  # Spade < Club < Diamond < Heart

# Tiến Lên rank values: 3 smallest, 2 highest
TIEN_LEN_RANK_VALUE = {3: 1, 4: 2, 5: 3, 6: 4, 7: 5, 8: 6, 9: 7, 10: 8,
                       11: 9, 12: 10, 13: 11, 14: 12, 2: 13}

SUIT_ORDER = {suit: i for i, suit in enumerate(SUITS)}  # For tie-breaks

class Card:
    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit

    def __str__(self):
        return f"{self.rank_symbol()}{self.suit}"

    def rank_symbol(self):
        if self.rank <= 10:
            return str(self.rank)
        return {11: "J", 12: "Q", 13: "K", 14: "A"}[self.rank]

    def value(self):
        """Return tuple (Tien Len rank value, suit order) for comparison"""
        return (TIEN_LEN_RANK_VALUE[self.rank], SUIT_ORDER[self.suit])
