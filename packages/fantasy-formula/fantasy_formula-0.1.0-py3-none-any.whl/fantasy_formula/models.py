"""Data models for Fantasy Formula scoring."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum


class SessionType(Enum):
    """Types of F1 sessions."""
    QUALIFYING = "qualifying"
    SPRINT = "sprint"
    RACE = "race"


class DriverStatus(Enum):
    """Driver session status."""
    CLASSIFIED = "classified"
    NOT_CLASSIFIED = "not_classified"
    DISQUALIFIED = "disqualified"
    DID_NOT_START = "did_not_start"


@dataclass
class LapData:
    """Represents a single lap of data for a driver."""
    lap_number: int
    position: int
    lap_time: Optional[float] = None
    sector_1_time: Optional[float] = None
    sector_2_time: Optional[float] = None
    sector_3_time: Optional[float] = None
    is_pit_lap: bool = False
    track_status: Optional[str] = None


@dataclass
class PitStopData:
    """Represents a pit stop."""
    lap: int
    pit_time: float
    driver: str
    team: str


@dataclass
class SessionData:
    """Base data for any F1 session."""
    session_type: SessionType
    driver_abbreviation: str
    driver_name: str
    team_name: str
    starting_position: Optional[int] = None
    finishing_position: Optional[int] = None
    status: DriverStatus = DriverStatus.CLASSIFIED
    laps: List[LapData] = field(default_factory=list)
    fastest_lap_time: Optional[float] = None
    is_fastest_lap: bool = False
    


@dataclass 
class QualifyingData(SessionData):
    """Qualifying session specific data."""
    q1_time: Optional[float] = None
    q2_time: Optional[float] = None
    q3_time: Optional[float] = None
    reached_q2: bool = False
    reached_q3: bool = False
    grid_position: Optional[int] = None
    
    def __post_init__(self):
        if self.session_type != SessionType.QUALIFYING:
            self.session_type = SessionType.QUALIFYING


@dataclass
class SprintData(SessionData):
    """Sprint session specific data."""
    positions_gained: int = 0
    positions_lost: int = 0
    overtakes_made: int = 0
    
    def __post_init__(self):
        if self.session_type != SessionType.SPRINT:
            self.session_type = SessionType.SPRINT


@dataclass
class RaceData(SessionData):
    """Race session specific data."""
    positions_gained: int = 0
    positions_lost: int = 0
    overtakes_made: int = 0
    is_driver_of_the_day: bool = False
    pit_stops: List[PitStopData] = field(default_factory=list)
    fastest_pit_stop_time: Optional[float] = None
    
    def __post_init__(self):
        if self.session_type != SessionType.RACE:
            self.session_type = SessionType.RACE


@dataclass
class DriverSessionScore:
    """Fantasy points for a driver in a specific session."""
    driver_abbreviation: str
    session_type: SessionType
    
    # Base scoring components
    finishing_position_points: int = 0
    positions_gained_points: int = 0
    positions_lost_points: int = 0
    overtakes_points: int = 0
    fastest_lap_points: int = 0
    
    # Special bonuses
    driver_of_the_day_points: int = 0
    
    # Penalties
    not_classified_penalty: int = 0
    disqualification_penalty: int = 0
    
    # Qualifying specific
    pole_position_points: int = 0
    q2_progression_points: int = 0
    q3_progression_points: int = 0
    
    @property
    def total_points(self) -> int:
        """Calculate total fantasy points for this session."""
        return (
            self.finishing_position_points +
            self.positions_gained_points +
            self.positions_lost_points +  # This will be negative
            self.overtakes_points +
            self.fastest_lap_points +
            self.driver_of_the_day_points +
            self.pole_position_points +
            self.q2_progression_points +
            self.q3_progression_points +
            self.not_classified_penalty +  # This will be negative
            self.disqualification_penalty  # This will be negative
        )


@dataclass
class ConstructorSessionScore:
    """Fantasy points for a constructor in a specific session."""
    constructor_name: str
    session_type: SessionType
    
    # Combined driver scores
    driver_points_total: int = 0
    
    # Constructor specific bonuses
    both_drivers_q2_bonus: int = 0
    both_drivers_q3_bonus: int = 0
    one_driver_q2_bonus: int = 0
    one_driver_q3_bonus: int = 0
    neither_driver_q2_penalty: int = 0
    
    # Pit stop bonuses (race only)
    pit_stop_time_points: int = 0
    fastest_pit_stop_bonus: int = 0
    world_record_pit_stop_bonus: int = 0
    
    # Penalties
    disqualification_penalty: int = 0
    
    @property
    def total_points(self) -> int:
        """Calculate total fantasy points for this session."""
        return (
            self.driver_points_total +
            self.both_drivers_q2_bonus +
            self.both_drivers_q3_bonus +
            self.one_driver_q2_bonus +
            self.one_driver_q3_bonus +
            self.neither_driver_q2_penalty +  # This will be negative
            self.pit_stop_time_points +
            self.fastest_pit_stop_bonus +
            self.world_record_pit_stop_bonus +
            self.disqualification_penalty  # This will be negative
        )


@dataclass
class DriverWeekendScore:
    """Complete fantasy scoring for a driver across all sessions."""
    driver_abbreviation: str
    driver_name: str
    team_name: str
    
    qualifying_score: Optional[DriverSessionScore] = None
    sprint_score: Optional[DriverSessionScore] = None
    race_score: Optional[DriverSessionScore] = None
    
    # Transfer penalty
    transfer_penalty: int = 0
    
    @property
    def total_points(self) -> int:
        """Calculate total weekend fantasy points."""
        total = self.transfer_penalty  # This will be negative if applicable
        
        if self.qualifying_score:
            total += self.qualifying_score.total_points
        if self.sprint_score:
            total += self.sprint_score.total_points
        if self.race_score:
            total += self.race_score.total_points
            
        return total
    
    def get_session_breakdown(self) -> Dict[str, Dict[str, int]]:
        """Get detailed points breakdown by session."""
        breakdown = {}
        
        if self.qualifying_score:
            breakdown['qualifying'] = {
                'finishing_position': self.qualifying_score.finishing_position_points,
                'pole_position': self.qualifying_score.pole_position_points,
                'not_classified_penalty': self.qualifying_score.not_classified_penalty,
                'disqualification_penalty': self.qualifying_score.disqualification_penalty,
                'total': self.qualifying_score.total_points
            }
        
        if self.sprint_score:
            breakdown['sprint'] = {
                'finishing_position': self.sprint_score.finishing_position_points,
                'positions_gained': self.sprint_score.positions_gained_points,
                'positions_lost': self.sprint_score.positions_lost_points,
                'overtakes': self.sprint_score.overtakes_points,
                'fastest_lap': self.sprint_score.fastest_lap_points,
                'not_classified_penalty': self.sprint_score.not_classified_penalty,
                'disqualification_penalty': self.sprint_score.disqualification_penalty,
                'total': self.sprint_score.total_points
            }
        
        if self.race_score:
            breakdown['race'] = {
                'finishing_position': self.race_score.finishing_position_points,
                'positions_gained': self.race_score.positions_gained_points,
                'positions_lost': self.race_score.positions_lost_points,
                'overtakes': self.race_score.overtakes_points,
                'fastest_lap': self.race_score.fastest_lap_points,
                'driver_of_the_day': self.race_score.driver_of_the_day_points,
                'not_classified_penalty': self.race_score.not_classified_penalty,
                'disqualification_penalty': self.race_score.disqualification_penalty,
                'total': self.race_score.total_points
            }
        
        breakdown['weekend_total'] = self.total_points
        if self.transfer_penalty != 0:
            breakdown['transfer_penalty'] = self.transfer_penalty
            
        return breakdown


@dataclass
class ConstructorWeekendScore:
    """Complete fantasy scoring for a constructor across all sessions."""
    constructor_name: str
    
    qualifying_score: Optional[ConstructorSessionScore] = None
    sprint_score: Optional[ConstructorSessionScore] = None
    race_score: Optional[ConstructorSessionScore] = None
    
    @property
    def total_points(self) -> int:
        """Calculate total weekend fantasy points."""
        total = 0
        
        if self.qualifying_score:
            total += self.qualifying_score.total_points
        if self.sprint_score:
            total += self.sprint_score.total_points
        if self.race_score:
            total += self.race_score.total_points
            
        return total
    
    def get_session_breakdown(self) -> Dict[str, Dict[str, int]]:
        """Get detailed points breakdown by session."""
        breakdown = {}
        
        if self.qualifying_score:
            breakdown['qualifying'] = {
                'driver_points': self.qualifying_score.driver_points_total,
                'both_q2_bonus': self.qualifying_score.both_drivers_q2_bonus,
                'both_q3_bonus': self.qualifying_score.both_drivers_q3_bonus,
                'one_q2_bonus': self.qualifying_score.one_driver_q2_bonus,
                'one_q3_bonus': self.qualifying_score.one_driver_q3_bonus,
                'neither_q2_penalty': self.qualifying_score.neither_driver_q2_penalty,
                'disqualification_penalty': self.qualifying_score.disqualification_penalty,
                'total': self.qualifying_score.total_points
            }
        
        if self.sprint_score:
            breakdown['sprint'] = {
                'driver_points': self.sprint_score.driver_points_total,
                'disqualification_penalty': self.sprint_score.disqualification_penalty,
                'total': self.sprint_score.total_points
            }
        
        if self.race_score:
            breakdown['race'] = {
                'driver_points': self.race_score.driver_points_total,
                'pit_stop_points': self.race_score.pit_stop_time_points,
                'fastest_pit_stop_bonus': self.race_score.fastest_pit_stop_bonus,
                'world_record_bonus': self.race_score.world_record_pit_stop_bonus,
                'disqualification_penalty': self.race_score.disqualification_penalty,
                'total': self.race_score.total_points
            }
        
        breakdown['weekend_total'] = self.total_points
            
        return breakdown


@dataclass
class WeekendResults:
    """Complete results for a race weekend."""
    season: int
    round_number: int
    event_name: str
    
    drivers: Dict[str, DriverWeekendScore] = field(default_factory=dict)
    constructors: Dict[str, ConstructorWeekendScore] = field(default_factory=dict)
    
    # Weekend metadata
    has_sprint: bool = False
    fastest_race_pit_stop_team: Optional[str] = None
    world_record_pit_stop_team: Optional[str] = None
    driver_of_the_day: Optional[str] = None