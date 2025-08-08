"""FastF1 data fetching and session management."""

import logging
from typing import Dict, Optional, Union, List
import fastf1
import pandas as pd
from pathlib import Path

from ..config import CACHE_DIR, FASTF1_CACHE_ENABLED, FASTF1_REQUEST_TIMEOUT

logger = logging.getLogger(__name__)


class SessionDataError(Exception):
    """Raised when session data cannot be loaded or processed."""
    pass


class RaceDataLoader:
    """Handles fetching and caching of F1 session data using FastF1."""

    def __init__(
        self, 
        season: int, 
        round_num: int, 
        cache_dir: Optional[Path] = None,
        enable_cache: bool = True
    ):
        """Initialize the data loader for a specific race weekend.
        
        Args:
            season: F1 season year (e.g., 2025)
            round_num: Race round number (1-24)
            cache_dir: Custom cache directory (uses default if None)
            enable_cache: Whether to enable FastF1 caching
        """
        self.season = season
        self.round_num = round_num
        self.sessions: Dict[str, fastf1.core.Session] = {}
        
        # Configure FastF1 caching
        if enable_cache:
            cache_path = cache_dir or CACHE_DIR
            cache_path.mkdir(parents=True, exist_ok=True)
            fastf1.Cache.enable_cache(str(cache_path))
        
        # Set request timeout
        fastf1.set_log_level('WARNING')  # Reduce FastF1 logging noise
        
    def get_session(
        self, 
        session_type: str, 
        force_reload: bool = False
    ) -> fastf1.core.Session:
        """Load a specific session for the race weekend.
        
        Args:
            session_type: Type of session ('Q', 'S', 'R' for Qualifying, Sprint, Race)
            force_reload: Force reload even if cached in memory
            
        Returns:
            FastF1 Session object
            
        Raises:
            SessionDataError: If session cannot be loaded
        """
        session_key = session_type.upper()
        
        if not force_reload and session_key in self.sessions:
            return self.sessions[session_key]
        
        try:
            logger.info(f"Loading {session_type} session for {self.season} round {self.round_num}")
            
            # Load the session
            session = fastf1.get_session(self.season, self.round_num, session_type)
            session.load(
                weather=False,  # We don't need weather data for fantasy scoring
                messages=False,  # We don't need race messages
                telemetry=True,  # We need telemetry for overtakes
                laps=True,      # We need lap data for positions
            )
            
            self.sessions[session_key] = session
            logger.info(f"Successfully loaded {session_type} session")
            
            return session
            
        except Exception as e:
            error_msg = f"Failed to load {session_type} session for {self.season} round {self.round_num}: {str(e)}"
            logger.error(error_msg)
            raise SessionDataError(error_msg) from e
    
    def get_qualifying_session(self, force_reload: bool = False) -> fastf1.core.Session:
        """Get the qualifying session."""
        return self.get_session('Q', force_reload)
    
    def get_sprint_session(self, force_reload: bool = False) -> Optional[fastf1.core.Session]:
        """Get the sprint session if it exists for this weekend."""
        try:
            return self.get_session('S', force_reload)
        except SessionDataError:
            # Not all weekends have sprint sessions
            logger.info(f"No sprint session found for {self.season} round {self.round_num}")
            return None
    
    def get_race_session(self, force_reload: bool = False) -> fastf1.core.Session:
        """Get the race session."""
        return self.get_session('R', force_reload)
    
    def get_all_sessions(self, force_reload: bool = False) -> Dict[str, Optional[fastf1.core.Session]]:
        """Load all available sessions for the weekend.
        
        Returns:
            Dictionary with session types as keys and Session objects as values
        """
        sessions = {}
        
        # Always try to load qualifying and race
        try:
            sessions['qualifying'] = self.get_qualifying_session(force_reload)
        except SessionDataError as e:
            logger.warning(f"Could not load qualifying: {e}")
            sessions['qualifying'] = None
        
        try:
            sessions['race'] = self.get_race_session(force_reload)
        except SessionDataError as e:
            logger.warning(f"Could not load race: {e}")
            sessions['race'] = None
        
        # Try to load sprint (optional)
        sessions['sprint'] = self.get_sprint_session(force_reload)
        
        return sessions
    
    def validate_session_data(self, session: fastf1.core.Session) -> bool:
        """Validate that a session has the required data for fantasy scoring.
        
        Args:
            session: FastF1 session object
            
        Returns:
            True if session data is valid for fantasy scoring
        """
        try:
            # Check if we have results data
            if session.results is None or session.results.empty:
                logger.warning(f"No results data available for session")
                return False
            
            # Check if we have lap data
            if session.laps is None or session.laps.empty:
                logger.warning(f"No lap data available for session")
                return False
            
            # Check if we have driver information
            drivers = session.results['Abbreviation'].unique()
            if len(drivers) < 10:  # Minimum expected drivers
                logger.warning(f"Insufficient driver data: only {len(drivers)} drivers found")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating session data: {e}")
            return False
    
    def get_session_info(self) -> Dict[str, Union[str, int]]:
        """Get basic information about the race weekend.
        
        Returns:
            Dictionary with race weekend information
        """
        try:
            # Load any session to get weekend info
            qualifying = self.get_qualifying_session()
            
            return {
                'season': self.season,
                'round': self.round_num,
                'event_name': getattr(qualifying, 'event_name', f"Round {self.round_num}"),
                'country': getattr(qualifying, 'country', 'Unknown'),
                'location': getattr(qualifying, 'location', 'Unknown'),
                'date': str(getattr(qualifying, 'date', 'Unknown')),
            }
        except Exception as e:
            logger.warning(f"Could not get session info: {e}")
            return {
                'season': self.season,
                'round': self.round_num,
                'event_name': f"Round {self.round_num}",
                'country': 'Unknown',
                'location': 'Unknown',
                'date': 'Unknown',
            }