import os
import random
import math

import pygame

import settings


def try_load_image(path, size=None, mode="stretch"):
    """Attempt to load an image from disk. Returns a Surface or None."""
    if not path or not os.path.isfile(path):
        return None
    try:
        image = pygame.image.load(path).convert_alpha()
        if size is not None:
            if mode == "fit":
                image = _fit_image(image, size)
            elif mode == "cover":
                image = _cover_image(image, size)
            else:
                image = pygame.transform.smoothscale(image, size)
        return image
    except Exception:
        return None


def _fit_image(image, size):
    """Scale an image into a logical sprite box without changing its shape."""
    target_w, target_h = size
    source_w, source_h = image.get_size()
    scale = min(target_w / source_w, target_h / source_h)
    scaled_size = (max(1, round(source_w * scale)), max(1, round(source_h * scale)))
    scaled = pygame.transform.smoothscale(image, scaled_size)
    fitted = pygame.Surface(size, pygame.SRCALPHA)
    fitted.blit(scaled, scaled.get_rect(center=fitted.get_rect().center))
    return fitted


def _cover_image(image, size):
    """Scale an image to cover a viewport, cropping only excess edges."""
    target_w, target_h = size
    source_w, source_h = image.get_size()
    scale = max(target_w / source_w, target_h / source_h)
    scaled_size = (max(1, round(source_w * scale)), max(1, round(source_h * scale)))
    scaled = pygame.transform.smoothscale(image, scaled_size)
    crop = scaled.get_rect()
    crop.size = size
    crop.center = scaled.get_rect().center
    return scaled.subsurface(crop).copy()


def make_fallback_player(size, walk_phase=0.0):
    """A small readable 'person' made of primitives - not a rectangle blob."""
    w, h = size
    surf = pygame.Surface(size, pygame.SRCALPHA)

    bob = math.sin(walk_phase * math.pi * 2) * 2

    body_color = settings.BLUE
    skin = settings.SKIN

    leg_swing = math.sin(walk_phase * math.pi * 2) * 6
    leg_w = w * 0.18
    leg_top = h * 0.62
    pygame.draw.rect(surf, settings.DARK_GRAY,
                      (w * 0.30 - leg_swing * 0.15, leg_top, leg_w, h * 0.34),
                      border_radius=4)
    pygame.draw.rect(surf, settings.DARK_GRAY,
                      (w * 0.55 + leg_swing * 0.15, leg_top, leg_w, h * 0.34),
                      border_radius=4)

    body_rect = pygame.Rect(w * 0.20, h * 0.32 + bob, w * 0.60, h * 0.36)
    pygame.draw.rect(surf, body_color, body_rect, border_radius=10)

    arm_w = w * 0.14
    pygame.draw.rect(surf, body_color,
                      (w * 0.06, h * 0.38 + bob, arm_w, h * 0.26), border_radius=6)
    pygame.draw.rect(surf, body_color,
                      (w * 0.80, h * 0.38 - bob, arm_w, h * 0.26), border_radius=6)

    head_r = w * 0.26
    head_center = (w * 0.5, h * 0.24 + bob)
    pygame.draw.circle(surf, skin, head_center, head_r)
    pygame.draw.circle(surf, settings.DARK_BROWN,
                        (head_center[0], head_center[1] - head_r * 0.55),
                        head_r * 0.9, width=0)
    pygame.draw.circle(surf, settings.BLACK,
                        (head_center[0] - head_r * 0.35, head_center[1]), 2)
    pygame.draw.circle(surf, settings.BLACK,
                        (head_center[0] + head_r * 0.35, head_center[1]), 2)

    return surf


_player_fallback_cache = {}


def load_player_frame(walk_phase, size=settings.PLAYER_SIZE):
    """
    Returns the player's current frame. If assets/characters/player.png
    exists, it is used as-is with a tiny procedural bob applied so a
    single static PNG still reads as "animated" while walking.
    """
    real = try_load_image(settings.PLAYER_IMAGE_PATH, size, mode="fit")
    if real is not None:
        bob = int(math.sin(walk_phase * math.pi * 2) * 3)
        framed = pygame.Surface(size, pygame.SRCALPHA)
        framed.blit(real, (0, bob))
        return framed

    key = round(walk_phase, 2)
    if key not in _player_fallback_cache:
        if len(_player_fallback_cache) >= 40:
            _player_fallback_cache.clear()
        _player_fallback_cache[key] = make_fallback_player(size, walk_phase)
    return _player_fallback_cache[key]


def make_fallback_egg_base(size):
    """A believable egg silhouette made from an ellipse, not a rectangle."""
    w, h = size
    surf = pygame.Surface(size, pygame.SRCALPHA)

    cx, cy = w / 2, h / 2
    points = []
    steps = 24
    for i in range(steps):
        angle = (i / steps) * math.pi * 2
        rx = (w / 2) * (0.86 if math.cos(angle) < 0 else 1.0)
        ry = (h / 2)
        taper = 1.0 - 0.18 * max(0, math.sin(angle))
        x = cx + math.cos(angle) * rx * taper
        y = cy + math.sin(angle) * ry
        points.append((x, y))

    pygame.draw.polygon(surf, settings.CREAM, points)
    pygame.draw.polygon(surf, (210, 195, 165), points, width=2)

    highlight = pygame.Surface(size, pygame.SRCALPHA)
    pygame.draw.ellipse(highlight, (255, 255, 255, 110),
                         (w * 0.20, h * 0.14, w * 0.28, h * 0.30))
    surf.blit(highlight, (0, 0))

    shadow = pygame.Surface(size, pygame.SRCALPHA)
    pygame.draw.ellipse(shadow, (0, 0, 0, 40),
                         (w * 0.15, h * 0.78, w * 0.7, h * 0.16))
    surf.blit(shadow, (0, 0))

    return surf


_egg_base_cache = None
_egg_base_is_real = False


def get_egg_base(size=settings.EGG_SIZE):
    """Loads the real egg.png once, or builds the fallback once. Cached."""
    global _egg_base_cache, _egg_base_is_real
    if _egg_base_cache is None:
        real = try_load_image(settings.EGG_IMAGE_PATH, size, mode="fit")
        if real is not None:
            _egg_base_cache = real
            _egg_base_is_real = True
        else:
            _egg_base_cache = make_fallback_egg_base(size)
            _egg_base_is_real = False
    return _egg_base_cache


def _draw_crack_line(surf, start, end, width=2):
    pygame.draw.line(surf, (90, 70, 50), start, end, width)


def draw_egg_surface(condition, size=settings.EGG_SIZE, wobble_seed=0):
    """
    Builds a fresh egg surface for this frame: base image/fallback plus
    crack overlays appropriate to the current condition tier. wobble_seed
    slightly varies crack jitter each call so cracks feel "alive" without
    being randomly repositioned every single frame (caller controls how
    often this is recomputed).
    """
    w, h = size
    base = get_egg_base(size).copy()

    rng = random.Random(int(wobble_seed))

    if condition <= settings.TIER_BROKEN:
        pygame.draw.line(base, (90, 70, 50), (w * 0.15, h * 0.5), (w * 0.85, h * 0.55), 3)
        return base

    if condition > settings.TIER_SMALL_CRACK:
        return base

    if condition > settings.TIER_CRACKED:
        cx, cy = w * 0.5, h * 0.4
        _draw_crack_line(base, (cx - 4, cy - 8), (cx + 3, cy + 6), 2)
        _draw_crack_line(base, (cx + 3, cy + 6), (cx - 2, cy + 14), 2)

    elif condition > settings.TIER_CRITICAL:
        for i in range(3):
            ox = rng.uniform(-3, 3)
            cx, cy = w * (0.35 + i * 0.18), h * 0.35
            _draw_crack_line(base, (cx - 5 + ox, cy - 10), (cx + 4 + ox, cy + 8), 2)
            _draw_crack_line(base, (cx + 4 + ox, cy + 8), (cx - 3 + ox, cy + 18), 2)

    else:
        for i in range(5):
            ox = rng.uniform(-4, 4)
            oy = rng.uniform(-4, 4)
            cx, cy = w * (0.25 + i * 0.13), h * (0.28 + (i % 2) * 0.12)
            _draw_crack_line(base, (cx - 6 + ox, cy - 12 + oy), (cx + 5 + ox, cy + 10 + oy), 2)
            _draw_crack_line(base, (cx + 5 + ox, cy + 10 + oy), (cx - 4 + ox, cy + 20 + oy), 2)
        tint = pygame.Surface(size, pygame.SRCALPHA)
        tint.fill((255, 220, 150, 35))
        base.blit(tint, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

    return base


def make_fallback_background(size, scheme):
    """
    Procedural placeholder background so every level looks like a real
    place (floor, walls, sky, road, etc.) instead of a flat color.
    scheme: one of "house", "market", "road", "construction", "grandma"
    """
    w, h = size
    surf = pygame.Surface(size)

    if scheme == "house":
        surf.fill((235, 220, 195))
        pygame.draw.rect(surf, (200, 175, 140), (0, h * 0.65, w, h * 0.35))
        for x in range(0, w, 96):
            pygame.draw.line(surf, (185, 160, 125), (x, h * 0.65), (x, h))
        pygame.draw.rect(surf, (170, 130, 90), (0, 0, w, 14))

    elif scheme == "market":
        surf.fill((225, 210, 175))
        pygame.draw.rect(surf, (195, 175, 140), (0, h * 0.7, w, h * 0.3))
        for x in range(0, w, 140):
            pygame.draw.rect(surf, (200, 90, 80), (x, h * 0.12, 90, 26))

    elif scheme == "road":
        surf.fill(settings.SKY_BLUE)
        pygame.draw.rect(surf, (110, 150, 90), (0, h * 0.15, w, h * 0.15))
        pygame.draw.rect(surf, (70, 70, 75), (0, h * 0.3, w, h * 0.4))
        for x in range(0, w, 70):
            pygame.draw.rect(surf, (230, 220, 90), (x, h * 0.5 - 4, 40, 8))
        pygame.draw.rect(surf, (110, 150, 90), (0, h * 0.7, w, h * 0.3))

    elif scheme == "construction":
        surf.fill((210, 190, 150))
        for i in range(0, w, 40):
            pygame.draw.line(surf, (190, 170, 130), (i, 0), (i, h), 1)
        pygame.draw.rect(surf, (225, 170, 60), (0, h * 0.85, w, h * 0.15))
        for x in range(20, w, 160):
            pygame.draw.rect(surf, (225, 170, 60), (x, h * 0.85 - 30, 60, 30))
            pygame.draw.line(surf, (60, 60, 60), (x, h * 0.85 - 30), (x + 60, h * 0.85), 3)
            pygame.draw.line(surf, (60, 60, 60), (x + 60, h * 0.85 - 30), (x, h * 0.85), 3)

    elif scheme == "grandma":
        surf.fill((215, 235, 210))
        pygame.draw.rect(surf, (190, 165, 130), (0, h * 0.72, w, h * 0.28))
        pygame.draw.rect(surf, (150, 100, 70), (w * 0.42, h * 0.35, w * 0.16, h * 0.4))
        pygame.draw.polygon(surf, (140, 70, 60),
                             [(w * 0.36, h * 0.35), (w * 0.5, h * 0.18), (w * 0.64, h * 0.35)])

    else:
        surf.fill(settings.LIGHT_GRAY)

    return surf


_background_cache = {}


def load_background(name, scheme, size=(settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT)):
    key = (name, size)
    if key in _background_cache:
        return _background_cache[key]

    path = os.path.join(settings.BACKGROUNDS_DIR, name)
    real = try_load_image(path, size, mode="cover")
    if real is None:
        bg = make_fallback_background(size, scheme)
    else:
        bg = make_fallback_background(size, scheme)
        bg.blit(real, (0, 0))
    _background_cache[key] = bg
    return bg


_destination_cache = {}


def load_destination(name, size):
    """Load a destination illustration into a fixed-size transparent box."""
    key = (name, size)
    if key in _destination_cache:
        return _destination_cache[key]

    path = os.path.join(settings.BACKGROUNDS_DIR, name)
    destination = try_load_image(path, size, mode="fit")
    if destination is None:
        destination = pygame.Surface(size, pygame.SRCALPHA)
    _destination_cache[key] = destination
    return destination


def make_fallback_box(size, color=settings.BROWN):
    w, h = size
    surf = pygame.Surface(size, pygame.SRCALPHA)
    shadow = pygame.Rect(max(2, int(w * 0.04)), max(3, int(h * 0.06)),
                         max(1, w - max(2, int(w * 0.04))),
                         max(1, h - max(3, int(h * 0.06))))
    pygame.draw.rect(surf, (35, 28, 24, 110), shadow, border_radius=8)

    body = pygame.Rect(0, 0, w, max(1, h - max(2, int(h * 0.06))))
    pygame.draw.rect(surf, color, body, border_radius=7)
    pygame.draw.rect(surf, (255, 235, 190, 55), body, width=2, border_radius=7)

    board_count = max(2, min(5, int(h / 34)))
    for index in range(1, board_count):
        y = int(h * index / board_count)
        pygame.draw.line(surf, (70, 45, 30, 120), (5, y), (max(5, w - 5), y), 2)
    if w > 45 and h > 35:
        pygame.draw.line(surf, (255, 220, 160, 80), (8, h - 10), (w - 10, 8), 3)
        pygame.draw.line(surf, (65, 40, 28, 100), (8, 8), (w - 10, h - 10), 3)

    bolt_radius = max(2, min(5, int(min(w, h) * 0.06)))
    for x in (max(7, int(w * 0.12)), min(w - 7, int(w * 0.88))):
        for y in (max(7, int(h * 0.16)), min(h - 7, int(h * 0.84))):
            pygame.draw.circle(surf, (45, 42, 38), (x, y), bolt_radius)
            pygame.draw.circle(surf, (220, 200, 155), (x - 1, y - 1), max(1, bolt_radius // 2))
    return surf


def make_fallback_barrier(size, color=settings.YELLOW):
    """Draw a readable construction barrier with legs and warning stripes."""
    w, h = size
    surf = pygame.Surface(size, pygame.SRCALPHA)
    shadow_h = max(3, int(h * 0.1))
    pygame.draw.ellipse(surf, (25, 25, 25, 100), (w * 0.08, h - shadow_h, w * 0.84, shadow_h))

    rail_h = max(12, int(h * 0.36))
    rail_y = max(2, int(h * 0.24))
    rail = pygame.Rect(2, rail_y, max(1, w - 4), rail_h)
    pygame.draw.rect(surf, (45, 48, 48), rail, border_radius=4)
    pygame.draw.rect(surf, (215, 215, 195), rail.inflate(-4, -4), border_radius=2)

    stripe_w = max(10, int(h * 0.24))
    for x in range(-h, w + h, stripe_w * 2):
        pygame.draw.polygon(
            surf, color,
            [(x, rail.bottom), (x + stripe_w, rail.bottom),
             (x + stripe_w + rail_h, rail.top), (x + rail_h, rail.top)],
        )
    pygame.draw.rect(surf, (40, 42, 42), rail, width=3, border_radius=4)

    leg_w = max(5, int(w * 0.1))
    leg_top = rail.bottom - 2
    for x in (max(3, int(w * 0.12)), min(w - leg_w - 3, int(w * 0.78))):
        pygame.draw.polygon(surf, (55, 58, 57),
                            [(x, leg_top), (x + leg_w, leg_top),
                             (x + leg_w + 4, h - shadow_h), (x - 4, h - shadow_h)])
    return surf


def load_obstacle_image(filename, size, color=settings.BROWN):
    path = os.path.join(settings.OBJECTS_DIR, filename)
    real = try_load_image(path)
    if real is not None:
        visible_bounds = real.get_bounding_rect()
        if visible_bounds.width > 0 and visible_bounds.height > 0:
            real = real.subsurface(visible_bounds).copy()
        return pygame.transform.smoothscale(real, size)
    if filename == "construction_barrier.png":
        return make_fallback_barrier(size, color)
    return make_fallback_box(size, color)


def make_fallback_npc(size, color=settings.ORANGE):
    w, h = size
    surf = make_fallback_player(size)
    tint = pygame.Surface(size, pygame.SRCALPHA)
    tint.fill((*color, 90))
    surf.blit(tint, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
    return surf


def load_npc_image(size, color=settings.ORANGE):
    real = try_load_image(settings.NPC_IMAGE_PATH, size, mode="fit")
    return real if real is not None else make_fallback_npc(size, color)


def make_fallback_car(size, color=settings.RED):
    w, h = size
    surf = pygame.Surface(size, pygame.SRCALPHA)
    pygame.draw.rect(surf, color, (0, h * 0.25, w, h * 0.5), border_radius=8)
    pygame.draw.rect(surf, color, (w * 0.2, 0, w * 0.6, h * 0.5), border_radius=6)
    pygame.draw.rect(surf, (200, 230, 240), (w * 0.26, h * 0.08, w * 0.48, h * 0.32), border_radius=4)
    pygame.draw.circle(surf, settings.BLACK, (int(w * 0.2), int(h * 0.8)), int(h * 0.16))
    pygame.draw.circle(surf, settings.BLACK, (int(w * 0.8), int(h * 0.8)), int(h * 0.16))
    return surf


def load_car_image(filename, size, color=settings.RED):
    path = os.path.join(settings.OBJECTS_DIR, filename)
    real = try_load_image(path, size)
    return real if real is not None else make_fallback_car(size, color)
