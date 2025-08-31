import os
import pandas as pd
from typing import List, Dict, Any, Optional, Tuple, Union, Literal
from dotenv import load_dotenv
from sqlalchemy import create_engine, text, inspect, URL
from sqlalchemy.engine import Engine, Connection
from sqlalchemy.exc import SQLAlchemyError

# Load environment variables from .env file
load_dotenv()

class DBConnector:
    """
    A class for connecting to and interacting with databases (PostgreSQL or Azure SQL) using SQLAlchemy.
    """
    
    def __init__(self, 
                 host: Optional[str] = None,
                 database: Optional[str] = None, 
                 user: Optional[str] = None,
                 password: Optional[str] = None,
                 port: Optional[int] = None,
                 connection_string: Optional[str] = None,
                 db_type: Literal['postgresql', 'azure_sql'] = 'postgresql'):
        """
        Initialize the SQLAlchemy connector with connection parameters.
        If parameters are not provided, they will be loaded from environment variables.
        
        Args:
            host: Database host address
            database: Database name
            user: Database user
            password: Database password
            port: Database port
            connection_string: Direct connection string (overrides other parameters if provided)
            db_type: Type of database to connect to ('postgresql' or 'azure_sql')
        """
        self.db_type = db_type
        
        # Use appropriate environment variables based on database type
        if self.db_type == 'postgresql':
            self.host = host or os.environ.get("DB_HOST")
            self.database = database or os.environ.get("DB_NAME")
            self.user = user or os.environ.get("DB_USER")
            self.password = password or os.environ.get("DB_PASSWORD")
            self.port = port or os.environ.get("DB_PORT", 5432)
        elif self.db_type == 'azure_sql':
            self.host = host or os.environ.get("AZURE_SQL_SERVER")
            self.database = database or os.environ.get("AZURE_SQL_DB")
            self.user = user or os.environ.get("AZURE_SQL_USER")
            self.password = password or os.environ.get("AZURE_SQL_PASSWORD")
            self.port = port or 1433  # Default port for SQL Server
        
        self.connection_string = connection_string
        
        self.engine = None
        self.connection = None
        self.inspector = None
    
    def connect(self) -> bool:
        """
        Establish a connection to the database (PostgreSQL or Azure SQL).
        
        Returns:
            bool: True if connection is successful, False otherwise
        """
        try:
            if self.connection_string:
                conn_str = self.connection_string
            elif self.db_type == 'postgresql':
                conn_str = f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"
            elif self.db_type == 'azure_sql':
                # Format for Azure SQL using ODBC driver
                conn_str = (
                    f"mssql+pyodbc://{self.user}:{self.password}@{self.host}:1433/{self.database}"
                    "?driver=ODBC+Driver+18+for+SQL+Server"
                    "&encrypt=yes&trustservercertificate=no&connection_timeout=30"
                )
            else:
                raise ValueError(f"Unsupported database type: {self.db_type}")
            
            self.engine = create_engine(conn_str)
            self.connection = self.engine.connect()
            self.inspector = inspect(self.engine)
            return True
        except SQLAlchemyError as e:
            print(f"Error connecting to {self.db_type} database: {e}")
            return False
    
    def disconnect(self) -> None:
        """
        Close the database connection.
        """
        if self.connection:
            self.connection.close()
        if self.engine:
            self.engine.dispose()
        self.connection = None
        self.engine = None
        self.inspector = None
    
    def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> List[Tuple]:
        """
        Execute a SQL query with optional parameters.
        
        Args:
            query: SQL query string
            params: Dictionary of parameters for the query
            
        Returns:
            List of tuples containing the query results or empty list if no results/error
        """
        try:
            if not self.connection:
                if not self.connect():
                    return []
            
            result = self.connection.execute(text(query), params or {})
            
            if result.returns_rows:
                return result.fetchall()
            else:
                self.connection.commit()
                return []
        except SQLAlchemyError as e:
            print(f"Error executing query: {e}")
            if self.connection:
                self.connection.rollback()
            return []
    
    def query_to_dataframe(self, query: str, params: Optional[Dict[str, Any]] = None) -> Optional[pd.DataFrame]:
        """
        Execute a query and return the results as a pandas DataFrame.
        
        Args:
            query: SQL query string
            params: Dictionary of parameters for the query
            
        Returns:
            DataFrame containing the query results or None if error
        """
        try:
            if not self.connection:
                if not self.connect():
                    return None
            
            return pd.read_sql_query(text(query), self.connection, params=params or {})
        except SQLAlchemyError as e:
            print(f"Error executing query to dataframe: {e}")
            return None
    
    def insert_data(self, table: str, data: Dict[str, Any]) -> bool:
        """
        Insert a single row of data into a table.
        
        Args:
            table: Table name
            data: Dictionary with column names as keys and values to insert
            
        Returns:
            bool: True if insertion was successful, False otherwise
        """
        try:
            if not self.connection:
                if not self.connect():
                    return False
            
            columns = ", ".join(data.keys())
            placeholders = ", ".join(f":{key}" for key in data.keys())
            
            query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
            
            self.connection.execute(text(query), data)
            self.connection.commit()
            return True
        except SQLAlchemyError as e:
            print(f"Error inserting data: {e}")
            if self.connection:
                self.connection.rollback()
            return False
    
    def bulk_insert(self, table: str, data_list: List[Dict[str, Any]]) -> bool:
        """
        Insert multiple rows of data into a table.
        
        Args:
            table: Table name
            data_list: List of dictionaries with column names as keys and values to insert
            
        Returns:
            bool: True if bulk insertion was successful, False otherwise
        """
        if not data_list:
            return True
        
        try:
            if not self.connection:
                if not self.connect():
                    return False
            
            # Ensure all dictionaries have the same keys
            columns = data_list[0].keys()
            
            # Create the insert statement
            column_str = ", ".join(columns)
            value_str = ", ".join(f":{col}" for col in columns)
            
            query = f"INSERT INTO {table} ({column_str}) VALUES ({value_str})"
            
            # Execute for each row
            for data in data_list:
                self.connection.execute(text(query), data)
            
            self.connection.commit()
            return True
        except SQLAlchemyError as e:
            print(f"Error during bulk insert: {e}")
            if self.connection:
                self.connection.rollback()
            return False
    
    def get_table_schema(self, table: str) -> Optional[pd.DataFrame]:
        """
        Get the schema of a table.
        
        Args:
            table: Table name
            
        Returns:
            DataFrame containing column information or None if error
        """
        try:
            if not self.inspector:
                if not self.connect():
                    return None
            
            columns = self.inspector.get_columns(table)
            return pd.DataFrame([{
                'column_name': col['name'],
                'data_type': str(col['type']),
                'is_nullable': not col.get('nullable', True)
            } for col in columns])
        except SQLAlchemyError as e:
            print(f"Error getting table schema: {e}")
            return None
    
    def list_tables(self) -> List[str]:
        """
        List all tables in the current database.
        
        Returns:
            List of table names or empty list if error
        """
        try:
            if not self.inspector:
                if not self.connect():
                    return []
            
            return self.inspector.get_table_names()
        except SQLAlchemyError as e:
            print(f"Error listing tables: {e}")
            return []
