# logic/edit_mode.py
"""
Edit mode functionality for ShopQuote operations
Handles add, edit, delete, and reorder operations with validation
"""

from typing import List, Dict, Any, Optional
from .ops import resequenced
from src.core.io_files import load_ops_name_options

class EditModeManager:
    """Manages edit mode operations for quotes"""

    def __init__(self):
        self.operation_options = load_ops_name_options()
        self.edit_buffer = []
        self.is_active = False

    def start_edit_mode(self, current_operations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Start edit mode with current operations"""
        self.edit_buffer = [op.copy() for op in current_operations]  # Deep copy
        self.is_active = True
        return self.edit_buffer.copy()

    def end_edit_mode(self) -> List[Dict[str, Any]]:
        """End edit mode and return final operations"""
        final_ops = resequenced(self.edit_buffer)
        self.edit_buffer = []
        self.is_active = False
        return final_ops

    def cancel_edit_mode(self) -> List[Dict[str, Any]]:
        """Cancel edit mode and discard changes"""
        self.edit_buffer = []
        self.is_active = False
        return []

    def add_operation(self, position: str = "end") -> List[Dict[str, Any]]:
        """Add new operation at specified position"""
        new_op = {
            "seq": len(self.edit_buffer) + 1,
            "operation": "",
            "setup_min": 0,
            "ops": 1,
            "time_sec": 0,
            "cost_per_part": 0.0,
            "is_new": True  # Flag for UI highlighting
        }

        if position == "end":
            self.edit_buffer.append(new_op)
        elif position == "before_final":
            # Insert before Final Insp. if it exists
            final_insp_idx = None
            for i, op in enumerate(self.edit_buffer):
                if op.get("operation", "").lower() == "final insp.":
                    final_insp_idx = i
                    break

            if final_insp_idx is not None:
                self.edit_buffer.insert(final_insp_idx, new_op)
            else:
                self.edit_buffer.append(new_op)

        return resequenced(self.edit_buffer)

    def delete_operation(self, sequence_number: int) -> List[Dict[str, Any]]:
        """Delete operation by sequence number"""
        # Don't allow deletion of mandatory operations
        mandatory_ops = ["plan", "final insp.", "package"]

        op_to_delete = None
        for op in self.edit_buffer:
            if op.get("seq") == sequence_number:
                op_to_delete = op
                break

        if op_to_delete:
            op_name = op_to_delete.get("operation", "").lower()
            if op_name in mandatory_ops:
                raise ValueError(f"Cannot delete mandatory operation: {op_to_delete.get('operation')}")

            self.edit_buffer = [op for op in self.edit_buffer if op.get("seq") != sequence_number]

        return resequenced(self.edit_buffer)

    def update_operation(self, sequence_number: int, updates: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Update operation properties"""
        for op in self.edit_buffer:
            if op.get("seq") == sequence_number:
                # Validate operation name if provided
                if "operation" in updates:
                    op_name = updates["operation"].strip()
                    if op_name and op_name not in self.operation_options:
                        # Try partial match
                        matches = [opt for opt in self.operation_options if op_name.lower() in opt.lower()]
                        if matches:
                            op_name = matches[0]  # Use first match
                        else:
                            raise ValueError(f"Invalid operation: {op_name}")

                    op["operation"] = op_name

                # Update other fields
                for key, value in updates.items():
                    if key != "operation":
                        if key in ["setup_min", "ops", "time_sec"]:
                            op[key] = max(0, int(value) if isinstance(value, (int, float)) else 0)
                        elif key == "cost_per_part":
                            op[key] = max(0.0, float(value) if isinstance(value, (int, float)) else 0.0)
                        else:
                            op[key] = value

                # Return the updated buffer
                return resequenced(self.edit_buffer)

        # If operation not found, return current buffer
        return resequenced(self.edit_buffer)

    def reorder_operations(self, from_seq: int, to_seq: int) -> List[Dict[str, Any]]:
        """Reorder operations by moving from_seq before to_seq"""
        if from_seq == to_seq:
            return self.edit_buffer.copy()

        # Find operations
        from_op = None
        from_idx = None
        to_idx = None

        for i, op in enumerate(self.edit_buffer):
            if op.get("seq") == from_seq:
                from_op = op
                from_idx = i
            elif op.get("seq") == to_seq:
                to_idx = i

        if from_op is None or to_idx is None:
            raise ValueError("Invalid sequence numbers for reordering")

        # Remove from current position
        self.edit_buffer.pop(from_idx)

        # Insert at new position (adjusting for removal)
        insert_pos = to_idx if to_idx < from_idx else to_idx - 1
        self.edit_buffer.insert(insert_pos, from_op)

        return resequenced(self.edit_buffer)

    def validate_operations(self) -> List[str]:
        """Validate current operations and return error messages"""
        errors = []

        if not self.edit_buffer:
            errors.append("At least one operation is required")
            return errors

        # Check for mandatory operations
        op_names = [op.get("operation", "").lower() for op in self.edit_buffer]
        mandatory_ops = ["plan", "final insp.", "package"]

        for mandatory in mandatory_ops:
            if mandatory not in op_names:
                errors.append(f"Missing mandatory operation: {mandatory.title()}")

        # Check sequence order (Final Insp. should be second-to-last, Package last)
        if len(self.edit_buffer) >= 2:
            second_last = self.edit_buffer[-2].get("operation", "").lower()
            last = self.edit_buffer[-1].get("operation", "").lower()

            if second_last != "final insp.":
                errors.append("Final Insp. must be second-to-last operation")
            if last != "package":
                errors.append("Package must be the last operation")

        # Check for duplicate operations
        seen_ops = set()
        for op in self.edit_buffer:
            op_name = op.get("operation", "").lower()
            if op_name and op_name in seen_ops:
                errors.append(f"Duplicate operation: {op_name.title()}")
            seen_ops.add(op_name)

        # Validate numeric fields
        for i, op in enumerate(self.edit_buffer, 1):
            if op.get("setup_min", 0) < 0:
                errors.append(f"Operation {i}: Setup time cannot be negative")
            if op.get("ops", 1) <= 0:
                errors.append(f"Operation {i}: Number of ops must be positive")
            if op.get("time_sec", 0) < 0:
                errors.append(f"Operation {i}: Time cannot be negative")

        return errors

    def get_operation_options(self) -> List[str]:
        """Get available operation options"""
        return self.operation_options.copy()

# Global edit mode manager instance
_edit_mode_manager = None

def get_edit_mode_manager() -> EditModeManager:
    """Get the global edit mode manager instance"""
    global _edit_mode_manager
    if _edit_mode_manager is None:
        _edit_mode_manager = EditModeManager()
    return _edit_mode_manager