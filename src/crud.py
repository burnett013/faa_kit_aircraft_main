# src/crud.py
from sqlalchemy.orm import Session
from sqlalchemy import func
from models import Kit

def count_distinct_cities(db, states: list[str] | None = None) -> int:
    q = db.query(func.count(func.distinct(Kit.city)))
    if states:
        q = q.filter(Kit.state.in_(states))
    return q.scalar() or 0

def list_kits(
    db: Session,
    *,
    mfr: str | None = None,
    model: str | None = None,
    state: str | None = None,
    states: list[str] | None = None,   # <- supports region scoping
    kitmfg: str | None = None,
    kitmdl: str | None = None,
    limit: int = 100,
    offset: int = 0,
):
    q = db.query(Kit)

    if kitmfg:
        q = q.filter(Kit.kitmfg == kitmfg)
    if kitmdl:
        q = q.filter(Kit.kitmdl == kitmdl)
    if mfr:
        q = q.filter(Kit.mfr == mfr)
    if model:
        q = q.filter(Kit.model == model)
    if state:
        q = q.filter(Kit.state == state.upper())
    if states:
        q = q.filter(Kit.state.in_([s.upper() for s in states]))

    total = q.count()
    rows = q.order_by(Kit.n_number).offset(offset).limit(limit).all()
    return total, rows

def distinct_values(db: Session, field: str, kitmfg: str | None = None) -> list[str]:
    """
    Generic distinct getter.
    If field == 'kitmdl' and kitmfg is provided, scope models to that manufacturer.
    """
    allowed = {
        "mfr", "model", "state", "acftcat", "engcat", "surfcat",
        "ac_weight", "city", "zip_min", "kitmfg", "kitmdl"
    }
    if field not in allowed:
        raise ValueError(f"Unsupported field for distinct: {field}")

    if field == "kitmdl" and kitmfg:
        q = (
            db.query(Kit.kitmdl)
              .filter(Kit.kitmdl.isnot(None), Kit.kitmfg == kitmfg)
              .distinct()
              .order_by(Kit.kitmdl)
        )
        return [v for (v,) in q.all()]

    col = getattr(Kit, field)
    q = db.query(col).filter(col.isnot(None)).distinct().order_by(col)
    return [v for (v,) in q.all()]

def count_by_kitmfg(db: Session, states: list[str] | None = None):
    q = db.query(Kit.kitmfg, func.count().label("cnt"))
    if states:
        q = q.filter(Kit.state.in_([s.upper() for s in states]))
    return (
        q.group_by(Kit.kitmfg)
         .order_by(func.count().desc())
         .all()
    )

def count_by_state(db: Session, states: list[str] | None = None):
    """
    Return (state, count) pairs; optionally scoped to a list of state codes.
    """
    q = db.query(Kit.state, func.count().label("cnt"))
    if states:
        q = q.filter(Kit.state.in_([s.upper() for s in states]))
    return (
        q.group_by(Kit.state)
         .order_by(func.count().desc())
         .all()
    )

def count_by_engcat(db, states: list[str] | None=None):
    q = db.query(Kit.engcat, func.count()).filter(Kit.engcat.isnot(None), Kit.engcat != "")
    if states:
        q = q.filter(Kit.state.in_(states))
    return (
        q.group_by(Kit.engcat).order_by(func.count().desc()).all()

    )