# logic/quote_utils.py
"""
Quote utility functions migrated from frontend_main.py
"""

import datetime as dt
import re
from typing import Dict, Any, Optional

QNUM_RE = re.compile(r"^SQ-\d{8}-\d{3,}$")

def auto_quote_number() -> str:
    """Generate automatic quote number"""
    base = dt.datetime.now().strftime("SQ-%Y%m%d")
    # In Taipy, we'll need to track this differently
    # For now, return a simple format
    return f"{base}-001"

def validate_quote_number(qnum: str) -> bool:
    """Validate quote number format"""
    return bool(QNUM_RE.match(qnum.strip()))

def normalize_quote_metadata(quote: Dict[str, Any]) -> None:
    """Normalize quote metadata fields"""
    quote.setdefault("quote_number", auto_quote_number())
    quote.setdefault("customer", "")
    quote.setdefault("part_number", "")
    quote.setdefault("description", "")

    if "thickness" in quote and "thickness_in" not in quote:
        m = re.search(r"([0-9]*\.?[0-9]+)", str(quote["thickness"]))
        if m:
            try:
                quote["thickness_in"] = float(m.group(1))
            except Exception:
                quote["thickness_in"] = None

    fs = quote.get("flat_size_in")
    if isinstance(fs, dict):
        fs.setdefault("width", None)
        fs.setdefault("height", None)
    else:
        quote["flat_size_in"] = {"width": None, "height": None}

    if "outside_process" in quote and "outside_processes" not in quote:
        quote["outside_processes"] = quote.get("outside_process") or []

    quote.setdefault("outside_processes", quote.get("outside_processes", []))
    quote.setdefault("hardware", quote.get("hardware", []))
    quote.setdefault("material", "")
    quote.setdefault("bend_count", None)

def format_hardware(hw: Dict[str, Any]) -> str:
    """Format hardware entry for display"""
    if not isinstance(hw, dict):
        return str(hw)
    t = hw.get("type", hw.get("part", "HW"))
    q = hw.get("qty_per_part", hw.get("qty", ""))
    return f'{t} x{q}' if q not in ("", None) else f'{t}'

def format_outside_process(op: Dict[str, Any]) -> str:
    """Format outside process entry for display"""
    if not isinstance(op, dict):
        return str(op)
    return op.get("label") or op.get("name") or "Outside Process"