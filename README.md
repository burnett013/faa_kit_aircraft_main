# FAA Kit Aircraft Database Explorer
##### Build In Texas by JABurnett (Updated 9/2025)

A Streamlit + FastAPI + PostgreSQL application for exploring and visualizing **FAA-registered kit-built aircraft** in the United States.  
This project lets users search, filter, and analyze data on experimental aircraft manufacturers, models, and registration trends.

---

## Purpose

The **FAA Kit Aircraft Database Explorer** provides an interactive way to:
- Query and browse FAA aircraft registration data filtered to **kit-built** aircraft.
- Explore manufacturers, models, and state distributions.
- Visualize aircraft counts by **manufacturer** and **state**.
- Quickly find data subsets using **sidebar filters** (manufacturer, model, state, limit).
- Drill down with a **search box** that supports partial manufacturer name matches.

This app demonstrates a clean **Python data pipeline** with:
- A **FastAPI backend** serving filtered data and aggregation endpoints.
- A **PostgreSQL** database storing the FAA dataset.
- A **Streamlit frontend** that consumes the API and renders charts.

---

## 🧠 How It Works

### Architecture Overview

+———––+        +———––+        +—————+
|  Streamlit  | <––> |   FastAPI   | <––> |   PostgreSQL   |
|  Frontend   |        |  Backend    |        |   Database     |
+———––+        +———––+        +—————+

1. **Data Preparation** (`prepare_kits.py` / `ingest_kits.py`):
   - Cleans and normalizes raw FAA registration data.
   - Trims whitespace, standardizes case, and selects only kit-built aircraft.
   - Loads the cleaned dataset into the `kits` table in PostgreSQL.

2. **API Service** (`main.py` + `crud.py`):
   - Provides REST endpoints for querying and aggregating aircraft data.
   - Exposes `/kits`, `/kits/filters/*`, and `/kits/agg/*` routes.
   - Uses SQLAlchemy ORM for querying.

3. **Streamlit App** (`app.py`):
   - Interacts with the API service using `requests`.
   - Renders filters and charts in a dashboard format.
   - Supports partial-text search for manufacturers.
   - Dynamically loads available models based on the selected manufacturer.

---

## Key Features

| Feature | Description |
|----------|--------------|
| Search | Type part of a manufacturer name to narrow down results (e.g. “vans”). |
| Manufacturer Filter | Dropdown to select from available kit manufacturers. |
| Model Filter | Auto-populates based on selected manufacturer. |
| State Filter | Filter by U.S. state of registration. |
| Visuals | Bar charts showing aircraft counts by manufacturer and by state. |
| Pagination | Adjustable result limit for browsing data tables. |

---

## Project Structure

faa_kits/
│
├── src/
│   ├── app.py                # Streamlit frontend
│   ├── main.py               # FastAPI entry point
│   ├── crud.py               # Database query helpers
│   ├── models.py             # SQLAlchemy ORM models
│   ├── prepare_kits.py       # Data cleaning / preprocessing
│   ├── ingest_kits.py        # DB loading logic
│   └── database.py           # Connection engine setup
│
├── docker-compose.yml        # Container orchestration
├── Dockerfile.api_service    # FastAPI container
├── Dockerfile.app_service    # Streamlit container
└── requirements.txt          # Dependencies

---

## Dependencies

| Package | Purpose |
|----------|----------|
| **FastAPI** | Backend web framework for serving API endpoints. |
| **SQLAlchemy** | ORM for interacting with the PostgreSQL database. |
| **Streamlit** | Frontend dashboard for user interaction. |
| **Requests** | HTTP client for connecting Streamlit → FastAPI. |
| **Pandas** | Used during preprocessing for data cleaning. |
| **Uvicorn** | ASGI server for FastAPI. |
| **PostgreSQL** | Relational database for persistent storage. |
| **Docker Compose** | Multi-service orchestration (DB + API + UI). |

Install all dependencies via:
```
pip install -r requirements.txt
```
## Running the App Via Docker
From the project root:
```
docker compose up --build
```

Then open your browser and visit:
http://localhost:8501

By default:
	•	Streamlit runs on port 8501.
	•	FastAPI runs on port 8000.
	•	PostgreSQL runs on port 5432.

To view API docs:
http://localhost:8000/docs

## Local Development (Without Docker)

If you prefer running manually:
	1.	Start PostgreSQL locally and create a database named faa_kits.
	2.	Update database connection in database.py.
	3.	Prepare data:
```
python src/prepare_kits.py
python src/ingest_kits.py
 ```
Start API:
```
uvicorn src.main:app --reload
```
Start Streramlit:
```
streamlit run src/app.py
```
## Example Endpoints

| Endpoint | Description |
|-----------|--------------|
| `/kits` | Returns aircraft list (with query filters). |
| `/kits/filters/mfrs` | Distinct manufacturers. |
| `/kits/filters/states` | Distinct states. |
| `/kits/filters/kitmdls?kitmfg=VANS%20AIRCRAFT%20INC` | Models for selected manufacturer. |
| `/kits/agg/by_kitmfg` | Count of aircraft by manufacturer. |
| `/kits/agg/by_state` | Count of aircraft by state. |

## Future Enhhancements
• Dynamic linking between filters (completed: KitMFG → KitMDL).
• Additional charts (engine category, airframe type, weight class).
• Full-text search (SQL ILIKE support for partial matches).
• Map visualization of registrations by ZIP or city.
• File upload support for new FAA dataset versions.

⸻
