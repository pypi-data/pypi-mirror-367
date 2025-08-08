"""Command-line interface for Fantasy Formula scoring."""

import json
import logging
import sys
from pathlib import Path
from typing import Optional

import click

from .. import FantasyScorer
from ..config import DEFAULT_SEASON, DEFAULT_FORMAT


def setup_logging(verbose: bool = False):
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


@click.command()
@click.option(
    '--year', '-y', 
    type=int, 
    default=DEFAULT_SEASON,
    help=f'F1 season year (default: {DEFAULT_SEASON})'
)
@click.option(
    '--round', '-r', 'round_num',
    type=int, 
    required=True,
    help='Race round number (1-24)'
)
@click.option(
    '--format', '-f', 'output_format',
    type=click.Choice(['json', 'table', 'summary'], case_sensitive=False),
    default=DEFAULT_FORMAT,
    help=f'Output format (default: {DEFAULT_FORMAT})'
)
@click.option(
    '--driver', '-d',
    type=str,
    help='Calculate score for specific driver only (e.g., VER, HAM)'
)
@click.option(
    '--constructor', '-c',
    type=str, 
    help='Calculate score for specific constructor only (e.g., "Red Bull", "Ferrari")'
)
@click.option(
    '--driver-of-the-day', '--dotd',
    type=str,
    help='Override Driver of the Day (driver abbreviation)'
)
@click.option(
    '--cache-dir',
    type=click.Path(exists=False, file_okay=False, dir_okay=True, path_type=Path),
    help='Custom cache directory for FastF1 data'
)
@click.option(
    '--no-cache',
    is_flag=True,
    help='Disable FastF1 caching'
)
@click.option(
    '--validate', 
    is_flag=True,
    help='Validate event data for consistency issues'
)
@click.option(
    '--session',
    type=click.Choice(['qualifying', 'sprint', 'race'], case_sensitive=False),
    help='Get summary for specific session only'
)
@click.option(
    '--verbose', '-v',
    is_flag=True,
    help='Enable verbose logging'
)
def main(
    year: int,
    round_num: int,
    output_format: str,
    driver: Optional[str] = None,
    constructor: Optional[str] = None,
    driver_of_the_day: Optional[str] = None,
    cache_dir: Optional[Path] = None,
    no_cache: bool = False,
    validate: bool = False,
    session: Optional[str] = None,
    verbose: bool = False
):
    """Fantasy Formula scoring calculator using real race data.
    
    Calculate fantasy points for drivers and constructors based on the 2025
    Fantasy Formula scoring rules and real race data from FastF1.
    
    Examples:
    
      # Calculate full event for Round 12 of 2025
      fantasy-calc --year 2025 --round 12
      
      # Get specific driver score
      fantasy-calc --year 2025 --round 12 --driver VER
      
      # Get constructor score with table format
      fantasy-calc --year 2025 --round 12 --constructor "Red Bull" --format table
      
      # Validate data quality
      fantasy-calc --year 2025 --round 12 --validate
    """
    setup_logging(verbose)
    
    try:
        # Initialize scorer
        scorer = FantasyScorer(
            season=year,
            round_num=round_num,
            cache_dir=cache_dir,
            enable_cache=not no_cache
        )
        
        # Handle validation mode
        if validate:
            click.echo(f"Validating data for {year} Round {round_num}...")
            validation_results = scorer.validate_event_data()
            output_results(validation_results, output_format)
            return
        
        # Handle session summary mode
        if session:
            click.echo(f"Getting {session} summary for {year} Round {round_num}...")
            session_summary = scorer.get_session_summary(session)
            output_results(session_summary, output_format)
            return
        
        # Handle specific driver mode
        if driver:
            click.echo(f"Calculating score for driver {driver} - {year} Round {round_num}...")
            driver_score = scorer.calculate_driver_score(
                driver.upper(), 
                driver_of_the_day=driver_of_the_day
            )
            
            if driver_score:
                result = {
                    'driver': driver.upper(),
                    'score': driver_score,
                    'breakdown': driver_score.get_session_breakdown()
                }
                output_results(result, output_format)
            else:
                click.echo(f"Driver {driver} not found in event data.", err=True)
                sys.exit(1)
            return
        
        # Handle specific constructor mode  
        if constructor:
            click.echo(f"Calculating score for constructor {constructor} - {year} Round {round_num}...")
            constructor_score = scorer.calculate_constructor_score(
                constructor,
                driver_of_the_day=driver_of_the_day
            )
            
            if constructor_score:
                result = {
                    'constructor': constructor,
                    'score': constructor_score,
                    'breakdown': constructor_score.get_session_breakdown()
                }
                output_results(result, output_format)
            else:
                click.echo(f"Constructor {constructor} not found in event data.", err=True)
                sys.exit(1)
            return
        
        # Calculate full event
        click.echo(f"Calculating full event - {year} Round {round_num}...")
        results = scorer.calculate_full_event(driver_of_the_day=driver_of_the_day)
        
        output_results(results, output_format)
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


def output_results(results: dict, format_type: str):
    """Output results in the specified format."""
    if format_type.lower() == 'json':
        output_json(results)
    elif format_type.lower() == 'table':
        output_table(results)
    elif format_type.lower() == 'summary':
        output_summary(results)
    else:
        output_json(results)  # Default fallback


def output_json(results: dict):
    """Output results as formatted JSON."""
    # Convert any non-serializable objects to strings
    serializable_results = convert_to_serializable(results)
    click.echo(json.dumps(serializable_results, indent=2, default=str))


def output_table(results: dict):
    """Output results in table format."""
    if 'drivers' in results and 'constructors' in results:
        # Full event results
        output_full_event_table(results)
    elif 'driver' in results:
        # Single driver results
        output_driver_table(results)
    elif 'constructor' in results:
        # Single constructor results  
        output_constructor_table(results)
    else:
        # Fallback to JSON
        output_json(results)


def output_summary(results: dict):
    """Output results as a summary."""
    if 'drivers' in results and 'constructors' in results:
        output_event_summary(results)
    else:
        output_json(results)


def output_full_event_table(results: dict):
    """Output full event results in table format."""
    event_info = results.get('event_info', {})
    
    click.echo(f"\n{'='*60}")
    click.echo(f"FANTASY FORMULA RESULTS - {event_info.get('event_name', 'Unknown Event')}")
    click.echo(f"Season: {event_info.get('season', 'Unknown')} | Round: {event_info.get('round', 'Unknown')}")
    click.echo(f"{'='*60}")
    
    # Driver standings
    drivers = results.get('drivers', {})
    if drivers:
        click.echo(f"\n{'DRIVER STANDINGS':<20}")
        click.echo(f"{'-'*60}")
        click.echo(f"{'Pos':<3} {'Driver':<8} {'Team':<15} {'Points':<8} {'Total':<8}")
        click.echo(f"{'-'*60}")
        
        # Sort drivers by points
        sorted_drivers = sorted(
            [(abbr, score) for abbr, score in drivers.items()],
            key=lambda x: x[1].total_points,
            reverse=True
        )
        
        for i, (driver_abbr, score) in enumerate(sorted_drivers[:20], 1):
            click.echo(f"{i:<3} {driver_abbr:<8} {score.team_name:<15} {score.total_points:<8} {score.total_points:<8}")
    
    # Constructor standings
    constructors = results.get('constructors', {})
    if constructors:
        click.echo(f"\n{'CONSTRUCTOR STANDINGS':<20}")
        click.echo(f"{'-'*60}")
        click.echo(f"{'Pos':<3} {'Constructor':<20} {'Points':<8}")
        click.echo(f"{'-'*60}")
        
        # Sort constructors by points
        sorted_constructors = sorted(
            [(name, score) for name, score in constructors.items()],
            key=lambda x: x[1].total_points,
            reverse=True
        )
        
        for i, (constructor_name, score) in enumerate(sorted_constructors, 1):
            click.echo(f"{i:<3} {constructor_name:<20} {score.total_points:<8}")
    
    click.echo(f"\n{'='*60}")


def output_driver_table(results: dict):
    """Output single driver results in table format."""
    driver_abbr = results.get('driver')
    score = results.get('score')
    breakdown = results.get('breakdown', {})
    
    if not score:
        click.echo("No driver score data available")
        return
    
    click.echo(f"\nDriver: {score.driver_name} ({driver_abbr})")
    click.echo(f"Team: {score.team_name}")
    click.echo(f"Total Points: {score.total_points}")
    click.echo(f"{'-'*40}")
    
    for session_name, session_breakdown in breakdown.items():
        if session_name == 'weekend_total':
            continue
        if isinstance(session_breakdown, dict) and 'total' in session_breakdown:
            click.echo(f"{session_name.title()}: {session_breakdown['total']} pts")
            for component, points in session_breakdown.items():
                if component != 'total' and points != 0:
                    click.echo(f"  {component}: {points}")


def output_constructor_table(results: dict):
    """Output single constructor results in table format."""
    constructor_name = results.get('constructor')
    score = results.get('score')
    breakdown = results.get('breakdown', {})
    
    if not score:
        click.echo("No constructor score data available")
        return
    
    click.echo(f"\nConstructor: {constructor_name}")
    click.echo(f"Total Points: {score.total_points}")
    click.echo(f"{'-'*40}")
    
    for session_name, session_breakdown in breakdown.items():
        if session_name == 'weekend_total':
            continue
        if isinstance(session_breakdown, dict) and 'total' in session_breakdown:
            click.echo(f"{session_name.title()}: {session_breakdown['total']} pts")
            for component, points in session_breakdown.items():
                if component != 'total' and points != 0:
                    click.echo(f"  {component}: {points}")


def output_event_summary(results: dict):
    """Output event summary."""
    event_info = results.get('event_info', {})
    drivers = results.get('drivers', {})
    constructors = results.get('constructors', {})
    
    click.echo(f"\nEvent: {event_info.get('event_name', 'Unknown Event')}")
    click.echo(f"Season {event_info.get('season')} - Round {event_info.get('round')}")
    
    if results.get('has_sprint'):
        click.echo("Format: Sprint Weekend")
    
    if results.get('driver_of_the_day'):
        click.echo(f"Driver of the Day: {results.get('driver_of_the_day')}")
    
    click.echo(f"\nDrivers: {len(drivers)}")
    if drivers:
        top_driver = max(drivers.items(), key=lambda x: x[1].total_points)
        click.echo(f"Top Scorer: {top_driver[1].driver_name} ({top_driver[0]}) - {top_driver[1].total_points} pts")
    
    click.echo(f"Constructors: {len(constructors)}")
    if constructors:
        top_constructor = max(constructors.items(), key=lambda x: x[1].total_points)
        click.echo(f"Top Constructor: {top_constructor[0]} - {top_constructor[1].total_points} pts")


def convert_to_serializable(obj):
    """Convert objects to JSON-serializable format."""
    if hasattr(obj, 'get_session_breakdown'):
        return {
            'total_points': obj.total_points,
            'breakdown': obj.get_session_breakdown()
        }
    elif hasattr(obj, '__dict__'):
        return {k: convert_to_serializable(v) for k, v in obj.__dict__.items()}
    elif isinstance(obj, dict):
        return {k: convert_to_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_serializable(item) for item in obj]
    else:
        return obj


if __name__ == '__main__':
    main()