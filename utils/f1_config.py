# tdr = tire damage rate
# fbph = fuel burn per hr

F1_CONFIG = {
    "Monaco_Street": {
        "laps": 78,
        "base_lap": 78.5,           # Slow street circuit
        "tdr": 2.8,           # Tires die FASTEST
        "fbph": 115,      # Stop-go traffic
        "pit_time": 25,             # Seconds
        "fuel_tank": 110            # kg
    },
    "Silverstone_Fast": {
        "laps": 52,
        "base_lap": 85.2,           # Fast corners
        "tdr": 1.8,           # Medium wear
        "fbph": 110,
        "pit_time": 25,
        "fuel_tank": 110
    },
    "Spa_LongWet": {
        "laps": 44,
        "base_lap": 96.1,           # Longest lap
        "tdr": 2.2,
        "fbph": 108,
        "pit_time": 25,
        "fuel_tank": 110
    }
}

# Tire multipliers (SOFT wears 3x faster than HARD)
TIRE_MULTIPLIERS = {
    "SOFT": 3.0,
    "MEDIUM": 1.5,
    "HARD": 1.0,
    "INTERMEDIATE": 1.2,
    "WET": 1.0
}
