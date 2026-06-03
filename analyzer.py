import os
import sys
import urllib.parse
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine
from google import genai
from google.genai import types

# Load environment configurations
load_dotenv()

class PowerPlantAIAnalyzer:
    # Orchestrates data extraction from PostgreSQL and handles LLM analysis.
    
    def __init__(self):
        # Initialize Gemini Developer API Client
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("Error: GEMINI_API_KEY missing from environment variables.")
            sys.exit(1)
        self.ai_client = genai.Client(api_key=api_key)
        
    def _get_db_engine(self):
        # Creates a SQLAlchemy engine using environment variables
        host = os.getenv("DB_HOST")
        port = os.getenv("DB_PORT")
        user = os.getenv("DB_USER")
        database = os.getenv("DB_NAME")
        raw_password = os.getenv("DB_PASSWORD")
        
        encoded_password = urllib.parse.quote_plus(raw_password)
        
        db_uri = f"postgresql://{user}:{encoded_password}@{host}:{port}/{database}"
        return create_engine(db_uri)

    def fetch_anomaly_data(self, energy_threshold: float = 400.0) -> pd.DataFrame:
        # Queries the database for plants operating below a specific capacity. Uses SQLAlchemy to comply with modern Pandas standards.
        
        query = """
            SELECT 
                country, 
                name, 
                capacity_mw, 
                fuel1, 
                commissioning_year, 
                is_renewable, 
                renewable_capacity_mw
            FROM power_plants_cleaned
            WHERE capacity_mw < %s
            ORDER BY capacity_mw DESC
            LIMIT 5;
        """
        try:
            engine = self._get_db_engine()
            # Safely open and close the connection using a context manager
            with engine.connect() as conn:
                df = pd.read_sql_query(query, conn, params = (energy_threshold,))
            return df
        except Exception as e:
            print(f"Database Query Failed: {e}")
            return pd.DataFrame()

    def generate_ai_report(self, anomaly_df: pd.DataFrame) -> str:
        # Transforms tabular structured data into an analytical prompt context and executes an API call to a generative model.
        
        if anomaly_df.empty:
            return "No plant data anomalies detected within the current threshold boundaries."

        data_context = anomaly_df.to_string(index=False)
        
        system_instruction = (
            "You are an expert Reliability Engineer specializing in international power grids. "
            "Analyze raw data updates, prioritize operational risk, and format insights professionally."
        )

        prompt = f"""
        Review the following dataset of lower-capacity power plants sourced from our clean energy repository:
        
        ### RAW SYSTEM DATA:
        {data_context}
        
        ### TASK:
        Generate a structured Operational Incident Summary. 
        1. Identify which fuel types or countries are showing concentrated lower capacities.
        2. Specifically note if the grid footprint is weighted towards renewable or non-renewable sources based on the dataset metrics.
        3. Provide 3 highly specific engineering action steps for remediation based on these fuel asset mixtures.
        4. Keep the report clear, technical, and actionable for project managers.
        """

        try:
            response = self.ai_client.models.generate_content(
                model = 'gemini-2.5-flash',
                contents = prompt,
                config = types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.2,
                )
            )
            return response.text
        except Exception as e:
            return f"Failed to interface with AI Model API: {e}"

if __name__ == "__main__":
    print("Initializing Data-Driven AI Analyzer pipeline...")
    analyzer = PowerPlantAIAnalyzer()
    
    print("Step 1: Extracting metrics from PostgreSQL via Pandas & SQLAlchemy...")
    raw_anomalies = analyzer.fetch_anomaly_data(energy_threshold = 150.0)
    
    print("Step 2: Transferring structured context into Gemini-2.5-Flash API...")
    report = analyzer.generate_ai_report(raw_anomalies)
    
    print("\n--- AI GENERATED INCIDENT REPORT ---\n")
    print(report)