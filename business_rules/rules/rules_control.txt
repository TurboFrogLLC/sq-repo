===== SUB_BLOCK: [SSX000] – USER AUTHENTICATION =====  
[SSX000.A] - USERNAME VALIDATION  
Status: DISABLED  
Dependencies: —  
Applies To: GPT Instructions, CSV Schema, Backend Parser, Edit Mode, Simulation Output  
Rule Scope: Logic Only  
Description:  
At session start, the system prompts the user for a username. Input is validated against the authorized list in `Usernames[UFG]_sQL.txt`.

Validation Rules:  
• Only usernames listed in the file are accepted  
• The username `flawswatter` is flagged as Developer Mode  
• All other entries, including blank or malformed input, are rejected  

Purpose:  
Enforces secure, deterministic access control using file-based username validation. Prevents unauthorized use or GPT inference paths.

Source: SubProg_[SSX]_REF_only.txt  
Validated In: Dev Test 5.2, Forced Login Rejection Audit  

---

[SSX000.B] - LOGIN FAILURE HANDLER  
Status: DISABLED  
Dependencies: [SSX000.A]  
Applies To: GPT Instructions, CSV Schema, Backend Parser, Edit Mode, Simulation Output  
Rule Scope: Logic Only  
Description:  
If the input username is not found in `Usernames[UFG]_sQL.txt`, the system halts execution and displays this exact message:  
> ⚡🐸 User not recognized. Login failed.

Purpose:  
Standardizes behavior for unauthorized logins using controlled emoji and message format.

Source: SubProg_[SSX]_REF_only.txt  
Validated In: Sim v1.0a, Invalid User Matrix  

===== END_SUB_BLOCK: [SSX000] =====
---
===== SUB_BLOCK: [SSX001] – MULTI-PART QUEUE HANDLER =====  
[SSX001.A] - MULTI-PART QUEUE RECOGNITION  
Status: DISABLED 
Dependencies: —  
Applies To: GPT Instructions, CSV Schema, Backend Parser, Edit Mode, Simulation Output  
Rule Scope: Logic Only  
Description:  
When multiple parts are detected during file upload, each part is parsed and added to a Multi-Part Queue (MPQ).  
The MPQ processes quotes one part at a time — batch mode is not allowed.  
There is no visual indicator for the queue contents.

Purpose:  
Enables deterministic, file-based part stack processing while hiding internal GPT queue logic from user view.

Source: SubProg_[SSX]_REF_only.txt  
Validated In: Sim v1.0a (Multi-Part Upload)  

---

[SSX001.B] - MPQ CONTINUATION TRIGGER  
Status: DISABLED  
Dependencies: [SSX001.A]  
Applies To: GPT Instructions, CSV Schema, Backend Parser, Edit Mode, Simulation Output  
Rule Scope: Logic Only  
Description:  
After a quote summary is displayed, the system checks the MPQ for any remaining unquoted parts.  
If present, it bypasses the upload step and automatically loads the next part for quoting.

Purpose:  
Ensures seamless, sequential quoting of multiple uploaded parts.  
Allows the `[New Quote]` command to act as both reset and progression controller.

Source: SubProg_[SSX]_REF_only.txt  
Validated In: Sim v1.0a (Multi-Quote Sequence)  

===== END_SUB_BLOCK: [SSX001] =====
---
===== SUB_BLOCK: [SSX002] – FILE ROUTING + PARSE FALLBACK =====
  
[SSX002.A] – FILE PRIORITY RULES  
Status: ENFORCED  
Dependencies: —  
Applies To: GPT Instructions, CSV Schema, Backend Parser, Edit Mode, Simulation Output  
Rule Scope: Parsing Precedence  
Description:  
When multiple file types are uploaded (e.g., STEP + PDF, DXF + PDF), extractable values are resolved in the following strict priority order:

• Material Type → trust PDF  
• Material Thickness → trust PDF  
• Notes / Annotations → trust PDF  
• Outside Processes → trust PDF  
• Hardware, Countersinks, Taps → trust PDF  
• Flat Pattern Size → trust STEP or DXF  
• Form Count (# Ops) → trust STEP or DXF  
• Part Weight → calculated using flat size + PDF thickness  

If a conflict exists between STEP/DXF and PDF, the PDF wins.

Purpose:  
Ensures deterministic parsing when overlapping file data is present.

Source: SubProg_[SSX]_REF_only.txt  
Validated In: Sim v1.0a (Dual File Test)  

---

[SSX002.B] – GPT OUTSIDE PROCESS INFERENCE  
Status: ENFORCED  
Dependencies: [SSX002.A]  
Applies To: GPT Instructions, CSV Schema, Backend Parser, Edit Mode, Simulation Output  
Rule Scope: Inference Logic  
Description:  
GPT may autofill outside processes from parsed title blocks or annotations. If the OP does not match a known entry:

• Add to OP display block  
• Tag under operation: `Misc`  
• No price is applied unless user edits manually  

Purpose:  
Allows unpriced OPs to surface visibly for user review.

Source: SubProg_[SSX]_REF_only.txt  
Validated In: Sim v1.0a (Print-Only OP Injection)  

---

[SSX002.C] – UNMAPPED DXF LAYER FALLBACK  
Status: ENFORCED  
Dependencies: —  
Applies To: GPT Instructions, CSV Schema, Backend Parser, Edit Mode, Simulation Output  
Rule Scope: File Parsing  
Description:  
If a DXF file contains layers that do not map to known operations (e.g., L-EXTERNAL, C-FORM), GPT must discard these layers **without** triggering an error.

Rules:  
• Unknown DXF layers are ignored  
• No fallback inference or guessing allowed  
• User is not alerted to discarded layers unless debugging is enabled  

Purpose:  
Prevents malformed or nonstandard DXF layers from breaking part extraction.

Source: SubProg_[SSX]_REF_only.txt  
Validated In: DXF Layer Rejection Sim v1.1  

---

[SSX002.D] – REDUNDANT FIELD CONFLICT HANDLER  
Status: ENFORCED  
Dependencies: [SSX002.A]  
Applies To: GPT Instructions, CSV Schema, Backend Parser, Edit Mode, Simulation Output  
Rule Scope: File Merge Safety  
Description:  
When a field is extracted from both STEP and PDF (e.g., flat size, note fields), GPT must enforce the following:

• PDF value always takes priority  
• STEP/DXF values are retained silently for comparison  
• If PDF field is blank or malformed → fallback to STEP  
• If both are missing → field is marked as `null`

Purpose:  
Guarantees consistent resolution of field conflicts across file types.

Source: SubProg_[SSX]_REF_only.txt  
Validated In: Merge Conflict Safety Test v2.0  

---

[SSX002.E] – FLAT SIZE OVERRIDE HANDLER  
Status: ENFORCED  
Dependencies: —  
Applies To: GPT Instructions, CSV Schema, Backend Parser, Edit Mode, Simulation Output  
Rule Scope: Override Resolution  
Description:  
If flat size is extracted from both PDF and CAD, the PDF value overrides **only if**:

• PDF size is well-formed (inches)  
• Both X and Y dimensions are numeric and ≥ 0.01  
• Label includes a unit (e.g., “in”, “inches”)  

Otherwise → fallback to STEP or DXF value  

Purpose:  
Protects against malformed PDF field extractions while preserving valid manual size overrides.

Source: SubProg_[SSX]_REF_only.txt  
Validated In: Flat Size Override Sim v1.1  

---

[SSX002.F] – THICKNESS UNITS PARSER  
Status: ENFORCED  
Dependencies: —  
Applies To: GPT Instructions, CSV Schema, Backend Parser, Edit Mode, Simulation Output  
Rule Scope: PDF Parsing  
Description:  
Material thickness extracted from PDF must be normalized as a float in inches.

Accepted Units:  
• `GA` (gauge) → map via Material[UFG]_sQL.csv  
• `mm` → convert to inches (1mm = 0.03937 in)  
• `in`, `inches` → parse directly  

Rules:  
• GA must include base material for correct lookup  
• Invalid/missing units → discard field  
• Result must be stored as a float (e.g., 0.0625)  

Purpose:  
Ensures that all thickness values are machine-computable and valid across file formats.

Source: SubProg_[SSX]_REF_only.txt  
Validated In: Thickness Unit Parse Sim v2.0  

---

[SSX002.G] – PDF FIELD TRIMMER  
Status: ENFORCED  
Dependencies: —  
Applies To: GPT Instructions, CSV Schema, Backend Parser, Edit Mode, Simulation Output  
Rule Scope: Field Cleanup  
Description:  
Trims all extracted PDF fields to remove formatting artifacts.

Cleanup Rules:  
• Strip leading/trailing whitespace  
• Remove colons, brackets, and trailing units from labels  
• Collapse internal whitespace to single space  
• Preserve casing, symbols, and material formatting  
• Remove footnotes or superscripts (e.g., “*”, “†”, etc.)

Applies To:  
• Material  
• Description  
• Part Number  
• Notes  
• Customer  

Purpose:  
Standardizes PDF-derived text before quoting. Prevents parsing errors due to formatting debris.

Source: SubProg_[SSX]_REF_only.txt  
Validated In: PDF Text Cleanup Audit v1.2  

===== END_SUB_BLOCK: [SSX002] =====
---
===== SUB_BLOCK: [SSX003] – QUOTE CONTINUATION LOGIC =====  
[SSX003.A] – NEXT QUOTE / SESSION RESET HANDLER  
Status: ENFORCED  
Dependencies: —  
Applies To: GPT Instructions, CSV Schema, Backend Parser, Edit Mode, Simulation Output  
Rule Scope: Post-quote prompt loop, quote memory purge  
Description:  
Handles post-quote navigation logic. After quote finalization and summary display, the system offers the user a set of explicit keypress options to continue quoting or exit the session.

Command Format:  
→ Type [ s ] to Save Quote  
→ Type [ n ] to Start New Quote  
→ Type [ q ] to Quit

Trigger Behavior:  
• On `n` (New Quote):  
 → Fully clear `quote_metadata`  
 → Reset all internal state objects  
 → Return to start prompt: “Enter access code or type demo to start quoting”

• On `q` (Quit):  
 → Terminate quoting session  
 → Do not offer further prompts  
 → Do not clear stored quote history (for scroll-back access)

• On `s` (Save Quote):  
 → Trigger quote export using active metadata snapshot  
 → Prompt user with save type: TXT or PDF  
 → Return to post-save menu with S/N/Q prompt again

Enforcement Notes:  
• New Quote must be clean — no partial metadata may be retained  
• No system state (e.g. last part, last material) should bleed into next quote  
• Save must be completed before another quote can be started  
• All logic must originate from runtime state — no memory fallback

Purpose:  
Controls deterministic navigation between quote cycles. Prevents state bleed or residual metadata from polluting new quotes.

Source: SubProg_[SSX]_REF_only.txt  
Validated In: Sim v1.0a (Quote Lifecycle Control)  

---

[SSX003.B] – SESSION LOGGING + RECALL INDEX  
Status: ENFORCED  
Dependencies: —  
Applies To: GPT Instructions, CSV Schema, Backend Parser, Edit Mode, Simulation Output  
Rule Scope: In-session quote recall, edit tracking  
Description:  
Enables persistent in-session storage of previously completed quotes, including metadata snapshots and timestamps. These stored entries can be manually recalled or used to regenerate quotes.

Session Stack Logic:  
• Upon quote finalization or reset:  
 → Push active `quote_metadata` snapshot into `quote_stack[]`  
 → Tag with part number and timestamp (if available)  
 → Store as deep copy to protect against mutation during edits

Structure of `quote_stack[]` entry:
```json
{
  "part_number": "BRKT-001",
  "timestamp": "2025-07-31T16:28:00Z",
  "quote_metadata": { ... }
}
Purpose:
Preserves a complete record of past quotes during the active session. Enables edit recovery, replay, and audit alignment.
Source: SubProg_[SSX]_REF_only.txt
Validated In: Session Recall and Replay Stack v2.1

===== END_SUB_BLOCK: [SSX003] =====

===== SUB_BLOCK: [IFX000] – IMPORT FRAMEWORK CONTROL ===== 
 
[IFX000.A] – FILE IMPORT ENTRY POINT  
Status: ENFORCED  
Dependencies: —  
Applies To: GPT Instructions, CSV Schema, Backend Parser, Edit Mode, Simulation Output  
Rule Scope: File Parsing  
Description:  
Handles the classification and dispatch of uploaded files at session start. Each file is routed into a specific parser or metadata injection routine based on its format.

Routing Rules:  
• `.STEP` or `.step` → forward to unfolding microservice  
• `.DXF` → forward to DXF parser for flat geometry  
• `.PDF` → scanned for title block, material, finish, and outside process entries  
• `.TXT` or `.JSON` → scanned for embedded `quote_metadata`  
• Invalid or unsupported formats → trigger error  

Behavior:  
• Multi-file upload supported; order of processing is enforced  
• File origin (drag-drop or dialog) has no effect on logic  
• Any detected `quote_metadata` is validated before use  
• This rule performs file classification only — not parsing  

Purpose:  
Ensures deterministic routing of uploaded files. Prevents quote logic from running on malformed or unsupported content.

Source: SubProg_[IFX]_REF_only.txt  
Validated In: Format Intake Stack Sim v2.0  

===== END_SUB_BLOCK: [IFX000] =====
---
===== SUB_BLOCK: [IFX001] – QUOTE METADATA PARSE & VALIDATION ===== 
 
[IFX001.A] – METADATA DETECTION AND SCHEMA CHECK  
Status: ENFORCED  
Dependencies: —  
Applies To: GPT Instructions, CSV Schema, Backend Parser, Edit Mode, Simulation Output  
Rule Scope: File Parsing  
Description:  
Scans uploaded `.txt` or `.json` files for embedded `quote_metadata`. Validates structure before injecting data into the session.

Detection Logic:  
• `.json` → root-level keys must include:  
 – `part_number`  
 – `material`  
 – `thickness`  
 – `flat_size`  
 – `operation_sequence`  

• `.txt` → must contain the marker `quote_metadata:` followed by a valid JSON block  

Validation Rules:  
• Required fields must be non-null and structurally valid  
• If schema check fails → metadata is ignored silently  
• Only one `quote_metadata` block is evaluated per import  

Purpose:  
Guarantees that only valid and complete metadata snapshots are accepted into the session. Prevents malformed field injection.

Source: SubProg_[IFX]_REF_only.txt  
Validated In: Metadata Parse Sim v3.0  

===== END_SUB_BLOCK: [IFX001] =====
---
===== SUB_BLOCK: [IFX002] – QUOTE METADATA INJECTION ===== 
 
[IFX002.A] – MEMORY POPULATION FROM METADATA  
Status: ENFORCED  
Dependencies: —  
Applies To: GPT Instructions, CSV Schema, Backend Parser, Edit Mode, Simulation Output  
Rule Scope: Reload Handler  
Description:  
Injects quote state into the session from a pre-validated `quote_metadata` object. Bypasses geometry parsing and rehydrates the quote in memory.

Injected Fields:  
• `part_number`  
• `material_type`  
• `material_thickness`  
• `flat_size_x`, `flat_size_y`  
• `flat_area`  
• `part_weight`  
• `description`  
• `operation_sequence`  
• `hardware`  
• `outside_processes`  
• `quote_date`  
• `username`

Enforcement Rules:  
• All injected values are treated as read-only session memory  
• Any unrecognized fields are discarded  
• No calculations, formatting, or pricing is triggered by this rule  
• Injection fails silently if critical fields are invalid  

Restrictions:  
• This rule performs no computation or dynamic recomposition  
• Output rendering is deferred to post-injection logic  
• No GPT-derived assumptions or field patching allowed  

Purpose:  
Supports safe quote recall using prior session data or imported quote files. Ensures only deterministic data enters the execution layer.

Source: SubProg_[IFX]_REF_only.txt  
Validated In: IFX Inject Replay Sim v1.0  

===== END_SUB_BLOCK: [IFX002] =====
---
===== SUB_BLOCK: [IFX003] – PARTIAL METADATA FALLBACK HANDLER ===== 
 
[IFX003.A] – NON-CRITICAL FIELD NORMALIZER  
Status: ENFORCED  
Dependencies: —  
Applies To: GPT Instructions, CSV Schema, Backend Parser, Edit Mode, Simulation Output  
Rule Scope: Quote Reload  
Description:  
Handles optional fields in the `quote_metadata` object by assigning safe fallbacks if they are missing or null. Required fields must already be validated before this logic executes.

Fields eligible for fallback:  
• `description` → default: empty string  
• `quote_date` → default: empty string  
• `username` → default: `"anonymous"`  
• `hardware` → default: empty array  
• `outside_processes` → default: empty array  
• `part_weight` → default: `null`  
• `flat_area` → default: `null`

Rules:  
• No fallback is applied to critical quoting fields  
• Substitutions are silent — no warnings are displayed  
• This logic executes only if `quote_metadata` is already structurally valid  
• This rule cannot generate or infer new data  

Purpose:  
Allows partially saved or manually edited quotes to reload without triggering quote errors. Ensures consistent quote behavior despite missing non-critical fields.

Source: SubProg_[IFX]_REF_only.txt  
Validated In: IFX003 Fallback Sim 1.2  

===== END_SUB_BLOCK: [IFX003] =====
---
===== SUB_BLOCK: [IFX004] – TRACE SNAPSHOT LOGGER ===== 
 
[IFX004.A] – QUOTE TRACE LOGGER  
Status: ENFORCED  
Dependencies: —  
Applies To: GPT Instructions, CSV Schema, Backend Parser, Edit Mode, Simulation Output  
Rule Scope: Universal Trace Export  
Description:  
Creates a complete snapshot of the quote session state upon save. Captures all user-visible fields and internal system data for audit and replay.

Trace Contents:  
• `quote_metadata` (verbatim copy)  
• File names and types uploaded  
• Timestamp of save event  
• Username (or `"orphan"` fallback)  
• File classification result (PDF, STEP, etc.)  
• System version and sandbox ID  
• `session_trace[]` (user/system interactions)  
• `operation_breakdown[]`  
• `quote_totals` (all tiers)

Behavior:  
• Trace file is written automatically during Save  
• Stored as `.trace` in system directory  
• Trace is not user-accessible but supports replay and debugging  

Purpose:  
Preserves tamper-proof history of all saved quotes. Enables secure audit logging and system validation.

Source: SubProg_[IFX]_REF_only.txt  
Validated In: TraceKit Log Sim v1.3  

---

[IFX004.B] – TRACE FILE STRUCTURE & PATH  
Status: ENFORCED  
Dependencies: [IFX004.A]  
Applies To: GPT Instructions, CSV Schema, Backend Parser, Edit Mode, Simulation Output  
Rule Scope: Trace Dispatch Path  
Description:  
Defines how and where trace files are saved. Ensures naming consistency and file accessibility for the replay engine.

File Format:  
• Saved as:  
 `/mnt/data/<username>/<username>_<HHMMSS>_<MMDDYYYY>.trace`  
• Uses UTC timestamp unless provided in metadata  
• Username pulled from `quote_metadata`; fallback = `"orphan"`  
• File path is deterministic and human-readable  

Rules:  
• No hashing, compression, or obfuscation  
• Only `.trace` extension permitted  
• One trace per quote event  

Purpose:  
Guarantees consistent trace file management and auditability.

Source: SubProg_[IFX]_REF_only.txt  
Validated In: Trace File Path Sim v2.0  

---

[IFX004.C] – TRACE PAYLOAD DISPATCH  
Status: ENFORCED  
Dependencies: [IFX004.A], [IFX004.B]  
Applies To: GPT Instructions, CSV Schema, Backend Parser, Edit Mode, Simulation Output  
Rule Scope: Remote Microservice Call  
Description:  
Handles the push of the trace file payload to the external trace collector microservice.

Target Endpoint:  
`https://shopquote-trace-collector.onrender.com/log/session_trace`  
• Content-Type: `application/json`  
• POST body = full trace payload  
• Success response must include:  
 → `"status": "ok"`  
 → `"path": "/mnt/data/<username>/<filename>.trace"`

Rules:  
• Dispatch is triggered after trace file generation  
• Push errors do not block save behavior  
• Applies to all users regardless of access tier  

Purpose:  
Enables secure offloading of trace data for compliance logging, dev review, and error triage.

Source: SubProg_[IFX]_REF_only.txt  
Validated In: Remote Sync Audit Stack v1.2  

===== END_SUB_BLOCK: [IFX004] =====

===== SUB_BLOCK: [SEC000] – EXPORT SANITIZATION + STRUCTURE LOCKING =====  

[SEC000.A] – TEXT EXPORT SANITIZER  
Status: ENFORCED  
Dependencies: —  
Applies To: GPT Instructions, CSV Schema, Backend Parser, Edit Mode, Simulation Output  
Rule Scope: TXT File Export Only  
Description:  
Before exporting a `.txt` quote file, the system must sanitize the output by removing any of the following:

Forbidden Patterns:  
• GPT-specific phrases (e.g., "As an AI model…")  
• Markdown links or formatting  
• Emoji not in the official UFG UI set  
• OpenAI/ChatGPT branding  
• Internal prompt history or system logs  
• HTML, LaTeX, or markdown block syntax

Sanitization Behavior:  
• All forbidden patterns are stripped silently  
• Fields are retained as plaintext  
• Final file must be clean, readable, and audit-safe  
• No alternate encodings or export formatting allowed  

Purpose:  
Prevents export of system-specific artifacts, branding, or GPT-originated language into quote files.

Source: SubProg_[SEC]_REF_only.txt  
Validated In: TXT Filter Test v1.4  

---

[SEC000.B] – PDF STRUCTURE LOCKER  
Status: ENFORCED  
Dependencies: —  
Applies To: GPT Instructions, CSV Schema, Backend Parser, Edit Mode, Simulation Output  
Rule Scope: PDF Export Layout  
Description:  
Enforces locked structure and visual consistency for all PDF quote exports.

Rules:  
• Page size: US Letter (8.5" × 11")  
• Font: Helvetica or Arial, 10pt–12pt  
• Title section: includes customer, part number, quote date  
• One quote per page (no multiparts)  
• All monetary fields = `$X.XX`  
• Table layout must mirror on-screen Quote Breakdown  
• Part Summary must precede Quote Breakdown  
• Footer includes:  
 – Exported by [username]  
 – Timestamp  
 – `"Generated using ShopQuoteLite"`

Restrictions:  
• No dynamic layout, scaling, or embedded images  
• No page breaks inside tables  
• No hyperlinks, form fields, or branding inserts allowed  

Purpose:  
Enforces deterministic PDF generation behavior. Protects against formatting drift, accidental branding, or inconsistent quoting.

Source: SubProg_[SEC]_REF_only.txt  
Validated In: PDF Layout Stability Suite v2.0  

===== END_SUB_BLOCK: [SEC000] =====
---
===== SUB_BLOCK: [SEC001] – ACCESS TIER ENFORCEMENT =====
  
[SEC001.A] – USERNAME TIER MAPPING  
Status: ENFORCED  
Dependencies: —  
Applies To: GPT Instructions, CSV Schema, Backend Parser, Edit Mode, Simulation Output  
Rule Scope: Role Control  
Description:  
At session start, the user’s input username must be matched to a known access tier using `Usernames[UFG]_sQL.txt`.

Access Levels:  
• `flawswatter` → developer tier  
• `roger` → general user tier  
• All others → rejected (see [SSX000.B])  

Behavior:  
• Access tier is used to enable or restrict privileged features  
• Case-insensitive match  
• If username not found → session is terminated  

Purpose:  
Establishes deterministic role-based control across quoting features.

Source: SubProg_[SEC]_REF_only.txt  
Validated In: Tier Gate Sim v1.1  

---

[SEC001.B] – DEV FEATURE LOCKOUT  
Status: ENFORCED  
Dependencies: [SEC001.A]  
Applies To: GPT Instructions, CSV Schema, Backend Parser, Edit Mode, Simulation Output  
Rule Scope: Feature Guard  
Description:  
The following quoting features are restricted to developer-tier users only:

• Markup override commands  
• Raw memory injection  
• Direct cost multiplier edit  
• Manual field patching  
• Trace dispatch confirmation

Rules:  
• If access tier ≠ developer → these features are hidden  
• No messages or visual indication of hidden features  
• Attempts to invoke these by other users are ignored silently  

Purpose:  
Prevents exposure of nonpublic tools and pricing controls to standard users.

Source: SubProg_[SEC]_REF_only.txt  
Validated In: Feature Visibility Suppression Test v2.0  

===== END_SUB_BLOCK: [SEC001] =====

===== SUB_BLOCK: [SAV000] – SAVE / EXPORT CONTROL ===== 
 
[SAV000.A] – TXT/PDF EXPORT FILENAME FORMATTER  
Status: ENFORCED  
Dependencies: —  
Applies To: GPT Instructions, CSV Schema, Backend Parser, Edit Mode, Simulation Output  
Rule Scope: Export Filename Logic  
Description:  
Defines the export filename structure for quotes saved as `.txt` or `.pdf`.

Format:  
`sQ-[part_number]_[DD-MM-YYYY].[ext]`  
→ Prefix: `sQ-`  
→ `[part_number]`: pulled directly from `quote_metadata.part_number`  
→ `[DD-MM-YYYY]`: UTC system date at export time  
→ Extension: `.txt` or `.pdf`

Examples:  
• `sQ-BRKT-42_04-08-2025.txt`  
• `sQ-WDG-101_04-08-2025.pdf`

Rules:  
• No user inference or abbreviation  
• No timestamp or hash added  
• Filename must be generated automatically at the moment of export  
• User may rename before saving, but the default must follow this pattern  

Purpose:  
Standardizes exported quote filenames for traceability, recall, and clean versioning.

Source: SubProg_[SAV]_REF_only.txt  
Validated In: Save Filename Render Audit v2.0  

---

[SAV000.B] – SAVE PERMISSION LOCK  
Status: ENFORCED  
Dependencies: —  
Applies To: GPT Instructions, CSV Schema, Backend Parser, Edit Mode, Simulation Output  
Rule Scope: Export Readiness  
Description:  
Prevents quote export unless the quote is complete and in a finalized state.

Save Allowed Only If:  
• `quote_metadata` is present and schema-valid  
• Edit Mode is not active  
• Quote Breakdown has been rendered  
• Summary View is present  
• Export format = `.txt` or `.pdf`

Enforcement Behavior:  
• If any requirement fails → Save button/trigger is suppressed  
• No errors or user prompts are shown  
• Save is re-enabled automatically when all requirements are met  

Purpose:  
Ensures quotes are never saved in an unstable or partial state.

Source: SubProg_[SAV]_REF_only.txt  
Validated In: Export Readiness Lock Sim v1.3  

---

[SAV000.C] – CLIENT-SIDE FILENAME COLLISION GUARD  
Status: ENFORCED  
Dependencies: [SAV000.A]  
Applies To: GPT Instructions, CSV Schema, Backend Parser, Edit Mode, Simulation Output  
Rule Scope: Local File Save  
Description:  
If a quote is exported using the default filename and a file of the same name already exists locally, the system must prompt for overwrite confirmation.

Trigger:  
• Local client detects filename collision at save time  
• Applies only to manual `.txt` or `.pdf` downloads  

Prompt:  
> File already exists. Overwrite?  
• If confirmed → save proceeds, existing file is replaced  
• If declined → reopen filename dialog  

Rules:  
• This rule applies only to local downloads  
• No GPT logic may simulate or infer file system state  
• No impact on server- or cloud-based saves  

Purpose:  
Prevents unintentional file overwrites on local devices during quote export.

Source: SubProg_[SAV]_REF_only.txt  
Validated In: Client Save Collision Guard Sim v1.1  

===== END_SUB_BLOCK: [SAV000] =====



