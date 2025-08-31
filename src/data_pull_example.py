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

def main():
    """
    Pull projects from the Project table that were created on a specific date.
    """
    # Set up command-line argument parsing
    parser = argparse.ArgumentParser(description='Generate a summary of projects created on a specific date')
    parser.add_argument('--date', type=parse_date, default=None, 
                        help='Date in YYYY-MM-DD format (default: today)')
    args = parser.parse_args()
    
    # Use provided date or default to today
    target_date = args.date or datetime.now()
    
    # Format date for display
    date_str = target_date.strftime("%Y-%m-%d")
    
    # Calculate next day for query range
    next_day = target_date + timedelta(days=1)
    next_day_str = next_day.strftime("%Y-%m-%d")
    
    print(f"Generating project summary for date: {date_str}")
    
    # Create a connector instance
    db = DBConnector(
        host=os.getenv("DB_HOST") or "34.148.221.200",
        database=os.getenv("DB_NAME") or "sundai_db",
        user=os.getenv("DB_USER") or "readonly",
        password=os.getenv("DB_PASS") or "readonly",
        port=5432
    )
    
    # Connect to the database
    if db.connect():
        print("Connected to the database successfully!")
        
        # Find the Project table
        tables = db.list_tables()
        if 'Project' in tables:
            print(f"\nFound Project table. Querying for projects created on {date_str}...")
            
            # Query for projects created on the specified date
            # Note: Using >= and < to get the full day in UTC
            query = f"""
            SELECT * 
            FROM "Project" 
            WHERE "createdAt" >= '{date_str} 00:00:00' 
            AND "createdAt" < '{next_day_str} 00:00:00'
            ORDER BY "createdAt"
            """
            
            projects_df = db.query_to_dataframe(query)
            
            if projects_df is not None and not projects_df.empty:
                print(f"\nFound {len(projects_df)} projects created on {date_str}:")
                
                # Display project information
                print("\nProject Summary:")
                summary_df = projects_df[['id', 'title', 'createdAt', 'status']].copy()
                
                # Format the datetime for better readability
                summary_df['createdAt'] = summary_df['createdAt'].dt.strftime('%Y-%m-%d %H:%M:%S')
                
                print(summary_df)
                
                # Save to CSV with date in filename
                filename_date = date_str.replace("-", "_")
                output_file = f"../projects_{filename_date}.csv"
                projects_df.to_csv(output_file, index=False)
                print(f"\nSaved detailed project data to {output_file}")
                
                # Display more detailed information for each project
                print("\nDetailed Project Information:")
                for idx, project in projects_df.iterrows():
                    print(f"\n{'='*50}")
                    print(f"Project #{idx+1}: {project.get('title', 'Untitled')}")
                    print(f"{'='*50}")
                    print(f"ID: {project.get('id')}")
                    print(f"Created: {project.get('createdAt').strftime('%Y-%m-%d %H:%M:%S')}")
                    print(f"Status: {project.get('status')}")
                    
                    # Display preview or description if available
                    if pd.notna(project.get('preview')):
                        print(f"Preview: {project.get('preview')}")
                    elif pd.notna(project.get('description')):
                        print(f"Description: {project.get('description')}")
                    
                    # Display URLs if available
                    if pd.notna(project.get('githubUrl')):
                        print(f"GitHub: {project.get('githubUrl')}")
                    
                    if pd.notna(project.get('demoUrl')):
                        print(f"Demo: {project.get('demoUrl')}")
                    
                    print(f"{'='*50}")
            else:
                print(f"No projects found with creation date {date_str}.")
                
                # Check if there are any projects in the table
                count_query = 'SELECT COUNT(*) FROM "Project"'
                count_result = db.execute_query(count_query)
                
                if count_result and count_result[0][0] > 0:
                    print(f"\nThere are {count_result[0][0]} total projects in the database.")
                    
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
        else:
            print("Project table not found in the database.")
            print("Available tables:")
            for table in tables:
                print(f"- {table}")
        
        # Disconnect when done
        db.disconnect()
        print("\nDisconnected from the database.")
    else:
        print("Failed to connect to the database.")


if __name__ == "__main__":
    main()