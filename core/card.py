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

    def __repr__(self):
        return self.__str__()

    def rank_symbol(self):
        if self.rank <= 10:
            return str(self.rank)
        # Handle all rank cases including 2
        rank_map = {
            2: "2",
            11: "J",
            12: "Q", 
            13: "K",
            14: "A"
        }
        return rank_map.get(self.rank, str(self.rank))

    def value(self):
        """Return tuple (Tien Len rank value, suit order) for comparison"""
        return (TIEN_LEN_RANK_VALUE[self.rank], SUIT_ORDER[self.suit])
    
    # NEW VISUAL ENHANCEMENT METHODS (don't affect game logic)
    
    def get_rank_str(self):
        """Get rank as string for display purposes only"""
        return self.rank_symbol()
    
    def get_suit_color(self):
        """Get RGB color for this suit (visual only)"""
        if self.suit in ["♥", "♦"]:
            return (200, 0, 0)  # Red for hearts and diamonds
        else:
            return (0, 0, 0)    # Black for spades and clubs
    
    def get_card_name(self):
        """Get full card name for tooltips (visual only)"""
        rank_names = {
            2: "Two",
            3: "Three",
            4: "Four",
            5: "Five",
            6: "Six",
            7: "Seven",
            8: "Eight",
            9: "Nine",
            10: "Ten",
            11: "Jack",
            12: "Queen",
            13: "King",
            14: "Ace"
        }
        
        suit_names = {
            "♠": "Spades",
            "♣": "Clubs",
            "♦": "Diamonds",
            "♥": "Hearts"
        }
        
        rank_name = rank_names.get(self.rank, str(self.rank))
        suit_name = suit_names.get(self.suit, self.suit)
        
        return f"{rank_name} of {suit_name}"
    
    def is_face_card(self):
        """Check if this is a face card (J, Q, K, A) - visual only"""
        return self.rank in [11, 12, 13, 14]
    
    def get_sort_key(self):
        """Get sorting key for display purposes only"""
        # Sort by rank first, then suit
        rank_order = TIEN_LEN_RANK_VALUE.get(self.rank, 0)
        suit_order = SUIT_ORDER.get(self.suit, 0)
        return (rank_order, suit_order)
    
    def __eq__(self, other):
        """Compare cards for equality - game logic"""
        if not isinstance(other, Card):
            return False
        return self.rank == other.rank and self.suit == other.suit
    
    def __hash__(self):
        """Make cards hashable - game logic"""
        return hash((self.rank, self.suit))

# NEW VISUAL UTILITY FUNCTIONS (don't affect game logic)

def create_deck_visual():
    """Create a standard 52-card deck for visual reference"""
    deck = []
    for suit in SUITS:
        for rank in RANKS:
            deck.append(Card(rank, suit))
    return deck

def sort_cards_for_display(cards):
    """Sort cards for nice visual display (doesn't affect gameplay)"""
    return sorted(cards, key=lambda card: card.get_sort_key())

def filter_cards_by_suit(cards, suit):
    """Filter cards by suit for visual organization"""
    return [card for card in cards if card.suit == suit]

def filter_cards_by_rank(cards, rank):
    """Filter cards by rank for visual organization"""
    return [card for card in cards if card.rank == rank]

def get_card_groups(cards):
    """Group cards for visual display (pairs, triples, etc.)"""
    groups = {}
    for card in cards:
        rank = card.rank
        if rank not in groups:
            groups[rank] = []
        groups[rank].append(card)
    
    # Sort groups by size and rank
    result = {}
    for rank in sorted(groups.keys(), key=lambda r: TIEN_LEN_RANK_VALUE.get(r, 0)):
        group = groups[rank]
        if len(group) > 1:  # Only show groups with multiples
            result[rank] = sort_cards_for_display(group)
    
    return result

# Keep all original game logic functions

def compare_cards(card1, card2):
    """Original game logic for comparing two cards"""
    val1 = card1.value()
    val2 = card2.value()
    if val1[0] != val2[0]:
        return val1[0] - val2[0]
    return val1[1] - val2[1]

def is_higher_than(card1, card2):
    """Original game logic: check if card1 is higher than card2"""
    return compare_cards(card1, card2) > 0

# Optional: Add visual constants that don't affect gameplay
CARD_VISUAL_CONFIG = {
    'width': 70,
    'height': 100,
    'border_radius': 10,
    'shadow_offset': (3, 3),
    'selected_lift': -15,
    'hover_scale': 1.05
}

# For compatibility with existing code that might use these
if __name__ == "__main__":
    # Test that original functionality is preserved
    test_card1 = Card(10, "♥")
    test_card2 = Card(11, "♠")  # J♠
    
    print(f"Card 1: {test_card1}")
    print(f"Card 2: {test_card2}")
    print(f"Card 1 value: {test_card1.value()}")
    print(f"Card 2 value: {test_card2.value()}")
    print(f"Is {test_card1} higher than {test_card2}? {is_higher_than(test_card1, test_card2)}")
    
    # Test visual enhancements
    print(f"\nVisual enhancements:")
    print(f"Card 1 name: {test_card1.get_card_name()}")
    print(f"Card 1 suit color: {test_card1.get_suit_color()}")
    print(f"Card 2 is face card: {test_card2.is_face_card()}")