# ShopQuote Master UI Format Specification

## Overview
This document serves as the **source of truth** for the ShopQuote UI layout. It defines the complete user interface structure, layout proportions, and interaction patterns for the Taipy-based web application.

## Global App Layout (Fixed Structure)

### Header (Full Width, Top of Page)
- **HTML Structure**: `<div class='app-header'><h1><span style='color:#111;'>shop</span><span style='color:#22c55e;'>Quote</span></h1><div class="company-tag">powered by Turbo Frog LLC</div></div>`
- **Always Visible**: Across all pages
- **Content**: Brand name with company tag
- **Background**: White to black gradient (left to right)
- **Positioning**: Fixed at top with full viewport width

### Sidebar (1/3 Width, Left Side)
- **Fixed Width**: 33.33% of viewport
- **Content**: Changes based on active page (see per-page specs below)
- **Includes**: Navigation elements, inputs, and buttons

### Main Window (2/3 Width, Right Side)
- **Dynamic Content**: All pages rendered here
- **Page Transitions**: Seamless replacement (Welcome → Part Summary → Operations → Quote Breakdown → Summary)
- **No Fixed Content**: All generated dynamically based on user actions

### Pages List (Navigation Flow)
1. **Welcome** (`welcome.html`) - startup/default page
2. **Part Summary** (`part-summary.html`) - part information display
3. **Operations** (`operations.html`) - manufacturing operations management
4. **Quote Breakdown** (`quote-breakdown.html`) - cost analysis and markup
5. **Quote Summary** (`quote-summary.html`) - final professional quote
6. **Settings** (`settings.html`) - application configuration

## Navigation Rules

### General Navigation
- **Forward/Backward**: Via sidebar buttons or actions
- **Quote # Mandatory**: Required before proceeding beyond Welcome or Part Summary
- **File Processing**: Automatically transitions from Welcome to Part Summary
- **Manual Mode**: Bypasses file upload, goes directly to Part Summary with blank fields
- **Settings Page**: Modal/overlay (does not replace main window)

### Settings Integration
- **Settings Button**: ID `btn-settings` appears on every sidebar except Settings page itself
- **Behavior**: Opens Settings page in modal overlay
- **Settings Page Sidebar**: Shows only Settings-specific elements (no Settings button)

## Sidebar Layout Per Page (top → bottom order; deterministic)

### Welcome Page (startup + new quote)
1. **Brand Header** (in sidebar)
   - HTML div: `<div class='sidebar-brand'><h2><span style="color: white;">shop</span><span class="brand-quote">Quote</span></h2></div>`
   - Background: White to black gradient (left to right)
   - Always visible.

2. **Quote # Input**
   - ID: `in-quote-number`
   - Placeholder: `Enter Quote #`
   - Behavior:
     • At startup/new quote, user may enter any combination of letters, numbers, symbols.
     • This Quote # is **mandatory**: the user must enter a valid value before proceeding to any other tab (Part Summary, Operations, etc.).
     • When the user processes a file or chooses Manual Mode, the Quote # becomes constant for the session.
     • If the user generates a new quote, a new sequential number is generated automatically.
     • User-defined format is preserved; only the trailing number increments by 1.
     • If the user attempts to proceed without entering a Quote #, a warning appears and navigation is blocked.

3. **File Upload & Processing**
   - ID: `btn-upload-files` (multi-file uploader).
   - ID: `btn-process-files` (button).
   - Visible only when `active_page = Welcome`.
   - Behavior: On process, transition to Part Summary page in main window.

4. **Manual Mode**
   - ID: `btn-manual-mode` (button).
   - Behavior:
     • Takes the user directly to the **Part Summary** page.
     • All fields in Part Summary are blank (no parsing).
     • Quote # must still be entered before proceeding further.

5. **Settings Button**
   - ID: `btn-settings` (button).
   - Behavior: Opens Settings modal.

### Part Summary Page
1. **Brand Header** (in sidebar)
   - Same as above.

2. **Quote # Display**
   - ID: `display-quote-number`
   - Shows the entered/constant Quote #.

3. **Navigation Buttons**
   - ID: `btn-back-to-welcome` (back to Welcome).
   - ID: `btn-next-to-operations` (proceed to Operations).

4. **Settings Button**
   - ID: `btn-settings` (button).

### Operations Page
1. **Brand Header** (in sidebar)
   - Same as above.

2. **Quote # Display**
   - ID: `display-quote-number`

3. **Navigation Buttons**
   - ID: `btn-back-to-part-summary` (back to Part Summary).
   - ID: `btn-next-to-quote-breakdown` (proceed to Quote Breakdown).

4. **Settings Button**
   - ID: `btn-settings` (button).

### Quote Breakdown Page
1. **Brand Header** (in sidebar)
   - Same as above.

2. **Quote # Display**
   - ID: `display-quote-number`

3. **Navigation Buttons**
   - ID: `btn-back-to-operations` (back to Operations).
   - ID: `btn-next-to-summary` (proceed to Summary).

4. **Settings Button**
   - ID: `btn-settings` (button).

### Summary Page
1. **Brand Header** (in sidebar)
   - Same as above.

2. **Quote # Display**
   - ID: `display-quote-number`

3. **Navigation Buttons**
   - ID: `btn-back-to-quote-breakdown` (back to Quote Breakdown).
   - ID: `btn-new-quote` (start new quote, reset to Welcome).

4. **Settings Button**
   - ID: `btn-settings` (button).

### Settings Page (Modal Overlay)
1. **Settings Header**
   - HTML div: `<div class='settings-header'><h2>Settings</h2></div>`

2. **Settings Options** (e.g., theme, preferences)
   - ID: `settings-theme` (dropdown).
   - ID: `settings-save` (button).

3. **Close Button**
   - ID: `btn-close-settings` (closes modal, returns to previous page).

### 2. Part & Operations Page Layout

#### Sidebar (1/3rd width) - Navigation & Quick Actions
```html
<|sidebar|>
# 🏭 ShopQuote

<|in-quote-number|input|value={quote_number}|label=Quote #|>

## 🧭 Navigation
<|🏠 Home|button|on_action=navigate_to_home|>
<|📄 Part & Ops|button|on_action=navigate_to_part_ops|active|>
<|📊 Quote Breakdown|button|on_action=navigate_to_quote_breakdown|>
<|📋 Summary|button|on_action=navigate_to_summary|>
<|⚙️ Settings|button|on_action=navigate_to_settings|>

## ⚙️ Quick Actions
<|📤 Upload Files|button|on_action=show_file_upload|>
<|🔄 New Quote|button|on_action=start_new_quote|>

## 🔧 System Status
**OCR Engine:** ✅ Active
**File Parsers:** ✅ Ready
**Database:** ✅ Connected
|sidebar|>
```

#### Main Content (2/3rds width) - Part Summary & Operations
```html
<|main|>
# 📄 Part & Operations

<!-- Part Summary - Always Visible -->
<|Part Summary|expandable|expanded|>
## 📋 Part Summary
**Quote #:** {quote_number}
Customer: {quote_data.customer or '—'}
Part Number: {quote_data.part_number or '—'}
Material: {quote_data.material or '—'}
Thickness: {format_thickness(quote_data.thickness_in)}
Flat Size: {format_flat_size(quote_data.flat_size_width, quote_data.flat_size_height)}
Bends: {quote_data.bend_count or '—'}
|>

<!-- File Processing - Triggered by Upload Files button -->
<|File Processing|expandable|>
## 📤 File Upload & Processing
<|{uploaded_files}|file_selector|multiple|extensions=.dxf,.step,.stp,.pdf|label=Upload CAD files|on_action=process_files|>
<|Process Files|button|on_action=process_files|>
## 📊 Processing Results
<|{processing_results}|expandable|>
|>

<!-- Data Quality - Triggered by Process Files -->
<|Data Quality|expandable|>
## 🎯 Data Quality Indicators
<|{extracted_metadata}|expandable|>
|>

<!-- Operations - Always Visible -->
<|Operations|expandable|expanded|>
## ⚙️ Operation Breakdown
<|{operations_table}|table|columns=Seq;Operation;Setup;Setup Cost;# Ops;Time;$/Part|show_all|>
<|btn-enter-edit|button|on_action=on_edit_operations|>Edit ⚙️ Operations</button>
|>

<!-- Edit Mode Prompts - Triggered by Edit Operations button -->
<|edit-mode-prompt|text|value={edit_mode_prompt}|class_name=edit-prompt|>

<!-- Hardware - Triggered by Edit Operations -->
<|Hardware|expandable|>
## 🛠️ Hardware
<|{hardware_table}|table|show_all|>
<|Add Hardware|button|on_action=show_add_hardware_dialog|>
|>

<!-- Outside Processes - Triggered by Edit Operations -->
<|Outside Processes|expandable|>
## 📦 Outside Processes
<|{outside_processes_table}|table|show_all|>
<|Add Outside Process|button|on_action=show_add_outside_process_dialog|>
|>

<!-- Action Buttons - Always Visible -->
<|btn-generate-quote|button|on_action=navigate_to_quote_breakdown|class_name=primary|>Generate 📉 Quote</button>
|main|>
```

### 3. Quote Breakdown Page Layout

#### Sidebar (1/3rd width)
```html
<|sidebar|>
# 🏭 ShopQuote

<|in-quote-number|input|value={quote_number}|label=Quote #|>

## 🧭 Navigation
<|🏠 Home|button|on_action=navigate_to_home|>
<|📄 Part & Ops|button|on_action=navigate_to_part_ops|>
<|📊 Quote Breakdown|button|on_action=navigate_to_quote_breakdown|active|>
<|📋 Summary|button|on_action=navigate_to_summary|>
<|⚙️ Settings|button|on_action=navigate_to_settings|>

## ⚙️ Quick Actions
<|📤 Upload Files|button|on_action=show_file_upload|>
<|🔄 New Quote|button|on_action=start_new_quote|>

## 🔧 System Status
**OCR Engine:** ✅ Active
**File Parsers:** ✅ Ready
**Database:** ✅ Connected
|sidebar|>
```

#### Main Content (2/3rds width)
```html
<|main|>
# 📊 Quote Breakdown

<|Quote Summary|expandable|expanded|>
**Customer:** {quote_data.customer or '—'}
**Part Number:** {quote_data.part_number or '—'}
**Material:** {quote_data.material or '—'}
**Thickness:** {format_thickness(quote_data.thickness_in)}
**Flat Size:** {format_flat_size(quote_data.flat_size_width, quote_data.flat_size_height)}
**Bends:** {quote_data.bend_count or '—'}
|>

<|Pricing Table|expandable|expanded|>
<|{pricing_table}|table|show_all|>
<|{markup_percent}% Markup|slider|min=0|max=100|on_change=update_markup|>
|>

<|btn-save-quote|button|on_action=on_save_quote|>Save Quote</button>
<|btn-new-quote|button|on_action=on_new_quote|>New Quote</button>
<|btn-quit-session|button|on_action=on_quit_session|>Quit Session</button>
|main|>
```

### 4. Summary Page Layout

#### Sidebar (1/3rd width)
```html
<|sidebar|>
# 🏭 ShopQuote

<|in-quote-number|input|value={quote_number}|label=Quote #|>

## 🧭 Navigation
<|🏠 Home|button|on_action=navigate_to_home|>
<|📄 Part & Ops|button|on_action=navigate_to_part_ops|>
<|📊 Quote Breakdown|button|on_action=navigate_to_quote_breakdown|>
<|📋 Summary|button|on_action=navigate_to_summary|active|>
<|⚙️ Settings|button|on_action=navigate_to_settings|>

## ⚙️ Quick Actions
<|📤 Upload Files|button|on_action=show_file_upload|>
<|🔄 New Quote|button|on_action=start_new_quote|>

## 🔧 System Status
**OCR Engine:** ✅ Active
**File Parsers:** ✅ Ready
**Database:** ✅ Connected
|sidebar|>
```

#### Main Content (2/3rds width)
```html
<|main|>
# 📌 Summary

Customer: {quote_data.customer or '—'}
Part Number: {quote_data.part_number or '—'}
Description: {quote_data.description or '—'}

💲 Quote Totals
- Qty 1: {format_quote_total(quote_totals.get('1', 0.00))}
- Qty 10: {format_quote_total(quote_totals.get('10', 0.00))}
- Qty 25: {format_quote_total(quote_totals.get('25', 0.00))}
- Qty 50: {format_quote_total(quote_totals.get('50', 0.00))}

<|btn-save-quote|button|on_action=on_save_quote|>Save Quote</button>
<|btn-new-quote|button|on_action=on_new_quote|>New Quote</button>
<|btn-quit-session|button|on_action=on_quit_session|>Quit Session</button>
|main|>
```

### 5. Settings Page Layout

#### Sidebar (1/3rd width)
```html
<|sidebar|>
# 🏭 ShopQuote

<|in-quote-number|input|value={quote_number}|label=Quote #|>

<|{selected_database}|selector|lov={database_options}|on_change=on_database_change|label=Select Database|>

## Session Settings
<|Load Session|button|on_action=on_load_session|>Load Session</button>
<|Save Session|button|on_action=on_save_session|>Save Session</button>
<|Reset Session|button|on_action=on_reset_session|class_name=warning|>Reset Session</button>

## Go to…
<|btn-new-quote|button|on_action=on_new_quote|>🆕 New Quote</button>
<|btn-part-ops|button|on_action=on_back_to_part_ops|>↩️ Part & Ops</button>
<|btn-quote-breakdown|button|on_action=on_back_to_breakdown|>↩️ Quote Breakdown</button>
<|btn-summary|button|on_action=on_back_to_summary|>↩️ Summary</button>
|sidebar|>
```

#### Main Content (2/3rd width)
```html
<|main|>
# ⚙️ Settings

<|container|
## 📊 Database Management

### {selected_database} Data ({table_row_count} rows)
<|{current_table}|table|show_all=True|width=100%|height=400px|>

<|Add Row|button|on_action=on_add_row|>
<|Edit Row|button|on_action=on_edit_row|>
<|Delete Row|button|on_action=on_delete_row|class_name=danger|>
<|Refresh|button|on_action=on_refresh_table|>
|>

<|container|
## 🔧 Rate Configuration

<|{rates_setup_per_min}|number|label=Setup Rate ($/min)|min=0.0|step=1.0|>
<|{rates_labor_per_min}|number|label=Labor Rate ($/min)|min=0.0|step=0.1|>
<|{rates_machine_per_min}|number|label=Machine Rate ($/min)|min=0.0|step=0.1|>
<|{pricing_markup_percent}|number|label=Markup Percent (%)|min=0|max=100|step=1|>

<|Save Rates|button|on_action=on_save_rates|class_name=success|>
|>

### Session Status
{session_status}
|main|>
|layout|>
```

## Formatting Rules
- Sidebar order must remain deterministic per page.
- All IDs must remain fixed as listed.
- A Quote # is **mandatory** in all modes before navigation beyond the Welcome or Part Summary pages.
- Warning message must appear if user attempts to continue without entering a Quote #.
- Transitions between pages must update the main window content seamlessly.
- Settings modal does not affect main window layout.

## CSS Styling Specifications

### Global Styles
```css
body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    margin: 0;
    padding: 20px;
    background-color: #f5f5f5;
}

.app-header {
    background: linear-gradient(to right, #ffffff 0%, #000000 100%);
    color: #000000;
    padding: 20px;
    width: 100vw;
    position: fixed;
    top: 0;
    left: 0;
    z-index: 1000;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    display: flex;
    align-items: center;
    gap: 20px;
    box-sizing: border-box;
}

.taipy-layout {
    min-height: 100vh;
    margin-top: 80px; /* Account for fixed header */
}

.taipy-sidebar {
    border-right: 1px solid #e0e0e0;
    padding: 20px; /* Equal spacing on all sides */
    background-color: #f8f9fa;
    width: 33.33%;
    position: fixed;
    height: calc(100vh - 80px);
    overflow-y: auto;
}

.taipy-main {
    padding: 20px;
    margin-left: 33.33%;
    width: 66.67%;
}
```

### Component-Specific Styles
```css
/* Sidebar Brand */
.sidebar-brand {
    text-align: center;
    margin-bottom: 20px;
    padding: 15px;
    background: linear-gradient(to right, #ffffff 0%, #000000 100%);
    border-radius: 6px;
}

/* Settings Modal */
.settings-modal {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.5);
    z-index: 2000;
    display: flex;
    align-items: center;
    justify-content: center;
}

.settings-content {
    background: white;
    border-radius: 8px;
    padding: 20px;
    max-width: 600px;
    width: 90%;
    max-height: 80vh;
    overflow-y: auto;
}

/* Buttons */
.button, .taipy-button, .nav-button {
    background-color: #007bff;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 12px 16px; /* Equal padding on all sides */
    cursor: pointer;
    margin: 5px;
    display: block;
    width: 100%;
    text-align: center; /* Centered text inside buttons */
    box-sizing: border-box;
}

.button:hover, .taipy-button:hover, .nav-button:hover {
    background-color: #0056b3;
}

.button.active, .nav-button.active {
    background-color: #0056b3;
    font-weight: bold;
}

/* Form Fields */
.form-field {
    margin: 10px 0;
}

.form-field label {
    display: block;
    margin-bottom: 5px;
    font-weight: 500;
}

.form-field input, .form-field select {
    width: 100%;
    padding: 8px 12px;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 14px;
}
```

## Button Styling Rules

### Sidebar Button Specifications
- **Text Alignment**: All sidebar buttons must have `text-align: center`
- **Padding**: Equal padding on all sides (`padding: 12px 16px`)
- **Width**: Full width (`width: 100%`)
- **Centering**: Buttons are centered from right to left with equal padding
- **Emoji Prohibition**: Use of emojis in button text is prohibited unless otherwise instructed

### Sidebar Layout Rules
- **Padding**: Equal spacing on all sides (`padding: 20px`)
- **Button Consistency**: All navigation buttons follow the same styling rules
- **Visual Hierarchy**: Consistent button sizing and spacing throughout

## Responsive Design

### Breakpoints
- **Desktop (>1200px)**: 1:3 sidebar ratio maintained
- **Tablet (768px-1200px)**: Sidebar becomes top navigation
- **Mobile (<768px)**: Stacked layout, single column

### Mobile Optimizations
- Touch-friendly button sizes (minimum 44px)
- Simplified navigation
- Collapsible sections for space efficiency
- Horizontal scrolling for tables

## Integration with ShopQuote App

### File Structure
```
shopquote/
├── welcome.html              # Welcome/Landing page
├── part-summary.html         # Part information display
├── operations.html           # Operations management
├── quote-breakdown.html      # Cost analysis and markup
├── quote-summary.html        # Final professional quote
├── settings.html             # Application configuration
├── main_taipy.py             # Taipy application (legacy)
├── ui/
│   ├── integrated_parsers.py # File processing logic
│   ├── ocr_processor.py      # OCR processing
│   └── microservices/        # Individual service modules
├── requirements.txt
├── render.yaml
├── master_ui_format.md       # This file (source of truth)
└── README.md
```

### Running the Application
```bash
# Install dependencies (for Taipy version)
cd /Users/computer/Documents/shopQuote
python3 -m pip install -r requirements.txt

# Run Taipy application
python3 main_taipy.py

# Or run HTML demo (current implementation)
cd /Users/computer/Documents/shopQuote
python3 -m http.server 8000
# Then open welcome.html in browser for full application
```

### Implementation Notes
- **Quote # Validation**: Implement client-side validation before navigation
- **Settings Modal**: Use Taipy's modal components or custom overlay
- **Page Transitions**: Use Taipy's navigate function with state management
- **Responsive Design**: Implement CSS media queries for mobile/tablet breakpoints

## Version History

- **v1.0** - Initial master UI format specification
- **v1.1** - Added responsive design specifications
- **v1.2** - Updated layout proportions (1:3 sidebar ratio)
- **v1.3** - Added button trigger specifications
- **v1.4** - Integrated with existing ShopQuote app structure
- **v1.5** - Added comprehensive sidebar layouts per page
- **v1.6** - Added navigation rules and settings integration
- **v1.7** - Updated for HTML implementation with separate page files
- **v1.8** - Updated branding to green theme with gradient backgrounds
- **v1.9** - Added connected navigation system and professional styling

---

## ✅ **LOCKED-IN DESIGN RULES**

The following design rules have been established and locked in for the ShopQuote application:

### **🔒 Content Structure Rules (LOCKED)**
- **File Processing Status Card**: Permanently removed from Part Summary page
- **Reason**: Streamlines the interface and focuses on core part information
- **Alternative**: Processing status information moved to Operations page workflow
- **Implementation**: Removed from part-summary.html, documented in master format

- **Page Subtitle and Description**: Permanently removed from Part Summary page
- **Removed Content**: "Manufacturing Part Information" subtitle and explanatory paragraph
- **Reason**: Further streamlines interface, removes redundant explanatory text
- **Result**: Clean, direct presentation of part data without unnecessary descriptions
- **Implementation**: Removed from part-summary.html, documented in master format

- **Customer Information Card**: Permanently removed and consolidated into Part Information card
- **Change**: Customer field moved to top of Part Information section, above Part Number
- **Removed Content**: Entire "Customer Information" section (Contact, Quote Date fields)
- **Reason**: Streamlines to single data card, prioritizes customer visibility
- **Result**: Customer information prominently displayed at top of part details
- **Implementation**: Modified part-summary.html, documented in master format

- **Layout Positioning Fix**: Corrected CSS positioning conflicts in Part Summary page
- **Issues Fixed**: Removed conflicting fixed positioning, corrected width calculations
- **Changes**: Simplified .page-section to use normal flow instead of fixed positioning
- **Result**: Proper responsive layout following locked-in 33.33%/66.67% ratio
- **Implementation**: Updated CSS in part-summary.html, documented in master format

- **Padding Alignment**: Matched Part Summary container top padding to sidebar top padding
- **Change**: .page-section top padding changed from 40px to 20px to match sidebar
- **Result**: Consistent vertical alignment between sidebar and main content
- **Implementation**: Updated CSS in part-summary.html, documented in master format

- **Header Alignment Fix**: Corrected layout positioning to account for header height
- **Issues Fixed**: Layout container margin and sidebar positioning misaligned with header
- **Changes**: Increased layout margin from 120px to 140px, added explicit sidebar top position
- **Result**: Perfect vertical alignment between header, sidebar, and main content
- **Implementation**: Updated CSS positioning in part-summary.html, documented in master format

- **Page Title Branding**: Updated Part Summary title to match brand styling
- **Change**: "Part Summary" → "partSummary" with "Summary" in brand green (#22c55e)
- **Reason**: Consistent branding with shopQuote header styling
- **Result**: Professional, branded page title following design system
- **Implementation**: Updated HTML in part-summary.html, documented in master format

- **Section Header Removal**: Permanently removed "Part Information" section header
- **Change**: Removed `<h3>Part Information</h3>` from data section
- **Reason**: Streamlines interface by removing redundant section labeling
- **Result**: Cleaner data presentation with direct field display
- **Implementation**: Updated HTML in part-summary.html, documented in master format

- **Navigation Button Rename**: Updated Back to Welcome button to Start New Quote
- **Change**: "Back to Welcome" → "Start New Quote" with updated function name
- **Reason**: Better reflects the action of starting a new quote workflow
- **Result**: Clearer user intent and improved navigation labeling
- **Implementation**: Updated HTML and JavaScript in part-summary.html, documented in master format

- **Operations Button Simplify**: Simplified Next: Operations button to just Operations
- **Change**: "Next: Operations" → "Operations" with updated button ID
- **Reason**: Cleaner, more direct navigation labeling
- **Result**: Streamlined button text without redundant "Next:" prefix
- **Implementation**: Updated HTML in part-summary.html, documented in master format

- **Navigation Expansion**: Added Quote Breakdown and Quote Summary navigation buttons
- **New Buttons**: "Quote Breakdown" and "Quote Summary" added below Operations button
- **Reason**: Complete workflow navigation from Part Summary to final quote stages
- **Result**: Full quote creation workflow accessible from single navigation panel
- **Implementation**: Added HTML buttons and JavaScript functions in part-summary.html, documented in master format

- **Navigation Reordering**: Moved Start New Quote button to bottom of navigation
- **New Order**: Operations → Quote Breakdown → Quote Summary → Start New Quote
- **Reason**: Logical workflow progression with reset action at bottom
- **Result**: Better user experience with primary workflow actions first, reset last
- **Implementation**: Reordered HTML buttons in part-summary.html, documented in master format

- **Quote Number Editability**: Made Quote # field editable for user customization
- **Change**: Converted read-only div to editable input field with proper styling
- **Reason**: Allows users to customize quote numbers for their business needs
- **Result**: Flexible quote numbering system with consistent form styling
- **Implementation**: Updated HTML input field in part-summary.html, documented in master format

- **Element Width Adjustments**: Reduced button and input widths for better spacing
- **Changes**: Navigation buttons width: 100% → 75%, Quote # input width: 100% → 75%
- **Reason**: Improved visual balance and reduced horizontal scroll issues
- **Result**: Better proportioned elements with improved sidebar layout
- **Implementation**: Updated CSS and inline styles in part-summary.html, documented in master format

- **Sidebar Element Centering**: Standardized widths and centering for all sidebar elements
- **Changes**: All elements set to 85% width and centered, added green hover effects
- **Reason**: Consistent visual alignment and improved user interaction feedback
- **Result**: Professional, centered layout with enhanced hover states
- **Implementation**: Updated CSS for buttons, inputs, and branding box in part-summary.html, documented in master format

- **Horizontal Scroll Bar Fix**: Removed horizontal scroll bar from sidebar
- **Change**: Added overflow-x: hidden to sidebar CSS
- **Reason**: Prevented horizontal overflow caused by padding and fixed positioning
- **Result**: Clean sidebar layout without horizontal scroll bar
- **Implementation**: Updated sidebar CSS in part-summary.html, documented in master format

- **Label to Divider Conversion**: Replaced text labels with green divider lines
- **Changes**: Navigation and Settings labels replaced with 85% width green dividers
- **Reason**: Cleaner visual hierarchy using consistent divider styling
- **Result**: Streamlined sidebar with visual separation instead of text labels
- **Implementation**: Updated HTML structure in part-summary.html, documented in master format

- **Layout and Text Alignment Adjustments**: Modified sidebar width and input text alignment
- **Changes**: Sidebar width 33.33% → 30%, main content adjusted accordingly, Quote # text left-aligned
- **Reason**: Better proportioned layout and improved text readability in input fields
- **Result**: More balanced layout with left-aligned text in Quote # input
- **Implementation**: Updated CSS and inline styles in part-summary.html, documented in master format

- **Inline Editable Fields**: Converted part summary fields to editable inputs without visual change
- **Changes**: Customer, Part Number, Description, Bend Count as text inputs; Material & Thickness as dropdowns
- **Reason**: Enable user editing of parsed data while maintaining identical visual appearance
- **Result**: Seamless inline editing with auto-population, hover effects, and auto-save functionality
- **Implementation**: Replaced spans with styled inputs/selects, added CSS and JavaScript in part-summary.html, documented in master format

- **Field Enhancement Updates**: Made Flat Size editable, right-aligned text, removed number spinners
- **Changes**: Flat Size converted to editable input, all fields right-aligned, Bend Count spinner arrows removed
- **Reason**: Complete field editability, consistent text alignment, cleaner number input appearance
- **Result**: All part fields now editable with uniform right alignment and professional styling
- **Implementation**: Updated HTML inputs, enhanced CSS styling in part-summary.html, documented in master format

- **Full-Width Input Extension**: Extended input boxes to use maximum available width with 10px gap
- **Changes**: Changed layout from space-between to flex-start, labels fixed width with 10px margin, inputs take remaining space
- **Reason**: Maximize input field size while maintaining right alignment and proper spacing
- **Result**: Wide, professional input fields spanning almost full width with consistent 10px label gap
- **Implementation**: Updated CSS flexbox layout in part-summary.html, documented in master format

- **Edit Mode Toggle**: Added controlled editing mode for part information fields with dual action buttons
- **Changes**: Fields readonly by default, toggle button repositioned outside part info panel (inside part summary container, right-aligned), visual state indicators, removed divider lines and emojis, mirrored sidebar button styling, fixed 150px width for all buttons, green hover color, enhanced sidebar dividers (above operations, below settings), optimized spacing, edit mode field styling matches hover colors (green border, light green background), black text color, enhanced focus state, reverted readonly padding to zero for minimal layout changes, preserved black text color for auto-populated fields, removed all animations/transitions for instant state changes, updated button colors (black default/green hover), added Cancel and Save Changes buttons in edit mode with consistent 150px width and sidebar button height, implemented responsive gap system to prevent sidebar/main content collision
- **Reason**: Prevent accidental changes while providing full editing capability with better visual hierarchy, consistent design, optimal button sizing matching sidebar buttons, improved layout organization, instant state transitions, clear action options, responsive design to prevent overlap, and visual feedback for edit states with unified color scheme
- **Result**: Professional edit/view mode toggle with refined positioning outside part info panel, clean design, consistent button styling matching sidebar dimensions, enhanced sidebar organization, optimal user experience, unified color scheme between edit and hover states, instant layout transitions, consistent text colors, clear action buttons (Cancel/Save) with uniform dimensions, responsive gap system preventing collision, and visual distinction between edit and view modes
- **Implementation**: Added CSS readonly styles with zero padding, repositioned toggle button outside data-section with right alignment and reduced margin, removed divider lines and emojis, updated button styling to match sidebar with green hover, set fixed 150px width for all buttons with consistent line-height, added comprehensive sidebar dividers, optimized spacing, implemented edit mode field styling matching hover colors, changed text color to black and preserved it for auto-populated fields, enhanced focus state with thicker outline and darker colors, removed all CSS transitions for instant changes, updated button to black default with green hover, added dual action buttons (Cancel/Save Changes) for edit mode with matching dimensions, implemented responsive gap system (60px large, 35px medium, stacked small screens), and JavaScript state management in part-summary.html, documented in master format

- **Operations Page Layout**: Mirrored part summary sidebar structure and implemented business rules compliance with fully editable operations table
- **Changes**: Updated layout gap from 20px to 40px, adjusted sidebar width from 33.33% to 30%, updated main content margin from 33.33% to 30%, corrected header margin from 120px to 140px, added responsive gap system (60px large, 35px medium, stacked small screens), implemented operations table format per [OPR001.A] with exact columns (Seq, Operation, Setup, Setup Cost, # Ops, RUNTIME, $/Part), added mandatory operations (Plan, Final Insp., Package), included edit mode prompt per [OPR001.B] with Type 1 to Edit Operations / Press [enter] to Generate Quote, mirrored exact part summary sidebar button layout with dividers (Quote # field, Navigation section with HR dividers, Settings section, Save/Start New Quote section), added flatExtract manual calculator feature with unique gradient button styling (black to white gradient, 'flat' white text, 'Extract' red text), positioned as collapsed card above operations table for manual fail-safe calculations, optimized table cell padding to 5px for more compact display, enhanced table visual design with light grey header background (#f8f9fa), dark grey bottom border (2px solid #666666), light grey table borders (1px solid #e0e0e0), black $/part column text color (#000000), improved typography with system font stack matching sidebar buttons (-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif), added subtle shadows for depth, implemented fully editable operations table with sequence reordering arrows (^v), operation dropdown tied to operations list, editable input fields for setup time, number of operations, and runtime, read-only fields for setup cost and cost per part (auto-calculated), special input handling for Install operations (hardware selection) and Outside Process operations (process specification)
- **Reason**: Ensure operations page mirrors part summary layout structure, implements business rules compliance for operations UI, provides consistent user experience across pages, prevents sidebar/main content collision with responsive design, follows established design patterns with exact sidebar button layout mirroring, and adds manual flat calculation capability as fail-safe for parsing failures, optimize space usage with compact table padding, enhance visual appeal with modern styling while maintaining professional appearance, ensure consistent typography across all UI elements, improve data readability with appropriate color contrast and subtle borders, provide full operational flexibility with editable table, sequence reordering, and special operation handling per business rules
- **Result**: Operations page now matches part summary layout with consistent sidebar structure, proper responsive gap system preventing collision, business rules compliant operations table format with compact 5px padding and enhanced visual design, mandatory operations included, edit mode prompt properly positioned, unified design language across pages, exact sidebar button layout with dividers matching part summary, flatExtract manual calculator with distinctive gradient button (black→white, split text colors: 'flat' white, 'Extract' red) positioned above operations table as manual fail-safe for bend calculations, visually enhanced table with light grey header background, dark grey bottom border, light grey table borders for subtle definition, black $/part column text for better readability, system font stack for consistency, subtle shadows for professional depth, fully editable operations table with sequence reordering (^v arrows), operation dropdown selection, editable setup time, number of operations, and runtime fields, read-only auto-calculated setup cost and cost per part fields, special handling for Install operations (hardware prompts) and Outside Process operations (process specification prompts)
- **Implementation**: Updated layout-container gap to 40px, adjusted sidebar to 30% width with proper positioning, implemented responsive breakpoints (60px large, 35px medium, stacked small screens), formatted operations table per [OPR001.A] with exact column structure and 5px cell padding, included mandatory operations (Plan, Final Insp., Package), added edit mode prompt per [OPR001.B], mirrored exact part summary sidebar structure with 85% width buttons, centered margins, green HR dividers, Quote # editable field, Navigation section (Part Summary, Quote Breakdown, Quote Summary), Settings section, and Save/Start New Quote section, implemented flatExtract calculator with gradient button styling (linear-gradient black to white, split text colors), positioned as collapsible card above operations table, added real-time calculation for area/perimeter/weight, Apply to Quote and Reset functionality, enhanced table visual design with #f8f9fa light grey header background, 2px solid #666666 dark grey bottom border, 1px solid #e0e0e0 light grey table borders, #000000 black $/part column text color, system font stack (-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif) for both header and body cells, improved typography with font-weight variations (600 for headers, 600 for sequence numbers, 500 for data cells), added subtle box-shadow for depth, implemented dynamic JavaScript operations table with sequence reordering arrows (^v), operation dropdown from predefined list, editable input fields for setup, numOps, runtime, read-only display for setupCost, costPerPart with auto-recalculation, special operation handling for Install (hardware selection dialog) and Outside Process (process specification dialog), maintained consistent styling and spacing, documented in master format

- **Actions Section Refinement**: Removed Actions label, matched divider thickness, repositioned buttons
- **Changes**: Removed "Actions" label, divider thickness matches sidebar border (1px), moved Start New Quote below Save Quote
- **Reason**: Cleaner visual hierarchy with consistent border thickness and logical button grouping
- **Result**: Streamlined sidebar with primary actions (Save Quote) and secondary actions (Start New Quote) clearly separated
- **Implementation**: Updated HTML structure in part-summary.html, documented in master format

- **Global Rates Expanding Container**: Added expandable rates configuration directly in sidebar with clean arrow indicators and centered text
- **Changes**: Added "Global Rates" button above Settings button with expanding container containing Setup Rate, Labor Rate, Machine Rate inputs and Apply Rates button, smooth CSS animations with line down arrow (↓) when closed and line up arrow (↑) when expanded, localStorage persistence, backend integration, adjusted sidebar height to accommodate expanded content without vertical scroll bar, centered "Global Rates" text using flexbox justify-content: center
- **Reason**: Quick access to rate configuration without opening Settings modal, improved workflow efficiency, cleaner visual design with proper arrow indicators and centered text alignment
- **Result**: Professional expanding container with same dimensions as sidebar buttons when collapsed, 3 vertically stacked input fields when expanded, right-aligned Apply Rates button, clean line arrow indicators (↓/↑), dynamic sidebar height adjustment, no vertical scroll bar, centered text alignment, consistent styling with existing sidebar elements
- **Implementation**: Added HTML structure with span-based arrow, CSS animations with transform rotate and flexbox centering, JavaScript functionality, backend function in operations.html and src/app.py, sidebar height adjustment using CSS :has() selector, documented in master format

- **Sidebar Button Borders**: Added consistent green borders to all sidebar buttons and Global Rates container with black hover borders
- **Changes**: Applied 1px solid green border (#22c55e) to all .nav-button elements and .global-rates-container, added 1px solid black border on hover for all elements, maintained existing hover effects and styling
- **Reason**: Consistent visual design across all sidebar interactive elements, enhanced visual hierarchy and user experience
- **Result**: All sidebar buttons and Global Rates container now have green borders by default, black borders on hover, maintaining existing color transitions and animations
- **Implementation**: Updated .nav-button CSS with border: 1px solid #22c55e and border-color: #000000 on hover, added border: 1px solid #22c55e to .global-rates-container with border-color: #000000 on hover, documented in master format

- **Edit Mode Prompt Removal**: Removed the edit mode prompt panel from operations page
- **Changes**: Completely removed the div containing "→ Type 1 to Edit ⚙️ Operations" and "→ Press [enter] to Generate 📊 Quote" text and its containing panel
- **Reason**: Streamlined operations page interface by removing outdated keyboard shortcut prompts that are no longer relevant to the current workflow
- **Result**: Cleaner operations page layout without the instructional prompt panel, maintaining focus on the main operations table and flatExtract calculator
- **Implementation**: Removed the entire div block with class styling for the edit mode prompt, documented in master format

- **Enhanced Operations Editor Implementation**: Successfully ported exact Streamlit operations editor logic to JavaScript/HTML with sophisticated conditional logic
- **Changes**: Implemented panel-based operations editor with exact Streamlit logic port, sophisticated conditional dropdown system for hardware/outside process operations, smart detail preservation when switching operation types, deterministic key naming for stable UI updates (op-${i}-select pattern), real-time buffer updates following Streamlit pattern, professional panel styling with hover effects and responsive design, working buffer system isolating edits from canonical data, save/cancel workflow with proper state management, preloaded dropdown options from business-approved lists, row management actions (move up/down, insert above/below, delete), validation and error display per row, enhanced user experience with web-native interactions
- **Reason**: Provide exact Streamlit behavior fidelity while maintaining web-native performance and user experience, implement sophisticated conditional logic for special operation types, ensure data integrity with working buffer system, provide professional editing interface matching modern web applications
- **Result**: Production-ready operations editor with exact Streamlit logic port, sophisticated conditional dropdowns (hardware for Install operations, outside process for Outside Process operations), smart detail preservation, real-time updates, professional panel-based UI, working buffer system with save/cancel workflow, row management actions, validation system, web-native interactions with smooth animations and hover effects, responsive design, deterministic key naming for stable updates, preloaded business-approved dropdown options
- **Implementation**: Added exact Streamlit logic port to JavaScript with conditional dropdown system, panel-based HTML structure, sophisticated state management, real-time buffer updates, professional CSS styling with animations, web-native interactions, responsive design, deterministic key naming, preloaded dropdown options, documented in master format

### **🔒 Button Styling Rules (LOCKED)**
- **Text Alignment**: All sidebar buttons MUST have `text-align: center`
- **Padding**: All sidebar buttons MUST have equal padding (`padding: 12px 16px`)
- **Centering**: All buttons MUST be centered from right to left with equal padding
- **Box Sizing**: All buttons MUST include `box-sizing: border-box`
- **Width**: All buttons MUST be full width (`width: 100%`)
- **Text Decoration**: All buttons MUST have `text-decoration: none`

### **🔒 Sidebar Layout Rules (LOCKED)**
- **Padding**: Sidebar MUST have equal spacing on all sides (`padding: 20px`)
- **Button Consistency**: All navigation buttons MUST follow the same styling rules
- **Visual Hierarchy**: Consistent button sizing and spacing throughout

### **🔒 Emoji Prohibition (LOCKED)**
- **Prohibition**: Use of emojis in button text is prohibited unless otherwise instructed
- **Scope**: Applies to all user-facing text in the application
- **Exception**: Only when explicitly instructed in future requirements

### **🔒 Layout Proportions (LOCKED)**
- **Sidebar**: 33.33% of viewport width
- **Main Content**: 66.67% of viewport width
- **Fixed Positioning**: Sidebar uses `position: fixed` with proper height calculation

### **🔒 Implementation Status**
- **✅ Master Format Updated**: All rules documented in master_ui_format.md
- **✅ HTML Files Updated**: All 6 HTML pages updated to comply
- **✅ CSS Rules Applied**: Button styling rules implemented across all pages
- **✅ Testing Verified**: Layout proportions and button centering confirmed

---

**This document serves as the authoritative source for all UI layout decisions. The current implementation uses separate HTML files with consistent styling and navigation. Any changes to the UI must be reflected here first and approved before implementation.**

**🔒 LOCKED RULES: The button styling, sidebar layout, and emoji prohibition rules are now locked in and must be followed for all future development.**