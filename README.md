# Global Power Plant Efficiency Pipeline

### Project Context
Modern data analysis often starts with a significant hurdle: raw datasets are frequently too large for standard hardware and too "noisy" for immediate use. This project serves as a Production-Grade ETL (Extract, Transform, Load) solution designed to bridge that gap.

By utilizing the Global Power Plant Database, I developed a modular, class-based pipeline that prioritizes memory efficiency and data integrity, transforming 30,000+ rows of raw information into a streamlined dataset housed in a relational database.

### Technical Approach

1. Object-Oriented Architecture (OOP):
The pipeline is refactored from a procedural script into a modular PowerPlantETL class. This approach improves maintainability, allows for easier unit testing, and follows industry-standard software engineering patterns.

2. High-Performance Ingestion:
Instead of a standard load, the pipeline uses strategic schema definitions:

- Downcasting: Capacity metrics are stored as float32.

- Categorical Encoding: Repetitive strings like 'Country' and 'Fuel Type' are converted to categories.

- Result: Reduced the initial memory footprint by approximately 90%, ensuring stability on limited-resource environments.

3. Contextual Data Repair (Data Science Logic):
Real-world data is rarely complete. Rather than using a generic "fill-all" approach for missing commissioning years, the script uses a grouped median strategy. It calculates the median age of plants within the specific fuel category (e.g., matching a missing Hydro plant year with other Hydro plants), preserving the statistical integrity of the timeline.

4. Advanced Feature Engineering:
The pipeline classifies facilities into "Renewable" and "Non-Renewable" categories using vectorized operations. It also calculates renewable_capacity_mw as a specific feature for immediate green-energy analytics.

### Tools and Infrastructure
Language        -> Python | 
Data Processing -> Pandas | 
Database Engine -> SQLAlchemy | 
Storage         -> PostgreSQL (Relational) | 
Workflow        -> Object-Oriented ETL Class

### Getting Started
#### Prerequisites
- A running PostgreSQL instance
- A database named energy_db

#### Setup
1. Clone the repo:
   git clone https://github.com/shreygtm3-png/EnergyDataPipeline.git

2. Install dependencies:
   pip install pandas sqlalchemy pyscopg2

3. Environmental Configuration:
   Ensure your Database URI is correctly set in the script's CONFIG block:
   postgresql://username:password@localhost:5432/energy_db

4. Execute
