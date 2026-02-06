import pygame
import sys
import math
import random
from enum import Enum
from collections import deque
from core.game import Game
from gui.renderer import draw_card, draw_rounded_rect
from core.rules import is_valid_play, beats, get_play_type

pygame.init()

# -------------------- CONFIG --------------------
WIDTH, HEIGHT = 1200, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tiến Lên Miền Nam - Premium Edition")
clock = pygame.time.Clock()

# Enhanced fonts
FONT = pygame.font.SysFont("arial", 20, bold=True)
SMALL_FONT = pygame.font.SysFont("arial", 14)
LARGE_FONT = pygame.font.SysFont("arial", 32, bold=True)
TITLE_FONT = pygame.font.SysFont("arial", 48, bold=True)

CARD_WIDTH = 70
CARD_HEIGHT = 100
CARD_GAP = 10

BUTTON_WIDTH = 120
BUTTON_HEIGHT = 45

HAND_Y = HEIGHT - CARD_HEIGHT - 60

# Enhanced colors
BACKGROUND = (30, 120, 30)  # Darker forest green
TABLE_COLOR = (20, 80, 20)   # Dark green for table
PLAYER_HIGHLIGHT = (255, 215, 0)  # Gold
CARD_BACKGROUND = (255, 255, 255)
SELECTED_BORDER = (0, 100, 255)
HOVER_BORDER = (255, 200, 0)
TEXT_COLOR = (240, 240, 240)
BUTTON_COLOR = (60, 140, 60)
BUTTON_HOVER = (80, 160, 80)
BUTTON_ACTIVE = (100, 180, 100)
BOMB_COLOR = (255, 100, 100)  # Red color for bombs

# Animation settings
class AnimationType(Enum):
    MOVE = 1
    FLOAT = 2
    PULSE = 3

class CardAnimation:
    def __init__(self, card, start_pos, end_pos, duration=0.5, anim_type=AnimationType.MOVE):
        self.card = card
        self.start_pos = list(start_pos)
        self.end_pos = list(end_pos)
        self.duration = duration
        self.elapsed = 0
        self.anim_type = anim_type
        self.active = True
        
    def update(self, dt):
        self.elapsed += dt
        if self.elapsed >= self.duration:
            self.active = False
            return self.end_pos
        
        progress = self.elapsed / self.duration
        
        # Smooth easing function
        if progress < 0.5:
            ease = 2 * progress * progress
        else:
            progress = 2 * progress - 1
            ease = 1 - (1 - progress) * (1 - progress)
        
        if self.anim_type == AnimationType.FLOAT:
            # Add sine wave for floating effect
            float_offset = math.sin(self.elapsed * 5) * 5
            y_offset = float_offset
        else:
            y_offset = 0
        
        x = self.start_pos[0] + (self.end_pos[0] - self.start_pos[0]) * ease
        y = self.start_pos[1] + (self.end_pos[1] - self.start_pos[1]) * ease + y_offset
        return (int(x), int(y))

class Particle:
    def __init__(self, x, y, color=None, bomb_effect=False):
        self.x = x
        self.y = y
        if bomb_effect:
            self.vx = random.uniform(-8, 8)
            self.vy = random.uniform(-10, -5)
            self.size = random.randint(5, 12)
        else:
            self.vx = random.uniform(-3, 3)
            self.vy = random.uniform(-5, -2)
            self.size = random.randint(3, 8)
        self.color = color or random.choice([
            (255, 215, 0),  # Gold
            (255, 255, 255), # White
            (255, 100, 100), # Red
            (100, 200, 255)  # Blue
        ])
        self.lifetime = random.uniform(0.8, 1.5)
        if bomb_effect:
            self.lifetime = random.uniform(1.0, 2.0)
        self.age = 0
        self.gravity = 0.3
        self.bomb_effect = bomb_effect
    
    def update(self, dt):
        self.age += dt
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity
        return self.age < self.lifetime
    
    def draw(self, surface):
        alpha = int(255 * (1 - self.age / self.lifetime))
        if alpha <= 0:
            return
        
        if self.bomb_effect:
            # Bomb particles are more dramatic
            temp_surface = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            # Inner bright core
            pygame.draw.circle(temp_surface, (*self.color, alpha), 
                              (self.size, self.size), self.size)
            # Outer glow
            pygame.draw.circle(temp_surface, (*self.color, alpha // 2), 
                              (self.size, self.size), self.size * 1.5)
            surface.blit(temp_surface, (int(self.x - self.size), int(self.y - self.size)))
        else:
            # Regular particles
            temp_surface = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            pygame.draw.circle(temp_surface, (*self.color, alpha), 
                              (self.size, self.size), self.size)
            surface.blit(temp_surface, (int(self.x - self.size), int(self.y - self.size)))

class PassNotification:
    def __init__(self, bot_name, x, y):
        self.bot_name = bot_name
        self.x = x
        self.y = y
        self.start_time = pygame.time.get_ticks()
        self.duration = 1500  # Show for 1.5 seconds
        self.active = True
        self.scale = 0
        
    def update(self):
        current_time = pygame.time.get_ticks()
        elapsed = current_time - self.start_time
        self.active = elapsed < self.duration
        
        # Animation progress (0 to 1 to 0)
        if elapsed < 500:  # Fade in
            self.scale = elapsed / 500
        elif elapsed > 1000:  # Fade out
            self.scale = 1 - ((elapsed - 1000) / 500)
        else:  # Hold
            self.scale = 1
            
        return self.active
    
    def draw(self, screen):
        if not self.active:
            return
        
        # Create notification background with rounded corners
        notification_width = 200
        notification_height = 60
        notification_x = self.x - notification_width // 2
        notification_y = self.y - notification_height // 2
        
        # Background with shadow
        pygame.draw.rect(screen, (0, 0, 0, 100), 
                        (notification_x + 3, notification_y + 3, notification_width, notification_height), 
                        border_radius=10)
        
        # Notification background
        pygame.draw.rect(screen, (30, 40, 60, 230), 
                        (notification_x, notification_y, notification_width, notification_height), 
                        border_radius=10)
        
        # Gold border
        pygame.draw.rect(screen, (255, 215, 0), 
                        (notification_x, notification_y, notification_width, notification_height), 
                        3, border_radius=10)
        
        # Bot name text
        font = pygame.font.SysFont("arial", 16, bold=True)
        name_text = font.render(f"{self.bot_name}", True, (255, 215, 0))
        screen.blit(name_text, (self.x - name_text.get_width() // 2, notification_y + 10))
        
        # PASS text with animation
        pass_font = pygame.font.SysFont("arial", 24, bold=True)
        pass_text = pass_font.render("PASSED!", True, (255, 100, 100))
        
        # Scale the "PASSED!" text during animation
        scaled_width = int(pass_text.get_width() * self.scale)
        scaled_height = int(pass_text.get_height() * self.scale)
        if scaled_width > 0 and scaled_height > 0:
            scaled_pass = pygame.transform.scale(pass_text, (scaled_width, scaled_height))
            screen.blit(scaled_pass, 
                       (self.x - scaled_width // 2, notification_y + 35 - scaled_height // 2))
        
        # Optional: Add a pass icon
        icon_font = pygame.font.SysFont("arial", 20)
        icon_text = icon_font.render("⏭️", True, (255, 255, 255))
        screen.blit(icon_text, (notification_x + 10, notification_y + 20))

# -------------------- INIT GAME --------------------
game = Game()
selected_indexes = []
animations = []
particles = []
pass_notifications = []  # For bot pass notifications

current_player = 0
winner_of_current_round = None
is_new_round = True
last_play_time = 0
game_over = False

# Button rectangles
play_button_rect = pygame.Rect(WIDTH - 250, HEIGHT - 70, BUTTON_WIDTH, BUTTON_HEIGHT)
pass_button_rect = pygame.Rect(WIDTH - 120, HEIGHT - 70, BUTTON_WIDTH, BUTTON_HEIGHT)
restart_button_rect = pygame.Rect(WIDTH - 250, 30, BUTTON_WIDTH, BUTTON_HEIGHT)  # New restart button

# -------------------- HELPER FUNCTIONS --------------------

def add_log(log_type, message):
    """Add message to console log"""
    print(f"[{log_type.upper()}] {message}")

def draw_hand(player):
    """Draw player's hand with enhanced visuals"""
    total_cards = len(player.hand)
    if total_cards == 0:
        return
    
    # Calculate spacing with overlap for many cards
    max_spacing = CARD_WIDTH + CARD_GAP
    min_spacing = CARD_WIDTH // 2
    available_width = WIDTH - 100
    
    if total_cards * max_spacing > available_width:
        spacing = max(min_spacing, available_width // total_cards)
        overlap = max_spacing - spacing
    else:
        spacing = max_spacing
        overlap = 0
    
    start_x = (WIDTH - (total_cards * spacing - overlap * (total_cards - 1))) // 2
    
    mouse_pos = pygame.mouse.get_pos()
    
    for i, card in enumerate(player.hand):
        x = start_x + i * (spacing - overlap)
        
        # Hover effect
        card_rect = pygame.Rect(x, HAND_Y, CARD_WIDTH, CARD_HEIGHT)
        is_hovered = card_rect.collidepoint(mouse_pos) and current_player == 0 and not game_over
        is_selected = i in selected_indexes
        
        # Lift card on hover/selection
        y_offset = -15 if is_hovered or is_selected else 0
        
        # Use the renderer's draw_card function
        draw_card(screen, card, x, HAND_Y + y_offset, 
                 selected=is_selected, hovered=is_hovered, show_shadow=(i == 0 or not is_selected))
        
        # Selection indicator
        if is_selected:
            pygame.draw.circle(screen, SELECTED_BORDER, 
                             (x + CARD_WIDTH // 2, HAND_Y + y_offset - 5), 5)

def draw_table():
    """Draw the table with play history"""
    # Table background - taller to accommodate history
    table_bg = pygame.Rect(50, 50, WIDTH - 100, 250)
    draw_rounded_rect(screen, table_bg, TABLE_COLOR, 20)
    
    # Table border with glow effect
    border_color = (100, 200, 100) if is_new_round else (80, 160, 80)
    pygame.draw.rect(screen, border_color, table_bg, 4, 20)
    
    # Table label
    label = FONT.render("PLAY HISTORY", True, (200, 255, 200))
    screen.blit(label, (WIDTH // 2 - 60, 60))
    
    # Get recent plays from game history
    recent_plays = game.get_recent_plays(count=5, current_round_only=True)
    
    if not recent_plays and not game.last_play:
        # Empty table message
        empty_text = LARGE_FONT.render("Start the round!", True, (200, 255, 200))
        screen.blit(empty_text, (WIDTH // 2 - 100, 120))
        return
    
    # Draw each recent play in a timeline
    start_y = 90
    max_plays_to_show = 5
    
    # Show most recent plays (up to 5)
    plays_to_show = recent_plays[-max_plays_to_show:] if recent_plays else []
    
    for i, play in enumerate(plays_to_show):
        player_name = play['player']
        cards = play['cards']
        is_pass = play['is_pass']
        play_type = play['play_type']
        is_bomb = play.get('is_bomb', False)
        
        # Calculate position
        y_pos = start_y + i * 45
        
        # Background for the play row
        if i == len(plays_to_show) - 1:  # Highlight most recent
            row_bg = pygame.Rect(60, y_pos - 5, WIDTH - 120, 40)
            bg_color = (255, 50, 50, 60) if is_bomb else (255, 255, 0, 30)
            pygame.draw.rect(screen, bg_color, row_bg, border_radius=8)
        
        # Draw turn number
        turn_num = len(recent_plays) - max_plays_to_show + i + 1
        if turn_num < 1:
            turn_num = i + 1
        
        # Draw player info
        player_color = (255, 255, 0) if player_name == "You" else (200, 255, 200)
        
        if is_pass:
            # Draw pass
            pass_text = f"Turn {turn_num}: {player_name} passed"
            text_color = (255, 150, 150)  # Reddish for passes
            turn_surface = SMALL_FONT.render(pass_text, True, text_color)
            screen.blit(turn_surface, (70, y_pos))
        else:
            # Draw play info
            play_info = f"Turn {turn_num}: {player_name} played"
            turn_surface = SMALL_FONT.render(play_info, True, player_color)
            screen.blit(turn_surface, (70, y_pos))
            
            # Draw bomb indicator
            if is_bomb:
                bomb_text = SMALL_FONT.render("💣", True, (255, 50, 50))
                screen.blit(bomb_text, (70, y_pos + 15))
            
            # Draw cards
            num_cards = len(cards)
            card_start_x = 250
            
            for j, card in enumerate(cards):
                x = card_start_x + j * (CARD_WIDTH // 2)  # Overlap cards
                y = y_pos
                
                # Draw smaller cards for history
                draw_card(screen, card, x, y, 
                         show_shadow=True,
                         scale=0.6)  # Removed highlight parameter
                
                # Show "..." if too many cards
                if num_cards > 6 and j == 5:
                    ellipsis = SMALL_FONT.render(f"... +{num_cards - 5}", True, (255, 255, 255))
                    screen.blit(ellipsis, (x + 30, y + CARD_HEIGHT // 2 - 10))
                    break
            
            # Draw play type
            type_text = SMALL_FONT.render(f"({play_type})", True, (200, 200, 255))
            screen.blit(type_text, (card_start_x + min(num_cards, 6) * (CARD_WIDTH // 2) + 20, y_pos + 5))

def draw_current_play():
    """Draw the current/last play prominently"""
    if not game.last_play:
        return
    
    # Get the most recent play to check if it's a bomb or contains 2
    recent_plays = game.get_recent_plays(count=1, current_round_only=True)
    is_bomb = recent_plays[-1].get('is_bomb', False) if recent_plays else False
    has_two = any(card.rank == 2 or card.rank == 15 for card in game.last_play)
    
    # Draw a separator
    separator_y = 300
    pygame.draw.line(screen, (100, 200, 100), (50, separator_y), (WIDTH - 50, separator_y), 2)
    
    # Label for current play
    current_label = FONT.render("CURRENT PLAY", True, (255, 255, 0))
    screen.blit(current_label, (WIDTH // 2 - 70, separator_y + 10))
    
    if is_bomb:
        bomb_label = FONT.render("💣 BOMB! 💣", True, (255, 50, 50))
        screen.blit(bomb_label, (WIDTH // 2 + 30, separator_y + 10))
    elif has_two:
        two_label = FONT.render("CONTAINS 2!", True, (255, 255, 100))
        screen.blit(two_label, (WIDTH // 2 + 30, separator_y + 10))

def draw_buttons():
    """Draw enhanced buttons with hover effects"""
    mouse_pos = pygame.mouse.get_pos()
    current_time = pygame.time.get_ticks()
    
    # Restart Button (only show when game is over)
    if game_over:
        restart_hover = restart_button_rect.collidepoint(mouse_pos)
        restart_color = BUTTON_HOVER if restart_hover else BUTTON_COLOR
        
        # Draw restart button
        shadow_rect = restart_button_rect.move(4, 4)
        draw_rounded_rect(screen, shadow_rect, (0, 0, 0, 100), 12)
        
        draw_rounded_rect(screen, restart_button_rect, restart_color, 10)
        
        border_color = (255, 255, 255) if restart_hover else (200, 200, 200)
        draw_rounded_rect(screen, restart_button_rect, border_color, 10, 2, border_color)
        
        restart_text = FONT.render("RESTART", True, (255, 255, 255))
        text_shadow = FONT.render("RESTART", True, (0, 0, 0, 150))
        text_rect = restart_text.get_rect(center=restart_button_rect.center)
        screen.blit(text_shadow, text_rect.move(2, 2))
        screen.blit(restart_text, text_rect)
    
    # Play Button
    play_hover = play_button_rect.collidepoint(mouse_pos) and current_player == 0 and not game_over
    play_color = BUTTON_ACTIVE if play_hover else BUTTON_COLOR
    
    # Pulsing effect for current player
    if current_player == 0 and not game_over:
        pulse = abs(math.sin(current_time * 0.002)) * 20
        play_button_rect_pulse = play_button_rect.inflate(pulse, pulse)
    else:
        play_button_rect_pulse = play_button_rect
    
    # Shadow
    shadow_rect = play_button_rect_pulse.move(4, 4)
    draw_rounded_rect(screen, shadow_rect, (0, 0, 0, 100), 12)
    
    # Button
    draw_rounded_rect(screen, play_button_rect_pulse, play_color, 10)
    
    # Border
    border_color = (255, 255, 255) if play_hover else (200, 200, 200)
    draw_rounded_rect(screen, play_button_rect_pulse, border_color, 10, 2, border_color)
    
    # Text with shadow
    play_text = FONT.render("PLAY", True, (255, 255, 255))
    text_shadow = FONT.render("PLAY", True, (0, 0, 0, 150))
    text_rect = play_text.get_rect(center=play_button_rect.center)
    screen.blit(text_shadow, text_rect.move(2, 2))
    screen.blit(play_text, text_rect)
    
    # Pass Button
    pass_hover = pass_button_rect.collidepoint(mouse_pos) and current_player == 0 and not game_over
    pass_color = (180, 60, 60) if pass_hover else (140, 40, 40)
    
    # Shadow
    shadow_rect = pass_button_rect.move(4, 4)
    draw_rounded_rect(screen, shadow_rect, (0, 0, 0, 100), 12)
    
    # Button
    draw_rounded_rect(screen, pass_button_rect, pass_color, 10)
    
    # Border
    border_color = (255, 255, 255) if pass_hover else (200, 200, 200)
    draw_rounded_rect(screen, pass_button_rect, border_color, 10, 2, border_color)
    
    # Text with shadow
    pass_text = FONT.render("PASS", True, (255, 255, 255))
    text_shadow = FONT.render("PASS", True, (0, 0, 0, 150))
    text_rect = pass_text.get_rect(center=pass_button_rect.center)
    screen.blit(text_shadow, text_rect.move(2, 2))
    screen.blit(pass_text, text_rect)

def draw_player_info():
    """Draw player information panels"""
    player_positions = [
        (50, 380),   # Player 1 (left)
        (WIDTH - 250, 380),  # Player 2 (right top)
        (50, 450),   # Player 3 (left bottom)
        (WIDTH - 250, 450)   # Player 4 (right bottom)
    ]
    
    for i, player in enumerate(game.players):
        is_current = i == current_player and not game_over
        has_won = player.has_won()
        
        # Position and size
        x, y = player_positions[i]
        width, height = 200, 60
        
        # Colors based on state
        if has_won:
            bg_color = (255, 215, 0)  # Gold for winner
            text_color = (0, 0, 0)
        elif is_current:
            bg_color = (70, 130, 180)  # Steel blue for current player
            text_color = (255, 255, 255)
        else:
            bg_color = (40, 40, 40, 200)
            text_color = (200, 200, 200)
        
        # Panel background
        panel_rect = pygame.Rect(x, y, width, height)
        draw_rounded_rect(screen, panel_rect, bg_color, 12)
        
        # Border for current player
        if is_current:
            pygame.draw.rect(screen, (255, 255, 255), panel_rect, 3, 12)
        
        # Player name
        name = "YOU" if i == 0 else player.name
        name_text = FONT.render(name, True, text_color)
        screen.blit(name_text, (x + 15, y + 10))
        
        # Card count
        count_text = SMALL_FONT.render(f"Cards: {len(player.hand)}", True, text_color)
        screen.blit(count_text, (x + 15, y + 35))
        
        # Visual card indicators
        card_count = len(player.hand)
        max_indicators = min(8, card_count)
        indicator_spacing = 12
        
        for j in range(max_indicators):
            indicator_x = x + width - 30 - j * (indicator_spacing - 3)
            indicator_y = y + height // 2
            
            # Create small card-like indicators
            indicator_rect = pygame.Rect(indicator_x, indicator_y, 8, 12)
            indicator_color = (255, 255, 255) if is_current else (180, 180, 180)
            pygame.draw.rect(screen, indicator_color, indicator_rect, border_radius=2)
            pygame.draw.rect(screen, (100, 100, 100), indicator_rect, 1, border_radius=2)
        
        # Winner crown
        if has_won:
            crown_y = y - 25
            pygame.draw.polygon(screen, (255, 215, 0), [
                (x + width//2 - 15, crown_y + 20),
                (x + width//2, crown_y),
                (x + width//2 + 15, crown_y + 20),
                (x + width//2 + 10, crown_y + 20),
                (x + width//2 + 10, crown_y + 30),
                (x + width//2 - 10, crown_y + 30),
                (x + width//2 - 10, crown_y + 20)
            ])

def draw_game_status():
    """Draw current game status information with panel"""
    # Position for status panel
    panel_x = WIDTH - 370
    panel_y = 80
    panel_width = 300
    panel_height = 110
    
    # Draw status panel background
    panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
    draw_rounded_rect(screen, panel_rect, (40, 40, 40, 180), 12)
    pygame.draw.rect(screen, (100, 200, 100), panel_rect, 2, 12)
    
    # Panel title
    panel_title = SMALL_FONT.render("GAME STATUS", True, (255, 255, 200))
    screen.blit(panel_title, (panel_x + 10, panel_y + 5))
    
    # Status items
    status_items = [
        f"Round: {game.round_number}",
        f"Passes: {game.pass_count}/{len(game.players)-1}",
        f"Plays this round: {len(game.get_current_round_plays())}",
        f"Bomb used: {'Yes' if game.bomb_used else 'No'}"
    ]
    
    # Colors for each item
    item_colors = [
        (255, 255, 200),  # Round - yellow
        (255, 255, 200),  # Passes - yellow
        (255, 255, 200),  # Plays - yellow
        (255, 100, 100) if game.bomb_used else (200, 200, 200)  # Bomb - red if used
    ]
    
    # Draw each status item
    for i, (text, color) in enumerate(zip(status_items, item_colors)):
        item_surface = SMALL_FONT.render(text, True, color)
        screen.blit(item_surface, (panel_x + 15, panel_y + 30 + i * 20))
    
    # New round indicator (above the table)
    if is_new_round:
        # Create a banner at the top of the table
        banner_rect = pygame.Rect(WIDTH // 2 - 200, 15, 400, 30)
        draw_rounded_rect(screen, banner_rect, (255, 215, 0, 200), 8)  # Gold banner
        
        banner_text = FONT.render("NEW ROUND - Play Any Valid Combination!", 
                                 True, (0, 0, 0))  # Black text for contrast
        text_rect = banner_text.get_rect(center=banner_rect.center)
        screen.blit(banner_text, text_rect)
    
    # Turn indicator at bottom
    if not game_over:
        turn_text = f"Current Turn: {game.players[current_player].name}"
        turn_color = (255, 255, 0) if current_player == 0 else (255, 200, 100)
        turn_surface = FONT.render(turn_text, True, turn_color)
        
        # Optional: Add background for turn indicator
        text_rect = turn_surface.get_rect(center=(WIDTH // 2, HEIGHT - 30))
        bg_rect = text_rect.inflate(20, 10)
        draw_rounded_rect(screen, bg_rect, (40, 40, 40, 180), 8)
        
        screen.blit(turn_surface, text_rect)

def draw_game_over():
    """Draw game over screen"""
    if not any(player.has_won() for player in game.players):
        return
    
    # Find winner
    winner = None
    for player in game.players:
        if player.has_won():
            winner = player
            break
    
    if winner:
        # Semi-transparent overlay
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        
        # Winner announcement
        winner_text = TITLE_FONT.render(f"{winner.name} WINS!", True, (255, 215, 0))
        text_rect = winner_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
        screen.blit(winner_text, text_rect)
        
        # Celebration message
        if winner.name == "YOU":
            message = "Congratulations! You are the Tiến Lên Master!"
        else:
            message = f"{winner.name} has won the game!"
        
        message_surface = LARGE_FONT.render(message, True, (255, 255, 255))
        message_rect = message_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 20))
        screen.blit(message_surface, message_rect)
        
        # Game statistics
        stats = game.get_player_stats()
        stats_text = f"Total plays: {game.total_plays} | Round: {game.round_number}"
        stats_surface = SMALL_FONT.render(stats_text, True, (200, 200, 200))
        stats_rect = stats_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 70))
        screen.blit(stats_surface, stats_rect)
        
        # Bomb statistics if any were used
        bombs_used = sum(stats[player.name]['bombs_used'] for player in game.players)
        if bombs_used > 0:
            bomb_stats = f"Bombs used in game: {bombs_used}"
            bomb_surface = SMALL_FONT.render(bomb_stats, True, (255, 100, 100))
            bomb_rect = bomb_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 100))
            screen.blit(bomb_surface, bomb_rect)
        
        # Restart instruction
        restart_text = SMALL_FONT.render("Press SPACE to restart or ESC to quit", True, (200, 200, 200))
        restart_rect = restart_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 130))
        screen.blit(restart_text, restart_rect)

def create_celebration_particles(x, y, count=20, is_bomb=False):
    """Create celebration particles"""
    for _ in range(count):
        color = None
        if is_bomb:
            # Bomb particles are red/orange
            color = random.choice([
                (255, 100, 100),  # Red
                (255, 150, 50),   # Orange
                (255, 200, 0)     # Yellow-orange
            ])
        particles.append(Particle(x, y, color, bomb_effect=is_bomb))

def get_card_index_at_pos(pos, player):
    """Get card index at mouse position"""
    total_cards = len(player.hand)
    if total_cards == 0:
        return None
    
    max_spacing = CARD_WIDTH + CARD_GAP
    min_spacing = CARD_WIDTH // 2
    available_width = WIDTH - 100
    
    if total_cards * max_spacing > available_width:
        spacing = max(min_spacing, available_width // total_cards)
        overlap = max_spacing - spacing
    else:
        spacing = max_spacing
        overlap = 0
    
    start_x = (WIDTH - (total_cards * spacing - overlap * (total_cards - 1))) // 2
    
    for i in range(total_cards):
        x = start_x + i * (spacing - overlap)
        rect = pygame.Rect(x, HAND_Y, CARD_WIDTH, CARD_HEIGHT)
        if rect.collidepoint(pos):
            return i
    return None

def restart_game():
    """Restart the game completely"""
    global game, selected_indexes, animations, particles, pass_notifications
    global current_player, winner_of_current_round, is_new_round, last_play_time, game_over
    global bot_thinking, last_bot_turn_time
    
    # Create new game
    game = Game()
    selected_indexes = []
    animations = []
    particles = []
    pass_notifications = []  # Clear notifications
    current_player = 0
    winner_of_current_round = None
    is_new_round = True
    game_over = False
    bot_thinking = False
    last_bot_turn_time = 0
    
    print("Game restarted!")
    add_log('system', "Game restarted!")

def process_player_turn():
    """Process human player's turn"""
    global selected_indexes, winner_of_current_round, is_new_round, game_over
    
    if not selected_indexes:
        return False
    
    selected_cards = [game.players[0].hand[i] for i in selected_indexes]
    
    # Debug info
    print(f"\n=== PLAY ATTEMPT ===")
    print(f"Selected {len(selected_cards)} cards: {[str(c) for c in selected_cards]}")
    print(f"Table has: {[str(c) for c in game.last_play] if game.last_play else 'Nothing'}")
    print(f"Is new round: {is_new_round}")
    
    # DEBUG: Show card strengths
    from core.rules import card_strength
    if selected_cards:
        print("DEBUG - Selected card strengths:")
        for card in selected_cards:
            print(f"  {card}: rank={card.rank} (type: {type(card.rank)}), strength={card_strength(card)}")
    
    if game.last_play:
        print("DEBUG - Table card strengths:")
        for card in game.last_play:
            print(f"  {card}: rank={card.rank} (type: {type(card.rank)}), strength={card_strength(card)}")
    
    # Always check if play is valid first
    if not is_valid_play(selected_cards):
        print("❌ Invalid combination!")
        selected_indexes.clear()
        return False
    
    # Check if this is a bomb
    play_type = get_play_type(selected_cards)
    is_bomb = play_type in ["quadruple", "consecutive_pairs"] and len(selected_cards) >= 4
    
    # If table has cards (not new round), check if play beats them
    if game.last_play and not is_new_round:
        beats_result = beats(selected_cards, game.last_play)
        print(f"Beats check: {beats_result}")
        
        # Check if table has 2 for bomb validation
        table_has_two = any(card.rank == 2 or card.rank == 15 for card in game.last_play)
        
        if is_bomb and not table_has_two:
            print("❌ Bomb can only be used to beat plays containing 2!")
            selected_indexes.clear()
            return False
        
        if not beats_result:
            print("❌ Invalid move! Your play doesn't beat the table.")
            selected_indexes.clear()
            return False
        elif is_bomb:
            print("💣 Bomb played on 2! 💣")
    
    # Execute move - IMPORTANT: Make sure we remove the actual card objects
    selected_card_objects = []
    for idx in sorted(selected_indexes, reverse=True):
        selected_card_objects.append(game.players[0].hand[idx])
        game.players[0].hand.pop(idx)
    
    # Update game state using game methods
    winner_of_current_round = 0
    is_new_round = False
    game.last_play = selected_card_objects.copy()  # Use the actual card objects
    game.pass_count = 0
    
    # Record the play in history
    game._record_play(game.players[0], selected_card_objects)
    
    selected_indexes.clear()
    
    # Create celebration particles
    if is_bomb:
        create_celebration_particles(WIDTH // 2, 150, 30, is_bomb=True)
        print("💣 BOMB PLAYED! 💣")
    else:
        create_celebration_particles(WIDTH // 2, 150, 15)
    
    print(f"✅ Play successful! Remaining cards: {len(game.players[0].hand)}")
    
    # Print updated history
    print_play_history()
    
    # Check win
    if game.players[0].has_won():
        print("🎉 YOU WIN!")
        create_celebration_particles(WIDTH // 2, HEIGHT // 2, 50)
        game_over = True
    
    return True

def print_play_history():
    """Print play history to console"""
    print("\n" + "="*60)
    print("PLAY HISTORY (Current Round)")
    print("="*60)
    
    current_round_plays = game.get_current_round_plays()
    if not current_round_plays:
        print("No plays in current round.")
        print("="*60)
        return
    
    for i, play in enumerate(current_round_plays):
        play_str = game.get_play_string(play)
        print(f"{i+1:2d}. {play_str}")
    
    print("="*60)
    print(f"Total plays this round: {len(current_round_plays)}")
    print(f"Bombs used this round: {sum(1 for p in current_round_plays if p.get('is_bomb', False))}")
    if winner_of_current_round is not None:
        print(f"Current player to beat: {game.players[winner_of_current_round].name}")
    else:
        print("Current player to beat: None (new round)")
    print("="*60 + "\n")

# -------------------- MAIN LOOP --------------------

running = True
last_time = pygame.time.get_ticks()
bot_turn_delay = 500  # Delay between bot turns in milliseconds
last_bot_turn_time = 0
bot_thinking = False

while running:
    # Calculate delta time for smooth animations
    current_time = pygame.time.get_ticks()
    dt = (current_time - last_time) / 1000.0
    last_time = current_time
    
    # Clear screen with gradient
    for y in range(HEIGHT):
        color_factor = y / HEIGHT
        color = (
            int(BACKGROUND[0] * (0.7 + 0.3 * color_factor)),
            int(BACKGROUND[1] * (0.7 + 0.3 * color_factor)),
            int(BACKGROUND[2] * (0.7 + 0.3 * color_factor))
        )
        pygame.draw.line(screen, color, (0, y), (WIDTH, y))
    
    # Update and draw particles
    particles = [p for p in particles if p.update(dt)]
    for particle in particles:
        particle.draw(screen)
    
    # Update animations
    for anim in animations[:]:
        pos = anim.update(dt)
        if not anim.active:
            animations.remove(anim)
    
    # Update and draw pass notifications
    pass_notifications = [n for n in pass_notifications if n.update()]
    for notification in pass_notifications:
        notification.draw(screen)
    
    # Draw game elements
    draw_table()
    draw_current_play()
    draw_player_info()
    draw_game_status()
    draw_hand(game.players[0])
    draw_buttons()
    
    # Check for game over
    game_over = any(player.has_won() for player in game.players)
    if game_over:
        draw_game_over()
    
    # -------------------- EVENT HANDLING --------------------
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_SPACE and game_over:
                # Restart game
                restart_game()
            elif event.key == pygame.K_h and current_player == 0:  # Hint key
                print("\n=== HINT ===")
                print(f"Your hand: {[str(c) for c in game.players[0].hand]}")
                if game.last_play:
                    print(f"Table: {[str(c) for c in game.last_play]}")
                    valid_plays = game.get_valid_plays(game.players[0])
                    print(f"Valid plays: {len(valid_plays)}")
                    if valid_plays:
                        print("You can play:")
                        for i, play in enumerate(valid_plays[:5]):  # Show first 5
                            play_type = get_play_type(play)
                            is_bomb = play_type in ["quadruple", "consecutive_pairs"] and len(play) >= 4
                            bomb_indicator = " 💣" if is_bomb else ""
                            print(f"  {i+1}. {[str(c) for c in play]} ({play_type}{bomb_indicator})")
                else:
                    print("Table is empty - you can play any valid combination!")
                print("============\n")
            elif event.key == pygame.K_p:  # Print history
                print_play_history()
            elif event.key == pygame.K_s:  # Show game stats
                print("\n=== GAME STATISTICS ===")
                stats = game.get_game_summary()
                for key, value in stats.items():
                    print(f"{key}: {value}")
                print("=====================\n")
            elif event.key == pygame.K_r:  # Debug: show current state
                print(f"\n=== DEBUG INFO ===")
                print(f"Current player: {current_player} ({game.players[current_player].name})")
                print(f"Winner of round: {winner_of_current_round}")
                print(f"Is new round: {is_new_round}")
                print(f"Last play: {game.last_play}")
                print(f"Pass count: {game.pass_count}")
                print(f"Game over: {game_over}")
                print(f"Bomb used this round: {game.bomb_used}")
                print("==================\n")
        
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if game_over:
                # Check restart button
                if restart_button_rect.collidepoint(event.pos):
                    restart_game()
                    continue
                else:
                    continue
                
            if current_player == 0:
                # Play button
                if play_button_rect.collidepoint(event.pos):
                    if selected_indexes:
                        if process_player_turn():
                            # Move to next player if not game over
                            if not game_over:
                                current_player = (current_player + 1) % 4
                                bot_thinking = True
                                last_bot_turn_time = current_time

                # Pass button
                elif pass_button_rect.collidepoint(event.pos):
                    print("You pass")
                    game.pass_count += 1
                    game._record_pass(game.players[0])
                    selected_indexes.clear()
                    
                    # Print updated history
                    print_play_history()
                    
                    # Check if all others passed
                    if game.pass_count == len(game.players) - 1:
                        print("All passed. New round!")
                        game.reset_round()
                        is_new_round = True
                        current_player = winner_of_current_round if winner_of_current_round is not None else current_player
                    else:
                        current_player = (current_player + 1) % 4
                        bot_thinking = True
                        last_bot_turn_time = current_time

                # Click card to select/deselect
                else:
                    idx = get_card_index_at_pos(event.pos, game.players[0])
                    if idx is not None:
                        if idx in selected_indexes:
                            selected_indexes.remove(idx)
                            print(f"Deselected card {idx}")
                        else:
                            selected_indexes.append(idx)
                            print(f"Selected card {idx}: {game.players[0].hand[idx]}")
    
    # -------------------- BOT TURN PROCESSING --------------------
    if not game_over and current_player != 0 and not bot_thinking:
        # Start bot thinking
        bot_thinking = True
        last_bot_turn_time = current_time
    
    if bot_thinking and current_time - last_bot_turn_time >= bot_turn_delay:
        bot_thinking = False
        
        # Process bot turn
        bot = game.players[current_player]
        
        # If bot has won, skip turn
        if bot.has_won():
            print(f"{bot.name} has already won, skipping turn")
            current_player = (current_player + 1) % 4
            bot_thinking = True
            last_bot_turn_time = current_time
            continue
        
        print(f"\n{bot.name}'s turn...")
        print(f"Table has: {[str(c) for c in game.last_play] if game.last_play else 'Nothing'}")
        
        # DEBUG: Print card strengths
        if game.last_play:
            print("DEBUG - Table card strengths:")
            for card in game.last_play:
                from core.rules import card_strength
                print(f"  {card}: rank={card.rank}, strength={card_strength(card)}")
        
        # Use game's bot_turn method
        play = game.bot_turn(bot)
        
        if play:
            print(f"{bot.name} plays: {' '.join(map(str, play))}")
            
            # DEBUG: Print card strengths of play
            print("DEBUG - Play card strengths:")
            from core.rules import card_strength
            for card in play:
                print(f"  {card}: rank={card.rank}, strength={card_strength(card)}")
            
            # DEBUG: Check if play beats table
            if game.last_play:
                beats_result = beats(play, game.last_play)
                print(f"DEBUG - beats check: {beats_result}")
            
            winner_of_current_round = current_player
            is_new_round = False
            
            # Check if this was a bomb
            play_type = get_play_type(play)
            is_bomb = play_type in ["quadruple", "consecutive_pairs"] and len(play) >= 4
            
            # Create animation for bot's play
            if is_bomb:
                create_celebration_particles(WIDTH // 2, 150, 30, is_bomb=True)
                print("💣 BOMB PLAYED! 💣")
            elif len(play) > 0:
                create_celebration_particles(WIDTH // 2, 150, 10)
        else:
            print(f"{bot.name} passes")
            game.pass_count += 1
            
            # Create pass notification
            # Position based on bot index
            bot_positions = [
                (WIDTH // 4, HEIGHT // 4),      # Bot 1 (top-left)
                (3 * WIDTH // 4, HEIGHT // 4),  # Bot 2 (top-right)
                (WIDTH // 4, 3 * HEIGHT // 4),  # Bot 3 (bottom-left)
            ]
            bot_index = current_player - 1  # Bot index (0-2)
            if bot_index < 3:
                x, y = bot_positions[bot_index]
                pass_notifications.append(PassNotification(bot.name, x, y))
        
        # IMPORTANT FIX: Check if all others passed
        if game.pass_count == len(game.players) - 1:
            print("All passed. New round!")
            game.reset_round()
            is_new_round = True
            # Set current player to the winner of the round
            current_player = winner_of_current_round if winner_of_current_round is not None else current_player
            # Reset pass count for new round
            game.pass_count = 0
            if current_player == 0:
                # Human player's turn, just continue to next frame
                pass
            else:
                bot_thinking = True
                last_bot_turn_time = current_time
        else:
            current_player = (current_player + 1) % 4
            if current_player != 0:
                bot_thinking = True
                last_bot_turn_time = current_time
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()