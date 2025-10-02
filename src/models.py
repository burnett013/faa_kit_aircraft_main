# src/models.py

from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, Date
from pydantic import BaseModel
from typing import Optional
from datetime import date

Base = declarative_base()

# ---------- SQLAlchemy ORM ----------

class Kit(Base):
    __tablename__ = "kits"

    # Use n_number as the natural primary key
    n_number = Column(String, primary_key=True, nullable=False, index=True)

    serial_number  = Column(String)
    mfr_mdl_code   = Column(String)
    mfr            = Column(String, index=True)
    model          = Column(String, index=True)
    acftcat        = Column(String)
    no_seats       = Column(Integer)
    ac_weight      = Column(String)
    engcat         = Column(String)
    surfcat        = Column(String)
    no_eng         = Column(Integer)
    city           = Column(String)
    state          = Column(String, index=True)
    zip_min        = Column(String)
    kitmfg         = Column(String, index=True)
    kitmdl         = Column(String)
    mode_s_code    = Column(String)

    # Newly restored fields
    year_mfr         = Column(Integer)
    last_action_date = Column(Date)
    cert_issue_date  = Column(Date)
    air_worth_date   = Column(Date)

# ---------- Pydantic schema (API responses) ----------
class KitOut(BaseModel):
    n_number: str
    serial_number: Optional[str] = None
    mfr_mdl_code: Optional[str] = None
    mfr: Optional[str] = None
    model: Optional[str] = None
    acftcat: Optional[str] = None
    no_seats: Optional[int] = None
    ac_weight: Optional[str] = None
    engcat: Optional[str] = None
    surfcat: Optional[str] = None
    no_eng: Optional[int] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_min: Optional[str] = None
    kitmfg: Optional[str] = None
    kitmdl: Optional[str] = None
    mode_s_code: Optional[str] = None

    class Config:
        from_attributes = True  # map from SQLAlchemy rows -> Pydantic model