# core/deck.py
from core.card import Card, RANKS, SUITS
import random

class Deck:
    def __init__(self):
        self.cards = [Card(rank, suit) for suit in SUITS for rank in RANKS]

    def shuffle(self):
        random.shuffle(self.cards)

    def deal(self, num_players=4):
        hands = [[] for _ in range(num_players)]
        for i, card in enumerate(self.cards):
            hands[i % num_players].append(card)
        # Sort each hand by Tiến Lên value
        for hand in hands:
            hand.sort(key=lambda c: c.value())
        return hands
