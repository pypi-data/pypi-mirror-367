"""
DNS BIND Zone and View File Parser

A utility to parse DNS BIND zone and view files and convert them to CSV format.
"""

__version__ = "0.1.2"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .parser import DNSZoneParser
from .main import app

__all__ = ["DNSZoneParser", "app"]