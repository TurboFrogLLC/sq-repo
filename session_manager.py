# logic/session_manager.py
"""
Session management for ShopQuote Taipy
Handles saving/loading session data and user preferences
"""

import json
import os
from typing import Dict, Any, Optional
from pathlib import Path

class SessionManager:
    """Manages session data persistence"""

    def __init__(self, session_dir: str = None):
        if session_dir is None:
            # Default to user's home directory
            home = Path.home()
            session_dir = home / ".shopquote" / "sessions"

        self.session_dir = Path(session_dir)
        self.session_dir.mkdir(parents=True, exist_ok=True)

    def save_session(self, session_data: Dict[str, Any], session_name: str = "default") -> bool:
        """Save session data to file"""
        try:
            session_file = self.session_dir / f"{session_name}.json"

            # Add metadata
            session_data["_metadata"] = {
                "saved_at": str(Path(session_file).stat().st_mtime) if session_file.exists() else None,
                "version": "1.0"
            }

            with open(session_file, 'w') as f:
                json.dump(session_data, f, indent=2, default=str)

            return True
        except Exception as e:
            print(f"Error saving session: {e}")
            return False

    def load_session(self, session_name: str = "default") -> Optional[Dict[str, Any]]:
        """Load session data from file"""
        try:
            session_file = self.session_dir / f"{session_name}.json"

            if not session_file.exists():
                return None

            with open(session_file, 'r') as f:
                data = json.load(f)

            # Remove metadata before returning
            if "_metadata" in data:
                del data["_metadata"]

            return data
        except Exception as e:
            print(f"Error loading session: {e}")
            return None

    def list_sessions(self) -> list:
        """List available session files"""
        try:
            return [f.stem for f in self.session_dir.glob("*.json")]
        except Exception:
            return []

    def delete_session(self, session_name: str) -> bool:
        """Delete a session file"""
        try:
            session_file = self.session_dir / f"{session_name}.json"
            if session_file.exists():
                session_file.unlink()
                return True
            return False
        except Exception as e:
            print(f"Error deleting session: {e}")
            return False

# Global session manager instance
_session_manager = None

def get_session_manager() -> SessionManager:
    """Get the global session manager instance"""
    global _session_manager
    if _session_manager is None:
        _session_manager = SessionManager()
    return _session_manager

def save_current_session(state) -> bool:
    """Save current Taipy state to session file"""
    try:
        # Convert quote object to dictionary properly
        quote_data = {}
        if hasattr(state, 'quote') and state.quote:
            # Handle both dict and object types
            if isinstance(state.quote, dict):
                quote_data = state.quote.copy()
            else:
                # Convert object attributes to dict
                for attr in dir(state.quote):
                    if not attr.startswith('_'):
                        try:
                            value = getattr(state.quote, attr)
                            if not callable(value):
                                quote_data[attr] = value
                        except:
                            pass

        session_data = {
            "quote": quote_data,
            "operations": list(state.operations) if hasattr(state, 'operations') else [],
            "rates": {
                "setup_per_min": getattr(state, 'rates_setup_per_min', 60.0),
                "labor_per_min": getattr(state, 'rates_labor_per_min', 1.0),
                "machine_per_min": getattr(state, 'rates_machine_per_min', 1.5),
                "markup_percent": getattr(state, 'pricing_markup_percent', 15.0)
            },
            "settings": {
                "selected_database": getattr(state, 'selected_database', 'Materials')
            }
        }

        manager = get_session_manager()
        return manager.save_session(session_data)
    except Exception as e:
        print(f"Error saving current session: {e}")
        return False

def load_session_to_state(session_name: str, state) -> bool:
    """Load session data into Taipy state"""
    try:
        manager = get_session_manager()
        session_data = manager.load_session(session_name)

        if session_data is None:
            return False

        # Load quote data
        if "quote" in session_data:
            for key, value in session_data["quote"].items():
                setattr(state.quote, key, value)

        # Load operations
        if "operations" in session_data:
            state.operations = session_data["operations"]

        # Load rates
        if "rates" in session_data:
            rates = session_data["rates"]
            state.rates_setup_per_min = rates.get("setup_per_min", 60.0)
            state.rates_labor_per_min = rates.get("labor_per_min", 1.0)
            state.rates_machine_per_min = rates.get("machine_per_min", 1.5)
            state.pricing_markup_percent = rates.get("markup_percent", 15.0)

        # Load settings
        if "settings" in session_data:
            settings = session_data["settings"]
            state.selected_database = settings.get("selected_database", "Materials")

        return True
    except Exception as e:
        print(f"Error loading session to state: {e}")
        return False