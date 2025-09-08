# logic/pricing.py
"""
Pricing calculation logic for ShopQuote Taipy
Migrated from original Streamlit implementation
"""

from typing import List, Dict, Any, Tuple
import math

def _safe_num(v: Any, as_int: bool = False) -> float:
    """Safe numeric conversion"""
    try:
        x = float(v)
        if as_int:
            return int(x)
        return x
    except Exception:
        return 0.0

def _op_cost_per_part(row: Dict[str, Any], rates: Dict[str, float], qty: int) -> float:
    """Calculate cost per part for an operation"""
    qty = max(int(qty or 1), 1)
    setup_min = _safe_num(row.get("setup_min"))
    time_sec = _safe_num(row.get("time_sec"))
    runtime_min = time_sec / 60.0
    setup_cpp = (setup_min * rates["setup"]) / qty
    run_cpp = runtime_min * (rates["labor"] + rates["machine"])
    return round(setup_cpp + run_cpp, 4)

def _collect_adders_per_part(quote: Dict[str, Any]) -> Tuple[float, Dict[str, float]]:
    """Collect hardware and outside process costs"""
    hw_sum = 0.0
    for hw in (quote.get("hardware") or []):
        if not isinstance(hw, dict):
            continue
        qty = _safe_num(hw.get("qty_per_part") or hw.get("qty") or 1, as_int=True) or 1
        unit = (_safe_num(hw.get("unit_cost"))
                or _safe_num(hw.get("cost_per_part"))
                or _safe_num(hw.get("price"))
                or _safe_num(hw.get("unit_price")))
        hw_sum += qty * unit

    op_sum = 0.0
    for opx in (quote.get("outside_processes") or []):
        if not isinstance(opx, dict):
            continue
        unit = (_safe_num(opx.get("unit_cost_per_part"))
                or _safe_num(opx.get("cost_per_part"))
                or _safe_num(opx.get("price"))
                or _safe_num(opx.get("unit_price")))
        op_sum += unit

    total = round(hw_sum + op_sum, 4)
    return total, {"Hardware": round(hw_sum, 4), "Outside Process": round(op_sum, 4)}

def compute_pricing_table(ops: List[Dict[str, Any]],
                         quote: Dict[str, Any],
                         rates: Dict[str, float],
                         quantities: List[int],
                         markup_percent: float) -> Tuple[dict, dict]:
    """
    Compute complete pricing table for quote breakdown

    Returns:
        (table_data, summary)
    """
    quantities = [max(int(q or 1), 1) for q in (quantities or [1, 10, 25, 50])]

    # Aggregate setup and runtime
    total_setup_min = sum((_safe_num(r.get("setup_min")) for r in ops), 0.0)
    runtime_per_part = sum(((_safe_num(r.get("time_sec")) / 60.0) * (rates["labor"] + rates["machine"])) for r in ops)

    # Hardware and outside process data
    hw_items = []
    for hw in (quote.get("hardware") or []):
        if not isinstance(hw, dict):
            continue
        typ = (str(hw.get("type") or hw.get("part") or "HW")).strip() or "HW"
        per_part_qty = _safe_num(hw.get("qty_per_part") or hw.get("qty") or 1, as_int=True) or 1
        unit = (_safe_num(hw.get("unit_cost")) or
                _safe_num(hw.get("cost_per_part")) or
                _safe_num(hw.get("price")) or
                _safe_num(hw.get("unit_price")))
        if unit <= 0:
            continue
        hw_items.append((f"HW-[{typ}({per_part_qty})]", per_part_qty, unit))

    op_items = []
    for opx in (quote.get("outside_processes") or []):
        if not isinstance(opx, dict):
            continue
        raw = (opx.get("label") or opx.get("name") or opx.get("process") or "Outside Process")
        unit = (_safe_num(opx.get("unit_cost_per_part")) or
                _safe_num(opx.get("cost_per_part")) or
                _safe_num(opx.get("price")) or
                _safe_num(opx.get("unit_price")))
        if unit <= 0:
            continue
        op_items.append((f"OP-[{str(raw).strip()}]", unit))

    # Build table data
    table_data = {}

    # Setup: one-time per job
    setup_ext = total_setup_min * rates["setup"]
    table_data["Setup"] = {qv: round(setup_ext, 2) for qv in quantities}

    # Runtime: per-part cost × qty
    table_data["Runtime"] = {qv: round(runtime_per_part * qv, 2) for qv in quantities}

    # HW and OP rows
    for label, per_part_qty, unit in hw_items:
        table_data[label] = {qv: round(per_part_qty * unit * qv, 2) for qv in quantities}

    for label, unit in op_items:
        table_data[label] = {qv: round(unit * qv, 2) for qv in quantities}

    # Subtotal (before markup)
    subtotal = {qv: 0.0 for qv in quantities}
    for lbl, vals in table_data.items():
        if lbl in ("Subtotal", "Markup", "Total"):
            continue
        for qv, amt in vals.items():
            subtotal[qv] += amt
    table_data["Subtotal"] = {qv: round(subtotal[qv], 2) for qv in quantities}

    # Markup
    markup_vals = {qv: round(subtotal[qv] * (markup_percent / 100.0), 2) for qv in quantities}
    table_data[f"Markup ({markup_percent:.0f}%)"] = markup_vals

    # Total
    total_vals = {qv: round(subtotal[qv] + markup_vals[qv], 2) for qv in quantities}
    table_data["Total"] = total_vals

    # Summary
    adders_per_part, adders_breakdown = _collect_adders_per_part(quote)
    summary = {
        "quantities": quantities,
        "per_qty_ext_subtotal": {q: round(subtotal[q], 2) for q in quantities},
        "markup_percent": round(markup_percent, 2),
        "per_qty_markup": {q: round(markup_vals[q], 2) for q in quantities},
        "per_qty_grand": {q: round(total_vals[q], 2) for q in quantities},
        "adders_breakdown": adders_breakdown,
    }

    return table_data, summary