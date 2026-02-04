import pygame
import sys
from core.game import Game
from gui.renderer import draw_card
from core.rules import is_valid_play, beats

pygame.init()

# -------------------- CONFIG --------------------
WIDTH, HEIGHT = 1100, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tiến Lên Miền Nam")
clock = pygame.time.Clock()
FONT = pygame.font.SysFont("arial", 20)

CARD_WIDTH = 60
CARD_HEIGHT = 90
CARD_GAP = 10

BUTTON_WIDTH = 100
BUTTON_HEIGHT = 40

HAND_Y = HEIGHT - CARD_HEIGHT - 80  # move hand up for buttons

BACKGROUND = (34, 139, 34)
CARD_COLOR = (245, 245, 245)
CARD_BORDER = (0, 0, 0)
SELECTED_BORDER = (255, 0, 0)
TEXT_COLOR = (0, 0, 0)
BUTTON_COLOR = (200, 200, 200)
BUTTON_HOVER = (170, 170, 170)

# -------------------- INIT GAME --------------------
game = Game()
selected_indexes = []

current_player = 0  # 0 = human, 1-3 = bots
winner_of_current_round = None  # tracks who will start next round
is_new_round = True  # Track if we're starting a new round

# Button rectangles
play_button_rect = pygame.Rect(WIDTH - 230, HEIGHT - 60, BUTTON_WIDTH, BUTTON_HEIGHT)
pass_button_rect = pygame.Rect(WIDTH - 110, HEIGHT - 60, BUTTON_WIDTH, BUTTON_HEIGHT)

# -------------------- HELPER FUNCTIONS --------------------

def draw_hand(player):
    start_x = 50
    y = HAND_Y
    for i, card in enumerate(player.hand):
        x = start_x + i * (CARD_WIDTH + CARD_GAP)
        rect = pygame.Rect(x, y, CARD_WIDTH, CARD_HEIGHT)
        pygame.draw.rect(screen, CARD_COLOR, rect, border_radius=8)
        border_color = SELECTED_BORDER if i in selected_indexes else CARD_BORDER
        pygame.draw.rect(screen, border_color, rect, 3, border_radius=8)
        text = FONT.render(str(card), True, TEXT_COLOR)
        screen.blit(text, (x + 5, y + 5))


def draw_table():
    table_y = 100
    table_x = 50
    if game.last_play:
        for i, card in enumerate(game.last_play):
            draw_card(screen, card, table_x + i * (CARD_WIDTH + 10), table_y, FONT)
    else:
        text = FONT.render("Table is empty", True, (255, 255, 255))
        screen.blit(text, (50, table_y))


def draw_buttons():
    mouse_pos = pygame.mouse.get_pos()
    # Play
    color = BUTTON_HOVER if play_button_rect.collidepoint(mouse_pos) else BUTTON_COLOR
    pygame.draw.rect(screen, color, play_button_rect)
    screen.blit(FONT.render("Play", True, TEXT_COLOR), (play_button_rect.x + 20, play_button_rect.y + 10))
    # Pass
    color = BUTTON_HOVER if pass_button_rect.collidepoint(mouse_pos) else BUTTON_COLOR
    pygame.draw.rect(screen, color, pass_button_rect)
    screen.blit(FONT.render("Pass", True, TEXT_COLOR), (pass_button_rect.x + 20, pass_button_rect.y + 10))


def get_card_index_at_pos(pos, player):
    start_x = 50
    y = HAND_Y
    for i, card in enumerate(player.hand):
        x = start_x + i * (CARD_WIDTH + CARD_GAP)
        rect = pygame.Rect(x, y, CARD_WIDTH, CARD_HEIGHT)
        if rect.collidepoint(pos):
            return i
    return None


def bot_play(bot):
    global winner_of_current_round, is_new_round
    
    # If it's a new round, clear the table so bot can play anything
    temp_last_play = game.last_play
    if is_new_round and winner_of_current_round == current_player:
        game.last_play = []
    
    play = game.bot_turn(bot)
    
    # Restore last_play if we modified it
    if is_new_round and winner_of_current_round == current_player:
        game.last_play = temp_last_play
    
    if play:
        print(f"{bot.name} plays: {' '.join(map(str, play))}")
        # Update winner_of_current_round and clear new round flag
        winner_of_current_round = current_player
        is_new_round = False
        game.last_play = play
        game.pass_count = 0
        return True  # Return True if bot played successfully
    else:
        print(f"{bot.name} passes")
        game.pass_count += 1
        return False  # Return False if bot passed


def next_player():
    global current_player
    current_player = (current_player + 1) % 4


# -------------------- MAIN LOOP --------------------

running = True
while running:
    clock.tick(60)
    screen.fill(BACKGROUND)
    draw_table()
    draw_hand(game.players[0])
    draw_buttons()

    # -------------------- HUMAN INPUT --------------------
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if current_player == 0:
                # Play button
                if play_button_rect.collidepoint(event.pos):
                    if selected_indexes:
                        selected_cards = [game.players[0].hand[i] for i in selected_indexes]

                        # Validate move based on whether it's a new round
                        if is_new_round:
                            # New round: can play any valid combination
                            if not is_valid_play(selected_cards):
                                print("Invalid combination!")
                                continue
                        else:
                            # Normal play: must beat current table
                            if not game.last_play or not is_valid_play(selected_cards) or not beats(selected_cards, game.last_play):
                                print("Invalid move!")
                                continue

                        # Execute move
                        for card in selected_cards:
                            game.players[0].hand.remove(card)
                        
                        # Update game state
                        winner_of_current_round = 0
                        is_new_round = False
                        game.last_play = selected_cards
                        game.pass_count = 0
                        selected_indexes.clear()

                        # Check win
                        if game.players[0].has_won():
                            print("You win!")
                            running = False
                        else:
                            next_player()

                # Pass button
                elif pass_button_rect.collidepoint(event.pos):
                    print("You pass")
                    game.pass_count += 1
                    selected_indexes.clear()
                    
                    # Check if all others passed
                    if game.pass_count == len(game.players) - 1:
                        print("All passed. New round!")
                        game.last_play = []
                        game.pass_count = 0
                        is_new_round = True
                        # winner_of_current_round starts next round
                        current_player = winner_of_current_round
                        if current_player != 0:  # If bot's turn, let them play immediately
                            continue
                    else:
                        next_player()

                # Click card to select/deselect
                else:
                    idx = get_card_index_at_pos(event.pos, game.players[0])
                    if idx is not None:
                        if idx in selected_indexes:
                            selected_indexes.remove(idx)
                        else:
                            selected_indexes.append(idx)

    # -------------------- BOT TURN --------------------
    while current_player != 0 and running:
        bot = game.players[current_player]
        bot_played = bot_play(bot)
        
        # Check win
        if bot.has_won():
            print(f"{bot.name} wins!")
            running = False
            break

        # Check if all others passed
        if game.pass_count == len(game.players) - 1:
            print("All passed. New round!")
            game.last_play = []
            game.pass_count = 0
            is_new_round = True
            # winner_of_current_round starts next round
            current_player = winner_of_current_round
            if current_player == 0:  # human starts new round
                break
        else:
            # Move to next player
            next_player()
            # If next player is the winner_of_current_round in a new round,
            # they should be able to play anything
            if is_new_round and current_player == winner_of_current_round:
                continue
            elif current_player == 0:
                break  # Human's turn, exit bot loop

    pygame.display.flip()

pygame.quit()
sys.exit()