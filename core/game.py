# core/game.py
from core.deck import Deck
from core.player import Player
from core.rules import is_valid_play, beats
import random

class Game:
    def __init__(self):
        self.players = [Player(f"You"), Player("Bot 1"), Player("Bot 2"), Player("Bot 3")]
        deck = Deck()
        deck.shuffle()
        hands = deck.deal()
        for i, player in enumerate(self.players):
            player.hand = hands[i]

        self.last_play = []       # Cards on table
        self.pass_count = 0       # Consecutive passes

    def bot_turn(self, bot):
        # Simple AI: play first valid card(s) that beats table or pass
        hand = bot.hand
        if not hand:
            return None

        # Try single cards first
        for card in hand:
            if not self.last_play or beats([card], self.last_play):
                bot.hand.remove(card)
                return [card]

        # Try pairs
        rank_count = {}
        for card in hand:
            rank_count[card.rank] = rank_count.get(card.rank, 0) + 1
        for rank, count in rank_count.items():
            if count >= 2 and (not self.last_play or (len(self.last_play)==2 and beats([c for c in hand if c.rank==rank][:2], self.last_play))):
                pair = [c for c in hand if c.rank==rank][:2]
                for c in pair:
                    hand.remove(c)
                return pair

        # Try triple / four-of-a-kind similarly if needed (optional)
        return None  # pass
