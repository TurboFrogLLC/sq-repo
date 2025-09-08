===== AMENDMENTS TO rules_ops_ui.txt =====

[OPR001] – OPERATION BREAKDOWN DISPLAY  
• No debug math sliders or Dev-only widgets allowed.  
• Runtime/setup values come only from CSV masters or valid overlays.  

[OPR002.B] – INPUT ALIAS VALIDATION  
• Session overlays may extend valid alias lists.  
• No GPT inference or free-text tolerance beyond overlay definitions.  

[OPR003.A] – MANDATORY OPERATIONS  
• Still enforced (Plan, Final Insp., Package).  
• Cannot be bypassed via Dev flags.  

[EMX000–006] – EDIT MODE FLOWS
• All prompts remain intact.
• Dev-only shortcuts/hidden commands are disabled.
• User can only edit via sanctioned flows; no raw field injection.

[OPR004] – ENHANCED OPERATIONS EDITOR IMPLEMENTATION
• Successfully ported exact Streamlit operations editor logic to JavaScript/HTML
• Implemented sophisticated conditional dropdown system for hardware/outside process operations
• Added smart detail preservation when switching between operation types
• Real-time buffer management with working copy isolation
• Panel-based UI architecture with per-row editing containers
• Deterministic key naming for stable UI updates (op-${i}-select pattern)
• Professional styling with hover effects and responsive design

[OPR005] – CONDITIONAL LOGIC SYSTEM
• Hardware dropdown appears only for Install operations (PEM, FH, CLS, Rivet, Screw, Nut, etc.)
• Outside Process dropdown appears only for Outside Process operations (Anodize, Powdercoat, etc.)
• Smart detail preservation: existing hardware selections remembered when switching operation types
• Dynamic show/hide based on selected operation type with smooth transitions
• Preloaded dropdown options from business-approved lists

[OPR006] – STATE MANAGEMENT & BUFFER SYSTEM
• Working buffer (opsEditBuffer) isolates edits from canonical data (operationsData)
• Save commits buffer to canonical data with resequencing
• Cancel discards buffer changes, restoring original state
• Real-time updates within buffer without affecting saved data
• Automatic resequencing after structural changes (insert/move/delete)

[OPR007] – ROW MANAGEMENT ACTIONS
• Move Up/Down: Reorder operations with automatic resequencing
• Insert Above/Below: Add new operations at specific positions
• Delete Row: Remove operations with minimum validation (keeps at least one)
• All actions work on buffer, require Save to commit changes
• Visual feedback and disabled states for boundary conditions

[FUTURE] – ADVANCED BEND EDITING SCALING
• flatExtract may evolve into surgical bend editing tool for future versions
• Individual bend manipulation (angle, radius, type: HEM, JOG, OFFSET, etc.)
• Import parsed bend data for granular editing without re-processing CAD files
• Foundation for traveller module with specific bend operations
• User option between simple Form operations vs detailed bend breakdowns
• Enable revision changes by editing individual bends instead of re-uploading
• JSON data structure supports bend arrays for rehydration and persistence

[OPR008] – DYNAMIC RULES ENGINE IMPLEMENTATION ✅
• Phase 2 implementation: Context-aware validation and suggestions system
• Material-specific rules: Different validation for CRS vs Aluminum vs Stainless Steel
• Thickness-based logic: Rules adapt based on gauge (0.0478" vs 0.125" vs 0.250")
• Machine capability integration: Rules based on available equipment and processes
• Real-time feedback: Immediate validation as users make selections
• Smart suggestions: Operation sequencing recommendations based on material/thickness
• Cost optimization: Automatic flagging of inefficient operation combinations
• Manufacturability assurance: Prevent impossible combinations before quoting

[OPR009] – RULES ENGINE ARCHITECTURE ✅
• Rules evaluation system: Context-aware validation engine implemented
• Material-thickness combinations: Predefined valid operation sets loaded
• Real-time feedback UI: Visual indicators for rule violations in operations page
• Smart suggestions panel: Operation sequencing recommendations displayed
• Cost optimization flags: Highlight inefficient combinations detected
• Manufacturability validation: Prevent impossible process combinations

[OPR010] – BASIC UI DEPLOYMENT ✅
• Rules engine UI: Integrated into operations page with expandable section
• Validation status display: Real-time status indicators implemented
• Smart suggestions interface: Basic suggestion display and application
• Backend integration: Rules evaluation functions connected to UI
• State management: Rules engine state variables properly managed
