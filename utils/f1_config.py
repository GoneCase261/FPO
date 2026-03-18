# tdr  = tire damage rate (% wear per lap, before compound multiplier)
# fbph = fuel burn per hour (kg/h)

F1_CONFIG = {
    "Monaco_Street": {
        "laps":         78,
        "base_lap":     78.5,     # Slow street circuit
        "tdr":           2.8,     # Highest wear — stop-go corners
        "fbph":         115,      # High fuel burn — stop-go traffic
        "pit_time":      25,      # Seconds lost in pits
        "fuel_tank":    110,      # kg
        "default_tire": "SOFT",   # Low speeds, tires don't overheat
    },
    "Silverstone_Fast": {
        "laps":         52,
        "base_lap":     85.2,     # High-speed sweeping corners
        "tdr":           1.8,     # Medium wear
        "fbph":         110,
        "pit_time":      25,
        "fuel_tank":    110,
        "default_tire": "MEDIUM",  # High speed, softs blister quickly
    },
    "Spa_LongWet": {
        "laps":         44,
        "base_lap":     96.1,     # Longest lap on calendar
        "tdr":           2.2,
        "fbph":         108,
        "pit_time":      25,
        "fuel_tank":    110,
        "default_tire": "MEDIUM",  # Long lap, medium most consistent
    },
}

# Compound multipliers applied on top of tdr
# SOFT wears 3x faster than HARD
TIRE_MULTIPLIERS = {
    "SOFT":         3.0,
    "MEDIUM":       1.5,
    "HARD":         1.0,
    "INTERMEDIATE": 1.2,
    "WET":          1.0,
}
