# # src/schemas.py
# '''
# schemas.py defines how the data is serialized (sent over the web).
# '''
# from pydantic import BaseModel
# from typing import Optional
# from datetime import date

# class KitOut(BaseModel):
#     n_number:      Optional[str] = None
#     serial_number: Optional[str] = None
#     mfr_mdl_code:  Optional[str] = None
#     mfr:           Optional[str] = None
#     model:         Optional[str] = None
#     acftcat:       Optional[str] = None
#     no_seats:      Optional[int] = None
#     ac_weight:     Optional[str] = None
#     engcat:        Optional[str] = None
#     surfcat:       Optional[str] = None
#     no_eng:        Optional[int] = None
#     city:          Optional[str] = None
#     state:         Optional[str] = None
#     zip_min:       Optional[str] = None
#     mode_s_code:   Optional[str] = None

#     kitmfg:        Optional[str] = None
#     kitmdl:        Optional[str] = None

#     # back in
#     year_mfr:         Optional[int]  = None
#     last_action_date: Optional[date] = None
#     cert_issue_date:  Optional[date] = None
#     air_worth_date:   Optional[date] = None

#     class Config:
#         from_attributes = True