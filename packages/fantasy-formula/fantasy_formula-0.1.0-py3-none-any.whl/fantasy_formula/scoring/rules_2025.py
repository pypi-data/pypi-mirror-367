"""2025 Fantasy Formula scoring rules configuration."""

from dataclasses import dataclass
from typing import Dict, List


@dataclass
class ScoringRules2025:
    """Complete 2025 Fantasy Formula scoring rules."""
    
    # Driver qualifying position points
    QUALIFYING_POINTS = {
        1: 10,   # Pole position
        2: 9,
        3: 8,
        4: 7,
        5: 6,
        6: 5,
        7: 4,
        8: 3,
        9: 2,
        10: 1,
        # 11-20: 0 points (default)
    }
    
    # Driver sprint finishing position points
    SPRINT_POSITION_POINTS = {
        1: 8,
        2: 7,
        3: 6,
        4: 5,
        5: 4,
        6: 3,
        7: 2,
        8: 1,
        # 9-20: 0 points (default)
    }
    
    # Driver race finishing position points (F1 system)
    RACE_POSITION_POINTS = {
        1: 25,
        2: 18,
        3: 15,
        4: 12,
        5: 10,
        6: 8,
        7: 6,
        8: 4,
        9: 2,
        10: 1,
        # 11-20: 0 points (default)
    }
    
    # Position movement points
    POSITIONS_GAINED_POINTS = 1  # Per position gained
    POSITIONS_LOST_POINTS = -1   # Per position lost
    
    # Overtaking points
    OVERTAKE_POINTS = 1  # Per valid overtake made
    
    # Fastest lap bonuses
    SPRINT_FASTEST_LAP_POINTS = 5
    RACE_FASTEST_LAP_POINTS = 10
    
    # Driver of the Day bonus (race only)
    DRIVER_OF_THE_DAY_POINTS = 10
    
    # Penalties
    QUALIFYING_NC_PENALTY = -5      # No time set in Q1
    QUALIFYING_DSQ_PENALTY = -5     # Disqualified in qualifying
    SPRINT_DNF_PENALTY = -20        # DNF/Not classified in sprint
    SPRINT_DSQ_PENALTY = -20        # Disqualified in sprint  
    RACE_DNF_PENALTY = -20          # DNF/Not classified in race
    RACE_DSQ_PENALTY = -20          # Disqualified in race
    
    # Constructor qualifying bonuses
    CONSTRUCTOR_BOTH_Q2_BONUS = 3
    CONSTRUCTOR_BOTH_Q3_BONUS = 10
    CONSTRUCTOR_ONE_Q2_BONUS = 1
    CONSTRUCTOR_ONE_Q3_BONUS = 5
    CONSTRUCTOR_NEITHER_Q2_PENALTY = -1
    
    # Constructor pitstop points (race only)
    PITSTOP_TIME_POINTS = {
        # Time ranges in seconds mapped to points
        (0.0, 2.0): 20,      # Under 2.0s
        (2.0, 2.19): 10,     # 2.00 - 2.19s
        (2.20, 2.49): 5,     # 2.20 - 2.49s
        (2.50, 2.99): 2,     # 2.50 - 2.99s
        (3.0, float('inf')): 0  # Over 3.0s
    }
    
    # Pitstop bonuses
    FASTEST_PITSTOP_BONUS = 5      # Team with fastest pitstop of race
    WORLD_RECORD_PITSTOP_BONUS = 15  # Team that sets world record (under 1.8s)
    WORLD_RECORD_THRESHOLD = 1.8   # Current world record threshold
    
    # Constructor disqualification penalties (additional to driver penalties)
    CONSTRUCTOR_QUALIFYING_DSQ_PENALTY = -5   # Additional penalty per DSQ driver
    CONSTRUCTOR_SPRINT_DSQ_PENALTY = -10      # Additional penalty per DSQ driver  
    CONSTRUCTOR_RACE_DSQ_PENALTY = -10        # Additional penalty per DSQ driver
    
    # Transfer penalties
    TRANSFER_PENALTY = -10  # Per transfer exceeding free allowance
    
    @classmethod
    def get_qualifying_points(cls, position: int) -> int:
        """Get points for qualifying position."""
        return cls.QUALIFYING_POINTS.get(position, 0)
    
    @classmethod
    def get_sprint_position_points(cls, position: int) -> int:
        """Get points for sprint finishing position."""
        return cls.SPRINT_POSITION_POINTS.get(position, 0)
    
    @classmethod
    def get_race_position_points(cls, position: int) -> int:
        """Get points for race finishing position."""
        return cls.RACE_POSITION_POINTS.get(position, 0)
    
    @classmethod
    def get_pitstop_points(cls, pit_time: float) -> int:
        """Get points for pitstop time."""
        for (min_time, max_time), points in cls.PITSTOP_TIME_POINTS.items():
            if min_time <= pit_time < max_time:
                return points
        return 0
    
    @classmethod
    def is_world_record_pitstop(cls, pit_time: float) -> bool:
        """Check if pitstop time is a world record."""
        return pit_time < cls.WORLD_RECORD_THRESHOLD


# Create instances for easy import
DRIVER_RULES_2025 = ScoringRules2025()
CONSTRUCTOR_RULES_2025 = ScoringRules2025()


# Additional configuration for rule variations
RULE_VARIATIONS = {
    "2025": ScoringRules2025,
    # Future years can be added here
    # "2026": ScoringRules2026,
}


def get_scoring_rules(year: int = 2025):
    """Get scoring rules for a specific year."""
    if year in RULE_VARIATIONS:
        return RULE_VARIATIONS[year]()
    else:
        # Default to 2025 rules if year not found
        return ScoringRules2025()


# Helper functions for common calculations
def calculate_position_change_points(
    start_position: int, 
    finish_position: int, 
    rules: ScoringRules2025 = None
) -> tuple[int, int]:
    """Calculate points for position changes.
    
    Returns:
        Tuple of (positions_gained_points, positions_lost_points)
    """
    if rules is None:
        rules = ScoringRules2025()
    
    if start_position is None or finish_position is None:
        return 0, 0
    
    change = start_position - finish_position
    
    if change > 0:  # Moved forward (gained positions)
        return change * rules.POSITIONS_GAINED_POINTS, 0
    elif change < 0:  # Moved backward (lost positions)  
        return 0, abs(change) * rules.POSITIONS_LOST_POINTS
    else:  # No change
        return 0, 0


def calculate_overtake_points(
    overtakes_made: int,
    rules: ScoringRules2025 = None
) -> int:
    """Calculate points for overtakes made."""
    if rules is None:
        rules = ScoringRules2025()
    
    return overtakes_made * rules.OVERTAKE_POINTS


def get_penalty_points(
    session_type: str,
    driver_status: str,
    rules: ScoringRules2025 = None
) -> int:
    """Get penalty points based on driver status and session type."""
    if rules is None:
        rules = ScoringRules2025()
    
    session_type = session_type.lower()
    driver_status = driver_status.lower()
    
    if driver_status == "disqualified":
        if session_type == "qualifying":
            return rules.QUALIFYING_DSQ_PENALTY
        elif session_type == "sprint":
            return rules.SPRINT_DSQ_PENALTY
        elif session_type == "race":
            return rules.RACE_DSQ_PENALTY
    elif driver_status == "not_classified":
        if session_type == "qualifying":
            return rules.QUALIFYING_NC_PENALTY
        elif session_type == "sprint":
            return rules.SPRINT_DNF_PENALTY
        elif session_type == "race":
            return rules.RACE_DNF_PENALTY
    
    return 0


def get_constructor_disqualification_penalty(
    session_type: str,
    num_disqualified_drivers: int,
    rules: ScoringRules2025 = None
) -> int:
    """Get additional constructor penalty for disqualified drivers."""
    if rules is None:
        rules = ScoringRules2025()
    
    session_type = session_type.lower()
    
    if session_type == "qualifying":
        return num_disqualified_drivers * rules.CONSTRUCTOR_QUALIFYING_DSQ_PENALTY
    elif session_type == "sprint":
        return num_disqualified_drivers * rules.CONSTRUCTOR_SPRINT_DSQ_PENALTY
    elif session_type == "race":
        return num_disqualified_drivers * rules.CONSTRUCTOR_RACE_DSQ_PENALTY
    
    return 0