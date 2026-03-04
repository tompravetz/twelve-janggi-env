import pygame
import sys
import numpy as np
from piece import PieceType, Owner
from game import Game

# ── Layout ────────────────────────────────────────────────────────────────────
SQUARE_SIZE  = 120
COLS         = 3
ROWS         = 4
HAND_WIDTH   = 110
BOARD_OFFSET = HAND_WIDTH
PANEL_HEIGHT = 80
BOARD_W      = COLS * SQUARE_SIZE        # 360
BOARD_H      = ROWS * SQUARE_SIZE        # 480
WIDTH        = HAND_WIDTH + BOARD_W + HAND_WIDTH   # 580
HEIGHT       = BOARD_H + PANEL_HEIGHT              # 560

PIECE_SLOT_H = 80
PIECE_RADIUS = 30

# ── Colors ────────────────────────────────────────────────────────────────────
BLACK        = (20,  20,  20)
WHITE        = (245, 245, 240)
DARK_BG      = (35,  35,  35)
P0_TERR      = (210, 230, 255)
P1_TERR      = (255, 210, 210)
NEUTRAL      = (240, 240, 225)
GRID_LINE    = (80,  80,  80)
HIGHLIGHT    = (255, 220,  50)
SELECT_RIM   = (255, 200,   0)
P0_CIRCLE    = (80,  140, 220)
P1_CIRCLE    = (220,  70,  70)
PANEL_BG     = (25,  25,  25)
PANEL_TEXT   = (180, 180, 180)
HAND_BG      = (45,  45,  45)
HAND_SLOT_HL = (80,  80,  40)
HAND_SLOT    = (55,  55,  55)
RESTART_BTN  = (70,  70,  70)
RESTART_HOV  = (100, 100, 100)
WIN_COLOR    = (255, 220,  80)

SHORT = {
    PieceType.MINISTER:    "Mi",
    PieceType.GENERAL:     "Ge",
    PieceType.KING:        "Ki",
    PieceType.MAN:         "Ma",
    PieceType.FEUDAL_LORD: "FL",
}


# ── Coordinate helpers ────────────────────────────────────────────────────────

def board_to_pixel(row, col):
    px = BOARD_OFFSET + col * SQUARE_SIZE
    py = (3 - row) * SQUARE_SIZE
    return px, py


def pixel_to_board(mouse_x, mouse_y):
    if mouse_y >= BOARD_H:
        return None
    bx = mouse_x - BOARD_OFFSET
    if bx < 0 or bx >= BOARD_W:
        return None
    col = bx // SQUARE_SIZE
    row = 3 - (mouse_y // SQUARE_SIZE)
    if 0 <= row <= 3 and 0 <= col <= 2:
        return row, col
    return None


# ── Drawing ───────────────────────────────────────────────────────────────────

def draw_hand_column(screen, board, owner, font, selected_hand):
    """Draw side panel for one player's captured pieces.
    Returns list of (rect, piece_type, index) for click detection."""
    hand = board.hands[owner]
    x    = BOARD_OFFSET + BOARD_W if owner == Owner.P0 else 0

    pygame.draw.rect(screen, HAND_BG, (x, 0, HAND_WIDTH, BOARD_H))

    label_color = P0_CIRCLE if owner == Owner.P0 else P1_CIRCLE
    lbl = font.render("P0" if owner == Owner.P0 else "P1", True, label_color)
    screen.blit(lbl, lbl.get_rect(centerx=x + HAND_WIDTH // 2, y=6))

    slots = []
    for i, piece_type in enumerate(hand):
        slot_y   = 36 + i * PIECE_SLOT_H
        rect     = pygame.Rect(x + 8, slot_y, HAND_WIDTH - 16, PIECE_SLOT_H - 8)
        is_sel   = (selected_hand is not None and
                    selected_hand[0] == owner and
                    selected_hand[1] == i)
        bg_color = HAND_SLOT_HL if is_sel else HAND_SLOT
        pygame.draw.rect(screen, bg_color, rect, border_radius=8)
        if is_sel:
            pygame.draw.rect(screen, SELECT_RIM, rect, 2, border_radius=8)

        cx = x + HAND_WIDTH // 2
        cy = slot_y + PIECE_SLOT_H // 2 - 4
        color = P0_CIRCLE if owner == Owner.P0 else P1_CIRCLE
        pygame.draw.circle(screen, color, (cx, cy), PIECE_RADIUS)
        pygame.draw.circle(screen, BLACK, (cx, cy), PIECE_RADIUS, 2)

        piece_lbl = font.render(SHORT[piece_type], True, WHITE)
        screen.blit(piece_lbl, piece_lbl.get_rect(center=(cx, cy)))

        slots.append((rect, piece_type, i))
    return slots


def draw_board(screen):
    for row in range(4):
        for col in range(3):
            px, py = board_to_pixel(row, col)
            color  = P0_TERR if row == 0 else (P1_TERR if row == 3 else NEUTRAL)
            pygame.draw.rect(screen, color,     (px, py, SQUARE_SIZE, SQUARE_SIZE))
            pygame.draw.rect(screen, GRID_LINE, (px, py, SQUARE_SIZE, SQUARE_SIZE), 1)


def draw_highlights(screen, legal_moves, selected_board):
    if selected_board:
        px, py = board_to_pixel(*selected_board)
        cx = px + SQUARE_SIZE // 2
        cy = py + SQUARE_SIZE // 2
        pygame.draw.circle(screen, SELECT_RIM, (cx, cy), 52, 4)
    for (r, c) in legal_moves:
        px, py = board_to_pixel(r, c)
        cx = px + SQUARE_SIZE // 2
        cy = py + SQUARE_SIZE // 2
        pygame.draw.circle(screen, HIGHLIGHT, (cx, cy), 18)


def draw_pieces(screen, board, font):
    for row in range(4):
        for col in range(3):
            cell = board.grid[row][col]
            if cell is None:
                continue
            px, py = board_to_pixel(row, col)
            cx = px + SQUARE_SIZE // 2
            cy = py + SQUARE_SIZE // 2
            color = P0_CIRCLE if cell.owner == Owner.P0 else P1_CIRCLE
            pygame.draw.circle(screen, color, (cx, cy), 44)
            pygame.draw.circle(screen, BLACK, (cx, cy), 44, 2)
            lbl = font.render(SHORT[cell.piece_type], True, WHITE)
            screen.blit(lbl, lbl.get_rect(center=(cx, cy)))


def draw_panel(screen, game, font_sm, human_owner, mouse_pos):
    pygame.draw.rect(screen, PANEL_BG, (0, BOARD_H, WIDTH, PANEL_HEIGHT))

    if game.winner is not None:
        msg = "You win! 🎉" if game.winner == human_owner else "Agent wins."
        surf = font_sm.render(msg, True, WIN_COLOR)
        screen.blit(surf, surf.get_rect(centerx=WIDTH // 2 - 40,
                                        centery=BOARD_H + PANEL_HEIGHT // 2))
    else:
        turn = "YOUR turn" if game.current_player == human_owner else "Agent thinking..."
        screen.blit(font_sm.render(turn, True, PANEL_TEXT),
                    (HAND_WIDTH + 10, BOARD_H + 12))

        for owner, prefix, y_off in [(Owner.P0, "You", 34), (Owner.P1, "Opp", 54)]:
            hand = game.board.hands[owner]
            s    = prefix + ": " + (", ".join(p.value for p in hand) if hand else "—")
            screen.blit(font_sm.render(s, True, PANEL_TEXT), (HAND_WIDTH + 10, BOARD_H + y_off))

    # Restart button
    btn = pygame.Rect(WIDTH - 92, BOARD_H + PANEL_HEIGHT // 2 - 16, 80, 32)
    pygame.draw.rect(screen, RESTART_HOV if btn.collidepoint(mouse_pos) else RESTART_BTN,
                     btn, border_radius=6)
    pygame.draw.rect(screen, GRID_LINE, btn, 1, border_radius=6)
    screen.blit(font_sm.render("Restart", True, WHITE), font_sm.render("Restart", True, WHITE)
                .get_rect(center=btn.center))
    return btn


# ── Human play mode ───────────────────────────────────────────────────────────

def human_play(human_owner=Owner.P0):
    pygame.init()
    screen  = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Twelve Janggi")
    font    = pygame.font.SysFont("Segoe UI", 24, bold=True)
    font_sm = pygame.font.SysFont("Segoe UI", 17)
    clock   = pygame.time.Clock()

    game = Game()

    selected_board = None   # (row, col)
    selected_hand  = None   # (owner, hand_index)
    legal_moves    = []

    def clear_selection():
        nonlocal selected_board, selected_hand, legal_moves
        selected_board = None
        selected_hand  = None
        legal_moves    = []

    while True:
        mouse_pos = pygame.mouse.get_pos()

        # Agent turn
        if game.winner is None and game.current_player != human_owner:
            pygame.time.wait(250)
            actions = game.get_all_legal_actions()
            if actions:
                game.step(actions[np.random.randint(len(actions))])
            clear_selection()

        # Draw
        screen.fill(DARK_BG)
        draw_board(screen)
        draw_highlights(screen, legal_moves, selected_board)
        draw_pieces(screen, game.board, font)
        p0_slots = draw_hand_column(screen, game.board, Owner.P0, font, selected_hand)
        p1_slots = draw_hand_column(screen, game.board, Owner.P1, font, selected_hand)
        btn_rect  = draw_panel(screen, game, font_sm, human_owner, mouse_pos)
        pygame.display.flip()
        clock.tick(60)

        # Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    game = Game()
                    clear_selection()

            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos

                # Restart button
                if btn_rect.collidepoint(mx, my):
                    game = Game()
                    clear_selection()
                    continue

                if game.winner is not None or game.current_player != human_owner:
                    continue

                # Click on board
                coords = pixel_to_board(mx, my)
                if coords is not None:
                    row, col = coords

                    if selected_hand is not None:
                        # Try to drop hand piece here
                        piece_type = game.board.hands[human_owner][selected_hand[1]]
                        if (row, col) in legal_moves:
                            game.step(("drop", piece_type, row, col))
                        clear_selection()

                    elif selected_board is not None:
                        if (row, col) == selected_board:
                            # Same piece clicked — deselect
                            clear_selection()
                        elif (row, col) in legal_moves:
                            game.step(("move", selected_board[0], selected_board[1], row, col))
                            clear_selection()
                        else:
                            # Reselect another friendly piece or deselect
                            cell = game.board.grid[row][col]
                            if cell is not None and cell.owner == human_owner:
                                selected_board = (row, col)
                                legal_moves    = game.board.get_legal_moves(row, col)
                                selected_hand  = None
                            else:
                                clear_selection()
                    else:
                        cell = game.board.grid[row][col]
                        if cell is not None and cell.owner == human_owner:
                            selected_board = (row, col)
                            legal_moves    = game.board.get_legal_moves(row, col)
                    continue

                # Click on human's hand column
                my_slots = p0_slots if human_owner == Owner.P0 else p1_slots
                for rect, piece_type, idx in my_slots:
                    if rect.collidepoint(mx, my):
                        if (selected_hand is not None and
                                selected_hand[0] == human_owner and
                                selected_hand[1] == idx):
                            clear_selection()   # toggle off
                        else:
                            selected_hand  = (human_owner, idx)
                            selected_board = None
                            drops = game.board.get_legal_drops(human_owner)
                            legal_moves = [(r, c) for r, c, pt in drops
                                          if pt == piece_type]
                        break


# ── Watch mode ────────────────────────────────────────────────────────────────

def watch_random(delay_ms=500):
    pygame.init()
    screen  = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Twelve Janggi — Random vs Random")
    font    = pygame.font.SysFont("Segoe UI", 24, bold=True)
    font_sm = pygame.font.SysFont("Segoe UI", 17)
    clock   = pygame.time.Clock()

    game      = Game()
    last_step = pygame.time.get_ticks()

    while True:
        now       = pygame.time.get_ticks()
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    game = Game()
                if event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                btn = pygame.Rect(WIDTH - 92, BOARD_H + PANEL_HEIGHT // 2 - 16, 80, 32)
                if btn.collidepoint(event.pos):
                    game = Game()

        if game.winner is None and now - last_step > delay_ms:
            actions = game.get_all_legal_actions()
            if actions:
                game.step(actions[np.random.randint(len(actions))])
            last_step = now

        screen.fill(DARK_BG)
        draw_board(screen)
        draw_pieces(screen, game.board, font)
        draw_hand_column(screen, game.board, Owner.P0, font, None)
        draw_hand_column(screen, game.board, Owner.P1, font, None)
        draw_panel(screen, game, font_sm, Owner.P0, mouse_pos)
        pygame.display.flip()
        clock.tick(60)


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "play"
    if mode == "watch":
        watch_random()
    else:
        human_play()