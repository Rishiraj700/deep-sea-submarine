"""
Environment and background renderer for Deep Sea Submarine Arcade Game.
Renders dynamic ocean gradients, shifting light caustics, parallax rocky seabed,
swaying kelp/coral, and bioluminescent abyssal plankton.
"""

import math
import random
import pygame
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    COLOR_OCEAN_SURFACE, COLOR_OCEAN_MID, COLOR_OCEAN_ABYSS, COLOR_SEABED,
    ZONE_SUNLIGHT_MAX, ZONE_TWILIGHT_MAX
)


class KelpFrond:
    """Individual kelp stalk that sways rhythmically with ocean currents."""

    def __init__(self, base_x, base_y, height=120, segments=6):
        self.base_x = float(base_x)
        self.base_y = float(base_y)
        self.height = height
        self.segments = segments
        self.phase = random.uniform(0, 2 * math.pi)
        self.speed = random.uniform(1.2, 2.2)
        self.color = (random.randint(15, 25), random.randint(65, 95), random.randint(45, 65))

    def draw(self, surface, time):
        pts = [(self.base_x, self.base_y)]
        seg_len = self.height / self.segments
        for i in range(1, self.segments + 1):
            factor = i / self.segments
            sway = math.sin(time * self.speed + self.phase + factor * 1.5) * (18.0 * factor)
            px = self.base_x + sway
            py = self.base_y - (seg_len * i)
            pts.append((px, py))

        if len(pts) >= 2:
            pygame.draw.lines(surface, self.color, False, pts, width=5)
            # Draw leaf nodes
            for p in pts[2:]:
                pygame.draw.circle(surface, self.color, (int(p[0]), int(p[1])), 4)


class Plankton:
    """Tiny bioluminescent organism drifting in the abyssal darkness."""

    def __init__(self):
        self.x = random.uniform(0, SCREEN_WIDTH)
        self.y = random.uniform(80, SCREEN_HEIGHT - 60)
        self.vx = random.uniform(-0.4, 0.4)
        self.vy = random.uniform(-0.2, 0.2)
        self.phase = random.uniform(0, 2 * math.pi)
        self.blink_speed = random.uniform(1.5, 3.5)

    def update(self, dt):
        self.phase += self.blink_speed * dt
        self.x += self.vx * (60.0 * dt)
        self.y += self.vy * (60.0 * dt)
        if self.x < 0:
            self.x = SCREEN_WIDTH
        elif self.x > SCREEN_WIDTH:
            self.x = 0
        if self.y < 50:
            self.y = SCREEN_HEIGHT - 60
        elif self.y > SCREEN_HEIGHT - 60:
            self.y = 50

    def draw(self, surface, is_abyss=False):
        alpha = int(120 + 100 * math.sin(self.phase))
        if alpha <= 0:
            return
        surf = pygame.Surface((6, 6), pygame.SRCALPHA)
        color = (100, 255, 200, alpha) if is_abyss else (160, 230, 255, int(alpha * 0.6))
        pygame.draw.circle(surf, color, (3, 3), 2)
        surface.blit(surf, (int(self.x) - 3, int(self.y) - 3))


class OceanEnvironment:
    """Renders the dynamic underwater environment and lighting."""

    def __init__(self):
        self.timer = 0.0
        self.kelp_forest = []
        # Generate kelp stalks along seabed
        for kx in range(40, SCREEN_WIDTH + 80, 55):
            kh = random.randint(90, 160)
            self.kelp_forest.append(KelpFrond(kx, SCREEN_HEIGHT, height=kh))

        self.plankton_swarm = [Plankton() for _ in range(35)]

    def get_zone_colors(self, depth):
        """Interpolate ocean gradient colors according to current depth."""
        if depth < ZONE_SUNLIGHT_MAX:
            # Sunlight -> Twilight
            t = depth / ZONE_SUNLIGHT_MAX
            top_c = self._lerp_color(COLOR_OCEAN_SURFACE, COLOR_OCEAN_MID, t)
            bot_c = self._lerp_color(COLOR_OCEAN_MID, COLOR_OCEAN_ABYSS, t)
            caustic_intensity = 1.0 - t * 0.7
        else:
            # Twilight -> Midnight Abyss
            t = min(1.0, (depth - ZONE_SUNLIGHT_MAX) / (ZONE_TWILIGHT_MAX - ZONE_SUNLIGHT_MAX))
            top_c = self._lerp_color(COLOR_OCEAN_MID, COLOR_OCEAN_ABYSS, t)
            bot_c = self._lerp_color(COLOR_OCEAN_ABYSS, (1, 4, 12), t)
            caustic_intensity = max(0.0, 0.3 * (1.0 - t))
        return top_c, bot_c, caustic_intensity

    def _lerp_color(self, c1, c2, t):
        t = max(0.0, min(1.0, t))
        return (
            int(c1[0] + (c2[0] - c1[0]) * t),
            int(c1[1] + (c2[1] - c1[1]) * t),
            int(c1[2] + (c2[2] - c1[2]) * t),
        )

    def update(self, dt):
        self.timer += dt
        for p in self.plankton_swarm:
            p.update(dt)

    def draw(self, surface, depth):
        top_color, bot_color, caustic_intensity = self.get_zone_colors(depth)

        # Draw vertical gradient background
        # Render in slices for smooth performance
        num_slices = 32
        slice_h = SCREEN_HEIGHT / num_slices
        for i in range(num_slices):
            t = i / num_slices
            c = self._lerp_color(top_color, bot_color, t)
            pygame.draw.rect(surface, c, (0, int(i * slice_h), SCREEN_WIDTH, int(slice_h) + 1))

        # Draw Sun Ray Caustics (in shallow / twilight zones)
        if caustic_intensity > 0.05:
            caustic_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            num_rays = 6
            for r in range(num_rays):
                ray_phase = self.timer * 0.8 + r * 1.1
                rx_top = 100 + r * 150 + math.sin(ray_phase) * 45
                rx_bot = rx_top + 160 + math.cos(ray_phase * 0.7) * 35
                ray_alpha = int(35 * caustic_intensity * (0.6 + 0.4 * math.sin(ray_phase * 1.5)))
                if ray_alpha > 0:
                    pts = [
                        (rx_top - 20, 0),
                        (rx_top + 25, 0),
                        (rx_bot + 75, SCREEN_HEIGHT),
                        (rx_bot - 45, SCREEN_HEIGHT),
                    ]
                    pygame.draw.polygon(caustic_surf, (180, 240, 255, ray_alpha), pts)
            surface.blit(caustic_surf, (0, 0))

        # Draw Plankton
        is_abyss = (depth > ZONE_TWILIGHT_MAX)
        for p in self.plankton_swarm:
            p.draw(surface, is_abyss=is_abyss)

        # Draw Swaying Kelp on Seabed
        for k in self.kelp_forest:
            k.draw(surface, self.timer)

        # Seabed silhouette
        pygame.draw.ellipse(surface, COLOR_SEABED, (-100, SCREEN_HEIGHT - 35, SCREEN_WIDTH + 200, 70))
        pygame.draw.ellipse(surface, (10, 14, 22), (50, SCREEN_HEIGHT - 25, SCREEN_WIDTH - 100, 50))
