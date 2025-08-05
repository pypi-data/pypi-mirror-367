#!/usr/bin/env python3
"""
dbt-colibri CLI entry point
"""

import sys
from .cli import generate_report

if __name__ == "__main__":
    sys.exit(generate_report()) 