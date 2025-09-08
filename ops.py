# logic/ops.py
from __future__ import annotations
from typing import List, Dict, Optional

def resequenced(rows: List[Dict]) -> List[Dict]:
    out = []
    for i, r in enumerate(rows, start=1):
        rr = dict(r)
        rr["seq"] = i
        out.append(rr)
    return out

def move(rows: List[Dict], idx: int, delta: int) -> List[Dict]:
    j = idx + delta
    if j < 0 or j >= len(rows):
        return rows
    rows[idx], rows[j] = rows[j], rows[idx]
    return resequenced(rows)

def insert(rows: List[Dict], idx: int, where: str) -> List[Dict]:
    blank = {"operation": "", "setup_min": 0, "ops": 1, "time_sec": 0, "cost_per_part": 0.0, "op_detail": None}
    ins_idx = idx if where == "above" else idx + 1
    rows = rows[:ins_idx] + [blank] + rows[ins_idx:]
    return resequenced(rows)

def delete(rows: List[Dict], idx: int) -> List[Dict]:
    del rows[idx]
    return resequenced(rows)

def sanitize_numeric(val: str, as_int: bool = False) -> Optional[float]:
    s = (val or "").strip()
    if s == "":
        return None
    try:
        if as_int:
            return int(float(s))
        return float(s)
    except Exception:
        return None

def is_install(name: str) -> bool:
    return "install" in (name or "").lower()

def is_outsideproc(name: str) -> bool:
    n = (name or "").lower()
    return ("outside" in n and "process" in n)

def collect_row_issues(row: Dict[str, any]) -> List[str]:
    issues = []
    name = (row.get("operation") or "").strip()
    if not name:
        issues.append("Operation name is required.")
    setup = row.get("setup_min", None)
    if setup is None or not isinstance(setup, (int, float)):
        issues.append("＃ Setup [min] must be numeric.")
    ops_cnt = row.get("ops", None)
    if ops_cnt is None or not isinstance(ops_cnt, (int, float)):
        issues.append("＃ of Ops must be an integer.")
    time_sec = row.get("time_sec", None)
    if time_sec is None or not isinstance(time_sec, (int, float)):
        issues.append("Time [sec] must be an integer.")
    if is_install(name) and not row.get("op_detail"):
        issues.append("Select a Hardware Item for Install operation.")
    if is_outsideproc(name) and not row.get("op_detail"):
        issues.append("Select an Outside Process for this operation.")
    return issues

def collect_all_issues(rows: List[Dict[str, any]]) -> Dict[int, List[str]]:
    out: Dict[int, List[str]] = {}
    for i, r in enumerate(rows, start=1):
        probs = collect_row_issues(r)
        if probs:
            out[i] = probs
    return out
