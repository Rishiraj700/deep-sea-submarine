"""
Configuration and constants for Deep Sea Submarine Arcade Game.
"""

# Screen configuration
SCREEN_WIDTH = 960
SCREEN_HEIGHT = 640
FPS = 60
TITLE = "Abyssal Expedition: Deep Sea Submarine"

# Color Palette (Deep Ocean Aesthetics)
COLOR_OCEAN_SURFACE = (12, 45, 80)
COLOR_OCEAN_MID = (6, 25, 52)
COLOR_OCEAN_ABYSS = (2, 10, 24)
COLOR_SEABED = (15, 20, 30)

COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)
COLOR_CYAN = (80, 230, 255)
COLOR_GOLD = (255, 215, 0)
COLOR_RED = (255, 60, 60)
COLOR_GREEN = (60, 230, 120)
COLOR_ORANGE = (255, 140, 40)
COLOR_YELLOW = (255, 230, 60)
COLOR_GRAY = (140, 150, 165)
COLOR_DARK_GRAY = (30, 35, 45)

# Physics & Submarine Tuning
SUB_ACCEL = 0.55
SUB_MAX_SPEED = 5.2
SUB_BOOST_SPEED = 8.0
SUB_DRAG = 0.92          # Underwater hydrodynamic friction
SUB_BUOYANCY = -0.06     # Gentle upward buoyancy force in water
SUB_WIDTH = 84
SUB_HEIGHT = 44

# Gameplay Rules & Balancing
MAX_HULL = 100           # Hull integrity percentage (100% max)
DAMAGE_MINE = 35         # Mine hit penalty
DAMAGE_TORPEDO = 45      # Torpedo hit penalty
MAX_OXYGEN = 100         # Oxygen percentage
OXYGEN_DEPLETION_RATE = 2.2  # Units per second
OXYGEN_CLAM_BONUS = 25   # Clam restores 25% oxygen
OXYGEN_BOOST_COST = 5.0  # Oxygen consumed per second during nitro boost

SONAR_COOLDOWN = 4.0     # Seconds between sonar pings
SONAR_SPEED = 480.0      # Pixels per second expansion
COMBO_TIMEOUT = 3.2      # Seconds before combo multiplier resets

# Depth Zones (Difficulty Progression)
ZONE_SUNLIGHT_MAX = 250   # 0 - 250m
ZONE_TWILIGHT_MAX = 600   # 250 - 600m
ZONE_MIDNIGHT_MAX = 1000  # 600 - 1000m+

# Scoring System
SCORE_PEARL = 100
SCORE_CLAM = 350
SCORE_SHIELD_PICKUP = 200
SCORE_DEPTH_RATE = 1.0   # Score per 5 meters descended
MAX_COMBO = 4
