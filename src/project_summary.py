import os
import sys
import json
import textwrap
import argparse
from dotenv import load_dotenv
import pandas as pd
from datetime import datetime, timedelta

from openai import OpenAI

# Add the parent directory to the path to import the module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import after adding to path
from db_connector import DBConnector
from utils import parse_date

load_dotenv()

def main():
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    if not OPENAI_API_KEY:
        raise SystemExit("Set OPENAI_API_KEY first.")

    client = OpenAI(api_key=OPENAI_API_KEY)

    if len(sys.argv) < 2:
        raise SystemExit("Usage: python script.py YYYY-MM-DD [max_projects]")
    release_date_str = sys.argv[1]
    try:
        release_date = datetime.strptime(release_date_str, "%Y-%m-%d").date()
    except ValueError:
        raise SystemExit("release date must be YYYY-MM-DD")

    MAX_PROJECTS = int(sys.argv[2]) if len(sys.argv) > 2 else 20  # cap prompt size



if __name__ == "__main__":
    main()
