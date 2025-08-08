"""Main FantasyScorer interface for Fantasy Formula."""

import logging
from typing import Dict, Optional, Any
from pathlib import Path

from .data import RaceDataLoader, DataPreprocessor
from .scoring import DriverScorer, ConstructorScorer, get_scoring_rules
from .utils import OvertakeCalculator, PitStopAnalyzer, ClassificationHelper, DriverStatusAnalyzer
from .models import (
    DriverWeekendScore, ConstructorWeekendScore,
    SessionType
)
from .config import DEFAULT_SEASON

logger = logging.getLogger(__name__)


class FantasyScorerError(Exception):
    """Raised when FantasyScorer encounters an error."""
    pass


class FantasyScorer:
    """Main interface for calculating Fantasy Formula points based on real race data."""
    
    def __init__(
        self,
        season: int = DEFAULT_SEASON,
        round_num: int = 1,
        scoring_year: int = None,
        cache_dir: Optional[Path] = None,
        enable_cache: bool = True
    ):
        """Initialize the Fantasy Formula scorer.
        
        Args:
            season: F1 season year (e.g., 2025)
            round_num: Race round number (1-24)
            scoring_year: Year for scoring rules (defaults to season year)
            cache_dir: Custom cache directory for FastF1
            enable_cache: Whether to enable FastF1 caching
        """
        self.season = season
        self.round_num = round_num
        self.scoring_year = scoring_year or season
        
        # Initialize components
        self.data_loader = RaceDataLoader(
            season=season,
            round_num=round_num,
            cache_dir=cache_dir,
            enable_cache=enable_cache
        )
        self.preprocessor = DataPreprocessor()
        
        # Get scoring rules for the specified year
        self.scoring_rules = get_scoring_rules(self.scoring_year)
        self.driver_scorer = DriverScorer(self.scoring_rules)
        self.constructor_scorer = ConstructorScorer(self.scoring_rules)
        
        # Initialize utility classes
        self.overtake_calc = OvertakeCalculator()
        self.pitstop_analyzer = PitStopAnalyzer()
        self.classification_helper = ClassificationHelper()
        self.driver_status_analyzer = DriverStatusAnalyzer()
        
        # Cache for processed data
        self._processed_data = {}
        self._session_data_cache = {}
    
    def calculate_full_event(
        self,
        driver_of_the_day: Optional[str] = None,
        transfer_penalties: Optional[Dict[str, int]] = None
    ) -> Dict[str, Any]:
        """Calculate complete fantasy points for all drivers and constructors.
        
        Args:
            driver_of_the_day: Driver abbreviation for DOTD (auto-detected if None)
            transfer_penalties: Dictionary mapping driver abbreviations to penalty points
            
        Returns:
            Dictionary with complete scoring results
        """
        logger.info(f"Calculating full event for {self.season} Round {self.round_num}")
        
        try:
            # Load all session data
            sessions = self.data_loader.get_all_sessions()
            
            # Process each session
            qualifying_data = None
            sprint_data = None
            race_data = None
            
            if sessions.get('qualifying'):
                qualifying_data = self.preprocessor.process_qualifying_session(
                    sessions['qualifying']
                )
                qualifying_data = self.classification_helper.normalize_team_names(
                    qualifying_data
                )
            
            if sessions.get('sprint'):
                sprint_data = self.preprocessor.process_sprint_session(
                    sessions['sprint'], qualifying_data
                )
                sprint_data = self.classification_helper.normalize_team_names(sprint_data)
                
                # Calculate overtakes for sprint
                sprint_overtakes = self.overtake_calc.calculate_overtakes_for_session(
                    sessions['sprint']
                )
                self._apply_overtakes_to_data(sprint_data, sprint_overtakes)
            
            if sessions.get('race'):
                race_data = self.preprocessor.process_race_session(
                    sessions['race'], qualifying_data
                )
                race_data = self.classification_helper.normalize_team_names(race_data)
                
                # Calculate overtakes for race
                race_overtakes = self.overtake_calc.calculate_overtakes_for_session(
                    sessions['race']
                )
                self._apply_overtakes_to_data(race_data, race_overtakes)
                
                # Handle Driver of the Day
                if driver_of_the_day is None:
                    driver_of_the_day = self.driver_status_analyzer.determine_driver_of_the_day(
                        self.season, self.round_num
                    )
                
                if driver_of_the_day:
                    race_data = self.driver_status_analyzer.apply_driver_of_the_day(
                        race_data, driver_of_the_day
                    )
                
                # Handle pit lane starters
                pit_lane_starters = self.driver_status_analyzer.identify_pit_lane_starters(
                    qualifying_data or {}, race_data
                )
                race_data = self.driver_status_analyzer.adjust_positions_for_pit_lane_start(
                    race_data, pit_lane_starters
                )
            
            # Calculate fantasy scores
            results = self._calculate_weekend_scores(
                qualifying_data, sprint_data, race_data, transfer_penalties
            )
            
            # Add metadata
            weekend_info = self.data_loader.get_session_info()
            results.update({
                'event_info': weekend_info,
                'has_sprint': sprint_data is not None,
                'driver_of_the_day': driver_of_the_day,
                'scoring_rules_year': self.scoring_year
            })
            
            logger.info("Successfully calculated full event scoring")
            return results
            
        except Exception as e:
            error_msg = f"Error calculating full event: {e}"
            logger.error(error_msg)
            raise FantasyScorerError(error_msg) from e
    
    def calculate_driver_score(
        self,
        driver_abbr: str,
        **kwargs
    ) -> Optional[DriverWeekendScore]:
        """Calculate fantasy points for a specific driver.
        
        Args:
            driver_abbr: Driver abbreviation (e.g., 'VER', 'HAM')
            **kwargs: Additional arguments passed to calculate_full_event
            
        Returns:
            DriverWeekendScore or None if driver not found
        """
        results = self.calculate_full_event(**kwargs)
        return results.get('drivers', {}).get(driver_abbr)
    
    def calculate_constructor_score(
        self,
        team_name: str,
        **kwargs
    ) -> Optional[ConstructorWeekendScore]:
        """Calculate fantasy points for a specific constructor.
        
        Args:
            team_name: Constructor/team name (e.g., 'Red Bull', 'Ferrari')
            **kwargs: Additional arguments passed to calculate_full_event
            
        Returns:
            ConstructorWeekendScore or None if constructor not found
        """
        results = self.calculate_full_event(**kwargs)
        return results.get('constructors', {}).get(team_name)
    
    def get_session_summary(
        self,
        session_type: str
    ) -> Dict[str, Any]:
        """Get summary information for a specific session.
        
        Args:
            session_type: 'qualifying', 'sprint', or 'race'
            
        Returns:
            Dictionary with session summary
        """
        try:
            session = self.data_loader.get_session(session_type.upper())
            
            if session_type.lower() == 'qualifying':
                data = self.preprocessor.process_qualifying_session(session)
                session_enum = SessionType.QUALIFYING
            elif session_type.lower() == 'sprint':
                data = self.preprocessor.process_sprint_session(session)
                session_enum = SessionType.SPRINT
            elif session_type.lower() == 'race':
                data = self.preprocessor.process_race_session(session)
                session_enum = SessionType.RACE
            else:
                raise ValueError(f"Invalid session type: {session_type}")
            
            summary = self.classification_helper.get_classification_summary(
                data, session_enum
            )
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting session summary: {e}")
            return {'error': str(e)}
    
    def validate_event_data(self) -> Dict[str, Any]:
        """Validate the consistency and completeness of event data.
        
        Returns:
            Dictionary with validation results
        """
        validation_results = {
            'qualifying': {'status': 'not_checked'},
            'sprint': {'status': 'not_checked'},
            'race': {'status': 'not_checked'},
            'overall': {'warnings': [], 'errors': []}
        }
        
        try:
            sessions = self.data_loader.get_all_sessions()
            
            # Validate each session
            for session_name, session in sessions.items():
                if session is None:
                    validation_results[session_name]['status'] = 'not_available'
                    continue
                
                try:
                    # Process session data
                    if session_name == 'qualifying':
                        data = self.preprocessor.process_qualifying_session(session)
                        session_type = SessionType.QUALIFYING
                    elif session_name == 'sprint':
                        data = self.preprocessor.process_sprint_session(session)
                        session_type = SessionType.SPRINT
                    else:  # race
                        data = self.preprocessor.process_race_session(session)
                        session_type = SessionType.RACE
                    
                    # Run validation
                    issues = self.classification_helper.validate_session_results(
                        data, session_type
                    )
                    
                    validation_results[session_name] = {
                        'status': 'validated',
                        'driver_count': len(data),
                        'issues': issues
                    }
                    
                except Exception as e:
                    validation_results[session_name] = {
                        'status': 'error',
                        'error': str(e)
                    }
            
            return validation_results
            
        except Exception as e:
            validation_results['overall']['errors'].append(f"Validation failed: {e}")
            return validation_results
    
    def _calculate_weekend_scores(
        self,
        qualifying_data: Optional[Dict[str, Any]],
        sprint_data: Optional[Dict[str, Any]],
        race_data: Optional[Dict[str, Any]],
        transfer_penalties: Optional[Dict[str, int]] = None
    ) -> Dict[str, Any]:
        """Calculate complete weekend scores for all drivers and constructors."""
        transfer_penalties = transfer_penalties or {}
        
        # Get all unique drivers
        all_drivers = set()
        if qualifying_data:
            all_drivers.update(qualifying_data.keys())
        if sprint_data:
            all_drivers.update(sprint_data.keys())
        if race_data:
            all_drivers.update(race_data.keys())
        
        # Calculate driver scores
        driver_scores = {}
        for driver_abbr in all_drivers:
            qual_data = qualifying_data.get(driver_abbr) if qualifying_data else None
            sprint_data_item = sprint_data.get(driver_abbr) if sprint_data else None
            race_data_item = race_data.get(driver_abbr) if race_data else None
            
            # Get driver info
            driver_name = driver_abbr
            team_name = "Unknown"
            
            for data in [qual_data, sprint_data_item, race_data_item]:
                if data:
                    driver_name = data.driver_name
                    team_name = data.team_name
                    break
            
            # Calculate weekend score
            weekend_score = self.driver_scorer.calculate_driver_weekend_score(
                driver_abbr=driver_abbr,
                driver_name=driver_name,
                team_name=team_name,
                qualifying_data=qual_data,
                sprint_data=sprint_data_item,
                race_data=race_data_item,
                transfer_penalty=transfer_penalties.get(driver_abbr, 0)
            )
            
            driver_scores[driver_abbr] = weekend_score
        
        # Group drivers by team for constructor scoring
        teams = {}
        for driver_abbr, weekend_score in driver_scores.items():
            team_name = weekend_score.team_name
            if team_name not in teams:
                teams[team_name] = []
            teams[team_name].append(driver_abbr)
        
        # Calculate constructor scores
        constructor_scores = {}
        for team_name, team_drivers in teams.items():
            if len(team_drivers) != 2:
                logger.warning(f"Team {team_name} has {len(team_drivers)} drivers: {team_drivers}")
            
            # Get driver session scores for this team
            qual_driver_scores = []
            sprint_driver_scores = []
            race_driver_scores = []
            
            qual_data_list = []
            sprint_data_list = []
            race_data_list = []
            
            for driver_abbr in team_drivers:
                weekend_score = driver_scores[driver_abbr]
                
                if weekend_score.qualifying_score:
                    qual_driver_scores.append(weekend_score.qualifying_score)
                    if qualifying_data and driver_abbr in qualifying_data:
                        qual_data_list.append(qualifying_data[driver_abbr])
                
                if weekend_score.sprint_score:
                    sprint_driver_scores.append(weekend_score.sprint_score)
                    if sprint_data and driver_abbr in sprint_data:
                        sprint_data_list.append(sprint_data[driver_abbr])
                
                if weekend_score.race_score:
                    race_driver_scores.append(weekend_score.race_score)
                    if race_data and driver_abbr in race_data:
                        race_data_list.append(race_data[driver_abbr])
            
            # Calculate constructor session scores
            qual_constructor_score = None
            if qual_driver_scores:
                qual_constructor_score = self.constructor_scorer.score_qualifying_session(
                    team_name, qual_driver_scores, qual_data_list
                )
            
            sprint_constructor_score = None
            if sprint_driver_scores:
                sprint_constructor_score = self.constructor_scorer.score_sprint_session(
                    team_name, sprint_driver_scores, sprint_data_list
                )
            
            race_constructor_score = None
            if race_driver_scores:
                # Need to determine fastest pitstop and world record teams
                fastest_pitstop_team = None
                world_record_team = None
                
                if race_data:
                    # Get all teams' race data for pitstop comparisons
                    all_teams_race_data = {}
                    for team_name_iter, drivers in teams.items():
                        team_race_data = []
                        for driver in drivers:
                            if driver in race_data:
                                team_race_data.append(race_data[driver])
                        if team_race_data:
                            all_teams_race_data[team_name_iter] = team_race_data
                    
                    fastest_pitstop_team, _ = self.constructor_scorer.get_fastest_pitstop_of_race(
                        all_teams_race_data
                    )
                    world_record_team = self.constructor_scorer.get_world_record_pitstop_team(
                        all_teams_race_data
                    )
                
                race_constructor_score = self.constructor_scorer.score_race_session(
                    team_name, race_driver_scores, race_data_list,
                    fastest_pitstop_team, world_record_team
                )
            
            # Calculate weekend constructor score
            constructor_weekend_score = self.constructor_scorer.calculate_constructor_weekend_score(
                team_name, qual_constructor_score, sprint_constructor_score, race_constructor_score
            )
            
            constructor_scores[team_name] = constructor_weekend_score
        
        return {
            'drivers': driver_scores,
            'constructors': constructor_scores
        }
    
    def _apply_overtakes_to_data(
        self,
        session_data: Dict[str, Any],
        overtakes: Dict[str, int]
    ):
        """Apply calculated overtakes to session data."""
        for driver_abbr, overtake_count in overtakes.items():
            if driver_abbr in session_data:
                session_data[driver_abbr].overtakes_made = overtake_count