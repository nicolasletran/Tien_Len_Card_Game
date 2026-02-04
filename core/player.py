class Player:
    def __init__(self, name, is_human=False):
        self.name = name
        self.hand = []
        self.is_human = is_human

    def sort_hand(self):
        # Sort by Tiến Lên value (rank + suit)
        self.hand.sort(key=lambda c: c.value())

    def remove_cards(self, cards):
        for c in cards:
            self.hand.remove(c)

    def has_won(self):
        return len(self.hand) == 0
