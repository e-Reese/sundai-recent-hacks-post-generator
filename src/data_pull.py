import sys
import os
import argparse
from dotenv import load_dotenv
import pandas as pd
from datetime import datetime, timedelta

# Add the parent directory to the path to import the module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import after adding to path
from db_connector import DBConnector
from utils import parse_date

load_dotenv()

def get_projects_by_date(date_str, verbose=True):
    """
    Fetch projects from the database that were created on a specific date.
    
    Args:
        date_str: Date string in YYYY-MM-DD format
        verbose: If True, print status messages
        
    Returns:
        DataFrame containing projects or None if error/not found
    """
    # Parse the date
    try:
        target_date = datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        if verbose:
            print(f"Error: Invalid date format '{date_str}'. Please use YYYY-MM-DD format.")
        return None
    
    # Calculate next day for query range
    next_day = target_date + timedelta(days=1)
    next_day_str = next_day.strftime("%Y-%m-%d")
    
    if verbose:
        print(f"Fetching projects created on {date_str}...")
    
    # Create a connector instance
    db = DBConnector(
        host=os.getenv("DB_HOST") or "34.148.221.200",
        database=os.getenv("DB_NAME") or "sundai_db",
        user=os.getenv("DB_USER") or "readonly",
        password=os.getenv("DB_PASS") or "readonly",
        port=5432
    )
    
    # Connect to the database
    if not db.connect():
        if verbose:
            print("Failed to connect to the database.")
        return None
    
    try:
        # Find the Project table
        tables = db.list_tables()
        if 'Project' not in tables:
            if verbose:
                print("Project table not found in the database.")
            return None
        
        # Query for projects created on the specified date
        query = f"""
        SELECT * 
        FROM "Project" 
        WHERE "createdAt" >= '{date_str} 00:00:00' 
        AND "createdAt" < '{next_day_str} 00:00:00'
        ORDER BY "createdAt"
        """
        
        projects_df = db.query_to_dataframe(query)
        
        if projects_df is None or projects_df.empty:
            if verbose:
                print(f"No projects found with creation date {date_str}.")
                
                # Get the date range of projects
                date_range_query = """
                SELECT 
                    MIN("createdAt") as earliest_date,
                    MAX("createdAt") as latest_date
                FROM "Project"
                """
                
                date_range = db.execute_query(date_range_query)
                
                if date_range:
                    earliest, latest = date_range[0]
                    print(f"Project creation dates range from {earliest} to {latest}")
                    
                    # Suggest some dates that have projects
                    sample_dates_query = """
                    SELECT DISTINCT DATE("createdAt") as creation_date, COUNT(*) as project_count
                    FROM "Project"
                    GROUP BY DATE("createdAt")
                    ORDER BY project_count DESC
                    LIMIT 5
                    """
                    
                    sample_dates = db.execute_query(sample_dates_query)
                    
                    if sample_dates:
                        print("\nDates with the most projects:")
                        for date, count in sample_dates:
                            print(f"  - {date}: {count} projects")
            
            return None
        
        if verbose:
            print(f"Found {len(projects_df)} projects created on {date_str}.")
        
        return projects_df
    
    finally:
        # Disconnect when done
        db.disconnect()
        if verbose:
            print("Disconnected from the database.")

def format_projects_for_prompt(projects_df, max_projects=20):
    """
    Format project data for the GPT prompt.
    
    Args:
        projects_df: DataFrame containing project data
        max_projects: Maximum number of projects to include
        
    Returns:
        String with formatted project data
    """
    if projects_df is None or projects_df.empty:
        return ""
    
    # Limit the number of projects to avoid token limits
    if len(projects_df) > max_projects:
        print(f"Limiting to {max_projects} projects for the prompt.")
        projects_df = projects_df.head(max_projects)
    
    formatted_projects = []
    
    for idx, project in projects_df.iterrows():
        project_info = []
        project_info.append(f"Project #{idx+1}: {project.get('title', 'Untitled Project')}")
        
        # Add preview/description
        if pd.notna(project.get('preview')):
            project_info.append(f"Preview: {project.get('preview')}")
        elif pd.notna(project.get('description')):
            project_info.append(f"Description: {project.get('description')}")
        
        # Add GitHub URL if available
        if pd.notna(project.get('githubUrl')):
            project_info.append(f"GitHub: {project.get('githubUrl')}")
        
        # Add Demo URL if available
        if pd.notna(project.get('demoUrl')):
            project_info.append(f"Demo: {project.get('demoUrl')}")
        
        formatted_projects.append("\n".join(project_info))
    
    return "\n\n".join(formatted_projects)

def save_projects_to_csv(projects_df, date_str=None, output_file=None):
    """
    Save projects DataFrame to a CSV file.
    
    Args:
        projects_df: DataFrame containing project data
        date_str: Date string in YYYY-MM-DD format (used for filename if output_file not provided)
        output_file: Custom output file path
        
    Returns:
        Path to the saved file or None if error
    """
    if projects_df is None or projects_df.empty:
        print("No projects to save.")
        return None
    
    # Determine output file path
    if output_file is None:
        if date_str:
            filename_date = date_str.replace("-", "_")
            output_file = f"../projects_{filename_date}.csv"
        else:
            output_file = f"../projects_{datetime.now().strftime('%Y_%m_%d')}.csv"
    
    try:
        projects_df.to_csv(output_file, index=False)
        print(f"Saved project data to {output_file}")
        return output_file
    except Exception as e:
        print(f"Error saving to CSV: {e}")
        return None

def main():
    """
    Command-line interface for fetching projects by date.
    """
    # Set up command-line argument parsing
    parser = argparse.ArgumentParser(description='Pull projects from the database for a specific date')
    parser.add_argument('--date', type=str, default=None, 
                        help='Date in YYYY-MM-DD format (default: today)')
    parser.add_argument('--output', type=str, default=None,
                        help='Output CSV file path (default: ../projects_YYYY_MM_DD.csv)')
    parser.add_argument('--quiet', action='store_true',
                        help='Suppress status messages')
    args = parser.parse_args()
    
    # Use provided date or default to today
    date_str = args.date or datetime.now().strftime("%Y-%m-%d")
    
    # Get projects for the specified date
    projects_df = get_projects_by_date(date_str, verbose=not args.quiet)
    
    if projects_df is not None and not projects_df.empty:
        # Save to CSV
        save_projects_to_csv(projects_df, date_str, args.output)
        
        if not args.quiet:
            # Display project summary
            print("\nProject Summary:")
            summary_df = projects_df[['id', 'title', 'createdAt', 'status']].copy()
            summary_df['createdAt'] = summary_df['createdAt'].dt.strftime('%Y-%m-%d %H:%M:%S')
            print(summary_df)
    else:
        if not args.quiet:
            print("No projects found or error occurred.")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())