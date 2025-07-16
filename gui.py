import pygame
import sys

from game.game_engine_gui import calculate_spacing_between_dots, store_coordinates_of_dots, draw_dots, draw_h_line, \
    draw_v_line, draw_acquired_boxes, check_game_over, show_outro_screen, handle_events, board_is_full, \
    show_intro_screen, show_setup_screen, draw_sidebar, detect_hovered_line, draw_hover_highlight, set_difficulty, \
    confirm_dialog, beginner_ai_make_move, advanced_ai_make_move, COLOR_PLAYER1, COLOR_PLAYER2, particle_manager, \
    set_cat_state
from game.constants import WINDOW_WIDTH, WINDOW_HEIGHT, SIDEBAR_WIDTH, GAME_WIDTH, COLOR_BACKGROUND, CAT_FRAME_DELAY

# TODO / ISSUES
'''
    -> AI-difficult moves mending
    -> Code refining
    -> application packaging (.exe, .bin, .deb)
'''
# loading assests with proper path for proper packaging
from pathlib import Path


def resource_path(relative_path):
    try:
        base_path = Path(sys._MEIPASS)  # PyInstaller temp dir
    except AttributeError:
        base_path = Path(__file__).parent  # Normal dev environment
    return base_path / relative_path



class GameGUI:
    def __init__(self):
        # === CONFIG ===
        self.WINDOW_WIDTH = WINDOW_WIDTH
        self.WINDOW_HEIGHT = WINDOW_HEIGHT
        self.SIDEBAR_WIDTH = SIDEBAR_WIDTH
        self.GAME_WIDTH = GAME_WIDTH
        self.BACKGROUND_COLOR = COLOR_BACKGROUND

        # === SETUP ===
        pygame.init()
        self.screen = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        self.current_screen = "intro"
        pygame.display.set_caption("Dots and Boxes")
        self.clock = pygame.time.Clock()
        self.selected_dot = None  # For storing first clicked dot
        self.game_over = False
        self.winner_text = ""
        self.current_player_idx = 0
        pygame.mixer.init()
        self.music_on = True
        pygame.mixer.music.load(str(resource_path("assets/music.mp3")))
        pygame.mixer.music.play(-1)
        pygame.mixer.music.set_volume(0.5)  # 0.0 to 1.0
        self.line_sound = pygame.mixer.Sound(str(resource_path("assets/sfx/line.mp3")))
        self.box_sound = pygame.mixer.Sound(str(resource_path("assets/sfx/box.mp3")))
        self.win_sound = pygame.mixer.Sound(str(resource_path("assets/sfx/win.mp3")))
        self.click_sound = pygame.mixer.Sound(str(resource_path("assets/sfx/click.mp3")))
        self.error_sound = pygame.mixer.Sound(str(resource_path("assets/sfx/error.mp3")))
        self.toggle_sound = pygame.mixer.Sound(str(resource_path("assets/sfx/toggle.mp3")))
        self.click_sound.set_volume(0.5)
        self.background_image = pygame.image.load(str(resource_path("assets/white.png"))).convert()
        self.grass_fg = pygame.image.load(str(resource_path("assets/grass1.png"))).convert_alpha()
        self.grass_bg = pygame.image.load(str(resource_path("assets/grass2.png"))).convert_alpha()
        self.cat_frames = [
            pygame.image.load(str(resource_path(f"assets/cat{i}.png"))).convert_alpha()
            for i in range(1, 4)
        ]

        self.frame_idx = 0
        self.players = None
        self.last_drawn_line = None  # To store (x, y, orientation)

    def reset(self):
        self.selected_dot = None
        self.winner_text = ""
        self.current_player_idx = 0
        self.game_over = False

    def game_loop(self, players, selected_mode, selected_ai):
        running = True
        ai_player_idx = 1 if selected_mode == "1-Player" else None

        while running:
            self.screen.blit(self.background_image, (0, 0))  # Blit background image

            # === DRAW ===
            draw_dots(self.screen)
            draw_h_line(self.screen, self.last_drawn_line)
            draw_v_line(self.screen, self.last_drawn_line)
            draw_acquired_boxes(self.screen, players)

            # Update and draw particles
            particle_manager.update()
            particle_manager.draw(self.screen)

            music_button, restart_button, quit_button = draw_sidebar(
                self.screen, players, self.current_player_idx, self.music_on, self.SIDEBAR_WIDTH, self.cat_frames
            )

            # === CHECK FOR GAME END ===
            self.game_over, self.winner_text = check_game_over(self.game_over, players)
            if self.game_over:
                pygame.display.flip()
                pygame.time.delay(400)
                self.screen.fill((255, 255, 255))
                command = show_outro_screen(self.screen, self.winner_text, self.click_sound, self.win_sound, players,
                                            selected_mode,
                                            selected_ai)
                if command == "replay":
                    return command
                else:
                    break

            # === HOVER HIGHLIGHT ===
            hovered_line = detect_hovered_line(*pygame.mouse.get_pos())
            draw_hover_highlight(self.screen, hovered_line)

            # === PLAYER INPUT OR AI TURN ===
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mouse_pos = pygame.mouse.get_pos()

                    if music_button.collidepoint(mouse_pos):
                        self.toggle_sound.play()
                        self.music_on = not self.music_on
                        if self.music_on:
                            pygame.mixer.music.unpause()
                        else:
                            pygame.mixer.music.pause()

                    elif restart_button.collidepoint(mouse_pos):
                        self.click_sound.play()
                        if confirm_dialog(self.screen, "Do you really wanna restart?", self.click_sound):
                            self.click_sound.play()
                            return "replay"

                    elif quit_button.collidepoint(mouse_pos):
                        self.click_sound.play()
                        if confirm_dialog(self.screen, "Do you really want to quit?", self.click_sound):
                            self.click_sound.play()
                            pygame.quit()
                            sys.exit()

                    elif not board_is_full() and (
                            selected_mode == "2-Player" or self.current_player_idx != ai_player_idx):
                        self.selected_dot, self.current_player_idx, new_move = handle_events(
                            self.screen, self.selected_dot, self.current_player_idx, players, self.click_sound,
                            self.box_sound
                        )
                        if new_move:
                            self.last_drawn_line = new_move

            # === AI TURN ===
            if selected_mode == "1-Player" and self.current_player_idx == ai_player_idx and not board_is_full() and not self.game_over:
                pygame.time.delay(300)
                if selected_ai == "Beginner":
                    made, new_move = beginner_ai_make_move(players[1])
                else:
                    made, new_move = advanced_ai_make_move(players[1], players[0])
                if new_move:
                    self.last_drawn_line = new_move

                self.current_player_idx = (self.current_player_idx + (1 - int(made))) % 2

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()

    def run(self):
        while True:
            if self.current_screen == "intro":
                if show_intro_screen(self.screen, self.click_sound, self.grass_bg, self.grass_fg, self.cat_frames):
                    self.current_screen = "setup"
            elif self.current_screen == "setup":
                self.players, selected_difficulty, selected_mode, selected_ai = show_setup_screen(self.screen,
                                                                                                  self.toggle_sound,
                                                                                                  self.click_sound,
                                                                                                  self.error_sound)
                set_difficulty(selected_difficulty)
                calculate_spacing_between_dots(self.GAME_WIDTH, self.WINDOW_HEIGHT)
                store_coordinates_of_dots()
                set_cat_state(self.WINDOW_WIDTH, self.SIDEBAR_WIDTH)
                if self.players:
                    self.current_screen = "game"
            elif self.current_screen == "game":
                result = self.game_loop(self.players, selected_mode, selected_ai)
                if result == "replay":
                    self.reset()
                    self.current_screen = "setup"
                else:
                    break  # Exit after game
