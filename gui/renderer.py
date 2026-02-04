import pygame

CARD_WIDTH = 60
CARD_HEIGHT = 90
CARD_COLOR = (245, 245, 245)
CARD_BORDER = (0, 0, 0)
TEXT_COLOR = (0, 0, 0)


def draw_card(screen, card, x, y, font):
    rect = pygame.Rect(x, y, CARD_WIDTH, CARD_HEIGHT)
    pygame.draw.rect(screen, CARD_COLOR, rect, border_radius=8)
    pygame.draw.rect(screen, CARD_BORDER, rect, 2, border_radius=8)

    text = font.render(str(card), True, TEXT_COLOR)
    screen.blit(text, (x + 8, y + 8))


def draw_hand(screen, hand, start_x, y, font):
    for i, card in enumerate(hand):
        x = start_x + i * (CARD_WIDTH + 10)
        draw_card(screen, card, x, y, font)
