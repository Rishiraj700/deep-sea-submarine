"""
Particle systems and visual effects for Deep Sea Submarine.
Includes bubbles, sparkles, explosion fragments, shockwaves, and sonar waves.
"""

import math
import random
import pygame
from config import SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_CYAN, COLOR_GOLD, COLOR_WHITE


class Bubble:
    """Rising underwater bubble with lateral sinusoidal oscillation."""

    def __init__(self, x, y, radius=None, speed=None, is_propeller=False, is_boost=False):
        self.x = float(x)
        self.y = float(y)
        self.is_propeller = is_propeller
        self.is_boost = is_boost

        if is_boost:
            self.radius = random.uniform(3.5, 7.0)
            self.vy = random.uniform(-1.5, -3.5)
            self.vx = random.uniform(-5.0, -2.5)  # Ejected backward
            self.max_life = random.uniform(0.6, 1.2)
        elif is_propeller:
            self.radius = random.uniform(2.0, 4.5)
            self.vy = random.uniform(-0.8, -2.2)
            self.vx = random.uniform(-2.5, -1.0)
            self.max_life = random.uniform(0.8, 1.8)
        else:
            # Ambient sea bubble
            self.radius = radius or random.uniform(1.5, 5.0)
            self.vy = speed or random.uniform(-0.6, -1.8)
            self.vx = random.uniform(-0.3, 0.3)
            self.max_life = random.uniform(3.0, 7.0)

        self.life = self.max_life
        self.phase = random.uniform(0, 2 * math.pi)
        self.wobble_speed = random.uniform(2.0, 4.5)

    def update(self, dt):
        self.life -= dt
        self.y += self.vy * (60.0 * dt)
        self.phase += self.wobble_speed * dt
        self.x += (self.vx + math.sin(self.phase) * 0.4) * (60.0 * dt)
        return self.life > 0 and self.y > -20

    def draw(self, surface):
        if self.life <= 0:
            return
        alpha = int(220 * min(1.0, self.life / (self.max_life * 0.3)))
        r = max(1, int(self.radius))
        bubble_surf = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
        # Translucent outer rim
        pygame.draw.circle(bubble_surf, (180, 235, 255, alpha), (r + 2, r + 2), r, width=1)
        # Subtle interior shading
        if r >= 3:
            pygame.draw.circle(bubble_surf, (220, 245, 255, int(alpha * 0.3)), (r + 2, r + 2), r - 1)
            # Specular shine
            pygame.draw.circle(bubble_surf, (255, 255, 255, alpha), (r + 1, r + 1), max(1, r // 3))
        surface.blit(bubble_surf, (int(self.x) - r - 2, int(self.y) - r - 2))


class Sparkle:
    """Twinkling star/glint particle emitted when collecting items."""

    def __init__(self, x, y, color=COLOR_GOLD):
        self.x = float(x)
        self.y = float(y)
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(1.5, 4.5)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.color = color
        self.max_life = random.uniform(0.4, 0.8)
        self.life = self.max_life
        self.size = random.uniform(2.5, 5.0)

    def update(self, dt):
        self.life -= dt
        self.x += self.vx * (60.0 * dt)
        self.y += self.vy * (60.0 * dt)
        self.vx *= 0.94
        self.vy *= 0.94
        return self.life > 0

    def draw(self, surface):
        alpha = int(255 * (self.life / self.max_life))
        s = max(1, int(self.size * (self.life / self.max_life)))
        spark_surf = pygame.Surface((s * 4 + 2, s * 4 + 2), pygame.SRCALPHA)
        c = (self.color[0], self.color[1], self.color[2], alpha)
        cx, cy = s * 2 + 1, s * 2 + 1
        pygame.draw.line(spark_surf, c, (cx - s * 2, cy), (cx + s * 2, cy), 1)
        pygame.draw.line(spark_surf, c, (cx, cy - s * 2), (cx, cy + s * 2), 1)
        pygame.draw.circle(spark_surf, (255, 255, 255, alpha), (cx, cy), max(1, s // 2))
        surface.blit(spark_surf, (int(self.x) - cx, int(self.y) - cy))


class ExplosionParticle:
    """Muffled underwater explosion fragment with smoke and fire ember."""

    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(1.5, 7.5)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.drag = random.uniform(0.88, 0.94)  # High water drag
        self.max_life = random.uniform(0.4, 0.9)
        self.life = self.max_life
        self.radius = random.uniform(3.0, 8.0)
        # Colors transition from bright fire -> orange -> deep murky smoke
        self.is_smoke = random.random() < 0.45

    def update(self, dt):
        self.life -= dt
        self.x += self.vx * (60.0 * dt)
        self.y += self.vy * (60.0 * dt)
        self.vx *= self.drag
        self.vy *= self.drag
        self.y -= 0.3 * (60.0 * dt)  # Smoke drifts upwards
        return self.life > 0

    def draw(self, surface):
        ratio = self.life / self.max_life
        alpha = int(220 * ratio)
        r = max(1, int(self.radius * (1.2 - 0.2 * ratio)))
        surf = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
        if self.is_smoke:
            c = (45, 55, 65, alpha)
        else:
            if ratio > 0.6:
                c = (255, 220, 80, alpha)
            elif ratio > 0.3:
                c = (255, 120, 30, alpha)
            else:
                c = (180, 40, 20, alpha)
        pygame.draw.circle(surf, c, (r + 2, r + 2), r)
        surface.blit(surf, (int(self.x) - r - 2, int(self.y) - r - 2))


class Shockwave:
    """Expanding circular shockwave ring from explosion or shield deflection."""

    def __init__(self, x, y, max_radius=80, color=COLOR_CYAN, duration=0.45):
        self.x = float(x)
        self.y = float(y)
        self.radius = 4.0
        self.max_radius = max_radius
        self.duration = duration
        self.elapsed = 0.0
        self.color = color

    def update(self, dt):
        self.elapsed += dt
        ratio = self.elapsed / self.duration
        self.radius = 4.0 + (self.max_radius - 4.0) * ratio
        return self.elapsed < self.duration

    def draw(self, surface):
        ratio = self.elapsed / self.duration
        alpha = int(240 * (1.0 - ratio))
        r = int(self.radius)
        if r <= 1:
            return
        surf = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
        c = (self.color[0], self.color[1], self.color[2], alpha)
        pygame.draw.circle(surf, c, (r + 2, r + 2), r, width=max(1, int(3 * (1.0 - ratio))))
        surface.blit(surf, (int(self.x) - r - 2, int(self.y) - r - 2))


class SonarWave:
    """Expanding sonar echolocation wave ring emitted from submarine."""

    def __init__(self, x, y, max_radius=420, speed=380.0):
        self.x = float(x)
        self.y = float(y)
        self.radius = 10.0
        self.max_radius = max_radius
        self.speed = speed
        self.active = True

    def update(self, dt):
        self.radius += self.speed * dt
        if self.radius >= self.max_radius:
            self.active = False
        return self.active

    def draw(self, surface):
        ratio = self.radius / self.max_radius
        alpha = int(180 * (1.0 - ratio))
        r = int(self.radius)
        if r <= 1:
            return
        surf = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
        c = (70, 230, 255, alpha)
        # Main wavefront ring
        pygame.draw.circle(surf, c, (r + 2, r + 2), r, width=2)
        # Inner harmonic acoustic ripple
        if r > 25:
            inner_alpha = int(alpha * 0.45)
            pygame.draw.circle(surf, (50, 190, 230, inner_alpha), (r + 2, r + 2), r - 12, width=1)
        surface.blit(surf, (int(self.x) - r - 2, int(self.y) - r - 2))


class ParticleManager:
    """Central manager handling particle updates and rendering."""

    def __init__(self):
        self.bubbles = []
        self.sparkles = []
        self.explosions = []
        self.shockwaves = []
        self.sonar_waves = []
        # Seed initial ambient bubbles across the screen
        for _ in range(40):
            bx = random.uniform(0, SCREEN_WIDTH)
            by = random.uniform(0, SCREEN_HEIGHT)
            self.bubbles.append(Bubble(bx, by))

    def emit_propeller_bubbles(self, x, y, is_boost=False):
        count = 3 if is_boost else 1
        for _ in range(count):
            self.bubbles.append(
                Bubble(x + random.uniform(-4, 4), y + random.uniform(-3, 3), is_propeller=True, is_boost=is_boost)
            )

    def emit_sparkles(self, x, y, color=COLOR_GOLD, count=14):
        for _ in range(count):
            self.sparkles.append(Sparkle(x, y, color=color))

    def emit_explosion(self, x, y, count=28):
        for _ in range(count):
            self.explosions.append(ExplosionParticle(x, y))
        self.shockwaves.append(Shockwave(x, y, max_radius=90, color=(255, 140, 40), duration=0.4))
        # Extra debris bubbles
        for _ in range(12):
            self.bubbles.append(Bubble(x + random.uniform(-10, 10), y + random.uniform(-10, 10), is_propeller=True))

    def emit_shield_deflect(self, x, y):
        self.shockwaves.append(Shockwave(x, y, max_radius=85, color=COLOR_CYAN, duration=0.35))
        self.emit_sparkles(x, y, color=COLOR_CYAN, count=16)

    def emit_sonar_wave(self, x, y):
        self.sonar_waves.append(SonarWave(x, y))

    def update(self, dt):
        # Maintain ambient bubbles count
        if len([b for b in self.bubbles if not b.is_propeller]) < 35:
            if random.random() < 0.25:
                self.bubbles.append(Bubble(random.uniform(0, SCREEN_WIDTH), SCREEN_HEIGHT + 10))

        self.bubbles = [b for b in self.bubbles if b.update(dt)]
        self.sparkles = [s for s in self.sparkles if s.update(dt)]
        self.explosions = [e for e in self.explosions if e.update(dt)]
        self.shockwaves = [sw for sw in self.shockwaves if sw.update(dt)]
        self.sonar_waves = [sw for sw in self.sonar_waves if sw.update(dt)]

    def draw(self, surface):
        for sw in self.sonar_waves:
            sw.draw(surface)
        for b in self.bubbles:
            b.draw(surface)
        for e in self.explosions:
            e.draw(surface)
        for sw in self.shockwaves:
            sw.draw(surface)
        for s in self.sparkles:
            s.draw(surface)
