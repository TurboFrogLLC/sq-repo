# logic/estimator.py
from __future__ import annotations
import math, csv
from typing import Optional, Tuple, List, Dict
from core.rules import DENSITY
from core.io_files import candidate_paths_first

def mm_to_in(x: Optional[float]) -> Optional[float]:
    if x in (None, ""): return None
    try: return float(x) / 25.4
    except Exception: return None

def parse_len_by_units(s: str, units: str) -> Optional[float]:
    s = (s or "").strip()
    if s == "": return None
    try:
        v = float(s)
        return v if units == "in" else (v / 25.4)
    except Exception:
        return None

def calc_ba(angle_deg: float, r_in: float, k_factor: float, t_in: float) -> float:
    return (math.pi / 180.0) * angle_deg * (r_in + k_factor * t_in)

def calc_bd(angle_deg: float, r_in: float, t_in: float, ba: float) -> float:
    sb = (r_in + t_in) * math.tan((angle_deg / 2.0) * (math.pi / 180.0))
    return 2.0 * sb - ba

def compute_weight_lb(material: str,
                      thickness_in: Optional[float],
                      flat_w_in: Optional[float],
                      flat_h_in: Optional[float]) -> Optional[float]:
    if not material or None in (thickness_in, flat_w_in, flat_h_in):
        return None
    dens = DENSITY.get(material.upper())
    if not dens:
        return None
    try:
        weight = dens * float(thickness_in) * float(flat_w_in) * float(flat_h_in)
        return round(weight, 4)
    except Exception:
        return None

def get_form_defaults_from_csv() -> Tuple[float, float]:
    """Returns (setup_min_default, sec_per_bend_default). Fallback (2.0, 10.0)."""
    setup_def = 2.0
    sec_per_bend_def = 10.0
    path = candidate_paths_first("Operations[UFG]_sQL.csv")
    if not path:
        return setup_def, sec_per_bend_def
    try:
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        if not rows: return setup_def, sec_per_bend_def
        header_map = {k.lower(): k for k in rows[0].keys()}
        cn = next((header_map[k] for k in ["operation","opname","name","operation_name","op_name","label"] if k in header_map), None)
        csetup = next((header_map[k] for k in ["setup_min","setup","setup_time_min","setup_minutes"] if k in header_map), None)
        csecop = next((header_map[k] for k in ["sec_per_op","time_sec_per_op","runtime_per_op_sec","sec_per_bend"] if k in header_map), None)
        ctime = next((header_map[k] for k in ["time_sec","runtime_sec","time_seconds"] if k in header_map), None)
        for r in rows:
            name = str(r.get(cn, "") if cn else "").strip().lower()
            if name == "form":
                if csetup:
                    try: setup_def = float(str(r.get(csetup,"")).strip() or setup_def)
                    except Exception: pass
                if csecop:
                    try: sec_per_bend_def = float(str(r.get(csecop,"")).strip() or sec_per_bend_def)
                    except Exception: pass
                elif ctime:
                    try:
                        val = float(str(r.get(ctime,"")).strip())
                        if val > 0: sec_per_bend_def = val
                    except Exception: pass
                break
    except Exception:
        return setup_def, sec_per_bend_def
    return setup_def, sec_per_bend_def

def ensure_form_op_with_bends(rows: List[Dict], bends: int) -> List[Dict]:
    """Ensure a 'Form' operation exists and has # of Ops = bends."""
    from logic.ops import resequenced  # local import to avoid cycles
    setup_def, sec_per_bend = get_form_defaults_from_csv()
    idx_form = next((i for i, r in enumerate(rows) if str(r.get("operation","")).strip().lower() == "form"), None)
    if idx_form is None:
        idx_laser = next((i for i, r in enumerate(rows) if str(r.get("operation","")).strip().lower() == "laser"), None)
        idx_plan  = next((i for i, r in enumerate(rows) if str(r.get("operation","")).strip().lower() == "plan"), None)
        ins_at = (idx_laser + 1) if idx_laser is not None else ((idx_plan + 1) if idx_plan is not None else len(rows))
        new_row = {
            "operation": "Form",
            "setup_min": setup_def,
            "ops": max(int(bends), 0),
            "time_sec": max(int(round(sec_per_bend * max(int(bends), 0))), 0),
            "cost_per_part": 0.0,
        }
        rows = rows[:ins_at] + [new_row] + rows[ins_at:]
    else:
        row = dict(rows[idx_form])
        row.setdefault("setup_min", setup_def)
        row["ops"] = max(int(bends), 0)
        row["time_sec"] = max(int(round(sec_per_bend * max(int(bends), 0))), 0)
        rows[idx_form] = row
    return resequenced(rows)
