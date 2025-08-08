"""Data preprocessing and normalization for FastF1 session data."""

import logging
from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np
import fastf1

from ..models import (
    SessionType, DriverStatus, QualifyingData, SprintData, RaceData,
    LapData, PitStopData
)

logger = logging.getLogger(__name__)


class DataPreprocessor:
    """Converts FastF1 session data into standardized models."""
    
    def __init__(self):
        self.driver_name_mapping = {}
        self.constructor_mapping = {}
    
    def process_qualifying_session(
        self, 
        session: fastf1.core.Session
    ) -> Dict[str, QualifyingData]:
        """Process qualifying session data into QualifyingData objects.
        
        Args:
            session: FastF1 qualifying session
            
        Returns:
            Dictionary mapping driver abbreviations to QualifyingData
        """
        logger.info("Processing qualifying session data")
        
        qualifying_data = {}
        results = session.results
        
        for idx, driver_result in results.iterrows():
            driver_abbr = driver_result['Abbreviation']
            
            # Handle missing or invalid data
            if pd.isna(driver_abbr):
                continue
                
            # Determine driver status
            status = self._determine_driver_status(driver_result)
            
            # Get qualifying times
            q1_time = self._get_time_value(driver_result.get('Q1'))
            q2_time = self._get_time_value(driver_result.get('Q2'))
            q3_time = self._get_time_value(driver_result.get('Q3'))
            
            # Determine Q2/Q3 progression
            reached_q2 = q2_time is not None
            reached_q3 = q3_time is not None
            
            # Get positions
            finishing_position = self._get_position_value(driver_result.get('Position'))
            grid_position = self._get_position_value(driver_result.get('GridPosition', finishing_position))
            
            qualifying_data[driver_abbr] = QualifyingData(
                session_type=SessionType.QUALIFYING,
                driver_abbreviation=driver_abbr,
                driver_name=str(driver_result.get('DriverName', driver_abbr)),
                team_name=str(driver_result.get('TeamName', 'Unknown')),
                finishing_position=finishing_position,
                status=status,
                q1_time=q1_time,
                q2_time=q2_time,
                q3_time=q3_time,
                reached_q2=reached_q2,
                reached_q3=reached_q3,
                grid_position=grid_position
            )
            
        logger.info(f"Processed {len(qualifying_data)} drivers from qualifying")
        return qualifying_data
    
    def process_sprint_session(
        self,
        session: fastf1.core.Session,
        qualifying_data: Optional[Dict[str, QualifyingData]] = None
    ) -> Dict[str, SprintData]:
        """Process sprint session data into SprintData objects.
        
        Args:
            session: FastF1 sprint session
            qualifying_data: Qualifying data for starting positions
            
        Returns:
            Dictionary mapping driver abbreviations to SprintData
        """
        logger.info("Processing sprint session data")
        
        sprint_data = {}
        results = session.results
        
        for idx, driver_result in results.iterrows():
            driver_abbr = driver_result['Abbreviation']
            
            if pd.isna(driver_abbr):
                continue
            
            # Get starting position (from sprint qualifying or main qualifying)
            starting_pos = self._get_starting_position(
                driver_abbr, driver_result, qualifying_data
            )
            
            # Get finishing position
            finishing_pos = self._get_position_value(driver_result.get('Position'))
            
            # Calculate positions gained/lost
            positions_gained, positions_lost = self._calculate_position_changes(
                starting_pos, finishing_pos
            )
            
            # Get overtakes (will be calculated later with telemetry)
            overtakes = 0  # Placeholder - will be calculated in utils
            
            # Check for fastest lap
            fastest_lap_time = self._get_time_value(driver_result.get('FastestLapTime'))
            is_fastest_lap = self._is_fastest_lap(session, driver_abbr)
            
            status = self._determine_driver_status(driver_result)
            
            sprint_data[driver_abbr] = SprintData(
                session_type=SessionType.SPRINT,
                driver_abbreviation=driver_abbr,
                driver_name=str(driver_result.get('DriverName', driver_abbr)),
                team_name=str(driver_result.get('TeamName', 'Unknown')),
                starting_position=starting_pos,
                finishing_position=finishing_pos,
                status=status,
                fastest_lap_time=fastest_lap_time,
                is_fastest_lap=is_fastest_lap,
                positions_gained=positions_gained,
                positions_lost=positions_lost,
                overtakes_made=overtakes
            )
            
        logger.info(f"Processed {len(sprint_data)} drivers from sprint")
        return sprint_data
    
    def process_race_session(
        self,
        session: fastf1.core.Session,
        qualifying_data: Optional[Dict[str, QualifyingData]] = None
    ) -> Dict[str, RaceData]:
        """Process race session data into RaceData objects.
        
        Args:
            session: FastF1 race session
            qualifying_data: Qualifying data for starting positions
            
        Returns:
            Dictionary mapping driver abbreviations to RaceData
        """
        logger.info("Processing race session data")
        
        race_data = {}
        results = session.results
        
        for idx, driver_result in results.iterrows():
            driver_abbr = driver_result['Abbreviation']
            
            if pd.isna(driver_abbr):
                continue
            
            # Get starting position (from qualifying, accounting for penalties)
            starting_pos = self._get_starting_position(
                driver_abbr, driver_result, qualifying_data
            )
            
            # Get finishing position
            finishing_pos = self._get_position_value(driver_result.get('Position'))
            
            # Calculate positions gained/lost
            positions_gained, positions_lost = self._calculate_position_changes(
                starting_pos, finishing_pos
            )
            
            # Get overtakes (will be calculated later with telemetry)
            overtakes = 0  # Placeholder
            
            # Check for fastest lap
            fastest_lap_time = self._get_time_value(driver_result.get('FastestLapTime'))
            is_fastest_lap = self._is_fastest_lap(session, driver_abbr)
            
            # Driver of the Day (placeholder - will be set externally)
            is_dotd = False
            
            status = self._determine_driver_status(driver_result)
            
            # Process pit stops
            pit_stops = self._get_pit_stops(session, driver_abbr)
            fastest_pit_stop = self._get_fastest_pit_stop_time(pit_stops)
            
            race_data[driver_abbr] = RaceData(
                session_type=SessionType.RACE,
                driver_abbreviation=driver_abbr,
                driver_name=str(driver_result.get('DriverName', driver_abbr)),
                team_name=str(driver_result.get('TeamName', 'Unknown')),
                starting_position=starting_pos,
                finishing_position=finishing_pos,
                status=status,
                fastest_lap_time=fastest_lap_time,
                is_fastest_lap=is_fastest_lap,
                positions_gained=positions_gained,
                positions_lost=positions_lost,
                overtakes_made=overtakes,
                is_driver_of_the_day=is_dotd,
                pit_stops=pit_stops,
                fastest_pit_stop_time=fastest_pit_stop
            )
            
        logger.info(f"Processed {len(race_data)} drivers from race")
        return race_data
    
    def _determine_driver_status(self, driver_result: pd.Series) -> DriverStatus:
        """Determine the driver's session status."""
        status_text = str(driver_result.get('Status', '')).upper()
        position = driver_result.get('Position')
        
        # Check for disqualification
        if 'DISQUALIFIED' in status_text or 'DSQ' in status_text:
            return DriverStatus.DISQUALIFIED
        
        # Check for DNF/NC
        if pd.isna(position) or status_text in ['DNF', 'NC', 'NOT CLASSIFIED']:
            return DriverStatus.NOT_CLASSIFIED
        
        return DriverStatus.CLASSIFIED
    
    def _get_time_value(self, time_value) -> Optional[float]:
        """Extract time value in seconds, handling various formats."""
        if pd.isna(time_value):
            return None
        
        if hasattr(time_value, 'total_seconds'):
            return time_value.total_seconds()
        
        try:
            return float(time_value)
        except (ValueError, TypeError):
            return None
    
    def _get_position_value(self, position) -> Optional[int]:
        """Extract position value, handling NaN."""
        if pd.isna(position):
            return None
        
        try:
            return int(position)
        except (ValueError, TypeError):
            return None
    
    def _get_starting_position(
        self,
        driver_abbr: str,
        driver_result: pd.Series,
        qualifying_data: Optional[Dict[str, QualifyingData]]
    ) -> Optional[int]:
        """Get the starting position for a driver."""
        # First try to get from GridPosition in results
        grid_pos = self._get_position_value(driver_result.get('GridPosition'))
        if grid_pos is not None:
            return grid_pos
        
        # Fall back to qualifying position
        if qualifying_data and driver_abbr in qualifying_data:
            return qualifying_data[driver_abbr].grid_position
        
        # Last resort: use qualifying finishing position
        if qualifying_data and driver_abbr in qualifying_data:
            return qualifying_data[driver_abbr].finishing_position
        
        return None
    
    def _calculate_position_changes(
        self,
        start_pos: Optional[int],
        finish_pos: Optional[int]
    ) -> Tuple[int, int]:
        """Calculate positions gained and lost."""
        if start_pos is None or finish_pos is None:
            return 0, 0
        
        change = start_pos - finish_pos
        
        if change > 0:  # Moved forward
            return change, 0
        elif change < 0:  # Moved backward
            return 0, abs(change)
        else:  # No change
            return 0, 0
    
    def _is_fastest_lap(
        self,
        session: fastf1.core.Session,
        driver_abbr: str
    ) -> bool:
        """Check if driver had fastest lap of the session."""
        try:
            fastest_lap = session.laps.pick_fastest()
            if fastest_lap is not None and hasattr(fastest_lap, 'Driver'):
                return fastest_lap.Driver == driver_abbr
        except Exception as e:
            logger.warning(f"Could not determine fastest lap: {e}")
        
        return False
    
    def _get_pit_stops(
        self,
        session: fastf1.core.Session,
        driver_abbr: str
    ) -> List[PitStopData]:
        """Extract pit stop data for a driver."""
        pit_stops = []
        
        try:
            if hasattr(session, 'laps') and session.laps is not None:
                driver_laps = session.laps.pick_driver(driver_abbr)
                
                # Look for pit stops in the lap data
                for idx, lap in driver_laps.iterrows():
                    if hasattr(lap, 'PitInTime') and not pd.isna(lap.PitInTime):
                        pit_time = self._calculate_pit_stop_time(lap)
                        if pit_time is not None:
                            pit_stops.append(PitStopData(
                                lap=int(lap.LapNumber),
                                pit_time=pit_time,
                                driver=driver_abbr,
                                team=str(getattr(lap, 'Team', 'Unknown'))
                            ))
                            
        except Exception as e:
            logger.warning(f"Could not extract pit stops for {driver_abbr}: {e}")
        
        return pit_stops
    
    def _calculate_pit_stop_time(self, lap_data) -> Optional[float]:
        """Calculate pit stop time from lap data."""
        try:
            # This is a simplified calculation - actual pit stop time calculation
            # would require more detailed telemetry analysis
            if hasattr(lap_data, 'PitInTime') and hasattr(lap_data, 'PitOutTime'):
                pit_in = lap_data.PitInTime
                pit_out = lap_data.PitOutTime
                
                if not pd.isna(pit_in) and not pd.isna(pit_out):
                    duration = (pit_out - pit_in).total_seconds()
                    return duration
        except Exception:
            pass
        
        return None
    
    def _get_fastest_pit_stop_time(
        self,
        pit_stops: List[PitStopData]
    ) -> Optional[float]:
        """Get the fastest pit stop time for a driver."""
        if not pit_stops:
            return None
        
        return min(stop.pit_time for stop in pit_stops)
    
    def get_constructor_mapping(
        self,
        session_data: Dict[str, any]
    ) -> Dict[str, List[str]]:
        """Create mapping of constructors to their drivers."""
        constructor_drivers = {}
        
        for driver_abbr, data in session_data.items():
            team = data.team_name
            if team not in constructor_drivers:
                constructor_drivers[team] = []
            constructor_drivers[team].append(driver_abbr)
        
        return constructor_drivers