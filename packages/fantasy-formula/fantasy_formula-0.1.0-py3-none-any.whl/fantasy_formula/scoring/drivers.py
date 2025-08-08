"""Driver fantasy scoring logic."""

import logging
from typing import Dict, Optional

from ..models import (
    SessionType, DriverStatus, QualifyingData, SprintData, RaceData,
    DriverSessionScore, DriverWeekendScore
)
from .rules_2025 import ScoringRules2025, calculate_position_change_points, get_penalty_points

logger = logging.getLogger(__name__)


class DriverScorer:
    """Calculates fantasy points for drivers across all sessions."""
    
    def __init__(self, scoring_rules: Optional[ScoringRules2025] = None):
        """Initialize with scoring rules.
        
        Args:
            scoring_rules: Scoring rules to use (defaults to 2025 rules)
        """
        self.rules = scoring_rules or ScoringRules2025()
    
    def score_qualifying_session(
        self,
        qualifying_data: QualifyingData
    ) -> DriverSessionScore:
        """Calculate fantasy points for a driver's qualifying session.
        
        Args:
            qualifying_data: Driver's qualifying session data
            
        Returns:
            DriverSessionScore with qualifying points breakdown
        """
        score = DriverSessionScore(
            driver_abbreviation=qualifying_data.driver_abbreviation,
            session_type=SessionType.QUALIFYING
        )
        
        # Finishing position points
        if qualifying_data.finishing_position:
            score.finishing_position_points = self.rules.get_qualifying_points(
                qualifying_data.finishing_position
            )
        
        # Pole position is already included in finishing position points
        if qualifying_data.finishing_position == 1:
            score.pole_position_points = 0  # Already counted in finishing_position_points
        
        # Apply penalties based on status
        if qualifying_data.status == DriverStatus.NOT_CLASSIFIED:
            score.not_classified_penalty = self.rules.QUALIFYING_NC_PENALTY
        elif qualifying_data.status == DriverStatus.DISQUALIFIED:
            score.disqualification_penalty = self.rules.QUALIFYING_DSQ_PENALTY
        
        logger.debug(f"Qualifying score for {qualifying_data.driver_abbreviation}: {score.total_points}")
        return score
    
    def score_sprint_session(
        self,
        sprint_data: SprintData
    ) -> DriverSessionScore:
        """Calculate fantasy points for a driver's sprint session.
        
        Args:
            sprint_data: Driver's sprint session data
            
        Returns:
            DriverSessionScore with sprint points breakdown
        """
        score = DriverSessionScore(
            driver_abbreviation=sprint_data.driver_abbreviation,
            session_type=SessionType.SPRINT
        )
        
        # Only calculate points for classified drivers
        if sprint_data.status == DriverStatus.CLASSIFIED:
            # Finishing position points
            if sprint_data.finishing_position:
                score.finishing_position_points = self.rules.get_sprint_position_points(
                    sprint_data.finishing_position
                )
            
            # Position change points
            gained_points, lost_points = calculate_position_change_points(
                sprint_data.starting_position,
                sprint_data.finishing_position,
                self.rules
            )
            score.positions_gained_points = gained_points
            score.positions_lost_points = lost_points
            
            # Overtakes points
            score.overtakes_points = sprint_data.overtakes_made * self.rules.OVERTAKE_POINTS
            
            # Fastest lap bonus
            if sprint_data.is_fastest_lap:
                score.fastest_lap_points = self.rules.SPRINT_FASTEST_LAP_POINTS
        
        # Apply penalties based on status
        if sprint_data.status == DriverStatus.NOT_CLASSIFIED:
            score.not_classified_penalty = self.rules.SPRINT_DNF_PENALTY
        elif sprint_data.status == DriverStatus.DISQUALIFIED:
            score.disqualification_penalty = self.rules.SPRINT_DSQ_PENALTY
        
        logger.debug(f"Sprint score for {sprint_data.driver_abbreviation}: {score.total_points}")
        return score
    
    def score_race_session(
        self,
        race_data: RaceData
    ) -> DriverSessionScore:
        """Calculate fantasy points for a driver's race session.
        
        Args:
            race_data: Driver's race session data
            
        Returns:
            DriverSessionScore with race points breakdown
        """
        score = DriverSessionScore(
            driver_abbreviation=race_data.driver_abbreviation,
            session_type=SessionType.RACE
        )
        
        # Only calculate points for classified drivers
        if race_data.status == DriverStatus.CLASSIFIED:
            # Finishing position points
            if race_data.finishing_position:
                score.finishing_position_points = self.rules.get_race_position_points(
                    race_data.finishing_position
                )
            
            # Position change points
            gained_points, lost_points = calculate_position_change_points(
                race_data.starting_position,
                race_data.finishing_position,
                self.rules
            )
            score.positions_gained_points = gained_points
            score.positions_lost_points = lost_points
            
            # Overtakes points
            score.overtakes_points = race_data.overtakes_made * self.rules.OVERTAKE_POINTS
            
            # Fastest lap bonus
            if race_data.is_fastest_lap:
                score.fastest_lap_points = self.rules.RACE_FASTEST_LAP_POINTS
            
            # Driver of the Day bonus
            if race_data.is_driver_of_the_day:
                score.driver_of_the_day_points = self.rules.DRIVER_OF_THE_DAY_POINTS
        
        # Apply penalties based on status
        if race_data.status == DriverStatus.NOT_CLASSIFIED:
            score.not_classified_penalty = self.rules.RACE_DNF_PENALTY
        elif race_data.status == DriverStatus.DISQUALIFIED:
            score.disqualification_penalty = self.rules.RACE_DSQ_PENALTY
        
        logger.debug(f"Race score for {race_data.driver_abbreviation}: {score.total_points}")
        return score
    
    def calculate_driver_weekend_score(
        self,
        driver_abbr: str,
        driver_name: str,
        team_name: str,
        qualifying_data: Optional[QualifyingData] = None,
        sprint_data: Optional[SprintData] = None,
        race_data: Optional[RaceData] = None,
        transfer_penalty: int = 0
    ) -> DriverWeekendScore:
        """Calculate complete weekend fantasy score for a driver.
        
        Args:
            driver_abbr: Driver abbreviation
            driver_name: Driver full name
            team_name: Team/constructor name
            qualifying_data: Qualifying session data (optional)
            sprint_data: Sprint session data (optional)
            race_data: Race session data (optional)
            transfer_penalty: Transfer penalty points (negative)
            
        Returns:
            DriverWeekendScore with complete weekend breakdown
        """
        weekend_score = DriverWeekendScore(
            driver_abbreviation=driver_abbr,
            driver_name=driver_name,
            team_name=team_name,
            transfer_penalty=transfer_penalty
        )
        
        # Calculate session scores
        if qualifying_data:
            weekend_score.qualifying_score = self.score_qualifying_session(qualifying_data)
        
        if sprint_data:
            weekend_score.sprint_score = self.score_sprint_session(sprint_data)
        
        if race_data:
            weekend_score.race_score = self.score_race_session(race_data)
        
        logger.info(
            f"Weekend score for {driver_name} ({driver_abbr}): {weekend_score.total_points} points"
        )
        
        return weekend_score
    
    def get_scoring_explanation(
        self,
        weekend_score: DriverWeekendScore
    ) -> Dict[str, str]:
        """Generate human-readable explanation of scoring.
        
        Args:
            weekend_score: Driver's weekend score
            
        Returns:
            Dictionary with scoring explanations
        """
        explanation = {
            "driver": f"{weekend_score.driver_name} ({weekend_score.driver_abbreviation})",
            "team": weekend_score.team_name,
            "total_points": str(weekend_score.total_points),
            "sessions": []
        }
        
        if weekend_score.qualifying_score:
            qual_score = weekend_score.qualifying_score
            qual_text = f"Qualifying: {qual_score.total_points} pts"
            
            components = []
            if qual_score.finishing_position_points > 0:
                components.append(f"Position: +{qual_score.finishing_position_points}")
            if qual_score.not_classified_penalty < 0:
                components.append(f"NC penalty: {qual_score.not_classified_penalty}")
            if qual_score.disqualification_penalty < 0:
                components.append(f"DSQ penalty: {qual_score.disqualification_penalty}")
            
            if components:
                qual_text += f" ({', '.join(components)})"
            
            explanation["sessions"].append(qual_text)
        
        if weekend_score.sprint_score:
            sprint_score = weekend_score.sprint_score
            sprint_text = f"Sprint: {sprint_score.total_points} pts"
            
            components = []
            if sprint_score.finishing_position_points > 0:
                components.append(f"Position: +{sprint_score.finishing_position_points}")
            if sprint_score.positions_gained_points > 0:
                components.append(f"Gained: +{sprint_score.positions_gained_points}")
            if sprint_score.positions_lost_points < 0:
                components.append(f"Lost: {sprint_score.positions_lost_points}")
            if sprint_score.overtakes_points > 0:
                components.append(f"Overtakes: +{sprint_score.overtakes_points}")
            if sprint_score.fastest_lap_points > 0:
                components.append(f"Fastest lap: +{sprint_score.fastest_lap_points}")
            if sprint_score.not_classified_penalty < 0:
                components.append(f"DNF: {sprint_score.not_classified_penalty}")
            if sprint_score.disqualification_penalty < 0:
                components.append(f"DSQ: {sprint_score.disqualification_penalty}")
            
            if components:
                sprint_text += f" ({', '.join(components)})"
            
            explanation["sessions"].append(sprint_text)
        
        if weekend_score.race_score:
            race_score = weekend_score.race_score
            race_text = f"Race: {race_score.total_points} pts"
            
            components = []
            if race_score.finishing_position_points > 0:
                components.append(f"Position: +{race_score.finishing_position_points}")
            if race_score.positions_gained_points > 0:
                components.append(f"Gained: +{race_score.positions_gained_points}")
            if race_score.positions_lost_points < 0:
                components.append(f"Lost: {race_score.positions_lost_points}")
            if race_score.overtakes_points > 0:
                components.append(f"Overtakes: +{race_score.overtakes_points}")
            if race_score.fastest_lap_points > 0:
                components.append(f"Fastest lap: +{race_score.fastest_lap_points}")
            if race_score.driver_of_the_day_points > 0:
                components.append(f"DOTD: +{race_score.driver_of_the_day_points}")
            if race_score.not_classified_penalty < 0:
                components.append(f"DNF: {race_score.not_classified_penalty}")
            if race_score.disqualification_penalty < 0:
                components.append(f"DSQ: {race_score.disqualification_penalty}")
            
            if components:
                race_text += f" ({', '.join(components)})"
            
            explanation["sessions"].append(race_text)
        
        if weekend_score.transfer_penalty < 0:
            explanation["transfer_penalty"] = f"Transfer penalty: {weekend_score.transfer_penalty}"
        
        return explanation