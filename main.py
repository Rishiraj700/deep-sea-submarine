"""
Abyssal Expedition: Deep Sea Submarine
Multimedia Systems Lab — Lab Test 2
2D Arcade Game with Custom Multimedia, Buoyancy Physics, and State Management.
"""

import json
import math
import os
import random
import sys
import pygame

from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, TITLE,
    COLOR_WHITE, COLOR_RED,
    SCORE_PEARL, SCORE_CLAM, SCORE_SHIELD_PICKUP,
    SCORE_DEPTH_RATE, COMBO_TIMEOUT, MAX_COMBO,
    DAMAGE_MINE, DAMAGE_TORPEDO
)
from environment import OceanEnvironment
from particles import ParticleManager
from entities import EntityManager, Pearl, GoldenClam, ShieldPickup, DepthCharge, Torpedo
from submarine import Submarine
from sound_manager import SoundManager
from ui import UIManager

# Game States
STATE_START = "start"
STATE_PLAYING = "playing"
STATE_PAUSED = "paused"
STATE_GAME_OVER = "game_over"


class Game:
    """Master Game Controller coordinating game loop, states, entities, and rendering."""

    def __init__(self, headless=False):
        if headless:
            os.environ["SDL_VIDEODRIVER"] = "dummy"

        pygame.init()
        pygame.display.set_caption(TITLE)

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = STATE_START

        # Initialize Subsystems
        self.sound_mgr = SoundManager()
        self.particle_mgr = ParticleManager()
        self.environment = OceanEnvironment()
        self.ui_mgr = UIManager()

        # Load Sprite Assets
        self.sprites = self._load_sprites()

        # Game Entities
        self.player = Submarine(
            x=140, y=300,
            normal_sprite=self.sprites.get("submarine.png"),
            shield_sprite=self.sprites.get("submarine_shield.png")
        )
        self.entity_mgr = EntityManager(self.sprites)

        # Game Session Variables
        self.score = 0
        self.high_score = self._load_high_score()
        self.depth = 50.0  # Starts at 50 meters
        self.combo = 1
        self.combo_timer = 0.0
        self.max_combo_streak = 1
        self.pearls_collected = 0
        self.clams_collected = 0
        self.game_over_reason = ""
        self.is_new_high_score = False

        # Visual Screen-shake & Flash feedback
        self.screen_shake_time = 0.0
        self.screen_flash_alpha = 0.0

    def _load_sprites(self):
        """Load sprite PNG images with graceful fallback."""
        images_dir = "assets/images"
        sprite_names = [
            "submarine.png", "submarine_shield.png", "pearl.png",
            "clam.png", "depth_charge.png", "torpedo.png", "shield_powerup.png"
        ]
        loaded = {}
        for name in sprite_names:
            path = os.path.join(images_dir, name)
            if os.path.exists(path):
                try:
                    loaded[name] = pygame.image.load(path).convert_alpha()
                except Exception as e:
                    print(f"Warning: Failed to load sprite {path}: {e}")
            else:
                print(f"Sprite not found at {path}, using fallback.")
        return loaded

    def _load_high_score(self):
        """Read saved high score from highscore.json."""
        filepath = "highscore.json"
        if os.path.exists(filepath):
            try:
                with open(filepath, "r") as f:
                    data = json.load(f)
                    return int(data.get("high_score", 0))
            except Exception:
                return 0
        return 0

    def _save_high_score(self):
        """Save updated high score to highscore.json."""
        filepath = "highscore.json"
        try:
            with open(filepath, "w") as f:
                json.dump({"high_score": self.high_score}, f, indent=2)
        except Exception as e:
            print(f"Failed to save high score: {e}")

    def reset_game(self):
        """Reset session to fresh dive without relaunching the application."""
        self.player.reset(x=140, y=300)
        self.entity_mgr.reset()
        self.score = 0
        self.depth = 50.0
        self.combo = 1
        self.combo_timer = 0.0
        self.max_combo_streak = 1
        self.pearls_collected = 0
        self.clams_collected = 0
        self.game_over_reason = ""
        self.is_new_high_score = False
        self.screen_shake_time = 0.0
        self.screen_flash_alpha = 0.0
        self.state = STATE_PLAYING

    def check_circle_collision(self, c1, c2):
        """
        Mathematical Circle-Circle Collision Detection:
        Two circles collide if the Euclidean distance between their centers
        is less than or equal to the sum of their radii:
            (x2 - x1)^2 + (y2 - y1)^2 <= (r1 + r2)^2
        Using distance-squared avoids computationally expensive square root calculation.
        """
        x1, y1, r1 = c1
        x2, y2, r2 = c2
        dx = x2 - x1
        dy = y2 - y1
        dist_sq = dx * dx + dy * dy
        radii_sum = r1 + r2
        return dist_sq <= (radii_sum * radii_sum)

    def handle_collisions(self):
        """Process player interactions with collectibles and hazards."""
        if not self.player.alive:
            return

        player_circle = self.player.get_hitbox_circle()

        # 1. Collectibles Interaction
        for item in self.entity_mgr.collectibles:
            if not item.alive:
                continue
            item_circle = item.get_hitbox_circle()
            if self.check_circle_collision(player_circle, item_circle):
                item.alive = False

                if isinstance(item, Pearl):
                    self.pearls_collected += 1
                    earned = SCORE_PEARL * self.combo
                    self.score += earned
                    self.sound_mgr.play("pearl_collect")
                    self.particle_mgr.emit_sparkles(item.x, item.y, color=(100, 240, 255), count=14)

                    # Advance combo
                    self.combo = min(MAX_COMBO, self.combo + 1)
                    self.max_combo_streak = max(self.max_combo_streak, self.combo)
                    self.combo_timer = COMBO_TIMEOUT

                elif isinstance(item, GoldenClam):
                    self.clams_collected += 1
                    earned = SCORE_CLAM * self.combo
                    self.score += earned
                    self.player.replenish_oxygen(25.0)
                    self.sound_mgr.play("clam_bonus")
                    self.particle_mgr.emit_sparkles(item.x, item.y, color=(255, 215, 0), count=24)

                elif isinstance(item, ShieldPickup):
                    self.player.equip_shield(self.sound_mgr)
                    self.score += SCORE_SHIELD_PICKUP
                    self.particle_mgr.emit_shield_deflect(self.player.x, self.player.y)

        # 2. Hazards Collision
        for hazard in self.entity_mgr.hazards:
            if not hazard.alive:
                continue
            hazard_circle = hazard.get_hitbox_circle()
            if self.check_circle_collision(player_circle, hazard_circle):
                hazard.alive = False
                damage = DAMAGE_TORPEDO if isinstance(hazard, Torpedo) else DAMAGE_MINE

                result = self.player.take_damage(damage, self.particle_mgr, self.sound_mgr)
                if result == "damaged":
                    # Screen shake & red flash
                    self.screen_shake_time = 0.35
                    self.screen_flash_alpha = 140.0
                    # Break combo streak
                    self.combo = 1
                    self.combo_timer = 0.0

                    if not self.player.alive:
                        self.trigger_game_over(reason="hull")

                elif result == "shield_absorbed":
                    # Shield successfully deflected hazard
                    self.screen_shake_time = 0.15

        # 3. Sonar Wave collision with pearls (echolocation magnet)
        for wave in self.particle_mgr.sonar_waves:
            self.entity_mgr.trigger_sonar_scan(wave)

    def trigger_game_over(self, reason):
        """Transition to GAME_OVER state and record telemetry."""
        self.state = STATE_GAME_OVER
        self.game_over_reason = reason
        if self.score > self.high_score:
            self.high_score = self.score
            self.is_new_high_score = True
            self._save_high_score()

    def update(self, dt):
        """Update game state, physics, and entities for current frame."""
        self.ui_mgr.update(dt)
        self.environment.update(dt)

        if self.state == STATE_PLAYING:
            keys = pygame.key.get_pressed()

            # Update Submarine Player
            self.player.update(dt, keys, self.particle_mgr, self.sound_mgr)

            # Check if oxygen ran out
            if not self.player.alive and self.player.oxygen <= 0:
                self.trigger_game_over(reason="oxygen")
                return

            # Advance Depth & Passive Depth Scoring
            # Submarine descends faster when steering downwards
            vertical_rate = max(0.5, 3.5 + self.player.vy * 0.8)
            self.depth += vertical_rate * dt
            self.score += int(SCORE_DEPTH_RATE * vertical_rate * dt * 5.0)

            # Update Combo Timer
            if self.combo > 1:
                self.combo_timer -= dt
                if self.combo_timer <= 0:
                    self.combo = 1
                    self.combo_timer = 0.0

            # Update Entities & Particle Systems
            self.entity_mgr.update(dt, self.depth, self.player, self.particle_mgr)
            self.particle_mgr.update(dt)

            # Collision Resolution
            self.handle_collisions()

            # Update Screen Flash & Shake Timers
            if self.screen_shake_time > 0:
                self.screen_shake_time = max(0.0, self.screen_shake_time - dt)
            if self.screen_flash_alpha > 0:
                self.screen_flash_alpha = max(0.0, self.screen_flash_alpha - 450.0 * dt)

        elif self.state in [STATE_START, STATE_GAME_OVER]:
            # Keep ambient bubbles and plankton moving in menus
            self.particle_mgr.update(dt)

    def draw(self):
        """Render active frame onto screen."""
        # Calculate camera shake offset
        shake_ox, shake_oy = 0, 0
        if self.screen_shake_time > 0:
            shake_ox = random.randint(-6, 6)
            shake_oy = random.randint(-6, 6)

        # Render Surface (with shake support)
        render_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

        # 1. Background Environment (Ocean Gradient, Caustics, Kelp)
        self.environment.draw(render_surf, self.depth)

        # 2. Game Entities & Particles
        self.entity_mgr.draw(render_surf)
        self.player.draw(render_surf)
        self.particle_mgr.draw(render_surf)

        # 3. Red Screen Flash (on damage hit)
        if self.screen_flash_alpha > 0:
            flash_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            flash_surf.fill((255, 30, 30, int(self.screen_flash_alpha)))
            render_surf.blit(flash_surf, (0, 0))

        # Blit main game scene to screen with shake
        self.screen.fill((0, 0, 0))
        self.screen.blit(render_surf, (shake_ox, shake_oy))

        # 4. State-specific UI Overlays (drawn without camera shake for crispness)
        if self.state == STATE_PLAYING:
            self.ui_mgr.draw_hud(
                self.screen, self.player, self.score, self.high_score,
                self.depth, self.combo, self.combo_timer, COMBO_TIMEOUT
            )
        elif self.state == STATE_START:
            self.ui_mgr.draw_start_screen(self.screen, self.high_score)
        elif self.state == STATE_PAUSED:
            self.ui_mgr.draw_hud(
                self.screen, self.player, self.score, self.high_score,
                self.depth, self.combo, self.combo_timer, COMBO_TIMEOUT
            )
            self.ui_mgr.draw_pause_screen(self.screen)
        elif self.state == STATE_GAME_OVER:
            self.ui_mgr.draw_game_over_screen(
                self.screen, self.game_over_reason, self.score, self.high_score,
                self.depth, self.pearls_collected, self.clams_collected,
                self.max_combo_streak, self.is_new_high_score
            )

        pygame.display.flip()

    def handle_input(self):
        """Process keyboard, mouse, and window events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:
                # Global Hotkeys
                if event.key == pygame.K_m:
                    self.sound_mgr.toggle_mute()

                elif event.key == pygame.K_F12:
                    # Save screenshot
                    fname = f"screenshot_{self.state}_{int(pygame.time.get_ticks())}.png"
                    pygame.image.save(self.screen, fname)
                    print(f"Saved screenshot: {fname}")

                # State-specific Key Handling
                if self.state == STATE_START:
                    if event.key in [pygame.K_SPACE, pygame.K_RETURN]:
                        self.reset_game()

                elif self.state == STATE_PLAYING:
                    if event.key in [pygame.K_p, pygame.K_ESCAPE]:
                        self.state = STATE_PAUSED
                    elif event.key == pygame.K_SPACE:
                        self.player.trigger_sonar(self.particle_mgr, self.sound_mgr)
                    elif event.key == pygame.K_r:
                        self.reset_game()

                elif self.state == STATE_PAUSED:
                    if event.key in [pygame.K_p, pygame.K_ESCAPE]:
                        self.state = STATE_PLAYING
                    elif event.key == pygame.K_r:
                        self.reset_game()

                elif self.state == STATE_GAME_OVER:
                    if event.key in [pygame.K_r, pygame.K_SPACE]:
                        self.reset_game()
                    elif event.key == pygame.K_ESCAPE:
                        self.running = False

    def run(self):
        """Main game loop executing at 60 FPS."""
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            # Clamp dt to prevent physics tunneling during window drag
            dt = min(0.05, dt)

            self.handle_input()
            self.update(dt)
            self.draw()

        pygame.quit()


def main():
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
