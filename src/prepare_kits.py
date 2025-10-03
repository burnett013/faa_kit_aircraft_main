# src/prepare_kits.py
import os
import pandas as pd
from pathlib import Path

SRC = os.environ.get("DATA_XLSX", "/app/data/demo.xlsx")
OUT = os.environ.get("DATA_OUT", "/app/data/processed/kits_prepared.parquet")

NEEDED = [
    "N-NUMBER","SERIAL NUMBER","MFR MDL CODE","MFR","MODEL",
    "ACFTCAT","NO-SEATS","AC-WEIGHT","ENGCAT",
    "SURFCAT","NO-ENG","CITY","STATE","ZIP_MIN",
    "KITMFG","KITMDL","MODE S CODE",
    "YEAR MFR","LAST ACTION DATE","CERT ISSUE DATE","AIR WORTH DATE",
]

RENAME = {
    "N-NUMBER": "n_number",
    "SERIAL NUMBER": "serial_number",
    "MFR MDL CODE": "mfr_mdl_code",
    "MFR": "mfr",
    "MODEL": "model",
    "ACFTCAT": "acftcat",
    "NO-SEATS": "no_seats",
    "AC-WEIGHT": "ac_weight",
    "ENGCAT": "engcat",
    "SURFCAT": "surfcat",
    "NO-ENG": "no_eng",
    "CITY": "city",
    "STATE": "state",
    "ZIP_MIN": "zip_min",
    "KITMFG": "kitmfg",
    "KITMDL": "kitmdl",
    "MODE S CODE": "mode_s_code",
    "YEAR MFR": "year_mfr",
    "LAST ACTION DATE": "last_action_date",
    "CERT ISSUE DATE": "cert_issue_date",
    "AIR WORTH DATE": "air_worth_date",
}

def main():
    if not os.path.exists(SRC):
        raise FileNotFoundError(SRC)

    df = pd.read_excel(SRC, engine="openpyxl")
    df = df[NEEDED].rename(columns=RENAME)

    # trim strings
    for c in ["n_number","mfr","model","acftcat","ac_weight","engcat","surfcat",
              "city","state","kitmfg","kitmdl","zip_min","mode_s_code"]:
        df[c] = df[c].astype(str).str.strip()

    # state normalization
    df["state"] = df["state"].str.upper().str[:2]

    # numeric coercions
    df["no_seats"] = pd.to_numeric(df["no_seats"], errors="coerce").astype("Int64")
    df["no_eng"]   = pd.to_numeric(df["no_eng"],   errors="coerce").astype("Int64")
    df["year_mfr"] = pd.to_numeric(df["year_mfr"], errors="coerce").astype("Int64")

    # date coercions (result is datetime64[ns]; convert to date for parquet portability)
    for dcol in ["last_action_date","cert_issue_date","air_worth_date"]:
        df[dcol] = pd.to_datetime(df[dcol], errors="coerce").dt.date

    Path(os.path.dirname(OUT)).mkdir(parents=True, exist_ok=True)
    df.to_parquet(OUT, index=False)
    print(f"Prepared {len(df)} rows → {OUT}")

if __name__ == "__main__":
    main()