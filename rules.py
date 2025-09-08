# core/rules.py
from __future__ import annotations
from typing import List, Tuple, Optional

# Material densities (lb/in^3)
DENSITY = {
    "CRS": 0.2840, "HRS": 0.2840, "SS": 0.2890, "STAINLESS": 0.2890, "STEEL": 0.2840,
    "ALUMINUM": 0.0975, "AL": 0.0975, "COPPER": 0.3230, "BRASS": 0.3070,
}

FERROUS_MATERIALS = {"CRS", "HRS", "SS", "STAINLESS", "STEEL"}

# Reference thickness set (inches) with optional gauge labels
THICKNESS_BASE: List[Tuple[float, Optional[str]]] = [
    (0.0478, "18GA"),
    (0.0598, "16GA"),
    (0.0747, "14GA"),
    (0.0900, "13GA"),
    (0.1250, None),
]

MATERIAL_CHOICES = ["CRS", "ALUMINUM", "SS", "COPPER", "BRASS", "HRS"]

def _inch_3(x: float) -> float:
    return float(f"{x:.3f}")

def thickness_choices_for(material: str) -> List[Tuple[str, float]]:
    """(Main UI) ferrous shows GA [inch], non-ferrous shows inch only."""
    is_ferrous = material and material.upper() in FERROUS_MATERIALS
    out: List[Tuple[str, float]] = []
    for inch, ga in THICKNESS_BASE:
        inch3 = _inch_3(inch)
        inch_str = f'{inch3:.3f}"'
        label = f"{ga} [{inch_str}]" if (is_ferrous and ga) else inch_str
        out.append((label, float(inch)))
    return out

def thickness_labels_for_units(material: str, units: str) -> List[Tuple[str, float]]:
    """(Estimator) in 'mm' mode show mm first: e.g., 3.00 mm [0.118"]."""
    base = thickness_choices_for(material)
    if units == "in":
        return base
    out: List[Tuple[str, float]] = []
    for lbl, inch in base:
        mm = inch * 25.4
        mm_str = f"{mm:.2f} mm"
        out.append((f"{mm_str} [{inch:.3f}\"]", inch))
    return out
