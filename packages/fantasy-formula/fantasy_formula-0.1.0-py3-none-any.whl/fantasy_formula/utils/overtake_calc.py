"""Overtake calculation utilities using FastF1 telemetry data."""

import logging
from typing import Dict, List, Tuple, Optional
import pandas as pd
import numpy as np
import fastf1

logger = logging.getLogger(__name__)


class OvertakeCalculator:
    """Calculates valid overtakes from FastF1 session data."""
    
    def __init__(self):
        self.min_lap_for_overtakes = 2  # Skip first lap for calculations
        self.pit_lane_threshold = 0.1   # Threshold for detecting pit lane activity
        
    def calculate_overtakes_for_session(
        self, 
        session: fastf1.core.Session
    ) -> Dict[str, int]:
        """Calculate overtakes for all drivers in a session.
        
        Args:
            session: FastF1 session object with loaded data
            
        Returns:
            Dictionary mapping driver abbreviations to overtake counts
        """
        logger.info("Calculating overtakes for session")
        
        try:
            if not hasattr(session, 'laps') or session.laps is None:
                logger.warning("No lap data available for overtake calculations")
                return {}
            
            # Get lap-by-lap position data
            position_data = self._extract_position_data(session)
            
            if position_data.empty:
                logger.warning("No position data available")
                return {}
            
            # Calculate overtakes for each driver
            overtakes = {}
            drivers = position_data.columns.difference(['LapNumber'])
            
            for driver in drivers:
                driver_overtakes = self._calculate_driver_overtakes(
                    position_data, driver, session
                )
                overtakes[driver] = driver_overtakes
            
            logger.info(f"Calculated overtakes for {len(overtakes)} drivers")
            return overtakes
            
        except Exception as e:
            logger.error(f"Error calculating overtakes: {e}")
            return {}
    
    def _extract_position_data(
        self, 
        session: fastf1.core.Session
    ) -> pd.DataFrame:
        """Extract lap-by-lap position data from session."""
        try:
            # Get all laps and create position matrix
            laps = session.laps
            
            if laps.empty:
                return pd.DataFrame()
            
            # Create a pivot table with lap numbers and driver positions
            position_data = laps.pivot_table(
                values='Position',
                index='LapNumber', 
                columns='Driver',
                aggfunc='first'
            ).reset_index()
            
            # Forward fill positions for consistency
            for col in position_data.columns:
                if col != 'LapNumber':
                    position_data[col] = position_data[col].fillna(method='ffill')
            
            return position_data
            
        except Exception as e:
            logger.error(f"Error extracting position data: {e}")
            return pd.DataFrame()
    
    def _calculate_driver_overtakes(
        self,
        position_data: pd.DataFrame,
        driver: str,
        session: fastf1.core.Session
    ) -> int:
        """Calculate valid overtakes for a specific driver."""
        overtakes = 0
        
        try:
            if driver not in position_data.columns:
                return 0
            
            driver_positions = position_data[['LapNumber', driver]].dropna()
            
            if len(driver_positions) < 2:
                return 0
            
            # Look at position changes lap by lap
            for i in range(1, len(driver_positions)):
                current_lap = driver_positions.iloc[i]['LapNumber']
                prev_lap = driver_positions.iloc[i-1]['LapNumber']
                
                current_pos = driver_positions.iloc[i][driver]
                prev_pos = driver_positions.iloc[i-1][driver]
                
                # Skip if positions are invalid or laps aren't consecutive
                if (pd.isna(current_pos) or pd.isna(prev_pos) or 
                    current_lap - prev_lap > 1 or current_lap < self.min_lap_for_overtakes):
                    continue
                
                # Check if driver improved position
                if current_pos < prev_pos:  # Lower position number = better
                    positions_gained = prev_pos - current_pos
                    
                    # Validate these are legitimate overtakes
                    valid_overtakes = self._validate_overtakes(
                        session, driver, int(current_lap), int(positions_gained)
                    )
                    
                    overtakes += valid_overtakes
            
            logger.debug(f"Driver {driver} made {overtakes} valid overtakes")
            return overtakes
            
        except Exception as e:
            logger.error(f"Error calculating overtakes for {driver}: {e}")
            return 0
    
    def _validate_overtakes(
        self,
        session: fastf1.core.Session,
        driver: str,
        lap_number: int,
        positions_gained: int
    ) -> int:
        """Validate that position gains are legitimate overtakes.
        
        This is a simplified validation - a full implementation would use
        telemetry data to verify on-track overtakes vs pit stops, etc.
        """
        try:
            # Get lap data for this driver and lap
            driver_laps = session.laps.pick_driver(driver)
            lap_data = driver_laps[driver_laps['LapNumber'] == lap_number]
            
            if lap_data.empty:
                return 0
            
            lap_row = lap_data.iloc[0]
            
            # Check if this was a pit stop lap (simplified check)
            if self._is_pit_stop_lap(lap_row):
                # Don't count position gains from pit stops as overtakes
                return 0
            
            # Check if lap time is reasonable (not too slow indicating issues)
            if self._is_lap_time_reasonable(lap_row, session):
                # Assume all position gains are valid overtakes for now
                # In a more sophisticated implementation, we would analyze
                # telemetry to confirm actual on-track overtakes
                return min(positions_gained, 5)  # Cap at 5 to avoid anomalies
            
            return 0
            
        except Exception as e:
            logger.debug(f"Error validating overtakes for {driver} lap {lap_number}: {e}")
            # Be conservative and count the overtakes if we can't validate
            return min(positions_gained, 2)
    
    def _is_pit_stop_lap(self, lap_data) -> bool:
        """Check if this lap involved a pit stop."""
        try:
            # Check for pit stop indicators in the data
            if hasattr(lap_data, 'PitInTime') and not pd.isna(lap_data.PitInTime):
                return True
            if hasattr(lap_data, 'PitOutTime') and not pd.isna(lap_data.PitOutTime):
                return True
            
            # Check for unusually long lap times that might indicate pit stops
            if hasattr(lap_data, 'LapTime') and not pd.isna(lap_data.LapTime):
                lap_time_seconds = lap_data.LapTime.total_seconds()
                # If lap time is more than 2x normal, likely a pit stop
                if lap_time_seconds > 180:  # 3 minutes is definitely a pit stop
                    return True
            
            return False
            
        except Exception:
            return False
    
    def _is_lap_time_reasonable(
        self, 
        lap_data, 
        session: fastf1.core.Session
    ) -> bool:
        """Check if lap time is reasonable (not indicating car problems)."""
        try:
            if not hasattr(lap_data, 'LapTime') or pd.isna(lap_data.LapTime):
                return True  # Assume reasonable if no data
            
            lap_time_seconds = lap_data.LapTime.total_seconds()
            
            # Very basic check - reject extremely slow laps
            if lap_time_seconds > 150:  # 2.5 minutes is very slow for F1
                return False
            
            # Could add more sophisticated checks here comparing to 
            # session average, track limits, etc.
            
            return True
            
        except Exception:
            return True  # Be permissive if we can't validate
    
    def get_overtake_summary(
        self, 
        session: fastf1.core.Session,
        overtakes: Dict[str, int]
    ) -> Dict[str, dict]:
        """Generate summary of overtake calculations.
        
        Args:
            session: FastF1 session object
            overtakes: Dictionary of calculated overtakes per driver
            
        Returns:
            Dictionary with overtake summary information
        """
        summary = {}
        
        try:
            total_overtakes = sum(overtakes.values())
            
            summary = {
                'total_overtakes': total_overtakes,
                'drivers_with_overtakes': len([d for d, o in overtakes.items() if o > 0]),
                'top_overtakers': sorted(
                    [(driver, count) for driver, count in overtakes.items()], 
                    key=lambda x: x[1], 
                    reverse=True
                )[:5],
                'session_type': getattr(session, 'name', 'Unknown'),
                'calculation_notes': [
                    "Overtakes calculated from lap-by-lap position changes",
                    "Excludes position gains from pit stops where detectable",
                    "Simplified validation - full telemetry analysis not implemented"
                ]
            }
            
        except Exception as e:
            logger.error(f"Error generating overtake summary: {e}")
            summary = {'error': str(e)}
        
        return summary