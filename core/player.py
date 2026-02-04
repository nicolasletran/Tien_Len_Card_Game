# core/player.py

class Player:
    def __init__(self, name, is_human=False):
        self.name = name
        self.hand = []
        self.is_human = is_human
        self.has_passed = False  # Track if player passed this round
        self.score = 0  # Optional: for tracking wins

    def sort_hand(self):
        """Sort hand by Tiến Lên value (rank + suit)"""
        self.hand.sort(key=lambda c: c.value())
        return self  # Allow method chaining

    def sort_hand_by_display(self):
        """Sort hand for better visual display (rank then suit)"""
        self.hand.sort(key=lambda c: (c.value()[0], c.value()[1]))
        return self

    def remove_cards(self, cards):
        """Remove specific cards from hand"""
        for card in cards:
            if card in self.hand:
                self.hand.remove(card)
        return self

    def add_cards(self, cards):
        """Add cards to hand"""
        self.hand.extend(cards)
        self.sort_hand()
        return self

    def has_won(self):
        """Check if player has won (empty hand)"""
        return len(self.hand) == 0

    def get_hand_size(self):
        """Get number of cards in hand"""
        return len(self.hand)

    def get_hand_copy(self):
        """Get a copy of the hand (for AI analysis without modifying)"""
        return self.hand.copy()

    def reset_round(self):
        """Reset player state for new round"""
        self.has_passed = False

    def __str__(self):
        """String representation of player"""
        return f"{self.name} ({len(self.hand)} cards)"

    def __repr__(self):
        return f"Player(name='{self.name}', hand_size={len(self.hand)})"

    # Optional: Add methods for AI analysis
    def get_card_groups(self):
        """Get groups of same-rank cards for AI strategy"""
        from collections import defaultdict
        groups = defaultdict(list)
        for card in self.hand:
            groups[card.rank].append(card)
        return groups

    def has_pair(self, rank=None):
        """Check if player has a pair of specific rank or any pair"""
        groups = self.get_card_groups()
        if rank:
            return len(groups.get(rank, [])) >= 2
        return any(len(cards) >= 2 for cards in groups.values())

    def has_triple(self, rank=None):
        """Check if player has a triple of specific rank or any triple"""
        groups = self.get_card_groups()
        if rank:
            return len(groups.get(rank, [])) >= 3
        return any(len(cards) >= 3 for cards in groups.values())