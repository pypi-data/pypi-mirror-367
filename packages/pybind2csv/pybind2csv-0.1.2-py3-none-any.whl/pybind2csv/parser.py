"""
DNS BIND Zone and View File Parser

This module provides functionality to parse DNS BIND zone files and view files,
then convert them to CSV format with the specified columns.
"""

import csv
import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from loguru import logger
from tqdm import tqdm
import dns.zone
import dns.node
import dns.rdatatype
import dns.rdata


class DNSZoneParser:
    """Parser for DNS BIND zone and view files."""
    
    def __init__(self):
        """Initialize the DNS zone parser."""
        self.records: List[Dict[str, Any]] = []
    
    def parse_zone_file(self, zone_file: Path, zone_name: str, view_name: str) -> List[Dict[str, Any]]:
        """
        Parse a DNS BIND zone file and extract records.
        
        Args:
            zone_file: Path to the zone file
            zone_name: Name of the zone
            view_name: Name of the view
            
        Returns:
            List of DNS record dictionaries
        """
        logger.info(f"Parsing zone file: {zone_file} for zone: {zone_name}, view: {view_name}")
        
        try:
            # Read the zone file
            with open(zone_file, 'r', encoding='utf-8') as f:
                zone_content = f.read()
            
            # Add $ORIGIN if not present
            if not zone_content.strip().startswith('$ORIGIN'):
                zone_content = f"$ORIGIN {zone_name}.\n{zone_content}"
            
            # Parse the zone using dnspython
            try:
                zone = dns.zone.from_text(
                    zone_content, 
                    origin=zone_name, 
                    check_origin=False,
                    relativize=False
                )
            except dns.exception.SyntaxError as e:
                logger.warning(f"Syntax error in zone file {zone_file}: {e}")
                logger.info("Attempting to parse with fallback method...")
                # Try to parse by ignoring unknown record types
                return self._parse_zone_with_fallback(zone_content, zone_name, view_name)
            
            records = []
            
            # Iterate through all nodes in the zone
            for name, node in zone.nodes.items():
                name_str = str(name)
                if name_str == '@':
                    name_str = zone_name
                elif not name_str.endswith('.'):
                    if zone_name.endswith('.'):
                        name_str = f"{name_str}.{zone_name.rstrip('.')}"
                    else:
                        name_str = f"{name_str}.{zone_name}"
                
                # Get all resource record sets for this node
                for rdataset in node.rdatasets:
                    try:
                        rrtype = dns.rdatatype.to_text(rdataset.rdtype)
                    except ValueError:
                        # Handle unknown record types
                        rrtype = str(rdataset.rdtype)
                    
                    ttl = rdataset.ttl
                    
                    # Process each individual record
                    for rdata in rdataset:
                        record = {
                            'zone': zone_name,
                            'view': view_name,
                            'name': name_str,
                            'type': rrtype,
                            'ttl': ttl,
                            'data': str(rdata)
                        }
                        records.append(record)
            
            logger.info(f"Parsed {len(records)} records from {zone_file}")
            return records
            
        except Exception as e:
            logger.error(f"Error parsing zone file {zone_file}: {e}")
            # Return empty list instead of raising for better error handling
            return []
    
    def _parse_zone_with_fallback(self, zone_content: str, zone_name: str, view_name: str) -> list:
        """Parse zone content with fallback method for unknown record types.
        
        Args:
            zone_content: Content of the zone file as string
            zone_name: Name of the DNS zone
            view_name: Name of the DNS view
            
        Returns:
            List of DNS record dictionaries
        """
        records = []
        
        # Add $ORIGIN if not present
        if not zone_content.strip().startswith('$ORIGIN'):
            zone_content = f"$ORIGIN {zone_name}.\n{zone_content}"
        
        # Parse each line manually
        origin = zone_name
        for line_num, line in enumerate(zone_content.split('\n'), 1):
            line = line.strip()
            if not line or line.startswith(';') or line.startswith('$'):
                continue
            
            try:
                # Parse record format: name [ttl] [class] type data
                parts = line.split()
                if len(parts) >= 3:
                    # Handle relative names
                    name = parts[0]
                    if name == '@':
                        name = origin
                    elif not name.endswith('.'):
                        name = f"{name}.{origin}"
                    else:
                        name = name.rstrip('.')
                    
                    # Find TTL, class, type, and data
                    i = 1
                    ttl = 300  # default TTL
                    record_class = 'IN'
                    
                    # Check for TTL
                    if i < len(parts) and parts[i].isdigit():
                        ttl = int(parts[i])
                        i += 1
                    
                    # Check for class
                    if i < len(parts) and parts[i] in ['IN', 'CH', 'HS']:
                        record_class = parts[i]
                        i += 1
                    
                    # Type should be next
                    if i < len(parts):
                        record_type = parts[i]
                        i += 1
                        
                        # Remaining parts are data
                        data = ' '.join(parts[i:])
                        
                        record = {
                            'zone': zone_name,
                            'view': view_name,
                            'name': name,
                            'type': record_type,
                            'ttl': ttl,
                            'data': data
                        }
                        records.append(record)
            except Exception as e:
                logger.warning(f"Skipping malformed line {line_num}: {line}")
                continue
        
        return records
    
    def parse_view_file(self, view_file: Path, view_name: str) -> List[Dict[str, Any]]:
        """
        Parse a DNS BIND view file (which is essentially a zone file).
        
        Args:
            view_file: Path to the view file
            view_name: Name of the view
            
        Returns:
            List of DNS record dictionaries
        """
        logger.info(f"Parsing view file: {view_file} for view: {view_name}")
        
        # Extract zone name from filename if possible
        zone_name = extract_zone_name_from_file(view_file)
        
        return self.parse_zone_file(view_file, zone_name, view_name)
    
    def parse_files(self, zone_file: Path, view_file: Path, zone_name: str, view_name: str) -> List[Dict[str, Any]]:
        """
        Parse both zone and view files.
        
        Args:
            zone_file: Path to the zone file
            view_file: Path to the view file
            zone_name: Name of the zone
            view_name: Name of the view
            
        Returns:
            Combined list of DNS record dictionaries
        """
        logger.info(f"Parsing zone file: {zone_file} and view file: {view_file}")
        
        # Parse both files
        zone_records = self.parse_zone_file(zone_file, zone_name, view_name)
        view_records = self.parse_view_file(view_file, view_name)
        
        # Combine records and remove duplicates
        all_records = zone_records + view_records
        
        # Remove exact duplicates
        seen = set()
        unique_records = []
        for record in all_records:
            key = (record['zone'], record['view'], record['name'], record['type'], record['ttl'], record['data'])
            if key not in seen:
                seen.add(key)
                unique_records.append(record)
        
        logger.info(f"Total unique records parsed: {len(unique_records)}")
        return unique_records
    
    def write_csv(self, records: List[Dict[str, Any]], output_file: Path) -> None:
        """
        Write DNS records to CSV file.
        
        Args:
            records: List of DNS record dictionaries
            output_file: Path to the output CSV file
        """
        logger.info(f"Writing {len(records)} records to CSV: {output_file}")
        
        fieldnames = ['zone', 'view', 'name', 'type', 'ttl', 'data']
        
        try:
            with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                # Use tqdm for progress bar
                for record in tqdm(records, desc="Writing CSV records"):
                    writer.writerow(record)
            
            logger.success(f"Successfully wrote {len(records)} records to {output_file}")
        except Exception as e:
            logger.error(f"Error writing CSV file {output_file}: {e}")
            raise


def validate_zone_file(file_path: Path) -> bool:
    """Validate if the file exists and is readable."""
    if not file_path.exists():
        logger.error(f"Zone file does not exist: {file_path}")
        return False
    
    if not file_path.is_file():
        logger.error(f"Path is not a file: {file_path}")
        return False
    
    return True


def extract_zone_name_from_file(file_path: Path) -> str:
    """Extract zone name from filename.
    
    Args:
        file_path: Path to the zone file
        
    Returns:
        Zone name extracted from filename
    """
    stem = file_path.stem
    
    # Handle view-specific suffixes first
    if stem.endswith('.vlocal'):
        stem = stem[:-7]
    elif stem.endswith('.vroaming'):
        stem = stem[:-8]
    elif stem.endswith('.vinternal'):
        stem = stem[:-9]
    elif stem.endswith('.vexternal'):
        stem = stem[:-9]
    elif stem.endswith('.int'):
        stem = stem[:-4]
    elif stem.endswith('.ext'):
        stem = stem[:-4]
    
    return stem


def extract_view_name_from_file(file_path: Path) -> str:
    """Extract view name from filename.
    
    Args:
        file_path: Path to the view file
        
    Returns:
        View name extracted from filename
    """
    name = file_path.name.lower()
    stem = file_path.stem.lower()
    
    # Map file extensions to view names
    view_mapping = {
        '.vlocal': 'local',
        '.vroaming': 'roaming',
        '.vinternal': 'internal',
        '.vexternal': 'external',
        '.int': 'internal',
        '.ext': 'external'
    }
    
    # Check file extension
    for suffix, view_name in view_mapping.items():
        if name.endswith(suffix):
            return view_name
    
    # Default to stem if no view suffix found
    return file_path.stem