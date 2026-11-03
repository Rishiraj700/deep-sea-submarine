"""
Sound Manager for Deep Sea Submarine Arcade Game.
Handles sound effects playback, volume control, mute toggling,
and graceful fallback if audio device is unavailable.
"""

import os
import pygame


class SoundManager:
    """Manages audio loading and playback with silent fallback."""

    def __init__(self, sounds_dir="assets/sounds"):
        self.sounds_dir = sounds_dir
        self.sounds = {}
        self.muted = False
        self.audio_available = False

        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            self.audio_available = True
            self.load_all_sounds()
        except Exception as e:
            print(f"[SoundManager] Warning: Audio system could not be initialized ({e}). Running in silent mode.")
            self.audio_available = False

    def load_all_sounds(self):
        sound_files = {
            "sonar_ping": "sonar_ping.wav",
            "pearl_collect": "pearl_collect.wav",
            "clam_bonus": "clam_bonus.wav",
            "explosion": "explosion.wav",
            "shield_activate": "shield_activate.wav",
            "shield_deflect": "shield_deflect.wav",
            "alarm": "alarm.wav",
        }
        for name, fname in sound_files.items():
            path = os.path.join(self.sounds_dir, fname)
            if os.path.exists(path):
                try:
                    self.sounds[name] = pygame.mixer.Sound(path)
                except Exception as e:
                    print(f"[SoundManager] Could not load sound {path}: {e}")
            else:
                print(f"[SoundManager] Missing audio file: {path}")

    def play(self, sound_name):
        """Play a sound effect if not muted and available."""
        if self.muted or not self.audio_available:
            return
        sound = self.sounds.get(sound_name)
        if sound:
            try:
                sound.play()
            except Exception:
                pass

    def toggle_mute(self):
        """Toggle mute state."""
        self.muted = not self.muted
        return self.muted
