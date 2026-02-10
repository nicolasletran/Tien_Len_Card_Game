# web_app.py - UPDATED VERSION for correct restart behavior
from flask import Flask, render_template, request, session, jsonify
import os
import json
import random
import sys
import traceback
import time
from core.game import Game
from core.player import Player
from core.card import Card
from core.rules import beats, is_valid_play, get_play_type, card_strength

app = Flask(__name__)
app.secret_key = os.urandom(24)

# -----------------------------
# Global exception handler
# -----------------------------

def handle_exception(e):
    """Global exception handler to prevent server crashes"""
    print(f"💥 UNHANDLED EXCEPTION: {type(e).__name__}: {e}")
    traceback.print_exc()
    return jsonify({
        'success': False,
        'error': f'Server error: {str(e)}'
    }), 500

# Register the error handler
@app.errorhandler(Exception)
def handle_all_exceptions(e):
    return handle_exception(e)

# -----------------------------
# Helper functions
# -----------------------------

def serialize_card(card):
    """Convert Card object to dict"""
    return {
        'rank': card.rank,
        'suit': card.suit,
        'display': str(card)  # e.g., "3♠", "J♥", "2♦"
    }

def serialize_player(player):
    """Convert Player object to dict"""
    return {
        'name': player.name,
        'cards_remaining': len(player.hand),
        'has_won': player.has_won(),
        'is_human': player.is_human if hasattr(player, 'is_human') else False
    }

def serialize_game_state(game):
    """Return dictionary matching JS expected state"""
    if not game:
        return None
    
    # Get current player
    current_player = None
    if game.current_player_index is not None and game.current_player_index < len(game.players):
        current_player = game.players[game.current_player_index]
    
    # Determine if it's player's turn (player index 0)
    is_player_turn = (game.current_player_index == 0)
    
    # Find human player (first player)
    human_player = game.players[0] if game.players else None
    
    # Get recent plays for current round
    recent_plays = game.get_recent_plays(count=3, current_round_only=True) if hasattr(game, 'get_recent_plays') else []
    round_plays = []
    
    for play in recent_plays:
        if hasattr(play, 'get'):
            round_plays.append(game.get_play_string(play))
        else:
            # Handle as dict
            if play.get('is_pass'):
                round_plays.append(f"{play.get('player', 'Unknown')} passed")
            else:
                cards = play.get('cards', [])
                cards_str = ' '.join(str(c) for c in cards) if cards else ''
                round_plays.append(f"{play.get('player', 'Unknown')} played {cards_str}")
    
    # Get round winner
    round_winner = None
    if game.round_winner:
        round_winner = game.round_winner.name
    elif hasattr(game, 'get_round_winner'):
        winner_obj = game.get_round_winner()
        if winner_obj:
            round_winner = winner_obj.name
    
    # Check if 3♠ rule applies (only for round 1)
    three_spades_player = None
    if game.round_number == 1:
        # Find who has 3♠ for round 1
        for i, player in enumerate(game.players):
            for card in player.hand:
                if card.rank == 3 and card.suit == "♠":
                    three_spades_player = player.name
                    break
            if three_spades_player:
                break
    auto_winner_info = None
    if hasattr(game, 'check_automatic_wins'):
        auto_winner, reason = game.check_automatic_wins()
        if auto_winner:
            auto_winner_info = {
                'player': auto_winner.name,
                'reason': reason,
                'player_index': game.get_player_index(auto_winner)
            }
    
    return {
        'is_player_turn': is_player_turn,
        'current_player': current_player.name if current_player else None,
        'current_player_index': game.current_player_index,
        'first_player_index': game.first_player_index,
        'game_over': game.is_game_over(),
        'players': [serialize_player(p) for p in game.players],
        'player_hand': [serialize_card(c) for c in human_player.hand] if human_player else [],
        'last_play': serialize_last_play(game.last_play, game) if game.last_play else None,
        'round_plays': round_plays,
        'summary': {
            'round': game.round_number,
            'total_plays': game.total_plays if hasattr(game, 'total_plays') else 0,
            'current_player_cards': len(human_player.hand) if human_player else 0,
            'players_remaining': len([p for p in game.players if not p.has_won()]),
            'last_play_type': get_play_type(game.last_play) if game.last_play else 'None',
            'consecutive_passes': game.pass_count,
            'is_new_round': len(game.last_play) == 0,
            'bomb_used_this_round': game.bomb_used if hasattr(game, 'bomb_used') else False,
            'is_first_play_of_game': game.is_first_play_of_game() if hasattr(game, 'is_first_play_of_game') else False,
            'is_first_play_of_round': game.is_first_play_of_round() if hasattr(game, 'is_first_play_of_round') else False,
            'three_spades_player': three_spades_player,
            'auto_winner': auto_winner_info,
        },
        'winner': game.get_winner().name if game.get_winner() else None,
        'round_winner': round_winner,
        'rules_info': {
            'requires_three_spades': (game.round_number == 1 and len(game.last_play) == 0),
            'three_spades_player': three_spades_player,
            'can_start_round': (game.current_player_index == game.first_player_index)
        }
    }

def serialize_last_play(play_cards, game):
    """Convert last play to serializable format"""
    if not play_cards:
        return None
    
    play_type = get_play_type(play_cards) if play_cards else None
    
    # Find who played last
    player_name = "Unknown"
    if hasattr(game, 'play_history') and game.play_history:
        for play in reversed(game.play_history):
            if not play.get('is_pass', False):
                player_name = play.get('player', 'Unknown')
                break
    
    return {
        'player': player_name,
        'cards': [str(card) for card in play_cards],
        'play_type': play_type,
        'is_bomb': play_type in ["quadruple", "consecutive_pairs"] and len(play_cards) >= 4,
        'is_pass': False
    }

def card_str_to_card(card_str):
    """Convert card string (e.g., "3♠", "J♥") to Card object"""
    # Map rank symbols to numbers
    rank_map = {
        '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10,
        'J': 11, 'Q': 12, 'K': 13, 'A': 14, '2': 2
    }
    
    # Parse the card string
    # Find the suit (last character)
    suit = card_str[-1]
    
    # Get rank part (everything except last character)
    rank_str = card_str[:-1]
    
    # Convert rank string to int
    rank = rank_map.get(rank_str)
    if rank is None:
        # Try to parse numeric rank
        try:
            rank = int(rank_str)
        except ValueError:
            return None
    
    # Create and return Card object
    return Card(rank, suit)

def validate_card_input(card_strs):
    """Validate card strings from web client"""
    if not isinstance(card_strs, list):
        return False
    
    valid_suits = {'♠', '♣', '♦', '♥'}
    valid_ranks = {'3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A', '2'}
    
    for card_str in card_strs:
        if not isinstance(card_str, str) or len(card_str) < 2:
            return False
        
        suit = card_str[-1]
        rank = card_str[:-1]
        
        if suit not in valid_suits or rank not in valid_ranks:
            return False
    
    return True

# -----------------------------
# Game session management
# -----------------------------

class GameSession:
    """Manage game sessions in memory"""
    
    def __init__(self):
        self.sessions = {}  # session_id -> game_data
        self.session_timeouts = {}
        self.last_cleanup = time.time()
    
    def create_session(self, player_name="You", is_fresh_game=True):
        """Create a new game session"""
        session_id = os.urandom(16).hex()
        
        # Create new game with correct parameters
        # is_fresh_game=True for page refresh/first time
        # is_fresh_game=False for restart button
        game = Game(is_fresh_game=is_fresh_game)
        
        # Update human player name
        game.players[0].name = player_name
        
        # Store game data
        self.sessions[session_id] = {
            'game': game,
            'created_at': time.time(),
            'last_activity': time.time(),
            'player_name': player_name,
            'is_fresh_game': is_fresh_game  # Track if this was a fresh game
        }
        
        # Set cleanup timeout
        self.session_timeouts[session_id] = time.time() + 3600  # 1 hour timeout
        
        if is_fresh_game:
            print(f"🎮 Created FRESH game session {session_id[:8]}... for {player_name}")
            print(f"   Round: {game.round_number}, First player: {game.players[game.first_player_index].name}")
            if game.round_number == 1:
                print(f"   3♠ rule applies: {game.players[game.first_player_index].name} has 3♠")
        else:
            print(f"🔄 Created RESTARTED game session {session_id[:8]}... for {player_name}")
            print(f"   Round: {game.round_number}, First player: {game.players[game.first_player_index].name} (simulated round winner)")
            print(f"   No 3♠ rule for round {game.round_number}")
        
        return session_id
    
    def get_game(self, session_id):
        """Get game for session"""
        if session_id not in self.sessions:
            return None
        
        # Update activity timestamp
        self.sessions[session_id]['last_activity'] = time.time()
        self.session_timeouts[session_id] = time.time() + 3600
        
        return self.sessions[session_id]['game']
    
    def update_session(self, session_id, game):
        """Update game in session"""
        if session_id in self.sessions:
            self.sessions[session_id]['game'] = game
            self.sessions[session_id]['last_activity'] = time.time()
            self.session_timeouts[session_id] = time.time() + 3600
    
    def cleanup_old_sessions(self):
        """Remove inactive sessions"""
        current_time = time.time()
        
        # Only cleanup every 5 minutes
        if current_time - self.last_cleanup < 300:
            return
        
        sessions_to_remove = []
        for session_id, timeout in self.session_timeouts.items():
            if current_time > timeout:
                sessions_to_remove.append(session_id)
        
        for session_id in sessions_to_remove:
            if session_id in self.sessions:
                player_name = self.sessions[session_id]['player_name']
                print(f"🧹 Cleaning up inactive session {session_id[:8]}... for {player_name}")
                del self.sessions[session_id]
            if session_id in self.session_timeouts:
                del self.session_timeouts[session_id]
        
        self.last_cleanup = current_time
    
    def restart_session(self, session_id, player_name):
        """Restart game in existing session with is_fresh_game=False"""
        if session_id not in self.sessions:
            return self.create_session(player_name, is_fresh_game=False)
        
        # Create new RESTARTED game (is_fresh_game=False)
        game = Game(is_fresh_game=False)
        game.players[0].name = player_name
        
        # Update session
        self.sessions[session_id]['game'] = game
        self.sessions[session_id]['last_activity'] = time.time()
        self.sessions[session_id]['player_name'] = player_name
        self.sessions[session_id]['is_fresh_game'] = False
        self.session_timeouts[session_id] = time.time() + 3600
        
        print(f"🔄 Restarted session {session_id[:8]}... for {player_name}")
        print(f"   Round: {game.round_number}, First player: {game.players[game.first_player_index].name}")
        print(f"   No 3♠ rule for round {game.round_number}")
        
        return session_id

# Initialize game session manager
game_manager = GameSession()

# -----------------------------
# Routes
# -----------------------------

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/favicon.ico')
def favicon():
    """Handle favicon requests to prevent 404 errors"""
    return '', 404

# -----------------------------
# API Endpoints
# -----------------------------

@app.route('/api/start_game', methods=['POST'])
def api_start_game():
    try:
        data = request.get_json()
        player_name = data.get('player_name', 'You')
        
        # Clean up old sessions
        game_manager.cleanup_old_sessions()
        
        # Create a NEW FRESH GAME (page refresh or first time)
        # is_fresh_game=True for Round 1 with 3♠ rule
        session_id = game_manager.create_session(player_name, is_fresh_game=True)
        game = game_manager.get_game(session_id)
        
        # Store session ID in Flask session for convenience
        session['session_id'] = session_id
        
        print(f"✅ FRESH GAME started for {player_name}")
        print(f"   Session: {session_id[:8]}...")
        print(f"   Round: {game.round_number}")
        if game.round_number == 1:
            print(f"   3♠ rule active: {game.players[game.first_player_index].name} has 3♠")
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'game_id': session_id,
            'state': serialize_game_state(game),
            'message': f'Fresh game started! Round {game.round_number}. {game.players[game.first_player_index].name} starts first.' + 
                      (' 3♠ rule applies.' if game.round_number == 1 else ' Round winner starts.')
        })
        
    except Exception as e:
        print(f"❌ Error in start_game: {str(e)}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/get_state', methods=['GET'])
def api_get_state():
    try:
        session_id = request.args.get('session_id')
        if not session_id:
            # Try to get from session
            session_id = session.get('session_id')
        
        if not session_id:
            return jsonify({
                'success': False,
                'error': 'No session ID provided. Start a new game first.'
            })
        
        # Get game from session manager
        game = game_manager.get_game(session_id)
        if not game:
            return jsonify({
                'success': False,
                'error': 'Game session not found or expired. Start a new game.'
            })
        
        # Return game state
        return jsonify({
            'success': True,
            'state': serialize_game_state(game)
        })
        
    except Exception as e:
        print(f"❌ Error in get_state: {str(e)}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/play_cards', methods=['POST'])
def api_play_cards():
    try:
        data = request.get_json()
        card_strs = data.get('cards', [])
        session_id = data.get('session_id')
        
        if not session_id:
            return jsonify({
                'success': False,
                'error': 'No session ID provided'
            })
        
        # Validate input
        if not card_strs:
            return jsonify({
                'success': False,
                'error': 'No cards selected'
            })
        
        if not validate_card_input(card_strs):
            return jsonify({
                'success': False,
                'error': 'Invalid card format'
            })
        
        # Get game
        game = game_manager.get_game(session_id)
        if not game:
            return jsonify({
                'success': False,
                'error': 'Game session not found'
            })
        
        print(f"🎮 Player wants to play cards: {card_strs}")
        print(f"   Round: {game.round_number}")
        print(f"   Current player: {game.players[game.current_player_index].name}")
        print(f"   First player: {game.players[game.first_player_index].name}")
        print(f"   Is first play of game: {game.is_first_play_of_game()}")
        print(f"   Is first play of round: {game.is_first_play_of_round()}")
        
        # Check if game is over
        if game.is_game_over():
            return jsonify({
                'success': False,
                'error': 'Game is already over'
            })
        
        # Check if it's player's turn
        if game.current_player_index != 0:
            return jsonify({
                'success': False,
                'error': f"Not your turn. It's {game.players[game.current_player_index].name}'s turn"
            })
        
        # Convert card strings to Card objects
        play_cards = []
        for card_str in card_strs:
            card = card_str_to_card(card_str)
            if card:
                play_cards.append(card)
        
        if not play_cards:
            return jsonify({
                'success': False,
                'error': 'No valid cards selected'
            })
        
        # Check if player has these cards
        human_player = game.players[0]
        for card in play_cards:
            if card not in human_player.hand:
                return jsonify({
                    'success': False,
                    'error': f"Card {card} not in your hand"
                })
        
        print(f"✅ Valid cards found: {[str(c) for c in play_cards]}")
        
        # Use the play_cards method from Game class
        success, message = game.play_cards(0, play_cards)
        
        if success:
            print(f"✅ Play successful: {message}")
            
            # Update game in session manager
            game_manager.update_session(session_id, game)
            
            # Check if player won
            if human_player.has_won():
                message = f"🎉 {human_player.name} wins the game! 🎉"
                print(message)
            
            return jsonify({
                'success': True,
                'message': message,
                'state': serialize_game_state(game)
            })
        else:
            print(f"❌ Play failed: {message}")
            return jsonify({
                'success': False,
                'error': message,
                'state': serialize_game_state(game)
            })
        
    except Exception as e:
        print(f"❌ Error in play_cards: {str(e)}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/pass_turn', methods=['POST'])
def api_pass_turn():
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        
        if not session_id:
            return jsonify({
                'success': False,
                'error': 'No session ID provided'
            })
        
        # Get game
        game = game_manager.get_game(session_id)
        if not game:
            return jsonify({
                'success': False,
                'error': 'Game session not found'
            })
        
        print(f"🎮 Player wants to pass")
        print(f"   Round: {game.round_number}")
        print(f"   Current player: {game.players[game.current_player_index].name}")
        
        # Check if game is over
        if game.is_game_over():
            return jsonify({
                'success': False,
                'error': 'Game is already over'
            })
        
        # Check if it's player's turn
        if game.current_player_index != 0:
            return jsonify({
                'success': False,
                'error': f"Not your turn. It's {game.players[game.current_player_index].name}'s turn"
            })
        
        # Use the pass_turn method from Game class
        success, message = game.pass_turn(0)
        
        if success:
            print(f"✅ Pass successful: {message}")
            
            # Update game in session manager
            game_manager.update_session(session_id, game)
            
            # Check if round ended
            if game.pass_count == 0 and game.round_winner:
                print(f"🔄 Round ended. Winner: {game.round_winner.name}")
            
            return jsonify({
                'success': True,
                'message': message,
                'state': serialize_game_state(game)
            })
        else:
            print(f"❌ Pass failed: {message}")
            return jsonify({
                'success': False,
                'error': message,
                'state': serialize_game_state(game)
            })
        
    except Exception as e:
        print(f"❌ Error in pass_turn: {str(e)}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/bot_move', methods=['POST'])
def api_bot_move():
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        
        if not session_id:
            return jsonify({
                'success': False,
                'error': 'No session ID provided'
            })
        
        # Get game
        game = game_manager.get_game(session_id)
        if not game:
            return jsonify({
                'success': False,
                'error': 'Game session not found'
            })
        
        # Check if game is over
        if game.is_game_over():
            return jsonify({
                'success': False,
                'error': 'Game is already over',
                'state': serialize_game_state(game)
            })
        
        # Check if it's a bot's turn (indices 1, 2, 3 are bots)
        if game.current_player_index == 0:
            return jsonify({
                'success': False,
                'error': "Not bot's turn. It's player's turn.",
                'state': serialize_game_state(game)
            })
        
        bot = game.players[game.current_player_index]
        
        print(f"🤖 Processing bot move for {bot.name}")
        print(f"   Round: {game.round_number}")
        print(f"   Current player index: {game.current_player_index}")
        print(f"   Is first play of game: {game.is_first_play_of_game()}")
        print(f"   Is first play of round: {game.is_first_play_of_round()}")
        
        # Check if bot has already won
        if bot.has_won():
            print(f"🤖 {bot.name} has already won, skipping")
            # Advance turn anyway
            game._advance_turn()
            game_manager.update_session(session_id, game)
            return jsonify({
                'success': True,
                'message': f"{bot.name} has already won",
                'is_pass': False,
                'state': serialize_game_state(game)
            })
        
        # Let bot play using the updated bot_turn method
        bot_play = game.bot_turn(bot)
        
        if bot_play:
            message = f"{bot.name} played {' '.join(str(c) for c in bot_play)}"
            is_pass = False
            
            # Special message for 3♠ play (only in round 1)
            if game.round_number == 1 and game.is_first_play_of_game() and any(card.rank == 3 and card.suit == "♠" for card in bot_play):
                message = f"{bot.name} starts the game with {' '.join(str(c) for c in bot_play)} (includes 3♠)"
        else:
            message = f"{bot.name} passed"
            is_pass = True
        
        print(f"🤖 Bot move result: {message}")
        
        # Update game in session manager
        game_manager.update_session(session_id, game)
        
        # Check if game is over after bot move
        if game.is_game_over():
            winner = game.get_winner()
            if winner:
                message = f"{message}. 🎉 {winner.name} wins the game! 🎉"
        
        return jsonify({
            'success': True,
            'message': message,
            'is_pass': is_pass,
            'state': serialize_game_state(game)
        })
        
    except Exception as e:
        print(f"❌ Error in bot_move: {str(e)}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/restart_game', methods=['POST'])
def api_restart_game():
    try:
        data = request.get_json()
        player_name = data.get('player_name', 'You')
        
        # Get session ID from request or session
        session_id = data.get('session_id') or session.get('session_id')
        
        previous_winner_index = None
        previous_winner_name = None
        
        if session_id and session_id in game_manager.sessions:
            # Get previous game to find winner
            previous_game = game_manager.sessions[session_id]['game']
            if previous_game:
                winner_info = previous_game.get_game_winner_info()
                if winner_info:
                    previous_winner_index = winner_info.get('index')
                    previous_winner_name = winner_info.get('name')
        
        # Create new game with winner tracking
        game = Game(is_fresh_game=False, 
                   previous_winner_index=previous_winner_index,
                   previous_winner_name=previous_winner_name)
        game.players[0].name = player_name
        
        # Update session
        game_manager.sessions[session_id]['game'] = game
        game_manager.sessions[session_id]['last_activity'] = time.time()
        game_manager.sessions[session_id]['player_name'] = player_name
        game_manager.sessions[session_id]['is_fresh_game'] = False
        game_manager.session_timeouts[session_id] = time.time() + 3600
        
        print(f"🔄 Game restarted for {player_name}")
        if previous_winner_name:
            print(f"   Previous winner: {previous_winner_name} starts")
        
        return jsonify({
            'success': True,
            'message': 'Game restarted successfully',
            'session_id': session_id,
            'state': serialize_game_state(game)
        })
        
    except Exception as e:
        print(f"❌ Error in restart_game: {str(e)}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/get_valid_plays', methods=['GET'])
def api_get_valid_plays():
    try:
        session_id = request.args.get('session_id')
        if not session_id:
            return jsonify({
                'success': False,
                'error': 'No session ID provided'
            })
        
        game = game_manager.get_game(session_id)
        if not game:
            return jsonify({
                'success': False,
                'error': 'Game session not found'
            })
        
        human_player = game.players[0]
        
        # Check if it's player's turn
        if game.current_player_index != 0:
            return jsonify({
                'success': False,
                'error': 'Not your turn',
                'valid_plays': []
            })
        
        # Get valid plays using game logic
        valid_plays = []
        if hasattr(game, 'get_valid_plays'):
            valid_plays = game.get_valid_plays(human_player)
        else:
            # Simple fallback
            if game.last_play:
                for card in human_player.hand:
                    if beats([card], game.last_play):
                        valid_plays.append([card])
            else:
                # Any single card is valid
                for card in human_player.hand:
                    valid_plays.append([card])
        
        # Filter for first play requirements
        if game.is_first_play_of_round():
            # For first play of game (round 1), must include 3♠
            if game.is_first_play_of_game():
                filtered_plays = []
                for play in valid_plays:
                    if any(card.rank == 3 and card.suit == "♠" for card in play):
                        filtered_plays.append(play)
                valid_plays = filtered_plays
            # For first play of round (round 2+), any valid play is OK
        
        plays = []
        for play_cards in valid_plays[:15]:  # Limit to 15 suggestions
            play_type = get_play_type(play_cards) if play_cards else 'single'
            
            # Check if this play would be valid for current situation
            is_valid = True
            error_msg = ""
            
            if game.is_first_play_of_round():
                # Use the game's validation
                is_valid, error_msg = game.validate_first_play(play_cards, 0)
            elif game.last_play:
                # Must beat last play
                is_valid = beats(play_cards, game.last_play)
                if not is_valid:
                    error_msg = "Doesn't beat last play"
            
            plays.append({
                'cards': [str(c) for c in play_cards],
                'type': play_type,
                'count': len(play_cards),
                'is_valid': is_valid,
                'error': error_msg if not is_valid else ""
            })
        
        # Find who has 3♠ for round 1
        three_spades_player = None
        if game.round_number == 1:
            for player in game.players:
                for card in player.hand:
                    if card.rank == 3 and card.suit == "♠":
                        three_spades_player = player.name
                        break
                if three_spades_player:
                    break
        
        return jsonify({
            'success': True,
            'valid_plays': plays,
            'is_first_play_of_game': game.is_first_play_of_game(),
            'is_first_play_of_round': game.is_first_play_of_round(),
            'requires_three_spades': (game.round_number == 1 and len(game.last_play) == 0),
            'three_spades_player': three_spades_player
        })
        
    except Exception as e:
        print(f"❌ Error in get_valid_plays: {str(e)}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/get_game_info', methods=['GET'])
def api_get_game_info():
    """Get detailed game information"""
    try:
        session_id = request.args.get('session_id')
        if not session_id:
            return jsonify({
                'success': False,
                'error': 'No session ID provided'
            })
        
        game = game_manager.get_game(session_id)
        if not game:
            return jsonify({
                'success': False,
                'error': 'Game session not found'
            })
        
        # Get detailed info
        info = {
            'round': game.round_number,
            'current_player': game.players[game.current_player_index].name if game.current_player_index is not None else None,
            'first_player': game.players[game.first_player_index].name if game.first_player_index is not None else None,
            'is_first_play_of_game': game.is_first_play_of_game(),
            'is_first_play_of_round': game.is_first_play_of_round(),
            'requires_three_spades': (game.round_number == 1 and len(game.last_play) == 0),
            'three_spades_player': None,
            'players': []
        }
        
        # Find who has 3♠ for round 1
        if game.round_number == 1:
            for i, player in enumerate(game.players):
                for card in player.hand:
                    if card.rank == 3 and card.suit == "♠":
                        info['three_spades_player'] = player.name
                        break
                if info['three_spades_player']:
                    break
        
        for i, player in enumerate(game.players):
            player_info = {
                'name': player.name,
                'index': i,
                'cards_remaining': len(player.hand),
                'has_won': player.has_won(),
                'is_current': (i == game.current_player_index),
                'is_first': (i == game.first_player_index)
            }
            info['players'].append(player_info)
        
        return jsonify({
            'success': True,
            'info': info
        })
        
    except Exception as e:
        print(f"❌ Error in get_game_info: {str(e)}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# -----------------------------
# Error Handling
# -----------------------------

@app.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'success': False, 'error': 'Internal server error'}), 500

# -----------------------------
# Run app
# -----------------------------
if __name__ == '__main__':
    print("\n" + "="*60)
    print("🎮 TIEN LEN MIEN NAM SERVER - UPDATED VERSION")
    print("="*60)
    print("✅ Features:")
    print("   - Round 1: 3♠ rule applies (whoever has 3♠ starts)")
    print("   - Round 2+: Round winner starts (any valid play)")
    print("   - Restart button: Starts at Round 2 (no 3♠ rule)")
    print("   - Page refresh: Starts at Round 1 (3♠ rule applies)")
    print("   - Bombs only beat plays containing 2")
    print("="*60)
    print("🌐 Server running at: http://localhost:5000")
    print("📁 Make sure you have:")
    print("   - Updated game.py with correct round sequencing")
    print("   - cards.js in /static directory")
    print("   - index.html in /templates directory")
    print("   - All core game modules")
    print("="*60 + "\n")
    
    app.run(debug=True, port=5000, threaded=True)
    # Add this at the VERY BOTTOM of web_app.py
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)