import pandas as pd
import os
import sys
from sqlalchemy import create_engine

class PowerPlantETL:
    def __init__(self, config):
        self.path = config['path']
        self.db_uri = config['db_uri']
        self.columns = ['country', 'name', 'capacity_mw', 'fuel1', 'commissioning_year']
        self.dtype_dict = {
            'country': 'category',
            'fuel1': 'category',
            'capacity_mw': 'float32'
        }
        self.renewable_sources = ['Hydro', 'Wind', 'Solar', 'Biomass', 'Geothermal', 'Wave and Tidal']

    def extract(self):
        print(f"--- Extracting data from {self.path} ---")
        try:
            df = pd.read_csv(self.path, usecols = self.columns, dtype = self.dtype_dict)
            print(f"Initial Memory Usage: {df.memory_usage(deep = True).sum() / 1024**2:.2f} MB")
            return df
        except Exception as e:
            print(f"Error during extraction: {e}")
            sys.exit()

    def transform(self, df):
        print("--- Transforming data ---")
        
        # Cleaning
        df['name'] = df['name'].str.strip().str.title()

        # Contextual Imputation
        df['commissioning_year'] = df.groupby('fuel1', observed = True)['commissioning_year'].transform(
            lambda x: x.fillna(x.median())
        )

        # Feature Engineering
        df['is_renewable'] = df['fuel1'].isin(self.renewable_sources)
        df['renewable_capacity_mw'] = df['capacity_mw'] * df['is_renewable']

        return df
    
    def load(self, df, table_name):
        print(f"--- Loading data into table: {table_name} ---")
        try: 
            engine = create_engine(self.db_uri)
            df.to_sql(table_name, engine, if_exists = 'replace', index = False)
            print("Successfully loaded data to Postgres!")
        
        except Exception as e:
            print(f"Database Error: {e}")

if __name__ == "__main__":
    # Hardcoded strings to os.environ.get() values, to read safe .env file locally!
    CONFIG = {
        'path': os.environ.get('DATA_PATH'),
        'db_uri': os.environ.get('DATABASE_URL')
    }
    if not CONFIG['path'] or not CONFIG['db_uri']:
        print("Error: DATA_PATH and DATABASE_URL must be set in environmental variables.")
        sys.exit(1)

    etl = PowerPlantETL(CONFIG)

    raw_df = etl.extract()
    cleaned_df = etl.transform(raw_df)
    etl.load(cleaned_df, "power_plants_cleaned")
    print("\nETL Pipeline Completed")