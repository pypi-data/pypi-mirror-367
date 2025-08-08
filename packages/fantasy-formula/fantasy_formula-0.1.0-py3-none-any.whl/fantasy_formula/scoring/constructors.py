"""Constructor fantasy scoring logic."""

import logging
from typing import Dict, List, Optional, Tuple

from ..models import (
    SessionType, DriverStatus, QualifyingData, SprintData, RaceData,
    DriverSessionScore, ConstructorSessionScore, ConstructorWeekendScore,
    PitStopData
)
from .rules_2025 import ScoringRules2025, get_constructor_disqualification_penalty

logger = logging.getLogger(__name__)


class ConstructorScorer:
    """Calculates fantasy points for constructors across all sessions."""
    
    def __init__(self, scoring_rules: Optional[ScoringRules2025] = None):
        """Initialize with scoring rules.
        
        Args:
            scoring_rules: Scoring rules to use (defaults to 2025 rules)
        """
        self.rules = scoring_rules or ScoringRules2025()
    
    def score_qualifying_session(
        self,
        constructor_name: str,
        driver_scores: List[DriverSessionScore],
        qualifying_data: List[QualifyingData]
    ) -> ConstructorSessionScore:
        """Calculate fantasy points for a constructor's qualifying session.
        
        Args:
            constructor_name: Name of the constructor
            driver_scores: List of both driver session scores
            qualifying_data: List of both drivers' qualifying data
            
        Returns:
            ConstructorSessionScore with qualifying points breakdown
        """
        score = ConstructorSessionScore(
            constructor_name=constructor_name,
            session_type=SessionType.QUALIFYING
        )
        
        # Sum driver points (excluding any constructor-specific penalties)
        score.driver_points_total = sum(ds.total_points for ds in driver_scores)
        
        # Calculate Q2/Q3 progression bonuses
        drivers_in_q2 = sum(1 for qd in qualifying_data if qd.reached_q2)
        drivers_in_q3 = sum(1 for qd in qualifying_data if qd.reached_q3)
        
        if drivers_in_q3 == 2:
            score.both_drivers_q3_bonus = self.rules.CONSTRUCTOR_BOTH_Q3_BONUS
        elif drivers_in_q3 == 1:
            score.one_driver_q3_bonus = self.rules.CONSTRUCTOR_ONE_Q3_BONUS
        
        if drivers_in_q2 == 2 and drivers_in_q3 == 0:
            # Only if both in Q2 but neither in Q3
            score.both_drivers_q2_bonus = self.rules.CONSTRUCTOR_BOTH_Q2_BONUS
        elif drivers_in_q2 == 1 and drivers_in_q3 == 0:
            # Only if one in Q2 but neither in Q3
            score.one_driver_q2_bonus = self.rules.CONSTRUCTOR_ONE_Q2_BONUS
        elif drivers_in_q2 == 0:
            # Neither driver reached Q2
            score.neither_driver_q2_penalty = self.rules.CONSTRUCTOR_NEITHER_Q2_PENALTY
        
        # Additional disqualification penalties
        disqualified_drivers = sum(
            1 for qd in qualifying_data 
            if qd.status == DriverStatus.DISQUALIFIED
        )
        if disqualified_drivers > 0:
            score.disqualification_penalty = get_constructor_disqualification_penalty(
                "qualifying", disqualified_drivers, self.rules
            )
        
        logger.debug(
            f"Qualifying score for {constructor_name}: {score.total_points} "
            f"(drivers: {score.driver_points_total}, bonuses: "
            f"Q2={score.both_drivers_q2_bonus + score.one_driver_q2_bonus}, "
            f"Q3={score.both_drivers_q3_bonus + score.one_driver_q3_bonus})"
        )
        
        return score
    
    def score_sprint_session(
        self,
        constructor_name: str,
        driver_scores: List[DriverSessionScore],
        sprint_data: List[SprintData]
    ) -> ConstructorSessionScore:
        """Calculate fantasy points for a constructor's sprint session.
        
        Args:
            constructor_name: Name of the constructor
            driver_scores: List of both driver session scores
            sprint_data: List of both drivers' sprint data
            
        Returns:
            ConstructorSessionScore with sprint points breakdown
        """
        score = ConstructorSessionScore(
            constructor_name=constructor_name,
            session_type=SessionType.SPRINT
        )
        
        # Sum driver points
        score.driver_points_total = sum(ds.total_points for ds in driver_scores)
        
        # Additional disqualification penalties
        disqualified_drivers = sum(
            1 for sd in sprint_data 
            if sd.status == DriverStatus.DISQUALIFIED
        )
        if disqualified_drivers > 0:
            score.disqualification_penalty = get_constructor_disqualification_penalty(
                "sprint", disqualified_drivers, self.rules
            )
        
        logger.debug(f"Sprint score for {constructor_name}: {score.total_points}")
        return score
    
    def score_race_session(
        self,
        constructor_name: str,
        driver_scores: List[DriverSessionScore],
        race_data: List[RaceData],
        fastest_pitstop_team: Optional[str] = None,
        world_record_pitstop_team: Optional[str] = None
    ) -> ConstructorSessionScore:
        """Calculate fantasy points for a constructor's race session.
        
        Args:
            constructor_name: Name of the constructor
            driver_scores: List of both driver session scores
            race_data: List of both drivers' race data
            fastest_pitstop_team: Team with fastest pitstop of the race
            world_record_pitstop_team: Team that set world record pitstop
            
        Returns:
            ConstructorSessionScore with race points breakdown
        """
        score = ConstructorSessionScore(
            constructor_name=constructor_name,
            session_type=SessionType.RACE
        )
        
        # Sum driver points (excluding DOTD bonus which is driver-only)
        score.driver_points_total = sum(
            ds.total_points - ds.driver_of_the_day_points 
            for ds in driver_scores
        )
        
        # Calculate pitstop points based on team's fastest pitstop
        fastest_team_pitstop = self._get_team_fastest_pitstop(race_data)
        if fastest_team_pitstop is not None:
            score.pit_stop_time_points = self.rules.get_pitstop_points(fastest_team_pitstop)
        
        # Fastest pitstop bonus
        if fastest_pitstop_team == constructor_name:
            score.fastest_pit_stop_bonus = self.rules.FASTEST_PITSTOP_BONUS
        
        # World record pitstop bonus  
        if world_record_pitstop_team == constructor_name:
            score.world_record_pit_stop_bonus = self.rules.WORLD_RECORD_PITSTOP_BONUS
        
        # Additional disqualification penalties
        disqualified_drivers = sum(
            1 for rd in race_data 
            if rd.status == DriverStatus.DISQUALIFIED
        )
        if disqualified_drivers > 0:
            score.disqualification_penalty = get_constructor_disqualification_penalty(
                "race", disqualified_drivers, self.rules
            )
        
        logger.debug(
            f"Race score for {constructor_name}: {score.total_points} "
            f"(drivers: {score.driver_points_total}, pitstop: {score.pit_stop_time_points})"
        )
        
        return score
    
    def calculate_constructor_weekend_score(
        self,
        constructor_name: str,
        qualifying_score: Optional[ConstructorSessionScore] = None,
        sprint_score: Optional[ConstructorSessionScore] = None,
        race_score: Optional[ConstructorSessionScore] = None
    ) -> ConstructorWeekendScore:
        """Calculate complete weekend fantasy score for a constructor.
        
        Args:
            constructor_name: Constructor name
            qualifying_score: Qualifying session score (optional)
            sprint_score: Sprint session score (optional)
            race_score: Race session score (optional)
            
        Returns:
            ConstructorWeekendScore with complete weekend breakdown
        """
        weekend_score = ConstructorWeekendScore(
            constructor_name=constructor_name,
            qualifying_score=qualifying_score,
            sprint_score=sprint_score,
            race_score=race_score
        )
        
        logger.info(
            f"Weekend score for {constructor_name}: {weekend_score.total_points} points"
        )
        
        return weekend_score
    
    def _get_team_fastest_pitstop(self, race_data: List[RaceData]) -> Optional[float]:
        """Get the fastest pitstop time for the team."""
        all_pitstops = []
        
        for driver_data in race_data:
            if driver_data.fastest_pit_stop_time is not None:
                all_pitstops.append(driver_data.fastest_pit_stop_time)
        
        return min(all_pitstops) if all_pitstops else None
    
    def get_fastest_pitstop_of_race(
        self, 
        all_race_data: Dict[str, List[RaceData]]
    ) -> Tuple[Optional[str], Optional[float]]:
        """Find the team with the fastest pitstop of the entire race.
        
        Args:
            all_race_data: Dictionary mapping team names to their drivers' race data
            
        Returns:
            Tuple of (team_name, fastest_time) or (None, None)
        """
        fastest_team = None
        fastest_time = None
        
        for team_name, team_race_data in all_race_data.items():
            team_fastest = self._get_team_fastest_pitstop(team_race_data)
            
            if team_fastest is not None:
                if fastest_time is None or team_fastest < fastest_time:
                    fastest_time = team_fastest
                    fastest_team = team_name
        
        return fastest_team, fastest_time
    
    def get_world_record_pitstop_team(
        self, 
        all_race_data: Dict[str, List[RaceData]]
    ) -> Optional[str]:
        """Find the team that set a world record pitstop time.
        
        Args:
            all_race_data: Dictionary mapping team names to their drivers' race data
            
        Returns:
            Team name that set world record, or None
        """
        fastest_team, fastest_time = self.get_fastest_pitstop_of_race(all_race_data)
        
        if fastest_time is not None and self.rules.is_world_record_pitstop(fastest_time):
            return fastest_team
        
        return None
    
    def get_scoring_explanation(
        self,
        weekend_score: ConstructorWeekendScore
    ) -> Dict[str, str]:
        """Generate human-readable explanation of scoring.
        
        Args:
            weekend_score: Constructor's weekend score
            
        Returns:
            Dictionary with scoring explanations
        """
        explanation = {
            "constructor": weekend_score.constructor_name,
            "total_points": str(weekend_score.total_points),
            "sessions": []
        }
        
        if weekend_score.qualifying_score:
            qual_score = weekend_score.qualifying_score
            qual_text = f"Qualifying: {qual_score.total_points} pts"
            
            components = []
            if qual_score.driver_points_total != 0:
                components.append(f"Drivers: {qual_score.driver_points_total}")
            if qual_score.both_drivers_q2_bonus > 0:
                components.append(f"Both Q2: +{qual_score.both_drivers_q2_bonus}")
            if qual_score.both_drivers_q3_bonus > 0:
                components.append(f"Both Q3: +{qual_score.both_drivers_q3_bonus}")
            if qual_score.one_driver_q2_bonus > 0:
                components.append(f"One Q2: +{qual_score.one_driver_q2_bonus}")
            if qual_score.one_driver_q3_bonus > 0:
                components.append(f"One Q3: +{qual_score.one_driver_q3_bonus}")
            if qual_score.neither_driver_q2_penalty < 0:
                components.append(f"No Q2: {qual_score.neither_driver_q2_penalty}")
            if qual_score.disqualification_penalty < 0:
                components.append(f"DSQ: {qual_score.disqualification_penalty}")
            
            if components:
                qual_text += f" ({', '.join(components)})"
            
            explanation["sessions"].append(qual_text)
        
        if weekend_score.sprint_score:
            sprint_score = weekend_score.sprint_score
            sprint_text = f"Sprint: {sprint_score.total_points} pts"
            
            components = []
            if sprint_score.driver_points_total != 0:
                components.append(f"Drivers: {sprint_score.driver_points_total}")
            if sprint_score.disqualification_penalty < 0:
                components.append(f"DSQ: {sprint_score.disqualification_penalty}")
            
            if components:
                sprint_text += f" ({', '.join(components)})"
            
            explanation["sessions"].append(sprint_text)
        
        if weekend_score.race_score:
            race_score = weekend_score.race_score
            race_text = f"Race: {race_score.total_points} pts"
            
            components = []
            if race_score.driver_points_total != 0:
                components.append(f"Drivers: {race_score.driver_points_total}")
            if race_score.pit_stop_time_points > 0:
                components.append(f"Pitstop: +{race_score.pit_stop_time_points}")
            if race_score.fastest_pit_stop_bonus > 0:
                components.append(f"Fastest pitstop: +{race_score.fastest_pit_stop_bonus}")
            if race_score.world_record_pit_stop_bonus > 0:
                components.append(f"World record: +{race_score.world_record_pit_stop_bonus}")
            if race_score.disqualification_penalty < 0:
                components.append(f"DSQ: {race_score.disqualification_penalty}")
            
            if components:
                race_text += f" ({', '.join(components)})"
            
            explanation["sessions"].append(race_text)
        
        return explanation