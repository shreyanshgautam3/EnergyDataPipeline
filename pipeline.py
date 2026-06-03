<<<<<<< HEAD
import pandas as pd
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
    CONFIG = {
        'path': r"D:\The_work\Python_Projects\Projects\Global Power Plant\globalpowerplantdatabasev110\global_power_plant_database.csv",
        'db_uri': "postgresql://postgres:Shreyansh%40123@localhost:5432/energy_db"
    }

    etl = PowerPlantETL(CONFIG)

    raw_df = etl.extract()
    cleaned_df = etl.transform(raw_df)
    etl.load(cleaned_df, "power_plants_cleaned")
    print("\n--- ETL Pipeline Complete")
=======
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
        df['commissiong_year'] = df.groupby('fuel1', observed = True)['commissioning_year'].transform(
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
    CONFIG = {
        'path': r"D:\Python_Projects\Projects\Global Power Plant\globalpowerplantdatabasev110\global_power_plant_database.csv",
        'db_uri': "postgresql://postgres:***************@localhost:5432/energy_db"
    }

    etl = PowerPlantETL(CONFIG)

    raw_df = etl.extract()
    cleaned_df = etl.transform(raw_df)
    etl.load(cleaned_df, "power_plants_cleaned")
    print("\n--- ETL Pipeline Complete")
>>>>>>> 8a1c440b9395ccfd82071ee69dfd8511f1b2561d
