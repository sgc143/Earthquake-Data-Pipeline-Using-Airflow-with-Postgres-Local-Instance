import os
import pandas as pd
import requests
import psycopg2
from psycopg2 import errors
from datetime import datetime, timedelta
from config import Config

class EarthquakePipeline:
    """Local earthquake data ETL pipeline."""
    
    def __init__(self):
        self.data_path = "./data"
        self.postgres_conn_details = {
            "host": os.getenv("PGHOST", "localhost"),
            "port": os.getenv("PGPORT", "5432"),
            "user": os.getenv("PGUSER", "postgres"),
            "password": os.getenv("PGPASSWORD", "postgres"),
            "dbname": os.getenv("PGDATABASE", "earthquake_data"),
        }
        
        # Ensure data directory exists
        os.makedirs(self.data_path, exist_ok=True)
    
    def get_postgres_conn(self):
        """Establishes a connection to the PostgreSQL database."""
        return psycopg2.connect(**self.postgres_conn_details)
    
    def get_postgres_admin_conn(self):
        """Establishes a connection to the default database for admin tasks."""
        admin_conn_details = self.postgres_conn_details.copy()
        admin_conn_details["dbname"] = "postgres"  # Connect to default database
        return psycopg2.connect(**admin_conn_details)
    
    def create_database(self):
        """Creates the earthquake_data database and tables if they don't exist."""
        try:
            conn = self.get_postgres_admin_conn()
            conn.autocommit = True
            cur = conn.cursor()
            
            # Check if database exists
            cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", 
                       (self.postgres_conn_details["dbname"],))
            if not cur.fetchone():
                # Create database
                cur.execute(f"CREATE DATABASE {self.postgres_conn_details['dbname']}")
                print(f"Database '{self.postgres_conn_details['dbname']}' created successfully.")
            else:
                print(f"Database '{self.postgres_conn_details['dbname']}' already exists.")
            
            cur.close()
            conn.close()
            
        except Exception as e:
            print(f"Error creating database: {e}")
        
        # Create tables
        self.create_tables()
    
    def create_tables(self):
        """Creates the earthquake and stage_earthquake tables."""
        try:
            conn = self.get_postgres_conn()
            cur = conn.cursor()
            
            # Create earthquake table
            create_earthquake_table = """
            CREATE TABLE IF NOT EXISTS public.earthquake (
                id SERIAL PRIMARY KEY,
                time BIGINT NOT NULL,
                place VARCHAR(255),
                magnitude FLOAT,
                longitude FLOAT NOT NULL,
                latitude FLOAT NOT NULL,
                depth FLOAT,
                file_name VARCHAR(255) NOT NULL
            )
            """
            cur.execute(create_earthquake_table)
            
            # Create stage_earthquake table
            create_stage_table = """
            CREATE TABLE IF NOT EXISTS public.stage_earthquake (
                id SERIAL PRIMARY KEY,
                ts TIMESTAMP NOT NULL,
                dt DATE NOT NULL,
                place VARCHAR(255),
                magnitude FLOAT,
                latitude FLOAT NOT NULL,
                longitude FLOAT NOT NULL
            )
            """
            cur.execute(create_stage_table)
            
            conn.commit()
            print("Tables created successfully.")
            
        except Exception as e:
            print(f"Error creating tables: {e}")
            conn.rollback()
        finally:
            cur.close()
            conn.close()
    
    def fetch_data_to_local_csv(self, execution_date):
        """Fetches earthquake data and saves it to a CSV file."""
        print(f"Fetching data for date: {execution_date}")
        start_time = execution_date
        # Fetch one full day of data
        end_time = (datetime.strptime(execution_date, "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")
        
        url = f"https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&starttime={start_time}&endtime={end_time}"
        
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data from USGS API: {e}")
            return ""
        
        data = response.json()
        features = data.get("features", [])
        if not features:
            print("No features found. Skipping file creation.")
            return ""
        
        filename = f"{execution_date.replace('-', '')}_earthquakedata.csv"
        full_path = os.path.join(self.data_path, filename)
        
        earthquakes = []
        for feature in features:
            properties = feature["properties"]
            geometry = feature["geometry"]
            earthquake = {
                "time": properties.get("time"),
                "place": properties.get("place"),
                "magnitude": properties.get("mag"),
                "longitude": geometry["coordinates"][0],
                "latitude": geometry["coordinates"][1],
                "depth": geometry["coordinates"][2],
                "file_name": filename,
            }
            earthquakes.append(earthquake)
        
        df = pd.DataFrame(earthquakes)
        df.to_csv(full_path, index=False)
        print(f"File successfully created at: {full_path}")
        return full_path
    
    def load_csv_to_postgres(self, csv_path):
        """Deletes old records and loads the new CSV into the 'earthquake' table."""
        if not csv_path:
            print("No CSV path provided. Skipping load.")
            return
        
        filename_only = os.path.basename(csv_path)
        conn = self.get_postgres_conn()
        cur = conn.cursor()
        
        try:
            # 1. Delete old records for this file
            delete_query = "DELETE FROM public.earthquake WHERE file_name=%s"
            cur.execute(delete_query, (filename_only,))
            print(f"Deleted old records for file: {filename_only}")
            
            # 2. Load new records from CSV
            sql = "COPY public.earthquake(time, place, magnitude, longitude, latitude, depth, file_name) FROM STDIN WITH (FORMAT CSV, HEADER, DELIMITER ',')"
            with open(csv_path, "r", encoding='utf-8') as f:
                cur.copy_expert(sql, f)
            print(f"Successfully loaded new data from {filename_only}")
            
            conn.commit()
        except Exception as e:
            print(f"An error occurred during load: {e}")
            conn.rollback()
            raise
        finally:
            cur.close()
            conn.close()
    
    def transform_in_postgres(self, p_start_date, p_end_date):
        """Deletes old records and transforms data from raw table to stage table."""
        conn = self.get_postgres_conn()
        cur = conn.cursor()
        
        try:
            # 1. Delete old records from the staging table for the date range
            delete_query = "DELETE FROM public.stage_earthquake WHERE dt BETWEEN %s AND %s"
            cur.execute(delete_query, (p_start_date, p_end_date))
            print(f"Deleted old stage records for dates: {p_start_date} to {p_end_date}")
            
            # 2. Insert transformed records
            transform_sql = """
                INSERT INTO public.stage_earthquake (ts, dt, place, magnitude, latitude, longitude)
                SELECT
                    to_timestamp(time/1000) AS ts,
                    to_timestamp(time/1000)::date AS dt,
                    CASE 
                        WHEN place IS NOT NULL AND POSITION(' of ' IN place) > 0 
                        THEN TRIM(SUBSTRING(place FROM POSITION(' of ' IN place) + 4))
                        ELSE place
                    END AS place,
                    magnitude,
                    latitude,
                    longitude
                FROM public.earthquake
                WHERE to_timestamp(time/1000)::date BETWEEN %s AND %s
                AND magnitude IS NOT NULL
                AND latitude IS NOT NULL
                AND longitude IS NOT NULL;
            """
            cur.execute(transform_sql, (p_start_date, p_end_date))
            print(f"Successfully transformed and inserted new records for {p_start_date}")
            
            conn.commit()
        except errors.UndefinedTable:
            print("A table was not found. Please ensure tables are created first.")
            conn.rollback()
            raise
        except Exception as e:
            print(f"An unexpected error occurred during transform: {e}")
            conn.rollback()
            raise
        finally:
            cur.close()
            conn.close()
