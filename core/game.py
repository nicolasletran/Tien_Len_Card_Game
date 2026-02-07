# core/game.py - COMPLETE CORRECTED VERSION WITH AUTO WINS
# Proper round sequencing: Round 1 = 3♠ rule, Round 2+ = Round winner starts
# Bombs only beat plays containing 2
# Automatic win rules: 4x2s, 6 pairs, 5 consecutive pairs, 4x3s (first round only)

from core.deck import Deck
from core.player import Player
from core.rules import is_valid_play, beats, get_play_type, is_single, is_pair, is_triple, is_straight
import random
from collections import defaultdict
from datetime import datetime

class Game:
    def __init__(self, is_fresh_game=True, previous_winner_index=None, previous_winner_name=None):
        """
        Initialize a new game with proper winner tracking
        
        Parameters:
        - is_fresh_game: True for brand new game (page refresh), False for restart button
        - previous_winner_index: Index of previous game winner (for restarts across sessions)
        - previous_winner_name: Name of previous game winner (for restarts)
        """
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
        self.play_history = []    # Track all plays in current round
        self.total_plays = 0      # Total plays in game
        self.bomb_used = False    # Track if a bomb has been used this round
        
        # Track round winner and starter
        self.round_winner = None           # Who won the current round
        self.first_player_index = None     # Who starts the current round
        self.current_player_index = None   # Whose turn it is currently
        
        # Track game winner (for restarts)
        self.game_winner_index = None
        self.game_winner_name = None
        
        # Handle fresh game vs restart differently
        if is_fresh_game:
            # Fresh game (page refresh): Start at Round 1 with 3♠ rule
            self.round_number = 1
            self._initialize_first_round()
            print(f"🎮 FRESH GAME: Round {self.round_number}, {self.players[self.first_player_index].name} has 3♠")
        else:
            # Restart button: Start at Round 2 with previous winner starting
            self.round_number = 2
            
            # Determine who starts based on previous winner
            self._initialize_restart_game(previous_winner_index, previous_winner_name)
        
        # Initialize current player to the starter
        self.current_player_index = self.first_player_index

    def _initialize_first_round(self):
        """Initialize first round - find player with 3♠ for fresh games only"""
        self.first_player_index = self._find_three_of_spades()
        print(f"🏁 ROUND 1 (3♠ rule): {self.players[self.first_player_index].name} has 3♠ and starts!")
        
        # No round winner for first round yet
        self.round_winner = None

    def _initialize_restart_game(self, previous_winner_index, previous_winner_name):
        """
        Initialize a restarted game with proper winner tracking
        
        Priority:
        1. Use previous_winner_index if valid
        2. Use previous_winner_name to find player
        3. Use human player (index 0) as default
        4. Fallback to random player
        """
        # Try to find previous winner by index
        if previous_winner_index is not None and 0 <= previous_winner_index < len(self.players):
            self.first_player_index = previous_winner_index
            print(f"🔄 RESTARTED GAME: Round {self.round_number}, {self.players[self.first_player_index].name} starts (previous winner by index)")
        
        # Try to find by name
        elif previous_winner_name:
            # Find player with matching name
            for i, player in enumerate(self.players):
                if player.name == previous_winner_name:
                    self.first_player_index = i
                    print(f"🔄 RESTARTED GAME: Round {self.round_number}, {self.players[self.first_player_index].name} starts (previous winner by name)")
                    break
            
            if self.first_player_index is None:
                # Name not found, default to human
                self.first_player_index = 0
                print(f"🔄 RESTARTED GAME: Round {self.round_number}, {self.players[self.first_player_index].name} starts (default, name not found)")
        
        else:
            # No winner info, default to human player
            self.first_player_index = 0
            print(f"🔄 RESTARTED GAME: Round {self.round_number}, {self.players[self.first_player_index].name} starts (default, no winner info)")
        
        # Set as round winner
        self.round_winner = self.players[self.first_player_index]

    def _find_three_of_spades(self):
        """Find which player has 3♠, return their index, or 0 if not found"""
        for i, player in enumerate(self.players):
            for card in player.hand:
                if card.rank == 3 and card.suit == "♠":
                    print(f"🔍 Found 3♠ with player {player.name} (index {i})")
                    return i
        print("⚠️ Warning: No one has 3♠! Defaulting to player 0")
        return 0

    def is_first_play_of_game(self):
        """Check if this is the very first play of a FRESH game"""
        return self.round_number == 1 and len(self.last_play) == 0 and self.pass_count == 0

    def is_first_play_of_round(self):
        """Check if this is the first play of the current round"""
        return len(self.last_play) == 0 and self.pass_count == 0

    def validate_first_play(self, cards, player_index):
        """
        Validate first play of round/game according to Tiến Lên rules
        Returns: (is_valid, error_message)
        """
        # Basic validation
        if not cards:
            return False, "No cards selected"
        
        if not is_valid_play(cards):
            return False, "Invalid card combination"
        
        # Check if this is the first play of a FRESH GAME (round 1)
        if self.is_first_play_of_game():
            # Player must have 3♠ and must include it in their play
            if player_index != self.first_player_index:
                return False, f"Only player with 3♠ can start the game. {self.players[self.first_player_index].name} has 3♠."
            
            # Check if play contains 3♠
            has_three_spades = any(card.rank == 3 and card.suit == "♠" for card in cards)
            if not has_three_spades:
                return False, "First play of the game must include 3♠"
            
            return True, "Valid first play of fresh game"
        
        # Check if this is first play of a NEW ROUND (round 2+)
        elif self.is_first_play_of_round():
            # For round 2+, player must be the round winner or first player
            if player_index != self.current_player_index:
                return False, f"Only {self.players[self.current_player_index].name} can start this round"
            
            # In rounds after round 1, any valid combination is OK (no 3♠ required)
            return True, "Valid first play of round"
        
        # Not a first play - normal validation
        return True, "Valid play"

    def play_cards(self, player_index, cards):
        """
        Attempt to play cards for a player
        Returns: (success, message)
        """
        player = self.players[player_index]
        
        # ===== AUTOMATIC WIN CHECK =====
        auto_winner, reason = self.check_automatic_wins()
        if auto_winner:
            if auto_winner != player:
                return False, f"Cannot play - {auto_winner.name} has an automatic winning hand!"
            # If the current player has auto-win, they just win immediately
            message = self._declare_automatic_winner(player, reason)
            return True, message
        # ===== END AUTOMATIC WIN CHECK =====
        
        # Check if game is over
        if self.is_game_over():
            return False, "Game is already over"
        
        # Check if it's player's turn
        if player_index != self.current_player_index:
            return False, f"Not your turn. It's {self.players[self.current_player_index].name}'s turn"
        
        # Check if player has won
        if player.has_won():
            return False, f"{player.name} has already won"
        
        # Validate the play
        if self.is_first_play_of_round():
            is_valid, error_msg = self.validate_first_play(cards, player_index)
            if not is_valid:
                return False, error_msg
        else:
            # Normal play must beat the table
            if not beats(cards, self.last_play):
                return False, "Your play doesn't beat the table"
        
        # Remove cards from player's hand
        for card in cards:
            if card in player.hand:
                player.hand.remove(card)
            else:
                return False, f"Card {card} not in player's hand"
        
        # Record the play
        self._record_play(player, cards)
        
        # Reset pass count since someone played
        self.pass_count = 0
        
        # Check if player won
        if player.has_won():
            self.round_winner = player
            # Also track as game winner
            self.game_winner_index = player_index
            self.game_winner_name = player.name
            print(f"🎉 {player.name} has won the game!")
        
        # Advance to next player
        self._advance_turn()
        
        return True, f"{player.name} played {' '.join(str(c) for c in cards)}"

    def pass_turn(self, player_index):
        """
        Player passes their turn
        Returns: (success, message)
        """
        player = self.players[player_index]
        
        # ===== AUTOMATIC WIN CHECK =====
        auto_winner, reason = self.check_automatic_wins()
        if auto_winner:
            if auto_winner != player:
                return False, f"Cannot pass - {auto_winner.name} has an automatic winning hand!"
            # If the current player has auto-win, they win
            message = self._declare_automatic_winner(player, reason)
            return True, message
        # ===== END AUTOMATIC WIN CHECK =====
        
        # Check if game is over
        if self.is_game_over():
            return False, "Game is already over"
        
        # Check if it's player's turn
        if player_index != self.current_player_index:
            return False, f"Not your turn. It's {self.players[self.current_player_index].name}'s turn"
        
        # Record pass
        self._record_pass(player)
        
        # Increment pass count
        self.pass_count += 1
        
        # Check if round should end (everyone passed except last player)
        active_players = len([p for p in self.players if not p.has_won()])
        if self.pass_count >= active_players - 1:
            print(f"🔄 All players passed. Round {self.round_number} ended!")
            
            # Round ended - set round winner to last player who played
            if self.last_play:
                # Find who played last
                current_round_plays = self.get_current_round_plays()
                non_pass_plays = [p for p in current_round_plays if not p['is_pass']]
                if non_pass_plays:
                    last_play = non_pass_plays[-1]
                    winner_index = last_play['player_index']
                    self.round_winner = self.players[winner_index]
                    print(f"   Round winner: {self.round_winner.name}")
            
            # Start new round
            self.start_new_round()
        else:
            # Advance to next player
            self._advance_turn()
        
        return True, f"{player.name} passed"

    def _advance_turn(self):
        """Advance to next player's turn, skipping players who have won"""
        if self.is_game_over():
            return
        
        max_attempts = len(self.players) * 2  # Prevent infinite loop
        attempts = 0
        
        while attempts < max_attempts:
            # Move to next player
            self.current_player_index = (self.current_player_index + 1) % len(self.players)
            player = self.players[self.current_player_index]
            
            # Check if this player hasn't won
            if not player.has_won():
                return
            
            attempts += 1
        
        # If all players have won (shouldn't happen), set to first player
        self.current_player_index = self.first_player_index if self.first_player_index is not None else 0

    def start_new_round(self, starting_player=None):
        """Start a new round with round winner starting"""
        print(f"\n{'='*60}")
        print(f"🏁 STARTING NEW ROUND {self.round_number + 1}")
        print(f"{'='*60}")
        
        # Clear table
        self.last_play = []
        self.pass_count = 0
        self.bomb_used = False
        
        # DETERMINE WHO STARTS THIS ROUND - FIXED LOGIC
        if starting_player is not None:
            # Specific player requested to start
            self.first_player_index = self.get_player_index(starting_player)
            print(f"Round started by request: {starting_player.name}")
        elif self.round_winner is not None and not self.round_winner.has_won():
            # Winner of last round starts, if they haven't won the game
            self.first_player_index = self.get_player_index(self.round_winner)
            print(f"🏆 {self.round_winner.name} won round {self.round_number} and starts round {self.round_number + 1}")
        else:
            # Find last non-pass play to determine round winner
            current_round_plays = self.get_current_round_plays()
            for play in reversed(current_round_plays):
                if not play.get('is_pass', False):
                    winner_index = play.get('player_index')
                    if 0 <= winner_index < len(self.players) and not self.players[winner_index].has_won():
                        self.round_winner = self.players[winner_index]
                        self.first_player_index = winner_index
                        print(f"🏆 {self.round_winner.name} won round {self.round_number} and starts round {self.round_number + 1}")
                        break
            
            # If still no winner, find first available player
            if self.first_player_index is None:
                available_players = [i for i, p in enumerate(self.players) if not p.has_won()]
                if available_players:
                    self.first_player_index = available_players[0]
                    self.round_winner = self.players[self.first_player_index]
                    print(f"🎲 First available player starts: {self.players[self.first_player_index].name}")
                else:
                    self.first_player_index = 0
                    print(f"⚠️ All players have won, defaulting to player 0")
        
        # Set current player to the starter
        self.current_player_index = self.first_player_index
        
        # Increment round number
        self.round_number += 1
        
        # Reset player pass status
        for player in self.players:
            player.reset_round()
        
        print(f"Round {self.round_number} started. {self.players[self.first_player_index].name} goes first.")
        print(f"{'='*60}\n")

    def bot_turn(self, bot):
        """
        CORRECTED bot AI with automatic win checking
        """
        # ===== AUTOMATIC WIN CHECK =====
        auto_winner, reason = self.check_automatic_wins()
        if auto_winner:
            if auto_winner == bot:
                # Bot has automatic win
                message = self._declare_automatic_winner(bot, reason)
                print(f"🤖 {message}")
                return None
            else:
                # Someone else has automatic win, bot should pass
                self.pass_turn(self.get_player_index(bot))
                return None
        # ===== END AUTOMATIC WIN CHECK =====
        
        bot_index = self.get_player_index(bot)
        
        if not bot.hand:
            return None
        
        # Sort bot's hand for consistent selection
        bot.sort_hand()
        
        # Check if this is first play of round
        is_first_play = self.is_first_play_of_round()
        
        # If table is empty and this bot starts the round
        if is_first_play and bot_index == self.current_player_index:
            print(f"🤖 {bot.name} starts round {self.round_number}")
            
            # Check if this is first play of FRESH GAME (round 1)
            if self.is_first_play_of_game():
                print(f"🤖 First play of FRESH GAME (Round 1) - must include 3♠")
                # First play of fresh game - must include 3♠
                play = self._play_with_three_spades(bot)
            else:
                print(f"🤖 First play of ROUND {self.round_number} - any valid combination")
                # First play of round (round 2+) - any valid combination
                play = self._play_best_first_combination(bot)
            
            if play:
                # Use the new play_cards method to handle everything
                success, message = self.play_cards(bot_index, play)
                if success:
                    print(f"🤖 {message}")
                    return play
                else:
                    print(f"🤖 Bot play failed: {message}")
                    # Bot should pass if it can't make a valid first play
                    self.pass_turn(bot_index)
                    return None
            else:
                # Bot can't make a valid first play - should pass
                self.pass_turn(bot_index)
                return None
        
        # Normal turn - try to beat the table
        table_type = get_play_type(self.last_play) if self.last_play else None
        
        # Check if table contains 2 - bombs can only be used against 2
        table_has_two = any(card.rank == 2 for card in self.last_play) if self.last_play else False
        
        # Try to find a combination that beats the table
        play = self._find_beating_play(bot, table_type, table_has_two)
        
        if play:
            success, message = self.play_cards(bot_index, play)
            if success:
                print(f"🤖 {message}")
                return play
            else:
                print(f"🤖 Bot play failed: {message}")
        
        # Bot passes
        self.pass_turn(bot_index)
        return None

    # ===== AUTOMATIC WIN METHODS =====
    
    def check_automatic_wins(self):
        """Check if any player has an automatic winning hand"""
        from core.rules import check_automatic_win
        
        for player in self.players:
            if not player.has_won() and len(player.hand) > 0:
                has_auto_win, reason = check_automatic_win(player.hand, self.round_number)
                if has_auto_win:
                    # Player automatically wins!
                    print(f"🎉 AUTOMATIC WIN! {player.name} {reason}!")
                    return player, reason
        return None, ""

    def _declare_automatic_winner(self, player, reason):
        """Declare a player as automatic winner"""
        print(f"🎉 {player.name} wins automatically! ({reason})")
        
        # Clear their hand to mark as winner
        player.hand.clear()
        
        # Update winner tracking
        self.round_winner = player
        self.game_winner_index = self.get_player_index(player)
        self.game_winner_name = player.name
        
        return f"{player.name} wins automatically with {reason}!"

    # ===== BOT PLAY HELPER METHODS =====
    
    def _play_with_three_spades(self, bot):
        """Find a valid combination that includes 3♠ for bot's first play of FRESH GAME"""
        hand = bot.hand.copy()
        
        # Find 3♠
        three_spades = None
        for card in hand:
            if card.rank == 3 and card.suit == "♠":
                three_spades = card
                break
        
        if not three_spades:
            print(f"🤖 ERROR: {bot.name} should have 3♠ but doesn't!")
            return None
        
        print(f"🤖 {bot.name} has 3♠ and must include it in first play of fresh game")
        
        # Try different combinations with 3♠:
        # 1. Single 3♠ (always valid)
        return [three_spades]

    def _play_best_first_combination(self, bot):
        """Play the best combination when starting a new round (round 2+)"""
        hand = bot.hand.copy()
        
        if not hand:
            return None
        
        # For rounds after round 1, any valid combination is OK
        
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

    def _find_beating_play(self, bot, table_type, table_has_two):
        """
        Find a play that beats the current table combination
        BOMBS CAN ONLY BE USED AGAINST PLAYS CONTAINING 2
        """
        hand = bot.hand.copy()
        
        # CRITICAL FIX: Bombs can only be used against plays containing 2
        if table_has_two:
            # Table contains 2 - check if bot has bombs and should use them
            bombs = self._find_all_bombs(hand)
            if bombs and self._should_use_bomb(bot):
                # Use the smallest appropriate bomb
                for bomb in sorted(bombs, key=lambda b: max(card_strength(card) for card in b)):
                    if beats(bomb, self.last_play):
                        print(f"🤖 {bot.name} using bomb on 2 play")
                        return bomb
        
        # Normal play logic for all other cases (no 2 on table)
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
            # Only if table contains 2 (handled above) or we need a higher quadruple
            if not table_has_two:
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
            # Check if table has 2 (bomb case already handled)
            if not table_has_two:
                consecutive_pairs_plays = self._find_all_consecutive_pairs(hand)
                table_pairs = self.last_play
                
                for pairs in consecutive_pairs_plays:
                    if len(pairs) == len(table_pairs) and beats(pairs, table_pairs):
                        return pairs
        
        return None

    # ===== HELPER METHODS FOR FINDING COMBINATIONS =====
    
    def _find_all_straights(self, hand):
        """Find all possible straights in hand"""
        if len(hand) < 3:
            return []
        
        # Sort by card strength
        sorted_hand = sorted(hand, key=lambda c: card_strength(c))
        
        straights = []
        
        # Check for straights starting from each card
        for i in range(len(sorted_hand)):
            current_straight = [sorted_hand[i]]
            
            for j in range(i + 1, len(sorted_hand)):
                next_card = sorted_hand[j]
                
                # Check if this card continues the straight
                last_rank_val = card_strength(current_straight[-1]) // 4
                next_rank_val = card_strength(next_card) // 4
                
                # 2 cannot be in straight (rank value 12)
                if last_rank_val == 12 or next_rank_val == 12:
                    continue
                
                if next_rank_val == last_rank_val + 1:
                    current_straight.append(next_card)
                elif next_rank_val > last_rank_val + 1:
                    # Gap too big, can't continue this straight
                    break
            
            if len(current_straight) >= 3:
                straights.append(current_straight)
        
        return straights
    
    def _find_all_bombs(self, hand):
        """Find all bombs (quadruples and consecutive pairs) in hand"""
        bombs = []
        
        # Find quadruples
        rank_groups = defaultdict(list)
        for card in hand:
            rank_groups[card.rank].append(card)
        
        for cards in rank_groups.values():
            if len(cards) >= 4:
                bombs.append(cards[:4])
        
        # Find consecutive pairs (minimum 3 pairs = 6 cards)
        pairs_list = []
        for rank, cards in rank_groups.items():
            if len(cards) >= 2:
                pairs_list.append((rank, cards[:2]))
        
        if len(pairs_list) >= 3:
            # Sort by rank
            pairs_list.sort(key=lambda x: card_strength(x[1][0]))
            
            # Find consecutive pairs
            for i in range(len(pairs_list) - 2):
                # Check if next 3 ranks are consecutive
                rank1_val = card_strength(pairs_list[i][1][0]) // 4
                rank2_val = card_strength(pairs_list[i+1][1][0]) // 4
                rank3_val = card_strength(pairs_list[i+2][1][0]) // 4
                
                # 2 cannot be in consecutive pairs
                if rank1_val == 12 or rank2_val == 12 or rank3_val == 12:
                    continue
                
                if rank2_val == rank1_val + 1 and rank3_val == rank2_val + 1:
                    bomb_cards = []
                    bomb_cards.extend(pairs_list[i][1])
                    bomb_cards.extend(pairs_list[i+1][1])
                    bomb_cards.extend(pairs_list[i+2][1])
                    bombs.append(bomb_cards)
        
        return bombs
    
    def _find_all_consecutive_pairs(self, hand):
        """Find all consecutive pairs combinations"""
        pairs_list = []
        rank_groups = defaultdict(list)
        
        for card in hand:
            rank_groups[card.rank].append(card)
        
        for cards in rank_groups.values():
            if len(cards) >= 2:
                pairs_list.append((cards[0].rank, cards[:2]))
        
        if len(pairs_list) < 3:
            return []
        
        # Sort by rank
        pairs_list.sort(key=lambda x: card_strength(x[1][0]))
        
        consecutive_pairs = []
        
        # Find all possible consecutive pairs combinations
        for start in range(len(pairs_list) - 2):
            for end in range(start + 3, len(pairs_list) + 1):
                # Check if all ranks in this range are consecutive
                is_consecutive = True
                for i in range(start, end - 1):
                    rank1_val = card_strength(pairs_list[i][1][0]) // 4
                    rank2_val = card_strength(pairs_list[i+1][1][0]) // 4
                    
                    # 2 cannot be in consecutive pairs
                    if rank1_val == 12 or rank2_val == 12:
                        is_consecutive = False
                        break
                    
                    if rank2_val != rank1_val + 1:
                        is_consecutive = False
                        break
                
                if is_consecutive:
                    # Create the combination
                    combination = []
                    for i in range(start, end):
                        combination.extend(pairs_list[i][1])
                    consecutive_pairs.append(combination)
        
        return consecutive_pairs
    
    def _should_use_bomb(self, bot):
        """
        Determine if bot should use a bomb
        Bots should be conservative with bombs - only use when necessary
        """
        # If bot has few cards left, be more aggressive with bombs
        if len(bot.hand) <= 3:
            return True
        
        # If bot has many cards, save bombs for later
        if len(bot.hand) >= 10:
            return random.random() < 0.4  # 40% chance to use bomb
        
        # Check if many players are still in the round
        active_players = sum(1 for p in self.players if not p.has_won())
        if active_players > 2:
            # Save bomb for later when fewer players remain
            return random.random() < 0.3  # 30% chance to use bomb
        
        # Default: use bomb
        return True
    
    def _find_all_pairs(self, hand):
        """Find all pairs in hand"""
        pairs = []
        rank_groups = defaultdict(list)
        
        for card in hand:
            rank_groups[card.rank].append(card)
        
        for cards in rank_groups.values():
            if len(cards) >= 2:
                pairs.append(cards[:2])
        
        return pairs
    
    def _find_all_triples(self, hand):
        """Find all triples in hand"""
        triples = []
        rank_groups = defaultdict(list)
        
        for card in hand:
            rank_groups[card.rank].append(card)
        
        for cards in rank_groups.values():
            if len(cards) >= 3:
                triples.append(cards[:3])
        
        return triples
    
    def _find_all_quadruples(self, hand):
        """Find all quadruples in hand"""
        quadruples = []
        rank_groups = defaultdict(list)
        
        for card in hand:
            rank_groups[card.rank].append(card)
        
        for cards in rank_groups.values():
            if len(cards) >= 4:
                quadruples.append(cards[:4])
        
        return quadruples
    
    def get_valid_plays(self, player):
        """Get all valid plays for a player"""
        valid_plays = []
        hand = player.hand.copy()
        
        if not hand:
            return valid_plays
        
        # Check if it's first play of round
        if self.is_first_play_of_round():
            # Must start with valid combination
            # Check all possible combinations
            from itertools import combinations
            
            # Check singles
            for card in hand:
                if is_valid_play([card]):
                    valid_plays.append([card])
            
            # Check pairs, triples, etc.
            for r in range(2, min(5, len(hand) + 1)):
                for combo in combinations(hand, r):
                    combo_list = list(combo)
                    if is_valid_play(combo_list):
                        valid_plays.append(combo_list)
            
            # Check straights (3+ cards)
            straights = self._find_all_straights(hand)
            valid_plays.extend(straights)
            
            # Check consecutive pairs
            consecutive_pairs = self._find_all_consecutive_pairs(hand)
            valid_plays.extend(consecutive_pairs)
        else:
            # Must beat last play
            for play in self.get_valid_plays(player):  # Recursive but with empty table
                if beats(play, self.last_play):
                    valid_plays.append(play)
        
        return valid_plays
    
    # ===== PLAY HISTORY TRACKING =====
    
    def _record_play(self, player, cards):
        """Record a play in the history"""
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
    
    # ===== GAME STATE METHODS =====
    
    def is_game_over(self):
        """Check if game is over (any player has won)"""
        return any(player.has_won() for player in self.players)
    
    def get_winner(self):
        """Get the winning player if game is over"""
        for player in self.players:
            if player.has_won():
                return player
        return None
    
    def get_game_winner_info(self):
        """Get game winner information for restarts"""
        winner = self.get_winner()
        if winner:
            return {
                'index': self.get_player_index(winner),
                'name': winner.name
            }
        return None
    
    def reset_round(self):
        """Reset for a new round after everyone passes"""
        self.last_play = []
        self.pass_count = 0
        self.bomb_used = False
        
        # Set round winner if there was a last play
        current_round_plays = self.get_current_round_plays()
        non_pass_plays = [p for p in current_round_plays if not p['is_pass']]
        if non_pass_plays:
            last_play = non_pass_plays[-1]
            winner_index = last_play['player_index']
            self.round_winner = self.players[winner_index]
    
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
        # Check for automatic win
        auto_winner, reason = self.check_automatic_wins()
        
        return {
            'round': self.round_number,
            'total_plays': self.total_plays,
            'current_player_cards': len(self.players[0].hand),
            'players_remaining': len([p for p in self.players if not p.has_won()]),
            'last_play_type': get_play_type(self.last_play) if self.last_play else 'None',
            'consecutive_passes': self.pass_count,
            'is_new_round': len(self.last_play) == 0,
            'bomb_used_this_round': self.bomb_used,
            'first_player_index': self.first_player_index,
            'current_player_index': self.current_player_index,
            'is_first_play_of_game': self.is_first_play_of_game(),
            'is_first_play_of_round': self.is_first_play_of_round(),
            'three_spades_player': self.players[self.first_player_index].name if self.round_number == 1 and self.first_player_index is not None else None,
            'game_winner': self.game_winner_name if self.game_winner_name else None,
            'game_winner_index': self.game_winner_index if self.game_winner_index is not None else None,
            # Auto win info
            'auto_winner': auto_winner.name if auto_winner else None,
            'auto_win_reason': reason if auto_winner else None
        }
    
    # ===== HISTORY METHODS =====
    
    def get_current_round_plays(self):
        """Get all plays in the current round"""
        return [play for play in self.play_history 
                if play['round'] == self.round_number]
    
    def get_recent_plays(self, count=5, current_round_only=True):
        """Get recent plays, optionally filtered to current round only"""
        if not self.play_history:
            return []
        
        if current_round_only:
            recent_plays = [play for play in self.play_history 
                          if play['round'] == self.round_number]
        else:
            recent_plays = self.play_history
        
        return recent_plays[-count:]
    
    def get_round_winner(self):
        """Get the player who won the current round"""
        current_round_plays = self.get_current_round_plays()
        if not current_round_plays:
            return None
        
        for play in reversed(current_round_plays):
            if not play['is_pass']:
                return self.players[play['player_index']]
        return None
    
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
        print(f"Round winner: {self.round_winner.name if self.round_winner else 'None'}")
        print(f"Game winner: {self.game_winner_name if self.game_winner_name else 'None'}")
        print(f"First player next round: {self.players[self.first_player_index].name if self.first_player_index is not None else 'None'}")
        print(f"{'='*50}")

    def __str__(self):
        """String representation of game state"""
        summary = self.get_game_summary()
        three_spades_info = ""
        if self.round_number == 1:
            three_spades_holder = self._find_three_of_spades()
            three_spades_info = f", 3♠: {self.players[three_spades_holder].name}"
        
        return (f"Game: Round {summary['round']}, "
                f"Current Player: {self.players[self.current_player_index].name if self.current_player_index is not None else 'None'}, "
                f"First Player: {self.players[self.first_player_index].name if self.first_player_index is not None else 'None'}"
                f"{three_spades_info}")

# Helper function for card strength (needed in this file)
def card_strength(card):
    from core.rules import card_strength as get_strength
    return get_strength(card)