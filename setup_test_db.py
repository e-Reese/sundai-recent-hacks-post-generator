"""
Seed Azure SQL with hackathon project test data.
- Creates table [dbo].[HackathonProjects] if it doesn't exist
- Inserts N fake projects completed on 2025-08-25
Usage:
  python seed_hackathon_projects.py --rows 50 --hackathon "Global Hack 2025"
"""

import os
import argparse
from datetime import datetime
import random
import pyodbc
from faker import Faker

try:
    # Optional: load .env if present
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

COMPLETED_AT = datetime(2025, 8, 25)  # fixed completion date

def connect():
    """Create a secure connection to Azure SQL using ODBC Driver 18."""
    server = os.getenv("AZURE_SQL_SERVER")
    database = os.getenv("AZURE_SQL_DB")
    username = os.getenv("AZURE_SQL_USER")
    password = os.getenv("AZURE_SQL_PASSWORD")

    if not all([server, database, username, password]):
        raise RuntimeError(
            "Missing required environment variables: "
            "AZURE_SQL_SERVER, AZURE_SQL_DB, AZURE_SQL_USER, AZURE_SQL_PASSWORD"
        )

    conn_str = (
        "DRIVER={{ODBC Driver 18 for SQL Server}};"
        f"SERVER=tcp:{server},1433;"
        f"DATABASE={database};"
        f"UID={username};"
        f"PWD={password};"
        "Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
    )
    return pyodbc.connect(conn_str)

def ensure_table(cursor):
    cursor.execute(
        """
        IF NOT EXISTS (
            SELECT 1 FROM sys.tables t
            JOIN sys.schemas s ON t.schema_id = s.schema_id
            WHERE t.name = 'HackathonProjects' AND s.name = 'dbo'
        )
        BEGIN
            CREATE TABLE dbo.HackathonProjects (
                ProjectID      INT IDENTITY(1,1) PRIMARY KEY,
                ProjectName    NVARCHAR(200)    NOT NULL,
                TeamName       NVARCHAR(200)    NOT NULL,
                TeamMembers    NVARCHAR(500)    NULL,         -- comma-separated
                Description    NVARCHAR(2000)   NULL,
                TechStack      NVARCHAR(300)    NULL,         -- comma-separated
                RepoUrl        NVARCHAR(400)    NULL,
                DemoUrl        NVARCHAR(400)    NULL,
                Track          NVARCHAR(100)    NULL,         -- e.g., AI, Web, Health
                Prize          NVARCHAR(200)    NULL,         -- e.g., "1st Place", "Honorable Mention"
                JudgesScore    DECIMAL(5,2)     NULL,         -- 0-100
                HackathonName  NVARCHAR(200)    NOT NULL,
                CompletedAt    DATETIME2(0)     NOT NULL,
                CreatedAt      DATETIME2(0)     NOT NULL DEFAULT SYSUTCDATETIME()
            );
            CREATE INDEX IX_HackathonProjects_CompletedAt ON dbo.HackathonProjects(CompletedAt);
            CREATE INDEX IX_HackathonProjects_Hackathon   ON dbo.HackathonProjects(HackathonName);
        END
        """
    )

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
        "CompletedAt": COMPLETED_AT,
    }

def seed_projects(rows: int, hackathon_name: str):
    faker = Faker()
    conn = connect()
    try:
        with conn:
            cur = conn.cursor()
            ensure_table(cur)

            data = [random_project(faker, hackathon_name) for _ in range(rows)]

            cur.fast_executemany = True
            cur.executemany(
                """
                INSERT INTO dbo.HackathonProjects
                (ProjectName, TeamName, TeamMembers, Description, TechStack, RepoUrl, DemoUrl, Track, Prize,
                 JudgesScore, HackathonName, CompletedAt)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        d["ProjectName"], d["TeamName"], d["TeamMembers"], d["Description"], d["TechStack"],
                        d["RepoUrl"], d["DemoUrl"], d["Track"], d["Prize"], d["JudgesScore"],
                        d["HackathonName"], d["CompletedAt"]
                    )
                    for d in data
                ],
            )
            print(f"Inserted {rows} rows into dbo.HackathonProjects for '{hackathon_name}'.")
    finally:
        conn.close()

def parse_args():
    p = argparse.ArgumentParser(description="Seed Azure SQL with hackathon projects")
    p.add_argument("--rows", type=int, default=5, help="Number of projects to create (default: 5)")
    p.add_argument("--hackathon", type=str, default="Hackathon 2025",
                   help='Hackathon name to stamp into rows (default: "Hackathon 2025")')
    return p.parse_args()

if __name__ == "__main__":
    args = parse_args()
    seed_projects(rows=args.rows, hackathon_name=args.hackathon)