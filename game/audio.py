"""
game/audio.py
-----------------
A tiny wrapper around pygame.mixer that NEVER crashes the game because
a .wav/.ogg file is missing. Every event-driven sound in the design
document is preloaded here (or silently skipped if absent).
"""

import os
import math
import struct
import pygame

import settings

# name -> filename inside assets/sounds/
SOUND_FILES = {
    "pickup": "pickup.wav",
    "drop": "drop.wav",
    "place": "place.wav",
    "delivery_ready": "delivery_ready.wav",
    "distractor": "distractor.wav",
    "footsteps": "footsteps.wav",
    "egg_wobble": "egg_wobble.wav",
    "small_impact": "small_impact.wav",
    "large_impact": "large_impact.wav",
    "crack": "crack.wav",
    "egg_break": "egg_break.wav",
    "button_click": "button_click.wav",
    "level_complete": "level_complete.wav",
    "game_over": "game_over.wav",
    "success": "success.wav",
}

MUSIC_FILES = {
    "menu": "menu_theme.ogg",
    "gameplay": "gameplay_theme.ogg",
    "victory": "victory_theme.ogg",
}


class AudioManager:
    def __init__(self):
        self.enabled = True
        try:
            pygame.mixer.init()
        except Exception:
            self.enabled = False

        self.sounds = {}
        self._current_music = None

        if self.enabled:
            for name, filename in SOUND_FILES.items():
                self.sounds[name] = self._load_sound(filename) or self._make_fallback_sound(name)

    def _load_sound(self, filename):
        path = os.path.join(settings.SOUNDS_DIR, filename)
        if not os.path.isfile(path):
            return None
        try:
            return pygame.mixer.Sound(path)
        except Exception:
            return None

    def _make_fallback_sound(self, name):
        """Create a tiny synthetic effect when the optional sound file is absent."""
        mixer_format = pygame.mixer.get_init()
        if mixer_format is None:
            return None
        frequency, sample_format, channels = mixer_format
        if sample_format != -16:
            return None

        profiles = {
            "pickup": (0.10, 520, 760),
            "place": (0.16, 420, 260),
            "delivery_ready": (0.20, 660, 880),
            "distractor": (0.12, 180, 120),
            "small_impact": (0.09, 120, 70),
            "large_impact": (0.16, 95, 45),
            "crack": (0.13, 900, 240),
            "egg_break": (0.35, 180, 55),
            "button_click": (0.05, 700, 700),
            "level_complete": (0.28, 520, 780),
            "game_over": (0.40, 220, 55),
            "success": (0.55, 520, 980),
            "footsteps": (0.05, 90, 70),
            "egg_wobble": (0.08, 330, 400),
        }
        duration, start_hz, end_hz = profiles.get(name, (0.08, 300, 300))
        sample_count = max(1, int(frequency * duration))
        frames = bytearray()
        for index in range(sample_count):
            progress = index / sample_count
            hz = start_hz + (end_hz - start_hz) * progress
            envelope = min(1.0, index / max(1, sample_count * 0.08))
            envelope *= max(0.0, 1.0 - progress)
            value = int(math.sin(2 * math.pi * hz * index / frequency) * 11000 * envelope)
            packed = struct.pack("<h", value)
            frames.extend(packed * channels)
        try:
            return pygame.mixer.Sound(buffer=bytes(frames))
        except Exception:
            return None

    def play(self, name, volume=1.0):
        if not self.enabled:
            return
        sound = self.sounds.get(name)
        if sound is not None:
            try:
                sound.set_volume(volume)
                sound.play()
            except Exception:
                pass

    def play_music(self, key, loops=-1, volume=0.35):
        if not self.enabled or self._current_music == key:
            return
        filename = MUSIC_FILES.get(key)
        if not filename:
            return
        path = os.path.join(settings.MUSIC_DIR, filename)
        if not os.path.isfile(path):
            self._current_music = key  # avoid retrying every frame
            return
        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(volume)
            pygame.mixer.music.play(loops)
            self._current_music = key
        except Exception:
            pass

    def stop_music(self):
        if not self.enabled:
            return
        try:
            pygame.mixer.music.stop()
        except Exception:
            pass
        self._current_music = None
