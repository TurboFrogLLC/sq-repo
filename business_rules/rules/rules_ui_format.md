===== SHOPQUOTE — UI LAYOUT SPEC (Advisory; Non-Mandatory) =====
Purpose: Provide a consistent, mouse-driven UI reference for shopQuote. This spec is ADVISORY only.
Nothing in this file is mandatory unless enforced elsewhere (e.g., control/export rules).

RUNTIME MODE
• DEV_MODE = DISABLED (assumed). Dev/debug widgets are not rendered.
• Masters (CSV) are read-only; Settings edits apply to session overlays only.

TAB ORDER (left → right)
1) Part & Ops
2) Quote Breakdown
3) Summary
4) Settings

GLOBAL SIDEBAR (common patterns; IDs may already exist in code)
• Brand header
• Quote # input  → id: in-quote-number  (validated format, e.g., SQ-YYYYMMDD-###)
• Navigation shortcuts (optional): to Part & Ops / Quote Breakdown / Summary / Settings

MAIN PANE — PART & OPS
Inputs (IDs):
• in-customer
• in-part-number
• in-description
• in-markup  → NOT RENDERED when DEV_MODE=DISABLED

Buttons:
• btn-upload-files           (file_uploader or equivalent trigger)
• btn-generate-ops           (derive operation list / summary from inputs & files)
• btn-enter-edit             (“Edit ⚙️ Operations” — toggles Edit Mode)
• btn-generate-quote         (“Generate 📉 Quote” — proceeds to pricing)

Panels (read-only labels; fixed vertical order):
• Part Summary:
  – Customer
  – Part Number (append “Rev. X” inline if present)
  – Material
  – Thickness
  – Flat Size
  – Bends

Operation Breakdown (table headers fixed):
| Seq | Operation | Setup | Setup Cost | # Ops | Time | $/Part |

Edit Mode (modal/inline prompts only; no dev shortcuts):
• Insert / Reorder / Remove prompts match the EMX rules (see ops UI rules).

MAIN PANE — QUOTE BREAKDOWN
Header:
• “📉 Quote Breakdown”

Rules (advisory mirror of QBX spec):
• Fixed tier columns: 1, 10, 25, 50
• Row order (locked elsewhere): Setup → Runtime → HW[…] → OP[…] → Subtotal → Markup (N%) → Total
• Currency display: $X.XX
• No extra rows/columns rendered in this view

MAIN PANE — SUMMARY
Header:
• “📌 Summary”

Contents:
• Customer, Part Number, Description
• Final per-part totals for 1/10/25/50 (after markup)

Actions:
• btn-save-quote
• btn-new-quote
• btn-quit-session

SETTINGS TAB (session overlay model)
Sidebar (top → bottom):
• Brand header
• Quote # (in-quote-number)
• Select Database (dropdown): Materials | Operations | Hardware | Outside Process | Rates
• Session Settings group:
  – Load Session (import overlay snapshot: csv-overlay-1)
  – Save Session (export overlay snapshot: csv-overlay-1)
  – Reset Session (clears overlays ONLY — preserves current quote)
• “Go to…” shortcuts:
  – 🆕 New Quote
  – ↩️ Part & Ops
  – ↩️ Quote Breakdown
  – ↩️ Summary

Main Pane behavior:
• Show only the selected database table (effective view = masters ∪ overlays \ deletes)
• Actions:
  – Add (creates overlay upsert)
  – Edit (updates overlay upsert by PK)
  – Delete (adds PK to overlay_deletes; not allowed for Rates)
• Primary Keys:
  – Materials: Material + Thickness(in)
  – Operations: Operation Name
  – Hardware: Part Number
  – Outside Process: Process Name + Spec
  – Rates: single-record overlay (no deletes; upsert only)

EXPORT APPENDIX (advisory note)
• Saved TXT/PDF include:
  – METADATA SNAPSHOT block (quote_metadata)
  – OVERLAY SNAPSHOT block (version: csv-overlay-1), appended after metadata

DEV/DEBUG WIDGET POLICY
• When DEV_MODE=DISABLED:
  – Hide any debug sliders, raw math inputs, or markup overrides
  – Do not expose hidden fields via querystring or keyboard shortcuts
