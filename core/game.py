# core/game.py
from core.deck import Deck
from core.player import Player
from core.rules import is_valid_play, beats, get_play_type, is_single, is_pair, is_triple, is_straight
import random
from collections import defaultdict
from datetime import datetime

class Game:
    def __init__(self):
        self.players = [Player("You"), Player("Bot 1"), Player("Bot 2"), Player("Bot 3")]
        deck = Deck()
        deck.shuffle()
        hands = deck.deal()
        for i, player in enumerate(self.players):
            player.hand = hands[i]
            # Sort bot hands for better AI decisions
            if i > 0:  # Sort bot hands only
                player.sort_hand()

        self.last_play = []       # Current cards on table
        self.pass_count = 0       # Consecutive passes
        self.play_history = []    # NEW: Track all plays in current round
        self.round_number = 1     # Track round number
        self.total_plays = 0      # Total plays in game
        self.bomb_used = False    # Track if a bomb has been used this round

    def bot_turn(self, bot):
        """
        Improved bot AI that tries to play valid combinations that beat the table
        Strategy: Play the smallest valid combination that beats the table
        """
        if not bot.hand:
            return None
        
        # Sort bot's hand for consistent selection
        bot.sort_hand()
        
        # If table is empty (new round), play various combinations
        if not self.last_play:
            play = self._play_best_first_combination(bot)
            if play:
                # IMPORTANT: Remove cards from bot's hand
                for card in play:
                    bot.hand.remove(card)
                self._record_play(bot, play)
            return play
        
        # Get the type of play on table
        table_type = get_play_type(self.last_play) if self.last_play else None
        
        # Try to find a combination that beats the table
        play = self._find_beating_play(bot, table_type)
        
        if play:
            # Remove played cards from bot's hand
            for card in play:
                bot.hand.remove(card)
            self._record_play(bot, play)
            return play
        
        # Bot passes
        self._record_pass(bot)
        return None

    def _play_best_first_combination(self, bot):
        """
        Play the best combination when starting a new round
        Strategy: Try to play combinations that use more cards to reduce hand size
        """
        from core.rules import card_strength
        
        hand = bot.hand.copy()
        
        if not hand:
            return None
        
        # Try to play various combinations in order of preference:
        # 1. Consecutive pairs (reduces hand size the most)
        # 2. Straight
        # 3. Quadruple (four of a kind)
        # 4. Triple
        # 5. Pair
        # 6. Single (last resort)
        
        # Check for consecutive pairs (3+ pairs = 6+ cards)
        consecutive_pairs = self._find_all_consecutive_pairs(hand)
        if consecutive_pairs:
            # Play the longest consecutive pairs
            longest_pairs = max(consecutive_pairs, key=len)
            if len(longest_pairs) >= 6:  # At least 3 pairs
                return longest_pairs
        
        # Check for straights
        straights = self._find_all_straights(hand)
        if straights:
            # Play the longest straight
            longest_straight = max(straights, key=len)
            if len(longest_straight) >= 3:
                return longest_straight
        
        # Check for quadruples (four of a kind)
        quadruples = self._find_all_quadruples(hand)
        if quadruples:
            # Play the smallest quadruple
            smallest_quadruple = min(quadruples, key=lambda q: max(card_strength(card) for card in q))
            return smallest_quadruple
        
        # Check for triples
        triples = self._find_all_triples(hand)
        if triples:
            # Play the smallest triple
            smallest_triple = min(triples, key=lambda t: max(card_strength(card) for card in t))
            return smallest_triple
        
        # Check for pairs
        pairs = self._find_all_pairs(hand)
        if pairs:
            # Play the smallest pair
            smallest_pair = min(pairs, key=lambda p: max(card_strength(card) for card in p))
            return smallest_pair
        
        # Last resort: play smallest single card
        if hand:
            smallest_card = min(hand, key=lambda c: card_strength(c))
            return [smallest_card]
        
        return None

    def _find_beating_play(self, bot, table_type):
        """
        Find a play that beats the current table combination
        """
        from core.rules import card_strength, beats
        
        hand = bot.hand.copy()
        
        # First check if table has 2 - if yes, consider using bomb
        table_has_two = any(card.rank == 2 or card.rank == 15 for card in self.last_play)
        if table_has_two:
            bombs = self._find_all_bombs(hand)
            if bombs and self._should_use_bomb(bot):
                # Use the smallest appropriate bomb
                for bomb in sorted(bombs, key=lambda b: max(card_strength(card) for card in b)):
                    if beats(bomb, self.last_play):
                        return bomb
        
        # Normal play logic for all other cases
        if table_type == "single":
            # Find a single card that beats the table
            table_card = self.last_play[0]
            for card in hand:
                if beats([card], [table_card]):
                    return [card]
        
        elif table_type == "pair":
            # Find a pair that beats the table pair
            table_rank = self.last_play[0].rank
            
            # Group cards by rank
            rank_groups = defaultdict(list)
            for card in hand:
                rank_groups[card.rank].append(card)
            
            # Look for pairs with higher rank
            for rank, cards in sorted(rank_groups.items(), key=lambda x: card_strength(x[1][0])):
                if len(cards) >= 2 and beats(cards[:2], self.last_play):
                    return cards[:2]
        
        elif table_type == "triple":
            # Find a triple that beats the table triple
            table_rank = self.last_play[0].rank
            
            # Group cards by rank
            rank_groups = defaultdict(list)
            for card in hand:
                rank_groups[card.rank].append(card)
            
            # Look for triples with higher rank
            for rank, cards in sorted(rank_groups.items(), key=lambda x: card_strength(x[1][0])):
                if len(cards) >= 3 and beats(cards[:3], self.last_play):
                    return cards[:3]
        
        elif table_type == "straight":
            # Find a straight that beats the table straight
            straights = self._find_all_straights(hand)
            table_straight = self.last_play
            
            for straight in straights:
                if len(straight) == len(table_straight) and beats(straight, table_straight):
                    return straight
        
        elif table_type == "quadruple":
            # Find a quadruple that beats the table quadruple
            table_rank = self.last_play[0].rank
            
            # Group cards by rank
            rank_groups = defaultdict(list)
            for card in hand:
                rank_groups[card.rank].append(card)
            
            # Look for quadruples with higher rank
            for rank, cards in sorted(rank_groups.items(), key=lambda x: card_strength(x[1][0])):
                if len(cards) >= 4 and beats(cards[:4], self.last_play):
                    return cards[:4]
        
        elif table_type == "consecutive_pairs":
            # Find consecutive pairs that beat the table
            consecutive_pairs_plays = self._find_all_consecutive_pairs(hand)
            table_pairs = self.last_play
            
            for pairs in consecutive_pairs_plays:
                if len(pairs) == len(table_pairs) and beats(pairs, table_pairs):
                    return pairs
        
        return None

    def _find_all_straights(self, hand):
        """
        Find all possible straights in a hand
        """
        from core.rules import card_strength
        
        straights = []
        if len(hand) < 3:
            return straights
        
        # Sort by card strength
        hand_sorted = sorted(hand, key=card_strength)
        
        # Remove duplicates by rank
        unique_ranks = []
        seen_ranks = set()
        for card in hand_sorted:
            if card.rank not in seen_ranks and card.rank != 2 and card.rank != 15:  # No 2s in straights
                unique_ranks.append(card)
                seen_ranks.add(card.rank)
        
        # Find consecutive sequences
        for i in range(len(unique_ranks) - 2):
            for j in range(i + 3, len(unique_ranks) + 1):
                sequence = unique_ranks[i:j]
                
                # Check if sequence is consecutive
                is_consecutive = True
                for k in range(len(sequence) - 1):
                    if card_strength(sequence[k]) // 4 + 1 != card_strength(sequence[k + 1]) // 4:
                        is_consecutive = False
                        break
                
                if is_consecutive and len(sequence) >= 3:
                    straights.append(sequence)
        
        return straights

    def _find_all_bombs(self, hand):
        """
        Find all possible bombs in a hand
        Bombs are:
        1. Four of a kind (quadruple)
        2. Three or more consecutive pairs
        """
        bombs = []
        
        # 1. Find four of a kind
        rank_groups = defaultdict(list)
        for card in hand:
            rank_groups[card.rank].append(card)
        
        for cards in rank_groups.values():
            if len(cards) >= 4:
                bombs.append(cards[:4])  # Take first 4 cards of this rank
        
        # 2. Find consecutive pairs (3 or more)
        consecutive_pairs = self._find_all_consecutive_pairs(hand)
        for pairs in consecutive_pairs:
            if len(pairs) >= 6:  # 3 pairs = 6 cards, 4 pairs = 8 cards, etc.
                bombs.append(pairs)
        
        return bombs

    def _find_all_consecutive_pairs(self, hand):
        """
        Find all sequences of consecutive pairs
        Example: [3♠3♣, 4♠4♣, 5♠5♣] is 3 consecutive pairs
        """
        from core.rules import card_strength
        
        consecutive_pairs_list = []
        
        # Group cards by rank and get pairs
        rank_groups = defaultdict(list)
        for card in hand:
            rank_groups[card.rank].append(card)
        
        # Get ranks that have at least 2 cards (can form pairs)
        pair_ranks = []
        for rank, cards in rank_groups.items():
            if len(cards) >= 2 and rank != 2 and rank != 15:  # 2 cannot be in consecutive pairs
                # Sort cards by suit strength
                cards.sort(key=card_strength, reverse=True)
                pair_ranks.append((rank, cards[:2]))
        
        # Sort by card strength
        pair_ranks.sort(key=lambda x: card_strength(x[1][0]))
        
        # Find consecutive sequences of pairs
        if len(pair_ranks) >= 3:
            # Find all possible sequences
            for start in range(len(pair_ranks) - 2):
                for end in range(start + 3, len(pair_ranks) + 1):
                    sequence = pair_ranks[start:end]
                    
                    # Check if ranks are consecutive
                    is_consecutive = True
                    for i in range(len(sequence) - 1):
                        rank1_strength = card_strength(sequence[i][1][0])
                        rank2_strength = card_strength(sequence[i + 1][1][0])
                        if rank1_strength // 4 + 1 != rank2_strength // 4:
                            is_consecutive = False
                            break
                    
                    if is_consecutive:
                        # Flatten the pairs into a single list
                        cards_sequence = []
                        for _, pair_cards in sequence:
                            cards_sequence.extend(pair_cards)
                        consecutive_pairs_list.append(cards_sequence)
        
        return consecutive_pairs_list

    def _should_use_bomb(self, bot):
        """
        Determine if bot should use a bomb
        Strategy: Use bomb only when table has 2
        """
        from core.rules import card_strength
        
        # Don't use bomb on first play of round
        if not self.last_play:
            return False
        
        # Check if table has a 2
        has_two = any(card.rank == 2 or card.rank == 15 for card in self.last_play)
        
        # Only use bomb if table has 2
        if not has_two:
            return False
        
        # If we have few cards left, use bomb to try to win
        if len(bot.hand) <= 5:
            return True
        
        # Use bomb if we have a good bomb (four of a kind or long consecutive pairs)
        bombs = self._find_all_bombs(bot.hand)
        if not bombs:
            return False
        
        # Check if we have a strong bomb
        for bomb in bombs:
            bomb_type = get_play_type(bomb)
            if bomb_type == "quadruple":
                # Four of a kind is always good against 2
                return True
            elif bomb_type == "consecutive_pairs" and len(bomb) >= 8:  # 4 pairs or more
                return True
        
        return False

    
    def _find_all_pairs(self, hand):
        """Find all possible pairs in hand"""
        from core.rules import card_strength
        
        pairs = []
        rank_groups = defaultdict(list)
        
        for card in hand:
            rank_groups[card.rank].append(card)
        
        for cards in rank_groups.values():
            if len(cards) >= 2:
                # Sort by strength and take strongest two
                cards.sort(key=card_strength, reverse=True)
                pairs.append(cards[:2])
        
        return pairs

    def _find_all_triples(self, hand):
        """Find all possible triples in hand"""
        from core.rules import card_strength
        
        triples = []
        rank_groups = defaultdict(list)
        
        for card in hand:
            rank_groups[card.rank].append(card)
        
        for cards in rank_groups.values():
            if len(cards) >= 3:
                # Sort by strength and take strongest three
                cards.sort(key=card_strength, reverse=True)
                triples.append(cards[:3])
        
        return triples

    def _find_all_quadruples(self, hand):
        """Find all possible quadruples (four of a kind) in hand"""
        from core.rules import card_strength
        
        quadruples = []
        rank_groups = defaultdict(list)
        
        for card in hand:
            rank_groups[card.rank].append(card)
        
        for cards in rank_groups.values():
            if len(cards) >= 4:
                # Sort by strength and take strongest four
                cards.sort(key=card_strength, reverse=True)
                quadruples.append(cards[:4])
        
        return quadruples

    def get_valid_plays(self, player):
        """
        Get all valid plays for a player given current table state
        Useful for hint system or more advanced AI
        """
        from core.rules import card_strength
        
        valid_plays = []
        
        # If table is empty, any valid combination is allowed (including bombs)
        if not self.last_play:
            # Singles
            for card in player.hand:
                valid_plays.append([card])
            
            # Pairs
            pairs = self._find_all_pairs(player.hand)
            valid_plays.extend(pairs)
            
            # Triples
            triples = self._find_all_triples(player.hand)
            valid_plays.extend(triples)
            
            # Quadruples (four of a kind)
            quadruples = self._find_all_quadruples(player.hand)
            valid_plays.extend(quadruples)
            
            # Straights
            straights = self._find_all_straights(player.hand)
            valid_plays.extend(straights)
            
            # Consecutive pairs (3 or more pairs)
            consecutive_pairs = self._find_all_consecutive_pairs(player.hand)
            for pairs_seq in consecutive_pairs:
                if len(pairs_seq) >= 6:  # At least 3 pairs
                    valid_plays.append(pairs_seq)
            
            return valid_plays
        
        # Table has cards, must beat them
        table_type = get_play_type(self.last_play)
        
        # Bombs can beat anything
        bombs = self._find_all_bombs(player.hand)
        if bombs:
            valid_plays.extend(bombs)
        
        if table_type == "single":
            for card in player.hand:
                if beats([card], self.last_play):
                    valid_plays.append([card])
        
        elif table_type == "pair":
            pairs = self._find_all_pairs(player.hand)
            for pair in pairs:
                if beats(pair, self.last_play):
                    valid_plays.append(pair)
        
        elif table_type == "triple":
            triples = self._find_all_triples(player.hand)
            for triple in triples:
                if beats(triple, self.last_play):
                    valid_plays.append(triple)
        
        elif table_type == "quadruple":
            quadruples = self._find_all_quadruples(player.hand)
            for quadruple in quadruples:
                if beats(quadruple, self.last_play):
                    valid_plays.append(quadruple)
        
        elif table_type == "straight":
            straights = self._find_all_straights(player.hand)
            for straight in straights:
                if len(straight) == len(self.last_play) and beats(straight, self.last_play):
                    valid_plays.append(straight)
        
        elif table_type == "consecutive_pairs":
            consecutive_pairs = self._find_all_consecutive_pairs(player.hand)
            for pairs_seq in consecutive_pairs:
                if len(pairs_seq) == len(self.last_play) and beats(pairs_seq, self.last_play):
                    valid_plays.append(pairs_seq)
        
        return valid_plays

    # NEW METHODS FOR PLAY HISTORY TRACKING

    def _record_play(self, player, cards):
        """Record a play in the history"""
        from core.rules import get_play_type
        
        play_type = get_play_type(cards)
        
        # Check if this is a bomb
        is_bomb = False
        if play_type == "quadruple" or (play_type == "consecutive_pairs" and len(cards) >= 6):
            is_bomb = True
            self.bomb_used = True
        
        play_record = {
            'player': player.name,
            'player_index': self.get_player_index(player),
            'cards': cards.copy(),
            'play_type': play_type,
            'is_bomb': is_bomb,
            'timestamp': datetime.now(),
            'round': self.round_number,
            'play_number': self.total_plays + 1,
            'is_pass': False
        }
        self.play_history.append(play_record)
        self.total_plays += 1
        self.last_play = cards.copy()

    def _record_pass(self, player):
        """Record a pass in the history"""
        pass_record = {
            'player': player.name,
            'player_index': self.get_player_index(player),
            'cards': [],
            'play_type': 'pass',
            'is_bomb': False,
            'timestamp': datetime.now(),
            'round': self.round_number,
            'play_number': self.total_plays + 1,
            'is_pass': True
        }
        self.play_history.append(pass_record)
        self.total_plays += 1

    def get_recent_plays(self, count=5, current_round_only=True):
        """
        Get recent plays, optionally filtered to current round only
        """
        if not self.play_history:
            return []
        
        if current_round_only:
            # Get plays from current round only
            recent_plays = [play for play in self.play_history 
                          if play['round'] == self.round_number]
        else:
            # Get all plays
            recent_plays = self.play_history
        
        # Return the most recent plays
        return recent_plays[-count:]

    def get_current_round_plays(self):
        """Get all plays in the current round"""
        return [play for play in self.play_history 
                if play['round'] == self.round_number]

    def get_round_winner(self):
        """Get the player who won the current round (last player to play before reset)"""
        current_round_plays = self.get_current_round_plays()
        if not current_round_plays:
            return None
        
        # Find the last non-pass play in current round
        for play in reversed(current_round_plays):
            if not play['is_pass']:
                return self.players[play['player_index']]
        return None

    def start_new_round(self, starting_player_index):
        """Start a new round with specified player"""
        self.last_play = []
        self.pass_count = 0
        self.bomb_used = False  # Reset bomb flag
        self.round_number += 1

    # EXISTING METHODS (updated for play history)

    def is_game_over(self):
        """Check if game is over (any player has won)"""
        return any(player.has_won() for player in self.players)

    def get_winner(self):
        """Get the winning player if game is over"""
        for player in self.players:
            if player.has_won():
                return player
        return None

    def reset_round(self):
        """Reset for a new round after everyone passes"""
        self.last_play = []
        self.pass_count = 0
        self.bomb_used = False  # Reset bomb flag
        # Don't clear history - we want to keep it for display

    def get_player_by_name(self, name):
        """Get player object by name"""
        for player in self.players:
            if player.name == name:
                return player
        return None

    def get_player_index(self, player):
        """Get index of player in players list"""
        try:
            return self.players.index(player)
        except ValueError:
            return -1

    def get_next_player(self, current_player):
        """Get next player in turn order"""
        current_index = self.get_player_index(current_player)
        if current_index == -1:
            return None
        next_index = (current_index + 1) % len(self.players)
        return self.players[next_index]

    def get_previous_player(self, current_player):
        """Get previous player in turn order"""
        current_index = self.get_player_index(current_player)
        if current_index == -1:
            return None
        prev_index = (current_index - 1) % len(self.players)
        return self.players[prev_index]

    def get_player_stats(self):
        """Get statistics for all players"""
        stats = {}
        for player in self.players:
            stats[player.name] = {
                'cards_remaining': len(player.hand),
                'has_won': player.has_won(),
                'plays_made': len([p for p in self.play_history 
                                 if p['player'] == player.name and not p['is_pass']]),
                'passes_made': len([p for p in self.play_history 
                                  if p['player'] == player.name and p['is_pass']]),
                'bombs_used': len([p for p in self.play_history 
                                 if p['player'] == player.name and p.get('is_bomb', False)])
            }
        return stats

    def get_game_summary(self):
        """Get a summary of the game state"""
        from core.rules import get_play_type
        
        return {
            'round': self.round_number,
            'total_plays': self.total_plays,
            'current_player_cards': len(self.players[0].hand),
            'players_remaining': len([p for p in self.players if not p.has_won()]),
            'last_play_type': get_play_type(self.last_play) if self.last_play else 'None',
            'consecutive_passes': self.pass_count,
            'is_new_round': len(self.last_play) == 0,
            'bomb_used_this_round': self.bomb_used
        }

    def get_play_string(self, play_record):
        """Convert a play record to a readable string"""
        if play_record['is_pass']:
            return f"{play_record['player']} passed"
        
        cards_str = ' '.join(str(card) for card in play_record['cards'])
        bomb_indicator = " 💣" if play_record.get('is_bomb', False) else ""
        return f"{play_record['player']} played {cards_str} ({play_record['play_type']}{bomb_indicator})"

    def print_play_history(self, current_round_only=True):
        """Print play history to console (for debugging)"""
        plays = self.get_current_round_plays() if current_round_only else self.play_history
        
        print(f"\n{'='*50}")
        print(f"PLAY HISTORY (Round {self.round_number})")
        print(f"{'='*50}")
        
        if not plays:
            print("No plays recorded yet.")
            return
        
        for i, play in enumerate(plays):
            play_str = self.get_play_string(play)
            print(f"{i+1:3d}. {play_str}")
        
        print(f"{'='*50}")
        print(f"Total plays: {len(plays)}")
        print(f"Bombs used this round: {sum(1 for p in plays if p.get('is_bomb', False))}")
        print(f"{'='*50}")

    # For compatibility with existing main.py
    def __str__(self):
        """String representation of game state"""
        summary = self.get_game_summary()
        return (f"Game: Round {summary['round']}, "
                f"Plays: {summary['total_plays']}, "
                f"Passes: {summary['consecutive_passes']}, "
                f"Bomb used: {summary['bomb_used_this_round']}")

# Helper function for card strength (needed in this file)
def card_strength(card):
    from core.rules import card_strength as get_strength
    return get_strength(card)