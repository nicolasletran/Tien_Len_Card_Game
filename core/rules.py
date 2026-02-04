# core/rules.py

# -----------------------------
# Card strength & ordering
# -----------------------------

RANK_ORDER = {
    '3': 0, '4': 1, '5': 2, '6': 3, '7': 4, '8': 5,
    '9': 6, '10': 7, 'J': 8, 'Q': 9, 'K': 10, 'A': 11, '2': 12
}

# Mapping from integer ranks to string values
INT_RANK_TO_STR = {
    3: '3', 4: '4', 5: '5', 6: '6', 7: '7', 8: '8',
    9: '9', 10: '10', 11: 'J', 12: 'Q', 13: 'K', 14: 'A', 15: '2'
}

SUIT_ORDER = {
    '♠': 0,  # smallest
    '♣': 1,
    '♦': 2,
    '♥': 3   # biggest
}

def card_strength(card):
    """
    Normalizes rank so:
    3 < 4 < ... < K < A < 2
    Works with card.rank as int OR string.
    
    Your card system uses:
    3=3, 4=4, 5=5, 6=6, 7=7, 8=8, 9=9, 10=10
    J=11, Q=12, K=13, A=14, 2=2
    """
    # DEBUG - uncomment to see what's happening
    # print(f"DEBUG card_strength: {card}, rank={card.rank}, type={type(card.rank)}")
    
    # Normalize rank
    if isinstance(card.rank, int):
        # Your card system: 3=3, 4=4, ..., 10=10, J=11, Q=12, K=13, A=14, 2=2
        # We need to map this to: 3=0, 4=1, ..., K=10, A=11, 2=12
        
        if card.rank == 2:      # 2 is highest
            rank_value = 12
        elif card.rank == 14:   # A
            rank_value = 11
        elif card.rank == 13:   # K
            rank_value = 10
        elif card.rank == 12:   # Q
            rank_value = 9
        elif card.rank == 11:   # J
            rank_value = 8
        elif card.rank == 10:   # 10
            rank_value = 7
        elif card.rank == 9:    # 9
            rank_value = 6
        elif card.rank == 8:    # 8
            rank_value = 5
        elif card.rank == 7:    # 7
            rank_value = 4
        elif card.rank == 6:    # 6
            rank_value = 3
        elif card.rank == 5:    # 5
            rank_value = 2
        elif card.rank == 4:    # 4
            rank_value = 1
        elif card.rank == 3:    # 3 (lowest)
            rank_value = 0
        else:
            # Fallback
            rank_value = 0
    else:
        # Handle string ranks
        if card.rank == '2':
            rank_value = 12
        elif card.rank == 'A':
            rank_value = 11
        elif card.rank == 'K':
            rank_value = 10
        elif card.rank == 'Q':
            rank_value = 9
        elif card.rank == 'J':
            rank_value = 8
        else:
            # Handle numeric ranks like '10', '9', etc.
            try:
                num_rank = int(card.rank)
                if num_rank >= 3 and num_rank <= 10:
                    rank_value = num_rank - 3  # 3=0, 4=1, ..., 10=7
                else:
                    rank_value = 0  # Default
            except ValueError:
                rank_value = 0  # Default fallback
    
    # Calculate total strength: rank * 4 + suit
    suit_value = SUIT_ORDER.get(card.suit, 0)
    strength = rank_value * 4 + suit_value
    
    # DEBUG - uncomment to see calculations
    # print(f"DEBUG card_strength result: rank_value={rank_value}, suit_value={suit_value}, strength={strength}")
    
    return strength

# -----------------------------
# Combination detection
# -----------------------------

def is_single(cards):
    return len(cards) == 1

def is_pair(cards):
    if len(cards) != 2:
        return False
    return cards[0].rank == cards[1].rank

def is_triple(cards):
    if len(cards) != 3:
        return False
    return cards[0].rank == cards[1].rank == cards[2].rank

def is_quadruple(cards):
    """
    Four of a kind
    """
    if len(cards) != 4:
        return False
    return all(card.rank == cards[0].rank for card in cards)

def is_straight(cards):
    """
    Straight rules:
    - At least 3 cards
    - Continuous ranks
    - Cannot contain 2
    """
    if len(cards) < 3:
        return False

    # 2 cannot be in straight
    if any(card.rank == 2 or card.rank == 15 for card in cards):
        return False

    # Get card strengths and extract rank values (divide by 4)
    strengths = [card_strength(card) for card in cards]
    rank_values = [s // 4 for s in strengths]
    
    # Sort and check for consecutive
    rank_values.sort()
    
    for i in range(len(rank_values) - 1):
        if rank_values[i] + 1 != rank_values[i + 1]:
            return False

    return True

def is_consecutive_pairs(cards):
    """
    Three or more consecutive pairs
    Example: [3♠3♣, 4♠4♣, 5♠5♣] is 3 consecutive pairs
    """
    # Must have even number of cards and at least 6 cards (3 pairs)
    if len(cards) < 6 or len(cards) % 2 != 0:
        return False
    
    # 2 cannot be in consecutive pairs
    if any(card.rank == 2 or card.rank == 15 for card in cards):
        return False
    
    # Group cards by rank
    rank_groups = {}
    for card in cards:
        if card.rank not in rank_groups:
            rank_groups[card.rank] = []
        rank_groups[card.rank].append(card)
    
    # Check if all ranks have exactly 2 cards
    for rank, cards_list in rank_groups.items():
        if len(cards_list) != 2:
            return False
    
    # Get sorted rank values
    rank_values = sorted([card_strength(cards[0]) // 4 for cards in rank_groups.values()])
    
    # Check if we have enough pairs
    if len(rank_values) < 3:
        return False
    
    # Check if ranks are consecutive
    for i in range(len(rank_values) - 1):
        if rank_values[i] + 1 != rank_values[i + 1]:
            return False
    
    return True

# -----------------------------
# Play type detection
# -----------------------------

def get_play_type(cards):
    if is_single(cards):
        return "single"
    if is_pair(cards):
        return "pair"
    if is_triple(cards):
        return "triple"
    if is_quadruple(cards):
        return "quadruple"
    if is_straight(cards):
        return "straight"
    if is_consecutive_pairs(cards):
        return "consecutive_pairs"
    return None

def is_valid_play(cards):
    """
    Used when table is empty or starting a new round.
    """
    return get_play_type(cards) is not None

# -----------------------------
# Beating logic with BOMB support
# -----------------------------

def beats(play, table):
    """
    Determines if `play` beats `table`.
    Bombs can only beat plays containing 2.
    """
    # Empty table → always valid
    if not table:
        return is_valid_play(play)

    play_type = get_play_type(play)
    table_type = get_play_type(table)

    # Check for bombs
    play_is_bomb = play_type in ["quadruple", "consecutive_pairs"] and len(play) >= 4
    
    # Check if table contains any 2
    table_has_two = any(card.rank == 2 or card.rank == 15 for card in table)
    
    # Bomb logic: bombs can only beat plays containing 2
    if play_is_bomb:
        if table_has_two:
            # Bomb can beat plays containing 2
            return True
        else:
            # Bomb cannot beat plays without 2
            return False
    
    # Non-bomb cannot beat bomb (if bomb was used legally on a 2 play)
    if not play_is_bomb and table_type in ["quadruple", "consecutive_pairs"] and len(table) >= 4:
        # Check if the bomb was played on a 2
        bomb_was_on_two = any(card.rank == 2 or card.rank == 15 for card in table)
        if bomb_was_on_two:
            return False  # Can't beat a bomb that was played on a 2
    
    # Normal play comparison (both non-bombs, or bomb not applicable)
    # Must be same type
    if play_type != table_type:
        return False

    # Must be same length (important for straights and consecutive pairs)
    if play_type in ["straight", "consecutive_pairs"]:
        if len(play) != len(table):
            return False

    # Compare strongest card
    play_sorted = sorted(play, key=card_strength)
    table_sorted = sorted(table, key=card_strength)

    return card_strength(play_sorted[-1]) > card_strength(table_sorted[-1])

def _compare_bombs(bomb1, bomb2):
    """
    Compare two bombs when both are played on 2s.
    Higher/longer bomb beats lower/shorter bomb.
    """
    bomb1_type = get_play_type(bomb1)
    bomb2_type = get_play_type(bomb2)
    
    # Helper function to get bomb strength
    def get_bomb_strength(bomb):
        bomb_type = get_play_type(bomb)
        if bomb_type == "quadruple":
            # Four of a kind: strength based on rank
            rank = bomb[0].rank
            # Get rank value using card_strength and extract rank component
            rank_strength = card_strength(bomb[0])
            rank_value = rank_strength // 4
            return rank_value * 100 + len(bomb)
        else:  # consecutive_pairs
            # Longer chain is stronger, and higher ranks within chain matter
            max_strength = max(card_strength(card) for card in bomb)
            max_rank_value = max_strength // 4
            return max_rank_value * 100 + len(bomb)
    
    bomb1_strength = get_bomb_strength(bomb1)
    bomb2_strength = get_bomb_strength(bomb2)
    
    return bomb1_strength > bomb2_strength