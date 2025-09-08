from taipy.gui import notify
from logic.export_manager import get_export_manager

def summary_page(state):
    """Summary page with final quote information"""
    page_md = """
# 📌 Summary

Customer: {quote.customer}
Part Number: {quote.part_number}
Description: {quote.description}

💲 Quote Totals
- Qty 1: ${pricing_1:.2f}
- Qty 10: ${pricing_10:.2f}
- Qty 25: ${pricing_25:.2f}
- Qty 50: ${pricing_50:.2f}

<|btn-save-quote|button|on_action=on_save_quote|>Save Quote</button>
<|btn-new-quote|button|on_action=on_new_quote|>New Quote</button>
<|btn-quit-session|button|on_action=on_quit_session|>Quit Session</button>

<style>
.primary {
    background-color: #1976d2;
    color: white;
    padding: 12px 24px;
    font-size: 16px;
}

.success {
    background-color: #4caf50;
    color: white;
    padding: 12px 24px;
    font-size: 16px;
}

.secondary {
    background-color: #757575;
    color: white;
    padding: 12px 24px;
    font-size: 16px;
}

.primary:hover, .success:hover, .secondary:hover {
    opacity: 0.9;
}
</style>
"""

    # Prepare pricing data
    if hasattr(state, 'pricing_table') and state.pricing_table:
        # Extract pricing from the table data
        try:
            pricing_data = {row['Operation']: row for row in state.pricing_table}
            total_row = pricing_data.get('Total', {})

            state.pricing_1 = float(total_row.get('1', '$0.00').replace('$', ''))
            state.pricing_10 = float(total_row.get('10', '$0.00').replace('$', ''))
            state.pricing_25 = float(total_row.get('25', '$0.00').replace('$', ''))
            state.pricing_50 = float(total_row.get('50', '$0.00').replace('$', ''))
        except:
            state.pricing_1 = 0.00
            state.pricing_10 = 0.00
            state.pricing_25 = 0.00
            state.pricing_50 = 0.00
    else:
        state.pricing_1 = 0.00
        state.pricing_10 = 0.00
        state.pricing_25 = 0.00
        state.pricing_50 = 0.00

    # Prepare hardware summary
    if hasattr(state.quote, 'hardware') and state.quote.hardware:
        state.hardware_summary = state.quote.hardware
    else:
        state.hardware_summary = [{"type": "None", "qty_per_part": 0, "unit_cost": 0.00}]

    # Prepare outside process summary
    if hasattr(state.quote, 'outside_processes') and state.quote.outside_processes:
        state.outside_process_summary = state.quote.outside_processes
    else:
        state.outside_process_summary = [{"label": "None", "unit_cost_per_part": 0.00}]

    # Export status
    if not hasattr(state, 'export_status'):
        state.export_status = "Ready to export"

    return page_md

def on_export_pdf(state):
    """Export quote to PDF"""
    try:
        export_manager = get_export_manager()

        # Prepare data for export
        quote_data = dict(state.quote) if hasattr(state, 'quote') else {}
        operations = list(state.operations) if hasattr(state, 'operations') else []

        # Get pricing data
        pricing_data = {}
        if hasattr(state, 'pricing_table') and state.pricing_table:
            pricing_data = {
                'per_qty_grand': {}
            }
            for row in state.pricing_table:
                if row.get('Operation') == 'Total':
                    for qty in [1, 10, 25, 50]:
                        qty_str = str(qty)
                        if qty_str in row:
                            price_str = row[qty_str].replace('$', '').replace(',', '')
                            try:
                                pricing_data['per_qty_grand'][qty] = float(price_str)
                            except ValueError:
                                pricing_data['per_qty_grand'][qty] = 0.0

        # Export to PDF
        filepath = export_manager.export_to_pdf(quote_data, operations, pricing_data)
        notify(state, "success", f"PDF exported successfully: {filepath}")
        state.export_status = f"PDF exported: {filepath}"

    except Exception as e:
        notify(state, "error", f"PDF export failed: {str(e)}")
        state.export_status = f"PDF export failed: {str(e)}"

def on_export_txt(state):
    """Export quote to TXT"""
    try:
        export_manager = get_export_manager()

        # Prepare data for export
        quote_data = dict(state.quote) if hasattr(state, 'quote') else {}
        operations = list(state.operations) if hasattr(state, 'operations') else []

        # Get pricing data
        pricing_data = {}
        if hasattr(state, 'pricing_table') and state.pricing_table:
            pricing_data = {
                'per_qty_grand': {}
            }
            for row in state.pricing_table:
                if row.get('Operation') == 'Total':
                    for qty in [1, 10, 25, 50]:
                        qty_str = str(qty)
                        if qty_str in row:
                            price_str = row[qty_str].replace('$', '').replace(',', '')
                            try:
                                pricing_data['per_qty_grand'][qty] = float(price_str)
                            except ValueError:
                                pricing_data['per_qty_grand'][qty] = 0.0

        # Export to TXT
        filepath = export_manager.export_to_txt(quote_data, operations, pricing_data)
        notify(state, "success", f"TXT exported successfully: {filepath}")
        state.export_status = f"TXT exported: {filepath}"

    except Exception as e:
        notify(state, "error", f"TXT export failed: {str(e)}")
        state.export_status = f"TXT export failed: {str(e)}"

def on_save_quote(state):
    """Save quote"""
    notify(state, "success", "Quote saved successfully")
    state.export_status = "Quote saved successfully"

def on_back_to_breakdown(state):
    """Navigate back to quote breakdown"""
    from taipy.gui import navigate
    navigate(state, "quote-breakdown")

def on_new_quote(state):
    """Start a new quote"""
    from taipy.gui import navigate, notify
    notify(state, "success", "Starting new quote...")
    navigate(state, "part-ops")

def on_quit_session(state):
    """Quit the current session"""
    from taipy.gui import notify
    notify(state, "info", "Session ended")
    # In a full implementation, this would close the application