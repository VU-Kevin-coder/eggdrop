import pygame

from game import assets


class Obstacle:
    def __init__(self, rect, kind="solid", damage=0, image=None,
                 move_axis=None, move_range=0, move_speed=0, knockback=False,
                 warn_before_move=False):
        """
        rect: pygame.Rect - starting position/size
        kind: "solid" (blocks movement, e.g. furniture/stalls/barriers)
              "hazard" (does not necessarily block, deals damage on touch)
        damage: damage dealt to the egg on contact (hazards only)
        image: a pre-built pygame.Surface to draw, or None for a plain
               fallback box (still not a bare rectangle - assets.py
               draws a shaded crate look)
        move_axis: "x" or "y" if this obstacle patrols back and forth
        move_range: how far (pixels) it travels from its start position
        move_speed: pixels/second while patrolling
        knockback: if True, contact forces the player's egg out of
                   their hands (used for vehicles / falling debris)
        """
        self.start_rect = rect.copy()
        self.rect = rect.copy()
        self.kind = kind
        self.damage = damage
        self.image = image
        self.move_axis = move_axis
        self.move_range = move_range
        self.move_speed = move_speed
        self.knockback = knockback
        self._t = 0.0

    def is_moving(self):
        return self.move_axis is not None and self.move_range > 0

    def update(self, dt):
        if not self.is_moving():
            return
        self._t += dt

        span = self.move_range * 2
        period = span / max(1, self.move_speed)
        elapsed = self._t % period
        if elapsed < period / 2:
            offset = -self.move_range + self.move_speed * elapsed
        else:
            offset = self.move_range - self.move_speed * (elapsed - period / 2)

        if self.move_axis == "x":
            self.rect.x = int(self.start_rect.x + offset)
        else:
            self.rect.y = int(self.start_rect.y + offset)

    def draw(self, surface):
        if self.image is not None:
            surface.blit(self.image, self.rect.topleft)
        else:
            fallback = assets.make_fallback_box(self.rect.size)
            surface.blit(fallback, self.rect.topleft)
