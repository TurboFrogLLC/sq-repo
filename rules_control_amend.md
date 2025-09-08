===== AMENDMENTS TO rules_control.txt =====

[GLOBAL] – DEV MODE STATUS  
→ DEV_MODE = DISABLED (permanent)

[SSX000] – USER AUTHENTICATION  
• Remove Developer Mode tier (`flawswatter`)  
• All dev-only privileges disabled; no hidden overrides  
• Default username if auth OFF = "anonymous"

[SSX002.B] – GPT OUTSIDE PROCESS INFERENCE  
• STRUCK. GPT may not autofill outside processes.  
• All OPs must come from CAD/PDF parsing or overlay session edits.

[SEC001.B] – DEV FEATURE LOCKOUT  
• Expanded: All developer-only features (markup override, raw memory injection, cost multipliers) are DISABLED for all tiers.

[NEW] – SESSION OVERLAY CONTROL  
• Masters (CSV) = read-only.  
• Overlays = session-only upserts/deletes by primary key:  
   – Materials: `Material` + `Thickness(in)`  
   – Operations: `Operation Name`  
   – Hardware: `Part Number`  
   – OutsideProcess: `Process Name` + `Spec`  
   – Rates: single-record overlay (upsert only)  
• Effective dataset = overlays ∪ (masters \ deletes).  
• Reset Session clears overlays only.

[NEW] – SNAPSHOT EMBEDDING  
• Export must append JSON block:  
  – Schema: `csv-overlay-1`  
  – Includes overlay counts and session mutations  
  – Location: after main `quote_metadata` in PDF/TXT appendix  
