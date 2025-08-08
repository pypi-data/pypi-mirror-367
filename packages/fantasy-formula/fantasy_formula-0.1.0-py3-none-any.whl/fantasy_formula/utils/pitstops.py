"""Pit stop analysis utilities."""

import logging
from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np
import fastf1

from ..models import PitStopData

logger = logging.getLogger(__name__)


class PitStopAnalyzer:
    """Analyzes pit stop data for fantasy scoring."""
    
    def __init__(self):
        self.minimum_pit_time = 1.5    # Minimum realistic pit stop time
        self.maximum_pit_time = 60.0   # Maximum time to consider valid
        
    def extract_pit_stops_from_session(
        self,
        session: fastf1.core.Session
    ) -> Dict[str, List[PitStopData]]:
        """Extract pit stop data for all drivers from a session.
        
        Args:
            session: FastF1 session object with loaded data
            
        Returns:
            Dictionary mapping driver abbreviations to list of pit stops
        """
        logger.info("Extracting pit stop data from session")
        
        all_pit_stops = {}
        
        try:
            if not hasattr(session, 'laps') or session.laps is None:
                logger.warning("No lap data available for pit stop analysis")
                return all_pit_stops
            
            # Get unique drivers from the session
            drivers = session.laps['Driver'].unique()
            
            for driver in drivers:
                if pd.isna(driver):
                    continue
                    
                driver_pit_stops = self._extract_driver_pit_stops(session, driver)
                if driver_pit_stops:
                    all_pit_stops[driver] = driver_pit_stops
            
            logger.info(f"Extracted pit stops for {len(all_pit_stops)} drivers")
            return all_pit_stops
            
        except Exception as e:
            logger.error(f"Error extracting pit stops: {e}")
            return all_pit_stops
    
    def _extract_driver_pit_stops(
        self,
        session: fastf1.core.Session,
        driver: str
    ) -> List[PitStopData]:
        """Extract pit stops for a specific driver."""
        pit_stops = []
        
        try:
            driver_laps = session.laps.pick_driver(driver)
            
            if driver_laps.empty:
                return pit_stops
            
            # Get team name for the driver
            team_name = self._get_driver_team(session, driver)
            
            # Look for pit stop indicators in lap data
            for idx, lap in driver_laps.iterrows():
                pit_time = self._calculate_pit_stop_time(lap, session)
                
                if pit_time is not None and self._is_valid_pit_stop(pit_time):
                    pit_stop = PitStopData(
                        lap=int(lap['LapNumber']),
                        pit_time=pit_time,
                        driver=driver,
                        team=team_name
                    )
                    pit_stops.append(pit_stop)
            
            logger.debug(f"Found {len(pit_stops)} pit stops for {driver}")
            return pit_stops
            
        except Exception as e:
            logger.error(f"Error extracting pit stops for {driver}: {e}")
            return pit_stops
    
    def _calculate_pit_stop_time(
        self,
        lap_data,
        session: fastf1.core.Session
    ) -> Optional[float]:
        """Calculate pit stop time from lap data.
        
        This is a simplified implementation. A full implementation would
        use detailed telemetry to get accurate pit stop times.
        """
        try:
            # Method 1: Direct pit stop timing (if available)
            if hasattr(lap_data, 'PitInTime') and hasattr(lap_data, 'PitOutTime'):
                pit_in = lap_data.PitInTime
                pit_out = lap_data.PitOutTime
                
                if not pd.isna(pit_in) and not pd.isna(pit_out):
                    duration = (pit_out - pit_in).total_seconds()
                    return duration
            
            # Method 2: Estimate from lap time analysis
            # This is very simplified - real implementation would be more complex
            if hasattr(lap_data, 'LapTime') and not pd.isna(lap_data.LapTime):
                lap_time = lap_data.LapTime.total_seconds()
                
                # If lap time is unusually long, it might include a pit stop
                # Compare to typical lap times for the session
                typical_lap_time = self._get_typical_lap_time(session)
                
                if typical_lap_time and lap_time > typical_lap_time * 1.8:
                    # Estimate pit stop time as the excess over typical lap time
                    estimated_pit_time = lap_time - typical_lap_time
                    
                    # Only return if it's in a reasonable range
                    if self.minimum_pit_time <= estimated_pit_time <= 30:
                        return estimated_pit_time
            
            return None
            
        except Exception as e:
            logger.debug(f"Error calculating pit stop time: {e}")
            return None
    
    def _get_typical_lap_time(
        self,
        session: fastf1.core.Session
    ) -> Optional[float]:
        """Get typical lap time for the session (for comparison)."""
        try:
            if not hasattr(session, 'laps') or session.laps is None:
                return None
            
            # Get median lap time excluding outliers
            valid_lap_times = []
            
            for idx, lap in session.laps.iterrows():
                if hasattr(lap, 'LapTime') and not pd.isna(lap.LapTime):
                    lap_time = lap.LapTime.total_seconds()
                    if 60 <= lap_time <= 150:  # Reasonable F1 lap time range
                        valid_lap_times.append(lap_time)
            
            if len(valid_lap_times) > 10:
                return np.median(valid_lap_times)
            
            return None
            
        except Exception:
            return None
    
    def _is_valid_pit_stop(self, pit_time: float) -> bool:
        """Check if pit stop time is valid."""
        return self.minimum_pit_time <= pit_time <= self.maximum_pit_time
    
    def _get_driver_team(
        self,
        session: fastf1.core.Session,
        driver: str
    ) -> str:
        """Get team name for a driver."""
        try:
            if hasattr(session, 'results') and session.results is not None:
                driver_result = session.results[session.results['Abbreviation'] == driver]
                if not driver_result.empty:
                    team = driver_result.iloc[0].get('TeamName')
                    if team and not pd.isna(team):
                        return str(team)
            
            # Fallback: try to get from lap data
            driver_laps = session.laps.pick_driver(driver)
            if not driver_laps.empty:
                team = driver_laps.iloc[0].get('Team')
                if team and not pd.isna(team):
                    return str(team)
            
            return "Unknown"
            
        except Exception:
            return "Unknown"
    
    def get_fastest_pit_stops_by_team(
        self,
        all_pit_stops: Dict[str, List[PitStopData]]
    ) -> Dict[str, float]:
        """Get fastest pit stop time for each team.
        
        Args:
            all_pit_stops: Dictionary of all pit stops by driver
            
        Returns:
            Dictionary mapping team names to fastest pit stop times
        """
        team_fastest = {}
        
        for driver, pit_stops in all_pit_stops.items():
            for pit_stop in pit_stops:
                team = pit_stop.team
                pit_time = pit_stop.pit_time
                
                if team not in team_fastest or pit_time < team_fastest[team]:
                    team_fastest[team] = pit_time
        
        return team_fastest
    
    def find_fastest_pit_stop_of_session(
        self,
        all_pit_stops: Dict[str, List[PitStopData]]
    ) -> Tuple[Optional[str], Optional[float], Optional[str]]:
        """Find the fastest pit stop of the entire session.
        
        Args:
            all_pit_stops: Dictionary of all pit stops by driver
            
        Returns:
            Tuple of (team_name, pit_time, driver_abbreviation) or (None, None, None)
        """
        fastest_team = None
        fastest_time = None
        fastest_driver = None
        
        for driver, pit_stops in all_pit_stops.items():
            for pit_stop in pit_stops:
                if fastest_time is None or pit_stop.pit_time < fastest_time:
                    fastest_time = pit_stop.pit_time
                    fastest_team = pit_stop.team
                    fastest_driver = driver
        
        return fastest_team, fastest_time, fastest_driver
    
    def check_world_record_pit_stops(
        self,
        all_pit_stops: Dict[str, List[PitStopData]],
        world_record_threshold: float = 1.8
    ) -> List[Tuple[str, float, str]]:
        """Check for world record pit stops.
        
        Args:
            all_pit_stops: Dictionary of all pit stops by driver
            world_record_threshold: Time threshold for world record (seconds)
            
        Returns:
            List of tuples (team_name, pit_time, driver) for world record stops
        """
        world_records = []
        
        for driver, pit_stops in all_pit_stops.items():
            for pit_stop in pit_stops:
                if pit_stop.pit_time < world_record_threshold:
                    world_records.append((pit_stop.team, pit_stop.pit_time, driver))
                    logger.info(
                        f"World record pit stop: {pit_stop.team} - {pit_stop.pit_time:.3f}s "
                        f"(driver: {driver})"
                    )
        
        return world_records
    
    def get_pit_stop_summary(
        self,
        all_pit_stops: Dict[str, List[PitStopData]]
    ) -> Dict[str, any]:
        """Generate summary of pit stop analysis.
        
        Args:
            all_pit_stops: Dictionary of all pit stops by driver
            
        Returns:
            Dictionary with pit stop summary information
        """
        if not all_pit_stops:
            return {'total_pit_stops': 0, 'teams_with_stops': 0}
        
        total_stops = sum(len(stops) for stops in all_pit_stops.values())
        teams_with_stops = len(set(
            stop.team for stops in all_pit_stops.values() for stop in stops
        ))
        
        fastest_team, fastest_time, fastest_driver = self.find_fastest_pit_stop_of_session(
            all_pit_stops
        )
        
        team_fastest = self.get_fastest_pit_stops_by_team(all_pit_stops)
        
        world_records = self.check_world_record_pit_stops(all_pit_stops)
        
        summary = {
            'total_pit_stops': total_stops,
            'drivers_with_stops': len(all_pit_stops),
            'teams_with_stops': teams_with_stops,
            'fastest_overall': {
                'team': fastest_team,
                'time': fastest_time,
                'driver': fastest_driver
            } if fastest_time else None,
            'team_fastest_times': team_fastest,
            'world_records': world_records,
            'analysis_notes': [
                "Pit stop times calculated from available telemetry data",
                "Times may be estimates based on lap time analysis",
                "Actual pit stop times require detailed telemetry analysis"
            ]
        }
        
        return summary