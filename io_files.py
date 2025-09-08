# core/io_files.py
from __future__ import annotations
import os, csv
from typing import List, Optional, Tuple

def candidate_paths(filename: str) -> List[str]:
    return [
        os.path.join(os.path.dirname(__file__), "..", "data", filename),  # when core/… modules are placed
        os.path.join("data", filename),
        filename,
    ]

def candidate_paths_first(filename: str) -> Optional[str]:
    for p in candidate_paths(filename):
        p_norm = os.path.normpath(p)
        if os.path.isfile(p_norm):
            return p_norm
    return None

def load_ops_name_options() -> List[str]:
    path = candidate_paths_first("Operations[UFG]_sQL.csv")
    names: List[str] = []
    if path:
        try:
            with open(path, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                rows = list(reader)
            if rows:
                header_map = {k.lower(): k for k in rows[0].keys()}
                col = next((header_map[c] for c in ["operation","opname","name","operation_name","op_name","label"] if c in header_map), None)
                if col:
                    for r in rows:
                        v = str(r.get(col, "")).strip()
                        if v: names.append(v)
        except Exception:
            names = []
    if not names:
        names = [
            "Plan","Laser","Form","Deburr","Weld","Tapping","Hardware Install",
            "Mill","Lathe","Outside Process","Final Insp.","Package"
        ]
    # dedupe preserve order
    seen, out = set(), []
    for n in names:
        if n not in seen:
            out.append(n); seen.add(n)
    return out

def load_hardware_options() -> List[str]:
    path = candidate_paths_first("Hardware[UFG]_sQL.csv")
    out: List[str] = []
    if path:
        try:
            with open(path, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                rows = list(reader)
            if rows:
                header_map = {k.lower(): k for k in rows[0].keys()}
                cols = [c for c in ["part","part_number","hardware","type","name","description","label"] if c in header_map]
                if cols:
                    chosen = header_map[cols[0]]
                    for r in rows:
                        v = str(r.get(chosen, "")).strip()
                        if v: out.append(v)
        except Exception:
            out = []
    return sorted(set(out or ["— none found —"]))

def load_outsideproc_options() -> List[str]:
    path = candidate_paths_first("OutsideProcess[UFG]_sQL.csv")
    out: List[str] = []
    if path:
        try:
            with open(path, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                rows = list(reader)
            if rows:
                header_map = {k.lower(): k for k in rows[0].keys()}
                cols = [c for c in ["label","name","process","operation","op","outside_process"] if c in header_map]
                if cols:
                    chosen = header_map[cols[0]]
                    for r in rows:
                        v = str(r.get(chosen, "")).strip()
                        if v: out.append(v)
        except Exception:
            out = []
    return sorted(set(out or ["— none found —"]))

def load_rates_once(default_setup: float, default_labor: float, default_machine: float) -> Tuple[float, float, float]:
    path = candidate_paths_first("Rates[UFG]_sQL.csv")
    if not path:
        return default_setup, default_labor, default_machine
    setup, labor, machine = default_setup, default_labor, default_machine
    try:
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        if not rows:
            return setup, labor, machine
        direct = {k.lower(): k for k in rows[0].keys()}
        def col(*opts):
            for o in opts:
                if o.lower() in direct: return direct[o.lower()]
            return None
        c_setup = col("SetupRatePerMin","setup_rate_per_min","setup_rate")
        c_labor = col("LaborRatePerMin","labor_rate_per_min","labor_rate")
        c_machine = col("MachineRatePerMin","machine_rate_per_min","machine_rate")

        def first_float(cn):
            if not cn: return None
            for r in rows:
                try: return float(str(r.get(cn, "")).strip())
                except Exception: pass
            return None

        s = first_float(c_setup); l = first_float(c_labor); m = first_float(c_machine)
        if s is None or l is None or m is None:
            for r in rows:
                low = {k.lower(): str(v).strip() for k, v in r.items()}
                key = low.get("type") or low.get("name") or low.get("rate_type")
                val = low.get("value") or low.get("rate") or low.get("amount")
                if key and val:
                    try: fv = float(val)
                    except Exception: continue
                    if "setup" in key and s is None: s = fv
                    elif "labor" in key and l is None: l = fv
                    elif "machine" in key and m is None: m = fv
        setup = s if s is not None else setup
        labor = l if l is not None else labor
        machine = m if m is not None else machine
        return float(setup), float(labor), float(machine)
    except Exception:
        return default_setup, default_labor, default_machine
