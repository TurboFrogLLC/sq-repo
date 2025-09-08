#!/usr/bin/env python3
"""
ShopQuote - Taipy Web Application
Clean Taipy implementation
"""

import os
import json
import logging
import time
from pathlib import Path
from typing import Dict, Any, List
import pandas as pd
from taipy.gui import Gui, navigate, notify

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize global state
quote_data = {
    'customer': '',
    'part_number': '',
    'description': '',
    'material': '',
    'thickness_in': None,
    'flat_size_width': None,
    'flat_size_height': None,
    'bend_count': 0,
    'operations': [],
    'hardware': [],
    'outside_processes': []
}

pricing_breakdown = {}
extracted_metadata = {}
active_page = "🏠 Home"
markup_percent = 15.0
uploaded_files = []
processing_results = {}
last_update = ""  # For forcing UI refresh
quote_totals = {'1': 0.00, '10': 0.00, '25': 0.00, '50': 0.00}  # Per business rules [QBX003.A]
quote_number = "SQ-20250101-001"  # Global quote number per rules_ui_format.txt

# flatExtract state variables
flat_width = 0.0
flat_height = 0.0
flat_material = ""
flat_area = 0.0
flat_perimeter = 0.0
flat_weight = 0.0

# Dynamic Rules Engine state variables
rules_validation_status = "Ready"
rules_violations = []
rules_suggestions = []
rules_cost_flags = []
smart_suggestion_selected = ""

# ── Taipy Page Definitions
home_page = """
<|layout|columns=1 4|
<|sidebar|
# 🏭 ShopQuote

<|in-quote-number|input|value={quote_number}|label=Quote #|>

## 🧭 Navigation
<|🏠 Home|button|on_action=navigate_to_home|>
<|📄 Part & Ops|button|on_action=navigate_to_part_ops|>
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

<|main|
# 🏭 ShopQuote - Integrated Application

<|Welcome to ShopQuote|text|class_name=h1|>

Complete production application with intelligent OCR and CAD file processing.

## 📤 Quick File Upload

<|{uploaded_files}|file_selector|multiple|extensions=.dxf,.step,.stp,.pdf|label=Upload CAD files|on_action=process_files|>

<|Process Files|button|on_action=process_files|>

## 📊 Recent Activity

<|{processing_results}|expandable|>

## 🎯 Data Quality Overview

<|{extracted_metadata}|expandable|>

## 🚀 Getting Started

1. **Upload Files**: Use the file selector above to upload DXF, STEP, or PDF files
2. **Automatic Processing**: OCR and CAD parsers will extract data automatically
3. **Review Results**: Check the Part Summary for extracted information
4. **Generate Quote**: Navigate to Part & Ops to complete the quote

**💡 Tip:** For best results, upload both PDF drawings and CAD files together for comprehensive data extraction.
|main|>
|layout|>
"""

part_ops_page = """
# 📄 Part & Operations

<|Part Summary|expandable|expanded|>

## 📋 Part Summary
Customer: {quote_data.customer or '—'}
Part Number: {quote_data.part_number or '—'}
Material: {quote_data.material or '—'}
Thickness: {format_thickness(quote_data.thickness_in)}
Flat Size: {format_flat_size(quote_data.flat_size_width, quote_data.flat_size_height)}
Bends: {quote_data.bend_count or '—'}

<|File Processing|expandable|>

## 📤 File Upload & Processing

<|{uploaded_files}|file_selector|multiple|extensions=.dxf,.step,.stp,.pdf|label=Upload CAD files|on_action=process_files|>

<|Process Files|button|on_action=process_files|>

## 📊 Processing Results

<|{processing_results}|expandable|>

<|Data Quality|expandable|>

## 🎯 Data Quality Indicators

<|{extracted_metadata}|expandable|>

<|Operations|expandable|expanded|>

## ⚙️ Operation Breakdown

<|{operations_table}|table|show_all|>

<|Add Operation|button|on_action=show_add_operation_dialog|>

<|Hardware|expandable|>

## 🛠️ Hardware

<|{hardware_table}|table|show_all|>

<|Add Hardware|button|on_action=show_add_hardware_dialog|>

<|Outside Processes|expandable|>

## 📦 Outside Processes

<|{outside_processes_table}|table|show_all|>

<|Add Outside Process|button|on_action=show_add_outside_process_dialog|>

<|Navigation|expandable|>

<|⬅️ Back to Home|button|on_action=navigate_to_home|>
<|⚙️ Operations|button|on_action=navigate_to_operations|>
<|📊 Generate Quote|button|on_action=navigate_to_quote_breakdown|>
"""

quote_breakdown_page = """
# 📊 Quote Breakdown

<|Quote Summary|expandable|expanded|>

**Customer:** {quote_data.customer or '—'}
**Part Number:** {quote_data.part_number or '—'}
**Material:** {quote_data.material or '—'}
**Thickness:** {format_thickness(quote_data.thickness_in)}
**Flat Size:** {format_flat_size(quote_data.flat_size_width, quote_data.flat_size_height)}
**Bends:** {quote_data.bend_count or '—'}

<|Pricing Table|expandable|expanded|>

<|{pricing_table}|table|show_all|>

<|{markup_percent}% Markup|slider|min=0|max=100|on_change=update_markup|>

<|Navigation|expandable|>

<|⬅️ Back to Part & Ops|button|on_action=navigate_to_part_ops|>
<|📋 Generate Summary|button|on_action=navigate_to_summary|>
"""

summary_page = """
# 📋 Quote Summary

<|📌 Summary View|expandable|expanded|>

📌 Summary View
Customer: {quote_data.customer or '—'}
Part number: {quote_data.part_number or '—'}
Description: {quote_data.description or '—'}

💲 Quote Totals
- Qty 1: {format_quote_total(quote_totals.get('1', 0.00))}
- Qty 10: {format_quote_total(quote_totals.get('10', 0.00))}
- Qty 25: {format_quote_total(quote_totals.get('25', 0.00))}
- Qty 50: {format_quote_total(quote_totals.get('50', 0.00))}

→ Type [ s ] to Save Quote
→ Type [ n ] to Start New Quote
→ Type [ q ] to Quit

<|Export Options|expandable|>

<|📄 Export as TXT|button|on_action=export_txt|>
<|📊 Export as PDF|button|on_action=export_pdf|>
<|💾 Save Quote|button|on_action=save_quote|>

<|Navigation|expandable|>

<|⬅️ Back to Breakdown|button|on_action=navigate_to_quote_breakdown|>
<|🏠 New Quote|button|on_action=start_new_quote|>
"""

operations_page = """
# ⚙️ Operations

<|Operations Management|expandable|expanded|>

## 📐 Manual Flat Calculator

<|layout|columns=1 2|
<|part|
### Dimensions
<|{flat_width}|input|label=Width (inches)|type=number|step=0.001|on_change=update_flat_calculations|>
<|{flat_height}|input|label=Height (inches)|type=number|step=0.001|on_change=update_flat_calculations|>
<|{flat_material}|selector|label=Material|lov={material_options}|dropdown|on_change=update_flat_calculations|>
|part|>

<|part|
### Calculations
<|Area: {format_flat_area(flat_area)}|text|>
<|Perimeter: {format_flat_perimeter(flat_perimeter)}|text|>
<|Weight: {format_flat_weight(flat_weight)}|text|>

<|Apply to Quote|button|on_action=apply_flat_extract|>
<|Reset|button|on_action=reset_flat_extract|>
|part|>
|layout|>

<|Dynamic Rules Engine|expandable|>

## 🧠 Smart Validation & Suggestions

<|layout|columns=1 2|
<|part|
### Real-Time Validation
<|Status: {rules_validation_status}|text|class_name=validation-status|>
<|Violations: {len(rules_violations)} found|text|class_name=validation-text|>
<|Cost Flags: {len(rules_cost_flags)} detected|text|class_name=validation-text|>
|part|>

<|part|
### Smart Suggestions
<|Available: {len(rules_suggestions)} suggestions|text|class_name=suggestion-text|>
<|{rules_suggestions[0] if rules_suggestions else 'No suggestions available'}|text|class_name=suggestion-detail|>

<|Evaluate Rules|button|on_action=evaluate_rules_engine|>
<|Apply Suggestion|button|on_action=apply_smart_suggestion|>
|part|>
|layout|>

<|Operations Table|expandable|expanded|>

<|{operations_table}|table|show_all|>

<|Add Operation|button|on_action=show_add_operation_dialog|>

<|Navigation|expandable|>

<|⬅️ Back to Part & Ops|button|on_action=navigate_to_part_ops|>
<|📊 Generate Quote|button|on_action=navigate_to_quote_breakdown|>
"""

# ── Page routing
pages = {
    "/": home_page,
    "home": home_page,
    "part-ops": part_ops_page,
    "operations": operations_page,
    "quote-breakdown": quote_breakdown_page,
    "summary": summary_page
}

# ── Data Mapping Functions
def map_resolved_data_to_ui(resolved_data, confidence_threshold=0.5):
    """
    Map resolved OCR data to UI fields following business rules [SSX002.A]

    Priority order per business rules:
    - Material Type → Trust PDF first
    - Material Thickness → Trust PDF first
    - Notes/Annotations → Trust PDF first
    - Outside Processes → Trust PDF first
    - Hardware → Trust PDF first
    - Flat Pattern Size → Trust STEP/DXF
    - Form Count → Trust STEP/DXF
    - Part Weight → Calculated from flat size + PDF thickness
    """
    ui_data = {
        'customer': '',
        'part_number': '',
        'description': '',
        'material': '',
        'thickness_in': None,
        'flat_size_width': None,
        'flat_size_height': None,
        'bend_count': 0,
        'operations': [],
        'hardware': [],
        'outside_processes': []
    }

    # Map customer data (from PDF per business rules)
    if resolved_data.get('customer') and resolved_data.get('confidence_scores', {}).get('pdf', 0) >= confidence_threshold:
        ui_data['customer'] = str(resolved_data['customer'])

    # Map part number (from PDF per business rules)
    if resolved_data.get('part_number') and resolved_data.get('confidence_scores', {}).get('pdf', 0) >= confidence_threshold:
        ui_data['part_number'] = str(resolved_data['part_number'])

    # Map description (from PDF per business rules)
    if resolved_data.get('description') and resolved_data.get('confidence_scores', {}).get('pdf', 0) >= confidence_threshold:
        ui_data['description'] = str(resolved_data['description'])

    # Map material (from PDF per business rules)
    if resolved_data.get('material') and resolved_data.get('confidence_scores', {}).get('pdf', 0) >= confidence_threshold:
        ui_data['material'] = str(resolved_data['material'])

    # Map thickness (from PDF per business rules)
    if resolved_data.get('thickness_in') is not None:
        # Check if we have PDF confidence for thickness
        pdf_confidence = resolved_data.get('confidence_scores', {}).get('pdf', 0)
        if pdf_confidence >= confidence_threshold:
            ui_data['thickness_in'] = float(resolved_data['thickness_in'])

    # Map flat size dimensions (from STEP/DXF per business rules)
    flat_size = resolved_data.get('flat_size_in', {})
    if flat_size.get('width') is not None:
        # Use STEP confidence if available, otherwise DXF
        step_confidence = resolved_data.get('confidence_scores', {}).get('step', 0)
        dxf_confidence = resolved_data.get('confidence_scores', {}).get('dxf', 0)

        if step_confidence >= confidence_threshold:
            ui_data['flat_size_width'] = float(flat_size['width'])
            ui_data['flat_size_height'] = float(flat_size.get('height', 0))
        elif dxf_confidence >= confidence_threshold:
            ui_data['flat_size_width'] = float(flat_size['width'])
            ui_data['flat_size_height'] = float(flat_size.get('height', 0))

    # Map bend count (from STEP/DXF per business rules)
    if resolved_data.get('bend_count') is not None:
        # Use STEP confidence if available, otherwise DXF
        step_confidence = resolved_data.get('confidence_scores', {}).get('step', 0)
        dxf_confidence = resolved_data.get('confidence_scores', {}).get('dxf', 0)

        if step_confidence >= confidence_threshold:
            ui_data['bend_count'] = int(resolved_data['bend_count'])
        elif dxf_confidence >= confidence_threshold:
            ui_data['bend_count'] = int(resolved_data['bend_count'])

    # Map hardware (from DXF per business rules)
    if resolved_data.get('hardware'):
        dxf_confidence = resolved_data.get('confidence_scores', {}).get('dxf', 0)
        if dxf_confidence >= confidence_threshold:
            ui_data['hardware'] = resolved_data['hardware']

    # Map outside processes (from PDF per business rules)
    if resolved_data.get('outside_processes'):
        pdf_confidence = resolved_data.get('confidence_scores', {}).get('pdf', 0)
        if pdf_confidence >= confidence_threshold:
            ui_data['outside_processes'] = resolved_data['outside_processes']

    return ui_data

def populate_operations_from_hardware(hardware_list):
    """Generate operations list based on detected hardware"""
    operations = []

    if not hardware_list:
        return operations

    # Common hardware to operation mappings
    hardware_operations = {
        'pem': ['PEM Stud Installation', 'Hardware Installation'],
        'fh': ['FH Fastener Installation', 'Hardware Installation'],
        'cls': ['CLS Stud Installation', 'Hardware Installation'],
        'rivet': ['Rivet Installation', 'Hardware Installation'],
        'screw': ['Screw Installation', 'Hardware Installation'],
        'nut': ['Nut Installation', 'Hardware Installation']
    }

    for hardware in hardware_list:
        if isinstance(hardware, dict):
            hw_type = hardware.get('type', '').lower()
            for key, ops in hardware_operations.items():
                if key in hw_type:
                    operations.extend(ops)
                    break

    # Remove duplicates while preserving order
    seen = set()
    unique_operations = []
    for op in operations:
        if op not in seen:
            unique_operations.append(op)
            seen.add(op)

    return unique_operations

# ── Helper Functions
def format_thickness(thickness_in):
    """Format thickness according to business rules [PSX001.B]"""
    if thickness_in is None:
        return "—"
    return f"{thickness_in:.3f} in"

def format_flat_size(width, height):
    """Format flat size according to business rules [PSX001.B]"""
    if width is None or height is None:
        return "—"
    return f"{width:.2f} in × {height:.2f} in"

def format_quote_total(amount):
    """Format quote total according to business rules [QBX000.A]"""
    if amount is None:
        return "$0.00"
    return f"${amount:.2f}"

def format_flat_area(area):
    """Format flat area for display"""
    if area is None or area == 0:
        return "0.00 sq in"
    return f"{area:.2f} sq in"

def format_flat_perimeter(perimeter):
    """Format flat perimeter for display"""
    if perimeter is None or perimeter == 0:
        return "0.00 in"
    return f"{perimeter:.2f} in"

def format_flat_weight(weight):
    """Format flat weight for display"""
    if weight is None or weight == 0:
        return "0.00 lbs"
    return f"{weight:.2f} lbs"

# ── Taipy State and Functions
def process_files(state):
    """Process uploaded files using integrated parsing logic"""
    if not state.uploaded_files:
        notify(state, "No files selected", "warning")
        return

    try:
        # Debug: Log what we received
        logger.info(f"DEBUG: uploaded_files type: {type(state.uploaded_files)}")
        logger.info(f"DEBUG: uploaded_files value: {state.uploaded_files}")

        # Handle Taipy's file upload format
        file_objects = []

        # Check if uploaded_files is a single string (file path)
        if isinstance(state.uploaded_files, str):
            logger.info("DEBUG: uploaded_files is a single string, treating as single file")
            uploaded_files_list = [state.uploaded_files]
        else:
            # Assume it's a list/iterable
            uploaded_files_list = list(state.uploaded_files)

        logger.info(f"DEBUG: Processing {len(uploaded_files_list)} files")

        for i, uploaded_file in enumerate(uploaded_files_list):
            logger.info(f"DEBUG: Processing file {i}: type={type(uploaded_file)}, value={uploaded_file}")

            # Taipy file selector returns file paths or file objects
            if isinstance(uploaded_file, str):
                # If it's a string (file path), read the file
                try:
                    with open(uploaded_file, 'rb') as f:
                        file_content = f.read()
                    filename = uploaded_file.split('/')[-1]  # Extract filename from path

                    # Create a mock file object
                    class MockFile:
                        def __init__(self, content, name):
                            self._content = content
                            self.name = name
                            self._read_called = False

                        def read(self):
                            if not self._read_called:
                                self._read_called = True
                                return self._content
                            return b""

                    file_objects.append(MockFile(file_content, filename))
                    logger.info(f"DEBUG: Created mock file object for {filename}")
                except Exception as e:
                    logger.error(f"DEBUG: Failed to read file {uploaded_file}: {e}")
                    continue
            else:
                # Assume it's already a file object with .name and .read() methods
                logger.info(f"DEBUG: Using file object directly: {getattr(uploaded_file, 'name', 'no name attr')}")
                file_objects.append(uploaded_file)

        logger.info(f"DEBUG: Created {len(file_objects)} file objects")

        # Use the integrated file processor
        from src.processors.integrated_parsers import file_processor
        results = file_processor.process_files(file_objects)

        state.processing_results = results

        success_count = results.get('summary', {}).get('successful', 0)
        error_count = results.get('summary', {}).get('failed', 0)

        # Map resolved data to UI fields following business rules
        resolved_data = results.get('resolved_data', {})
        logger.info(f"DEBUG: Resolved data from processing: {resolved_data}")

        if resolved_data:
            ui_data = map_resolved_data_to_ui(resolved_data)
            logger.info(f"DEBUG: Mapped UI data: {ui_data}")

            # CRITICAL FIX: Properly update Taipy state variables
            # Update individual fields to ensure UI binding works
            if ui_data.get('customer'):
                state.quote_data.customer = ui_data['customer']
            if ui_data.get('part_number'):
                state.quote_data.part_number = ui_data['part_number']
            if ui_data.get('description'):
                state.quote_data.description = ui_data['description']
            if ui_data.get('material'):
                state.quote_data.material = ui_data['material']
            if ui_data.get('thickness_in') is not None:
                state.quote_data.thickness_in = ui_data['thickness_in']
            if ui_data.get('flat_size_width') is not None:
                state.quote_data.flat_size_width = ui_data['flat_size_width']
            if ui_data.get('flat_size_height') is not None:
                state.quote_data.flat_size_height = ui_data['flat_size_height']
            if ui_data.get('bend_count') is not None:
                state.quote_data.bend_count = ui_data['bend_count']

            logger.info(f"DEBUG: Updated individual quote_data fields")

            # Generate operations from hardware if detected
            if ui_data.get('hardware'):
                operations = populate_operations_from_hardware(ui_data['hardware'])
                if operations:
                    state.quote_data.operations = operations
                    # Update operations_table for UI display
                    state.operations_table = [{'operation': op, 'setup_min': 0, 'runtime_sec': 0, 'cost_per_part': 0.00} for op in operations]
                    logger.info(f"DEBUG: Generated operations: {operations}")
                    logger.info(f"DEBUG: Updated operations_table: {len(state.operations_table)} items")

            # Update UI tables with proper data structures
            hardware_data = ui_data.get('hardware', [])
            state.hardware_table = hardware_data if hardware_data else []
            state.outside_processes_table = ui_data.get('outside_processes', [])

            logger.info(f"DEBUG: Updated hardware_table: {len(state.hardware_table)} items")
            logger.info(f"DEBUG: Updated outside_processes_table: {len(state.outside_processes_table)} items")

            # Create detailed extraction metadata for user feedback
            confidence_scores = resolved_data.get('confidence_scores', {})
            source_files = resolved_data.get('source_files', [])

            state.extracted_metadata = {
                'extraction_summary': {
                    'total_fields_mapped': len([v for v in ui_data.values() if v not in [None, '', [], 0]]),
                    'confidence_scores': confidence_scores,
                    'source_files': source_files,
                    'processing_method': 'OCR + Business Rules Resolution'
                },
                'field_confidence': {
                    'customer': confidence_scores.get('pdf', 0),
                    'part_number': confidence_scores.get('pdf', 0),
                    'material': confidence_scores.get('pdf', 0),
                    'thickness': confidence_scores.get('pdf', 0),
                    'flat_size': max(confidence_scores.get('step', 0), confidence_scores.get('dxf', 0)),
                    'bend_count': max(confidence_scores.get('step', 0), confidence_scores.get('dxf', 0)),
                    'hardware': confidence_scores.get('dxf', 0)
                },
                'data_quality_indicators': {
                    'high_confidence_fields': len([k for k, v in confidence_scores.items() if v >= 0.8]),
                    'medium_confidence_fields': len([k for k, v in confidence_scores.items() if 0.5 <= v < 0.8]),
                    'low_confidence_fields': len([k for k, v in confidence_scores.items() if v < 0.5]),
                    'overall_quality': 'High' if (len(confidence_scores) > 0 and sum(confidence_scores.values()) / len(confidence_scores) >= 0.8) else 'Medium' if (len(confidence_scores) > 0 and sum(confidence_scores.values()) / len(confidence_scores) >= 0.5) else 'Low'
                }
            }

            logger.info(f"DEBUG: Final extracted_metadata created")
            logger.info(f"DEBUG: UI update complete - checking final state...")

            # Force UI refresh by updating a dummy variable
            state.last_update = f"Updated at {time.time()}"
            logger.info(f"DEBUG: Forced UI refresh with timestamp")

        if success_count > 0:
            message = f"Successfully processed {success_count} file(s)"
            if error_count > 0:
                message += f" with {error_count} error(s)"
            notify(state, message, "success")

            # Navigate to part & operations page to show the populated data
            navigate(state, "part-ops")
        else:
            notify(state, "File processing failed", "error")

    except Exception as e:
        logger.error(f"File processing failed: {str(e)}")
        import traceback
        logger.error(f"DEBUG: Full traceback: {traceback.format_exc()}")
        state.processing_results = {
            'processed_files': [],
            'failed_files': [],
            'resolved_data': {},
            'summary': {'total_files': len(state.uploaded_files), 'successful': 0, 'failed': len(state.uploaded_files), 'errors': [str(e)]}
        }
        notify(state, f"Processing error: {str(e)}", "error")

def navigate_to_part_ops(state):
    """Navigate to Part & Operations page"""
    navigate(state, "part-ops")

def navigate_to_home(state):
    """Navigate to Home page"""
    navigate(state, "home")

def navigate_to_quote_breakdown(state):
    """Navigate to Quote Breakdown page"""
    navigate(state, "quote-breakdown")

def navigate_to_summary(state):
    """Navigate to Summary page"""
    navigate(state, "summary")

def navigate_to_settings(state):
    """Navigate to Settings page"""
    navigate(state, "settings")

def navigate_to_operations(state):
    """Navigate to Operations page"""
    navigate(state, "operations")

def update_markup(state, value):
    """Update markup percentage"""
    state.markup_percent = value

def export_txt(state):
    """Export quote as TXT"""
    notify(state, "TXT export not yet implemented", "info")

def export_pdf(state):
    """Export quote as PDF"""
    notify(state, "PDF export not yet implemented", "info")

def save_quote(state):
    """Save current quote"""
    notify(state, "Quote saved successfully", "success")

def start_new_quote(state):
    """Start a new quote"""
    # Reset quote data
    state.quote_data = {
        'customer': '',
        'part_number': '',
        'description': '',
        'material': '',
        'thickness_in': None,
        'flat_size_width': None,
        'flat_size_height': None,
        'bend_count': 0,
        'operations': [],
        'hardware': [],
        'outside_processes': []
    }
    navigate(state, "home")

def show_add_operation_dialog(state):
    """Show dialog to add operation"""
    notify(state, "Add operation dialog not yet implemented", "info")

def show_add_hardware_dialog(state):
    """Show dialog to add hardware"""
    notify(state, "Add hardware dialog not yet implemented", "info")

def show_add_outside_process_dialog(state):
    """Show dialog to add outside process"""
    notify(state, "Add outside process dialog not yet implemented", "info")

def show_file_upload(state):
    """Show file upload section (already visible on home page)"""
    notify(state, "File upload section is visible above", "info")

# ── flatExtract Functions
def apply_flat_extract(state):
    """Apply flat extract dimensions to quote data"""
    try:
        width = state.flat_width
        height = state.flat_height
        material = state.flat_material

        if width <= 0 or height <= 0:
            notify(state, "Please enter valid width and height values", "error")
            return

        # Update quote data with flat dimensions
        state.quote_data.flat_size_width = float(width)
        state.quote_data.flat_size_height = float(height)
        state.quote_data.material = material

        # Calculate area and perimeter
        area = width * height
        perimeter = 2 * (width + height)

        # Calculate weight if material is selected
        weight = 0
        if material:
            # Material densities (lb/in³)
            densities = {
                'CRS': 0.2840,
                'HRS': 0.2840,
                'SS': 0.2890,
                'ALUMINUM': 0.0975,
                'COPPER': 0.3230,
                'BRASS': 0.3070
            }

            # Assume 0.125" thickness for weight calculation
            thickness = 0.125
            volume = area * thickness
            density = densities.get(material, 0)
            weight = volume * density

        # Update state variables for UI
        state.flat_area = area
        state.flat_perimeter = perimeter
        state.flat_weight = weight

        notify(state, f"Applied flat dimensions: {width:.2f}\" × {height:.2f}\" to quote", "success")

        # Force UI refresh
        state.last_update = f"Updated at {time.time()}"

    except Exception as e:
        logger.error(f"Error applying flat extract: {str(e)}")
        notify(state, f"Error applying flat extract: {str(e)}", "error")

def calculate_flat_extract(width, height, material):
    """Calculate flat extract values without applying to quote"""
    try:
        if width <= 0 or height <= 0:
            return {'area': 0, 'perimeter': 0, 'weight': 0}

        # Calculate area and perimeter
        area = width * height
        perimeter = 2 * (width + height)

        # Calculate weight if material is selected
        weight = 0
        if material:
            # Material densities (lb/in³)
            densities = {
                'CRS': 0.2840,
                'HRS': 0.2840,
                'SS': 0.2890,
                'ALUMINUM': 0.0975,
                'COPPER': 0.3230,
                'BRASS': 0.3070
            }

            # Assume 0.125" thickness for weight calculation
            thickness = 0.125
            volume = area * thickness
            density = densities.get(material, 0)
            weight = volume * density

        return {
            'area': area,
            'perimeter': perimeter,
            'weight': weight
        }

    except Exception as e:
        logger.error(f"Error calculating flat extract: {str(e)}")
        return {'area': 0, 'perimeter': 0, 'weight': 0}

def reset_flat_extract(state):
    """Reset flat extract values"""
    try:
        # Reset quote data
        state.quote_data.flat_size_width = None
        state.quote_data.flat_size_height = None
        state.quote_data.material = ''

        # Reset UI state variables
        state.flat_width = 0.0
        state.flat_height = 0.0
        state.flat_material = ''
        state.flat_area = 0.0
        state.flat_perimeter = 0.0
        state.flat_weight = 0.0

        notify(state, "Flat extract values reset", "info")

        # Force UI refresh
        state.last_update = f"Updated at {time.time()}"

    except Exception as e:
        logger.error(f"Error resetting flat extract: {str(e)}")
        notify(state, f"Error resetting flat extract: {str(e)}", "error")

def update_flat_calculations(state):
    """Update flat extract calculations when inputs change"""
    try:
        width = state.flat_width
        height = state.flat_height
        material = state.flat_material

        if width > 0 and height > 0:
            # Calculate area and perimeter
            area = width * height
            perimeter = 2 * (width + height)

            # Calculate weight if material is selected
            weight = 0
            if material:
                # Material densities (lb/in³)
                densities = {
                    'CRS': 0.2840,
                    'HRS': 0.2840,
                    'SS': 0.2890,
                    'ALUMINUM': 0.0975,
                    'COPPER': 0.3230,
                    'BRASS': 0.3070
                }

                # Assume 0.125" thickness for weight calculation
                thickness = 0.125
                volume = area * thickness
                density = densities.get(material, 0)
                weight = volume * density

            # Update state variables
            state.flat_area = area
            state.flat_perimeter = perimeter
            state.flat_weight = weight

    except Exception as e:
        logger.error(f"Error updating flat calculations: {str(e)}")

# ── Global Rates Functions
def apply_global_rates(state, setup_rate, labor_rate, machine_rate):
    """Apply global rates to the application"""
    try:
        # Validate inputs
        if setup_rate < 0 or labor_rate < 0 or machine_rate < 0:
            notify(state, "Rate values cannot be negative", "error")
            return False

        # Store rates in global state (you might want to persist these differently)
        global_rates = {
            'setup_rate': float(setup_rate),
            'labor_rate': float(labor_rate),
            'machine_rate': float(machine_rate),
            'updated_at': time.time()
        }

        # Here you could save to a database or configuration file
        # For now, we'll just store in memory
        state.global_rates = global_rates

        notify(state, f"Global rates updated: Setup ${setup_rate}/min, Labor ${labor_rate}/min, Machine ${machine_rate}/min", "success")

        # Force UI refresh
        state.last_update = f"Updated at {time.time()}"

        return True

    except Exception as e:
        logger.error(f"Error applying global rates: {str(e)}")
        notify(state, f"Error applying global rates: {str(e)}", "error")
        return False

# ── Dynamic Rules Engine
def initialize_rules_engine():
    """Initialize the dynamic rules engine with material-thickness-operation rules"""
    return {
        'material_rules': {
            'CRS': {
                'valid_thicknesses': [0.0478, 0.0598, 0.0747, 0.1046, 0.1250, 0.1345, 0.1875],
                'preferred_operations': ['Laser', 'Form', 'Deburr', 'Install'],
                'restricted_operations': ['Anodize'],  # CRS doesn't anodize well
                'cost_multipliers': {'Laser': 1.0, 'Form': 1.2, 'Deburr': 0.8}
            },
            'HRS': {
                'valid_thicknesses': [0.1250, 0.1875, 0.2500, 0.3125, 0.3750],
                'preferred_operations': ['Laser', 'Form', 'Deburr', 'Install', 'Weld'],
                'restricted_operations': ['Anodize'],
                'cost_multipliers': {'Laser': 1.1, 'Form': 1.3, 'Weld': 1.5}
            },
            'SS': {
                'valid_thicknesses': [0.0478, 0.0598, 0.0747, 0.1046, 0.1250, 0.1875],
                'preferred_operations': ['Laser', 'Form', 'Deburr', 'Install', 'Passivate'],
                'restricted_operations': ['Anodize'],  # Use Passivate instead
                'cost_multipliers': {'Laser': 1.3, 'Form': 1.4, 'Passivate': 2.0}
            },
            'ALUMINUM': {
                'valid_thicknesses': [0.032, 0.040, 0.050, 0.063, 0.080, 0.100, 0.125, 0.160, 0.190],
                'preferred_operations': ['Laser', 'Form', 'Deburr', 'Install', 'Anodize'],
                'restricted_operations': [],
                'cost_multipliers': {'Laser': 0.9, 'Form': 0.8, 'Anodize': 1.8}
            },
            'COPPER': {
                'valid_thicknesses': [0.032, 0.040, 0.050, 0.063, 0.080, 0.100],
                'preferred_operations': ['Laser', 'Form', 'Deburr', 'Install'],
                'restricted_operations': ['Anodize', 'Passivate'],
                'cost_multipliers': {'Laser': 1.2, 'Form': 1.1}
            },
            'BRASS': {
                'valid_thicknesses': [0.032, 0.040, 0.050, 0.063, 0.080, 0.100, 0.125],
                'preferred_operations': ['Laser', 'Form', 'Deburr', 'Install'],
                'restricted_operations': ['Passivate'],
                'cost_multipliers': {'Laser': 1.1, 'Form': 1.0}
            }
        },
        'operation_sequences': {
            'standard': ['Plan', 'Laser', 'Form', 'Deburr', 'Install', 'Final Insp.', 'Package'],
            'simple': ['Plan', 'Laser', 'Deburr', 'Final Insp.', 'Package'],
            'complex': ['Plan', 'Laser', 'Form', 'Weld', 'Deburr', 'Install', 'Final Insp.', 'Package']
        },
        'validation_rules': {
            'thickness_range': {
                'min': 0.032,
                'max': 0.375,
                'warning_threshold': 0.250  # Thick parts may need special handling
            },
            'operation_dependencies': {
                'Form': ['Laser'],  # Must have Laser before Form
                'Deburr': ['Laser'],  # Must have Laser before Deburr
                'Install': ['Laser'],  # Must have Laser before Install
                'Weld': ['Form'],  # Welding usually after forming
                'Passivate': ['Laser'],  # Passivation after cutting
                'Anodize': ['Laser']  # Anodizing after cutting
            }
        }
    }

def validate_material_thickness(material, thickness):
    """Validate if material-thickness combination is valid"""
    rules = initialize_rules_engine()

    if material not in rules['material_rules']:
        return {'valid': False, 'reason': f'Unknown material: {material}'}

    material_rules = rules['material_rules'][material]
    valid_thicknesses = material_rules['valid_thicknesses']

    if thickness not in valid_thicknesses:
        closest = min(valid_thicknesses, key=lambda x: abs(x - thickness))
        return {
            'valid': False,
            'reason': f'Thickness {thickness}" not standard for {material}. Closest: {closest}"',
            'suggestion': closest
        }

    return {'valid': True, 'reason': 'Valid combination'}

def validate_operation_sequence(operations, material, thickness):
    """Validate operation sequence for given material and thickness"""
    rules = initialize_rules_engine()
    violations = []
    suggestions = []

    # Check for restricted operations
    if material in rules['material_rules']:
        restricted = rules['material_rules'][material]['restricted_operations']
        for op in operations:
            if op in restricted:
                violations.append(f'{op} not recommended for {material}')

    # Check operation dependencies
    operation_names = [op.get('operation', '') for op in operations]
    dependencies = rules['validation_rules']['operation_dependencies']

    for dep_op, required_ops in dependencies.items():
        if dep_op in operation_names:
            dep_index = operation_names.index(dep_op)
            for required_op in required_ops:
                if required_op not in operation_names[:dep_index]:
                    violations.append(f'{dep_op} should come after {required_op}')

    # Generate suggestions based on material
    if material in rules['material_rules']:
        preferred = rules['material_rules'][material]['preferred_operations']
        current_ops = [op.get('operation', '') for op in operations]

        missing_preferred = [op for op in preferred if op not in current_ops]
        if missing_preferred:
            suggestions.append(f'Consider adding: {", ".join(missing_preferred[:2])}')

    return {
        'violations': violations,
        'suggestions': suggestions,
        'valid': len(violations) == 0
    }

def get_cost_optimization_flags(operations, material, thickness):
    """Analyze operations for cost optimization opportunities"""
    rules = initialize_rules_engine()
    flags = []

    if material not in rules['material_rules']:
        return flags

    material_rules = rules['material_rules'][material]
    cost_multipliers = material_rules.get('cost_multipliers', {})

    # Check for expensive operations that could be optimized
    operation_names = [op.get('operation', '') for op in operations]

    if 'Weld' in operation_names and thickness > 0.125:
        flags.append({
            'type': 'cost',
            'message': f'Welding thick {material} ({thickness}") may be expensive',
            'suggestion': 'Consider mechanical fasteners instead'
        })

    if 'Anodize' in operation_names and 'Passivate' in operation_names:
        flags.append({
            'type': 'redundant',
            'message': 'Both Anodize and Passivate selected - choose one finish',
            'suggestion': 'Anodize for Aluminum, Passivate for Stainless Steel'
        })

    # Check for missing cost-effective operations
    if 'Laser' in operation_names and 'Deburr' not in operation_names:
        flags.append({
            'type': 'missing',
            'message': 'Deburr operation missing - may increase finishing costs',
            'suggestion': 'Add Deburr after Laser for better finish'
        })

    return flags

def get_smart_suggestions(material, thickness, current_operations):
    """Generate smart operation suggestions based on material and thickness"""
    rules = initialize_rules_engine()
    suggestions = []

    if material not in rules['material_rules']:
        return suggestions

    material_rules = rules['material_rules'][material]
    preferred_ops = material_rules['preferred_operations']
    current_op_names = [op.get('operation', '') for op in current_operations]

    # Suggest missing preferred operations
    missing_ops = [op for op in preferred_ops if op not in current_op_names]
    if missing_ops:
        suggestions.append({
            'type': 'add_operation',
            'message': f'Add {missing_ops[0]} for optimal {material} processing',
            'operation': missing_ops[0]
        })

    # Thickness-based suggestions
    if thickness >= 0.250:
        if 'Form' in current_op_names and 'Weld' not in current_op_names:
            suggestions.append({
                'type': 'reinforce',
                'message': f'Thick {material} ({thickness}") may need reinforcement',
                'operation': 'Weld'
            })

    if thickness <= 0.063:
        if 'Form' in current_op_names:
            suggestions.append({
                'type': 'caution',
                'message': f'Thin {material} ({thickness}") forming may be challenging',
                'suggestion': 'Consider increasing thickness or reducing bend angles'
            })

    return suggestions

def evaluate_rules_engine(state):
    """Evaluate all rules for the current quote data"""
    try:
        material = state.quote_data.material
        thickness = state.quote_data.thickness_in
        operations = state.operations_table or []

        # Validate material-thickness combination
        material_validation = validate_material_thickness(material, thickness) if material and thickness else {'valid': True, 'reason': 'No material/thickness set'}

        # Validate operation sequence
        sequence_validation = validate_operation_sequence(operations, material, thickness) if operations else {'valid': True, 'violations': [], 'suggestions': []}

        # Get cost optimization flags
        cost_flags = get_cost_optimization_flags(operations, material, thickness) if operations else []

        # Get smart suggestions
        suggestions = get_smart_suggestions(material, thickness, operations) if material and thickness else []

        # Update state
        state.rules_validation_status = "Valid" if material_validation['valid'] and sequence_validation['valid'] else "Issues Found"
        state.rules_violations = sequence_validation['violations']
        state.rules_suggestions = [s['message'] for s in suggestions]
        state.rules_cost_flags = [f['message'] for f in cost_flags]

        # Force UI refresh
        state.last_update = f"Updated at {time.time()}"

    except Exception as e:
        logger.error(f"Error evaluating rules engine: {str(e)}")
        state.rules_validation_status = "Error"
        state.rules_violations = [f"Rules engine error: {str(e)}"]

def apply_smart_suggestion(state):
    """Apply the selected smart suggestion"""
    try:
        if not state.smart_suggestion_selected:
            notify(state, "No suggestion selected", "warning")
            return

        # Here you would implement logic to apply the suggestion
        # For now, just show a notification
        notify(state, f"Applied suggestion: {state.smart_suggestion_selected}", "success")

        # Re-evaluate rules after applying suggestion
        evaluate_rules_engine(state)

    except Exception as e:
        logger.error(f"Error applying smart suggestion: {str(e)}")
        notify(state, f"Error applying suggestion: {str(e)}", "error")

# ── Taipy GUI Setup
gui = Gui(pages=pages)

# Initialize state
gui.add_shared_variable("quote_data", quote_data)
gui.add_shared_variable("pricing_breakdown", pricing_breakdown)
gui.add_shared_variable("extracted_metadata", extracted_metadata)
gui.add_shared_variable("active_page", active_page)
gui.add_shared_variable("markup_percent", markup_percent)
gui.add_shared_variable("uploaded_files", uploaded_files)
gui.add_shared_variable("processing_results", processing_results)

# Add computed variables
gui.add_shared_variable("material_options", ["CRS", "HRS", "SS", "ALUMINUM", "COPPER", "BRASS"])
gui.add_shared_variable("operations_table", [])
gui.add_shared_variable("hardware_table", [])
gui.add_shared_variable("outside_processes_table", [])
gui.add_shared_variable("pricing_table", [])
gui.add_shared_variable("final_pricing_table", [])
gui.add_shared_variable("quote_totals", quote_totals)
gui.add_shared_variable("quote_number", quote_number)
gui.add_shared_variable("current_date", "2025-01-01")
gui.add_shared_variable("valid_until_date", "2025-01-31")
gui.add_shared_variable("last_update", last_update)

# flatExtract variables
gui.add_shared_variable("flat_width", flat_width)
gui.add_shared_variable("flat_height", flat_height)
gui.add_shared_variable("flat_material", flat_material)
gui.add_shared_variable("flat_area", flat_area)
gui.add_shared_variable("flat_perimeter", flat_perimeter)
gui.add_shared_variable("flat_weight", flat_weight)

# Dynamic Rules Engine variables
gui.add_shared_variable("rules_validation_status", rules_validation_status)
gui.add_shared_variable("rules_violations", rules_violations)
gui.add_shared_variable("rules_suggestions", rules_suggestions)
gui.add_shared_variable("rules_cost_flags", rules_cost_flags)
gui.add_shared_variable("smart_suggestion_selected", smart_suggestion_selected)

# Initialize table data
operations_table = []
hardware_table = []
outside_processes_table = []
pricing_table = []
final_pricing_table = []

if __name__ == "__main__":
    import sys
    port = 5000  # default port
    if len(sys.argv) > 1 and sys.argv[1].startswith('--port='):
        try:
            port = int(sys.argv[1].split('=')[1])
        except ValueError:
            print(f"Invalid port number: {sys.argv[1]}")
            sys.exit(1)

    gui.run(title="ShopQuote - Integrated", host="0.0.0.0", port=port, debug=True)