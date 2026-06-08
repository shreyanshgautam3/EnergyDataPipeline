# Global Power Plant AI Analysis Pipeline

A two-layer data pipeline that ingests and transforms a global power plant dataset, loads it into PostgreSQL, then queries anomalies and passes structured context to the **Google Gemini 2.5 Flash** API to generate operational incident reports.

---

## Architecture

```
CSV Dataset
    │
    ▼
[ pipeline.py ]  ── Extract → Transform → Load ──▶  PostgreSQL
                                                          │
                                                          ▼
                                                  [ analyzer.py ]
                                                  Threshold Query
                                                          │
                                                          ▼
                                                  Gemini 2.5 Flash
                                                          │
                                                          ▼
                                              AI Incident Report (stdout)
```

---

## Layer 1 — ETL Pipeline (`pipeline.py`)

Handles ingestion and transformation of the [Global Power Plant Database](https://datasets.wri.org/dataset/globalpowerplantdatabase) CSV.

**Extract**
- Reads selected columns with memory-optimised `dtype` mapping (`category`, `float32`)
- Reports initial memory usage on load

**Transform**
- Strips and title-cases plant names
- Applies fuel-type-grouped median imputation for missing `commissioning_year` values
- Engineers two features:
  - `is_renewable` — boolean flag based on fuel type classification
  - `renewable_capacity_mw` — derived capacity for renewable plants only

**Load**
- Loads the cleaned DataFrame into a PostgreSQL table (`power_plants_cleaned`) via SQLAlchemy

---

## Layer 2 — AI Analyzer (`analyzer.py`)

Queries anomaly data from the loaded table and sends it to the Gemini API for analysis.

**fetch_anomaly_data(energy_threshold)**
- Queries plants with `capacity_mw` below a configurable threshold
- Returns a structured DataFrame ordered by capacity

**generate_ai_report(anomaly_df)**
- Formats query results into a structured prompt with labelled context sections
- Sends to `gemini-2.5-flash` with a Reliability Engineer system instruction and `temperature=0.2`
- Returns a formatted Operational Incident Summary covering:
  - Fuel type and country concentration patterns
  - Renewable vs non-renewable grid footprint assessment
  - Three specific engineering remediation steps

---

## Project Structure

```
EnergyDataPipeline/
├── pipeline.py        # ETL layer: Extract, Transform, Load
├── analyzer.py        # AI layer: PostgreSQL query + Gemini API
├── .env               # Environment variables (not committed)
├── .env.example       # Template for environment setup
├── requirements.txt   # Python dependencies
└── README.md
```

---

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/shreyanshgautam3/EnergyDataPipeline
cd EnergyDataPipeline
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

Copy the example file and fill in your values:

```bash
cp .env.example .env
```

`.env.example`:

```
DATA_PATH=path/to/global_power_plant_database.csv
DATABASE_URL=postgresql://user:password@localhost:5432/energy_db

DB_HOST=localhost
DB_PORT=5432
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_NAME=energy_db

GEMINI_API_KEY=your_gemini_api_key
```

### 4. Download the dataset

Download `global_power_plant_database.csv` from the [WRI Open Data Portal](https://datasets.wri.org/dataset/globalpowerplantdatabase) and set its path in `DATA_PATH`.

---

## Usage

**Step 1 — Run the ETL pipeline** to load cleaned data into PostgreSQL:

```bash
python pipeline.py
```

**Step 2 — Run the AI analyzer** to generate an incident report:

```bash
python analyzer.py
```

The threshold defaults to `150.0 MW`. To adjust it, modify the `energy_threshold` parameter in `analyzer.py`:

```python
raw_anomalies = analyzer.fetch_anomaly_data(energy_threshold=300.0)
```

---

## Dependencies

```
pandas
sqlalchemy
psycopg2-binary
python-dotenv
google-genai
```

---

## Key Technical Decisions

| Decision | Reason |
|---|---|
| `category` dtype for country and fuel columns | Reduces memory footprint on high-cardinality string columns |
| Fuel-grouped median imputation | Preserves domain context when filling missing commissioning years |
| `urllib.parse.quote_plus` for DB password | Handles special characters in passwords safely |
| `temperature=0.2` for Gemini | Keeps model output deterministic and technically precise |
| Structured prompt with labelled sections | Constrains model output format for consistent, parseable reports |

---

## Renewable Classification

The following fuel types are classified as renewable:

`Hydro` · `Wind` · `Solar` · `Biomass` · `Geothermal` · `Wave and Tidal`
