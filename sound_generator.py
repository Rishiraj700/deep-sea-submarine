"""
Sound Generator for Deep Sea Submarine Arcade Game
Generates synthesized WAV sound effects using Python standard library (wave, struct, math).
Zero external dependencies required for audio asset generation.
"""

import math
import os
import struct
import wave

SAMPLE_RATE = 44100


def create_wave_file(filename, samples, sample_rate=SAMPLE_RATE):
    """Write raw float samples (-1.0 to 1.0) into a 16-bit PCM WAV file."""
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with wave.open(filename, "wb") as wf:
        wf.setnchannels(1)  # Mono
        wf.setsampwidth(2)  # 16-bit
        wf.setframerate(sample_rate)
        packed_data = bytearray()
        for s in samples:
            # Clamp sample to [-1.0, 1.0]
            clamped = max(-1.0, min(1.0, s))
            int_sample = int(clamped * 32767)
            packed_data.extend(struct.pack("<h", int_sample))
        wf.writeframes(packed_data)


def generate_sonar_ping(filename):
    """Classic underwater submarine sonar ping: high tone with long reverberant decay."""
    duration = 1.2
    freq = 950.0  # Hz
    total_samples = int(SAMPLE_RATE * duration)
    samples = []
    for i in range(total_samples):
        t = i / SAMPLE_RATE
        # Envelope: sharp attack, exponential ring-out decay
        envelope = math.exp(-3.5 * t)
        # Slight pitch glide downwards to simulate acoustic underwater travel
        current_freq = freq * (1.0 - 0.08 * t)
        wave_val = math.sin(2 * math.pi * current_freq * t)
        # Add subtle harmonic overtone
        wave_val += 0.3 * math.sin(4 * math.pi * current_freq * t)
        samples.append(envelope * wave_val * 0.7)
    create_wave_file(filename, samples)


def generate_pearl_collect(filename):
    """Chime / bubble collection sound: bright, sparkly two-tone bell."""
    duration = 0.35
    total_samples = int(SAMPLE_RATE * duration)
    samples = []
    for i in range(total_samples):
        t = i / SAMPLE_RATE
        envelope = math.exp(-9.0 * t)
        # Rising glissando
        freq = 600.0 + 800.0 * (t / duration)
        wave_val = math.sin(2 * math.pi * freq * t) + 0.4 * math.sin(4 * math.pi * freq * t)
        samples.append(envelope * wave_val * 0.6)
    create_wave_file(filename, samples)


def generate_clam_bonus(filename):
    """Major arpeggio chime for rare golden clam discovery."""
    duration = 0.5
    total_samples = int(SAMPLE_RATE * duration)
    samples = []
    # Arpeggio frequencies: C6, E6, G6, C7
    chord = [1046.5, 1318.5, 1567.9, 2093.0]
    for i in range(total_samples):
        t = i / SAMPLE_RATE
        # Step through chord notes
        idx = min(len(chord) - 1, int((t / duration) * len(chord)))
        freq = chord[idx]
        note_t = t - (idx * (duration / len(chord)))
        envelope = math.exp(-8.0 * note_t) * (1.0 - t / duration)
        wave_val = math.sin(2 * math.pi * freq * t) + 0.3 * math.sin(4 * math.pi * freq * t)
        samples.append(envelope * wave_val * 0.65)
    create_wave_file(filename, samples)


def generate_explosion(filename):
    """Underwater muffled explosion: low rumble with noise dissipation."""
    import random
    duration = 0.75
    total_samples = int(SAMPLE_RATE * duration)
    samples = []
    rng = random.Random(42)
    # Low-pass filter state
    lp_filter = 0.0
    for i in range(total_samples):
        t = i / SAMPLE_RATE
        envelope = math.exp(-4.5 * t)
        # White noise input
        noise = rng.uniform(-1.0, 1.0)
        # Low boom sine sweep
        boom_freq = max(35.0, 140.0 * (1.0 - t / duration))
        boom = math.sin(2 * math.pi * boom_freq * t)
        # Low pass filter noise
        lp_filter += (noise - lp_filter) * 0.12
        val = 0.6 * boom + 0.5 * lp_filter
        samples.append(envelope * val * 0.8)
    create_wave_file(filename, samples)


def generate_shield_activate(filename):
    """Shield aura activation: futuristic rising harmonic pulse."""
    duration = 0.45
    total_samples = int(SAMPLE_RATE * duration)
    samples = []
    for i in range(total_samples):
        t = i / SAMPLE_RATE
        envelope = (1.0 - math.exp(-12.0 * t)) * math.exp(-4.0 * t)
        freq = 300.0 + 500.0 * (t / duration)
        # Tremolo / wobble effect
        tremolo = 1.0 + 0.3 * math.sin(2 * math.pi * 30.0 * t)
        val = math.sin(2 * math.pi * freq * t) * tremolo
        samples.append(envelope * val * 0.6)
    create_wave_file(filename, samples)


def generate_shield_deflect(filename):
    """Shield deflection burst: resonant crystalline pop."""
    duration = 0.4
    total_samples = int(SAMPLE_RATE * duration)
    samples = []
    for i in range(total_samples):
        t = i / SAMPLE_RATE
        envelope = math.exp(-7.0 * t)
        freq = 880.0 * math.exp(-3.0 * t)
        val = math.sin(2 * math.pi * freq * t) + 0.5 * math.sin(2 * math.pi * 1760.0 * t)
        samples.append(envelope * val * 0.7)
    create_wave_file(filename, samples)


def generate_alarm(filename):
    """Critical warning alarm beep: dual-tone submarine klaxon."""
    duration = 0.5
    total_samples = int(SAMPLE_RATE * duration)
    samples = []
    for i in range(total_samples):
        t = i / SAMPLE_RATE
        # Two tone alternating at 4 Hz
        tone = 480.0 if (int(t * 8) % 2 == 0) else 650.0
        envelope = 0.6 if (t % 0.125 < 0.1) else 0.0
        val = math.sin(2 * math.pi * tone * t)
        samples.append(envelope * val * 0.6)
    create_wave_file(filename, samples)


def generate_all_sounds(target_dir="assets/sounds"):
    """Generate all game sound assets into the target directory."""
    os.makedirs(target_dir, exist_ok=True)
    sounds = {
        "sonar_ping.wav": generate_sonar_ping,
        "pearl_collect.wav": generate_pearl_collect,
        "clam_bonus.wav": generate_clam_bonus,
        "explosion.wav": generate_explosion,
        "shield_activate.wav": generate_shield_activate,
        "shield_deflect.wav": generate_shield_deflect,
        "alarm.wav": generate_alarm,
    }
    for fname, func in sounds.items():
        path = os.path.join(target_dir, fname)
        func(path)
        print(f"Generated sound asset: {path}")


if __name__ == "__main__":
    generate_all_sounds()
