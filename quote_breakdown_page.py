from taipy.gui import notify, navigate
from logic.pricing import compute_pricing_table

def quote_breakdown_page(state):
    """Quote Breakdown page with pricing table"""
    page_md = """
# 📉 Quote Breakdown

<|container|
## 💰 Pricing Table

<|{pricing_table}|table|show_all=True|width=100%|>

<|Adjust Rates|button|on_action=on_adjust_rates|>
<|Back to Part & Ops|button|on_action=on_back_to_part_ops|>
<|View Summary|button|on_action=on_view_summary|class_name=primary|>
|>

<style>
.primary {
    background-color: #1976d2;
    color: white;
    padding: 12px 24px;
    font-size: 16px;
    margin-left: 10px;
}

.primary:hover {
    background-color: #1565c0;
}
</style>
"""

    # Generate pricing table if we have operations
    if hasattr(state, 'operations') and state.operations:
        try:
            rates = {
                "setup": getattr(state, 'rates_setup_per_min', 60.0),
                "labor": getattr(state, 'rates_labor_per_min', 1.0),
                "machine": getattr(state, 'rates_machine_per_min', 1.5)
            }
            quantities = [1, 10, 25, 50]
            markup = getattr(state, 'pricing_markup_percent', 15.0)

            table_data, summary = compute_pricing_table(
                state.operations, state.quote, rates, quantities, markup
            )

            # Format table data for display
            formatted_table = []
            for row_name, qty_values in table_data.items():
                row = {"Operation": row_name}
                for qty in quantities:
                    row[str(qty)] = f"${qty_values.get(qty, 0):.2f}"
                formatted_table.append(row)

            state.pricing_table = formatted_table

            # Summary values
            state.setup_total = ".2f"
            state.runtime_total = ".2f"
            state.hardware_total = ".2f"
            state.outside_process_total = ".2f"
            state.subtotal = ".2f"
            state.markup_percent = int(markup)
            state.markup_total = ".2f"
            state.grand_total = ".2f"

        except Exception as e:
            notify(state, "error", f"Error calculating pricing: {str(e)}")
            state.pricing_table = [{"Operation": "Error calculating pricing"}]
            # Set default values
            state.setup_total = "0.00"
            state.runtime_total = "0.00"
            state.hardware_total = "0.00"
            state.outside_process_total = "0.00"
            state.subtotal = "0.00"
            state.markup_percent = 15
            state.markup_total = "0.00"
            state.grand_total = "0.00"
    else:
        # No operations yet
        state.pricing_table = [{"Operation": "No operations defined"}]
        state.setup_total = "0.00"
        state.runtime_total = "0.00"
        state.hardware_total = "0.00"
        state.outside_process_total = "0.00"
        state.subtotal = "0.00"
        state.markup_percent = 15
        state.markup_total = "0.00"
        state.grand_total = "0.00"

    return page_md

def on_adjust_rates(state):
    """Navigate to settings to adjust rates"""
    notify(state, "info", "Rate adjustment - navigating to settings")
    navigate(state, "settings")

def on_back_to_part_ops(state):
    """Navigate back to part & operations"""
    navigate(state, "part-ops")

def on_view_summary(state):
    """Navigate to summary page"""
    navigate(state, "summary")