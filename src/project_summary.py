import os
import sys
import json
import textwrap
import argparse
from dotenv import load_dotenv
import pandas as pd
from datetime import datetime

from openai import OpenAI

# Add the parent directory to the path to import the module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import after adding to path
from utils import parse_date
from data_pull import get_projects_by_date, format_projects_for_prompt, save_projects_to_csv

load_dotenv()

def generate_linkedin_post(client, projects_df, date_str, max_projects=20, mock=False):
    """
    Generate a LinkedIn post summarizing the projects using GPT.
    
    Args:
        client: OpenAI client (or None if mock=True)
        projects_df: DataFrame containing project data
        date_str: Date string in YYYY-MM-DD format
        max_projects: Maximum number of projects to include
        mock: If True, generate a mock post without using the OpenAI API
        
    Returns:
        Generated LinkedIn post as a string
    """
    # Format the projects for the prompt
    formatted_projects = format_projects_for_prompt(projects_df, max_projects)
    
    # Create the prompt
    prompt = f"""
    You are a community manager for a tech community called Sundai. 
    
    Please write an engaging LinkedIn post about the following projects that were created on {date_str}. 
    The post should be professional, enthusiastic, and highlight the innovative aspects of these projects.
    
    Here are the projects:
    
    {formatted_projects}
    
    Requirements for the LinkedIn post:
    1. Keep it concise (under 1300 characters)
    2. Include hashtags like #AI #TechCommunity #Sundai #Innovation
    3. Mention the date ({date_str}) when these projects were created
    4. Highlight the most interesting aspects of the projects
    5. Encourage readers to check out the projects
    6. Format it properly for LinkedIn with appropriate spacing and paragraph breaks
    7. Do not include all the GitHub links - just mention they can be found through Sundai
    8. The tone should be professional but enthusiastic
    """
    
    # If mock mode is enabled, return a mock post
    if mock:
        print("Generating mock LinkedIn post (no API call)...")
        project_count = len(projects_df)
        project_titles = ", ".join([f'"{p.get("title", "Untitled")}"' for _, p in projects_df.head(3).iterrows()])
        if project_count > 3:
            project_titles += f", and {project_count - 3} more"
        
        mock_post = f"""🚀 Exciting projects from our Sundai community on {date_str}! 

Today, our talented members created {project_count} innovative projects including {project_titles}.

These projects showcase the creativity and technical skills of our community members, ranging from AI tools to productivity enhancers.

Check out these amazing projects through Sundai and see how our community continues to push the boundaries of technology!

#Sundai #TechCommunity #Innovation #AI #BuildInPublic"""
        
        return mock_post
    
    print("Generating LinkedIn post with GPT...")
    
    try:
        # Call the OpenAI API
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": "You are a professional community manager who writes engaging LinkedIn posts."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        
        # Extract the generated post
        linkedin_post = response.choices[0].message.content.strip()
        return linkedin_post
    
    except Exception as e:
        print(f"Error generating LinkedIn post with GPT: {e}")
        print("Falling back to mock post generation...")
        # Fall back to mock generation if API call fails
        return generate_linkedin_post(None, projects_df, date_str, max_projects, mock=True)

def main():
    """
    Main function to generate a LinkedIn post summarizing projects from a specific date.
    """
    # Set up argument parsing
    parser = argparse.ArgumentParser(description='Generate a LinkedIn post summarizing projects from a specific date')
    parser.add_argument('--date', type=str, default=None, 
                        help='Date in YYYY-MM-DD format (default: today)')
    parser.add_argument('--max-projects', type=int, default=20,
                        help='Maximum number of projects to include in the summary (default: 20)')
    parser.add_argument('--output', type=str, default=None,
                        help='Output file path for the LinkedIn post (default: linkedin_post_YYYY_MM_DD.txt)')
    parser.add_argument('--mock', action='store_true',
                        help='Generate a mock LinkedIn post without using the OpenAI API')
    args = parser.parse_args()
    
    # Use provided date or default to today
    date_str = args.date or datetime.now().strftime("%Y-%m-%d")
    
    try:
        # Validate date format
        datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        raise SystemExit(f"Error: Invalid date format '{date_str}'. Please use YYYY-MM-DD format.")
    
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
    
    # Fetch projects from the database using data_pull.py
    projects_df = get_projects_by_date(date_str)
    
    if projects_df is None or projects_df.empty:
        print("No projects found to summarize.")
        return
    
    # Generate LinkedIn post
    linkedin_post = generate_linkedin_post(client, projects_df, date_str, args.max_projects, mock=args.mock)
    
    # Display the generated post
    print("\n" + "=" * 80)
    print("GENERATED LINKEDIN POST:")
    print("=" * 80)
    print(linkedin_post)
    print("=" * 80)
    
    # Save the post to a file
    filename_date = date_str.replace("-", "_")
    output_file = args.output or f"../linkedin_post_{filename_date}.txt"
    
    with open(output_file, 'w') as f:
        f.write(linkedin_post)
    
    print(f"\nLinkedIn post saved to {output_file}")
    
    # Also save project data to CSV for reference using data_pull.py
    save_projects_to_csv(projects_df, date_str)


if __name__ == "__main__":
    main()