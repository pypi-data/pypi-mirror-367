"""Test scoring rules and calculations."""

import unittest
from fantasy_formula.scoring.rules_2025 import ScoringRules2025, calculate_position_change_points


class TestScoringRules2025(unittest.TestCase):
    """Test the 2025 scoring rules implementation."""
    
    def setUp(self):
        self.rules = ScoringRules2025()
    
    def test_qualifying_points(self):
        """Test qualifying position points."""
        self.assertEqual(self.rules.get_qualifying_points(1), 10)  # Pole
        self.assertEqual(self.rules.get_qualifying_points(2), 9)
        self.assertEqual(self.rules.get_qualifying_points(10), 1)
        self.assertEqual(self.rules.get_qualifying_points(11), 0)  # No points
        self.assertEqual(self.rules.get_qualifying_points(20), 0)
    
    def test_race_position_points(self):
        """Test race finishing position points."""
        self.assertEqual(self.rules.get_race_position_points(1), 25)  # Win
        self.assertEqual(self.rules.get_race_position_points(2), 18)
        self.assertEqual(self.rules.get_race_position_points(3), 15)
        self.assertEqual(self.rules.get_race_position_points(10), 1)
        self.assertEqual(self.rules.get_race_position_points(11), 0)
    
    def test_sprint_position_points(self):
        """Test sprint finishing position points."""
        self.assertEqual(self.rules.get_sprint_position_points(1), 8)
        self.assertEqual(self.rules.get_sprint_position_points(8), 1)
        self.assertEqual(self.rules.get_sprint_position_points(9), 0)
    
    def test_pitstop_points(self):
        """Test pitstop time points."""
        self.assertEqual(self.rules.get_pitstop_points(1.9), 20)   # Under 2.0s
        self.assertEqual(self.rules.get_pitstop_points(2.1), 10)   # 2.00-2.19s
        self.assertEqual(self.rules.get_pitstop_points(2.3), 5)    # 2.20-2.49s
        self.assertEqual(self.rules.get_pitstop_points(2.7), 2)    # 2.50-2.99s
        self.assertEqual(self.rules.get_pitstop_points(3.5), 0)    # Over 3.0s
    
    def test_world_record_pitstop(self):
        """Test world record pitstop detection."""
        self.assertTrue(self.rules.is_world_record_pitstop(1.7))   # Under 1.8s
        self.assertFalse(self.rules.is_world_record_pitstop(1.9))  # Over 1.8s
    
    def test_position_change_points(self):
        """Test position change calculations."""
        # Positions gained
        gained, lost = calculate_position_change_points(10, 5, self.rules)
        self.assertEqual(gained, 5)
        self.assertEqual(lost, 0)
        
        # Positions lost
        gained, lost = calculate_position_change_points(5, 10, self.rules)
        self.assertEqual(gained, 0)
        self.assertEqual(lost, -5)
        
        # No change
        gained, lost = calculate_position_change_points(5, 5, self.rules)
        self.assertEqual(gained, 0)
        self.assertEqual(lost, 0)
        
        # Handle None values
        gained, lost = calculate_position_change_points(None, 5, self.rules)
        self.assertEqual(gained, 0)
        self.assertEqual(lost, 0)


if __name__ == '__main__':
    unittest.main()