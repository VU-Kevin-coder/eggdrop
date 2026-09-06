# DON'T DROP THE EGG

*A small, extremely serious game about a very ordinary task.*

## Concept

You have one job: carry one (1) egg from your house to your
grandmother's, across town, without breaking it. The game treats this
completely mundane errand like a top-secret military operation.

## Story

You receive an urgent message:

> IMPORTANT.
> Take this egg to Grandma.
> Do NOT drop it.

And so, **Operation Egg Delivery** begins. There are no long
cutscenes and no dialogue trees - the story is told through short
messages, a few NPC comments, and the sheer drama of carrying an egg
across five increasingly hazardous locations.

## Features

- A real egg-shaped egg (not a rectangle!) with a full condition
  system: it cracks visibly and behaves less predictably the more
  damaged it gets, and shatters for good at 0%.
- Five short, hand-designed levels that each introduce a new
  mechanic: carrying, obstacles, timed hazards, multiple hazards, and
  a final delivery.
- A physics-lite damage system: small bumps, medium hits, large
  impacts, and the occasional "major fall," all clearly readable from
  the egg's cracks and the condition bar.
- A full asset fallback system - the game runs (and still looks like
  a real game, not a placeholder) even with zero image or sound files
  added. Drop in your own PNGs/WAVs later with **no code changes**.
- Simple, readable HUD: level, egg condition, objective, controls.
- Full state machine: menu, story intro, gameplay, pause, level
  complete, game over (with retry), and victory.
- Sound feedback tied to actual gameplay events, not just background
  music - picking up, dropping, impacts, cracking, breaking, and
  completing levels each have their own cue (silently skipped if the
  sound file isn't present).

## Controls

| Key            | Action                        |
|----------------|-------------------------------|
| WASD / Arrows  | Move                          |
| E              | Pick up the egg                |
| SPACE          | Gently place the egg down      |
| ESC            | Pause / resume                 |
| R              | Retry after breaking the egg   |

## Installation

Requires Python 3 and Pygame.

```bash
pip install -r requirements.txt
```

## How to run

```bash
python main.py
```

or

```bash
python3 main.py
```

## Assets folder

Everything under `assets/` is optional - see `assets/README.md` for
the exact filenames the game looks for (backgrounds, player/NPC/egg
sprites, sound effects, and music). Anything missing is replaced by a
small procedurally-drawn fallback, so the game is playable and
presentable right out of the box.

## Project structure

```
dont_drop_the_egg/
├── main.py                 entry point
├── settings.py              all shared constants
│
├── game/
│   ├── game.py               main loop, state machine + state constants
│   ├── level.py              level data + Level class
│   ├── player.py             movement, animation, collider
│   ├── egg.py                condition/damage/wobble/cracks
│   ├── obstacle.py           solid + moving-hazard objects
│   ├── npc.py                proximity speech bubbles
│   ├── assets.py             image loading + procedural fallbacks
│   └── audio.py              sound/music with safe fallback
│
├── ui.py                                main menu, instructions + HUD
│
├── assets/
│   ├── backgrounds/  characters/  objects/  sounds/  music/
│
└── README.md
```

## Technologies used

- Python 3
- Pygame

## Design notes

The egg is the whole game. Every system - movement, obstacles,
hazards, sound, and the HUD - exists to make carrying that egg feel
tense, funny, and readable. The project intentionally avoids an
inventory system, dialogue trees, RPG mechanics, a physics engine, or
an entity-component-system framework: it's a small student project
about an egg, not a game engine.
