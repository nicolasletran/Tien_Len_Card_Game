# web_app.py - FIXED VERSION (prevents server crashes)
from flask import Flask, render_template, request, session, jsonify
import os
import json
import random
import pickle
import base64
import sys
import traceback
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

def serialize_game_to_session(game):
    """Convert Game object to session-storable format"""
    if game is None:
        return None
    
    # Use pickle to serialize the game object
    game_bytes = pickle.dumps(game)
    # Encode to base64 for safe storage in session
    return base64.b64encode(game_bytes).decode('utf-8')

def deserialize_game_from_session(game_data):
    """Convert session data back to Game object"""
    if game_data is None:
        return None
    
    try:
        # Decode from base64 and unpickle
        game_bytes = base64.b64decode(game_data.encode('utf-8'))
        return pickle.loads(game_bytes)
    except:
        return None

def get_game():
    """Get current game from session"""
    if 'game_data' in session:
        return deserialize_game_from_session(session['game_data'])
    return None

def save_game(game):
    """Save game to session"""
    if game:
        session['game_data'] = serialize_game_to_session(game)

def serialize_card(card):
    """Convert Card object to dict"""
    # Handle the rank display (your Card class uses rank_symbol method)
    rank_str = card.rank_symbol()
    
    return {
        'rank': card.rank,  # Keep as int for game logic
        'suit': card.suit,
        'display': str(card)  # This uses rank_symbol() internally
    }

def serialize_game_state(game):
    """Return dictionary matching JS expected state"""
    if not game:
        return None
    
    # Get current player index
    current_player_index = session.get('current_player_index', 0)
    
    # Safety check - ensure index is valid
    if not game.players or current_player_index >= len(game.players):
        current_player_index = 0
        session['current_player_index'] = 0
    
    current_player = game.players[current_player_index] if game.players else None
    
    # Determine if it's player's turn (player index 0)
    is_player_turn = (current_player_index == 0)
    
    # Find human player (first player)
    human_player = game.players[0] if game.players else None
    
    return {
        'is_player_turn': is_player_turn,
        'current_player': current_player.name if current_player else None,
        'game_over': game.is_game_over(),
        'players': [
            {
                'name': p.name,
                'cards_remaining': len(p.hand),
                'has_won': p.has_won()
            } for p in game.players
        ],
        'player_hand': [serialize_card(c) for c in human_player.hand] if human_player else [],
        'last_play': serialize_play(game.last_play) if game.last_play else None,
        'round_plays': [],
        'summary': {
            'round': game.round_number,
            'current_player_cards': len(human_player.hand) if human_player else 0
        },
        'winner': game.get_winner().name if game.get_winner() else None
    }

def serialize_play(play_cards):
    """Convert play cards to serializable format"""
    if not play_cards:
        return None
    
    play_type = get_play_type(play_cards) if play_cards else None
    
    return {
        'player': 'Unknown',
        'cards': [str(card) for card in play_cards],
        'play_type': play_type,
        'is_bomb': play_type in ["quadruple", "consecutive_pairs"],
        'is_pass': False
    }

def advance_turn():
    """Advance to next player's turn, skipping players who have won"""
    if 'current_player_index' not in session:
        session['current_player_index'] = 0
    
    game = get_game()
    if not game:
        return False
    
    max_attempts = len(game.players) * 2  # Prevent infinite loop
    attempts = 0
    
    while attempts < max_attempts:
        # Move to next player
        session['current_player_index'] = (session['current_player_index'] + 1) % len(game.players)
        current_index = session['current_player_index']
        
        # Check if current player has won AND if game is still ongoing
        if not game.players[current_index].has_won() or game.is_game_over():
            # Found a player who hasn't won OR game is over
            save_game(game)
            return True
        
        attempts += 1
    
    # If all players have won (shouldn't happen), reset to player 0
    session['current_player_index'] = 0
    save_game(game)
    return True

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
        
        # Create a new game using your Game class
        game = Game()
        
        # Update the human player's name
        game.players[0].name = player_name
        
        # Initialize turn tracking
        session['current_player_index'] = 0  # Human starts
        
        # Save game to session
        save_game(game)
        
        print(f"Game started for {player_name}")
        print(f"Players: {[p.name for p in game.players]}")
        print(f"Human hand: {[str(c) for c in game.players[0].hand]}")
        print(f"Human hand size: {len(game.players[0].hand)}")
        
        return jsonify({
            'success': True,
            'session_id': id(game),
            'game_id': id(game),
            'state': serialize_game_state(game)
        })
        
    except Exception as e:
        print(f"Error in start_game: {str(e)}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/get_state', methods=['GET'])
def api_get_state():
    try:
        game = get_game()
        if not game:
            return jsonify({
                'success': False,
                'error': 'No game found. Start a new game first.'
            })
        
        # Update current player index
        if 'current_player_index' not in session:
            session['current_player_index'] = 0
        
        # Safety check - ensure index is valid
        if session['current_player_index'] >= len(game.players):
            session['current_player_index'] = 0
        
        return jsonify({
            'success': True,
            'state': serialize_game_state(game)
        })
        
    except Exception as e:
        print(f"Error in get_state: {str(e)}")
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
        game = get_game()
        
        if not game:
            return jsonify({
                'success': False,
                'error': 'No game found'
            })
        
        # Check if game is over
        if game.is_game_over():
            return jsonify({
                'success': False,
                'error': 'Game is already over'
            })
        
        # Check if it's player's turn
        if session.get('current_player_index', 0) != 0:
            return jsonify({
                'success': False,
                'error': 'Not your turn'
            })
        
        # Get human player (first player)
        human_player = game.players[0]
        
        # Convert card strings to Card objects
        play_cards = []
        for card_str in card_strs:
            # Parse the card string (e.g., "3♠", "J♥", "2♦")
            # Extract rank and suit
            if card_str.endswith('♠') or card_str.endswith('♣') or card_str.endswith('♦') or card_str.endswith('♥'):
                rank_part = card_str[:-1]
                suit = card_str[-1]
                
                # Convert rank string to int
                rank_map = {
                    '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10,
                    'J': 11, 'Q': 12, 'K': 13, 'A': 14, '2': 2
                }
                
                rank = rank_map.get(rank_part)
                if rank is None:
                    # Try to parse numeric rank
                    try:
                        rank = int(rank_part)
                    except ValueError:
                        continue
                
                # Find matching card in player's hand
                for card in human_player.hand:
                    if card.rank == rank and card.suit == suit:
                        play_cards.append(card)
                        break
        
        print(f"Player wants to play cards: {card_strs}")
        print(f"Found cards in hand: {[str(c) for c in play_cards]}")
        
        if not play_cards:
            # No valid cards selected, treat as pass
            game.pass_count += 1
            if game.pass_count >= 3:  # All players passed
                game.reset_round()
            
            # Advance turn
            advance_turn()
            
            message = f"{human_player.name} passed."
        else:
            # Check if play is valid
            if not is_valid_play(play_cards):
                return jsonify({
                    'success': False,
                    'error': 'Invalid card combination'
                })
            
            # Check if play beats last play
            if game.last_play and not beats(play_cards, game.last_play):
                return jsonify({
                    'success': False,
                    'error': 'Play does not beat last play'
                })
            
            # Remove cards from player's hand
            for card in play_cards:
                if card in human_player.hand:
                    human_player.hand.remove(card)
            
            # Record the play
            game.last_play = play_cards
            game.pass_count = 0  # Reset pass count
            
            # Check if player won
            if len(human_player.hand) == 0:
                print(f"🎉 {human_player.name} won the game!")
            
            # Advance turn if game is not over
            if not game.is_game_over():
                advance_turn()
            
            message = f"{human_player.name} played {' '.join(str(c) for c in play_cards)}"
        
        # Save game state
        save_game(game)
        
        return jsonify({
            'success': True,
            'message': message,
            'state': serialize_game_state(game)
        })
        
    except Exception as e:
        print(f"Error in play_cards: {str(e)}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/pass_turn', methods=['POST'])
def api_pass_turn():
    try:
        game = get_game()
        if not game:
            return jsonify({
                'success': False,
                'error': 'No game found'
            })
        
        # Check if game is over
        if game.is_game_over():
            return jsonify({
                'success': False,
                'error': 'Game is already over'
            })
        
        # Check if it's player's turn
        if session.get('current_player_index', 0) != 0:
            return jsonify({
                'success': False,
                'error': 'Not your turn'
            })
        
        # Get human player (first player)
        human_player = game.players[0]
        
        # Record pass
        game.pass_count += 1
        human_player.has_passed = True
        
        if game.pass_count >= 3:  # All players passed
            game.reset_round()
            game.pass_count = 0
            # Reset all players' pass status
            for player in game.players:
                player.has_passed = False
        
        # Advance turn if game is not over
        if not game.is_game_over():
            advance_turn()
        
        message = f"{human_player.name} passed."
        
        # Save game state
        save_game(game)
        
        return jsonify({
            'success': True,
            'message': message,
            'state': serialize_game_state(game)
        })
        
    except Exception as e:
        print(f"Error in pass_turn: {str(e)}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/bot_move', methods=['POST'])
def api_bot_move():
    try:
        game = get_game()
        if not game:
            return jsonify({
                'success': False,
                'error': 'No game found'
            })
        
        # Check if game is over
        if game.is_game_over():
            return jsonify({
                'success': False,
                'error': 'Game is already over'
            })
        
        # Get current player index from session
        current_player_index = session.get('current_player_index', 0)
        
        # Safety check - ensure index is valid
        if current_player_index >= len(game.players):
            current_player_index = 0
            session['current_player_index'] = 0
        
        # Check if it's a bot's turn (indices 1, 2, 3 are bots)
        if current_player_index == 0:
            return jsonify({
                'success': False,
                'error': 'Not bot\'s turn'
            })
        
        bot = game.players[current_player_index]
        
        print(f"Bot {bot.name} is playing...")
        
        # Check if bot has already won
        if bot.has_won():
            message = f"{bot.name} has already won"
            is_pass = False
        else:
            # Let bot play
            bot_play = game.bot_turn(bot)
            
            if bot_play:
                message = f"{bot.name} played {' '.join(str(c) for c in bot_play)}"
                # Reset pass count since bot played
                game.pass_count = 0
                is_pass = False
            else:
                message = f"{bot.name} passed"
                game.pass_count += 1
                is_pass = True
                
                if game.pass_count >= 3:  # All players passed
                    game.reset_round()
                    game.pass_count = 0
        
        # Advance turn ONLY if game is not over
        if not game.is_game_over():
            advance_turn()
        
        print(f"Bot move result: {message}")
        
        # Save game state
        save_game(game)
        
        return jsonify({
            'success': True,
            'message': message,
            'is_pass': is_pass,
            'state': serialize_game_state(game)
        })
        
    except Exception as e:
        print(f"Error in bot_move: {str(e)}")
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
        
        # Clear the current game from session
        session.pop('game_data', None)
        session.pop('current_player_index', None)
        
        # Create a new game
        game = Game()
        game.players[0].name = player_name
        session['current_player_index'] = 0
        
        # Save game to session
        save_game(game)
        
        print(f"Game restarted for {player_name}")
        
        return jsonify({
            'success': True,
            'message': 'Game restarted successfully',
            'session_id': id(game),
            'game_id': id(game),
            'state': serialize_game_state(game)
        })
        
    except Exception as e:
        print(f"Error in restart_game: {str(e)}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/get_valid_plays', methods=['GET'])
def api_get_valid_plays():
    try:
        game = get_game()
        if not game:
            return jsonify({
                'success': False,
                'error': 'No game found'
            })
        
        human_player = game.players[0]
        
        # Get valid plays using your game logic
        valid_plays = []
        if hasattr(game, 'get_valid_plays'):
            valid_plays = game.get_valid_plays(human_player)
        else:
            # Simple fallback: single cards that beat last play
            if game.last_play:
                for card in human_player.hand:
                    if beats([card], game.last_play):
                        valid_plays.append([card])
            else:
                # Any single card is valid
                for card in human_player.hand:
                    valid_plays.append([card])
        
        plays = []
        for play_cards in valid_plays[:10]:  # Limit to 10 suggestions
            play_type = get_play_type(play_cards) if play_cards else 'single'
            plays.append({
                'cards': [str(c) for c in play_cards],
                'type': play_type,
                'count': len(play_cards)
            })
        
        return jsonify({
            'success': True,
            'valid_plays': plays
        })
        
    except Exception as e:
        print(f"Error in get_valid_plays: {str(e)}")
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
    print("🎮 Tien Len Mien Nam Server Starting...")
    print("🌐 Server running at: http://localhost:5000")
    print("🔒 Server includes crash protection and restart functionality")
    print("📁 Make sure you have:")
    print("   - cards.js in /static directory")
    print("   - index.html in /templates directory")
    print("   - core/ directory with all game modules")
    app.run(debug=True, port=5000)