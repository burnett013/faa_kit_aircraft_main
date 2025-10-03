# src/ingest_kits.py
import os
import pandas as pd
from sqlalchemy import text
from sqlalchemy.engine import Engine
from db import engine

# PARQUET_PATH = "/app/data/processed/kits_prepared.parquet"
PARQUET_PATH = os.getenv("DATA_OUT", "/app/data/processed/kits_prepared.parquet")

def load_raw(engine: Engine, path: str):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Could not find {path} inside container.")
    df = pd.read_parquet(path)
    print(f"Read {len(df):,} rows and {len(df.columns)} cols from {path}")

    # Re-create kits_raw from parquet
    with engine.begin() as conn:
        conn.execute(text("DROP TABLE IF EXISTS kits_raw CASCADE;"))
    df.to_sql("kits_raw", engine, if_exists="replace", index=False, method="multi", chunksize=1000)
    print("Wrote to kits_raw")

def create_curated_table(engine: Engine):
    # src/ingest_kits.py (only the SQL block shown)
    curated_sql = """
    DROP TABLE IF EXISTS kits;

    CREATE TABLE kits AS
    SELECT
    k.n_number::text               AS n_number,
    k.serial_number::text          AS serial_number,
    k.mfr_mdl_code::text           AS mfr_mdl_code,
    k.mfr::text                    AS mfr,
    k.model::text                  AS model,
    k.acftcat::text                AS acftcat,
    k.ac_weight::text              AS ac_weight,
    k.engcat::text                 AS engcat,
    k.surfcat::text                AS surfcat,
    k.kitmfg::text                 AS kitmfg,
    k.kitmdl::text                 AS kitmdl,

    CASE WHEN (k.no_seats)::text ~ '^[0-9]+$'
        THEN (k.no_seats)::int ELSE NULL END AS no_seats,

    CASE WHEN (k.no_eng)::text ~ '^[0-9]+$'
        THEN (k.no_eng)::int ELSE NULL END   AS no_eng,

    k.city::text                   AS city,
    UPPER(k.state::text)           AS state,
    k.zip_min::text                AS zip_min,
    k.mode_s_code::text            AS mode_s_code,

    -- year + dates back in
    CASE WHEN (k.year_mfr)::text ~ '^[0-9]{4}$' THEN (k.year_mfr)::int ELSE NULL END AS year_mfr,
    NULLIF(k.last_action_date::text,'')::date AS last_action_date,
    NULLIF(k.cert_issue_date::text,'')::date  AS cert_issue_date,
    NULLIF(k.air_worth_date::text,'')::date   AS air_worth_date

    FROM kits_raw k;

    ALTER TABLE kits ADD COLUMN id bigserial PRIMARY KEY;

    CREATE INDEX IF NOT EXISTS idx_kits_mfr      ON kits (mfr);
    CREATE INDEX IF NOT EXISTS idx_kits_model    ON kits (model);
    CREATE INDEX IF NOT EXISTS idx_kits_state    ON kits (state);
    CREATE INDEX IF NOT EXISTS idx_kits_acftcat  ON kits (acftcat);
    CREATE INDEX IF NOT EXISTS idx_kits_engcat   ON kits (engcat);
    CREATE INDEX IF NOT EXISTS idx_kits_year_mfr ON kits (year_mfr);
    """
    with engine.begin() as conn:
        for stmt in curated_sql.strip().split(";"):
            s = stmt.strip()
            if s:
                conn.execute(text(s + ";"))
    print("Built curated kits table")

def main():
    load_raw(engine, PARQUET_PATH)
    create_curated_table(engine)
    print("Done.")

if __name__ == "__main__":
    main()