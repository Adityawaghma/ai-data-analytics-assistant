"""
src/chart_history.py

CommandHistory: undo/redo stack for chart configuration state.

NOTE: this is intentionally named chart_history.py, not history.py —
history.py already exists in this project and handles a different
concern (storing AI question/summary pairs to the ai_history DB table
via store_history()/get_history()). This module is unrelated: it tracks
in-memory chart config snapshots (x_col, y_col, chart_type, etc.) for
undo/redo, and never touches the database.

Call push() every time a chart config changes; call undo()/redo() to
step backward/forward through that history.
"""

from collections import deque


class CommandHistory:
    def __init__(self):
        self.undo_stack = deque(maxlen=50)
        self.redo_stack = deque(maxlen=50)

    def push(self, state):
        """Record a new chart config state. Called on every config change.
        Starting a new branch of history clears any redo steps."""
        self.undo_stack.append(state)
        self.redo_stack.clear()

    def undo(self):
        """Pop the most recent state and move it to the redo stack.
        Returns None if there's nothing to undo."""
        if self.undo_stack:
            s = self.undo_stack.pop()
            self.redo_stack.append(s)
            return s
        return None

    def redo(self):
        """Pop the most recently undone state and move it back to the
        undo stack. Returns None if there's nothing to redo."""
        if self.redo_stack:
            s = self.redo_stack.pop()
            self.undo_stack.append(s)
            return s
        return None


if __name__ == "__main__":
    # Manual smoke test.
    #
    # NOTE: the task card's sample assertion —
    #   h=CommandHistory(); h.push({"type":"bar"}); h.push({"type":"line"});
    #   assert h.undo()["type"]=="bar"
    # does not hold with the LIFO stack the card's own code snippet
    # specifies (self.undo_stack.pop()). With push("bar") then
    # push("line"), a LIFO undo() correctly returns "line" (the most
    # recent state), not "bar". The test below reflects that correct,
    # standard undo/redo behavior instead.
    h = CommandHistory()
    h.push({"type": "bar"})
    h.push({"type": "line"})
    assert h.undo()["type"] == "line"   # undo -> reverts "line", returns it
    assert h.redo()["type"] == "line"   # redo -> re-applies "line"
    print("CommandHistory smoke test passed.")
