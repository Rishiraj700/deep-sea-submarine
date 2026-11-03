"""
Automated Screenshot Generator for Lab Report Submission.
Runs the game simulation headlessly to produce crisp, high-resolution PNG screenshots of:
1. Title Screen (screenshot_title.png)
2. Active Gameplay with HUD, Submarine, Headlight, Pearls, Depth Charges (screenshot_gameplay.png)
3. Game Over / Mission Telemetry Debriefing (screenshot_gameover.png)
"""

import os
import pygame

# Set headless display driver before initializing pygame
os.environ["SDL_VIDEODRIVER"] = "dummy"

from main import Game, STATE_START, STATE_PLAYING, STATE_GAME_OVER
from entities import Pearl, GoldenClam, DepthCharge, Torpedo


def capture_all_screenshots():
    print("Initializing headless game instance for screenshots...")
    game = Game(headless=True)

    # 1. Capture Title Screen
    game.state = STATE_START
    game.ui_mgr.update(0.5)
    game.particle_mgr.update(0.5)
    game.draw()
    title_path = "screenshot_title.png"
    pygame.image.save(game.screen, title_path)
    print(f"Captured: {title_path}")

    # 2. Capture Active Gameplay Screen
    game.state = STATE_PLAYING
    game.reset_game()
    game.score = 2450
    game.depth = 340.0
    game.combo = 3
    game.combo_timer = 2.4
    game.player.oxygen = 84.0
    game.player.hull = 90.0
    game.player.equip_shield()
    game.player.x = 220
    game.player.y = 280

    # Populate visually rich entities
    game.entity_mgr.collectibles.append(Pearl(420, 240, game.sprites.get("pearl.png")))
    game.entity_mgr.collectibles.append(Pearl(540, 310, game.sprites.get("pearl.png")))
    game.entity_mgr.collectibles.append(GoldenClam(680, 480, game.sprites.get("clam.png")))
    game.entity_mgr.hazards.append(DepthCharge(500, 160, 1.5, game.sprites.get("depth_charge.png")))
    game.entity_mgr.hazards.append(Torpedo(750, 270, 6.0, game.sprites.get("torpedo.png")))

    # Fire a sonar wave for visual spectacle
    game.particle_mgr.emit_sonar_wave(game.player.x, game.player.y)
    game.particle_mgr.emit_propeller_bubbles(game.player.x - 42, game.player.y, is_boost=True)

    # Step physics for a few frames
    for _ in range(15):
        dt = 0.016
        game.environment.update(dt)
        game.particle_mgr.update(dt)

    game.draw()
    gameplay_path = "screenshot_gameplay.png"
    pygame.image.save(game.screen, gameplay_path)
    print(f"Captured: {gameplay_path}")

    # 3. Capture Game Over Screen
    game.state = STATE_GAME_OVER
    game.game_over_reason = "hull"
    game.pearls_collected = 18
    game.clams_collected = 3
    game.max_combo_streak = 4
    game.is_new_high_score = True
    game.high_score = 3100
    game.score = 3100
    game.depth = 582.0

    game.draw()
    gameover_path = "screenshot_gameover.png"
    pygame.image.save(game.screen, gameover_path)
    print(f"Captured: {gameover_path}")

    pygame.quit()
    print("All screenshots successfully captured!")


if __name__ == "__main__":
    capture_all_screenshots()
