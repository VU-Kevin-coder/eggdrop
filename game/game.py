"""
game/game.py
------------
The Game class owns the main loop and the state machine. Every state
transition described in the design brief happens here, explicitly and
without placeholders:

MENU -> INTRO -> PLAYING -> (LEVEL_COMPLETE -> PLAYING)* -> VICTORY -> MENU
                     |                                  
                     +--> PAUSED --> PLAYING
                     |
                     +--> GAME_OVER --> PLAYING (retry) or MENU
"""

import sys
import pygame

import settings
from game.level import Level, LEVEL_DATA
from game.player import Player, distance
from game.egg import Egg
from game.audio import AudioManager
import ui


class states:
    MENU = "MENU"
    HOW_TO_PLAY = "HOW_TO_PLAY"
    INTRO = "INTRO"
    PLAYING = "PLAYING"
    PAUSED = "PAUSED"
    LEVEL_COMPLETE = "LEVEL_COMPLETE"
    GAME_OVER = "GAME_OVER"
    VICTORY = "VICTORY"


INTRO_LINES = [
    "IMPORTANT.",
    "Take this egg to Grandma.",
    "Do NOT drop it.",
    "OPERATION EGG DELIVERY HAS BEGUN.",
]

VICTORY_LINES = [
    "DELIVERY COMPLETE",
    "GRANDMA RECEIVED THE EGG.",
    "You carried an egg across the entire city.",
    "Congratulations.",
    "Grandma could have just bought one.",
]

GAME_OVER_TITLE = "THE EGG HAS LEFT THIS WORLD."
GAME_OVER_LINES = [
    "It fought bravely. It lost.",
    "Press R to retry this delivery, or ESC for the menu.",
]

BUMP_QUIPS = ["Please be more careful.", "Whoops.", "That was close."]
BIG_HIT_QUIPS = ["THAT WAS NOT CAREFUL.", "The egg has seen things.", "This is fine. Probably."]


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
        pygame.display.set_caption(settings.GAME_TITLE)
        self.clock = pygame.time.Clock()
        self.running = True

        self.fonts = {
            "tiny": pygame.font.SysFont(settings.FONT_NAME, 16),
            "small": pygame.font.SysFont(settings.FONT_NAME, 22),
            "medium": pygame.font.SysFont(settings.FONT_NAME, 32, bold=True),
            "large": pygame.font.SysFont(settings.FONT_NAME, 46, bold=True),
            "title": pygame.font.SysFont(settings.FONT_NAME, 64, bold=True),
        }

        self.audio = AudioManager()

        self.state = states.MENU
        self.menu_selected_index = 0
        self.menu_rects = []

        self.intro_index = 0

        self.current_level_index = 0
        self.level = None
        self.player = None
        self.egg = None
        self.egg_condition_carry = settings.EGG_START_CONDITION
        self.level_start_condition = settings.EGG_START_CONDITION

        self.level_complete_timer = 0.0
        self.hud_quip = ""
        self.hud_quip_timer = 0.0
        self._prev_egg_condition = settings.EGG_START_CONDITION
        self._footstep_timer = 0.0
        self._wobble_audio_timer = 0.0
        self.delivery_ready = False

        self.audio.play_music("menu")

    # ------------------------------------------------------------------
    # MAIN LOOP
    # ------------------------------------------------------------------
    def run(self):
        while self.running:
            dt = self.clock.tick(settings.FPS) / 1000.0
            dt = min(dt, 0.05)  # avoid huge jumps if the window is dragged/stalled
            self.handle_events()
            self.update(dt)
            self.draw()
            pygame.display.flip()
        pygame.quit()
        sys.exit()

    # ------------------------------------------------------------------
    # NEW GAME / LEVEL FLOW
    # ------------------------------------------------------------------
    def start_new_game(self):
        self.egg_condition_carry = settings.EGG_START_CONDITION
        self.current_level_index = 0
        self.intro_index = 0
        self.state = states.INTRO

    def start_level(self, index):
        self.current_level_index = index
        self.level = Level(index)
        self.player = Player(*self.level.player_start)

        if self.level.start_with_egg_carried:
            egg = Egg(*self.level.player_start)
            egg.condition = self.egg_condition_carry
            egg.carried = True
            self.player.carrying = egg
        else:
            egg = Egg(*self.level.egg_start)
            egg.condition = self.egg_condition_carry
            self.player.carrying = None

        self.egg = egg
        self.level_start_condition = egg.condition
        self._prev_egg_condition = egg.condition
        self.delivery_ready = False
        self.hud_quip = ""
        self.hud_quip_timer = 0.0

        self.state = states.PLAYING
        self.audio.play_music("gameplay")

    def retry_level(self):
        self.egg_condition_carry = self.level_start_condition
        self.start_level(self.current_level_index)

    def advance_level(self):
        next_index = self.current_level_index + 1
        if next_index >= len(LEVEL_DATA):
            self.state = states.VICTORY
            self.audio.play_music("victory")
            self.audio.play("success")
        else:
            self.start_level(next_index)

    def return_to_menu(self):
        self.state = states.MENU
        self.egg_condition_carry = settings.EGG_START_CONDITION
        self.current_level_index = 0
        self.audio.play_music("menu")

    # ------------------------------------------------------------------
    # EVENTS
    # ------------------------------------------------------------------
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return

            if self.state == states.MENU:
                self._handle_menu_event(event)
            elif self.state == states.HOW_TO_PLAY:
                self._handle_how_to_play_event(event)
            elif self.state == states.INTRO:
                self._handle_intro_event(event)
            elif self.state == states.PLAYING:
                self._handle_playing_event(event)
            elif self.state == states.PAUSED:
                self._handle_paused_event(event)
            elif self.state == states.LEVEL_COMPLETE:
                self._handle_level_complete_event(event)
            elif self.state == states.GAME_OVER:
                self._handle_game_over_event(event)
            elif self.state == states.VICTORY:
                self._handle_victory_event(event)

    def _handle_menu_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w):
                self.menu_selected_index = (self.menu_selected_index - 1) % len(ui.MENU_OPTIONS)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.menu_selected_index = (self.menu_selected_index + 1) % len(ui.MENU_OPTIONS)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self._activate_menu_option(self.menu_selected_index)
        elif event.type == pygame.MOUSEMOTION:
            for i, rect in enumerate(self.menu_rects):
                if rect.collidepoint(event.pos):
                    self.menu_selected_index = i
        elif event.type == pygame.MOUSEBUTTONDOWN:
            for i, rect in enumerate(self.menu_rects):
                if rect.collidepoint(event.pos):
                    self._activate_menu_option(i)

    def _activate_menu_option(self, index):
        self.audio.play("button_click")
        option = ui.MENU_OPTIONS[index]
        if option == "PLAY":
            self.start_new_game()
        elif option == "HOW TO PLAY":
            self.state = states.HOW_TO_PLAY
        elif option == "QUIT":
            self.running = False

    def _handle_how_to_play_event(self, event):
        if event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_ESCAPE):
            self.audio.play("button_click")
            self.state = states.MENU
        elif event.type == pygame.MOUSEBUTTONDOWN:
            self.audio.play("button_click")
            self.state = states.MENU

    def _handle_intro_event(self, event):
        advance = (
            (event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_SPACE)) or
            event.type == pygame.MOUSEBUTTONDOWN
        )
        if advance:
            self.intro_index += 1
            if self.intro_index >= len(INTRO_LINES):
                self.start_level(0)

    def _handle_playing_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.state = states.PAUSED
            elif event.key == pygame.K_e:
                if self.player.carrying is None and not self.egg.broken:
                    if distance(self.player.center, self.egg.pos) <= settings.EGG_PICKUP_RADIUS:
                        self.egg.pick_up(self.audio)
                        self.player.carrying = self.egg
                elif self.delivery_ready and self.player.carrying is self.egg:
                    self.egg.place_down(self.level.exit_rect.center, self.audio)
                    self.player.carrying = None
                    self.delivery_ready = False
                    self.egg_condition_carry = self.egg.condition
                    self.audio.play("level_complete")
                    self.state = states.LEVEL_COMPLETE
                    self.level_complete_timer = settings.LEVEL_COMPLETE_DELAY
            elif event.key == pygame.K_SPACE:
                if self.player.carrying is not None:
                    place_pos = self._position_in_front_of_player(28)
                    self.egg.drop_down(place_pos, self.audio)
                    self.player.carrying = None
                    self.delivery_ready = False

    def _handle_paused_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.state = states.PLAYING
            elif event.key == pygame.K_m:
                self.return_to_menu()

    def _handle_level_complete_event(self, event):
        if event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_SPACE):
            self.advance_level()

    def _handle_game_over_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                self.retry_level()
            elif event.key == pygame.K_ESCAPE:
                self.return_to_menu()

    def _handle_victory_event(self, event):
        if event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_ESCAPE):
            self.return_to_menu()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            self.return_to_menu()

    # ------------------------------------------------------------------
    def _position_in_front_of_player(self, distance_px):
        px, py = self.player.pos.x, self.player.pos.y
        offsets = {
            "up": (0, -distance_px),
            "down": (0, distance_px),
            "left": (-distance_px, 0),
            "right": (distance_px, 0),
        }
        ox, oy = offsets.get(self.player.facing, (0, distance_px))
        return (px + ox, py + oy)

    # ------------------------------------------------------------------
    # UPDATE
    # ------------------------------------------------------------------
    def update(self, dt):
        if self.state == states.PLAYING:
            self._update_playing(dt)
        elif self.state == states.LEVEL_COMPLETE:
            self.level_complete_timer -= dt
            if self.level_complete_timer <= 0:
                self.advance_level()

        if self.hud_quip_timer > 0:
            self.hud_quip_timer -= dt

    def _update_playing(self, dt):
        keys = pygame.key.get_pressed()
        self.player.handle_movement(keys, dt, self.level.solid_rects, self.level.bounds)

        if self.player.moving:
            self._footstep_timer -= dt
            if self._footstep_timer <= 0:
                self.audio.play("footsteps", volume=0.5)
                self._footstep_timer = 0.32
        else:
            self._footstep_timer = 0.0

        if self.player.carrying is not None and self.egg.tier != "normal":
            self._wobble_audio_timer -= dt
            if self._wobble_audio_timer <= 0:
                self.audio.play("egg_wobble", volume=0.45)
                self._wobble_audio_timer = 1.1
        else:
            self._wobble_audio_timer = 0.0

        if self.egg.carried:
            self.egg.follow(self.player.center, self.player.facing)
        self.egg.update(dt)

        before_condition = self.egg.condition
        result = self.level.update(dt, self.player, self.egg, self.audio)

        if result == "ready_to_place":
            if not self.delivery_ready:
                self.audio.play("delivery_ready")
                self.hud_quip = "GENTLY PRESS E TO PLACE THE EGG."
                self.hud_quip_timer = 2.0
            self.delivery_ready = True
        else:
            self.delivery_ready = False

        if self.egg.condition < before_condition:
            self._show_damage_quip(before_condition - self.egg.condition)

        if self.egg.broken:
            self.state = states.GAME_OVER
            self.audio.stop_music()
            self.audio.play("game_over")
            return

    def _show_damage_quip(self, amount):
        import random
        if amount >= settings.DAMAGE_LARGE_LOW:
            self.hud_quip = random.choice(BIG_HIT_QUIPS)
        else:
            self.hud_quip = random.choice(BUMP_QUIPS)
        self.hud_quip_timer = 1.6

    # ------------------------------------------------------------------
    # DRAW
    # ------------------------------------------------------------------
    def draw(self):
        if self.state == states.MENU:
            self.menu_rects = ui.draw_main_menu(self.screen, self.fonts, self.menu_selected_index)
        elif self.state == states.HOW_TO_PLAY:
            ui.draw_how_to_play(self.screen, self.fonts)
        elif self.state == states.INTRO:
            self._draw_intro()
        elif self.state in (states.PLAYING, states.PAUSED):
            self._draw_playing()
            if self.state == states.PAUSED:
                self._draw_pause_overlay()
        elif self.state == states.LEVEL_COMPLETE:
            self._draw_playing()
            self._draw_level_complete_overlay()
        elif self.state == states.GAME_OVER:
            self._draw_game_over()
        elif self.state == states.VICTORY:
            self._draw_victory()

    def _draw_intro(self):
        self.screen.fill(settings.BLACK)
        line = INTRO_LINES[min(self.intro_index, len(INTRO_LINES) - 1)]
        label = self.fonts["large"].render(line, True, settings.WHITE)
        self.screen.blit(label, label.get_rect(
            center=(settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT // 2)))

        hint = self.fonts["tiny"].render("Click or press ENTER to continue", True, settings.GRAY)
        self.screen.blit(hint, hint.get_rect(
            center=(settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT - 80)))

    def _draw_playing(self):
        self.level.draw_background(self.screen)
        self.level.draw_exit_marker(self.screen, self.delivery_ready)
        self.level.draw_obstacles(self.screen)

        if not self.egg.carried:
            self.egg.draw(self.screen)

        self.player.draw(self.screen)

        if self.egg.carried:
            self.egg.draw(self.screen)

        self.level.draw_npcs(self.screen, self.fonts["tiny"], self.player.center)

        objective = (
            "Press E to gently place the egg."
            if self.delivery_ready else self.level.instruction
        )
        ui.draw_hud(
            self.screen, self.fonts,
            self.current_level_index + 1, self.level.name,
            objective, self.egg.condition,
        )

        if self.hud_quip_timer > 0:
            quip_surf = self.fonts["small"].render(self.hud_quip, True, settings.WHITE)
            bg = pygame.Surface((quip_surf.get_width() + 24, quip_surf.get_height() + 14), pygame.SRCALPHA)
            bg.fill((20, 20, 25, 180))
            bg_rect = bg.get_rect(center=(settings.SCREEN_WIDTH // 2, 130))
            self.screen.blit(bg, bg_rect)
            self.screen.blit(quip_surf, quip_surf.get_rect(center=bg_rect.center))

    def _draw_pause_overlay(self):
        overlay = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        self.screen.blit(overlay, (0, 0))

        title = self.fonts["large"].render("PAUSED", True, settings.WHITE)
        self.screen.blit(title, title.get_rect(
            center=(settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT // 2 - 30)))

        hint = self.fonts["small"].render("ESC to resume  \u2014  M for main menu", True, settings.LIGHT_GRAY)
        self.screen.blit(hint, hint.get_rect(
            center=(settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT // 2 + 30)))

    def _draw_level_complete_overlay(self):
        overlay = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((10, 30, 15, 170))
        self.screen.blit(overlay, (0, 0))

        title = self.fonts["large"].render("LEVEL COMPLETE", True, settings.CREAM)
        self.screen.blit(title, title.get_rect(
            center=(settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT // 2 - 20)))

        hint = self.fonts["small"].render("Press ENTER to continue", True, settings.LIGHT_GRAY)
        self.screen.blit(hint, hint.get_rect(
            center=(settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT // 2 + 40)))

    def _draw_game_over(self):
        self.screen.fill((25, 12, 12))
        title = self.fonts["large"].render(GAME_OVER_TITLE, True, settings.RED)
        self.screen.blit(title, title.get_rect(
            center=(settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT // 2 - 60)))

        y = settings.SCREEN_HEIGHT // 2
        for line in GAME_OVER_LINES:
            label = self.fonts["small"].render(line, True, settings.LIGHT_GRAY)
            self.screen.blit(label, label.get_rect(center=(settings.SCREEN_WIDTH // 2, y)))
            y += 36

    def _draw_victory(self):
        self.screen.fill((18, 30, 20))
        y = 200
        for i, line in enumerate(VICTORY_LINES):
            font = self.fonts["large"] if i < 2 else self.fonts["small"]
            color = settings.CREAM if i < 2 else settings.LIGHT_GRAY
            label = font.render(line, True, color)
            self.screen.blit(label, label.get_rect(center=(settings.SCREEN_WIDTH // 2, y)))
            y += 60 if i < 2 else 38

        hint = self.fonts["tiny"].render("Press ENTER to return to the menu", True, settings.GRAY)
        self.screen.blit(hint, hint.get_rect(center=(settings.SCREEN_WIDTH // 2, y + 30)))
