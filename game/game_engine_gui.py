from game.board import Board
from game.player import Player
from game.input_box import InputBox
import pygame
import sys
import random
import pygame.gfxdraw
from game.particles import ParticleManager

import random
import pygame.gfxdraw
from game.particles import ParticleManager
from game.constants import (
    GRID_ROWS, GRID_COLS, DOT_RADIUS, LINE_WIDTH, COLOR_BACKGROUND, COLOR_DOT, COLOR_LINE,
    COLOR_HIGHLIGHT, COLOR_PLAYER1, COLOR_PLAYER2, CAT_FRAME_DELAY, PARTICLE_NUM_LINE, PARTICLE_SPREAD_LINE,
    PARTICLE_SPEED_MIN_LINE, PARTICLE_SPEED_MAX_LINE, PARTICLE_SIZE_MIN_LINE, PARTICLE_SIZE_MAX_LINE,
    PARTICLE_LIFETIME_MIN_LINE, PARTICLE_LIFETIME_MAX_LINE, PARTICLE_NUM_BOX, PARTICLE_SPREAD_BOX,
    PARTICLE_SPEED_MIN_BOX, PARTICLE_SPEED_MAX_BOX, PARTICLE_SIZE_MIN_BOX, PARTICLE_SIZE_MAX_BOX,
    PARTICLE_LIFETIME_MIN_BOX, PARTICLE_LIFETIME_MAX_BOX
)

SPACING_X = 0
SPACING_Y = 0
dot_positions = []  # List of (x, y, row, col) tuples
board = Board(GRID_ROWS, GRID_COLS)
particle_manager = ParticleManager()  # Global particle manager
cat_state = {}


# ===Methods===-> FUNCTIONING
def calculate_spacing_between_dots(width, height):
    # Calculate spacing between dots
    global SPACING_X, SPACING_Y
    SPACING_X = width // GRID_COLS
    SPACING_Y = height // GRID_ROWS


def store_coordinates_of_dots():
    # Storing the coordinates of dots, to manage mouse clicks and draw lines
    global dot_positions
    dot_positions = []  # Re-initialize the list
    for row in range(GRID_ROWS):
        for col in range(GRID_COLS):
            x = col * SPACING_X + SPACING_X // 2
            y = row * SPACING_Y + SPACING_Y // 2
            dot_positions.append((x, y, row, col))  # For click detection


def set_cat_state(window_width, sidebar_width):
    global cat_state
    cat_state = {
        "frame_idx": 0,
        "timer": 0,
        "frame_delay": 10,  # Adjust this to make animation slower
        "x": window_width - sidebar_width - 120,
        "direction": 1
    }


def draw_sidebar(screen, players, current_player_idx, music_on, sidebar_width, cat_frames):
    global cat_state
    sidebar_x = screen.get_width() - sidebar_width
    pygame.draw.rect(screen, (30, 80, 90), (sidebar_x, 0, sidebar_width, screen.get_height()))

    font_heading = pygame.font.SysFont(None, 35)
    font = pygame.font.SysFont(None, 30)
    score_heading_surf = font_heading.render("Score:", True, (240, 255, 50))
    screen.blit(score_heading_surf, (sidebar_x + 20, 20))

    y = 70
    box_width = sidebar_width - 40
    box_height = 50

    # === SCORE BOXES ===
    for idx, player in enumerate(players):
        bg_color = (60, 100, 110)
        border_color = (0, 120, 200) if idx == current_player_idx else (100, 100, 100)
        text_color = (240, 255, 50) if idx != current_player_idx else (255, 255, 255)

        box_rect = pygame.Rect(sidebar_x + 20, y, box_width, box_height)
        pygame.draw.rect(screen, bg_color, box_rect, border_radius=8)
        pygame.draw.rect(screen, border_color, box_rect, 3, border_radius=8)

        text = f"{player.name} : {player.score}"
        text_surf = font.render(text, True, text_color)
        screen.blit(text_surf, (box_rect.x + 15, box_rect.y + 15))
        y += box_height + 15

    # === ANIMATED CAT ===
    if cat_frames:
        cat_state["timer"] += 1
        if cat_state["timer"] >= cat_state["frame_delay"]:
            cat_state["timer"] = 0
            cat_state["frame_idx"] = (cat_state["frame_idx"] + 1) % 3

        cat_state["x"] += cat_state["direction"] * 1
        if cat_state["x"] < sidebar_x + 20 or cat_state["x"] > sidebar_x + sidebar_width - cat_frames[
            0].get_width() - 20:
            cat_state["direction"] *= -1

        cat_img = cat_frames[cat_state["frame_idx"]]
        screen.blit(cat_img, (cat_state["x"], y + 10))
        y += cat_img.get_height() + 40

    # === MUSIC TOGGLE BUTTON ===
    if music_on:
        cat_state["frame_delay"] = 10
        music_bg = (100, 200, 150)
        music_text_color = (0, 0, 0)
        music_label = "Music: ON"
    else:
        cat_state["frame_delay"] = float("inf")
        music_bg = (180, 180, 180)
        music_text_color = (120, 120, 120)
        music_label = "Music: OFF"

    music_button = pygame.Rect(sidebar_x + 40, screen.get_height() - 140, 170, 40)
    pygame.draw.rect(screen, music_bg, music_button, border_radius=20)
    pygame.draw.rect(screen, (70, 70, 70), music_button, 2, border_radius=20)

    music_surf = font.render(music_label, True, music_text_color)
    music_text_rect = music_surf.get_rect(center=music_button.center)
    screen.blit(music_surf, music_text_rect)

    # === RESTART & QUIT BUTTONS ===
    button_y = screen.get_height() - 80
    button_width = 80
    button_height = 40
    spacing = 10

    restart_button = pygame.Rect(sidebar_x + 40, button_y, button_width, button_height)
    quit_button = pygame.Rect(sidebar_x + 40 + button_width + spacing, button_y, button_width, button_height)

    pygame.draw.rect(screen, (0, 200, 200), restart_button, border_radius=10)
    pygame.draw.rect(screen, (200, 50, 50), quit_button, border_radius=10)

    restart_text = font.render("Restart", True, (255, 255, 255))
    quit_text = font.render("Quit", True, (255, 255, 255))

    screen.blit(restart_text, restart_text.get_rect(center=restart_button.center))
    screen.blit(quit_text, quit_text.get_rect(center=quit_button.center))

    return music_button, restart_button, quit_button


def confirm_dialog(screen, prompt, click_sound):
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 36)

    # Dimmed background
    overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))

    # Dialog box
    dialog_rect = pygame.Rect(250, 200, 400, 200)
    pygame.draw.rect(screen, (255, 255, 255), dialog_rect, border_radius=10)
    pygame.draw.rect(screen, (100, 100, 100), dialog_rect, 2, border_radius=10)

    # Text
    message = font.render(prompt, True, (0, 0, 0))
    screen.blit(message, (dialog_rect.x + 40, dialog_rect.y + 40))

    # Yes and No buttons
    yes_button = pygame.Rect(dialog_rect.x + 60, dialog_rect.y + 120, 100, 40)
    no_button = pygame.Rect(dialog_rect.x + 240, dialog_rect.y + 120, 100, 40)

    pygame.draw.rect(screen, (200, 50, 50), yes_button, border_radius=6)
    pygame.draw.rect(screen, (50, 200, 50), no_button, border_radius=6)

    screen.blit(font.render("Yes", True, (255, 255, 255)), yes_button.move(30, 5))
    screen.blit(font.render("No", True, (255, 255, 255)), no_button.move(35, 5))

    pygame.display.flip()

    # Wait for user response
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return True  # allow quit via close button
            elif event.type == pygame.MOUSEBUTTONDOWN:
                click_sound.play()
                if yes_button.collidepoint(event.pos):
                    return True
                elif no_button.collidepoint(event.pos):
                    return False

        clock.tick(60)


def draw_dots(screen):
    # Draw dots with anti-aliasing
    for row in range(GRID_ROWS):
        for col in range(GRID_COLS):
            x = col * SPACING_X + SPACING_X // 2
            y = row * SPACING_Y + SPACING_Y // 2
            pygame.gfxdraw.aacircle(screen, x, y, DOT_RADIUS, COLOR_DOT)
            pygame.gfxdraw.filled_circle(screen, x, y, DOT_RADIUS, COLOR_DOT)


def draw_h_line(screen, last_move):
    # Draw horizontal lines
    for row in range(GRID_ROWS):
        for col in range(GRID_COLS - 1):
            if board.h_lines[row][col]:
                x1 = col * SPACING_X + SPACING_X // 2
                y1 = row * SPACING_Y + SPACING_Y // 2
                x2 = (col + 1) * SPACING_X + SPACING_X // 2
                y2 = y1
                if (row, col, 'H') == last_move:
                    pygame.gfxdraw.hline(screen, x1 + 5, x2 - 5, y1, COLOR_HIGHLIGHT)
                    pygame.gfxdraw.hline(screen, x1 + 5, x2 - 5, y1 + 1, COLOR_HIGHLIGHT)
                    pygame.gfxdraw.hline(screen, x1 + 5, x2 - 5, y1 - 1, COLOR_HIGHLIGHT)
                else:
                    pygame.gfxdraw.hline(screen, x1 + 5, x2 - 5, y1, COLOR_LINE)
                    pygame.gfxdraw.hline(screen, x1 + 5, x2 - 5, y1 + 1, COLOR_LINE)
                    pygame.gfxdraw.hline(screen, x1 + 5, x2 - 5, y1 - 1, COLOR_LINE)


def draw_v_line(screen, last_move):
    for row in range(GRID_ROWS - 1):
        for col in range(GRID_COLS):
            if board.v_lines[row][col]:
                x1 = col * SPACING_X + SPACING_X // 2
                y1 = row * SPACING_Y + SPACING_Y // 2
                x2 = x1
                y2 = (row + 1) * SPACING_Y + SPACING_Y // 2
                if (row, col, 'V') == last_move:
                    pygame.gfxdraw.vline(screen, x1, y1 + 5, y2 - 5, COLOR_HIGHLIGHT)
                    pygame.gfxdraw.vline(screen, x1 + 1, y1 + 5, y2 - 5, COLOR_HIGHLIGHT)
                    pygame.gfxdraw.vline(screen, x1 - 1, y1 + 5, y2 - 5, COLOR_HIGHLIGHT)
                else:
                    pygame.gfxdraw.vline(screen, x1, y1 + 5, y2 - 5, COLOR_LINE)
                    pygame.gfxdraw.vline(screen, x1 + 1, y1 + 5, y2 - 5, COLOR_LINE)
                    pygame.gfxdraw.vline(screen, x1 - 1, y1 + 5, y2 - 5, COLOR_LINE)


def draw_acquired_boxes(screen, pl):
    for r in range(GRID_ROWS - 1):
        for c in range(GRID_COLS - 1):
            symbol = board.boxes[r][c]
            if symbol:
                player = pl[0] if pl[0].symbol == symbol else pl[1]
                x = c * SPACING_X + SPACING_X // 2
                y = r * SPACING_Y + SPACING_Y // 2
                rect = pygame.Rect(x + DOT_RADIUS, y + DOT_RADIUS,
                                   SPACING_X - DOT_RADIUS * 2, SPACING_Y - DOT_RADIUS * 2)
                # Draw semi-transparent filled rectangle
                s = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)  # per-pixel alpha
                s.fill((player.color[0], player.color[1], player.color[2], 100))  # 100 alpha value
                screen.blit(s, (rect.x, rect.y))
                # Draw border
                pygame.draw.rect(screen, player.color, rect, 2)


def check_game_over(game_over, players):
    winner_text = ""
    flag = game_over
    if board.is_full():
        print("Yes it is full")
        flag = True
        if players[0].score > players[1].score:
            winner_text = f"{players[0].name} won!"
        elif players[1].score > players[0].score:
            winner_text = f"{players[1].name} won!"
        else:
            winner_text = "It's a draw!"
    return flag, winner_text


def detect_clicked_line(mx, my, click_sound):
    tolerance = 10  # vertical/horizontal "thickness"
    margin_from_dot = 15  # prevent near-dot clicks

    # Horizontal lines
    for r in range(GRID_ROWS):
        for c in range(GRID_COLS - 1):
            x1 = c * SPACING_X + SPACING_X // 2
            x2 = (c + 1) * SPACING_X + SPACING_X // 2
            y = r * SPACING_Y + SPACING_Y // 2

            allowed_x1 = x1 + margin_from_dot
            allowed_x2 = x2 - margin_from_dot
            width = allowed_x2 - allowed_x1

            rect = pygame.Rect(allowed_x1, y - tolerance, width, 2 * tolerance)
            if rect.collidepoint(mx, my) and not board.h_lines[r][c]:
                click_sound.play()
                return "h", r, c

    # Vertical lines
    for r in range(GRID_ROWS - 1):
        for c in range(GRID_COLS):
            x = c * SPACING_X + SPACING_X // 2
            y1 = r * SPACING_Y + SPACING_Y // 2
            y2 = (r + 1) * SPACING_Y + SPACING_Y // 2

            allowed_y1 = y1 + margin_from_dot
            allowed_y2 = y2 - margin_from_dot
            height = allowed_y2 - allowed_y1

            rect = pygame.Rect(x - tolerance, allowed_y1, 2 * tolerance, height)
            if rect.collidepoint(mx, my) and not board.v_lines[r][c]:
                click_sound.play()
                return "v", r, c

    return None  # No valid line clicked


def detect_hovered_line(mx, my):
    tolerance = 8
    margin_from_dot = 15

    # Horizontal lines
    for r in range(GRID_ROWS):
        for c in range(GRID_COLS - 1):
            x1 = c * SPACING_X + SPACING_X // 2
            x2 = (c + 1) * SPACING_X + SPACING_X // 2
            y = r * SPACING_Y + SPACING_Y // 2

            allowed_x1 = x1 + margin_from_dot
            allowed_x2 = x2 - margin_from_dot
            width = allowed_x2 - allowed_x1

            rect = pygame.Rect(allowed_x1, y - tolerance, width, 2 * tolerance)
            if rect.collidepoint(mx, my) and not board.h_lines[r][c]:
                return "h", r, c

    # Vertical lines
    for r in range(GRID_ROWS - 1):
        for c in range(GRID_COLS):
            x = c * SPACING_X + SPACING_X // 2
            y1 = r * SPACING_Y + SPACING_Y // 2
            y2 = (r + 1) * SPACING_Y + SPACING_Y // 2

            allowed_y1 = y1 + margin_from_dot
            allowed_y2 = y2 - margin_from_dot
            height = allowed_y2 - allowed_y1

            rect = pygame.Rect(x - tolerance, allowed_y1, 2 * tolerance, height)
            if rect.collidepoint(mx, my) and not board.v_lines[r][c]:
                return "v", r, c

    return None


def draw_hover_highlight(screen, line_info):
    if not line_info:
        return

    kind, r, c = line_info
    color = COLOR_HIGHLIGHT  # Use the new highlight color
    thickness = 3

    if kind == "h":
        x1 = c * SPACING_X + SPACING_X // 2
        y1 = r * SPACING_Y + SPACING_Y // 2
        x2 = (c + 1) * SPACING_X + SPACING_X // 2
        y2 = y1
        pygame.gfxdraw.hline(screen, x1 + 5, x2 - 5, y1, color)
        pygame.gfxdraw.hline(screen, x1 + 5, x2 - 5, y1 + 1, color)
        pygame.gfxdraw.hline(screen, x1 + 5, x2 - 5, y1 - 1, color)

    elif kind == "v":
        x1 = c * SPACING_X + SPACING_X // 2
        y1 = r * SPACING_Y + SPACING_Y // 2
        x2 = x1
        y2 = (r + 1) * SPACING_Y + SPACING_Y // 2
        pygame.gfxdraw.vline(screen, x1, y1 + 5, y2 - 5, color)
        pygame.gfxdraw.vline(screen, x1 + 1, y1 + 5, y2 - 5, color)
        pygame.gfxdraw.vline(screen, x1 - 1, y1 + 5, y2 - 5, color)


def handle_events(screen, selected_dot, current_player_idx, players, click_sound, box_sound):
    # print("Current Player IDX: ", current_player_idx, players[current_player_idx].name)
    mx, my = pygame.mouse.get_pos()
    last_move = None
    # ===Checking clicks between lines===
    line_result = detect_clicked_line(mx, my, click_sound)
    if line_result:
        typ, r, c = line_result
        player = players[current_player_idx]
        if typ == "h":
            board.draw_horizontal(r, c, player)
            last_move = (r, c, 'H')
            particle_manager.create_explosion(mx, my, COLOR_LINE, num_particles=PARTICLE_NUM_LINE,
                                              spread=PARTICLE_SPREAD_LINE, speed_min=PARTICLE_SPEED_MIN_LINE,
                                              speed_max=PARTICLE_SPEED_MAX_LINE, size_min=PARTICLE_SIZE_MIN_LINE,
                                              size_max=PARTICLE_SIZE_MAX_LINE, lifetime_min=PARTICLE_LIFETIME_MIN_LINE,
                                              lifetime_max=PARTICLE_LIFETIME_MAX_LINE)  # Particle effect for line draw
        elif typ == "v":
            board.draw_vertical(r, c, player)
            last_move = (r, c, 'V')
            particle_manager.create_explosion(mx, my, COLOR_LINE, num_particles=PARTICLE_NUM_LINE,
                                              spread=PARTICLE_SPREAD_LINE, speed_min=PARTICLE_SPEED_MIN_LINE,
                                              speed_max=PARTICLE_SPEED_MAX_LINE, size_min=PARTICLE_SIZE_MIN_LINE,
                                              size_max=PARTICLE_SIZE_MAX_LINE, lifetime_min=PARTICLE_LIFETIME_MIN_LINE,
                                              lifetime_max=PARTICLE_LIFETIME_MAX_LINE)  # Particle effect for line draw

        box_made = board.check_boxes(player)
        if box_made:
            box_sound.play()
            # Particle effect for box completion
            particle_manager.create_explosion(mx, my, player.color, num_particles=PARTICLE_NUM_BOX,
                                              spread=PARTICLE_SPREAD_BOX, speed_min=PARTICLE_SPEED_MIN_BOX,
                                              speed_max=PARTICLE_SPEED_MAX_BOX, size_min=PARTICLE_SIZE_MIN_BOX,
                                              size_max=PARTICLE_SIZE_MAX_BOX, lifetime_min=PARTICLE_LIFETIME_MIN_BOX,
                                              lifetime_max=PARTICLE_LIFETIME_MAX_BOX)
        if not box_made:
            current_player_idx = (current_player_idx + 1) % 2
        return None, current_player_idx, last_move
    # === if not the above case, checking click on dots===
    for (x, y, row, col) in dot_positions:
        if (x - mx) ** 2 + (y - my) ** 2 <= (DOT_RADIUS + 8) ** 2:  # --> If clicked a dot
            print(f"Clicked on dot ({row}, {col})")
            # You clicked on dot, let's see if it was first or second
            if selected_dot is None:  # -> It was first
                print("It was first dot")
                selected_dot = (row, col)
                pygame.draw.circle(screen, (255, 0, 0), (x, y), DOT_RADIUS + 3, 2)
                return selected_dot, current_player_idx, last_move
            else:  # -> It was second
                print("It was second dot")
                r1, c1 = selected_dot
                r2, c2 = row, col
                if (r1, c1) == (r2, c2):
                    # -> double-click on same dot
                    return selected_dot, current_player_idx, last_move
                # If it was second, let's see if it was valid to form a line (adjacent)
                if check_adjacency(r1, c1, r2, c2):
                    print("They were adjacent")
                    # Determine line type and update correct grid
                    player = players[current_player_idx]
                    # -> Got to draw a line
                    if r1 == r2 and abs(c1 - c2) == 1:
                        print("Gotta draw horizontally")
                        board.draw_horizontal(r1, min(c1, c2), player)
                    elif c1 == c2 and abs(r1 - r2) == 1:
                        print("Gotta draw vertically")
                        board.draw_vertical(min(r1, r2), c1, player)
                    box_made = board.check_boxes(player)
                    if not box_made:
                        current_player_idx = (current_player_idx + 1) % 2
                else:
                    print("Dots not adjacent")

                return None, current_player_idx, last_move
    return selected_dot, current_player_idx, last_move


def check_adjacency(r1, c1, r2, c2):
    if (abs(r1 - r2) == 1 and c1 == c2) or (abs(c1 - c2) == 1 and r1 == r2):
        print(f"Valid line between ({r1},{c1}) and ({r2},{c2})")
        return True
    return False


def board_is_full() -> bool:
    return board.is_full()


# ===METHODS===-> Display
def show_intro_screen(screen, click_sound, grass_bg, grass_fg,cat_frames):
    clock = pygame.time.Clock()
    font_title = pygame.font.SysFont(None, 72)
    font_button = pygame.font.SysFont(None, 40)

    screen_width, screen_height = screen.get_size()

    # Load and scale grass
    grass_bg = pygame.transform.scale(grass_bg, (screen_width, 150))
    grass_fg = pygame.transform.scale(grass_fg, (screen_width, 150))


    cat_index = 0
    cat_timer = 0
    cat_x = 0
    cat_y = 0
    cat_speed = 1.5
    cat_pause = 0  # Pause timer after going offscreen

    # Start button setup
    button_width, button_height = 160, 45
    shadow_offset = 8
    button_x = screen_width // 2 - button_width // 2
    button_y = screen_height // 2 + 50
    start_button = pygame.Rect(button_x, button_y, button_width, button_height)

    while True:
        screen.fill(COLOR_BACKGROUND)  # Use new background color

        # Cat animation timing
        now = pygame.time.get_ticks()
        if now - cat_timer > 200:
            cat_index = (cat_index + 1) % len(cat_frames)
            cat_timer = now

        # Cat movement
        if cat_pause == 0:
            cat_x += cat_speed
            if cat_x > screen_width:
                cat_pause = now  # Start pause timer
        else:
            if now - cat_pause > 2000:  # Pause for 2 seconds before reset
                cat_x = -60
                cat_pause = 0

        # Draw grass background first
        screen.blit(grass_bg, (0, screen_height - 150))

        # Draw title
        title_surf = font_title.render("Dots and Boxes", True, (0, 0, 0))
        title_rect = title_surf.get_rect(center=(screen_width // 2, screen_height // 2 - 100))
        screen.blit(title_surf, title_rect)

        # Draw button
        pygame.draw.rect(screen, (0, 120, 250), start_button, border_radius=12)
        button_text = font_button.render("Start Game", True, (255, 255, 255))
        text_rect = button_text.get_rect(center=start_button.center)
        screen.blit(button_text, text_rect)

        # Draw grass foreground slightly higher
        screen.blit(grass_fg, (0, screen_height - 160))

        # Draw cat on top of foreground grass
        screen.blit(cat_frames[cat_index], (cat_x, cat_y))

        # Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if start_button.collidepoint(pygame.mouse.get_pos()):
                    click_sound.play()
                    return True

        pygame.display.flip()
        clock.tick(60)


# Draws logo/title + start button
# Returns True if start button is clicked

def show_setup_screen(screen, toggle_sound, click_sound, error_sound):
    import pygame, sys

    clock = pygame.time.Clock()
    font = pygame.font.SysFont('Arial', 22)
    big_font = pygame.font.SysFont('Arial', 42, bold=True)
    medium_font = pygame.font.SysFont('Arial', 26, bold=True)
    small_font = pygame.font.SysFont('Arial', 18)

    screen_width = screen.get_width()
    screen_height = screen.get_height()

    def draw_gradient_background(surface):
        for y in range(screen_height):
            ratio = y / screen_height
            r = int(15 + (35 - 15) * ratio)
            g = int(25 + (45 - 25) * ratio)
            b = int(60 + (80 - 60) * ratio)
            pygame.draw.line(surface, (r, g, b), (0, y), (screen_width, y))

    class ModernInputBox:
        def __init__(self, x, y, width, height, font, placeholder):
            self.rect = pygame.Rect(x, y, width, height)
            self.font = font
            self.placeholder = placeholder
            self.text = ""
            self.active = False
            self.cursor_visible = True
            self.cursor_timer = 0

        def handle_event(self, event):
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.active = self.rect.collidepoint(event.pos)
            elif event.type == pygame.KEYDOWN and self.active:
                if event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                elif event.unicode.isprintable():
                    self.text += event.unicode

        def draw(self, surface):
            self.cursor_timer += 1
            if self.cursor_timer > 30:
                self.cursor_visible = not self.cursor_visible
                self.cursor_timer = 0

            bg = (255, 255, 255) if self.active else (248, 249, 250)
            border = (52, 152, 219) if self.active else (189, 195, 199)

            pygame.draw.rect(surface, (0, 0, 0, 30), self.rect.move(2, 2), border_radius=8)
            pygame.draw.rect(surface, bg, self.rect, border_radius=8)
            pygame.draw.rect(surface, border, self.rect, 2, border_radius=8)

            txt_color = (60, 70, 90)
            if self.text:
                text_surface = self.font.render(self.text, True, txt_color)
            else:
                text_surface = self.font.render(self.placeholder, True, (149, 165, 166))

            text_rect = text_surface.get_rect(midleft=(self.rect.x + 15, self.rect.centery))
            surface.blit(text_surface, text_rect)

            if self.active and self.cursor_visible and self.text:
                cursor_x = text_rect.right + 2
                pygame.draw.line(surface, txt_color,
                                 (cursor_x, self.rect.y + 8),
                                 (cursor_x, self.rect.y + self.rect.height - 8), 2)

        def get_text(self):
            return self.text

    # Initial state
    game_modes = ["1-Player", "2-Player"]
    selected_mode = "1-Player"
    difficulties = ["Easy", "Medium", "Hard"]
    selected_difficulty = "Easy"
    ai_levels = ["Beginner", "Advanced"]
    selected_ai = "Beginner"
    error_message = ""
    error_timer = 0

    # Card dimensions
    card_width, card_height = 650, 700
    card_x = (screen_width - card_width) // 2
    card_y = (screen_height - card_height) // 2
    shadow_offset = 8
    button_width, button_height = 140, 45

    # Input boxes
    input_boxes = []

    while True:
        screen.fill((0, 0, 0))
        draw_gradient_background(screen)

        pygame.draw.rect(screen, (0, 0, 0, 50),
                         (card_x + shadow_offset, card_y + shadow_offset, card_width, card_height), border_radius=20)
        pygame.draw.rect(screen, (255, 255, 255), (card_x, card_y, card_width, card_height), border_radius=20)

        title_text = big_font.render("Game Setup", True, (45, 55, 75))
        screen.blit(title_text, title_text.get_rect(center=(screen_width // 2, card_y + 50)))

        # Start building UI from this Y
        y = card_y + 100

        # --- Mode Selection ---
        screen.blit(medium_font.render("Game Mode", True, (60, 70, 90)), (card_x + 50, y))
        mode_y = y + 50
        for i, mode in enumerate(game_modes):
            x = card_x + 120 + i * 180
            rect = pygame.Rect(x, mode_y, button_width, button_height)
            pygame.draw.rect(screen, (52, 152, 219) if selected_mode == mode else (236, 240, 241), rect,
                             border_radius=12)
            txt = font.render(mode, True, (255, 255, 255) if selected_mode == mode else (60, 70, 90))
            screen.blit(txt, txt.get_rect(center=rect.center))
        y += 100

        # --- Input Boxes (2P only) ---
        if selected_mode == "2-Player":
            y += 40
            screen.blit(medium_font.render("Player Names", True, (60, 70, 90)), (card_x + 50, y))
            y += 50
            if not input_boxes:
                input_boxes = [
                    InputBox(card_x + 100, y, card_width - 200, 50, font, "Player 1 Name"),
                    InputBox(card_x + 100, y + 70, card_width - 200, 50, font, "Player 2 Name")
                ]
            for box in input_boxes:
                box.draw(screen)
            y += 100
        else:
            input_boxes = []  # Clear if user switched back to 1P

        # --- Difficulty ---
        screen.blit(medium_font.render("Difficulty", True, (60, 70, 90)), (card_x + 50, y + 50))
        diff_y = y + 100
        for i, diff in enumerate(difficulties):
            x = card_x + 80 + i * 170
            rect = pygame.Rect(x, diff_y, button_width, button_height)
            pygame.draw.rect(screen, (46, 204, 113) if selected_difficulty == diff else (236, 240, 241), rect,
                             border_radius=12)
            txt = font.render(diff, True, (255, 255, 255) if selected_difficulty == diff else (60, 70, 90))
            screen.blit(txt, txt.get_rect(center=rect.center))
        y += 90

        # --- AI Level (1P only) ---
        if selected_mode == "1-Player":
            y += 100
            screen.blit(medium_font.render("Computer Level", True, (60, 70, 90)), (card_x + 50, y))
            ai_y = y + 50
            for i, level in enumerate(ai_levels):
                x = card_x + 120 + i * 200
                rect = pygame.Rect(x, ai_y, button_width + 20, button_height)
                pygame.draw.rect(screen, (155, 89, 182) if selected_ai == level else (236, 240, 241), rect,
                                 border_radius=12)
                txt = font.render(level, True, (255, 255, 255) if selected_ai == level else (60, 70, 90))
                screen.blit(txt, txt.get_rect(center=rect.center))
            y += 90

        # --- Start Button ---
        start_y = card_y + card_height - 100
        start_rect = pygame.Rect(card_x + (card_width - 200) // 2, start_y, 200, 55)
        pygame.draw.rect(screen, (231, 76, 60), start_rect, border_radius=15)
        screen.blit(medium_font.render("Start Game", True, (255, 255, 255)), start_rect.move(30, 10))

        # --- Error Message ---
        if error_message and pygame.time.get_ticks() - error_timer < 3000:
            error_surface = small_font.render(error_message, True, (231, 76, 60))
            screen.blit(error_surface, error_surface.get_rect(center=(screen_width // 2, card_y + card_height - 30)))

        # --- Events ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            for box in input_boxes:
                box.handle_event(event)

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos

                # Game Mode toggle
                for i, mode in enumerate(game_modes):
                    x = card_x + 120 + i * 180
                    if pygame.Rect(x, mode_y, button_width, button_height).collidepoint(pos):
                        selected_mode = mode
                        toggle_sound.play()
                        input_boxes = []  # Force reset to rebuild properly

                # Difficulty toggle
                for i, diff in enumerate(difficulties):
                    x = card_x + 80 + i * 170
                    if pygame.Rect(x, diff_y, button_width, button_height).collidepoint(pos):
                        selected_difficulty = diff
                        toggle_sound.play()

                # AI toggle
                if selected_mode == "1-Player":
                    for i, level in enumerate(ai_levels):
                        x = card_x + 120 + i * 180
                        if pygame.Rect(x, ai_y, button_width + 20, button_height).collidepoint(pos):
                            selected_ai = level
                            toggle_sound.play()

                # Start Game
                if start_rect.collidepoint(pos):
                    if selected_mode == "2-Player":
                        name1 = input_boxes[0].get_text() if input_boxes else ""
                        name2 = input_boxes[1].get_text() if len(input_boxes) > 1 else ""
                        if not (name1.strip() and name2.strip()):
                            error_message = "Please enter both player names!"
                            error_timer = pygame.time.get_ticks()
                            error_sound.play()
                        else:
                            click_sound.play()
                            return [Player(name1.strip(), COLOR_PLAYER1, 'X'),
                                    Player(name2.strip(), COLOR_PLAYER2,
                                           'O')], selected_difficulty, selected_mode, None
                    else:
                        click_sound.play()
                        return [Player("You", COLOR_PLAYER1, 'X'),
                                Player("Computer", COLOR_PLAYER2,
                                       'O')], selected_difficulty, selected_mode, selected_ai

        pygame.display.flip()
        clock.tick(60)

        pygame.draw.rect(screen, (0, 0, 0, 50),
                         (card_x + shadow_offset, card_y + shadow_offset, card_width, card_height), border_radius=20)
        pygame.draw.rect(screen, (255, 255, 255), (card_x, card_y, card_width, card_height), border_radius=20)

        title_text = big_font.render("Game Setup", True, (45, 55, 75))
        screen.blit(title_text, title_text.get_rect(center=(screen_width // 2, card_y + 50)))

        # Start building UI from this Y
        y = card_y + 100

        # --- Mode Selection ---
        screen.blit(medium_font.render("Game Mode", True, (60, 70, 90)), (card_x + 50, y))
        mode_y = y + 50
        for i, mode in enumerate(game_modes):
            x = card_x + 120 + i * 180
            rect = pygame.Rect(x, mode_y, button_width, button_height)
            pygame.draw.rect(screen, (52, 152, 219) if selected_mode == mode else (236, 240, 241), rect,
                             border_radius=12)
            txt = font.render(mode, True, (255, 255, 255) if selected_mode == mode else (60, 70, 90))
            screen.blit(txt, txt.get_rect(center=rect.center))
        y += 100

        # --- Input Boxes (2P only) ---
        if selected_mode == "2-Player":
            y += 40
            screen.blit(medium_font.render("Player Names", True, (60, 70, 90)), (card_x + 50, y))
            y += 50
            if not input_boxes:
                input_boxes = [
                    InputBox(card_x + 100, y, card_width - 200, 50, font, "Player 1 Name"),
                    InputBox(card_x + 100, y + 70, card_width - 200, 50, font, "Player 2 Name")
                ]
            for box in input_boxes:
                box.draw(screen)
            y += 100
        else:
            input_boxes = []  # Clear if user switched back to 1P

        # --- Difficulty ---
        screen.blit(medium_font.render("Difficulty", True, (60, 70, 90)), (card_x + 50, y + 50))
        diff_y = y + 100
        for i, diff in enumerate(difficulties):
            x = card_x + 80 + i * 170
            rect = pygame.Rect(x, diff_y, button_width, button_height)
            pygame.draw.rect(screen, (46, 204, 113) if selected_difficulty == diff else (236, 240, 241), rect,
                             border_radius=12)
            txt = font.render(diff, True, (255, 255, 255) if selected_difficulty == diff else (60, 70, 90))
            screen.blit(txt, txt.get_rect(center=rect.center))
        y += 90

        # --- AI Level (1P only) ---
        if selected_mode == "1-Player":
            y += 100
            screen.blit(medium_font.render("Computer Level", True, (60, 70, 90)), (card_x + 50, y))
            ai_y = y + 50
            for i, level in enumerate(ai_levels):
                x = card_x + 120 + i * 200
                rect = pygame.Rect(x, ai_y, button_width + 20, button_height)
                pygame.draw.rect(screen, (155, 89, 182) if selected_ai == level else (236, 240, 241), rect,
                                 border_radius=12)
                txt = font.render(level, True, (255, 255, 255) if selected_ai == level else (60, 70, 90))
                screen.blit(txt, txt.get_rect(center=rect.center))
            y += 90

        # --- Start Button ---
        start_y = card_y + card_height - 100
        start_rect = pygame.Rect(card_x + (card_width - 200) // 2, start_y, 200, 55)
        pygame.draw.rect(screen, (231, 76, 60), start_rect, border_radius=15)
        screen.blit(medium_font.render("Start Game", True, (255, 255, 255)), start_rect.move(30, 10))

        # --- Error Message ---
        if error_message and pygame.time.get_ticks() - error_timer < 3000:
            error_surface = small_font.render(error_message, True, (231, 76, 60))
            screen.blit(error_surface, error_surface.get_rect(center=(screen_width // 2, card_y + card_height - 30)))

        # --- Events ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            for box in input_boxes:
                box.handle_event(event)

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos

                # Game Mode toggle
                for i, mode in enumerate(game_modes):
                    x = card_x + 120 + i * 180
                    if pygame.Rect(x, mode_y, button_width, button_height).collidepoint(pos):
                        selected_mode = mode
                        toggle_sound.play()
                        input_boxes = []  # Force reset to rebuild properly

                # Difficulty toggle
                for i, diff in enumerate(difficulties):
                    x = card_x + 80 + i * 170
                    if pygame.Rect(x, diff_y, button_width, button_height).collidepoint(pos):
                        selected_difficulty = diff
                        toggle_sound.play()

                # AI toggle
                if selected_mode == "1-Player":
                    for i, level in enumerate(ai_levels):
                        x = card_x + 120 + i * 180
                        if pygame.Rect(x, ai_y, button_width + 20, button_height).collidepoint(pos):
                            selected_ai = level
                            toggle_sound.play()

                # Start Game
                if start_rect.collidepoint(pos):
                    if selected_mode == "2-Player":
                        name1 = input_boxes[0].get_text() if input_boxes else ""
                        name2 = input_boxes[1].get_text() if len(input_boxes) > 1 else ""
                        if not (name1.strip() and name2.strip()):
                            error_message = "Please enter both player names!"
                            error_timer = pygame.time.get_ticks()
                            error_sound.play()
                        else:
                            click_sound.play()
                            return [Player(name1.strip(), COLOR_PLAYER1, 'X'),
                                    Player(name2.strip(), COLOR_PLAYER2,
                                           'O')], selected_difficulty, selected_mode, None
                    else:
                        click_sound.play()
                        return [Player("You", COLOR_PLAYER1, 'X'),
                                Player("Computer", COLOR_PLAYER2,
                                       'O')], selected_difficulty, selected_mode, selected_ai

        pygame.display.flip()
        clock.tick(60)


# Text input for names and symbols
# Returns player data if submitted

def set_difficulty(level):
    global GRID_ROWS, GRID_COLS
    if level == "Easy":
        GRID_ROWS, GRID_COLS = 6, 6
    elif level == "Medium":
        GRID_ROWS, GRID_COLS = 10, 10
    elif level == "Hard":
        GRID_ROWS, GRID_COLS = 15, 15
    global board
    board = Board(GRID_ROWS, GRID_COLS)


def show_outro_screen(screen, winner_text, click_sound, win_sound, players, selected_mode, selected_ai):
    clock = pygame.time.Clock()

    # === Keep original fonts ===
    font_title = pygame.font.SysFont(None, 60)
    font_button = pygame.font.SysFont(None, 36)
    font_score = pygame.font.SysFont("Arial", 32, bold=True)  # Only for scoreboard

    win_sound.play()
    bg_y = 0
    scroll_speed = 0.2

    # === Confetti ===
    confetti = []
    for _ in range(100):
        x = random.randint(0, screen.get_width())
        y = random.randint(-300, 0)
        size = random.randint(3, 6)
        speed = random.uniform(1, 3)
        color = random.choice([
            (255, 0, 0), (0, 255, 0), (255, 255, 0),
            (0, 255, 255), (255, 0, 255), (255, 150, 0)
        ])
        confetti.append([x, y, size, speed, color])

    # Buttons
    replay_btn = pygame.Rect(screen.get_width() // 2 - 140, 530, 280, 60)
    exit_btn = pygame.Rect(screen.get_width() // 2 - 140, 620, 280, 60)

    # Summary info
    # total_boxes = (GRID_ROWS - 1) * (GRID_COLS - 1)
    # total_moves = sum([player.moves for player in players])
    # summary_lines = [
    #     f"Total Boxes: {total_boxes}",
    #     f"Total Moves: {total_moves}",
    #     f"Mode: {selected_mode}" + (f" ({selected_ai})" if selected_mode == "1-Player" else ""),
    #     f"Winner: {winner_text}"
    # ]

    while True:
        screen.fill((255, 255, 255))

        # === Confetti Animation ===
        bg_y += scroll_speed
        if bg_y >= screen.get_height():
            bg_y = 0

        for particle in confetti:
            x, y, size, speed, color = particle
            pygame.draw.circle(screen, color, (int(x), int(y)), size)
            particle[1] += speed
            if particle[1] > screen.get_height():
                particle[1] = random.randint(-100, -10)
                particle[0] = random.randint(0, screen.get_width())

        # === Winner Text ===
        title_surf = font_title.render(winner_text, True, (30, 30, 30))
        title_rect = title_surf.get_rect(center=(screen.get_width() // 2, 100))
        screen.blit(title_surf, title_rect)

        # === Scoreboard ===
        box_width = 480
        box_height = 180
        box_x = (screen.get_width() - box_width) // 2
        box_y = title_rect.bottom + 40

        pygame.draw.rect(screen, (0, 0, 0, 40), (box_x + 4, box_y + 4, box_width, box_height), border_radius=18)
        pygame.draw.rect(screen, (245, 248, 255), (box_x, box_y, box_width, box_height), border_radius=18)
        pygame.draw.rect(screen, (200, 200, 200), (box_x, box_y, box_width, box_height), 2, border_radius=18)

        for i, player in enumerate(players):
            name_text = f"{player.name}"
            score_text = f"{player.score} box{'es' if player.score != 1 else ''}"

            name_surf = font_score.render(name_text, True, player.color)
            score_surf = font_score.render(score_text, True, (60, 60, 60))

            name_rect = name_surf.get_rect(midleft=(box_x + 40, box_y + 50 + i * 60))
            score_rect = score_surf.get_rect(midright=(box_x + box_width - 40, box_y + 50 + i * 60))

            screen.blit(name_surf, name_rect)
            screen.blit(score_surf, score_rect)

        # === Game Summary ===
        # summary_y = box_y + box_height + 40
        # for i, line in enumerate(summary_lines):
        #     summary_surf = font_button.render(line, True, (50, 50, 50))
        #     summary_rect = summary_surf.get_rect(center=(screen.get_width() // 2, summary_y + i * 35))
        #     screen.blit(summary_surf, summary_rect)

        # === Buttons ===
        pygame.draw.rect(screen, (46, 204, 113), replay_btn, border_radius=12)
        pygame.draw.rect(screen, (39, 174, 96), replay_btn, 3, border_radius=12)
        replay_text = font_button.render("Play Again", True, (255, 255, 255))
        screen.blit(replay_text, replay_text.get_rect(center=replay_btn.center))

        pygame.draw.rect(screen, (231, 76, 60), exit_btn, border_radius=12)
        pygame.draw.rect(screen, (192, 57, 43), exit_btn, 3, border_radius=12)
        exit_text = font_button.render("Exit", True, (255, 255, 255))
        screen.blit(exit_text, exit_text.get_rect(center=exit_btn.center))

        pygame.display.flip()

        # === Event Handling ===
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                if replay_btn.collidepoint(mouse_pos):
                    board.reset()
                    return "replay"
                elif exit_btn.collidepoint(mouse_pos):
                    if confirm_dialog(screen, "You really wanna quit?", click_sound):
                        return "exit"

        clock.tick(60)


# === 1P mode ===
def get_all_available_lines():
    l = []


def beginner_ai_make_move(current_player):
    last_move = None
    # First, try to find any line that completes a box
    for r in range(len(board.h_lines)):
        for c in range(len(board.h_lines[0])):
            if not board.h_lines[r][c]:
                board.h_lines[r][c] = True  # Temporarily mark
                if board.check_boxes(current_player):  # box made?
                    last_move = (r, c, 'H')
                    return True, last_move
                board.h_lines[r][c] = False  # Undo

    for r in range(len(board.v_lines)):
        for c in range(len(board.v_lines[0])):
            if not board.v_lines[r][c]:
                board.v_lines[r][c] = True
                if board.check_boxes(current_player):
                    last_move = (r, c, 'V')
                    return True, last_move
                board.v_lines[r][c] = False

    # If no box-completing line found, choose a random available line
    lines = []

    for r in range(len(board.h_lines)):
        for c in range(len(board.h_lines[0])):
            if not board.h_lines[r][c]:
                lines.append(("h", r, c))

    for r in range(len(board.v_lines)):
        for c in range(len(board.v_lines[0])):
            if not board.v_lines[r][c]:
                lines.append(("v", r, c))

    if lines:
        line = random.choice(lines)
        direction, r, c = line
        if direction == "h":
            board.h_lines[r][c] = True
            last_move = (r, c, 'H')
        else:
            board.v_lines[r][c] = True
            last_move = (r, c, 'V')
        return board.check_boxes(current_player), last_move


def advanced_ai_make_move(ai, opponent):
    """
    1) If any move completes one or more boxes, pick the one with max gain.
    2) Else pick any move that leaves opponent with ZERO new 3‑sided boxes.
    3) Else pick the move that *adds* the fewest new 3‑sided boxes. -> it's catchy, not perfect!
    Returns (box_made: bool, last_move: (r, c, orientation))
    """

    all_moves = board.get_available_moves()

    # Precompute baseline 3‑sided count
    def count_3_sided():
        total = 0
        for br in range(board.rows - 1):
            for bc in range(board.cols - 1):
                if board.boxes[br][bc]:
                    continue
                sides = (
                        board.h_lines[br][bc] +
                        board.v_lines[br][bc] +
                        board.h_lines[br + 1][bc] +
                        board.v_lines[br][bc + 1]
                )
                if sides == 3:
                    total += 1
        return total

    baseline_risk = count_3_sided()

    # Helper: simulate move, count new boxes made
    def count_new_boxes(move):
        before = sum(
            1 for rr in range(board.rows - 1)
            for cc in range(board.cols - 1)
            if board.boxes[rr][cc] == ai.symbol
        )
        board.make_move_simulated(move, ai.symbol)
        after = sum(
            1 for rr in range(board.rows - 1)
            for cc in range(board.cols - 1)
            if board.boxes[rr][cc] == ai.symbol
        )
        board.undo_move(move)
        return after - before

    # Helper: simulate move, return added 3‑sided boxes (risk delta)
    def added_risk(move):
        board.make_move_simulated(move, ai.symbol)
        new_risk = count_3_sided()
        board.undo_move(move)
        return new_risk - baseline_risk

    # === STEP1: look for scoring moves ===
    scoring_moves = [(m, count_new_boxes(m)) for m in all_moves]
    max_gain = max((gain for m, gain in scoring_moves), default=0)
    if max_gain > 0:
        best = [m for m, gain in scoring_moves if gain == max_gain]
        chosen = random.choice(best)

    else:
        # === STEP2: avoid any NEW risk ===
        zero_risk = [m for m in all_moves if added_risk(m) == 0]
        if zero_risk:
            chosen = random.choice(zero_risk)
        else:
            # === STEP3: pick move with minimal added risk ===
            risks = [(m, added_risk(m)) for m in all_moves]
            min_r = min(r for m, r in risks)
            best = [m for m, r in risks if r == min_r]
            chosen = random.choice(best) if best else None

    # === Execute the chosen move ===
    direction, r, c = chosen
    if direction == "h":
        board.draw_horizontal(r, c, ai)
        last_move = (r, c, 'H')
    else:
        board.draw_vertical(r, c, ai)
        last_move = (r, c, 'V')

    box_made = board.check_boxes(ai)
    return box_made, last_move
