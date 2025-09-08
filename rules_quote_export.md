===== SUB_BLOCK: [QBX000] – QUOTE BREAKDOWN TABLE CONTROL ===== 
 
[QBX000.A] – QUOTE BREAKDOWN TABLE FORMAT  
Status: ENFORCED  
Dependencies: —  
Applies To: GPT Instructions, CSV Schema, Backend Parser, Edit Mode, Simulation Output  
Rule Scope: Output Table + Display Rules  
Description:  
Controls the layout, content, and order of the Quote Breakdown table shown to users. All values are rendered per quantity tier using fixed columns and row rules.

📉 Table Layout:  
|        | 1     | 10    | 25    | 50    |
|--------|-------|-------|-------|-------|
| Setup  | $X.XX | $X.XX | $X.XX | $X.XX |
| Runtime| $X.XX | $X.XX | $X.XX | $X.XX |
| HW-[Type(qty)] | $X.XX | $X.XX | $X.XX | $X.XX |
| OP-[Process]   | $X.XX | $X.XX | $X.XX | $X.XX |
| Subtotal | $X.XX | $X.XX | $X.XX | $X.XX |
| Markup (35%) | $X.XX | $X.XX | $X.XX | $X.XX |
| Total   | $X.XX | $X.XX | $X.XX | $X.XX |

Formatting Rules:  
• Columns = fixed quantities: 1, 10, 25, 50  
• Row order is hardcoded — may not be re-ordered or customized  
• `HW` and `OP` rows may be omitted if no content  
• All other rows (Setup → Total) must always appear  
• Label format:  
 → HW row: `HW-[PartNumber(qty)]`  
 → OP row: `OP-[Process]`  
• Do not include specs (e.g., MIL-A) in OP labels  
• All dollar values must display as `$X.XX`  

Purpose:  
Locks visual formatting and structural behavior of quote breakdown display. Prevents row drift, unit ambiguity, or formatting substitutions.

Source: SubProg_[QBX]_REF_only.txt  
Validated In: QBX Table Render Sim v1.0  

---

[QBX000.B] – COST SOURCE ENFORCEMENT  
Status: ENFORCED  
Dependencies: —  
Applies To: GPT Instructions, CSV Schema, Backend Parser, Edit Mode, Simulation Output  
Rule Scope: Table Calculation Logic  
Description:  
Controls all numeric values rendered in the Quote Breakdown table. Each value must be computed directly from `quote_metadata`.

Enforcement Rules:  
• Quote metadata is immutable and isolated at display time  
• All tiered values must be calculated per part — not batch  
• Math must use file-defined rates and static logic only  
• Each row type uses the following:

– Setup:  
 → `(setup_minutes_total ÷ 60 × $75) ÷ Qty`

– Runtime:  
 → `(runtime_seconds_total ÷ 3600) × $75` (labor ops)  
 → or `$250` if machine-op pre-resolved

– HW rows:  
 → Unit cost × install quantity (from `hardware[]`)  
 → Per-part cost — not multiplied by quantity tier

– OP rows:  
 → Flat cost per part (from `outside_processes[]`)

– Subtotal:  
 → Sum of all above row values

– Markup:  
 → `Subtotal × (markup_percent ÷ 100)`

– Total:  
 → `Subtotal + Markup`

Restrictions:  
• No fallback logic, interpolation, or chaining allowed  
• $0.00 values are permitted where logic resolves to zero  
• All results must round to two decimal places post-calculation  

Purpose:  
Ensures all quote output math originates from frozen memory snapshot. Blocks dynamic computation or GPT speculation.

Source: SubProg_[QBX]_REF_only.txt  
Validated In: Quote Snapshot Isolation Audit v2.0  

---

[QBX000.C] – ROW PRESENCE + LABEL LOGIC  
Status: ENFORCED  
Dependencies: [QBX000.A], [QBX000.B]  
Applies To: GPT Instructions, CSV Schema, Backend Parser, Edit Mode, Simulation Output  
Rule Scope: Row suppression, label formatting  
Description:  
Controls conditional row display and label format behavior.

Rules:  
• Setup, Runtime, Subtotal, Markup, Total → always shown  
• HW and OP rows → only shown if corresponding block is non-empty  
• All rows must use `$X.XX` format  
• No alternate wording, punctuation, or ordering permitted  
• Label casing and punctuation must match spec exactly  
• HW and OP rows must appear together in row groupings if present  
• Table must never contain fewer than 5 rows

Purpose:  
Preserves structural integrity and visual uniformity across quote tables.

Source: SubProg_[QBX]_REF_only.txt  
Validated In: QBX Display Filter Sim v1.7  

===== END_SUB_BLOCK: [QBX000] =====
---
===== SUB_BLOCK: [QBX001] – QUOTE BREAKDOWN TABLE TRIGGER =====  

[QBX001.A] – TABLE RENDER TRIGGER  
Status: ENFORCED  
Dependencies: —  
Applies To: GPT Instructions, CSV Schema, Backend Parser, Edit Mode, Simulation Output  
Rule Scope: Table invocation, snapshot validation  
Description:  
Controls when the Quote Breakdown table is allowed to render. Execution depends on the presence and validity of a finalized `quote_metadata` object.

Trigger Conditions:  
• If `quote_metadata` exists and passes schema validation:  
 → Begin rendering the Quote Breakdown table  
 → Include all required rows: Setup, Runtime, Subtotal, Markup, Total  
 → Conditionally include HW and OP rows if relevant data is present  
 → No substitutions or structural overrides permitted  

• If `quote_metadata` is missing or invalid:  
 → Display message:  
 > ⚠️ No quote data available. Type R to reload.  
 → If user types `R` (case-insensitive):  
  ↳ Restore last valid quote snapshot and freeze it  
 → If user does not respond → rendering is halted  

Enforcement Rules:  
• No quote table may render without valid `quote_metadata`  
• No GPT fallback, memory recomputation, or file guessing allowed  
• Reload is terminal — no in-place editing or patching permitted  

Compatibility Notes:  
• Allows regeneration from saved TXT/PDF quote files with valid metadata  
• Trigger must execute before any summary view, totals, or export is displayed  

Purpose:  
Guarantees that all quote outputs are driven by valid, immutable memory objects. Prevents contamination from inferred or partial quote states.

Source: SubProg_[QBX]_REF_only.txt  
Validated In: Snapshot Load Test v3.0  

===== END_SUB_BLOCK: [QBX001] =====
---
===== SUB_BLOCK: [QBX002] – MARKUP OVERRIDE (DEV ONLY) =====
  
[QBX002.A] – MARKUP OVERRIDE HANDLER  
Status: ENFORCED  
Dependencies: —  
Applies To: GPT Instructions, CSV Schema, Backend Parser, Edit Mode, Simulation Output  
Rule Scope: Markup substitution, developer-only access  
Description:  
Allows developer-tier users to override the default markup percentage applied in the Quote Breakdown table. Overrides are applied directly to the `markup_percent` field in `quote_metadata`.

Trigger Conditions:  
• User has access tier = `flawswatter`  
• User enters a valid override command (markup value)  
 → Acceptable values: whole numbers between 0–100  

Behavior:  
• Override is applied before any totals are rendered  
• Markup row label must reflect new value:  
 → `Markup (XX%)`  
• All calculations are re-evaluated using new percent  
• Override is session-bound and does not persist after export  

Restrictions:  
• Overrides are locked to developer-tier users only  
• If user is not `flawswatter` → override is silently ignored  
• No chaining, multiplication, or conditional logic allowed  
• Override is not shown in non-dev sessions  
• Final markup row must always be displayed  

Purpose:  
Enables controlled markup testing for developers without exposing logic to regular users.

Source: SubProg_[QBX]_REF_only.txt  
Validated In: Developer Override Sim v2.1  

===== END_SUB_BLOCK: [QBX002] =====
---
===== SUB_BLOCK: [QBX003] – 📌 SUMMARY VIEW =====  

[QBX003.A] – QUOTE SUMMARY BLOCK: VERTICAL LAYOUT FORMAT  
Status: ENFORCED  
Dependencies: —  
Applies To: GPT Instructions, CSV Schema, Backend Parser, Edit Mode, Simulation Output  
Rule Scope: Summary content layout, pricing tier display, final quote prompt  
Description:  
Defines the vertical format of the final summary view shown after the Quote Breakdown. Displays key part identifiers and final per-part pricing for all fixed quantity tiers.

Summary Layout:  
📌 Summary View  
Customer: [value]  
Part number: [value]  
Description: [value]  

💲 Quote Totals  
- Qty 1: $X.XX  
- Qty 10: $X.XX  
- Qty 25: $X.XX  
- Qty 50: $X.XX  

→ Type [ s ] to Save Quote  
→ Type [ n ] to Start New Quote  
→ Type [ q ] to Quit

Rendering Rules:  
• All fields must come from `quote_metadata`  
• Quote Totals must reflect final per-part cost at each quantity tier (after markup)  
• Fixed tier set: 1, 10, 25, 50 — no substitutions allowed  
• No batch pricing, extended totals, or alternative summaries permitted  
• Only these three metadata fields are shown: Customer, Part number, Description  
• Save/Start/Quit prompts must appear in exact format and order  
• Summary must not display if Quote Breakdown fails to render  

Purpose:  
Locks the final summary output to a fixed visual layout and trusted input source. Prevents ambiguous totals or structural drift.

Source: SubProg_[QBX]_REF_only.txt  
Validated In: Summary Display Conformance Audit v2.3  

===== END_SUB_BLOCK: [QBX003] =====
---
===== SUB_BLOCK: [QBX004] – METADATA EXPORT ===== 
 
[QBX004.A] – QUOTE METADATA EMBED / ATTACH LOGIC  
Status: ENFORCED  
Dependencies: —  
Applies To: GPT Instructions, CSV Schema, Backend Parser, Edit Mode, Simulation Output  
Rule Scope: Metadata persistence, quote recall, cross-mode continuity  
Description:  
Controls how finalized quote metadata is embedded or attached during export operations (TXT and PDF). The metadata must be a raw JSON snapshot of the quoting state.

Export Behavior:  
• On `Save Quote` trigger:  
 → Append `quote_metadata` object to the end of the export file  
 → Wrap metadata in delimiters:  
  `=== METADATA SNAPSHOT START ===`  
  {... JSON content ...}  
  `=== METADATA SNAPSHOT END ===`

Rules:  
• Format must be machine-readable and JSON-valid  
• User must not see the metadata during save  
• Metadata must reflect **exactly** what was used in pricing  
• Edits, overrides, or injected values must appear in metadata  
• Applies equally to `.txt` and `.pdf` exports  
• No obfuscation, compression, or transformation allowed  

Purpose:  
Enables future quote recall and auditability by embedding complete quoting context directly in export files.

Source: SubProg_[QBX]_REF_only.txt  
Validated In: Metadata Export Recovery Test v1.0  

---

[QBX004.B] – METADATA FIELD STRUCTURE  
Status: ENFORCED  
Dependencies: —  
Applies To: GPT Instructions, CSV Schema, Backend Parser, Edit Mode, Simulation Output  
Rule Scope: Field names, types, export structure definition  
Description:  
Defines the required structure of the `quote_metadata` object embedded in export files.

Required Fields:
```json
{
  "customer": "Acme Corp",
  "part_number": "BRKT-001",
  "description": "Left-hand mounting bracket",
  "material": "CRS",
  "thickness": "16 GA (0.060 in)",
  "flat_size": "3.25 × 6.50 in",
  "operations": [
    {
      "seq": 1,
      "operation": "Laser",
      "setup_min": 2,
      "num_ops": 1,
      "runtime_sec": 8,
      "cost_per_part": 0.27
    }
  ],
  "hardware": [
    {
      "type": "CLS-440-2",
      "qty_per_part": 2,
      "unit_cost": 0.10
    }
  ],
  "outside_processes": [
    {
      "label": "Anodize – Black",
      "unit_cost_per_part": 0.74
    }
  ],
  "setup_total_min": 8,
  "runtime_total_sec": 64,
  "markup_percent": 35,
  "totals": {
    "1": 12.43,
    "10": 4.81,
    "25": 2.75,
    "50": 1.94
  }
}
Restrictions:
• No fields may be renamed, omitted, or inferred
• Field values must match the runtime quote session
• This snapshot must be frozen at the time of export
Purpose:
Ensures all exported quotes carry a complete, verifiable trace of how pricing was calculated.

Source: SubProg_[QBX]_REF_only.txt
Validated In: Quote State Replay Test v2.4

===== END_SUB_BLOCK: [QBX004] =====

===== SUB_BLOCK: [PDF000] – PDF FORMAT SCORE CALCULATOR ===== 
 
[PDF000.A] – FORMAT SCORE CALCULATION  
Status: ENFORCED  
Dependencies: —  
Applies To: GPT Instructions, CSV Schema, Backend Parser, Edit Mode, Simulation Output  
Rule Scope: File Scoring  
Description:  
Each uploaded PDF must be scored based on its extractability and formatting consistency. The resulting value is a float between `0.00` and `1.00`, called `pdf_format_score`.

Scoring Inputs:  
• Presence of text layer (searchable text)  
• Detection of bounding boxes around fields  
• OCR fallback presence  
• Field density and positional structure  
• Header/footer detection (non-BOM text)  

Formula (weighted):  
• +0.4 = contains searchable text layer  
• +0.2 = bounding boxes detected  
• +0.2 = field positioning is grid-aligned  
• +0.1 = OCR fallback usable  
• +0.1 = header/footer density acceptable  
• Total is capped at 1.00  

Behavior:  
• The score is computed at file import time  
• Stored in session memory as `pdf_format_score`  
• Immutable after evaluation  

Purpose:  
Quantifies the structural quality of uploaded PDFs. Used to control downstream fallback behavior for OCR and parsing.

Source: SubProg_[PDF]_REF_only.txt  
Validated In: PDF Extractability Benchmark Sim v2.1  

---

[PDF000.B] – FORMAT SCORE USAGE + LOCKOUT  
Status: ENFORCED  
Dependencies: [PDF000.A]  
Applies To: GPT Instructions, CSV Schema, Backend Parser, Edit Mode, Simulation Output  
Rule Scope: OCR and Field Trust Enforcement  
Description:  
Controls how `pdf_format_score` is applied in logic. Sets thresholds for whether OCR or fallback field data can be used.

Rules:  
• If `pdf_format_score ≥ 0.5`:  
 → OCR fields may be trusted  
 → Fallback to `ocr_data[field]` is permitted if all structured sources fail  
• If `pdf_format_score < 0.5`:  
 → OCR fields must be discarded  
 → Fallback fields may not be displayed or injected  

Restrictions:  
• No memory or GPT-derived patching allowed  
• Fields extracted under lockout conditions must be flagged and excluded  
• The score must be checked explicitly in logic before fallback is attempted  

Purpose:  
Guarantees that fallback parsing (especially from OCR) is only used when structural quality meets a minimum standard.

Source: SubProg_[PDF]_REF_only.txt  
Validated In: OCR Lockout Gatekeeper Test v1.0  

===== END_SUB_BLOCK: [PDF000] =====
---
===== SUB_BLOCK: [PDF001] – TITLE BLOCK PARSER ===== 
 
[PDF001.A] – FIELD DETECTION FROM PDF TITLE BLOCK  
Status: ENFORCED  
Dependencies: —  
Applies To: GPT Instructions, CSV Schema, Backend Parser, Edit Mode, Simulation Output  
Rule Scope: PDF Parsing  
Description:  
Scans structured PDF title blocks for common part metadata. Populates fields using visible, aligned labels.

Parsed Fields:  
• Customer  
• Part Number  
• Revision  
• Material  
• Thickness  
• Description  

Detection Logic:  
• Keys must be visually aligned with values  
• Keys must match known patterns (e.g., “Material”, “Part #”)  
• Must appear within bounding box of title block region  
• Parsing order: vertical → left-to-right  
• Each detected key-value pair is stripped, normalized, and stored  

Restrictions:  
• Values must not span multiple lines  
• No inference or guesswork allowed  
• OCR is permitted only if `pdf_format_score ≥ 0.5`  

Purpose:  
Extracts structured part metadata from title blocks in engineering drawings.

Source: SubProg_[PDF]_REF_only.txt  
Validated In: Title Block Field Extractor Test v2.3  

===== END_SUB_BLOCK: [PDF001] =====
---
===== SUB_BLOCK: [PDF002] – OUTSIDE PROCESS PARSER ===== 
 
[PDF002.A] – OUTSIDE PROCESS EXTRACTION FROM PDF  
Status: ENFORCED  
Dependencies: —  
Applies To: GPT Instructions, CSV Schema, Backend Parser, Edit Mode, Simulation Output  
Rule Scope: PDF Parsing  
Description:  
Scans PDF files for outside process instructions using structured text and callout detection.

Detection Sources:  
• BOM notes section  
• Finish block in title area  
• General notes (e.g., “Anodize per MIL-A…”)

Matching Logic:  
• Keyword match required:  
 → “Anodize”, “Silk Screen”, “Powdercoat”, “Chemfilm”, etc.  
• Matched phrases must include a recognized finish or coating  
• Optional spec parsing if phrase includes:  
 → “MIL-”, “RoHS”, “Type II”, “Black”, etc.  

Spec Handling:  
• If matched against `OutsideProcess[UFG]_sQL.csv`, store as structured OP row  
• If unmatched, store as `"Outside Process – [Raw Phrase]"` with `$0.00` fallback  
• No formatting applied beyond sanitization  
• Each OP inserted into `outside_processes[]` list in `quote_metadata`  

Fallback Enforcement:  
• If `pdf_format_score < 0.5` → discard all matches  
• No memory, alias inference, or GPT expansion permitted  

Purpose:  
Allows deterministic extraction of finishing and outsourced processes directly from engineering PDFs.

Source: SubProg_[PDF]_REF_only.txt  
Validated In: PDF Process Extractor Suite v3.0  

===== END_SUB_BLOCK: [PDF002] =====


