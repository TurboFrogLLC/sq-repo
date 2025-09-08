from taipy.gui import notify
from logic.session_manager import save_current_session, load_session_to_state, get_session_manager

def settings_page(state):
    """Settings page with database management"""
    page_md = """
<|layout|columns=1 4|
<|sidebar|
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

<|main|
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

<style>
.success {
    background-color: #4caf50;
    color: white;
    padding: 8px 16px;
}

.danger {
    background-color: #f44336;
    color: white;
    padding: 8px 16px;
}

.warning {
    background-color: #ff9800;
    color: white;
    padding: 8px 16px;
}

.success:hover, .danger:hover, .warning:hover {
    opacity: 0.9;
}
</style>
"""

    # Initialize settings if not present
    if not hasattr(state, 'rates_setup_per_min'):
        state.rates_setup_per_min = 60.0
    if not hasattr(state, 'rates_labor_per_min'):
        state.rates_labor_per_min = 1.0
    if not hasattr(state, 'rates_machine_per_min'):
        state.rates_machine_per_min = 1.5
    if not hasattr(state, 'pricing_markup_percent'):
        state.pricing_markup_percent = 15.0

    # Database options
    if not hasattr(state, 'database_options'):
        state.database_options = ["Materials", "Operations", "Hardware", "Outside Process", "Rates"]

    if not hasattr(state, 'selected_database'):
        state.selected_database = "Materials"

    # Load current table data
    load_table_data(state)

    # Session status
    if not hasattr(state, 'session_status'):
        state.session_status = "Session active - data pipeline connected"

    return page_md

def load_table_data(state):
    """Load table data based on selected database"""
    try:
        import os
        import pandas as pd

        data_dir = os.path.join(os.path.dirname(__file__), "..", "data")

        if state.selected_database == "Materials":
            df = pd.read_csv(os.path.join(data_dir, "Materials[UFG]_sQL.csv"))
        elif state.selected_database == "Operations":
            df = pd.read_csv(os.path.join(data_dir, "Operations[UFG]_sQL.csv"))
        elif state.selected_database == "Hardware":
            df = pd.read_csv(os.path.join(data_dir, "Hardware[UFG]_sQL.csv"))
        elif state.selected_database == "Outside Process":
            df = pd.read_csv(os.path.join(data_dir, "OutsideProcess[UFG]_sQL.csv"))
        elif state.selected_database == "Rates":
            df = pd.read_csv(os.path.join(data_dir, "Rates[UFG]_sQL.csv"))
        else:
            df = pd.DataFrame()

        state.current_table = df.to_dict('records')
        state.table_row_count = len(df)

    except Exception as e:
        state.current_table = [{"Error": f"Failed to load {state.selected_database}: {str(e)}"}]
        state.table_row_count = 0

def on_save_rates(state):
    """Save rate configuration"""
    try:
        # Update the rates in the global state
        rates_data = {
            "setup_per_min": state.rates_setup_per_min,
            "labor_per_min": state.rates_labor_per_min,
            "machine_per_min": state.rates_machine_per_min,
            "markup_percent": state.pricing_markup_percent
        }
        # In a full implementation, this would persist to a configuration file
        notify(state, "success", ".2f")
    except Exception as e:
        notify(state, "error", f"Error saving rates: {str(e)}")

def on_database_change(state):
    """Handle database selection change"""
    load_table_data(state)
    notify(state, "info", f"Loaded {state.table_row_count} rows from {state.selected_database}")

def on_add_row(state):
    """Add new row to selected database"""
    notify(state, "info", "Add row functionality - implemented in Phase 5")
    # TODO: Implement add row modal/form in Phase 5

def on_edit_row(state):
    """Edit selected row"""
    notify(state, "info", "Edit row functionality - implemented in Phase 5")
    # TODO: Implement edit row modal/form in Phase 5

def on_delete_row(state):
    """Delete selected row"""
    notify(state, "warning", "Delete row functionality - implemented in Phase 5")
    # TODO: Implement delete confirmation and row removal in Phase 5

def on_refresh_table(state):
    """Refresh the current table data"""
    load_table_data(state)
    notify(state, "success", f"Refreshed {state.selected_database} data ({state.table_row_count} rows)")

def on_load_session(state):
    """Load session data"""
    try:
        manager = get_session_manager()
        sessions = manager.list_sessions()

        if not sessions:
            notify(state, "info", "No saved sessions found")
            return

        # Load the most recent session (default)
        if load_session_to_state("default", state):
            # Refresh table data after loading
            load_table_data(state)
            notify(state, "success", "Session loaded successfully")
        else:
            notify(state, "error", "Failed to load session")
    except Exception as e:
        notify(state, "error", f"Error loading session: {str(e)}")

def on_save_session(state):
    """Save session data"""
    try:
        if save_current_session(state):
            notify(state, "success", "Session saved successfully")
        else:
            notify(state, "error", "Failed to save session")
    except Exception as e:
        notify(state, "error", f"Error saving session: {str(e)}")

def on_reset_session(state):
    """Reset session to defaults"""
    try:
        # Reset rates to defaults
        state.rates_setup_per_min = 60.0
        state.rates_labor_per_min = 1.0
        state.rates_machine_per_min = 1.5
        state.pricing_markup_percent = 15.0
        state.selected_database = "Materials"

        # Reset quote and operations
        state.quote = type('Quote', (), {
            "quote_number": "",
            "customer": "",
            "part_number": "",
            "description": "",
            "material": "",
            "thickness_in": None,
            "flat_size_in": {"width": None, "height": None},
            "bend_count": None,
            "hardware": [],
            "outside_processes": [],
        })()

        state.operations = []

        # Refresh table data
        load_table_data(state)
        notify(state, "warning", "Session reset to default values")
    except Exception as e:
        notify(state, "error", f"Error resetting session: {str(e)}")

def on_back_to_part_ops(state):
    """Navigate back to Part & Operations"""
    from taipy.gui import navigate
    navigate(state, "part-ops")

def on_back_to_breakdown(state):
    """Navigate back to Quote Breakdown"""
    from taipy.gui import navigate
    navigate(state, "quote-breakdown")

def on_back_to_summary(state):
    """Navigate back to Summary"""
    from taipy.gui import navigate
    navigate(state, "summary")