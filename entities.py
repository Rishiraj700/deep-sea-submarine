"""
Game entities for Deep Sea Submarine Arcade Game.
Includes Collectibles (Pearls, Golden Clams, Shield Pickups)
and Hazards (Naval Depth Charges, High-Speed Torpedoes).
"""

import math
import random
import pygame
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    COLOR_CYAN, COLOR_GOLD, COLOR_RED, COLOR_YELLOW,
    ZONE_SUNLIGHT_MAX, ZONE_TWILIGHT_MAX
)


class Entity:
    """Base class for all interactive game objects."""

    def __init__(self, x, y, radius, sprite=None):
        self.x = float(x)
        self.y = float(y)
        self.radius = radius
        self.sprite = sprite
        self.alive = True

    def get_hitbox_circle(self):
        """Returns (x, y, radius) for circular collision detection."""
        return (self.x, self.y, self.radius)

    def is_offscreen(self):
        return (
            self.x < -100 or self.x > SCREEN_WIDTH + 100 or
            self.y < -100 or self.y > SCREEN_HEIGHT + 100
        )


class Pearl(Entity):
    """Luminescent pearl orb collectible item."""

    def __init__(self, x, y, sprite=None):
        super().__init__(x, y, radius=14, sprite=sprite)
        self.base_y = float(y)
        self.speed_x = random.uniform(1.6, 2.5)
        self.phase = random.uniform(0, 2 * math.pi)
        self.amplitude = random.uniform(15.0, 30.0)
        self.frequency = random.uniform(1.8, 3.0)
        self.is_magnetized = False
        self.glow_timer = 0.0

    def update(self, dt, player=None):
        self.glow_timer += dt
        self.phase += self.frequency * dt

        if self.is_magnetized and player and player.alive:
            # Magnetic pull towards player when scanned by Sonar Ping
            dx = player.x - self.x
            dy = player.y - self.y
            dist = math.hypot(dx, dy)
            if dist > 5:
                pull_speed = 320.0 * dt
                self.x += (dx / dist) * pull_speed
                self.y += (dy / dist) * pull_speed
        else:
            self.x -= self.speed_x * (60.0 * dt)
            self.y = self.base_y + math.sin(self.phase) * self.amplitude

        if self.is_offscreen():
            self.alive = False

    def draw(self, surface):
        if not self.alive:
            return
        if self.sprite:
            # Gentle pulsing scale
            pulse = 1.0 + 0.08 * math.sin(self.glow_timer * 6.0)
            sw = int(self.sprite.get_width() * pulse)
            sh = int(self.sprite.get_height() * pulse)
            scaled = pygame.transform.smoothscale(self.sprite, (sw, sh))
            rect = scaled.get_rect(center=(int(self.x), int(self.y)))
            surface.blit(scaled, rect)
        else:
            # Fallback procedural render
            pygame.draw.circle(surface, COLOR_CYAN, (int(self.x), int(self.y)), int(self.radius))


class GoldenClam(Entity):
    """Rare golden clam that replenishes oxygen and rewards bonus score."""

    def __init__(self, x, y, sprite=None):
        super().__init__(x, y, radius=18, sprite=sprite)
        self.speed_x = random.uniform(1.2, 1.8)
        self.bob_phase = random.uniform(0, 2 * math.pi)
        self.sparkle_timer = 0.0

    def update(self, dt, player=None, particle_mgr=None):
        self.bob_phase += 2.0 * dt
        self.x -= self.speed_x * (60.0 * dt)
        self.y += math.sin(self.bob_phase) * 0.4 * (60.0 * dt)

        # Emit ambient golden sparkle flecks
        self.sparkle_timer += dt
        if self.sparkle_timer >= 0.2 and particle_mgr:
            self.sparkle_timer = 0.0
            particle_mgr.emit_sparkles(self.x, self.y, color=COLOR_GOLD, count=2)

        if self.is_offscreen():
            self.alive = False

    def draw(self, surface):
        if not self.alive:
            return
        if self.sprite:
            rect = self.sprite.get_rect(center=(int(self.x), int(self.y)))
            surface.blit(self.sprite, rect)
        else:
            pygame.draw.circle(surface, COLOR_GOLD, (int(self.x), int(self.y)), int(self.radius))


class ShieldPickup(Entity):
    """Oxygen Bubble Shield power-up capsule."""

    def __init__(self, x, y, sprite=None):
        super().__init__(x, y, radius=18, sprite=sprite)
        self.speed_x = random.uniform(1.4, 2.0)
        self.rot_angle = 0.0
        self.bob_phase = random.uniform(0, 2 * math.pi)

    def update(self, dt, player=None):
        self.bob_phase += 2.5 * dt
        self.rot_angle = (self.rot_angle + 60.0 * dt) % 360
        self.x -= self.speed_x * (60.0 * dt)
        self.y += math.sin(self.bob_phase) * 0.6 * (60.0 * dt)
        if self.is_offscreen():
            self.alive = False

    def draw(self, surface):
        if not self.alive:
            return
        if self.sprite:
            rect = self.sprite.get_rect(center=(int(self.x), int(self.y)))
            surface.blit(self.sprite, rect)
        else:
            pygame.draw.circle(surface, (80, 220, 255), (int(self.x), int(self.y)), int(self.radius))


class DepthCharge(Entity):
    """Naval depth charge sea mine with spikes and pulsing proximity fuse."""

    def __init__(self, x, y, speed_y=None, sprite=None):
        super().__init__(x, y, radius=18, sprite=sprite)
        self.speed_y = speed_y or random.uniform(1.2, 2.2)
        self.base_x = float(x)
        self.swing_amplitude = random.uniform(25.0, 50.0)
        self.swing_speed = random.uniform(1.4, 2.4)
        self.swing_phase = random.uniform(0, 2 * math.pi)
        self.blink_timer = 0.0
        self.is_blinking = False

    def update(self, dt, player=None):
        self.swing_phase += self.swing_speed * dt
        self.y += self.speed_y * (60.0 * dt)
        self.x = self.base_x + math.sin(self.swing_phase) * self.swing_amplitude

        # Proximity sensor: blinks faster if player is near
        dist_to_player = 9999.0
        if player and player.alive:
            dist_to_player = math.hypot(player.x - self.x, player.y - self.y)

        blink_period = 0.15 if dist_to_player < 160 else 0.5
        self.blink_timer += dt
        if self.blink_timer >= blink_period:
            self.blink_timer = 0.0
            self.is_blinking = not self.is_blinking

        if self.y > SCREEN_HEIGHT + 60 or self.x < -80 or self.x > SCREEN_WIDTH + 80:
            self.alive = False

    def draw(self, surface):
        if not self.alive:
            return
        if self.sprite:
            rect = self.sprite.get_rect(center=(int(self.x), int(self.y)))
            surface.blit(self.sprite, rect)
            # Draw glowing red proximity beacon on top of sprite center when blinking
            if self.is_blinking:
                pygame.draw.circle(surface, (255, 30, 30), (int(self.x), int(self.y)), 6)
                pygame.draw.circle(surface, (255, 200, 200), (int(self.x), int(self.y)), 2)
        else:
            pygame.draw.circle(surface, (50, 55, 65), (int(self.x), int(self.y)), int(self.radius))


class Torpedo(Entity):
    """High-speed abyssal torpedo projectile with cavitation wake."""

    def __init__(self, x, y, speed_x=None, sprite=None):
        super().__init__(x, y, radius=12, sprite=sprite)
        self.speed_x = speed_x or random.uniform(5.5, 7.8)
        self.vy = random.uniform(-0.4, 0.4)
        self.bubble_timer = 0.0

    def update(self, dt, particle_mgr=None):
        self.x -= self.speed_x * (60.0 * dt)
        self.y += self.vy * (60.0 * dt)

        # Cavitation bubbles emitted from tail
        self.bubble_timer += dt
        if self.bubble_timer >= 0.04 and particle_mgr:
            self.bubble_timer = 0.0
            tail_x = self.x + 24
            tail_y = self.y
            particle_mgr.emit_propeller_bubbles(tail_x, tail_y, is_boost=False)

        if self.x < -100:
            self.alive = False

    def draw(self, surface):
        if not self.alive:
            return
        if self.sprite:
            rect = self.sprite.get_rect(center=(int(self.x), int(self.y)))
            surface.blit(self.sprite, rect)
        else:
            pygame.draw.rect(surface, COLOR_RED, (int(self.x) - 20, int(self.y) - 6, 40, 12))


class TorpedoWarning:
    """Warning indicator arrow at screen edge alerting incoming torpedo."""

    def __init__(self, target_y, duration=0.85):
        self.y = float(target_y)
        self.duration = duration
        self.elapsed = 0.0
        self.ready_to_spawn = False

    def update(self, dt):
        self.elapsed += dt
        if self.elapsed >= self.duration:
            self.ready_to_spawn = True
        return self.elapsed < self.duration

    def draw(self, surface):
        alpha_blink = int(255 * (0.5 + 0.5 * math.sin(self.elapsed * 24.0)))
        surf = pygame.Surface((34, 28), pygame.SRCALPHA)
        # Danger hazard icon
        pygame.draw.polygon(
            surf, (255, 40, 40, alpha_blink),
            [(4, 4), (30, 14), (4, 24)]
        )
        pygame.draw.polygon(
            surf, (255, 240, 80, alpha_blink),
            [(8, 8), (24, 14), (8, 20)]
        )
        surface.blit(surf, (SCREEN_WIDTH - 38, int(self.y) - 14))


class EntityManager:
    """Manages entity pools, spawning schedules, difficulty scaling, and interactions."""

    def __init__(self, sprites=None):
        self.sprites = sprites or {}
        self.collectibles = []
        self.hazards = []
        self.warnings = []

        # Timers
        self.pearl_spawn_timer = 0.0
        self.mine_spawn_timer = 0.0
        self.torpedo_spawn_timer = 0.0
        self.clam_spawn_timer = 0.0
        self.shield_spawn_timer = 0.0

    def reset(self):
        self.collectibles.clear()
        self.hazards.clear()
        self.warnings.clear()
        self.pearl_spawn_timer = 0.0
        self.mine_spawn_timer = 0.0
        self.torpedo_spawn_timer = 0.0
        self.clam_spawn_timer = 0.0
        self.shield_spawn_timer = 0.0

    def trigger_sonar_scan(self, sonar_wave):
        """Attract pearls and reveal hazards touched by the sonar wave."""
        for c in self.collectibles:
            if isinstance(c, Pearl):
                dist = math.hypot(c.x - sonar_wave.x, c.y - sonar_wave.y)
                if abs(dist - sonar_wave.radius) < 35.0:
                    c.is_magnetized = True

    def update(self, dt, current_depth, player, particle_mgr):
        # Determine difficulty progression rates based on depth
        depth_factor = min(2.5, 1.0 + (current_depth / 500.0))

        # Pearl Spawning (consistent collectibles)
        self.pearl_spawn_timer += dt
        pearl_interval = max(0.9, 1.6 / depth_factor)
        if self.pearl_spawn_timer >= pearl_interval:
            self.pearl_spawn_timer = 0.0
            py = random.uniform(60, SCREEN_HEIGHT - 60)
            self.collectibles.append(Pearl(SCREEN_WIDTH + 40, py, self.sprites.get("pearl.png")))

        # Golden Clam Spawning (rare bonus, every ~18-24s)
        self.clam_spawn_timer += dt
        if self.clam_spawn_timer >= 18.0:
            if random.random() < 0.65:
                self.clam_spawn_timer = 0.0
                cy = random.uniform(SCREEN_HEIGHT * 0.45, SCREEN_HEIGHT - 50)
                self.collectibles.append(GoldenClam(SCREEN_WIDTH + 40, cy, self.sprites.get("clam.png")))

        # Shield Pickup Spawning (protective power-up, every ~28-35s)
        self.shield_spawn_timer += dt
        if self.shield_spawn_timer >= 28.0:
            if random.random() < 0.55:
                self.shield_spawn_timer = 0.0
                sy = random.uniform(80, SCREEN_HEIGHT - 100)
                self.collectibles.append(ShieldPickup(SCREEN_WIDTH + 40, sy, self.sprites.get("shield_powerup.png")))

        # Depth Charge Spawning (scale with depth)
        self.mine_spawn_timer += dt
        mine_interval = max(1.4, 3.8 / depth_factor)
        if self.mine_spawn_timer >= mine_interval:
            self.mine_spawn_timer = 0.0
            mx = random.uniform(120, SCREEN_WIDTH - 80)
            speed_y = random.uniform(1.2, 2.2) * (1.0 + 0.3 * (current_depth / 1000.0))
            self.hazards.append(DepthCharge(mx, -50, speed_y, self.sprites.get("depth_charge.png")))

        # Torpedo Spawning (begins after 150m, scales rapidly in Twilight & Midnight Abyss)
        if current_depth > 150:
            self.torpedo_spawn_timer += dt
            torpedo_interval = max(2.8, 7.5 / depth_factor)
            if self.torpedo_spawn_timer >= torpedo_interval:
                self.torpedo_spawn_timer = 0.0
                ty = random.uniform(80, SCREEN_HEIGHT - 80)
                # Add warning arrow first
                self.warnings.append(TorpedoWarning(ty, duration=0.85))

        # Process Torpedo Warnings
        remaining_warnings = []
        for w in self.warnings:
            if w.update(dt):
                remaining_warnings.append(w)
            elif w.ready_to_spawn:
                # Spawn torpedo now
                torp_speed = random.uniform(5.8, 8.5) * (1.0 + 0.25 * (current_depth / 1000.0))
                self.hazards.append(Torpedo(SCREEN_WIDTH + 40, w.y, torp_speed, self.sprites.get("torpedo.png")))
        self.warnings = remaining_warnings

        # Update Collectibles
        for c in self.collectibles:
            if isinstance(c, GoldenClam):
                c.update(dt, player, particle_mgr)
            else:
                c.update(dt, player)
        self.collectibles = [c for c in self.collectibles if c.alive]

        # Update Hazards
        for h in self.hazards:
            if isinstance(h, Torpedo):
                h.update(dt, particle_mgr)
            else:
                h.update(dt, player)
        self.hazards = [h for h in self.hazards if h.alive]

    def draw(self, surface):
        for w in self.warnings:
            w.draw(surface)
        for c in self.collectibles:
            c.draw(surface)
        for h in self.hazards:
            h.draw(surface)
