"""Basic usage examples for Fantasy Formula."""

from fantasy_formula import FantasyScorer


def basic_scoring_example():
    """Basic example of calculating fantasy points."""
    print("Fantasy Formula Basic Usage Example")
    print("=" * 40)
    
    # Initialize scorer for a specific race
    scorer = FantasyScorer(season=2024, round_num=1)  # 2024 Bahrain GP
    
    try:
        # Calculate full event scores
        print("Calculating full event scores...")
        results = scorer.calculate_full_event()
        
        # Display top 5 drivers
        print("\nTop 5 Drivers:")
        drivers = results['drivers']
        top_drivers = sorted(
            [(abbr, score) for abbr, score in drivers.items()],
            key=lambda x: x[1].total_points,
            reverse=True
        )[:5]
        
        for i, (driver_abbr, score) in enumerate(top_drivers, 1):
            print(f"{i}. {score.driver_name} ({driver_abbr}): {score.total_points} points")
        
        # Display top 3 constructors
        print("\nTop 3 Constructors:")
        constructors = results['constructors']
        top_constructors = sorted(
            [(name, score) for name, score in constructors.items()],
            key=lambda x: x[1].total_points,
            reverse=True
        )[:3]
        
        for i, (constructor_name, score) in enumerate(top_constructors, 1):
            print(f"{i}. {constructor_name}: {score.total_points} points")
        
        # Show event information
        event_info = results.get('event_info', {})
        print(f"\nEvent: {event_info.get('event_name', 'Unknown')}")
        print(f"Sprint Weekend: {'Yes' if results.get('has_sprint') else 'No'}")
        
        if results.get('driver_of_the_day'):
            print(f"Driver of the Day: {results['driver_of_the_day']}")
    
    except Exception as e:
        print(f"Error calculating scores: {e}")
        print("Note: This example requires valid F1 data to be available.")


def specific_driver_example():
    """Example of calculating points for a specific driver."""
    print("\nSpecific Driver Example")
    print("=" * 40)
    
    scorer = FantasyScorer(season=2024, round_num=1)
    
    try:
        # Calculate score for a specific driver
        driver_score = scorer.calculate_driver_score('VER')  # Max Verstappen
        
        if driver_score:
            print(f"Driver: {driver_score.driver_name}")
            print(f"Team: {driver_score.team_name}")
            print(f"Total Points: {driver_score.total_points}")
            
            # Show session breakdown
            breakdown = driver_score.get_session_breakdown()
            print("\nSession Breakdown:")
            for session, points in breakdown.items():
                if session != 'weekend_total':
                    if isinstance(points, dict):
                        print(f"  {session.title()}: {points.get('total', 0)} points")
                    else:
                        print(f"  {session.title()}: {points}")
        else:
            print("Driver VER not found in the event data.")
    
    except Exception as e:
        print(f"Error: {e}")


def validation_example():
    """Example of validating event data."""
    print("\nData Validation Example")
    print("=" * 40)
    
    scorer = FantasyScorer(season=2024, round_num=1)
    
    try:
        validation_results = scorer.validate_event_data()
        
        print("Validation Results:")
        for session, results in validation_results.items():
            if session != 'overall':
                print(f"\n{session.title()}:")
                print(f"  Status: {results.get('status', 'unknown')}")
                
                if 'driver_count' in results:
                    print(f"  Drivers: {results['driver_count']}")
                
                issues = results.get('issues', {})
                if issues:
                    print("  Issues found:")
                    for issue_type, issue_list in issues.items():
                        if issue_list:
                            print(f"    {issue_type}: {len(issue_list)}")
                else:
                    print("  No issues found")
    
    except Exception as e:
        print(f"Error during validation: {e}")


if __name__ == "__main__":
    # Run examples
    basic_scoring_example()
    specific_driver_example()
    validation_example()
    
    print("\n" + "=" * 40)
    print("Examples completed!")
    print("Note: Examples use 2024 data which may not be fully available.")
    print("For testing purposes, try using completed race weekends.")