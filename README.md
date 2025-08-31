# Sundai Recent Hacks Post Generator

A tool for automatically generating and posting LinkedIn updates about recent projects in the Sundai community.

## Features

- Pulls project data from the Sundai database for a specific date
- Generates engaging LinkedIn posts using OpenAI's GPT
- Posts updates directly to LinkedIn via the LinkedIn API
- Saves project data and generated posts for reference

## Setup

1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Create a `.env` file with the following variables:
   ```
   # PostgreSQL Database credentials
   DB_HOST=your_db_host
   DB_NAME=your_db_name
   DB_USER=your_db_user
   DB_PASS=your_db_password
   DB_PORT=5432
   
   # OpenAI API
   OPENAI_API_KEY=your_openai_api_key
   OPENAI_MODEL=gpt-4o-mini  # or your preferred model
   
   # LinkedIn API
   CLIENT_ID=your_linkedin_client_id
   CLIENT_SECRET=your_linkedin_client_secret
   REDIRECT_URI=your_redirect_uri
   AUTH_CODE=your_auth_code
   ACCESS_TOKEN=your_access_token
   PERSON_URN=your_person_urn
   ```

## Usage

Run the main script to pull data, generate a post, and publish to LinkedIn:

```
python main.py
```

### Command-line Options

- `--date YYYY-MM-DD`: Specify a date (defaults to today)
- `--max-projects N`: Maximum number of projects to include (default: 20)
- `--mock`: Generate a mock post without using OpenAI API
- `--dry-run`: Generate the post but don't publish to LinkedIn
- `--use-sqlite`: Use SQLite database instead of PostgreSQL
- `--sqlite-path PATH`: Path to SQLite database file (default: hackathon_projects.db)

### Examples

Generate a post for today's projects:
```
python main.py
```

Generate a post for a specific date:
```
python main.py --date 2023-05-15
```

Generate a post but don't publish it:
```
python main.py --dry-run
```

## Database Configuration

This tool supports both PostgreSQL and SQLite as database backends.

### PostgreSQL (Default)

Provide the following environment variables in your `.env` file:
```
DB_HOST=your_db_host
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASS=your_db_password
DB_PORT=5432
```

### SQLite (Local Development)

For local development or Next.js deployment, you can use SQLite instead of PostgreSQL.

To use SQLite, run the application with the `--use-sqlite` flag:
```
python main.py --use-sqlite
```

You can specify the path to the SQLite database file with the `--sqlite-path` flag:
```
python main.py --use-sqlite --sqlite-path=path/to/database.db
```

Alternatively, you can set the following environment variables in your `.env` file:
```
USE_SQLITE=true
SQLITE_PATH=path/to/database.db
```

### Creating a SQLite Test Database

You can create a test SQLite database with sample data using the provided script:
```
python setup_test_db_sqlite.py --rows 10 --hackathon "Your Hackathon Name"
```

This will create a `hackathon_projects.db` file with sample project data.

## Components

- `main.py`: Orchestrates the entire workflow
- `src/data_pull.py`: Pulls project data from the database
- `src/project_summary.py`: Generates LinkedIn posts using OpenAI
- `src/post_to_linkedin.py`: Posts content to LinkedIn
- `src/get_linkedin_token.py`: Helper for obtaining LinkedIn API tokens
- `src/db_connector.py`: Database connection utilities
- `src/utils.py`: Shared utility functions

## Output Files

- `projects_YYYY_MM_DD.csv`: CSV file with project data
- `linkedin_post_YYYY_MM_DD.txt`: Generated LinkedIn post content