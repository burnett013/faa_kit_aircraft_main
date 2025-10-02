# src/main.py
'''
The main.py file is the entry point and controller for the FastAPI backend — it’s what turns the database and data-access logic into an API service that the Streamlit app can call. The st app never talks to the database directly; it always goes through this API.
'''
from fastapi import FastAPI, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from db import engine, SessionLocal
from models import Base, Kit, KitOut
import crud
# from schemas import KitOut


Base.metadata.create_all(bind=engine)

app = FastAPI(title="FAA Kits API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/kits", response_model=list[KitOut])
def get_kits(
    mfr: str | None = Query(default=None),
    model: str | None = Query(default=None),
    state: str | None = Query(default=None),
    states: str | None = Query(default=None, description="Comma-separated states"),
    limit: int = Query(default=100, ge=1, le=5000),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    states_list = [s.strip() for s in states.split(",")] if states else None
    total, rows = crud.list_kits(
        db, mfr=mfr, model=model, state=state, states=states_list, limit=limit, offset=offset
    )
    return rows

# Filters ------------------------------------------------------------
@app.get("/kits/filters/mfrs", response_model=list[str])
def get_mfrs(db: Session = Depends(get_db)):
    return crud.distinct_values(db, "mfr")

@app.get("/kits/filters/kitmfgs", response_model=list[str])
def get_kitmfgs(db: Session = Depends(get_db)):
    return crud.distinct_values(db, "kitmfg")

@app.get("/kits/filters/kitmdls", response_model=list[str])
def get_kitmdls(kitmfg: str, db: Session = Depends(get_db)):
    return crud.distinct_values(db, "kitmdl", kitmfg=kitmfg)#-------

@app.get("/kits/filters/states", response_model=list[str])
def get_states(db: Session = Depends(get_db)):
    return crud.distinct_values(db, "state")

# Aggregations -----------------------------------------------------
@app.get("/kits/agg/by_kitmfg")
def agg_by_kitmfg(states: str | None = Query(default=None), db: Session = Depends(get_db)):
    states_list = [s.strip() for s in states.split(",")] if states else None
    rows = crud.count_by_kitmfg(db, states_list)
    return [{"kitmfg": k, "count": c} for k, c in rows]

@app.get("/kits/agg/by_state")
def agg_by_state(states: str | None = Query(default=None), db: Session = Depends(get_db)):
    states_list = [s.strip() for s in states.split(",")] if states else None
    rows = crud.count_by_state(db, states_list)
    return [{"state": s, "count": c} for s, c in rows]

@app.get("/kits/agg/by_engcat")
def agg_by_engcat(states: str | None = Query(None), db: Session = Depends(get_db)):
    states_list = [s.strip() for s in states.split(",")] if states else None
    return [{"engcat": e, "count": c} for e, c in crud.count_by_engcat(db, states_list)]

# Metrics -----------------------------------------------------
@app.get("/kits/metrics/city_count")
def city_count(states: str | None = Query(default=None), db: Session = Depends(get_db)):
    states_list = [s.strip() for s in states.split(",")] if states else None
    count = crud.count_distinct_cities(db, states_list)
    return {"city_count": count}

