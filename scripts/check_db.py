#!/usr/bin/env python
"""Verify database connectivity."""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import check_connection

if __name__ == "__main__":
    ok = check_connection()
    sys.exit(0 if ok else 1)
