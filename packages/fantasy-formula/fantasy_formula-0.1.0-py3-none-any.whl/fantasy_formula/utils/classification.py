"""Classification and result validation utilities."""

import logging
from typing import Dict, List, Optional, Tuple, Set
import pandas as pd

from ..models import DriverStatus, SessionType

logger = logging.getLogger(__name__)


class ClassificationHelper:
    """Helper for validating and processing F1 classification results."""
    
    def __init__(self):
        self.expected_driver_count = 20  # Standard F1 grid size
        self.position_tolerance = 2      # Allow some flexibility in position validation
    
    def validate_session_results(
        self,
        session_data: Dict[str, any],
        session_type: SessionType
    ) -> Dict[str, List[str]]:
        """Validate session results for consistency and completeness.
        
        Args:
            session_data: Dictionary of driver session data
            session_type: Type of session being validated
            
        Returns:
            Dictionary of validation issues by category
        """
        issues = {
            'missing_data': [],
            'position_gaps': [],
            'duplicate_positions': [],
            'invalid_positions': [],
            'status_inconsistencies': []
        }
        
        try:
            # Check for missing data
            for driver_abbr, data in session_data.items():
                if data.finishing_position is None and data.status == DriverStatus.CLASSIFIED:
                    issues['missing_data'].append(
                        f"{driver_abbr}: Missing finishing position for classified driver"
                    )
                
                if session_type != SessionType.QUALIFYING:
                    if data.starting_position is None:
                        issues['missing_data'].append(
                            f"{driver_abbr}: Missing starting position"
                        )
            
            # Check position consistency
            self._validate_positions(session_data, issues)
            
            # Check status consistency
            self._validate_statuses(session_data, issues, session_type)
            
        except Exception as e:
            logger.error(f"Error validating session results: {e}")
            issues['validation_errors'] = [str(e)]
        
        # Filter out empty issue categories
        return {k: v for k, v in issues.items() if v}
    
    def _validate_positions(
        self,
        session_data: Dict[str, any],
        issues: Dict[str, List[str]]
    ):
        """Validate position data for gaps and duplicates."""
        classified_drivers = [
            (abbr, data) for abbr, data in session_data.items()
            if data.status == DriverStatus.CLASSIFIED and data.finishing_position is not None
        ]
        
        if not classified_drivers:
            return
        
        # Check for duplicate positions
        positions = [data.finishing_position for _, data in classified_drivers]
        position_counts = {}
        for pos in positions:
            position_counts[pos] = position_counts.get(pos, 0) + 1
        
        for pos, count in position_counts.items():
            if count > 1:
                drivers = [abbr for abbr, data in classified_drivers 
                          if data.finishing_position == pos]
                issues['duplicate_positions'].append(
                    f"Position {pos}: {', '.join(drivers)}"
                )
        
        # Check for position gaps
        sorted_positions = sorted(positions)
        expected_positions = list(range(1, len(sorted_positions) + 1))
        
        for expected, actual in zip(expected_positions, sorted_positions):
            if expected != actual:
                issues['position_gaps'].append(
                    f"Expected position {expected}, found {actual}"
                )
                break
        
        # Check for invalid positions
        for abbr, data in classified_drivers:
            pos = data.finishing_position
            if pos < 1 or pos > 25:  # Reasonable F1 position range
                issues['invalid_positions'].append(
                    f"{abbr}: Invalid position {pos}"
                )
    
    def _validate_statuses(
        self,
        session_data: Dict[str, any],
        issues: Dict[str, List[str]],
        session_type: SessionType
    ):
        """Validate driver status consistency."""
        for driver_abbr, data in session_data.items():
            # Check status vs position consistency
            if data.status == DriverStatus.CLASSIFIED:
                if data.finishing_position is None:
                    issues['status_inconsistencies'].append(
                        f"{driver_abbr}: Classified but no finishing position"
                    )
            elif data.status in [DriverStatus.NOT_CLASSIFIED, DriverStatus.DISQUALIFIED]:
                if data.finishing_position is not None:
                    # Some series still assign positions to DNF drivers, so this is just a warning
                    pass
    
    def normalize_team_names(
        self,
        session_data: Dict[str, any]
    ) -> Dict[str, any]:
        """Normalize team names for consistency across sessions.
        
        Args:
            session_data: Dictionary of driver session data
            
        Returns:
            Updated session data with normalized team names
        """
        # Common team name mappings
        team_mappings = {
            'Red Bull Racing Honda RBPT': 'Red Bull',
            'Red Bull Racing': 'Red Bull',
            'Ferrari': 'Ferrari', 
            'Mercedes': 'Mercedes',
            'McLaren Mercedes': 'McLaren',
            'McLaren': 'McLaren',
            'Aston Martin Aramco Mercedes': 'Aston Martin',
            'Aston Martin': 'Aston Martin',
            'Alpine Renault': 'Alpine',
            'Alpine': 'Alpine',
            'Williams Mercedes': 'Williams',
            'Williams': 'Williams',
            'AlphaTauri Honda RBPT': 'AlphaTauri',
            'AlphaTauri': 'AlphaTauri',
            'Alfa Romeo Ferrari': 'Alfa Romeo',
            'Alfa Romeo': 'Alfa Romeo',
            'Haas Ferrari': 'Haas',
            'Haas': 'Haas'
        }
        
        for driver_abbr, data in session_data.items():
            original_team = data.team_name
            normalized_team = team_mappings.get(original_team, original_team)
            
            if normalized_team != original_team:
                data.team_name = normalized_team
                logger.debug(f"Normalized team name: {original_team} -> {normalized_team}")
        
        return session_data
    
    def group_drivers_by_team(
        self,
        session_data: Dict[str, any]
    ) -> Dict[str, List[str]]:
        """Group drivers by their team.
        
        Args:
            session_data: Dictionary of driver session data
            
        Returns:
            Dictionary mapping team names to list of driver abbreviations
        """
        teams = {}
        
        for driver_abbr, data in session_data.items():
            team_name = data.team_name
            if team_name not in teams:
                teams[team_name] = []
            teams[team_name].append(driver_abbr)
        
        return teams
    
    def validate_team_lineups(
        self,
        teams: Dict[str, List[str]]
    ) -> List[str]:
        """Validate that teams have the expected number of drivers.
        
        Args:
            teams: Dictionary mapping team names to driver lists
            
        Returns:
            List of validation warnings
        """
        warnings = []
        
        for team_name, drivers in teams.items():
            if len(drivers) != 2:
                warnings.append(
                    f"{team_name} has {len(drivers)} drivers: {', '.join(drivers)}"
                )
        
        return warnings
    
    def find_missing_drivers(
        self,
        session_data: Dict[str, any],
        expected_drivers: Optional[Set[str]] = None
    ) -> List[str]:
        """Find drivers that are expected but missing from session data.
        
        Args:
            session_data: Dictionary of driver session data
            expected_drivers: Set of expected driver abbreviations
            
        Returns:
            List of missing driver abbreviations
        """
        if expected_drivers is None:
            # Can't check without expected driver list
            return []
        
        present_drivers = set(session_data.keys())
        missing_drivers = expected_drivers - present_drivers
        
        return list(missing_drivers)
    
    def get_classification_summary(
        self,
        session_data: Dict[str, any],
        session_type: SessionType
    ) -> Dict[str, any]:
        """Generate summary of session classification.
        
        Args:
            session_data: Dictionary of driver session data
            session_type: Type of session
            
        Returns:
            Dictionary with classification summary
        """
        summary = {
            'session_type': session_type.value,
            'total_drivers': len(session_data),
            'classified': 0,
            'not_classified': 0,
            'disqualified': 0,
            'did_not_start': 0
        }
        
        for driver_abbr, data in session_data.items():
            status = data.status.value
            if status in summary:
                summary[status] += 1
        
        # Additional session-specific information
        if session_type == SessionType.QUALIFYING:
            summary['drivers_in_q2'] = sum(
                1 for data in session_data.values() 
                if hasattr(data, 'reached_q2') and data.reached_q2
            )
            summary['drivers_in_q3'] = sum(
                1 for data in session_data.values() 
                if hasattr(data, 'reached_q3') and data.reached_q3
            )
        
        elif session_type in [SessionType.SPRINT, SessionType.RACE]:
            total_overtakes = sum(
                data.overtakes_made for data in session_data.values() 
                if hasattr(data, 'overtakes_made')
            )
            summary['total_overtakes'] = total_overtakes
            
            fastest_lap_driver = None
            for driver_abbr, data in session_data.items():
                if hasattr(data, 'is_fastest_lap') and data.is_fastest_lap:
                    fastest_lap_driver = driver_abbr
                    break
            summary['fastest_lap_driver'] = fastest_lap_driver
        
        if session_type == SessionType.RACE:
            dotd_driver = None
            for driver_abbr, data in session_data.items():
                if hasattr(data, 'is_driver_of_the_day') and data.is_driver_of_the_day:
                    dotd_driver = driver_abbr
                    break
            summary['driver_of_the_day'] = dotd_driver
        
        return summary