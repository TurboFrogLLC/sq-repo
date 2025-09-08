from taipy.gui import notify, navigate
from core.rules import MATERIAL_CHOICES, thickness_choices_for
from logic.quote_utils import normalize_quote_metadata
from logic.edit_mode import get_edit_mode_manager

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

def part_ops_page(state):
    """Part & Operations page with form and table"""
    page_md = """
# 📄 Part & Operations

<|container|
## 📋 Part Summary

**Quote #:** {quote.quote_number}

Customer: {quote.customer or '—'}
Part Number: {quote.part_number or '—'}
Material: {quote.material or '—'}
Thickness: {format_thickness(quote.thickness_in)}
Flat Size: {format_flat_size(quote.flat_size_in.width, quote.flat_size_in.height)}
Bends: {quote.bend_count or '—'}

### Material & Dimensions
<|in-customer|input|value={quote.customer}|label=Customer|>
<|in-part-number|input|value={quote.part_number}|label=Part Number|>
<|in-description|input|value={quote.description}|label=Description|>
<|{quote.material}|selector|lov={material_options}|on_change=on_material_change|label=Material|>
<|{quote.thickness_in}|selector|lov={thickness_options}|label=Thickness|>
<|{quote.flat_size_in.width}|number|label=Width (in)|min=0.0|step=0.125|>
<|{quote.flat_size_in.height}|number|label=Height (in)|min=0.0|step=0.125|>

### Additional Details
<|{quote.bend_count}|number|label=Bend Count|min=0|max=20|>

<|Save Part|button|on_action=on_save_part|class_name=success|>
|>

<|container|
## 🔧 Operations

<|{operations}|table|columns=Seq;Operation;Setup;Setup Cost;# Ops;Time;$/Part|show_all=True|>

<|btn-upload-files|file_selector|multiple|extensions=.dxf,.step,.stp,.pdf|label=Upload Files|on_action=on_upload_files|>

<|btn-generate-ops|button|on_action=on_generate_ops|>Generate Operations</button>
<|btn-enter-edit|button|on_action=on_edit_operations|>Edit ⚙️ Operations</button>

<|edit-mode-prompt|text|value={edit_mode_prompt}|class_name=edit-prompt|>
<|btn-generate-quote|button|on_action=on_generate_quote|class_name=primary|>Generate 📉 Quote</button>
|>

<style>
.success {
    background-color: #4caf50;
    color: white;
}

.primary {
    background-color: #1976d2;
    color: white;
    padding: 12px 24px;
    font-size: 16px;
}

.edit-prompt {
    background-color: #fff3cd;
    border: 1px solid #ffeaa7;
    border-radius: 4px;
    padding: 10px;
    margin: 10px 0;
    font-family: monospace;
    white-space: pre-line;
}

.success:hover, .primary:hover {
    opacity: 0.9;
}
</style>
"""

    # Prepare data for the page
    if not hasattr(state, 'material_options'):
        state.material_options = MATERIAL_CHOICES

    if not hasattr(state, 'thickness_options'):
        current_material = getattr(state.quote, 'material', 'CRS') or 'CRS'
        thickness_opts = thickness_choices_for(current_material)
        state.thickness_options = [label for label, _ in thickness_opts]

    # Initialize operations if not present
    if not hasattr(state, 'operations'):
        state.operations = []

    # Initialize edit mode prompt
    if not hasattr(state, 'edit_mode_prompt'):
        state.edit_mode_prompt = ""

    return page_md

def on_material_change(state):
    """Handle material selection change"""
    current_material = state.quote.material or 'CRS'
    thickness_opts = thickness_choices_for(current_material)
    state.thickness_options = [label for label, _ in thickness_opts]
    notify(state, "info", f"Material changed to {current_material}")

def on_save_part(state):
    """Save part information"""
    try:
        normalize_quote_metadata(state.quote)
        notify(state, "success", "Part information saved successfully")
    except Exception as e:
        notify(state, "error", f"Error saving part: {str(e)}")

def on_upload_files(state):
    """Handle file upload"""
    if hasattr(state, 'uploaded_files') and state.uploaded_files:
        notify(state, "success", f"Uploaded {len(state.uploaded_files)} file(s)")
    else:
        notify(state, "warning", "No files selected")

def on_generate_ops(state):
    """Generate operations from inputs and files"""
    notify(state, "info", "Operation generation - feature coming in Phase 5")

def on_add_operation(state):
    """Add new operation"""
    if not hasattr(state, 'operations'):
        state.operations = []

    new_op = {
        "seq": len(state.operations) + 1,
        "operation": "",
        "setup_min": 0,
        "ops": 1,
        "time_sec": 0,
        "cost_per_part": 0.0
    }

    state.operations.append(new_op)
    notify(state, "success", "New operation added")

def on_edit_operations(state):
    """Enter edit mode for operations"""
    try:
        edit_manager = get_edit_mode_manager()
        if not hasattr(state, 'operations') or not state.operations:
            notify(state, "warning", "No operations to edit. Add some operations first.")
            return

        # Start edit mode
        state.operations_edit_buffer = edit_manager.start_edit_mode(state.operations)
        state.edit_mode_active = True

        # Set edit mode prompt according to [EMX000.A] rules
        state.edit_mode_prompt = """📝 Edit Mode Active
Which seq would you like to edit? (e.g. 2)
type [ i ] to insert a new operation
type [ r ] to reorder sequence (e.g. 6 to 3)
🚀 type [ d ] to exit"""

        notify(state, "success", "Edit mode activated")
    except Exception as e:
        notify(state, "error", f"Error entering edit mode: {str(e)}")

def on_generate_quote(state):
    """Generate quote and navigate to breakdown"""
    if not state.quote.customer or not state.quote.part_number:
        notify(state, "warning", "Please fill in customer and part number before generating quote")
        return

    notify(state, "success", "Quote generated successfully")
    navigate(state, "quote-breakdown")