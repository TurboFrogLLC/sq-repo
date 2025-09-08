===== AMENDMENTS TO rules_quote_export.txt =====

[QBX000.A] – QUOTE BREAKDOWN TABLE FORMAT  
• Row order and fixed tiers (1,10,25,50) locked.  
• No extra columns/rows permitted, even in Dev Mode.  

[QBX000.B] – COST SOURCE ENFORCEMENT  
• Locked: all math must use rates from CSV + overlays.  
• Markup always uses configured percent; no overrides.

[QBX002] – MARKUP OVERRIDE (DEV ONLY)  
• STRUCK. Markup override feature removed.  
• Markup row = locked global percent (from Rates overlay).  

[QBX004.A] – METADATA EXPORT  
• Overlay snapshot JSON (`csv-overlay-1`) must be appended after `quote_metadata`.  
• Both TXT and PDF exports must include this block verbatim.  
• Format:  
=== OVERLAY SNAPSHOT START (csv-overlay-1) ===
{ ... }
=== OVERLAY SNAPSHOT END ===

pgsql
Copy code

[SEC000.B] – PDF STRUCTURE LOCKER  
• Add: Appendix must include overlay snapshot after metadata.  