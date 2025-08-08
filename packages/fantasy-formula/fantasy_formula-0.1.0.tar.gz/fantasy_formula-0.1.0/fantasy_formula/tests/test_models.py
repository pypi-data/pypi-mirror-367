"""Test data models."""

import unittest
from fantasy_formula.models import (
    DriverSessionScore, ConstructorSessionScore, DriverWeekendScore,
    SessionType, DriverStatus, QualifyingData, RaceData
)


class TestDriverSessionScore(unittest.TestCase):
    """Test driver session scoring model."""
    
    def test_total_points_calculation(self):
        """Test total points calculation."""
        score = DriverSessionScore(
            driver_abbreviation="VER",
            session_type=SessionType.RACE
        )
        
        score.finishing_position_points = 25
        score.positions_gained_points = 3
        score.overtakes_points = 2
        score.fastest_lap_points = 10
        score.driver_of_the_day_points = 10
        
        expected_total = 25 + 3 + 2 + 10 + 10
        self.assertEqual(score.total_points, expected_total)
    
    def test_penalty_points(self):
        """Test penalty points are properly subtracted."""
        score = DriverSessionScore(
            driver_abbreviation="VER",
            session_type=SessionType.RACE
        )
        
        score.finishing_position_points = 25
        score.not_classified_penalty = -20
        
        self.assertEqual(score.total_points, 5)  # 25 - 20


class TestConstructorSessionScore(unittest.TestCase):
    """Test constructor session scoring model."""
    
    def test_qualifying_bonuses(self):
        """Test qualifying progression bonuses."""
        score = ConstructorSessionScore(
            constructor_name="Red Bull",
            session_type=SessionType.QUALIFYING
        )
        
        score.driver_points_total = 15  # Both drivers combined
        score.both_drivers_q3_bonus = 10
        
        self.assertEqual(score.total_points, 25)


class TestDriverWeekendScore(unittest.TestCase):
    """Test complete weekend scoring."""
    
    def test_weekend_total(self):
        """Test weekend total calculation."""
        weekend_score = DriverWeekendScore(
            driver_abbreviation="VER",
            driver_name="Max Verstappen",
            team_name="Red Bull"
        )
        
        # Add qualifying score
        qual_score = DriverSessionScore("VER", SessionType.QUALIFYING)
        qual_score.finishing_position_points = 10
        weekend_score.qualifying_score = qual_score
        
        # Add race score
        race_score = DriverSessionScore("VER", SessionType.RACE)
        race_score.finishing_position_points = 25
        race_score.fastest_lap_points = 10
        weekend_score.race_score = race_score
        
        self.assertEqual(weekend_score.total_points, 45)  # 10 + 25 + 10
    
    def test_transfer_penalty(self):
        """Test transfer penalty application."""
        weekend_score = DriverWeekendScore(
            driver_abbreviation="VER",
            driver_name="Max Verstappen", 
            team_name="Red Bull",
            transfer_penalty=-10
        )
        
        race_score = DriverSessionScore("VER", SessionType.RACE)
        race_score.finishing_position_points = 25
        weekend_score.race_score = race_score
        
        self.assertEqual(weekend_score.total_points, 15)  # 25 - 10


class TestDataModels(unittest.TestCase):
    """Test basic data models."""
    
    def test_qualifying_data_creation(self):
        """Test qualifying data model."""
        qual_data = QualifyingData(
            session_type=SessionType.QUALIFYING,
            driver_abbreviation="VER",
            driver_name="Max Verstappen",
            team_name="Red Bull",
            finishing_position=1,
            q3_time=82.123,
            reached_q2=True,
            reached_q3=True
        )
        
        self.assertEqual(qual_data.session_type, SessionType.QUALIFYING)
        self.assertEqual(qual_data.driver_abbreviation, "VER")
        self.assertTrue(qual_data.reached_q3)
    
    def test_race_data_creation(self):
        """Test race data model."""
        race_data = RaceData(
            session_type=SessionType.RACE,
            driver_abbreviation="VER",
            driver_name="Max Verstappen",
            team_name="Red Bull",
            starting_position=1,
            finishing_position=1,
            positions_gained=0,
            positions_lost=0,
            overtakes_made=3,
            is_fastest_lap=True,
            is_driver_of_the_day=True
        )
        
        self.assertEqual(race_data.session_type, SessionType.RACE)
        self.assertEqual(race_data.overtakes_made, 3)
        self.assertTrue(race_data.is_fastest_lap)
        self.assertTrue(race_data.is_driver_of_the_day)


if __name__ == '__main__':
    unittest.main()