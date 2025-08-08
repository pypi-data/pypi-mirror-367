"""Driver status analysis utilities."""

import logging
from typing import Dict, List, Optional, Tuple
import requests
from bs4 import BeautifulSoup
import re

logger = logging.getLogger(__name__)


class DriverStatusAnalyzer:
    """Analyzes driver status and special achievements like Driver of the Day."""
    
    def __init__(self):
        self.dotd_cache = {}  # Cache DOTD results to avoid repeated requests
        
    def determine_driver_of_the_day(
        self,
        season: int,
        round_num: int,
        manual_override: Optional[str] = None
    ) -> Optional[str]:
        """Determine Driver of the Day for a race.
        
        Args:
            season: F1 season year
            round_num: Race round number
            manual_override: Manual driver abbreviation if API/scraping fails
            
        Returns:
            Driver abbreviation of DOTD, or None if not found
        """
        if manual_override:
            logger.info(f"Using manual DOTD override: {manual_override}")
            return manual_override
        
        # Check cache first
        cache_key = f"{season}_{round_num}"
        if cache_key in self.dotd_cache:
            return self.dotd_cache[cache_key]
        
        try:
            # Try to get DOTD from official F1 website (simplified)
            dotd = self._scrape_driver_of_the_day(season, round_num)
            
            if dotd:
                self.dotd_cache[cache_key] = dotd
                logger.info(f"Found Driver of the Day for {season} R{round_num}: {dotd}")
                return dotd
            
        except Exception as e:
            logger.warning(f"Could not determine DOTD for {season} R{round_num}: {e}")
        
        return None
    
    def _scrape_driver_of_the_day(
        self,
        season: int, 
        round_num: int
    ) -> Optional[str]:
        """Attempt to scrape DOTD from F1 website.
        
        Note: This is a simplified implementation. A production version
        would need more robust scraping or API integration.
        """
        try:
            # This is a placeholder implementation
            # In practice, you'd need to implement proper web scraping
            # or use an API that provides DOTD information
            
            logger.info(f"Would scrape DOTD for {season} round {round_num}")
            
            # For now, return None to indicate no DOTD found
            # This allows the library to work without web scraping dependency
            return None
            
        except Exception as e:
            logger.debug(f"Error scraping DOTD: {e}")
            return None
    
    def apply_driver_of_the_day(
        self,
        race_data_dict: Dict[str, any],
        dotd_driver: Optional[str]
    ) -> Dict[str, any]:
        """Apply Driver of the Day status to race data.
        
        Args:
            race_data_dict: Dictionary of driver abbreviations to RaceData objects
            dotd_driver: Driver abbreviation who won DOTD
            
        Returns:
            Updated race data dictionary
        """
        if not dotd_driver:
            return race_data_dict
        
        # Find the driver and mark as DOTD
        for driver_abbr, race_data in race_data_dict.items():
            if driver_abbr == dotd_driver:
                race_data.is_driver_of_the_day = True
                logger.info(f"Applied DOTD bonus to {driver_abbr}")
                break
        else:
            logger.warning(f"DOTD driver {dotd_driver} not found in race data")
        
        return race_data_dict
    
    def validate_driver_statuses(
        self,
        session_data: Dict[str, any]
    ) -> Dict[str, List[str]]:
        """Validate driver statuses for potential issues.
        
        Args:
            session_data: Dictionary of driver data
            
        Returns:
            Dictionary of validation warnings by driver
        """
        warnings = {}
        
        for driver_abbr, data in session_data.items():
            driver_warnings = []
            
            # Check for missing positions
            if data.starting_position is None:
                driver_warnings.append("Missing starting position")
            if data.finishing_position is None and data.status.value != "not_classified":
                driver_warnings.append("Missing finishing position for classified driver")
            
            # Check for inconsistent position data
            if (data.starting_position and data.finishing_position and
                data.status.value == "classified"):
                
                start = data.starting_position
                finish = data.finishing_position
                
                # Sanity checks
                if start < 1 or start > 25:
                    driver_warnings.append(f"Unusual starting position: {start}")
                if finish < 1 or finish > 25:
                    driver_warnings.append(f"Unusual finishing position: {finish}")
            
            # Check for potential data quality issues
            if hasattr(data, 'overtakes_made') and data.overtakes_made > 15:
                driver_warnings.append(f"Unusually high overtake count: {data.overtakes_made}")
            
            if driver_warnings:
                warnings[driver_abbr] = driver_warnings
        
        return warnings
    
    def get_status_summary(
        self,
        session_data: Dict[str, any]
    ) -> Dict[str, int]:
        """Generate summary of driver statuses in session.
        
        Args:
            session_data: Dictionary of driver data
            
        Returns:
            Dictionary with status counts
        """
        summary = {
            'classified': 0,
            'not_classified': 0,
            'disqualified': 0,
            'did_not_start': 0,
            'total_drivers': len(session_data)
        }
        
        for driver_abbr, data in session_data.items():
            status = data.status.value
            if status in summary:
                summary[status] += 1
        
        return summary
    
    def identify_pit_lane_starters(
        self,
        qualifying_data: Dict[str, any],
        race_data: Dict[str, any]
    ) -> List[str]:
        """Identify drivers who started from the pit lane.
        
        Args:
            qualifying_data: Qualifying session data
            race_data: Race session data
            
        Returns:
            List of driver abbreviations who started from pit lane
        """
        pit_lane_starters = []
        
        for driver_abbr in race_data.keys():
            if driver_abbr in qualifying_data:
                qual_pos = qualifying_data[driver_abbr].finishing_position
                race_start_pos = race_data[driver_abbr].starting_position
                
                # Simplified check - if start position is much worse than qualifying
                # and appears to be from pit lane (typically last + 1)
                if qual_pos and race_start_pos:
                    total_drivers = len(race_data)
                    if race_start_pos > total_drivers:
                        pit_lane_starters.append(driver_abbr)
                        logger.info(f"Identified {driver_abbr} as pit lane starter")
        
        return pit_lane_starters
    
    def adjust_positions_for_pit_lane_start(
        self,
        race_data: Dict[str, any],
        pit_lane_starters: List[str]
    ) -> Dict[str, any]:
        """Adjust starting positions for pit lane starters.
        
        For fantasy scoring, pit lane starters are considered to start 
        from the last grid position + 1.
        
        Args:
            race_data: Race session data
            pit_lane_starters: List of drivers who started from pit lane
            
        Returns:
            Updated race data with adjusted starting positions
        """
        if not pit_lane_starters:
            return race_data
        
        # Find the highest grid position
        max_grid_pos = 0
        for driver_data in race_data.values():
            if driver_data.starting_position and driver_data.starting_position <= 20:
                max_grid_pos = max(max_grid_pos, driver_data.starting_position)
        
        # Adjust pit lane starters
        for driver_abbr in pit_lane_starters:
            if driver_abbr in race_data:
                max_grid_pos += 1
                race_data[driver_abbr].starting_position = max_grid_pos
                logger.info(
                    f"Adjusted {driver_abbr} pit lane start position to {max_grid_pos}"
                )
        
        return race_data