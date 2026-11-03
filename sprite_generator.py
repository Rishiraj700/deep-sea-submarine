"""
Sprite Generator for Deep Sea Submarine Arcade Game
Generates crisp, high-quality PNG sprite assets using Pygame's drawing functions
with per-pixel alpha transparency.
"""

import math
import os
import pygame


def init_pygame():
    os.environ["SDL_VIDEODRIVER"] = "dummy"  # Headless rendering for asset generation
    pygame.init()


def create_submarine_surface(has_shield=False):
    """Render the deep sea research submarine (Nautilus-II) with periscope and porthole."""
    width, height = 90, 50
    surf = pygame.Surface((width, height), pygame.SRCALPHA)

    center_x = 45
    center_y = 26

    # Headlight mount at bow (front is on the right)
    bow_x = 76
    pygame.draw.polygon(
        surf, (180, 195, 210), [(bow_x - 4, center_y - 6), (bow_x + 6, center_y - 2), (bow_x + 6, center_y + 2), (bow_x - 4, center_y + 6)]
    )
    # Headlight lens (glowing bright yellow/white)
    pygame.draw.ellipse(surf, (255, 255, 220), (bow_x + 4, center_y - 4, 5, 8))

    # Main Hull: Sleek hydrodynamic rounded body
    # Base navy/cyan body
    hull_rect = pygame.Rect(18, 12, 60, 28)
    pygame.draw.ellipse(surf, (28, 78, 128), hull_rect)

    # Upper hull highlight (light reflection)
    highlight_rect = pygame.Rect(22, 14, 50, 14)
    pygame.draw.ellipse(surf, (45, 120, 190), highlight_rect)

    # Lower hull shadow
    shadow_rect = pygame.Rect(22, 28, 52, 10)
    pygame.draw.ellipse(surf, (15, 45, 75), shadow_rect)

    # Conning Tower (top bridge)
    tower_rect = pygame.Rect(38, 5, 18, 14)
    pygame.draw.rect(surf, (35, 95, 150), tower_rect, border_radius=4)
    pygame.draw.rect(surf, (20, 55, 90), tower_rect, width=2, border_radius=4)

    # Periscope
    pygame.draw.line(surf, (180, 195, 210), (45, 6), (45, 1), 3)
    pygame.draw.line(surf, (180, 195, 210), (45, 1), (50, 1), 3)
    pygame.draw.circle(surf, (100, 230, 255), (51, 1), 2)  # Periscope optical lens

    # Glowing Portholes (circular observation windows)
    porthole_centers = [(36, center_y), (48, center_y), (60, center_y)]
    for px, py in porthole_centers:
        # Brass rim
        pygame.draw.circle(surf, (212, 175, 55), (px, py), 6)
        # Inner dark frame
        pygame.draw.circle(surf, (10, 25, 45), (px, py), 5)
        # Glowing cyan glass
        pygame.draw.circle(surf, (90, 240, 255), (px, py), 4)
        # Glint reflection
        pygame.draw.circle(surf, (240, 255, 255), (px - 1, py - 1), 1)

    # Brass Stern Propeller Mount
    pygame.draw.rect(surf, (180, 140, 40), (14, center_y - 4, 6, 8))
    # Propeller Blades
    pygame.draw.ellipse(surf, (230, 190, 60), (10, center_y - 12, 5, 12))
    pygame.draw.ellipse(surf, (230, 190, 60), (10, center_y, 5, 12))
    pygame.draw.circle(surf, (255, 220, 100), (14, center_y), 3)

    # Horizontal Stabilizer Fin at stern
    pygame.draw.polygon(surf, (25, 70, 115), [(18, center_y - 2), (6, center_y - 7), (12, center_y + 1)])

    # Hull Rivet Details
    rivet_color = (180, 210, 235)
    for rx in range(26, 72, 8):
        surf.set_at((rx, 14), rivet_color)
        surf.set_at((rx, 37), rivet_color)

    # Optional Shield Bubble overlay
    if has_shield:
        shield_surf = pygame.Surface((width, height), pygame.SRCALPHA)
        # Outer shimmering glow ring
        pygame.draw.ellipse(shield_surf, (80, 220, 255, 100), (4, 2, width - 8, height - 4), width=3)
        # Inner translucent fill
        pygame.draw.ellipse(shield_surf, (60, 190, 255, 40), (4, 2, width - 8, height - 4))
        # Shield specular glint arcs
        pygame.draw.arc(shield_surf, (255, 255, 255, 200), (8, 4, width - 16, height - 8), 0.8, 1.8, 2)
        surf.blit(shield_surf, (0, 0))

    return surf


def create_pearl_surface():
    """Render glowing luminescent ocean pearl orb."""
    size = 32
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    cx, cy = size // 2, size // 2

    # Outer soft glow halo
    for r in range(15, 8, -1):
        alpha = int(40 * (1.0 - (r - 8) / 7))
        pygame.draw.circle(surf, (100, 230, 255, alpha), (cx, cy), r)

    # Iridescent Pearl base (pearly white with lavender/cyan luster)
    pygame.draw.circle(surf, (225, 245, 255), (cx, cy), 8)
    pygame.draw.circle(surf, (200, 230, 250), (cx + 1, cy + 1), 7)
    # Pearlescent core
    pygame.draw.circle(surf, (255, 255, 255), (cx - 2, cy - 2), 4)
    # Bright specular glint
    pygame.draw.circle(surf, (255, 255, 255), (cx - 3, cy - 3), 2)
    return surf


def create_clam_surface():
    """Render golden clam shell with luminous pearl inside."""
    size = 40
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    cx, cy = size // 2, size // 2

    # Golden Shell glow
    for r in range(18, 12, -1):
        alpha = int(50 * (1.0 - (r - 12) / 6))
        pygame.draw.circle(surf, (255, 215, 0, alpha), (cx, cy), r)

    # Golden Shell Bottom
    shell_rect = pygame.Rect(cx - 14, cy - 8, 28, 20)
    pygame.draw.arc(surf, (255, 190, 0), shell_rect, 0, math.pi, 14)
    pygame.draw.ellipse(surf, (218, 165, 32), (cx - 13, cy - 2, 26, 12))

    # Shell Fluted Ridges
    for offset in [-9, -4, 0, 4, 9]:
        pygame.draw.line(surf, (255, 235, 120), (cx + offset, cy + 8), (cx + offset * 0.4, cy - 4), 2)

    # Glistening Golden Pearl inside
    pygame.draw.circle(surf, (255, 255, 240), (cx, cy - 1), 6)
    pygame.draw.circle(surf, (255, 215, 0), (cx, cy - 1), 5)
    pygame.draw.circle(surf, (255, 255, 255), (cx - 2, cy - 3), 2)
    return surf


def create_depth_charge_surface():
    """Render naval depth charge sea mine with spikes and pulsing proximity sensor."""
    size = 44
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    cx, cy = size // 2, size // 2

    # Spikes (contact horns) at 8 angles
    num_spikes = 8
    for i in range(num_spikes):
        angle = (2 * math.pi / num_spikes) * i
        sx = cx + int(math.cos(angle) * 19)
        sy = cy + int(math.sin(angle) * 19)
        # Spike stem
        pygame.draw.line(surf, (60, 65, 75), (cx, cy), (sx, sy), 4)
        # Detonator tip
        pygame.draw.circle(surf, (160, 165, 175), (sx, sy), 3)

    # Main Iron Spherical Body
    pygame.draw.circle(surf, (30, 35, 42), (cx, cy), 13)
    # Metallic shading
    pygame.draw.circle(surf, (55, 62, 72), (cx - 2, cy - 2), 11)
    pygame.draw.circle(surf, (80, 90, 105), (cx - 4, cy - 4), 5)

    # Rivets around sphere perimeter
    for a in [0.5, 1.5, 2.5, 3.5, 4.5, 5.5]:
        rx = cx + int(math.cos(a) * 8)
        ry = cy + int(math.sin(a) * 8)
        surf.set_at((rx, ry), (170, 180, 195))

    # Center red pulsing proximity beacon LED
    pygame.draw.circle(surf, (150, 0, 0), (cx, cy), 5)
    pygame.draw.circle(surf, (255, 40, 40), (cx, cy), 4)
    pygame.draw.circle(surf, (255, 200, 200), (cx - 1, cy - 1), 1)
    return surf


def create_torpedo_surface():
    """Render fast hydrodynamic abyssal torpedo."""
    width, height = 54, 22
    surf = pygame.Surface((width, height), pygame.SRCALPHA)
    cy = height // 2

    # Propeller at tail (left)
    pygame.draw.line(surf, (200, 180, 60), (4, cy - 7), (4, cy + 7), 2)
    pygame.draw.rect(surf, (100, 100, 110), (5, cy - 2, 4, 4))

    # Stabilizer Fins
    pygame.draw.polygon(surf, (70, 75, 85), [(9, cy - 8), (17, cy - 2), (9, cy - 2)])
    pygame.draw.polygon(surf, (70, 75, 85), [(9, cy + 8), (17, cy + 2), (9, cy + 2)])

    # Torpedo Cylindrical Hull
    body_rect = pygame.Rect(9, cy - 6, 32, 12)
    pygame.draw.rect(surf, (45, 50, 60), body_rect, border_radius=2)
    # Upper highlight
    pygame.draw.line(surf, (90, 95, 110), (10, cy - 4), (40, cy - 4), 2)

    # Hazard Stripes (Yellow / Black warning)
    for x in [22, 28, 34]:
        pygame.draw.polygon(surf, (240, 200, 20), [(x, cy - 6), (x + 3, cy - 6), (x, cy + 5), (x - 3, cy + 5)])

    # Warhead Dome (front on right)
    warhead_rect = pygame.Rect(36, cy - 6, 14, 12)
    pygame.draw.ellipse(surf, (200, 40, 40), warhead_rect)  # Red danger warhead
    pygame.draw.circle(surf, (255, 120, 120), (47, cy), 3)  # Fuse tip
    return surf


def create_shield_powerup_surface():
    """Render collectible oxygen bubble shield power-up item."""
    size = 36
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    cx, cy = size // 2, size // 2

    # Multi-layered glowing bubble
    for r in range(16, 10, -1):
        alpha = int(60 * (1.0 - (r - 10) / 6))
        pygame.draw.circle(surf, (60, 220, 255, alpha), (cx, cy), r)

    pygame.draw.circle(surf, (120, 240, 255, 140), (cx, cy), 11, width=2)
    pygame.draw.circle(surf, (40, 180, 255, 70), (cx, cy), 9)

    # Shield Crest / Emblem inside
    pygame.draw.polygon(
        surf, (255, 255, 255), [(cx, cy - 6), (cx + 5, cy - 4), (cx + 4, cy + 2), (cx, cy + 6), (cx - 4, cy + 2), (cx - 5, cy - 4)]
    )
    pygame.draw.polygon(
        surf, (20, 120, 220), [(cx, cy - 4), (cx + 3, cy - 3), (cx + 2, cy + 1), (cx, cy + 4), (cx - 2, cy + 1), (cx - 3, cy - 3)]
    )
    # Specular shine
    pygame.draw.arc(surf, (255, 255, 255, 220), (cx - 8, cy - 8, 16, 16), 0.7, 1.8, 2)
    return surf


def generate_all_sprites(target_dir="assets/images"):
    """Generate and save all game PNG sprite assets."""
    init_pygame()
    os.makedirs(target_dir, exist_ok=True)

    assets = {
        "submarine.png": create_submarine_surface(has_shield=False),
        "submarine_shield.png": create_submarine_surface(has_shield=True),
        "pearl.png": create_pearl_surface(),
        "clam.png": create_clam_surface(),
        "depth_charge.png": create_depth_charge_surface(),
        "torpedo.png": create_torpedo_surface(),
        "shield_powerup.png": create_shield_powerup_surface(),
    }

    for fname, surf in assets.items():
        path = os.path.join(target_dir, fname)
        pygame.image.save(surf, path)
        print(f"Generated sprite asset: {path} ({surf.get_width()}x{surf.get_height()})")


if __name__ == "__main__":
    generate_all_sprites()
