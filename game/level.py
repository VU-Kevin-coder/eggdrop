"""
game/level.py
--------------
Levels are described as plain data in LEVEL_DATA and turned into real
Obstacle/NPC objects by the Level class. This keeps all 5 levels easy
to read, tune and compare at a glance, without five near-duplicate
files.
"""

import pygame

import settings
from game.obstacle import Obstacle
from game.npc import NPC
from game import assets

# Play area (leaves room at the top of the screen for the HUD)
PLAY_BOUNDS = pygame.Rect(20, 104, settings.SCREEN_WIDTH - 40, settings.SCREEN_HEIGHT - 124)


LEVEL_DATA = [
    # ------------------------------------------------------------ LEVEL 1
    {
        "name": "THE HOUSE",
        "background": ("house.png", "house"),
        "instruction": "Pick up the egg (E) and take it outside.",
        "player_start": (160, 630),
        "egg_start": (160, 520),
        "start_with_egg_carried": False,
        "exit_rect": pygame.Rect(1190, 300, 60, 170),
        "obstacles": [
            {"rect": (200, 520, 760, 42), "kind": "solid", "color": settings.BROWN},
            {"rect": (420, 360, 620, 42), "kind": "solid", "color": settings.DARK_BROWN},
            {"rect": (20, 200, 760, 42), "kind": "solid", "color": settings.BROWN},
        ],
        "distractors": [
            {"pos": (520, 360), "line": "You are carrying that VERY carefully, right?"},
        ],
        "npcs": [],
    },
    # ------------------------------------------------------------ LEVEL 2
    {
        "name": "THE MARKET",
        "background": ("market.png", "market"),
        "instruction": "Weave through the market. Don't bump the stalls.",
        "player_start": (90, 660),
        "egg_start": (90, 560),
        "start_with_egg_carried": False,
        "distractors": [
            {"pos": (520, 260), "line": "Look at me. Ignore the egg."},
        ],
        "exit_rect": pygame.Rect(1190, 290, 60, 170),
        "obstacles": [
            {"rect": (20, 540, 540, 42), "kind": "solid", "color": settings.ORANGE},
            {"rect": (620, 390, 400, 42), "kind": "solid", "color": settings.RED},
            {"rect": (220, 240, 620, 42), "kind": "solid", "color": settings.BROWN},
        ],
        "npcs": [
            {"pos": (470, 630), "line": "Careful with that!"},
            {"pos": (960, 340), "line": "Is that REALLY an egg?"},
        ],
    },
    # ------------------------------------------------------------ LEVEL 3
    {
        "name": "THE ROAD",
        "background": ("road.png", "road"),
        "instruction": "Time your crossing. The cars won't stop for an egg.",
        "player_start": (630, 660),
        "egg_start": (630, 570),
        "start_with_egg_carried": False,
        "distractors": [
            {"pos": (380, 560), "line": "The shortcut is definitely safe."},
        ],
        "exit_rect": pygame.Rect(560, 112, 160, 55),
        "obstacles": [
            {
                "rect": (100, 260, 100, 55), "kind": "hazard", "color": settings.RED,
                "damage": settings.DAMAGE_LARGE_LOW, "knockback": True,
                "move_axis": "x", "move_range": 480, "move_speed": 260,
            },
            {
                "rect": (1080, 430, 100, 55), "kind": "hazard", "color": (60, 90, 190),
                "damage": settings.DAMAGE_LARGE_LOW, "knockback": True,
                "move_axis": "x", "move_range": 480, "move_speed": 200,
            },
        ],
        "npcs": [],
    },
    # ------------------------------------------------------------ LEVEL 4
    {
        "name": "CONSTRUCTION SITE",
        "background": ("construction.png", "construction"),
        "instruction": "Mind the barriers and the swinging debris.",
        "player_start": (110, 650),
        "egg_start": (110, 540),
        "start_with_egg_carried": False,
        "distractors": [
            {"pos": (820, 220), "line": "Wait for it..."},
        ],
        "exit_rect": pygame.Rect(1190, 150, 60, 150),
        "obstacles": [
            {"rect": (380, 104, 40, 320), "kind": "solid", "color": settings.YELLOW},
            {"rect": (380, 500, 40, 200), "kind": "solid", "color": settings.YELLOW},
            {"rect": (760, 260, 40, 444), "kind": "solid", "color": settings.YELLOW},
            {
                "rect": (600, 130, 60, 60), "kind": "hazard", "color": settings.GRAY,
                "damage": settings.DAMAGE_LARGE_HIGH, "knockback": True,
                "move_axis": "y", "move_range": 220, "move_speed": 300,
            },
            {
                "rect": (960, 300, 60, 60), "kind": "hazard", "color": settings.GRAY,
                "damage": settings.DAMAGE_LARGE_HIGH, "knockback": True,
                "move_axis": "y", "move_range": 200, "move_speed": 240,
            },
            {
                "rect": (150, 420, 130, 70), "kind": "hazard", "color": (140, 120, 60),
                "damage": settings.DAMAGE_MEDIUM_LOW, "knockback": False,
            },
            {
                # an open pit - a genuine "major fall" hazard, clearly
                # darker than everything else so it reads as dangerous
                "rect": (940, 480, 90, 90), "kind": "hazard", "color": settings.BLACK,
                "damage": settings.DAMAGE_MAJOR_FALL, "knockback": False,
            },
        ],
        "npcs": [],
    },
    # ------------------------------------------------------------ LEVEL 5
    {
        "name": "GRANDMA'S HOUSE",
        "background": ("grandma_house.png", "grandma"),
        "instruction": "Almost there. Deliver the egg to Grandma's door.",
        "player_start": (110, 650),
        "egg_start": (110, 540),
        "start_with_egg_carried": False,
        "distractors": [
            {"pos": (520, 380), "line": "One little bump won't matter.", "wander_range": 100},
        ],
        "exit_rect": pygame.Rect(1150, 330, 90, 170),
        "obstacles": [
            {"rect": (20, 520, 640, 42), "kind": "solid", "color": settings.DARK_GREEN},
            {"rect": (360, 350, 600, 42), "kind": "solid", "color": settings.DARK_GREEN},
            {"rect": (20, 180, 640, 42), "kind": "solid", "color": settings.DARK_GREEN},
            {
                "rect": (500, 590, 60, 40), "kind": "hazard", "color": settings.GRAY,
                "damage": settings.DAMAGE_MEDIUM_LOW, "knockback": False,
                "move_axis": "x", "move_range": 260, "move_speed": 90,
            },
        ],
        "npcs": [
            {"pos": (930, 420), "line": "Oh, you brought the egg!"},
            {"pos": (520, 640), "line": "Woof!", "wander_range": 80},
        ],
    },
]


class Level:
    def __init__(self, index):
        self.index = index
        self.data = LEVEL_DATA[index]
        self.name = self.data["name"]
        self.instruction = self.data["instruction"]
        self.exit_rect = pygame.Rect(self.data["exit_rect"])
        self.player_start = self.data["player_start"]
        self.egg_start = self.data["egg_start"]
        self.start_with_egg_carried = self.data["start_with_egg_carried"]

        bg_name, bg_scheme = self.data["background"]
        self.background = assets.make_fallback_background(
            (settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT), bg_scheme
        )
        self.destination = assets.load_destination(bg_name, (220, 140))
        self.destination_rect = self.destination.get_rect(center=self.exit_rect.center)
        self.destination_rect.clamp_ip(pygame.Rect(
            0, 104, settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT - 104
        ))

        self.bounds = PLAY_BOUNDS
        self._bump_cooldown = 0.0

        self.reset_hazards()

    # ------------------------------------------------------------------
    def reset_hazards(self):
        """(Re)builds obstacles/npcs so patrol timers/positions are fresh."""
        self.obstacles = []
        for obs_data in self.data["obstacles"]:
            rect = pygame.Rect(obs_data["rect"])
            kind = obs_data.get("kind", "solid")
            color = obs_data.get("color", settings.BROWN)
            if kind == "solid":
                image = assets.load_obstacle_image("box.png", rect.size, color)
            elif obs_data.get("knockback"):
                image = assets.load_car_image("car.png", rect.size, color)
            else:
                image = assets.load_obstacle_image(
                    "construction_barrier.png", rect.size, color
                )
            self.obstacles.append(Obstacle(
                rect=rect,
                kind=kind,
                damage=obs_data.get("damage", 0),
                image=image,
                move_axis=obs_data.get("move_axis"),
                move_range=obs_data.get("move_range", 0),
                move_speed=obs_data.get("move_speed", 0),
                knockback=obs_data.get("knockback", False),
            ))

        self.npcs = []
        for npc_data in self.data["npcs"]:
            x, y = npc_data["pos"]
            self.npcs.append(NPC(
                x, y, npc_data["line"],
                wander_range=npc_data.get("wander_range", 0),
            ))
        for npc_data in self.data.get("distractors", []):
            x, y = npc_data["pos"]
            self.npcs.append(NPC(
                x, y, npc_data["line"], color=settings.RED,
                wander_range=npc_data.get("wander_range", 35),
                is_distractor=True,
            ))

        self._bump_cooldown = 0.0
        self._hazard_cooldowns = {}
        self._distractor_cooldowns = {}
        self._chick_cooldowns = {}

    @property
    def solid_rects(self):
        return [o.rect for o in self.obstacles if o.kind == "solid"]

    @property
    def hazard_obstacles(self):
        return [o for o in self.obstacles if o.kind == "hazard"]

    # ------------------------------------------------------------------
    def update(self, dt, player, egg, audio):
        for obstacle in self.obstacles:
            obstacle.update(dt)
        for npc in self.npcs:
            npc.update(dt)

        if self._bump_cooldown > 0:
            self._bump_cooldown -= dt

        # --- solid bump damage (only while carrying, gentle, cooled down) ---
        if player.carrying is not None and self._bump_cooldown <= 0:
            player_rect = player.rect
            for solid_rect in self.solid_rects:
                if player_rect.colliderect(solid_rect):
                    egg.damage(settings.DAMAGE_SMALL_BUMP, audio)
                    self._bump_cooldown = settings.BUMP_COOLDOWN
                    break

        # --- hazards: can hurt the egg whether it's carried or sitting ---
        egg_rect = egg.rect
        for i, hazard in enumerate(self.hazard_obstacles):
            cooldown_key = id(hazard)
            cooldown = self._hazard_cooldowns.get(cooldown_key, 0.0)
            if cooldown > 0:
                self._hazard_cooldowns[cooldown_key] = cooldown - dt
                continue

            touched = hazard.rect.colliderect(egg_rect) or (
                player.carrying is not None and hazard.rect.colliderect(player.rect)
            )
            if touched:
                egg.damage(hazard.damage, audio)
                self._hazard_cooldowns[cooldown_key] = 1.0
                if hazard.knockback and egg.carried:
                    # the impact already accounted for the damage above -
                    # this just knocks it out of the player's hands so
                    # they have to go recover it, without double-charging
                    egg.carried = False
                    player.carrying = None
                    egg.pos = pygame.Vector2(player.pos.x, player.pos.y + 40)

        # --- distractors: hecklers add small stress when touched ---
        if player.carrying is not None:
            # Friendly chicks restore a little condition when the player
            # carrying the egg passes through them.
            for npc in self.npcs:
                if npc.is_distractor or not npc.rect.colliderect(player.rect):
                    continue
                cooldown_key = id(npc)
                cooldown = max(0.0, self._chick_cooldowns.get(cooldown_key, 0.0) - dt)
                if cooldown <= 0:
                    egg.heal(settings.EGG_CHICK_HEAL)
                    self._chick_cooldowns[cooldown_key] = settings.CHICK_HEAL_COOLDOWN
                else:
                    self._chick_cooldowns[cooldown_key] = cooldown

            for npc in self.npcs:
                if not npc.is_distractor or not npc.rect.colliderect(player.rect):
                    continue
                cooldown_key = id(npc)
                cooldown = self._distractor_cooldowns.get(cooldown_key, 0.0)
                if cooldown <= 0:
                    egg.damage(settings.DAMAGE_DISTRACTOR_BUMP, audio)
                    audio.play("distractor", volume=0.7)
                    self._distractor_cooldowns[cooldown_key] = 1.2
                else:
                    self._distractor_cooldowns[cooldown_key] = cooldown - dt

        # --- exit check: entering arms a deliberate placement, never completes ---
        if player.rect.colliderect(self.exit_rect) and egg.carried and not egg.broken:
            return "ready_to_place"
        return None

    # ------------------------------------------------------------------
    def draw_background(self, surface):
        surface.blit(self.background, (0, 0))

    def draw_obstacles(self, surface):
        for obstacle in self.obstacles:
            obstacle.draw(surface)

    def draw_npcs(self, surface, font, player_center):
        for npc in self.npcs:
            npc.draw(surface, font, player_center)

    def draw_exit_marker(self, surface, ready=False):
        surface.blit(self.destination, self.destination_rect)
        if ready:
            pygame.draw.rect(
                surface, settings.YELLOW, self.destination_rect, width=4, border_radius=8
            )
