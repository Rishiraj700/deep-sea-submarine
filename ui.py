"""
User Interface and HUD rendering for Deep Sea Submarine Arcade Game.
Handles Title Screen, HUD bars, Combo indicator, Depth gauges,
Pause Overlay, and Mission Debriefing / Game Over screen.
"""

import math
import pygame
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    COLOR_WHITE, COLOR_CYAN, COLOR_GOLD, COLOR_RED, COLOR_GREEN,
    COLOR_YELLOW, COLOR_GRAY, COLOR_DARK_GRAY,
    MAX_HULL, MAX_OXYGEN, SONAR_COOLDOWN,
    ZONE_SUNLIGHT_MAX, ZONE_TWILIGHT_MAX
)


class UIManager:
    """Renders all game interface overlays and HUD components."""

    def __init__(self):
        pygame.font.init()
        # Use clean system fonts with fallback
        self.font_title = pygame.font.SysFont("Trebuchet MS, Arial, Helvetica", 48, bold=True)
        self.font_subtitle = pygame.font.SysFont("Trebuchet MS, Arial, Helvetica", 24, bold=True)
        self.font_heading = pygame.font.SysFont("Trebuchet MS, Arial, Helvetica", 20, bold=True)
        self.font_body = pygame.font.SysFont("Segoe UI, Arial, sans-serif", 15)
        self.font_body_bold = pygame.font.SysFont("Segoe UI, Arial, sans-serif", 15, bold=True)
        self.font_hud = pygame.font.SysFont("Consolas, Courier New, monospace", 14, bold=True)
        self.font_hud_large = pygame.font.SysFont("Consolas, Courier New, monospace", 18, bold=True)

        self.blink_timer = 0.0

    def update(self, dt):
        self.blink_timer += dt

    def draw_hud(self, surface, player, score, high_score, depth, combo, combo_timer, max_combo_time):
        """Draw active gameplay HUD (Hull, Oxygen, Score, Depth, Abilities)."""
        hud_bar_y = 14

        # 1. Hull Integrity Bar (Top Left)
        hull_ratio = max(0.0, player.hull / MAX_HULL)
        bar_w, bar_h = 160, 16
        bx, by = 18, hud_bar_y

        # Border & background
        pygame.draw.rect(surface, (20, 25, 35), (bx - 2, by - 2, bar_w + 4, bar_h + 4), border_radius=4)
        pygame.draw.rect(surface, (10, 14, 20), (bx, by, bar_w, bar_h), border_radius=3)

        # Hull bar color: Green -> Yellow -> Red
        if hull_ratio > 0.5:
            hull_col = COLOR_GREEN
        elif hull_ratio > 0.25:
            hull_col = COLOR_YELLOW
        else:
            # Flashing red when critical
            pulse = 0.5 + 0.5 * math.sin(self.blink_timer * 12.0)
            hull_col = (255, int(40 * pulse), int(40 * pulse))

        fill_w = int(bar_w * hull_ratio)
        if fill_w > 0:
            pygame.draw.rect(surface, hull_col, (bx, by, fill_w, bar_h), border_radius=3)
        pygame.draw.rect(surface, (80, 110, 140), (bx - 2, by - 2, bar_w + 4, bar_h + 4), width=1, border_radius=4)

        lbl_hull = self.font_hud.render(f"HULL: {int(player.hull)}%", True, COLOR_WHITE)
        surface.blit(lbl_hull, (bx, by + bar_h + 3))

        # 2. Oxygen Bar (Below Hull)
        oxy_ratio = max(0.0, player.oxygen / MAX_OXYGEN)
        oy = by + bar_h + 24
        pygame.draw.rect(surface, (20, 25, 35), (bx - 2, oy - 2, bar_w + 4, bar_h + 4), border_radius=4)
        pygame.draw.rect(surface, (10, 14, 20), (bx, oy, bar_w, bar_h), border_radius=3)

        oxy_col = COLOR_CYAN if oxy_ratio > 0.35 else (
            COLOR_ORANGE if oxy_ratio > 0.18 else COLOR_RED
        )
        fill_oxy = int(bar_w * oxy_ratio)
        if fill_oxy > 0:
            pygame.draw.rect(surface, oxy_col, (bx, oy, fill_oxy, bar_h), border_radius=3)
        pygame.draw.rect(surface, (80, 110, 140), (bx - 2, oy - 2, bar_w + 4, bar_h + 4), width=1, border_radius=4)

        lbl_oxy = self.font_hud.render(f"OXYGEN: {int(player.oxygen)}%", True, COLOR_WHITE)
        surface.blit(lbl_oxy, (bx, oy + bar_h + 3))

        # 3. Center Depth & Zone Display
        if depth < ZONE_SUNLIGHT_MAX:
            zone_name = "SUNLIGHT SHALLOWS"
            zone_color = (120, 230, 255)
        elif depth < ZONE_TWILIGHT_MAX:
            zone_name = "TWILIGHT TRENCH"
            zone_color = (180, 160, 255)
        else:
            zone_name = "MIDNIGHT ABYSS"
            zone_color = (255, 90, 90)

        depth_str = f"DEPTH: {int(depth)} m"
        txt_depth = self.font_hud_large.render(depth_str, True, COLOR_WHITE)
        txt_zone = self.font_hud.render(f"[{zone_name}]", True, zone_color)
        cx = SCREEN_WIDTH // 2
        surface.blit(txt_depth, txt_depth.get_rect(center=(cx, 22)))
        surface.blit(txt_zone, txt_zone.get_rect(center=(cx, 44)))

        # 4. Score & Combo Display (Top Right)
        score_str = f"SCORE: {score:05d}"
        txt_score = self.font_hud_large.render(score_str, True, COLOR_GOLD)
        rx = SCREEN_WIDTH - 20
        rect_score = txt_score.get_rect(topright=(rx, hud_bar_y))
        surface.blit(txt_score, rect_score)

        hi_score_str = f"HI-SCORE: {high_score:05d}"
        txt_hi = self.font_hud.render(hi_score_str, True, COLOR_GRAY)
        surface.blit(txt_hi, txt_hi.get_rect(topright=(rx, hud_bar_y + 24)))

        # Combo Streak Meter
        if combo > 1:
            combo_str = f"COMBO: x{combo}!"
            txt_combo = self.font_hud_large.render(combo_str, True, COLOR_YELLOW)
            surface.blit(txt_combo, txt_combo.get_rect(topright=(rx, hud_bar_y + 46)))

            # Combo timer bar
            cw = 100
            ch = 6
            cx_bar = SCREEN_WIDTH - cw - 20
            cy_bar = hud_bar_y + 70
            time_ratio = max(0.0, min(1.0, combo_timer / max_combo_time))
            pygame.draw.rect(surface, (20, 25, 35), (cx_bar, cy_bar, cw, ch), border_radius=2)
            pygame.draw.rect(surface, COLOR_YELLOW, (cx_bar, cy_bar, int(cw * time_ratio), ch), border_radius=2)

        # 5. Abilities & Power-up Status (Bottom Bar)
        bot_y = SCREEN_HEIGHT - 32

        # Sonar Ping Status
        sonar_ready = (player.sonar_timer >= SONAR_COOLDOWN)
        if sonar_ready:
            txt_sonar = self.font_hud.render("SPACE: SONAR [READY]", True, COLOR_CYAN)
        else:
            pct = int((player.sonar_timer / SONAR_COOLDOWN) * 100)
            txt_sonar = self.font_hud.render(f"SPACE: SONAR [{pct}%]", True, COLOR_GRAY)
        surface.blit(txt_sonar, (20, bot_y))

        # Oxygen Bubble Shield Indicator
        if player.has_shield:
            txt_shield = self.font_hud.render("SHIELD: ACTIVE [PROTECTED]", True, (100, 240, 255))
        else:
            txt_shield = self.font_hud.render("SHIELD: OFFLINE", True, (90, 105, 120))
        surface.blit(txt_shield, (240, bot_y))

        # Nitro Boost Indicator
        boost_color = COLOR_YELLOW if player.is_boosting else COLOR_GRAY
        txt_boost = self.font_hud.render("SHIFT/B: NITRO BOOST", True, boost_color)
        surface.blit(txt_boost, (490, bot_y))

        # Controls Hint
        txt_hint = self.font_hud.render("P: PAUSE | M: MUTE", True, COLOR_GRAY)
        surface.blit(txt_hint, txt_hint.get_rect(bottomright=(SCREEN_WIDTH - 20, SCREEN_HEIGHT - 16)))

    def draw_start_screen(self, surface, high_score):
        """Draw Title Screen with mission briefing and customization details."""
        # Semi-transparent background overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((3, 12, 28, 205))
        surface.blit(overlay, (0, 0))

        cx = SCREEN_WIDTH // 2

        # Main Title
        txt_main = self.font_title.render("ABYSSAL EXPEDITION", True, COLOR_CYAN)
        txt_sub = self.font_subtitle.render("2D DEEP SEA SUBMARINE SIMULATION", True, COLOR_WHITE)
        surface.blit(txt_main, txt_main.get_rect(center=(cx, 75)))
        surface.blit(txt_sub, txt_sub.get_rect(center=(cx, 125)))

        # Customization Badge Card
        card_rect = pygame.Rect(cx - 380, 160, 760, 310)
        pygame.draw.rect(surface, (10, 25, 45, 230), card_rect, border_radius=10)
        pygame.draw.rect(surface, (40, 120, 180), card_rect, width=2, border_radius=10)

        # Customization Header
        badge_title = self.font_heading.render("★ INDIVIDUAL LAB CUSTOMIZATION SPECIFICATION ★", True, COLOR_GOLD)
        surface.blit(badge_title, badge_title.get_rect(center=(cx, 185)))

        details = [
            ("Visual Theme:", "Ocean Depths / Abyssal Trench with dynamic depth zones & sun caustics"),
            ("Player Vessel:", "Deep Sea Research Submersible with animated propeller & headlight beam"),
            ("Collectibles:", "Luminescent Pearls (+100 pts) & Rare Golden Clams (+350 pts & Oxygen restore)"),
            ("Hazards:", "Naval Depth Charges (drifting sea mines) & High-Speed Torpedoes"),
            ("Special Power-up:", "Oxygen Bubble Shield (absorbs 1 impact) & Sonar Radar Ping (SPACE)"),
            ("Physics Rule:", "Realistic water buoyancy lift & hydrodynamic drag deceleration"),
            ("Difficulty Rule:", "Increasing water depth scales torpedo speed, hazard frequency & light fade"),
        ]

        curr_y = 215
        for label, val in details:
            t_lbl = self.font_body_bold.render(label, True, COLOR_CYAN)
            t_val = self.font_body.render(val, True, COLOR_WHITE)
            surface.blit(t_lbl, (cx - 360, curr_y))
            surface.blit(t_val, (cx - 210, curr_y))
            curr_y += 24

        # Controls Bar
        ctrl_title = self.font_heading.render("CONTROLS:", True, COLOR_YELLOW)
        ctrl_desc = self.font_body.render(
            "WASD / Arrows: Navigate | SPACE: Sonar Ping | SHIFT/B: Nitro Boost | P: Pause | R: Restart",
            True, COLOR_WHITE
        )
        surface.blit(ctrl_title, (cx - 360, curr_y + 10))
        surface.blit(ctrl_desc, (cx - 240, curr_y + 12))

        # Flashing Start Prompt
        blink = (int(self.blink_timer * 3) % 2 == 0)
        start_col = COLOR_YELLOW if blink else (255, 255, 180)
        txt_start = self.font_subtitle.render("▶  PRESS SPACE OR ENTER TO DIVE  ◀", True, start_col)
        surface.blit(txt_start, txt_start.get_rect(center=(cx, 510)))

        txt_hi = self.font_hud.render(f"CURRENT ALL-TIME RECORD: {high_score:05d} PTS", True, COLOR_GRAY)
        surface.blit(txt_hi, txt_hi.get_rect(center=(cx, 555)))

    def draw_pause_screen(self, surface):
        """Draw pause overlay."""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((2, 8, 18, 180))
        surface.blit(overlay, (0, 0))

        cx, cy = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        txt_p = self.font_title.render("EXPEDITION PAUSED", True, COLOR_WHITE)
        txt_resume = self.font_subtitle.render("Press P or ESC to Resume Navigation", True, COLOR_CYAN)
        txt_restart = self.font_body.render("Press R to Restart Expedition", True, COLOR_GRAY)

        surface.blit(txt_p, txt_p.get_rect(center=(cx, cy - 50)))
        surface.blit(txt_resume, txt_resume.get_rect(center=(cx, cy + 15)))
        surface.blit(txt_restart, txt_restart.get_rect(center=(cx, cy + 55)))

    def draw_game_over_screen(self, surface, reason, score, high_score, depth, pearls, clams, max_combo, is_new_record):
        """Draw mission debriefing / Game Over screen."""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((4, 8, 20, 225))
        surface.blit(overlay, (0, 0))

        cx = SCREEN_WIDTH // 2

        # Title
        txt_over = self.font_title.render("MISSION TERMINATED", True, COLOR_RED)
        surface.blit(txt_over, txt_over.get_rect(center=(cx, 75)))

        # Failure Reason
        if reason == "hull":
            reason_str = "CAUSE: CATASTROPHIC HULL BREACH (PRESSURE IMPLOSION)"
        elif reason == "oxygen":
            reason_str = "CAUSE: LIFE SUPPORT DEPLETION (OXYGEN STARVATION)"
        else:
            reason_str = "CAUSE: VESSEL LOST AT SEA"

        txt_reason = self.font_heading.render(reason_str, True, (255, 140, 140))
        surface.blit(txt_reason, txt_reason.get_rect(center=(cx, 120)))

        # Score Debriefing Card
        card_rect = pygame.Rect(cx - 300, 155, 600, 260)
        pygame.draw.rect(surface, (12, 22, 38), card_rect, border_radius=10)
        pygame.draw.rect(surface, (50, 90, 140), card_rect, width=2, border_radius=10)

        txt_header = self.font_heading.render("MISSION TELEMETRY LOG", True, COLOR_CYAN)
        surface.blit(txt_header, txt_header.get_rect(center=(cx, 185)))

        stats = [
            ("Final Score:", f"{score:05d} PTS"),
            ("Maximum Depth Reached:", f"{int(depth)} meters"),
            ("Luminescent Pearls Collected:", f"{pearls}"),
            ("Golden Clams Discovered:", f"{clams}"),
            ("Highest Combo Streak:", f"x{max_combo}"),
            ("All-Time High Score:", f"{high_score:05d} PTS"),
        ]

        curr_y = 220
        for lbl, val in stats:
            t_lbl = self.font_body.render(lbl, True, COLOR_WHITE)
            t_val = self.font_body_bold.render(val, True, COLOR_GOLD)
            surface.blit(t_lbl, (cx - 260, curr_y))
            surface.blit(t_val, (cx + 80, curr_y))
            curr_y += 26

        if is_new_record:
            txt_rec = self.font_heading.render("★ NEW ALL-TIME RECORD ACHIEVED! ★", True, COLOR_YELLOW)
            surface.blit(txt_rec, txt_rec.get_rect(center=(cx, 440)))

        # Restart instructions
        blink = (int(self.blink_timer * 3) % 2 == 0)
        rst_col = COLOR_YELLOW if blink else COLOR_WHITE
        txt_rst = self.font_subtitle.render("PRESS R TO DIVE AGAIN  |  ESC TO QUIT", True, rst_col)
        surface.blit(txt_rst, txt_rst.get_rect(center=(cx, 490)))

        txt_cred = self.font_hud.render("Multimedia Systems Lab Test 2 - 2D Arcade Game", True, COLOR_GRAY)
        surface.blit(txt_cred, txt_cred.get_rect(center=(cx, 550)))
