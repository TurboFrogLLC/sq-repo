===== SUB_BLOCK: [PSX001] – PART SUMMARY CONSTRUCTION =====  
[PSX001.A] – FIELD PARSING ENFORCEMENT  
Status: ENFORCED  
Dependencies: —  
Applies To: GPT Instructions, CSV Schema, Backend Parser, Edit Mode, Simulation Output  
Rule Scope: File Parsing  
Description:  
All part metadata must be extracted using a fixed, deterministic hierarchy based on file type availability. No substitutions, memory reuse, or inference is allowed.

FIELD PARSING MATRIX:  
• Customer → PDF → DXF → else `UNKNOWN CUSTOMER`  
• Part Number → PDF → Filename → DXF  
• Description → PDF → DXF  
• Material Type → PDF → DXF → CSV match with price  
• Thickness → PDF → STEP → DXF  
• Flat Size → STEP → DXF  
• Weight → Flat Area × Thickness × Material Density  

PATCH – OCR ENFORCEMENT:  
• `ocr_data[field_name]` may only be used if `pdf_format_score ≥ 0.5`  
• OCR fields must originate from `shopquote-api`  
• No GPT inference, substitution, or pattern scanning allowed

PATCH – MATERIAL PRICE ENFORCEMENT:  
• Matched material rows must include a non-null numeric value in `Price per Pound ($)`  
• If price is missing → material is invalidated as `UNKNOWN MATERIAL`

Purpose:  
Ensures all metadata used in quoting is extracted from trusted, structured inputs. Prevents memory reuse or GPT logic injection.

Source: SubProg_[PSX]_REF_only.txt  
Validated In: Parsing Matrix Audit v3.2  

---

[PSX001.B] – UNIT NORMALIZATION  
Status: ENFORCED  
Dependencies: —  
Applies To: GPT Instructions, CSV Schema, Backend Parser, Edit Mode, Simulation Output  
Rule Scope: Output Formatting Only  
Description:  
Controls the display format for thickness and flat size values.

Formatting Rules:  
• `thickness_display`:  
 → Format as `0.060 in` or `16 GA (0.060 in)`  
 → 3 decimal places required  
• `flat_size_display`:  
 → Format as `[width] in × [height] in`  
 → Inches only — no metric units permitted

Purpose:  
Standardizes display rendering for critical dimensions. Prevents unit ambiguity and rounding errors in quote output.

Source: SubProg_[PSX]_REF_only.txt  
Validated In: Display Format Render Test 4.0  

---

[PSX001.C] – EMPTY FIELD LOCKOUT  
Status: ENFORCED  
Dependencies: —  
Applies To: GPT Instructions, CSV Schema, Backend Parser, Edit Mode, Simulation Output  
Rule Scope: Error Handling  
Description:  
If any core field is empty after parsing and fallback, it must be labeled with a deterministic fallback value.

Fallback Values:  
• Customer → `UNKNOWN CUSTOMER`  
• Part Number → `UNDEFINED`  
• Material Type → `UNKNOWN MATERIAL`  
• Thickness → `THICKNESS NOT FOUND`  
• Flat Size → `SIZE UNAVAILABLE`  
• Weight → `—`

Purpose:  
Prevents blank fields in quote UI and reinforces data integrity.

Source: SubProg_[PSX]_REF_only.txt  
Validated In: Output Clarity Audit v2  

---

[PSX001.D] – TEXT SANITIZATION  
Status: ENFORCED  
Dependencies: —  
Applies To: GPT Instructions, CSV Schema, Backend Parser, Edit Mode, Simulation Output  
Rule Scope: Post-Parse Filter  
Description:  
All parsed metadata strings must be cleaned of:

• Trailing spaces  
• Line breaks or newline anomalies  
• Tab, slash, or illegal characters (unless valid)  

Purpose:  
Guarantees consistent rendering and formatting integrity for exported quotes.

Source: SubProg_[PSX]_REF_only.txt  
Validated In: PDF Export Clean Test  

---

[PSX001.E] – BEND COUNT + TYPE EXTRACTION  
Status: ENFORCED  
Dependencies: —  
Applies To: GPT Instructions, CSV Schema, Backend Parser, Edit Mode, Simulation Output  
Rule Scope: Geometry Parsing  
Description:  
Extracts two metadata fields for forming classification:

Fields:  
• `bend_count` → Integer, must be ≥ 0  
• `bend_types[]` → Normalized label list, may be empty  

Sources:  
• STEP → curved edge count  
• DXF → `$BENDS`, BEND-LINES, or MTEXT  
• PDF → text pattern `"Bends: [#]"`  

Aliases matched include: `HEM`, `OFFSET`, `ROLL`, `Z_BEND`, `FORM_ONLY`, etc.  
Normalized to uppercase labels without deduplication.

Purpose:  
Supports downstream logic for complexity classification. Fields are internal only.

Source: SubProg_[PSX]_REF_only.txt  
Validated In: Geometry Metadata Isolation Suite 3.2  

---

[PSX001.F] – PART NUMBER + REVISION JOIN LOGIC  
Status: ENFORCED  
Dependencies: —  
Applies To: GPT Instructions, CSV Schema, Backend Parser, Edit Mode, Simulation Output  
Rule Scope: Identity Formatting  
Description:  
If both `part_number` and `revision` are valid, combine them using this format:  
 `[part_number] Rev. [revision]`

Rules:  
• Revision must match: A–Z, A1–Z9, 0.1–9.9, or hybrid (e.g. B5, R1.2)  
• If invalid, discard  
• Do not modify revision — only append to part number  
• Append once only — no chaining  

Examples:  
• "BRKT-42", "B2" → "BRKT-42 Rev. B2"  
• "PLATE-1", null → "PLATE-1"

Purpose:  
Preserves drawing versioning without expanding field count.

Source: SubProg_[PSX]_REF_only.txt  
Validated In: Rev Join Stack v2.0  

---

[PSX001.G] – OCR FIELD INJECTION (SOURCE-RANKED)  
Status: ENFORCED  
Dependencies: —  
Applies To: GPT Instructions, CSV Schema, Backend Parser, Edit Mode, Simulation Output  
Rule Scope: Fallback Input Logic  
Description:  
Allows fallback use of `ocr_data{}` values if all trust and precedence conditions are satisfied.

Injection Conditions:  
• `pdf_format_score ≥ 0.5`  
• STEP/DXF did not resolve field  
• Value is non-null, sanitized, and structurally valid  

Allowed Fields:  
• `part_number`  
• `revision`  
• `material_type`  
• `thickness`  
• `description`

Trace Logging:  
• Each field must record source = `"ocr"`  
• Must log `pdf_format_score` and `file_id`  
• No inference, casing normalization, or patching allowed

Purpose:  
Supports fallback population of core metadata from OCR when geometric sources are incomplete.

Source: SubProg_[PSX]_REF_only.txt  
Validated In: OCR Injection Audit Suite v3.0  

===== END_SUB_BLOCK: [PSX001] =====
---
===== SUB_BLOCK: [PSX002] – PART SUMMARY UI RENDER =====  
[PSX002.A] - PART SUMMARY DISPLAY FORMAT  
Status: ENFORCED  
Dependencies: —  
Applies To: GPT Instructions, CSV Schema, Backend Parser, Edit Mode, Simulation Output  
Rule Scope: Output Formatting  
Description:  
The Part Summary block must render the following fields in fixed vertical order with exact label syntax:

📄 Part Summary  
Customer: [value]  
Part Number: [value]  
Material: [value]  
Thickness: [value]  
Flat Size: [value]  
Bends: [value]

Field Source Logic:  
• All values originate from internal `quote_metadata`  
• `Bends` shows the parsed `bend_count`  
• If `bend_count = 0` or missing → fallback applies

Formatting Rules:  
• `Thickness` must appear in dual-unit format: `[GA] ([in])` if eligible  
• `Flat Size` uses inch-only format: `[X] in × [Y] in`  
• If any field is missing → render fallback symbol

Fallback Handling:  
• Display `—` in place of any invalid, null, or missing value  
• Do not show "0", "None", or blank fields  
• `Bends: —` is used if `bend_count = 0`  

Purpose:  
Enforces clean, consistent display of part metadata in the summary interface. Blocks inference or null leakage.

Source: SubProg_[PSX]_REF_only.txt  
Validated In: PSX Fallback Stress Sim 5.0  

---

[PSX002.B] - GAUGE LABEL RESTRICTION  
Status: ENFORCED  
Dependencies: —  
Applies To: GPT Instructions, CSV Schema, Backend Parser, Edit Mode, Simulation Output  
Rule Scope: Display Filter  
Description:  
The “GA” label may only appear in the `Thickness` field if:

• Material is ferrous steel (e.g. CRS, HRPO, GALV)  
• Gauge is 10 GA or thinner

If either condition fails, show decimal inches only.

Examples:  
• CRS, 16 GA → ✅ `16 GA (0.060 in)`  
• ALUMINUM, 16 GA → ❌ `0.060 in`  
• CRS, 7 GA → ❌ `0.187 in`

Purpose:  
Prevents improper or misleading gauge usage in thickness displays.

Source: SubProg_[PSX]_REF_only.txt  
Validated In: GA Rule Enforcement Batch B3  

---

[PSX002.C] - NULL FIELD FALLBACKS  
Status: ENFORCED  
Dependencies: —  
Applies To: GPT Instructions, CSV Schema, Backend Parser, Edit Mode, Simulation Output  
Rule Scope: Display Fallback  
Description:  
If any parsed field is missing, null, or malformed, display fallback `—` for the affected field.

Affected Fields:  
• Customer  
• Part Number  
• Material  
• Thickness  
• Flat Size  
• Bends

Rules:  
• Never display "None", "0", or leave a field blank  
• Flat Size must either be `X × Y` or `—`  
• Bends = 0 → show `—`  

Purpose:  
Ensures visual consistency and data completeness in the UI display layer.

Source: SubProg_[PSX]_REF_only.txt  
Validated In: PSX Fallback Stress Sim 5.0  

---

[PSX002.D] – DISPLAY FORMATTING FOR REVISION-INLINED PART NUMBERS  
Status: ENFORCED  
Dependencies: —  
Applies To: GPT Instructions, CSV Schema, Backend Parser, Edit Mode, Simulation Output  
Rule Scope: Label Presentation  
Description:  
If both `part_number` and `revision` are valid at render time, show the revision inline as:

 `Part Number: [part_number] Rev. [revision]`

Rules:  
• Append only if `revision` is valid  
• If revision is missing, show `part_number` only  
• No punctuation, line breaks, or hyphens allowed between part number and revision  
• Revision is never shown as a separate field

Examples:  
• part_number = "12345", revision = "B" → `Part Number: 12345 Rev. B`  
• part_number = "BRKT-42", revision = "" → `Part Number: BRKT-42`

Purpose:  
Preserves revision visibility without expanding layout. Prevents version mismatch with flattened part fields.

Source: SubProg_[PSX]_REF_only.txt  
Validated In: Part Summary Visual v9.6  

===== END_SUB_BLOCK: [PSX002] =====

===== SUB_BLOCK: [OPR001] – OPERATION BREAKDOWN DISPLAY =====

[OPR001.A] - OPERATION TABLE RENDER FORMAT  
Status: ENFORCED  
Dependencies: —  
Applies To: GPT Instructions, CSV Schema, Backend Parser, Edit Mode, Simulation Output  
Rule Scope: Output Formatting  
Description:  
When operations are present, render the Operation Breakdown table using the following fixed format:

| Seq | Operation     | Setup  | Setup Cost | # Ops | Time | $/Part |
|-----|---------------|--------|-------------|--------|------|--------|
| 1   | Laser         | 2m     | $2.50       | 1      | 12s  | $0.63  |
| 2   | Deburr        | 1m     | $1.25       | 1      | 10s  | $0.42  |

Formatting Rules:  
• Column headers must appear in this exact order  
• Setup = minutes only (e.g. `2m`)  
• Setup Cost = flat value per setup (e.g. `$2.50`)  
• Time = seconds only (e.g. `12s`)  
• Runtime values must be pulled from `Operations[UFG]_sQL.csv` — no live calculations allowed  
• Mandatory operations (Plan, Final Insp., Package) must be included by default  

Purpose:  
Standardizes visual structure for operations, ensuring consistent formatting and preventing column drift or layout ambiguity.

Source: SubProg_[OPR]_REF_only.txt  
Validated In: OPR Table Format Test v3.1  

---

[OPR001.B] – POST-BREAKDOWN EDIT MODE PROMPT  
Status: ENFORCED  
Dependencies: —  
Applies To: GPT Instructions, CSV Schema, Backend Parser, Edit Mode, Simulation Output  
Rule Scope: Post-Render Command Injection  
Description:  
After the final row of the Operation Breakdown table, display the following prompt:

→ Type 1 to Edit ⚙️ Operations  
→ Press [enter] to Generate 📉 Quote

Rules:  
• `Type 1` is the only valid entry into Edit Mode  
• `[enter]` proceeds to the Quote Breakdown and Summary  
• This prompt must immediately follow the last operation row  
• No extra spacing or UI elements may appear between the table and this prompt  
• This prompt must always appear before any summary or cost sections

Example Layout:  
| 5   | Final Insp. | 2m   | $2.50 | 1   | 12s | $0.75 |  
| 6   | Package     | 1m   | $1.25 | 1   | 6s  | $0.38 |

→ Type 1 to Edit ⚙️ Operations  
→ Press [enter] to Generate 📉 Quote

Purpose:  
Provides a consistent user interface trigger for entering Edit Mode. Prevents unintended skips or UI drift.

Source: SubProg_[OPR]_REF_only.txt  
Validated In: Prompt Placement Test v2.0  

===== END_SUB_BLOCK: [OPR001] =====
--
===== SUB_BLOCK: [OPR002] – OPERATION LABEL ENFORCEMENT =====  
[OPR002.A] - OFFICIAL DISPLAY LABELS  
Status: ENFORCED  
Dependencies: —  
Applies To: GPT Instructions, CSV Schema, Backend Parser, Edit Mode, Simulation Output  
Rule Scope: Output Formatting  
Description:  
All rendered operations in the Operation Breakdown table must use the official label as listed in `Operations[UFG]_sQL.csv`.

Display Rules:  
• Only the `Operation Name` field may be used for display  
• No aliases, abbreviations, or user input variants may be shown  
• Label formatting must exactly match source file (case, spacing, punctuation)

Purpose:  
Prevents UI drift and preserves label consistency across quoting, display, and export.

Source: SubProg_[OPR]_REF_only.txt  
Validated In: Label Enforcement Audit v2.3  

---

[OPR002.B] - INPUT ALIAS VALIDATION  
Status: ENFORCED  
Dependencies: —  
Applies To: GPT Instructions, CSV Schema, Backend Parser, Edit Mode, Simulation Output  
Rule Scope: Label Validation  
Description:  
All user input for operations — whether parsed or typed — must match a valid alias or abbreviation from `Operations[UFG]_sQL.csv`.

Matching Logic:  
• Case-insensitive  
• Whitespace stripped  
• Match accepted from any of:  
 → `Operation Name`  
 → `Aliases` (comma-separated)  
 → `Abbreviations` (if present)

First matching entry is used to resolve the operation label.

Purpose:  
Supports flexible input without compromising deterministic operation resolution.

Source: SubProg_[OPR]_REF_only.txt  
Validated In: OpName Alias Sim v4.3  

---

[OPR002.C] – UNKNOWN LABEL FALLBACK HANDLING  
Status: ENFORCED  
Dependencies: [OPR002.B]  
Applies To: GPT Instructions, CSV Schema, Backend Parser, Edit Mode, Simulation Output  
Rule Scope: Fallback & Error Containment  
Description:  
Handles input labels that fail to match any known operation or outside process alias.

Fallback Behavior:  
• If label resembles an outside process → insert inert row labeled `Outside Process`  
 → All cost fields = dash (`–`)  
 → Row is included visually but excluded from costing  
• If label is completely unrecognized → trigger terminal error:  
 `Unknown operation label: [input]`  
 → Quote session is halted

Fallback Row Format:  
| Seq | Operation       | Setup | Setup Cost | # Ops | Time | $/Part |  
|-----|------------------|--------|-------------|--------|------|--------|  
| N   | Outside Process |   –    |     –       |   –    |  –   |   –    |

Enforcement Rules:  
• Only one fallback row allowed per input  
• Label `Outside Process` is fixed and non-editable  
• Fallback logic must not share behavior or format from other SUB_BLOCKs  

Purpose:  
Prevents quote failure due to unknown labels while preserving structure and supporting review.

Source: SubProg_[OPR]_REF_only.txt  
Validated In: Edit Mode Fallback Regression v2.0  

===== END_SUB_BLOCK: [OPR002] =====
---
===== SUB_BLOCK: [OPR003] – OPERATION SEQUENCE VALIDATION =====  

[OPR003.A] - MANDATORY OPERATIONS ENFORCEMENT  
Status: ENFORCED  
Dependencies: —  
Applies To: GPT Instructions, CSV Schema, Backend Parser, Edit Mode, Simulation Output  
Rule Scope: Validation  
Description:  
All quotes must include the following operations:  
• `Plan`  
• `Final Insp.`  
• `Package`  

Enforcement:  
• These are inserted automatically if missing during quote generation  
• If removed by the user in Edit Mode, the change is honored  

Purpose:  
Guarantees all quotes include required system operations unless explicitly edited.

Source: SubProg_[OPR]_REF_only.txt  
Validated In: Sequence Completeness Sim 1.2  

---

[OPR003.B] - END-SEQUENCE VALIDATION  
Status: ENFORCED  
Dependencies: [OPR003.A]  
Applies To: GPT Instructions, CSV Schema, Backend Parser, Edit Mode, Simulation Output  
Rule Scope: Sequence Control  
Sequence Rules:  
• `Final Insp.` must appear second-to-last  
• `Package` must appear last  

Enforcement:  
• System reorders if these are out of position (unless manually reordered)  
• User-defined sequences override auto-placement  

Purpose:  
Maintains end-of-sequence conformity while allowing override by user.

Source: SubProg_[OPR]_REF_only.txt  
Validated In: Operation End-Cap Positional Test v2.0  

---

[OPR003.C] - DEBURR AUTO-INSERTION LOGIC  
Status: ENFORCED  
Dependencies: [OPR003.A]  
Applies To: GPT Instructions, CSV Schema, Backend Parser, Edit Mode, Simulation Output  
Rule Scope: Conditional Insert  
Insertion Rule:  
• If any of: `Drill`, `Countersink`, `Counterbore`, `Tap`, `Ream`  
 → Insert `Deburr` after the last of those operations  
• Else if any of: `Laser`, `Punch`, `Mill`  
 → Insert `Deburr` after the last of those  
• If `Deburr` is already present → no changes made  

Purpose:  
Ensures appropriate finishing steps based on prior operations.

Source: SubProg_[OPR]_REF_only.txt  
Validated In: Conditional Deburr Sim v3.3  

---

[OPR003.D] - INSTALL PLACEMENT CONSTRAINTS  
Status: ENFORCED  
Dependencies: —  
Applies To: GPT Instructions, CSV Schema, Backend Parser, Edit Mode, Simulation Output  
Rule Scope: Placement Validation  
Placement Rules:  
• `Install` operations must always be placed:  
 → After plating-related operations (e.g., `Anodize`, `C/F Gold`)  
 → Before painting/coating (e.g., `Powdercoat`)  

Enforcement:  
• User overrides take priority  
• Rule applies during initial sequencing and Edit Mode

Purpose:  
Prevents hardware installation from conflicting with finish coatings.

Source: SubProg_[OPR]_REF_only.txt  
Validated In: Install Placement Regression Stack  

---

[OPR003.E] - FORM OP INSERTION FROM BEND COUNT  
Status: ENFORCED  
Dependencies: —  
Applies To: GPT Instructions, CSV Schema, Backend Parser, Edit Mode, Simulation Output  
Rule Scope: Conditional Insert  
Description:  
If `bend_count ≥ 1` and no `Form` operation exists, insert a `Form` operation into the sequence.

Insertion Behavior:  
• Label = `Form`  
• # Ops = value of `bend_count`  
• Setup Time, Runtime, Cost = pulled from `Operations[UFG]_sQL.csv`  
• Insert after last cutting operation (`Laser`, `Punch`, `Mill`)  
• If no cutting op present → insert after initial operation  

Restrictions:  
• Only one `Form` operation may be inserted  
• Label must not be substituted  
• Operation persists unless removed by user in Edit Mode  

Purpose:  
Adds forming logic based on geometric complexity. Supports quotes for bent parts without user input.

Source: SubProg_[OPR]_REF_only.txt  
Validated In: OPR Form Insert Sim 3.4  

===== END_SUB_BLOCK: [OPR003] =====
---
===== SUB_BLOCK: [OPR004] – OUTSIDE PROCESS INSERTION =====

[OPR004.A] - OUTSIDE PROCESS AS OPERATION BLOCK  
Status: ENFORCED  
Dependencies: —  
Applies To: GPT Instructions, CSV Schema, Backend Parser, Edit Mode, Simulation Output  
Rule Scope: Conditional Rendering  
Description:  
If outside processes are present in the parsed file or entered by the user, they must also appear in the Operation Breakdown table.

Formatting Rules:  
• Operation = `Outside Process`  
• Setup = `-`  
• Setup Cost = `-`  
• # Ops = `-`  
• Time = `-`  
• $/Part = `[flat area] × [$/sqin]` (from `OutsideProcess[UFG]_sQL.csv`)  

Fallback:  
• If label is invalid → insert row with `$0.00` as cost

Purpose:  
Standardizes rendering and costing of outside process rows using deterministic logic.

Source: SubProg_[OPR]_REF_only.txt  
Validated In: OP Cost Display Sim v2.2  

---

[OPR004.B] - OUTSIDE PROCESS DISPLAY FORMATTING RULES  
Status: ENFORCED  
Dependencies: —  
Applies To: GPT Instructions, CSV Schema, Backend Parser, Edit Mode, Simulation Output  
Rule Scope: Rendering Rules  
Description:  
All outside process rows must follow strict formatting rules:

• Columns: Seq, Operation, Setup, Setup Cost, # Ops, Time, $/Part  
• Fixed values for Setup, Cost, # Ops, Time = `-`  
• $/Part = `[flat area] × [unit cost]`  
• If no match found in CSV → use `$0.00`  
• Row must render even when costing fails  

Purpose:  
Enforces deterministic rendering regardless of OP validity. Prevents layout inconsistencies due to missing specs.

Source: SubProg_[OPR]_REF_only.txt  
Validated In: Format Lock Regression Suite 3.1  

---

[OPR004.C] - OUTSIDE PROCESS ALIAS RESOLUTION  
Status: ENFORCED  
Dependencies: [OPR004.A], [OPR004.B]  
Applies To: GPT Instructions, CSV Schema, Backend Parser, Edit Mode, Simulation Output  
Rule Scope: Label Normalization  
Description:  
Parsed or user-entered outside process names are resolved against aliases in `OutsideProcess[UFG]_sQL.csv`.

Rules:  
• Case-insensitive matching  
• Match aliases to primary OP label  
• If no match found → fallback row is inserted per [OPR004.B]  

Purpose:  
Ensures flexible entry without sacrificing cost resolution accuracy.

Source: SubProg_[OPR]_REF_only.txt  
Validated In: OP Alias Normalization Test v2.0  

---

[OPR004.D] – OCR-Inferred Outside Process Injector  
Status: ENFORCED  
Dependencies: [OPR004.A], [OPR004.C]  
Applies To: GPT Instructions, CSV Schema, Backend Parser, Edit Mode, Simulation Output  
Rule Scope: Operation Injection via OCR  
Description:  
Allows outside processes to be auto-inserted into the operation list from `ocr_data["outside_processes"]`.

Trigger Conditions:  
• `ocr_data["outside_processes"]` is non-empty  
• Each entry is matched using alias resolution  
• No `pdf_format_score` check required for this field  

Behavior:  
• Label = `Outside Process`  
• Setup/Time/Cost = `-`  
• $/Part = `[flat area] × unit cost` from CSV  
• If no match found → use `$0.00`  
• Source is logged as `"ocr"`

Restrictions:  
• No GPT expansion, inference, or formatting allowed  
• Aliases must resolve cleanly  
• Ambiguity results in fallback row per [OPR004.B]  

Purpose:  
Supports clean injection of OPs from scanned drawings using trusted alias mappings and enforced pricing.

Source: SubProg_[OPR]_REF_only.txt  
Validated In: PDF_OP OCR Sim Suite 2.0  

===== END_SUB_BLOCK: [OPR004] =====

===== SUB_BLOCK: [OPX001] – OUTSIDE PROCESS UI RENDER =====  

[OPX001.A] - OUTSIDE PROCESS BLOCK DISPLAY FORMAT  
Status: ENFORCED  
Dependencies: —  
Applies To: GPT Instructions, CSV Schema, Backend Parser, Edit Mode, Simulation Output  
Rule Scope: Output Formatting  
Description:  
If outside processes are present, the system must display the block using the following exact layout:

📦 Outside Process  
• [Process Name] – [Description] (*[Spec]*)  
• [Process Name] – [Description] (*[Spec]*)

Display Rules:  
• Each entry begins with `•`, followed by name, description, and spec  
• No pricing or cost information is shown  
• Entries are ordered by operation sequence  
• Entire block is omitted if no valid outside process entries exist  
• No AI formatting, soft labels, or inferred tags allowed  
• Spec format must be wrapped in parentheses and asterisked: `(*MIL-XXX*)`, `(*RoHS*)`, etc.  
• No alternate wrappers permitted  

Example:  
📦 Outside Process  
• Anodize – Black (*MIL-A-8625F*)  
• Silk Screen – White logo (*RoHS*)

Purpose:  
Enforces strict rendering rules for outside process display to ensure consistency and prevent visual drift.

Source: SubProg_[OPX]_REF_only.txt  
Validated In: OP Block Sim 3.0  

===== END_SUB_BLOCK: [OPX001] =====
---
===== SUB_BLOCK: [OPX002] – OUTSIDE PROCESS COST SOURCE =====  

[OPX002.A] – OP COST DATA ENFORCEMENT  
Status: ENFORCED  
Dependencies: —  
Applies To: GPT Instructions, CSV Schema, Backend Parser, Edit Mode, Simulation Output  
Rule Scope: Cost Calculation  
Description:  
Governs the cost lookup and enforcement for all outside processes in a quote. All costs must originate from a validated CSV file.

Cost Source:  
→ `OutsideProcess[UFG]_sQL.csv` (exact match required)

Enforcement Rules:  
• All outside process costs must come directly from the CSV — no substitutions or approximations allowed  
• Exact match is required on:  
 → `Process Name`  
 → `Spec`  
• If no exact match is found → cost = `0.00`  
• No fallback aliasing, partial spec matching, or interpolation is permitted  
• Costs are applied on a per-part basis only — no per-lot or batch logic  
• Missing cost rows do not cause errors — but the OP is excluded from cost breakdown  
• This rule controls only the cost logic — not UI display or sequence formatting

Purpose:  
Enforces deterministic costing for outside process entries based on trusted data only. Prevents fabricated or estimated OP pricing.

Source: SubProg_[OPX]_REF_only.txt  
Validated In: Cost Sim Matrix 4.2, OP/Spec Resolution Audit v1.9  

===== END_SUB_BLOCK: [OPX002] =====

===== SUB_BLOCK: [HWX001] – HARDWARE UI RENDER =====  
  
[HWX001.A] – HARDWARE FIELD DISPLAY LOGIC  
Status: ENFORCED  
Dependencies: —  
Applies To: GPT Instructions, CSV Schema, Backend Parser, Edit Mode, Simulation Output  
Rule Scope: Hardware Breakdown Rendering  
Description:  
Controls how hardware inserts are shown in quote output. Each row reflects a unique hardware type and its per-part contribution.

Hardware Breakdown Table Format:  
| Type         | Qty | Unit Cost | Total Cost |  
|--------------|-----|-----------|------------|  
| FH-M3-6      | 2   | $0.15     | $0.30      |  
| CLS-440-2    | 4   | $0.12     | $0.48      |  

Rendering Rules:  
• Table must appear in the Operation Breakdown or standalone if no OPs exist  
• Qty = quantity per part  
• Unit Cost = pulled from `Hardware[UFG]_sQL.csv`  
• Total Cost = Qty × Unit Cost  
• $ values must be shown as `$X.XX`  
• Do not group by material or function — group strictly by part number  

Purpose:  
Standardizes hardware display during quoting and ensures consistent pricing visibility.

Source: SubProg_[HWX]_REF_only.txt  
Validated In: Hardware Table Display Sim v1.2  

===== END_SUB_BLOCK: [HWX001] =====
---
===== SUB_BLOCK: [HWX002] – HARDWARE PARSING FROM FILE LOAD =====  

[HWX002.A] - HARDWARE PARSE FROM SOURCE FILE  
Status: ENFORCED  
Dependencies: —  
Applies To: GPT Instructions, CSV Schema, Backend Parser, Edit Mode, Simulation Output  
Rule Scope: File-Driven Detection  
Description:  
Parses hardware inserts from uploaded files and queues them for use in Install operations. Parsing sources include PDF, DXF, and STEP.

Detection Sources:  
• PDF → detect via notes, BOM rows, or flag names  
• DXF → extract from metadata layers or annotations  
• STEP → scan part name strings or embedded annotations  

Parse Rules:  
• Match hardware type against `Hardware[UFG]_sQL.csv`  
• Quantity = count of matched entries or explicit quantity (e.g. `x4`)  
• Any unmatched hardware type is discarded  
• No operation is generated — hardware is queued only  

Purpose:  
Ensures deterministic file-based parsing of hardware, avoiding hallucinated entries or speculative inference.

Source: SubProg_[HWX]_REF_only.txt  
Validated In: HW Parse Stack Sim v3.0  

---

[HWX002.B] – HARDWARE SOURCE PRIORITY RESOLUTION  
Status: ENFORCED  
Dependencies: [HWX002.A]  
Applies To: GPT Instructions, CSV Schema, Backend Parser, Edit Mode, Simulation Output  
Rule Scope: Conflict Handling  
Description:  
If multiple file types contain hardware references, the system enforces this priority:

→ PDF > DXF > STEP

Rules:  
• If PDF-derived hardware exists → discard DXF and STEP results  
• If PDF is empty but DXF has data → discard STEP  
• STEP is only used if no higher source provides hardware  
• Do not merge or combine across sources  
• If no source yields valid entries → suppress hardware block  

Examples:  
• PDF = `4× FH-M3-6` → use only PDF  
• DXF = `3× CLS-440-2`, STEP = `2× PEM-832` → use only DXF  
• STEP only = `1× PEM-832` → use STEP  

Restrictions:  
• No blended entries or quantity merging allowed  
• Source priority is resolved once per file load only  

Purpose:  
Guarantees consistent selection of hardware source to avoid duplication or conflict.

Source: SubProg_[HWX]_REF_only.txt  
Validated In: HW Source Override Matrix v2.1  

---

[HWX002.C] – RESILIENT HARDWARE TABLE PARSER  
Status: ENFORCED  
Dependencies: —  
Applies To: GPT Instructions, CSV Schema, Backend Parser, Edit Mode, Simulation Output  
Rule Scope: Free-Text Parsing  
Description:  
Handles unstructured hardware tables and loose text blocks, including fallback to OCR content if available.

PATCH – OCR Fallback Enabled  
• If `ocr_data["raw_text"]` is available, use it as primary source  
• Overrides visible PDF or DXF blocks  

Detection Logic:  
• Must detect ≥ 3 of these header-like keywords:  
 → "QTY", "PART", "TYPE", "PN", "DESC"  
• Accepts lines where at least two fields match valid formats:  
 → Quantity = integer  
 → Part number = token ≥ 4 chars  
 → Description = optional fallback  

Output Format:  
• Each valid line becomes a `hardware[]` object:  
 → `{ "part_number": "ABC123", "qty": 4, "description": "Hex spacer" }`  
• Reject malformed or incomplete entries  

Restrictions:  
• No inference from drawing layers or filename  
• No cost lookup, aliasing, or substitutions allowed  
• Units, symbols, or notes must be stripped  

Purpose:  
Improves tolerance for loosely formatted hardware tables. Enables OCR scans to contribute valid hardware entries.

Source: SubProg_[HWX]_REF_only.txt  
Validated In: OCR RawText Expansion Audit v1.2  

===== END_SUB_BLOCK: [HWX002] =====
---
===== SUB_BLOCK: [HWX003] – UNKNOWN HARDWARE HANDLING =====  

[HWX003.A] - UNKNOWN HARDWARE DETECTION AND DISPLAY  
Status: ENFORCED  
Dependencies: —  
Applies To: GPT Instructions, CSV Schema, Backend Parser, Edit Mode, Simulation Output  
Rule Scope: Validation + UI Display  
Description:  
If a hardware insert is detected during file parsing but does not match any entry in `Hardware[UFG]_sQL.csv`, the system must take the following action:

Behavior:  
1. Attempt to resolve the hardware type via public hardware databases  
2. If resolved:  
 • Display entry in the Hardware block with suffix: `(not in internal database)`  
 • Do **not** generate an Install operation  
3. If unresolved:  
 • Discard silently with no listing or operation  

Display Format:  
🛠️ Hardware  
• FH-M3-6 (2×)  
• Unknown XYZ-55 (1×) (not in internal database)

Restrictions:  
• Applies only during file load (PDF, DXF, STEP)  
• Edit Mode entries must reject unknown hardware immediately  
• Unknown hardware is always excluded from Install operations  

Purpose:  
Allows flexible display of publicly known but unsupported hardware while preserving op logic integrity.

Source: SubProg_[HWX]_REF_only.txt  
Validated In: HWX Public Resolution Sim 4.4  

===== END_SUB_BLOCK: [HWX003] =====

===== SUB_BLOCK: [EMX000] – EDIT MODE DISPATCH + ENTRY ===== 
 
[EMX000.A] – EDIT MODE ENTRY PROMPT  
Status: ENFORCED  
Dependencies: —  
Applies To: GPT Instructions, CSV Schema, Backend Parser, Edit Mode, Simulation Output  
Rule Scope: Entry Interaction  
Description:  
When the user enters Edit Mode, the following prompt must appear exactly:

📝 Edit Mode Active  
Which seq would you like to edit? (e.g. 2)  
type [ i ] to insert a new operation  
type [ r ] to reorder sequence (e.g. 6 to 3)  
🚀 type [ d ] to exit

Rules:  
• Prompt must appear after every valid edit, insert, or reorder  
• Invalid commands trigger retry  
• Sequence numbers are 1-based  
• Re-entry into Edit Mode is allowed from the Operation Breakdown screen  

Purpose:  
Standardizes Edit Mode entry and navigation flow.

Source: SubProg_[EMX]_REF_only.txt  
Validated In: Edit Prompt UI Regression Test v1.0  

---

[EMX000.B] – DISPATCH RULES  
Status: ENFORCED  
Dependencies: —  
Applies To: GPT Instructions, CSV Schema, Backend Parser, Edit Mode, Simulation Output  
Rule Scope: Edit Mode Command Routing  
Description:  
Defines the allowed command inputs and expected routing:

| Command   | Action                                           |
|-----------|--------------------------------------------------|
| [ 1–n ]   | Edit operation by sequence number                |
| [ i ]     | Insert a new operation before Final Insp.        |
| [ r ]     | Reorder operations using “X to Y” format         |
| [ d ]     | Exit Edit Mode and return to OP breakdown        |

Purpose:  
Ensures deterministic routing from Edit Mode prompts.

Source: SubProg_[EMX]_REF_only.txt  
Validated In: Edit Path Dispatch Test v1.1  

---

[EMX000.C] – INVALID COMMAND HANDLER  
Status: ENFORCED  
Dependencies: —  
Applies To: GPT Instructions, CSV Schema, Backend Parser, Edit Mode, Simulation Output  
Rule Scope: Rejection and Loopback  
Description:  
When invalid input is received in Edit Mode:

Response:  
> ❌ Invalid input. Please enter a valid sequence number or command.

• Edit Mode prompt must reappear immediately  
• No auto-correct, inference, or alternate routes allowed  

Purpose:  
Guarantees consistent handling of invalid input with no ambiguity.

Source: SubProg_[EMX]_REF_only.txt  
Validated In: Invalid Edit Command Stress Test  

---

[EMX000.D] – MODE EXIT  
Status: ENFORCED  
Dependencies: —  
Applies To: GPT Instructions, CSV Schema, Backend Parser, Edit Mode, Simulation Output  
Rule Scope: Exit Handling  
Description:  
When user types `[ d ]`, exit Edit Mode immediately and resume Operation Breakdown.

Rules:  
• No summary or transition message may be shown  
• Edit Mode may be re-entered afterward  
• Once `[enter]` is pressed on OP table → quote is finalized  
• No edits allowed after finalization  

Purpose:  
Preserves a clean transition back to static mode after edit session.

Source: SubProg_[EMX]_REF_only.txt  
Validated In: Mode Transition Test v3.0  

---

[EMX000.E] – SESSION TIMEOUT  
Status: ENFORCED  
Dependencies: —  
Applies To: GPT Instructions, CSV Schema, Backend Parser, Edit Mode, Simulation Output  
Rule Scope: Session Management  
Description:  
If user is idle in Edit Mode for more than 10 minutes, automatically exit with:

> ⏱️ Edit Mode timed out. Returning to Operation Breakdown…

• All unsaved changes during that prompt cycle are discarded  
• No assumptions or retry prompts may be issued  

Purpose:  
Prevents stale Edit Mode sessions and limits system loop risk.

Source: SubProg_[EMX]_REF_only.txt  
Validated In: Edit Session Timeout Sim v2.1  

===== END_SUB_BLOCK: [EMX000] =====
---
===== SUB_BLOCK: [EMX001] – OPERATION EDIT FLOW =====
  
[EMX001.A] – OPERATION EDIT PROMPT  
Status: ENFORCED  
Dependencies: —  
Applies To: GPT Instructions, CSV Schema, Backend Parser, Edit Mode, Simulation Output  
Rule Scope: Edit Action Flow  
Description:  
When editing an operation row, GPT must display this prompt:

🛠️ Editing Seq {n}  
• Operation: {Operation}  
• Setup: {SetupTime}  
• # Ops: {OpCount}  
• Time: {Runtime}  
• $/Part: {RatePerPart}  

enter new operation (e.g. saw)  
edit # of ops (e.g. 6)  
type [ x ] to remove seq  
type [ c ] to cancel

Behavior:  
• Setup time is displayed but not editable  
• Operation name updates on valid alias or match  
• Op count updates on valid integer input  
• Only one field may be edited per prompt cycle  
• Cancel returns to Edit Mode with no changes  

Purpose:  
Enforces structured, one-field-at-a-time edits in Edit Mode.

Source: SubProg_[EMX]_REF_only.txt  
Validated In: Edit Mode Inline Test 2.3  

---

[EMX001.B] – OPERATION NAME VALIDATION + ALIAS / INFERENCE SYSTEM  
Status: ENFORCED  
Dependencies: [EMX001.A]  
Applies To: GPT Instructions, CSV Schema, Backend Parser, Edit Mode, Simulation Output  
Rule Scope: Operation Input Normalization  
Description:  
User-entered operation names must validate against `Operations[UFG]_sQL.csv`.

Rules:  
• Match allowed from:  
 – `Operation Name`  
 – `Aliases`  
 – `Abbreviations`  
• Case-insensitive, whitespace-stripped  
• 1:1 mapping required — ambiguous matches must trigger clarification  
• No fabricated or speculative labels allowed  

Examples:  
• `cntbr` → ✅ Counterbore  
• `chamfr` → ❌ Retry required  
• `fooop` → ❌ Rejected  

Purpose:  
Ensures strict alias resolution using file-based logic only.

Source: SubProg_[EMX]_REF_only.txt  
Validated In: Alias Mapping Sim v4.3  

---

[EMX001.C] – INVALID OPERATION HANDLER  
Status: ENFORCED  
Dependencies: [EMX001.A], [EMX001.B]  
Applies To: GPT Instructions, CSV Schema, Backend Parser, Edit Mode, Simulation Output  
Rule Scope: Retry Loop + Clarification  
Description:  
When input fails to resolve to a valid operation:

Response Format:  
> ⚡🐸 Invalid entry. Please enter a valid operation or number of ops.

• GPT must redisplay the full Edit Prompt for the sequence  
• Ambiguous matches →  
> ❓ Did you mean one of the following: [Option A], [Option B]?  
• Two failures →  
> ⚡🐸 Try again or type [ c ] to cancel  

Purpose:  
Enforces deterministic retry behavior with no auto-correction or GPT guessing.

Source: SubProg_[EMX]_REF_only.txt  
Validated In: Edit Reject Path Replay Sim v3.0  

---

[EMX001.D] – HARDWARE / OUTSIDE PROCESS REDIRECTOR  
Status: ENFORCED  
Dependencies: [EMX001.A], [EMX001.B]  
Applies To: GPT Instructions, CSV Schema, Backend Parser, Edit Mode, Simulation Output  
Rule Scope: Specialized Operation Dispatch  
Description:  
When editing or inserting `Install` or `Outside Process`, special handlers must activate:

• If `Install` → route to Hardware Edit Prompt (EMX003)  
> Action: change hardware  
> → Enter new hardware or include quantity  
> Example: FH-M3-6 or FH-M3-6 x4  

• If `Outside Process` → prompt for assignment:  
> Enter an outside process (e.g. Anodize, Powdercoat)  
→ Resolve spec using `OutsideProcess[UFG]_sQL.csv`  
→ Show:  
> Assigned process: Anodize – MIL-PRF-8625 Type II  

• Unrecognized process →  
> ⚡🐸 Process not recognized. Please enter a valid outside process.

Purpose:  
Routes special operation types to their respective config flows.

Source: SubProg_[EMX]_REF_only.txt  
Validated In: OP Redirect Handler Sim v2.2  

---

[EMX001.E] – SESSION TIMEOUT IN OPERATION EDIT  
Status: ENFORCED  
Dependencies: —  
Applies To: GPT Instructions, CSV Schema, Backend Parser, Edit Mode, Simulation Output  
Rule Scope: Timeout Guard  
Description:  
If user is idle during edit for more than 10 minutes, discard unconfirmed changes and return to Edit Mode.

Response:  
> ⏱️ Operation edit timed out. Returning to Edit Mode…

Purpose:  
Preserves quote integrity by enforcing prompt-level edit timeouts.

Source: SubProg_[EMX]_REF_only.txt  
Validated In: Timeout Loop Exit Sim v1.5  

---

[EMX001.F] – CANCEL + LOOPBACK GUARD  
Status: ENFORCED  
Dependencies: [EMX001.A], [EMX001.B]  
Applies To: GPT Instructions, CSV Schema, Backend Parser, Edit Mode, Simulation Output  
Rule Scope: Mid-Edit Exit  
Description:  
If user types `[ c ]`, cancel edit and return to Edit Mode with no changes.

• Prompt must include:  
> type [ c ] to cancel  
• No summary or explanation is shown  
• Applies to all operation types  

Purpose:  
Guarantees user-directed exit from active edit states.

Source: SubProg_[EMX]_REF_only.txt  
Validated In: Cancel Fallback Sim v3.1  

---

[EMX001.G] – REMOVE CONFIRMATION PROMPT  
Status: ENFORCED  
Dependencies: [EMX001.A]  
Applies To: GPT Instructions, CSV Schema, Backend Parser, Edit Mode, Simulation Output  
Rule Scope: Operation-Level Removal  
Description:  
Triggered by `[ x ]` input during edit. Requires confirmation:

Prompt:  
🛑 Confirm remove of Seq {n}  
Type [ y ] to confirm or [ d ] to cancel

Rules:  
• `[ y ]` → permanently delete the row  
• `[ d ]` → cancel and return to Edit Mode  
• No alias inputs accepted  
• Operation must be validated as removable prior to prompt  

Purpose:  
Provides an irreversible but guarded removal mechanism for operations.

Source: SubProg_[EMX]_REF_only.txt  
Validated In: Edit Sequence Delete Test v2.1  

===== END_SUB_BLOCK: [EMX001] =====
---
===== SUB_BLOCK: [EMX002] – OPERATION REORDER MODE =====  

[EMX002.A] – REORDER PROMPT  
Status: ENFORCED  
Dependencies: —  
Applies To: GPT Instructions, CSV Schema, Backend Parser, Edit Mode, Simulation Output  
Rule Scope: Prompt UI + Entry  
Description:  
When the user types `[ r ]` in Edit Mode, the system must display:

📦 Reorder Mode Active  
Reposition a sequence  
e.g. 6 to 3 (moves seq 6 before seq 3)  
type [ c ] to cancel

Rules:  
• Input must be strictly in `X to Y` format  
• Accept 1–2 digit sequences only  
• Reject malformed, partial, or ambiguous inputs  
• Cancel returns to Edit Mode without changes  

Purpose:  
Initiates reorder flow for adjusting sequence positions.

Source: SubProg_[EMX]_REF_only.txt  
Validated In: Sequence Reorder UI Prompt Test v1.2  

---

[EMX002.B] – REORDER EXECUTION HANDLER  
Status: ENFORCED  
Dependencies: [EMX002.A]  
Applies To: GPT Instructions, CSV Schema, Backend Parser, Edit Mode, Simulation Output  
Rule Scope: Reposition Logic  
Description:  
After receiving a valid `X to Y` input:

Behavior:  
• Remove operation at sequence `X`  
• Insert it immediately before sequence `Y`  
• Reindex all sequence numbers sequentially  
• Immediately re-render full updated sequence  
• Return to Edit Mode prompt with no transition text  

Example:  
`6 to 3`  
→ Moves Seq 6 above Seq 3  
→ Full sequence re-renders with updated numbering  

Edge Handling:  
• `4 to 4` or invalid positions →  
> ⚡🐸 Invalid move. Sequence unchanged.  
→ Re-display reorder prompt  

Purpose:  
Enforces deterministic repositioning while maintaining sequence integrity and structure.

Source: SubProg_[EMX]_REF_only.txt  
Validated In: Operation Movement Reindex Sim v2.0  

===== END_SUB_BLOCK: [EMX002] =====
---
===== SUB_BLOCK: [EMX003] – INSTALL OPERATION HANDLER ===== 
 
[EMX003.A] – INSTALL HANDLER ENTRY  
Status: ENFORCED  
Dependencies: —  
Applies To: GPT Instructions, CSV Schema, Backend Parser, Edit Mode, Simulation Output  
Rule Scope: Operation = Install  
Description:  
When a user selects or inserts an operation labeled `Install`, control must immediately route to the hardware input handler.

Prompt:  
> 🔩 Install Operation Active  
> enter hardware type (e.g. FH-M3-6)  
> or include quantity (e.g. FH-M3-6 x4)  
> type [ c ] to cancel

Rules:  
• Operation label = `Install` (fixed, not editable)  
• Input format accepted:  
 – `FH-M3-6 x4`  
 – `FH-M3-6x4`  
 – `FH-M3-6 4`  
• Part number must match `Hardware[UFG]_sQL.csv`  
• If hardware not found →  
> ⚡🐸 *Hardware not found.*

Purpose:  
Activates deterministic entry point for specifying installed hardware inline with operation editing.

Source: SubProg_[EMX]_REF_only.txt  
Validated In: Install Edit Trigger Sim v3.0  

---

[EMX003.B] – QUANTITY HANDLER  
Status: ENFORCED  
Dependencies: [EMX003.A]  
Applies To: GPT Instructions, CSV Schema, Backend Parser, Edit Mode, Simulation Output  
Rule Scope: # Ops Validation  
Description:  
Quantity must be extracted from the hardware input string.

Rules:  
• Must be a valid positive integer  
• If missing → prompt user:  
> ❓ *How many of this insert should be installed?*  
• If malformed →  
> ⚡🐸 *Invalid format. Use 'FH-M3-6 x4' or similar.*

Purpose:  
Enforces unambiguous and structured capture of installation quantity for hardware entries.

Source: SubProg_[EMX]_REF_only.txt  
Validated In: Quantity Extraction Sim v2.2  

---

[EMX003.C] – CANCEL HANDLER  
Status: ENFORCED  
Dependencies: [EMX003.A]  
Applies To: GPT Instructions, CSV Schema, Backend Parser, Edit Mode, Simulation Output  
Rule Scope: Flow Control  
Description:  
If user types `[ c ]`, cancel the install prompt immediately.

Behavior:  
• No changes are applied to the operation row  
• Return to Edit Mode prompt  
• No summary or rollback messaging shown  

Purpose:  
Preserves user control over hardware input loop. Allows safe mid-stream exit without mutation.

Source: SubProg_[EMX]_REF_only.txt  
Validated In: Install Cancel Sim v1.6  

===== END_SUB_BLOCK: [EMX003] =====
---
===== SUB_BLOCK: [EMX004] – OUTSIDE PROCESS ASSIGNMENT HANDLER ===== 
 
[EMX004.A] – OUTSIDE PROCESS OPERATION ASSIGNMENT  
Status: ENFORCED  
Dependencies: —  
Applies To: GPT Instructions, CSV Schema, Backend Parser, Edit Mode, Simulation Output  
Rule Scope: Operation = Outside Process  
Description:  
When a user selects or inserts an operation with the label `Outside Process`, the system must prompt the user to assign a valid process specification.

Prompt:  
📦 Outside Process  
enter a process to assign (e.g. Anodize)  
or type [ c ] to cancel

Assignment Logic:  
• Input may include color or modifier (e.g. “Black Anodize”)  
• GPT must resolve the process to its full specification using `OutsideProcess[UFG]_sQL.csv`  
• Example result shown to user:  
 > Assigned process: Anodize – MIL-PRF-8625 Type II  

Validation Rules:  
• Process must match a valid alias or label from CSV  
• If ambiguous → prompt:  
 > ❓ Did you mean one of the following: [Option A], [Option B]?  
• If invalid →  
 > ⚡🐸 Process not recognized. Try again or type [ c ] to cancel.  
• After assignment, return immediately to Edit Mode  

Restrictions:  
• User input may not be inferred or fabricated  
• No assumptions or tag expansions allowed  
• This logic applies equally to edits and inserts  

Purpose:  
Ensures all outside process operations are assigned to valid, spec-resolved labels with enforced cost lookup capability.

Source: SubProg_[EMX]_REF_only.txt  
Validated In: Outside Process Insert Sim 2.6  

===== END_SUB_BLOCK: [EMX004] =====
---
===== SUB_BLOCK: [EMX005] – DELETE OPERATION HANDLER ===== 
 
[EMX005.A] – OPERATION DELETION PROMPT  
Status: ENFORCED  
Dependencies: —  
Applies To: GPT Instructions, CSV Schema, Backend Parser, Edit Mode, Simulation Output  
Rule Scope: User-requested deletion of a sequence  
Description:  
When a user selects a sequence and types `[ x ]`, the system must confirm intent to delete:

Prompt:  
🗑️ Delete Operation  
Are you sure you want to delete seq {n}?  
Type [ y ] to confirm or [ c ] to cancel

Rules:  
• `[ y ]` → permanently deletes the row  
• `[ c ]` → returns to Edit Mode with no changes  
• All other inputs → repeat this prompt  
• No auto-confirm or alternate commands permitted  

Purpose:  
Prevents accidental removal of sequence operations. Requires explicit confirmation before deletion.

Source: SubProg_[EMX]_REF_only.txt  
Validated In: Delete Confirm Test v2.1  

---

[EMX005.B] – EXECUTE OPERATION DELETION  
Status: ENFORCED  
Dependencies: [EMX005.A]  
Applies To: GPT Instructions, CSV Schema, Backend Parser, Edit Mode, Simulation Output  
Rule Scope: Post-confirmation action handler  
Description:  
If user confirms deletion (`[ y ]`), perform the following actions:

Behavior:  
• Remove the specified sequence from the operation list  
• Recalculate sequence numbers for all remaining rows  
• Return to Edit Mode with updated table  
• Show:  
 > ✅ Seq {n} deleted. Sequence updated.

Purpose:  
Maintains correct operation indexing after user-directed deletion.

Source: SubProg_[EMX]_REF_only.txt  
Validated In: Reindex on Deletion Sim v3.1  

---

[EMX005.C] – PROTECTED OPERATION GUARDRAIL  
Status: ENFORCED  
Dependencies: [EMX005.A]  
Applies To: GPT Instructions, CSV Schema, Backend Parser, Edit Mode, Simulation Output  
Rule Scope: Enforcement of system-required operations  
Description:  
The following operations may not be deleted under any circumstances:

• Plan  
• Final Insp.  
• Package

If user attempts to delete one of these:  
> ⚡🐸 You can’t delete a required operation. Try another seq.

Rules:  
• Prompt returns to Edit Mode with no changes  
• Deletion attempt is rejected silently in standard sessions  

Purpose:  
Prevents critical quote structure from being compromised by manual edit.

Source: SubProg_[EMX]_REF_only.txt  
Validated In: System Operation Lockout Test v2.0  

===== END_SUB_BLOCK: [EMX005] =====
---
===== SUB_BLOCK: [EMX006] – INSERT OPERATION HANDLER ===== 
 
[EMX006.A] – INSERT COMMAND TRIGGER  
Status: ENFORCED  
Dependencies: —  
Applies To: GPT Instructions, CSV Schema, Backend Parser, Edit Mode, Simulation Output  
Rule Scope: Edit Mode Dispatch  
Description:  
When the user types `[ i ]` in Edit Mode, the system initiates the insert operation flow.

Behavior:  
• Insert new operation directly **before Final Insp.**  
• If `Final Insp.` is missing, insert at second-to-last position  
• All sequence numbers are updated immediately  
• No summary, explanation, or diff view is shown  

Purpose:  
Supports deterministic insertion behavior consistent with structural rules.

Source: SubProg_[EMX]_REF_only.txt  
Validated In: Insert Handler Trigger Test v1.0  

---

[EMX006.B] – INSERT OPERATION PROMPT + DISPATCH  
Status: ENFORCED  
Dependencies: —  
Applies To: GPT Instructions, CSV Schema, Backend Parser, Edit Mode, Simulation Output  
Rule Scope: Insert Mode Interaction  
Prompt:  
🆕 Insert New Operation  
enter operation name (e.g. form, laser)  
or type [ c ] to cancel

Behavior:  
• Input must match a valid entry in `Operations[UFG]_sQL.csv`  
• If valid → insert into sequence and re-render full table  
• If input is `Install` → redirect to [EMX006.E]  
• If input is `Outside Process` → redirect to [EMX006.F]  
• If `[ c ]` is entered → return to Edit Mode without changes  

Purpose:  
Standardizes entry point for insert logic while dispatching special types to their handlers.

Source: SubProg_[EMX]_REF_only.txt  
Validated In: Insert Entry Logic Sim 2.0  

---

[EMX006.C] – RETURN TO EDIT MODE PROMPT  
Status: ENFORCED  
Dependencies: —  
Applies To: GPT Instructions, CSV Schema, Backend Parser, Edit Mode, Simulation Output  
Rule Scope: Loopback Control  
Description:  
After any successful insert (standard, Install, or Outside Process), GPT must immediately re-display the Edit Mode prompt:

📝 Edit Mode Active  
Which seq would you like to edit? (e.g. 2)  
type [ i ] to insert a new operation  
type [ r ] to reorder sequence (e.g. 6 to 3)  
🚀 type [ d ] to exit

Rules:  
• No explanation or commentary is shown  
• Prompt must follow formatting exactly  
• Partial or abbreviated prompts are prohibited  

Purpose:  
Guarantees flow continuity after insert actions.

Source: SubProg_[EMX]_REF_only.txt  
Validated In: Insert Return Flow Sim 3.0  

---

[EMX006.D] – INVALID INPUT HANDLER  
Status: ENFORCED  
Dependencies: —  
Applies To: GPT Instructions, CSV Schema, Backend Parser, Edit Mode, Simulation Output  
Rule Scope: Insert Fallback + Retry  
Description:  
Handles user inputs that are invalid, ambiguous, or malformed during insert.

Failure Conditions:  
• Input does not match any valid operation  
• Matches multiple aliases  
• Input is blank, malformed, or incomplete

Responses:  
• Invalid input →  
 > ⚡🐸 Invalid entry. Please enter a valid operation or type [ c ] to cancel.  
• Ambiguous input →  
 > ❓ Did you mean one of the following: [Option A], [Option B]?  
• Two failures →  
 > ⚡🐸 Try again or type [ c ] to cancel.  

Purpose:  
Enforces deterministic fallback rules with no inference or substitution.

Source: SubProg_[EMX]_REF_only.txt  
Validated In: Insert Reject Sim 1.3  

---

[EMX006.E] – HARDWARE INSERT HANDLER  
Status: ENFORCED  
Dependencies: —  
Applies To: GPT Instructions, CSV Schema, Backend Parser, Edit Mode, Simulation Output  
Rule Scope: Specialized Insert Redirect  
Prompt:  
Action: change hardware  
→ Enter new hardware or include quantity  
→ Example: FH-M3-6 or FH-M3-6 x4  
(Quantity can also be edited in the # Ops column)

Behavior:  
• Hardware must match `Hardware[UFG]_sQL.csv`  
• Quantity required in format: `x4`, `4`, or inline  
• If hardware is not found → trigger [EMX006.D]  
• After entry, re-render OP table and return to Edit Mode  

Purpose:  
Isolates logic for Install operations during insert flow.

Source: SubProg_[EMX]_REF_only.txt  
Validated In: Hardware Insert Sim 3.1  

---

[EMX006.F] – OUTSIDE PROCESS INSERT HANDLER  
Status: ENFORCED  
Dependencies: —  
Applies To: GPT Instructions, CSV Schema, Backend Parser, Edit Mode, Simulation Output  
Rule Scope: Specialized Insert Redirect  
Prompt:  
Enter an outside process (e.g. Anodize, Powdercoat, Clear Chemfilm)

Rules:  
• Input must resolve to label or alias in `OutsideProcess[UFG]_sQL.csv`  
• Color/modifiers must be preserved  
• Match yields:  
 > Assigned process: Anodize – MIL-PRF-8625 Type II  
• If invalid → trigger [EMX006.D]  
• If ambiguous →  
 > ❓ Did you mean one of the following: [...]  

Purpose:  
Ensures OP assignments during insert are normalized and traceable.

Source: SubProg_[EMX]_REF_only.txt  
Validated In: Outside Process Insert Sim 2.6  

---

[EMX006.G] – OPERATION TABLE RE-RENDER AFTER INSERT  
Status: ENFORCED  
Dependencies: —  
Applies To: GPT Instructions, CSV Schema, Backend Parser, Edit Mode, Simulation Output  
Rule Scope: Post-Insert Display Enforcement  
Description:  
After any insert (standard, Install, OP), GPT must fully re-render the Operation Breakdown table.

Rules:  
• Use this exact layout:  
| Seq | Operation      | Setup | Setup Cost | # Ops | Time | $/Part |  
• Install rows → label = `Install` (no substitution)  
• Outside Process rows →  
 → Setup = `-`  
 → Setup Cost = `-`  
 → # Ops = `-`  
 → Time = `-`  
 → $/Part = `[flat area] × $/sqin` from `OutsideProcess[UFG]_sQL.csv`  

Restrictions:  
• No diff view or highlight  
• No commentary or summary permitted  
• Sequence must reindex completely  

Purpose:  
Preserves deterministic rendering and structural consistency after inserts.

Source: SubProg_[EMX]_REF_only.txt  
Validated In: Re-render Verification Suite v5.0  

===== END_SUB_BLOCK: [EMX006] =====





