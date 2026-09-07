import os
import math
import struct
import pygame

import settings

SOUND_FILES = {
    "pickup": ["pickup.wav"],
    "drop": ["drop.wav"],
    "place": ["place.wav"],
    "delivery_ready": ["delivery_ready.wav"],
    "distractor": ["distractor.wav"],
    "footsteps": ["footsteps.wav"],
    "egg_wobble": ["egg_wobble.wav"],
    "small_impact": ["small_impact.wav", "small_imact.wav"],
    "large_impact": ["large_impact.wav"],
    "crack": ["crack.wav"],
    "egg_break": ["egg_break.wav"],
    "button_click": ["button_click.wav"],
    "level_complete": ["level_complete.wav"],
    "game_over": ["game_over.wav"],
    "success": ["success.wav"],
    "reckless_voice": ["whyrunning.wav", "why_running.wav"],
}

MUSIC_FILES = {
    "menu": "menu_theme.ogg",
    "gameplay": "gameplay_theme.ogg",
    "victory": "victory_theme.ogg",
}

SOUND_MAX_MS = {
    "pickup": 1200,
    "drop": 1200,
    "place": 1200,
    "delivery_ready": 1200,
    "distractor": 900,
    "footsteps": 300,
    "egg_wobble": 500,
    "small_impact": 900,
    "large_impact": 1200,
    "crack": 700,
    "button_click": 400,
}


class AudioManager:
    def __init__(self):
        self.enabled = True
        try:
            pygame.mixer.init()
        except Exception:
            self.enabled = False

        self.sounds = {}
        self._channels = {}
        self._current_music = None

        if self.enabled:
            try:
                pygame.mixer.set_num_channels(max(16, len(SOUND_FILES) + 4))
            except Exception:
                pass

            for index, name in enumerate(SOUND_FILES):
                try:
                    self._channels[name] = pygame.mixer.Channel(index)
                except Exception:
                    self._channels[name] = None

            for name, filenames in SOUND_FILES.items():
                self.sounds[name] = self._load_sound(filenames) or self._make_fallback_sound(name)

    def _load_sound(self, filenames):
        """Try each candidate filename in order; first one that loads wins."""
        for filename in filenames:
            path = os.path.join(settings.SOUNDS_DIR, filename)
            if not os.path.isfile(path):
                continue
            try:
                return pygame.mixer.Sound(path)
            except Exception:
                continue
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
            "reckless_voice": (0.22, 260, 200),
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
        if sound is None:
            return
        try:
            sound.set_volume(volume)
        except Exception:
            return

        maxtime = SOUND_MAX_MS.get(name, 0)
        channel = self._channels.get(name)
        try:
            if channel is not None:
                channel.play(sound, maxtime=maxtime)
            else:
                sound.play(maxtime=maxtime)
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
            self._current_music = key
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
