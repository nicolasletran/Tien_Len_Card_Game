import pygame
import math

# Card dimensions
CARD_WIDTH = 70
CARD_HEIGHT = 100

# Color scheme
CARD_BACKGROUND = (255, 255, 255)
CARD_SHADOW = (0, 0, 0, 100)
CARD_BORDER_NORMAL = (50, 50, 50)
CARD_BORDER_SELECTED = (0, 100, 255)
CARD_BORDER_HOVER = (255, 200, 0)

# Suit colors
RED_SUIT_COLOR = (200, 0, 0)
BLACK_SUIT_COLOR = (0, 0, 0)

# Font cache for performance
_font_cache = {}

def get_font(size, bold=False):
    """Get cached font for better performance"""
    key = (size, bold)
    if key not in _font_cache:
        _font_cache[key] = pygame.font.SysFont("arial", size, bold=bold)
    return _font_cache[key]

def get_card_rank_suit(card):
    """Extract rank and suit from card object or string - FIXED for your Card class"""
    # For your Card class which has numeric ranks
    if hasattr(card, 'rank') and hasattr(card, 'suit'):
        rank_value = card.rank
        suit = card.suit
        
        # Convert numeric rank to symbol - FIXED to handle all cases
        if rank_value == 2:
            rank = '2'
        elif rank_value <= 10:
            rank = str(rank_value)
        elif rank_value == 11:
            rank = 'J'
        elif rank_value == 12:
            rank = 'Q'
        elif rank_value == 13:
            rank = 'K'
        elif rank_value == 14:
            rank = 'A'
        else:
            rank = str(rank_value)
        
        return rank, suit
    elif hasattr(card, '__str__'):
        card_str = str(card)
        # Extract suit symbol
        suit_symbols = ['♠', '♣', '♦', '♥']
        suit = None
        for symbol in suit_symbols:
            if symbol in card_str:
                suit = symbol
                rank = card_str.replace(symbol, '').strip()
                break
        if suit is None:
            # Fallback if no suit symbol found
            if len(card_str) >= 2:
                rank = card_str[:-1]
                suit = card_str[-1]
            else:
                rank = card_str
                suit = '♠'
    else:
        rank = str(card)
        suit = '♠'
    
    return rank, suit

def draw_rounded_rect(surface, rect, color, radius=10, border=0, border_color=None):
    """Draw a rounded rectangle with optional border"""
    x, y, width, height = rect
    
    # Create a temporary surface for alpha blending
    temp_surface = pygame.Surface((width, height), pygame.SRCALPHA)
    
    # Draw rounded rectangle
    pygame.draw.rect(temp_surface, color, (0, 0, width, height), border_radius=radius)
    
    # Draw border if specified
    if border > 0 and border_color:
        pygame.draw.rect(temp_surface, border_color, (0, 0, width, height), 
                        border, border_radius=radius)
    
    surface.blit(temp_surface, (x, y))
    return pygame.Rect(rect)

def draw_card_shadow(surface, x, y, width, height, radius=10, alpha=100):
    """Draw card shadow"""
    shadow_surface = pygame.Surface((width + 6, height + 6), pygame.SRCALPHA)
    pygame.draw.rect(shadow_surface, (0, 0, 0, alpha), 
                    (0, 0, width, height), border_radius=radius)
    surface.blit(shadow_surface, (x + 3, y + 3))

def draw_card_back(surface, x, y, width, height, pattern='default'):
    """Draw the back of a card with pattern"""
    # Shadow
    draw_card_shadow(surface, x, y, width, height)
    
    # Card background
    card_rect = pygame.Rect(x, y, width, height)
    
    if pattern == 'default':
        # Blue pattern with red diamond
        pygame.draw.rect(surface, (30, 60, 120), card_rect, border_radius=10)
        
        # Red diamond in center
        center_x, center_y = x + width // 2, y + height // 2
        diamond_size = 30
        diamond_points = [
            (center_x, center_y - diamond_size),
            (center_x + diamond_size, center_y),
            (center_x, center_y + diamond_size),
            (center_x - diamond_size, center_y)
        ]
        pygame.draw.polygon(surface, (200, 50, 50), diamond_points)
        
        # Border
        pygame.draw.rect(surface, (255, 255, 255), card_rect, 3, border_radius=10)
    else:
        # Simple blue pattern
        pygame.draw.rect(surface, (70, 130, 180), card_rect, border_radius=10)
        pygame.draw.rect(surface, (255, 255, 255), card_rect, 2, border_radius=10)

def draw_card_face(surface, card, x, y, width, height, selected=False, hovered=False, 
                  show_shadow=True, angle=0, scale=1.0):
    """Draw the face of a card with enhanced visuals - FIXED for rank display and colors"""
    # Apply scale if needed
    if scale != 1.0:
        orig_width, orig_height = width, height
        width = int(width * scale)
        height = int(height * scale)
        x = x + (orig_width - width) // 2
        y = y + (orig_height - height) // 2
    
    # Apply rotation if needed
    if angle != 0:
        # For simplicity, we'll skip full rotation implementation
        pass
    
    # Shadow
    if show_shadow:
        draw_card_shadow(surface, x, y, width, height)
    
    # Card background
    card_rect = pygame.Rect(x, y, width, height)
    draw_rounded_rect(surface, card_rect, CARD_BACKGROUND, 10)
    
    # Border based on card state
    border_color = CARD_BORDER_SELECTED if selected else \
                   CARD_BORDER_HOVER if hovered else CARD_BORDER_NORMAL
    border_width = 3 if selected or hovered else 2
    draw_rounded_rect(surface, card_rect, border_color, 10, border_width, border_color)
    
    # Get rank and suit
    rank, suit = get_card_rank_suit(card)
    
    # Determine text color based on suit - FIXED: Now properly checks suit
    if suit in ['♥', '♦']:
        text_color = RED_SUIT_COLOR  # (200, 0, 0) for hearts and diamonds
    else:
        text_color = BLACK_SUIT_COLOR  # (0, 0, 0) for spades and clubs
    
    # Fonts
    rank_font = get_font(20, bold=True)
    suit_font = get_font(20, bold=True)
    large_suit_font = get_font(32, bold=True)
    
    # Draw rank and suit in top-left
    rank_surface = rank_font.render(rank, True, text_color)
    suit_surface = suit_font.render(suit, True, text_color)
    
    surface.blit(rank_surface, (x + 8, y + 8))
    surface.blit(suit_surface, (x + 8, y + 30))
    
    # Draw rank and suit in bottom-right (rotated)
    rank_rotated = pygame.transform.rotate(rank_surface, 180)
    suit_rotated = pygame.transform.rotate(suit_surface, 180)
    
    surface.blit(rank_rotated, (x + width - 28, y + height - 28))
    surface.blit(suit_rotated, (x + width - 28, y + height - 50))
    
    # Draw center symbol - Different size for face cards vs number cards
    center_x, center_y = x + width // 2, y + height // 2
    
    if rank in ['J', 'Q', 'K', 'A', '2']:
        # Larger symbol for face cards and 2
        center_font = get_font(36, bold=True)
        center_symbol = center_font.render(suit, True, text_color)
    else:
        # Regular size for number cards
        center_font = get_font(28, bold=True)
        center_symbol = center_font.render(suit, True, text_color)
    
    symbol_rect = center_symbol.get_rect(center=(center_x, center_y))
    surface.blit(center_symbol, symbol_rect)
    
    # Optional: Add subtle corner decorations
    draw_corner_decorations(surface, x, y, width, height, text_color)
    
    return card_rect

def draw_face_card_pattern(surface, center_x, center_y, rank, suit, color, width, height):
    """Draw special patterns for face cards"""
    if rank == 'J':  # Jack
        # Crown symbol for Jack
        crown_points = [
            (center_x - 15, center_y + 5),
            (center_x - 10, center_y - 10),
            (center_x, center_y - 15),
            (center_x + 10, center_y - 10),
            (center_x + 15, center_y + 5),
            (center_x + 10, center_y + 5),
            (center_x + 10, center_y + 10),
            (center_x - 10, center_y + 10),
            (center_x - 10, center_y + 5)
        ]
        pygame.draw.polygon(surface, color, crown_points, 2)
        
        # Draw suit in small size below crown
        suit_font = get_font(16)
        suit_surface = suit_font.render(suit, True, color)
        suit_rect = suit_surface.get_rect(center=(center_x, center_y + 20))
        surface.blit(suit_surface, suit_rect)
        
    elif rank == 'Q':  # Queen
        # Diamond pattern for Queen
        diamond_size = 20
        diamond_points = [
            (center_x, center_y - diamond_size),
            (center_x + diamond_size, center_y),
            (center_x, center_y + diamond_size),
            (center_x - diamond_size, center_y)
        ]
        pygame.draw.polygon(surface, color, diamond_points, 2)
        
        # Small suit in center
        suit_font = get_font(14)
        suit_surface = suit_font.render(suit, True, color)
        suit_rect = suit_surface.get_rect(center=(center_x, center_y))
        surface.blit(suit_surface, suit_rect)
        
    elif rank == 'K':  # King
        # Crossed swords pattern
        # First diagonal
        pygame.draw.line(surface, color, 
                        (center_x - 15, center_y - 15),
                        (center_x + 15, center_y + 15), 3)
        # Second diagonal
        pygame.draw.line(surface, color,
                        (center_x - 15, center_y + 15),
                        (center_x + 15, center_y - 15), 3)
        
        # Suit in center
        suit_font = get_font(16)
        suit_surface = suit_font.render(suit, True, color)
        suit_rect = suit_surface.get_rect(center=(center_x, center_y))
        surface.blit(suit_surface, suit_rect)
        
    elif rank == 'A':  # Ace
        # Large suit with border
        large_suit_font = get_font(40, bold=True)
        suit_surface = large_suit_font.render(suit, True, color)
        suit_rect = suit_surface.get_rect(center=(center_x, center_y))
        
        # Draw outline
        outline_color = (255, 255, 255) if color == BLACK_SUIT_COLOR else (255, 255, 255)
        for dx, dy in [(-1, -1), (-1, 1), (1, -1), (1, 1), (0, -1), (0, 1), (-1, 0), (1, 0)]:
            outline_rect = suit_rect.move(dx * 2, dy * 2)
            outline_surface = large_suit_font.render(suit, True, outline_color)
            surface.blit(outline_surface, outline_rect)
        
        # Draw main suit
        surface.blit(suit_surface, suit_rect)

def draw_corner_decorations(surface, x, y, width, height, color):
    """Draw decorative elements in card corners"""
    # Top-left decorative corner
    corner_size = 8
    corner_points = [
        (x + 5, y + corner_size + 5),
        (x + corner_size + 5, y + 5),
        (x + corner_size + 10, y + 5),
        (x + 5, y + corner_size + 10)
    ]
    pygame.draw.polygon(surface, color, corner_points)
    
    # Bottom-right decorative corner (rotated)
    corner_points = [
        (x + width - 5, y + height - corner_size - 5),
        (x + width - corner_size - 5, y + height - 5),
        (x + width - corner_size - 10, y + height - 5),
        (x + width - 5, y + height - corner_size - 10)
    ]
    pygame.draw.polygon(surface, color, corner_points)

def draw_card(screen, card, x, y, font=None, selected=False, hovered=False, 
             flipped=False, angle=0, scale=1.0, show_shadow=True):
    """
    Main function to draw a card - SIMPLIFIED FIXED VERSION
    
    Parameters:
    - screen: Pygame surface to draw on
    - card: Card object or string representation
    - x, y: Position
    - font: Font for text (optional, will use default if None)
    - selected: Whether card is selected
    - hovered: Whether card is being hovered over
    - flipped: Whether to show card back
    - angle: Rotation angle in degrees
    - scale: Scale factor (1.0 = normal size)
    - show_shadow: Whether to show shadow
    """
    if flipped:
        draw_card_back(screen, x, y, CARD_WIDTH, CARD_HEIGHT)
    else:
        # Get rank and suit using our fixed function
        rank, suit = get_card_rank_suit(card)
        
        # Determine color based on suit - FIXED
        if suit in ['♥', '♦']:
            text_color = RED_SUIT_COLOR  # Red for hearts and diamonds
        else:
            text_color = BLACK_SUIT_COLOR  # Black for spades and clubs
        
        # Draw card background with shadow
        card_rect = pygame.Rect(x, y, CARD_WIDTH, CARD_HEIGHT)
        
        # Shadow
        if show_shadow:
            shadow_rect = pygame.Rect(x + 4, y + 4, CARD_WIDTH, CARD_HEIGHT)
            pygame.draw.rect(screen, (0, 0, 0, 100), shadow_rect, border_radius=10)
        
        # Card background
        pygame.draw.rect(screen, CARD_BACKGROUND, card_rect, border_radius=10)
        
        # Border based on card state
        border_color = CARD_BORDER_SELECTED if selected else \
                       CARD_BORDER_HOVER if hovered else CARD_BORDER_NORMAL
        border_width = 3 if selected or hovered else 2
        pygame.draw.rect(screen, border_color, card_rect, border_width, border_radius=10)
        
        # Use default font if none provided
        if font is None:
            font = get_font(20, bold=True)
        
        # Draw rank and suit
        rank_text = font.render(rank, True, text_color)
        suit_text = font.render(suit, True, text_color)
        
        # Top-left corner
        screen.blit(rank_text, (x + 8, y + 8))
        screen.blit(suit_text, (x + 8, y + 30))
        
        # Bottom-right corner (rotated)
        rank_rotated = pygame.transform.rotate(rank_text, 180)
        suit_rotated = pygame.transform.rotate(suit_text, 180)
        
        screen.blit(rank_rotated, (x + CARD_WIDTH - 28, y + CARD_HEIGHT - 28))
        screen.blit(suit_rotated, (x + CARD_WIDTH - 28, y + CARD_HEIGHT - 50))
        
        # Center symbol - different sizes for different card types
        center_x, center_y = x + CARD_WIDTH // 2, y + CARD_HEIGHT // 2
        
        if rank in ['J', 'Q', 'K', 'A', '2']:
            # Larger for face cards and 2
            center_font = get_font(36, bold=True)
        else:
            # Normal size for number cards
            center_font = get_font(28, bold=True)
        
        center_symbol = center_font.render(suit, True, text_color)
        symbol_rect = center_symbol.get_rect(center=(center_x, center_y))
        screen.blit(center_symbol, symbol_rect)
    
    # Return the card rectangle for collision detection
    return pygame.Rect(x, y, CARD_WIDTH, CARD_HEIGHT)

def draw_hand(screen, hand, start_x, y, font=None, selected_indices=None, 
             hovered_index=None, card_spacing=None, overlap=None):
    """
    Draw a hand of cards
    
    Parameters:
    - screen: Pygame surface
    - hand: List of cards
    - start_x, y: Starting position
    - font: Font for cards
    - selected_indices: List of indices of selected cards
    - hovered_index: Index of hovered card
    - card_spacing: Custom spacing between cards
    - overlap: Overlap amount between cards (for large hands)
    """
    if not hand:
        return []
    
    selected_indices = selected_indices or []
    
    # Calculate spacing
    if card_spacing is None:
        if len(hand) > 10:
            # Overlap cards when hand is large
            if overlap is None:
                overlap = 30
            spacing = CARD_WIDTH - overlap
        else:
            spacing = CARD_WIDTH + 10
    else:
        spacing = card_spacing
    
    card_rects = []
    
    for i, card in enumerate(hand):
        x = start_x + i * spacing
        
        # Lift selected or hovered cards
        y_offset = 0
        if i in selected_indices or i == hovered_index:
            y_offset = -15
        
        selected = i in selected_indices
        hovered = i == hovered_index
        
        card_rect = draw_card(screen, card, x, y + y_offset, font, 
                             selected, hovered, show_shadow=(i == 0 or not selected))
        card_rects.append(card_rect)
    
    return card_rects

def draw_card_stack(screen, cards, x, y, max_visible=3, angle_variation=5):
    """
    Draw a stack of cards (for deck or discard pile)
    
    Parameters:
    - cards: List of cards in stack
    - x, y: Base position
    - max_visible: Maximum number of cards to show
    - angle_variation: Random angle variation for visual effect
    """
    if not cards:
        return
    
    import random
    
    # Show only top few cards
    visible_cards = cards[-max_visible:]
    
    for i, card in enumerate(visible_cards):
        # Slight offset for each card in stack
        offset_x = i * 2
        offset_y = i * 2
        
        # Slight random angle for natural look
        angle = random.uniform(-angle_variation, angle_variation) if i > 0 else 0
        
        # Draw card (top card face up, others face down)
        flipped = i < len(visible_cards) - 1
        draw_card(screen, card, x + offset_x, y + offset_y, 
                 flipped=flipped, angle=angle, show_shadow=(i == 0))

def draw_card_animation(screen, card, start_pos, end_pos, progress, 
                       flipped=False, scale=1.0):
    """
    Draw a card at an intermediate position for animation
    
    Parameters:
    - screen: Pygame surface
    - card: Card to draw
    - start_pos: (x, y) start position
    - end_pos: (x, y) end position
    - progress: Animation progress (0.0 to 1.0)
    - flipped: Whether card is flipped
    - scale: Scale factor
    """
    # Calculate current position
    x = start_pos[0] + (end_pos[0] - start_pos[0]) * progress
    y = start_pos[1] + (end_pos[1] - start_pos[1]) * progress
    
    # Optional: Add arc to animation path
    # height_factor = math.sin(progress * math.pi) * 50
    # y -= height_factor
    
    # Draw card at current position
    return draw_card(screen, card, int(x), int(y), flipped=flipped, scale=scale)

def draw_card_highlight(screen, card_rect, color=(255, 215, 0), width=4):
    """
    Draw a highlight around a card
    
    Parameters:
    - screen: Pygame surface
    - card_rect: Rectangle of the card
    - color: Highlight color
    - width: Highlight line width
    """
    # Draw glowing effect
    for glow_width in range(width, 0, -1):
        glow_color = (*color, 100 // width * glow_width)
        temp_surface = pygame.Surface((card_rect.width + glow_width * 2, 
                                      card_rect.height + glow_width * 2), 
                                      pygame.SRCALPHA)
        pygame.draw.rect(temp_surface, glow_color, 
                        (0, 0, temp_surface.get_width(), temp_surface.get_height()),
                        border_radius=10 + glow_width)
        screen.blit(temp_surface, 
                   (card_rect.x - glow_width, card_rect.y - glow_width))
    
    # Draw main highlight border
    pygame.draw.rect(screen, color, card_rect.inflate(8, 8), 3, border_radius=12)

def draw_card_tooltip(screen, card, x, y, font=None):
    """
    Draw a tooltip with card information
    
    Parameters:
    - screen: Pygame surface
    - card: Card to show tooltip for
    - x, y: Position for tooltip
    - font: Font for tooltip text
    """
    if font is None:
        font = get_font(14)
    
    rank, suit = get_card_rank_suit(card)
    
    # Create tooltip text
    suit_names = {
        '♠': 'Spades',
        '♣': 'Clubs', 
        '♦': 'Diamonds',
        '♥': 'Hearts'
    }
    suit_name = suit_names.get(suit, suit)
    
    # Make the rank more readable
    rank_names = {
        'J': 'Jack',
        'Q': 'Queen',
        'K': 'King',
        'A': 'Ace',
        '2': 'Two'
    }
    display_rank = rank_names.get(rank, rank)
    
    tooltip_text = f"{display_rank} of {suit_name}"
    
    # Render tooltip
    text_surface = font.render(tooltip_text, True, (255, 255, 255))
    bg_rect = text_surface.get_rect()
    bg_rect.inflate_ip(10, 5)
    bg_rect.topleft = (x, y - bg_rect.height - 5)
    
    # Draw tooltip background
    pygame.draw.rect(screen, (0, 0, 0, 200), bg_rect, border_radius=5)
    pygame.draw.rect(screen, (255, 255, 255), bg_rect, 1, border_radius=5)
    
    # Draw text
    screen.blit(text_surface, (bg_rect.x + 5, bg_rect.y + 3))