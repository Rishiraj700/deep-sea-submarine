"""
Submarine player character for Deep Sea Submarine Arcade Game.
Handles buoyancy physics, propulsion, animation, porthole lighting,
oxygen bubble shield, headlight beam, and sonar ping.
"""

import math
import pygame
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    SUB_ACCEL, SUB_MAX_SPEED, SUB_BOOST_SPEED,
    SUB_DRAG, SUB_BUOYANCY,
    MAX_HULL, MAX_OXYGEN,
    OXYGEN_DEPLETION_RATE, OXYGEN_BOOST_COST,
    SONAR_COOLDOWN,
    COLOR_CYAN, COLOR_YELLOW, COLOR_WHITE, COLOR_RED
)


class Submarine:
    """Player-controlled research submersible (Nautilus-II)."""

    def __init__(self, x=140, y=300, normal_sprite=None, shield_sprite=None):
        self.x = float(x)
        self.y = float(y)
        self.vx = 0.0
        self.vy = 0.0

        self.normal_sprite = normal_sprite
        self.shield_sprite = shield_sprite

        # Hitbox dimensions (elliptical/circle approximation)
        self.radius = 24.0

        # Submarine State & Vitals
        self.hull = MAX_HULL
        self.oxygen = MAX_OXYGEN
        self.has_shield = False
        self.alive = True

        # Abilities & Timers
        self.sonar_timer = SONAR_COOLDOWN  # Ready at start
        self.is_boosting = False
        self.invulnerable_timer = 0.0

        # Animation states
        self.pitch_angle = 0.0  # Degrees (-15 to 15)
        self.propeller_angle = 0.0
        self.propeller_bubble_timer = 0.0
        self.ambient_timer = 0.0

    def reset(self, x=140, y=300):
        self.x = float(x)
        self.y = float(y)
        self.vx = 0.0
        self.vy = 0.0
        self.hull = MAX_HULL
        self.oxygen = MAX_OXYGEN
        self.has_shield = False
        self.alive = True
        self.sonar_timer = SONAR_COOLDOWN
        self.is_boosting = False
        self.invulnerable_timer = 0.0
        self.pitch_angle = 0.0

    def get_hitbox_circle(self):
        """Returns (x, y, radius) of submarine center."""
        return (self.x, self.y, self.radius)

    def trigger_sonar(self, particle_mgr, sound_mgr):
        """Trigger echolocation sonar ping if off cooldown."""
        if self.sonar_timer >= SONAR_COOLDOWN and self.alive:
            self.sonar_timer = 0.0
            particle_mgr.emit_sonar_wave(self.x, self.y)
            sound_mgr.play("sonar_ping")
            return True
        return False

    def equip_shield(self, sound_mgr=None):
        """Equip the oxygen bubble shield."""
        self.has_shield = True
        if sound_mgr:
            sound_mgr.play("shield_activate")

    def take_damage(self, amount, particle_mgr=None, sound_mgr=None):
        """Handle incoming hazard damage. If shield is active, deflect it!"""
        if not self.alive or self.invulnerable_timer > 0.0:
            return False

        if self.has_shield:
            # Shield deflects the hazard!
            self.has_shield = False
            self.invulnerable_timer = 0.8
            if particle_mgr:
                particle_mgr.emit_shield_deflect(self.x, self.y)
            if sound_mgr:
                sound_mgr.play("shield_deflect")
            return "shield_absorbed"
        else:
            # Hull takes damage
            self.hull = max(0, self.hull - amount)
            self.invulnerable_timer = 1.4
            if particle_mgr:
                particle_mgr.emit_explosion(self.x, self.y, count=24)
            if sound_mgr:
                sound_mgr.play("explosion")
            if self.hull <= 0:
                self.alive = False
            return "damaged"

    def replenish_oxygen(self, amount):
        self.oxygen = min(MAX_OXYGEN, self.oxygen + amount)

    def update(self, dt, keys, particle_mgr=None, sound_mgr=None):
        if not self.alive:
            return

        self.ambient_timer += dt
        self.sonar_timer += dt
        if self.invulnerable_timer > 0.0:
            self.invulnerable_timer = max(0.0, self.invulnerable_timer - dt)

        # Deplete oxygen
        oxygen_drain = OXYGEN_DEPLETION_RATE * dt
        if self.is_boosting:
            oxygen_drain += OXYGEN_BOOST_COST * dt
        self.oxygen = max(0.0, self.oxygen - oxygen_drain)
        if self.oxygen <= 0:
            self.alive = False
            if sound_mgr:
                sound_mgr.play("alarm")

        # Propulsion Input
        ax = 0.0
        ay = 0.0

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            ax -= SUB_ACCEL
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            ax += SUB_ACCEL
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            ay -= SUB_ACCEL
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            ay += SUB_ACCEL

        # Nitro Boost (Shift or B)
        self.is_boosting = (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT] or keys[pygame.K_b]) and self.oxygen > 5.0
        speed_limit = SUB_BOOST_SPEED if self.is_boosting else SUB_MAX_SPEED
        accel_multiplier = 1.5 if self.is_boosting else 1.0

        # Apply acceleration & Buoyancy
        self.vx += ax * accel_multiplier
        self.vy += (ay * accel_multiplier) + SUB_BUOYANCY

        # Apply hydrodynamic drag
        self.vx *= SUB_DRAG
        self.vy *= SUB_DRAG

        # Clamp speed
        curr_speed = math.hypot(self.vx, self.vy)
        if curr_speed > speed_limit:
            scale = speed_limit / curr_speed
            self.vx *= scale
            self.vy *= scale

        # Move
        self.x += self.vx * (60.0 * dt)
        self.y += self.vy * (60.0 * dt)

        # Screen boundaries
        min_x = 50
        max_x = SCREEN_WIDTH - 60
        min_y = 50
        max_y = SCREEN_HEIGHT - 55

        self.x = max(min_x, min(max_x, self.x))
        self.y = max(min_y, min(max_y, self.y))

        # Pitch tilt angle based on vertical velocity
        target_pitch = -self.vy * 3.8
        target_pitch = max(-16.0, min(16.0, target_pitch))
        self.pitch_angle += (target_pitch - self.pitch_angle) * 0.15

        # Propeller animation & bubble emission
        speed = math.hypot(self.vx, self.vy)
        propeller_rate = 8.0 + speed * 18.0
        self.propeller_angle += propeller_rate * dt

        if particle_mgr:
            self.propeller_bubble_timer += dt
            bubble_threshold = 0.04 if self.is_boosting else 0.12
            if self.propeller_bubble_timer >= bubble_threshold:
                self.propeller_bubble_timer = 0.0
                # Tail offset calculation
                tail_rad = math.radians(self.pitch_angle)
                tail_x = self.x - math.cos(tail_rad) * 42
                tail_y = self.y + math.sin(tail_rad) * 42
                particle_mgr.emit_propeller_bubbles(tail_x, tail_y, is_boost=self.is_boosting)

    def draw_headlight(self, surface):
        """Draw volumetric translucent headlight beam piercing dark water."""
        rad = math.radians(self.pitch_angle)
        bow_x = self.x + math.cos(rad) * 40
        bow_y = self.y - math.sin(rad) * 40

        beam_length = 260.0
        beam_spread = 70.0

        # End points of light cone
        end_center_x = bow_x + math.cos(rad) * beam_length
        end_center_y = bow_y - math.sin(rad) * beam_length

        perp_x = -math.sin(rad)
        perp_y = -math.cos(rad)

        p1 = (bow_x, bow_y)
        p2 = (end_center_x + perp_x * beam_spread, end_center_y + perp_y * beam_spread)
        p3 = (end_center_x - perp_x * beam_spread, end_center_y - perp_y * beam_spread)

        # Draw semi-transparent light cone polygon
        light_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        # Subtle light flicker
        alpha = int(45 + 6 * math.sin(self.ambient_timer * 8.0))
        pygame.draw.polygon(light_surf, (255, 255, 200, alpha), [p1, p2, p3])
        # Inner brighter beam core
        inner_spread = beam_spread * 0.4
        ip2 = (end_center_x + perp_x * inner_spread, end_center_y + perp_y * inner_spread)
        ip3 = (end_center_x - perp_x * inner_spread, end_center_y - perp_y * inner_spread)
        pygame.draw.polygon(light_surf, (255, 255, 230, alpha + 20), [p1, ip2, ip3])

        surface.blit(light_surf, (0, 0))

    def draw(self, surface):
        if not self.alive:
            return

        # Draw Headlight Beam first (so sub renders on top)
        self.draw_headlight(surface)

        # Flickering during invulnerability
        if self.invulnerable_timer > 0.0:
            if int(self.invulnerable_timer * 16) % 2 == 0:
                return

        # Select sprite (shielded vs normal)
        base_sprite = self.shield_sprite if self.has_shield else self.normal_sprite

        if base_sprite:
            # Rotate sprite according to pitch angle
            rotated_sprite = pygame.transform.rotozoom(base_sprite, self.pitch_angle, 1.0)
            rect = rotated_sprite.get_rect(center=(int(self.x), int(self.y)))
            surface.blit(rotated_sprite, rect)
        else:
            # Fallback procedural shape
            pygame.draw.ellipse(surface, (28, 78, 128), (int(self.x) - 40, int(self.y) - 20, 80, 40))

        # Dynamic shield pulsing aura effect if active
        if self.has_shield:
            pulse = 1.0 + 0.06 * math.sin(self.ambient_timer * 7.0)
            sw = int(96 * pulse)
            sh = int(58 * pulse)
            shield_overlay = pygame.Surface((sw + 8, sh + 8), pygame.SRCALPHA)
            alpha = int(80 + 30 * math.sin(self.ambient_timer * 7.0))
            pygame.draw.ellipse(shield_overlay, (80, 220, 255, alpha), (4, 4, sw, sh), width=2)
            pygame.draw.ellipse(shield_overlay, (120, 240, 255, int(alpha * 0.4)), (4, 4, sw, sh))
            rect = shield_overlay.get_rect(center=(int(self.x), int(self.y)))
            surface.blit(shield_overlay, rect)
