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
   # PostgreSQL Database credentials (default)
   DB_HOST=your_db_host
   DB_NAME=your_db_name
   DB_USER=your_db_user
   DB_PASS=your_db_password
   DB_PORT=5432
   
   # OR Azure SQL Database credentials (will be used if all are present)
   AZURE_SQL_SERVER=your-server-name.database.windows.net
   AZURE_SQL_DB=your-database-name
   AZURE_SQL_USER=your-username
   AZURE_SQL_PASSWORD=your-password
   
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

This tool supports two database backends:

### PostgreSQL (Default)

Provide the following environment variables in your `.env` file:
```
DB_HOST=your_db_host
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASS=your_db_password
DB_PORT=5432
```

### Azure SQL Database

To use Azure SQL instead of PostgreSQL, provide these environment variables:
```
AZURE_SQL_SERVER=your-server-name.database.windows.net
AZURE_SQL_DB=your-database-name
AZURE_SQL_USER=your-username
AZURE_SQL_PASSWORD=your-password
```

The application will automatically use Azure SQL if all Azure SQL environment variables are present.

**Note:** Using Azure SQL requires the ODBC Driver 18 for SQL Server to be installed on your system. 
Installation instructions:
- Windows: [Microsoft Docs](https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server)
- macOS: `brew install microsoft/mssql-release/msodbcsql18`
- Linux: [Microsoft Docs](https://docs.microsoft.com/en-us/sql/connect/odbc/linux-mac/installing-the-microsoft-odbc-driver-for-sql-server)

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