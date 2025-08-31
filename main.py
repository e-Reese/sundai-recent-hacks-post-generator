#!/usr/bin/env python3
import os
import sys
import argparse
from datetime import datetime
import requests
from dotenv import load_dotenv
from openai import OpenAI

# Import our modules
from src.data_pull import get_projects_by_date, save_projects_to_csv
from src.project_summary import generate_linkedin_post
import src.post_to_linkedin as linkedin_poster

def main():
    """
    Main function to orchestrate the workflow:
    1. Pull project data from database
    2. Generate a LinkedIn post using the project data
    3. Post the content to LinkedIn
    """
    # Load environment variables
    load_dotenv()
    
    # Set up argument parsing
    parser = argparse.ArgumentParser(description='Generate and post a LinkedIn update about recent Sundai projects')
    parser.add_argument('--date', type=str, default=None, 
                        help='Date in YYYY-MM-DD format (default: today)')
    parser.add_argument('--max-projects', type=int, default=20,
                        help='Maximum number of projects to include in the summary (default: 20)')
    parser.add_argument('--mock', action='store_true',
                        help='Generate a mock LinkedIn post without using the OpenAI API')
    parser.add_argument('--dry-run', action='store_true',
                        help='Generate the post but do not publish to LinkedIn')
    parser.add_argument('--use-sqlite', action='store_true',
                        help='Use SQLite database instead of PostgreSQL')
    parser.add_argument('--sqlite-path', type=str, default='hackathon_projects.db',
                        help='Path to SQLite database file (default: hackathon_projects.db)')
    args = parser.parse_args()
    
    # Set environment variables based on command line arguments
    if args.use_sqlite:
        os.environ["USE_SQLITE"] = "true"
        os.environ["SQLITE_PATH"] = args.sqlite_path
    
    # Use provided date or default to today
    date_str = args.date or datetime.now().strftime("%Y-%m-%d")
    
    try:
        # Validate date format
        datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        print(f"Error: Invalid date format '{date_str}'. Please use YYYY-MM-DD format.")
        return 1
    
    print(f"Starting workflow for projects created on {date_str}...")
    
    # Step 1: Pull project data from database
    print("\n=== STEP 1: Pulling project data ===")
    projects_df = get_projects_by_date(date_str)
    
    if projects_df is None or projects_df.empty:
        print("No projects found for the specified date. Exiting.")
        return 1
    
    print(f"Found {len(projects_df)} projects for {date_str}")
    
    # Save project data to CSV for reference
    csv_path = save_projects_to_csv(projects_df, date_str)
    if csv_path:
        print(f"Project data saved to {csv_path}")
    
    # Step 2: Generate LinkedIn post
    print("\n=== STEP 2: Generating LinkedIn post ===")
    
    # Initialize OpenAI client if not in mock mode
    client = None
    if not args.mock:
        # Check for OpenAI API key
        OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        if not OPENAI_API_KEY:
            print("Warning: OPENAI_API_KEY environment variable not set.")
            print("Falling back to mock mode. To use the OpenAI API, set the OPENAI_API_KEY environment variable.")
            args.mock = True
        else:
            # Initialize OpenAI client
            client = OpenAI(api_key=OPENAI_API_KEY)
    
    # Generate the LinkedIn post
    linkedin_post = generate_linkedin_post(client, projects_df, date_str, args.max_projects, mock=args.mock)
    
    # Display the generated post
    print("\n" + "=" * 80)
    print("GENERATED LINKEDIN POST:")
    print("=" * 80)
    print(linkedin_post)
    print("=" * 80)
    
    # Save the post to a file
    filename_date = date_str.replace("-", "_")
    output_file = f"linkedin_post_{filename_date}.txt"
    
    with open(output_file, 'w') as f:
        f.write(linkedin_post)
    
    print(f"\nLinkedIn post saved to {output_file}")
    
    # Step 3: Post to LinkedIn
    if not args.dry_run:
        print("\n=== STEP 3: Posting to LinkedIn ===")
        
        # Check for required environment variables
        access_token = os.getenv('ACCESS_TOKEN')
        person_urn = os.getenv('PERSON_URN')
        
        if not access_token or not person_urn:
            print("Error: LinkedIn ACCESS_TOKEN or PERSON_URN not set in environment variables.")
            print("Cannot post to LinkedIn. Use --dry-run to skip posting.")
            return 1
        
        # Prepare post data
        post_data = {
            "author": person_urn,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": linkedin_post
                    },
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }
        
        # Post to LinkedIn
        url = "https://api.linkedin.com/v2/ugcPosts"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0"
        }
        
        try:
            response = requests.post(url, headers=headers, json=post_data)
            print(f"LinkedIn API Status: {response.status_code}")
            
            if response.status_code == 201:
                print("Success! Post published to LinkedIn.")
                print(f"Response: {response.text}")
                return 0
            else:
                print(f"Failed to post to LinkedIn. Status code: {response.status_code}")
                print(f"Response: {response.text}")
                return 1
                
        except Exception as e:
            print(f"Error posting to LinkedIn: {e}")
            return 1
    else:
        print("\nDry run mode: Skipping LinkedIn posting")
        return 0

if __name__ == "__main__":
    sys.exit(main())
