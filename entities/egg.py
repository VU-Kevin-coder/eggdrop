"""
entities/egg.py
----------------
The egg. This is the star of the game - the mechanic, the challenge,
and the joke, all in one small oval object.
"""

import random
import math

import pygame

import settings
from game import assets


class Egg:
    def __init__(self, x, y):
        self.pos = pygame.Vector2(x, y)
        self.size = settings.EGG_SIZE
        self.condition = settings.EGG_START_CONDITION
        self.carried = False
        self.broken = False

        self.shake_timer = 0.0
        self.shake_strength = 0.0
        self._wobble_t = random.uniform(0, 10)
        self._last_tier = self._tier_for(self.condition)

        self._surface_cache_key = None
        self._surface_cache = None

        # bookkeeping used by Level to avoid re-damaging every single
        # frame while overlapping the same hazard
        self.hazard_cooldowns = {}

    # ------------------------------------------------------------------
    @property
    def rect(self):
        w, h = self.size
        return pygame.Rect(int(self.pos.x - w / 2), int(self.pos.y - h / 2), w, h)

    @staticmethod
    def _tier_for(condition):
        if condition <= settings.TIER_BROKEN:
            return "broken"
        if condition > settings.TIER_SMALL_CRACK:
            return "normal"
        if condition > settings.TIER_CRACKED:
            return "small_crack"
        if condition > settings.TIER_CRITICAL:
            return "cracked"
        return "critical"

    @property
    def tier(self):
        return self._tier_for(self.condition)

    # ------------------------------------------------------------------
    def pick_up(self, audio):
        self.carried = True
        audio.play("pickup")

    def place_down(self, pos=None, audio=None):
        """A deliberate, gentle placement - no damage."""
        self.carried = False
        if pos is not None:
            self.pos = pygame.Vector2(pos)
        if audio is not None:
            audio.play("place")

    def drop_down(self, pos=None, audio=None):
        """An uncontrolled drop that damages the egg immediately."""
        if not self.carried:
            return
        self.carried = False
        if pos is not None:
            self.pos = pygame.Vector2(pos)
        self.damage(settings.DAMAGE_KNOCKBACK_DROP, audio)
        if audio is not None:
            audio.play("drop")

    def force_drop(self, audio):
        """The egg gets knocked out of the player's hands - this hurts."""
        if self.carried:
            self.carried = False
            self.damage(settings.DAMAGE_KNOCKBACK_DROP, audio)

    # ------------------------------------------------------------------
    def damage(self, amount, audio):
        if self.broken or amount <= 0:
            return

        before_tier = self.tier
        self.condition = max(0, self.condition - amount)
        after_tier = self.tier

        self.shake_timer = 0.35
        self.shake_strength = min(10, 3 + amount * 0.18)

        if audio is not None:
            if amount >= settings.DAMAGE_LARGE_LOW:
                audio.play("large_impact")
            else:
                audio.play("small_impact")

        if after_tier != before_tier and after_tier in ("small_crack", "cracked", "critical"):
            if audio is not None:
                audio.play("crack")

        if self.condition <= 0 and not self.broken:
            self.broken = True
            self.carried = False
            if audio is not None:
                audio.play("egg_break")

    def heal(self, amount):
        """Restore condition without exceeding a perfect egg."""
        if self.broken or amount <= 0:
            return 0
        before = self.condition
        self.condition = min(settings.EGG_START_CONDITION, self.condition + amount)
        return self.condition - before

    # ------------------------------------------------------------------
    def update(self, dt):
        self._wobble_t += dt
        if self.shake_timer > 0:
            self.shake_timer = max(0.0, self.shake_timer - dt)

    def follow(self, player_pos, facing):
        """Egg visually rides with the player while carried."""
        if not self.carried:
            return
        ox, oy = settings.EGG_CARRY_OFFSET
        self.pos = pygame.Vector2(player_pos.x + ox, player_pos.y + oy)

    # ------------------------------------------------------------------
    def _current_shake_offset(self):
        offset = pygame.Vector2(0, 0)

        # short punchy shake right after taking damage
        if self.shake_timer > 0:
            mag = self.shake_strength * (self.shake_timer / 0.35)
            offset.x += random.uniform(-mag, mag)
            offset.y += random.uniform(-mag, mag)

        # continuous wobble that grows as the egg gets more fragile
        wobble_amp = {
            "normal": 0.0,
            "small_crack": 0.6,
            "cracked": 1.6,
            "critical": 3.2,
            "broken": 0.0,
        }[self.tier]
        if wobble_amp > 0:
            offset.x += math.sin(self._wobble_t * 9) * wobble_amp
            offset.y += math.cos(self._wobble_t * 7) * wobble_amp * 0.5

        return offset

    def draw(self, surface):
        w, h = self.size
        crack_seed = int(self._wobble_t * 3)  # cracks re-jitter a few times/sec, not every frame
        egg_surf = assets.draw_egg_surface(self.condition, self.size, wobble_seed=crack_seed)

        offset = self._current_shake_offset()
        draw_pos = (
            int(self.pos.x - w / 2 + offset.x),
            int(self.pos.y - h / 2 + offset.y),
        )
        surface.blit(egg_surf, draw_pos)
