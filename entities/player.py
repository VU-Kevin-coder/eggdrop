"""
entities/player.py
-------------------
The player character: movement, simple walk animation, and the
collider used against level obstacles.
"""

import pygame

import settings
from game import assets


def move_and_collide(rect, dx, dy, solids):
    collided = False

    rect.x += dx
    for solid in solids:
        if rect.colliderect(solid):
            collided = True
            if dx > 0:
                rect.right = solid.left
            elif dx < 0:
                rect.left = solid.right

    rect.y += dy
    for solid in solids:
        if rect.colliderect(solid):
            collided = True
            if dy > 0:
                rect.bottom = solid.top
            elif dy < 0:
                rect.top = solid.bottom

    return rect, collided


def clamp_to_bounds(rect, bounds):
    if rect.left < bounds.left:
        rect.left = bounds.left
    if rect.right > bounds.right:
        rect.right = bounds.right
    if rect.top < bounds.top:
        rect.top = bounds.top
    if rect.bottom > bounds.bottom:
        rect.bottom = bounds.bottom
    return rect


def distance(a_center, b_center):
    ax, ay = a_center
    bx, by = b_center
    return ((ax - bx) ** 2 + (ay - by) ** 2) ** 0.5


class Player:
    def __init__(self, x, y):
        self.pos = pygame.Vector2(x, y)
        self.size = settings.PLAYER_SIZE
        self.speed = settings.PLAYER_SPEED
        self.facing = "down"
        self.moving = False
        self.walk_phase = 0.0
        self.carrying = None  # reference to an Egg, or None

    # ------------------------------------------------------------------
    @property
    def rect(self):
        w, h = self.size
        ix, iy = settings.PLAYER_COLLIDER_INSET
        return pygame.Rect(
            int(self.pos.x - w / 2 + ix / 2),
            int(self.pos.y - h / 2 + iy / 2),
            w - ix,
            h - iy,
        )

    @property
    def center(self):
        return pygame.Vector2(self.pos.x, self.pos.y)

    # ------------------------------------------------------------------
    def handle_movement(self, keys, dt, solids, bounds, speed_multiplier=1.0):
        dx = dy = 0.0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= 1
            self.facing = "left"
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += 1
            self.facing = "right"
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy -= 1
            self.facing = "up"
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy += 1
            self.facing = "down"

        self.moving = (dx != 0 or dy != 0)

        if self.moving:
            length = (dx ** 2 + dy ** 2) ** 0.5
            dx, dy = dx / length, dy / length
            move_speed = self.speed * speed_multiplier
            step_x = dx * move_speed * dt
            step_y = dy * move_speed * dt

            rect = self.rect
            new_rect, _ = move_and_collide(rect, step_x, step_y, solids)
            new_rect = clamp_to_bounds(new_rect, bounds)

            self.pos.x = new_rect.centerx
            self.pos.y = new_rect.centery

            self.walk_phase = (self.walk_phase + dt * 3.2) % 1.0
        else:
            self.walk_phase = 0.0

    # ------------------------------------------------------------------
    def draw(self, surface):
        frame = assets.load_player_frame(self.walk_phase, self.size)
        w, h = self.size
        surface.blit(frame, (int(self.pos.x - w / 2), int(self.pos.y - h / 2)))
