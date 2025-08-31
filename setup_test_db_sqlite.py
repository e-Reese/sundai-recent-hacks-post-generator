"""
Seed SQLite with hackathon project test data.
- Creates table [HackathonProjects] if it doesn't exist
- Inserts N fake projects completed on 2025-08-25
Usage:
  python setup_test_db_sqlite.py --rows 50 --hackathon "Global Hack 2025"
"""

import os
import argparse
from datetime import datetime
import random
import sqlite3
from faker import Faker

try:
    # Optional: load .env if present
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

COMPLETED_AT = datetime(2025, 8, 25)  # fixed completion date
DB_FILE = "hackathon_projects.db"

def connect():
    """Create a connection to SQLite database."""
    conn = sqlite3.connect(DB_FILE)
    return conn

def ensure_table(cursor):
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS HackathonProjects (
            ProjectID      INTEGER PRIMARY KEY AUTOINCREMENT,
            ProjectName    TEXT    NOT NULL,
            TeamName       TEXT    NOT NULL,
            TeamMembers    TEXT    NULL,         -- comma-separated
            Description    TEXT    NULL,
            TechStack      TEXT    NULL,         -- comma-separated
            RepoUrl        TEXT    NULL,
            DemoUrl        TEXT    NULL,
            Track          TEXT    NULL,         -- e.g., AI, Web, Health
            Prize          TEXT    NULL,         -- e.g., "1st Place", "Honorable Mention"
            JudgesScore    REAL    NULL,         -- 0-100
            HackathonName  TEXT    NOT NULL,
            CompletedAt    TEXT    NOT NULL,
            CreatedAt      TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    
    # Create indexes
    cursor.execute("CREATE INDEX IF NOT EXISTS IX_HackathonProjects_CompletedAt ON HackathonProjects(CompletedAt)")
    cursor.execute("CREATE INDEX IF NOT EXISTS IX_HackathonProjects_Hackathon ON HackathonProjects(HackathonName)")

def random_project(faker: Faker, hackathon_name: str):
    adjectives = ["Quantum", "Swift", "Nebula", "Ripple", "Beacon", "Delta", "Nimbus", "Fusion", "Astra", "Pulse"]
    nouns = ["Vision", "Bridge", "Hub", "Forge", "Stream", "Pilot", "Sphere", "Link", "Lab", "Canvas"]
    tracks = ["AI/ML", "Web", "Mobile", "FinTech", "Health", "Climate", "Gov/Policy", "Education", "Data/Analytics"]
    tech_choices = [
        "Python", "Node.js", "TypeScript", "FastAPI", "Flask", "Django", "React", "Next.js", "Vue",
        "PostgreSQL", "SQL Server", "Cosmos DB", "Azure Functions", "Azure OpenAI", "Azure AI Search",
        "Docker", "Kubernetes", "Redis", "Kafka", "TensorFlow", "PyTorch"
    ]

    project_name = f"{random.choice(adjectives)} {random.choice(nouns)}"
    team_name = f"Team {faker.color_name()}"
    members = [faker.name() for _ in range(random.randint(2, 5))]
    description = faker.paragraph(nb_sentences=3)
    tech_stack = random.sample(tech_choices, k=random.randint(3, 6))
    repo_slug = f"{project_name.lower().replace(' ', '-')}"
    repo_url = f"https://github.com/{faker.user_name()}/{repo_slug}"
    demo_url = f"https://{repo_slug}.{faker.domain_name()}"
    track = random.choice(tracks)
    prize_bucket = [None, None, None, "Honorable Mention", "Category Winner", "3rd Place", "2nd Place", "1st Place"]
    prize = random.choice(prize_bucket)
    score = round(random.uniform(60, 98), 2)  # tilt toward good hackathon scores

    return {
        "ProjectName": project_name,
        "TeamName": team_name,
        "TeamMembers": ", ".join(members),
        "Description": description,
        "TechStack": ", ".join(tech_stack),
        "RepoUrl": repo_url,
        "DemoUrl": demo_url,
        "Track": track,
        "Prize": prize,
        "JudgesScore": score,
        "HackathonName": hackathon_name,
        "CompletedAt": COMPLETED_AT.isoformat(),
    }

def seed_projects(rows: int, hackathon_name: str):
    faker = Faker()
    conn = connect()
    try:
        cur = conn.cursor()
        ensure_table(cur)

        data = [random_project(faker, hackathon_name) for _ in range(rows)]

        for d in data:
            cur.execute(
                """
                INSERT INTO HackathonProjects
                (ProjectName, TeamName, TeamMembers, Description, TechStack, RepoUrl, DemoUrl, Track, Prize,
                 JudgesScore, HackathonName, CompletedAt)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    d["ProjectName"], d["TeamName"], d["TeamMembers"], d["Description"], d["TechStack"],
                    d["RepoUrl"], d["DemoUrl"], d["Track"], d["Prize"], d["JudgesScore"],
                    d["HackathonName"], d["CompletedAt"]
                ),
            )
        
        conn.commit()
        print(f"Inserted {rows} rows into HackathonProjects for '{hackathon_name}'.")
        print(f"Database created at: {os.path.abspath(DB_FILE)}")
    finally:
        conn.close()

def parse_args():
    p = argparse.ArgumentParser(description="Seed SQLite with hackathon projects")
    p.add_argument("--rows", type=int, default=5, help="Number of projects to create (default: 5)")
    p.add_argument("--hackathon", type=str, default="Hackathon 2025",
                   help='Hackathon name to stamp into rows (default: "Hackathon 2025")')
    return p.parse_args()

if __name__ == "__main__":
    args = parse_args()
    seed_projects(rows=args.rows, hackathon_name=args.hackathon)
