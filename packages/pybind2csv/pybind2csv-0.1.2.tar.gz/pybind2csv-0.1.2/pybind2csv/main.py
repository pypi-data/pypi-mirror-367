"""
Main CLI application for DNS BIND zone and view file parser.
"""

from pathlib import Path
from typing import Optional
import typer
from loguru import logger
from .parser import DNSZoneParser, validate_zone_file, extract_zone_name_from_file, extract_view_name_from_file

app = typer.Typer(help="DNS BIND Zone and View File Parser")

# Configure logger
logger.remove()
logger.add(
    lambda msg: typer.echo(msg, err=True),
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>",
    level="INFO"
)


@app.command()
def parse_zone(
    zone_file: Path = typer.Argument(..., help="Path to the DNS BIND zone file"),
    view_file: Path = typer.Argument(..., help="Path to the DNS BIND view file"),
    output: Optional[Path] = typer.Option(None, help="Output CSV file path"),
    zone_name: Optional[str] = typer.Option(None, help="Zone name (auto-detected if not provided)"),
    view_name: Optional[str] = typer.Option(None, help="View name (auto-detected if not provided)"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose logging")
):
    """
    Parse DNS BIND zone and view files and convert to CSV.
    
    Examples:
        pybind2csv parse-zone example.zone example.vroaming
        pybind2csv parse-zone example.zone example.vroaming --output dns_records.csv
        pybind2csv parse-zone example.zone example.vroaming --zone-name example.com --view-name roaming
    """
    if verbose:
        logger.remove()
        logger.add(
            lambda msg: typer.echo(msg, err=True),
            format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>",
            level="DEBUG"
        )
    
    # Validate input files
    if not validate_zone_file(zone_file):
        typer.echo(f"Error: Zone file validation failed: {zone_file}", err=True)
        raise typer.Exit(1)
    
    if not validate_zone_file(view_file):
        typer.echo(f"Error: View file validation failed: {view_file}", err=True)
        raise typer.Exit(1)
    
    # Auto-detect zone and view names if not provided
    if zone_name is None:
        zone_name = extract_zone_name_from_file(zone_file)
        logger.info(f"Auto-detected zone name: {zone_name}")
    
    if view_name is None:
        view_name = extract_view_name_from_file(view_file)
        logger.info(f"Auto-detected view name: {view_name}")
    
    # Set default output filename
    if output is None:
        output = Path(f"{zone_name}_{view_name}_dns_records.csv")
        logger.info(f"Using default output filename: {output}")
    
    try:
        # Initialize parser
        parser = DNSZoneParser()
        
        # Parse files
        records = parser.parse_files(zone_file, view_file, zone_name, view_name)
        
        # Write to CSV
        parser.write_csv(records, output)
        
        typer.echo(f"✅ Successfully parsed {len(records)} DNS records")
        typer.echo(f"📄 Output saved to: {output}")
        
    except Exception as e:
        typer.echo(f"❌ Error: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def parse_single(
    file: Path = typer.Argument(..., help="Path to a single DNS BIND file"),
    output: Optional[Path] = typer.Option(None, help="Output CSV file path"),
    zone_name: Optional[str] = typer.Option(None, help="Zone name (auto-detected if not provided)"),
    view_name: Optional[str] = typer.Option("default", help="View name"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose logging")
):
    """
    Parse a single DNS BIND file and convert to CSV.
    
    Examples:
        pybind2csv parse-single example.zone
        pybind2csv parse-single example.vroaming --zone-name example.com
    """
    if verbose:
        logger.remove()
        logger.add(
            lambda msg: typer.echo(msg, err=True),
            format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>",
            level="DEBUG"
        )
    
    # Validate input file
    if not validate_zone_file(file):
        typer.echo(f"Error: File validation failed: {file}", err=True)
        raise typer.Exit(1)
    
    # Auto-detect zone name if not provided
    if zone_name is None:
        zone_name = extract_zone_name_from_file(file)
        logger.info(f"Auto-detected zone name: {zone_name}")
    
    # Set default output filename
    if output is None:
        output = Path(f"{zone_name}_{view_name}_dns_records.csv")
        logger.info(f"Using default output filename: {output}")
    
    try:
        # Initialize parser
        parser = DNSZoneParser()
        
        # Parse file
        records = parser.parse_zone_file(file, zone_name, view_name)
        
        # Write to CSV
        parser.write_csv(records, output)
        
        typer.echo(f"✅ Successfully parsed {len(records)} DNS records")
        typer.echo(f"📄 Output saved to: {output}")
        
    except Exception as e:
        typer.echo(f"❌ Error: {e}", err=True)
        raise typer.Exit(1)


@app.callback()
def main():
    """DNS BIND Zone and View File Parser - Convert DNS records to CSV format."""
    pass


if __name__ == "__main__":
    app()