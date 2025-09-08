from taipy.gui import Html, navigate, notify

def main_page(state):
    """Main page with navigation tabs - Taipy style"""
    page_md = """
# 🏭 ShopQuote Quoting System

<|navbar|>

<|container|
## Welcome to ShopQuote

**Status:** ✅ Core Logic Migration Complete
**Phase:** 3 - UI Component Development

Select a tab above to begin quoting or manage your data.

### Quick Actions
<|New Quote|button|on_action=on_new_quote|class_name=primary|>
<|Load Quote|button|on_action=on_load_quote|>
<|Settings|button|on_action=on_settings|>

### System Status
- ✅ Business logic migrated and tested
- ✅ Pricing calculations working
- ✅ CSV data loading functional
- 🔄 UI components in development

### Recent Activity
- Core migration completed
- Demo server running at http://localhost:8000
- All business rules preserved
|>

<style>
.primary {
    background-color: #1976d2;
    color: white;
    padding: 12px 24px;
    border-radius: 6px;
    border: none;
    font-size: 16px;
    margin: 8px;
    cursor: pointer;
}

.primary:hover {
    background-color: #1565c0;
}
</style>
"""

    return page_md

def on_new_quote(state):
    """Start a new quote"""
    notify(state, "success", "Starting new quote...")
    navigate(state, "part-ops")

def on_load_quote(state):
    """Load existing quote"""
    notify(state, "info", "Quote loading feature coming in Phase 4")
    # TODO: Implement quote loading

def on_settings(state):
    """Navigate to settings"""
    navigate(state, "settings")