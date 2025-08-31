#!/usr/bin/env python3
"""
Test script to verify the Azure SQL connection using the updated DBConnector.
"""

import os
from dotenv import load_dotenv
from src.db_connector import DBConnector

def main():
    # Load environment variables
    load_dotenv()
    
    # Check if Azure SQL environment variables are set
    azure_vars = [
        "AZURE_SQL_SERVER",
        "AZURE_SQL_DB",
        "AZURE_SQL_USER",
        "AZURE_SQL_PASSWORD"
    ]
    
    missing_vars = [var for var in azure_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"Error: Missing required environment variables: {', '.join(missing_vars)}")
        print("Please create a .env file with the required variables or set them in your environment.")
        return 1
    
    print("Testing Azure SQL connection...")
    
    # Create a connector instance for Azure SQL
    db = DBConnector(db_type='azure_sql')
    
    # Try to connect
    if db.connect():
        print("Successfully connected to Azure SQL database!")
        
        # Try to list tables
        tables = db.list_tables()
        print(f"Tables in database: {tables}")
        
        # Check if HackathonProjects table exists
        if 'HackathonProjects' in tables:
            print("\nFetching sample data from HackathonProjects table...")
            query = "SELECT TOP 5 * FROM dbo.HackathonProjects"
            df = db.query_to_dataframe(query)
            
            if df is not None and not df.empty:
                print("\nSample data:")
                print(df)
            else:
                print("No data found in HackathonProjects table.")
        
        # Disconnect
        db.disconnect()
        return 0
    else:
        print("Failed to connect to Azure SQL database.")
        return 1

if __name__ == "__main__":
    exit(main())
