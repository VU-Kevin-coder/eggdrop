"""
entities/npc.py
----------------
Small, static (or gently wandering) characters that comment on the
player's very serious egg mission. Dialogue is short by design - the
gameplay is the story, not the NPCs.
"""

import math
import pygame

import settings
from game import assets


class NPC:
    def __init__(self, x, y, line, size=(44, 60), color=settings.ORANGE,
                 wander_range=0, is_distractor=False):
        self.pos = pygame.Vector2(x, y)
        self.start_pos = pygame.Vector2(x, y)
        self.line = line
        self.size = size
        self.image = assets.load_npc_image(size, color)
        self.wander_range = wander_range
        self.is_distractor = is_distractor
        self._t = 0.0

    @property
    def rect(self):
        w, h = self.size
        return pygame.Rect(int(self.pos.x - w / 2), int(self.pos.y - h / 2), w, h)

    def update(self, dt):
        if self.wander_range > 0:
            self._t += dt
            self.pos.x = self.start_pos.x + math.sin(self._t * 0.8) * self.wander_range

    def draw(self, surface, font, player_center, show_radius=110):
        w, h = self.size
        surface.blit(self.image, (int(self.pos.x - w / 2), int(self.pos.y - h / 2)))

        dist = (player_center - self.pos).length()
        if dist <= show_radius and self.line:
            self._draw_speech_bubble(surface, font)

    def _draw_speech_bubble(self, surface, font):
        text_surf = font.render(self.line, True, settings.BLACK)
        pad = 8
        bubble_w = text_surf.get_width() + pad * 2
        bubble_h = text_surf.get_height() + pad * 2
        bubble_x = int(self.pos.x - bubble_w / 2)
        bubble_y = int(self.pos.y - self.size[1] / 2 - bubble_h - 10)

        bubble_rect = pygame.Rect(bubble_x, bubble_y, bubble_w, bubble_h)
        pygame.draw.rect(surface, settings.WHITE, bubble_rect, border_radius=8)
        pygame.draw.rect(surface, settings.DARK_GRAY, bubble_rect, width=2, border_radius=8)
        tail = [
            (self.pos.x - 6, bubble_rect.bottom),
            (self.pos.x + 6, bubble_rect.bottom),
            (self.pos.x, bubble_rect.bottom + 8),
        ]
        pygame.draw.polygon(surface, settings.WHITE, tail)
        surface.blit(text_surf, (bubble_x + pad, bubble_y + pad))
