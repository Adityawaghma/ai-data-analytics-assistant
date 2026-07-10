"""
src/dashboard.py

DashboardWidget: a resizable grid layout for chart tiles, with built-in
auto-refresh support that polls the database on a timer and re-renders
all tiles with fresh data.

Combines:
  - Mon Jul 6 task: drag-and-resize grid layout (QGridLayout / QSplitter)
  - Wed Jul 8 task: auto-refresh via QTimer (start_refresh / stop_refresh)
"""

from PyQt5.QtWidgets import QWidget, QSplitter, QVBoxLayout, QSizePolicy
from PyQt5.QtCore import Qt, QTimer

# Assumes a DatabaseConnector class exists elsewhere in the project
# (e.g. src/db.py) exposing a `.query()` method that returns fresh data.
# Update this import path to match your actual project structure.
try:
    from .db import DatabaseConnector
except ImportError:  # pragma: no cover - fallback for direct script execution
    from src.db import DatabaseConnector


class DashboardWidget(QWidget):
    """
    A grid-based dashboard container for chart tiles.

    Tiles are added with add_tile(widget, row, col, rowspan, colspan) and
    are arranged in a resizable grid: each row is a horizontal QSplitter,
    and all rows sit inside an outer vertical QSplitter, so users can
    drag to resize both rows and columns.

    Also supports auto-refresh: start_refresh(interval_sec) polls the DB
    on a timer and re-renders all tiles with fresh data.
    """

    def __init__(self, db_connector: DatabaseConnector = None, parent=None):
        super().__init__(parent)

        # --- Layout setup ---
        self._outer_layout = QVBoxLayout(self)
        self._outer_layout.setContentsMargins(0, 0, 0, 0)

        self._row_splitter = QSplitter(Qt.Vertical)
        self._outer_layout.addWidget(self._row_splitter)

        # Track row splitters and tile positions so add_tile() can place
        # widgets by (row, col) similarly to a QGridLayout.
        self._rows = {}    # row_index -> QSplitter(Qt.Horizontal)
        self._tiles = {}   # (row, col) -> widget

        # --- Auto-refresh setup ---
        self.db = db_connector
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_data)
        self.refresh_interval = None  # seconds; set by settings panel (P3)

    # ------------------------------------------------------------------
    # Tile management
    # ------------------------------------------------------------------
    def add_tile(self, widget: QWidget, row: int, col: int,
                 rowspan: int = 1, colspan: int = 1):
        """
        Add a chart tile (ChartCanvas, Plotly view, or any QWidget) at the
        given grid position. rowspan/colspan are accepted for API
        compatibility; extend _get_row_splitter if you need true spanning
        across multiple rows/columns.
        """
        widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        row_splitter = self._get_row_splitter(row)
        row_splitter.addWidget(widget)

        self._tiles[(row, col)] = widget
        return widget

    def _get_row_splitter(self, row: int) -> QSplitter:
        """Return the horizontal splitter for a given row, creating it
        (and inserting it into the outer vertical splitter in order) if
        it doesn't exist yet."""
        if row not in self._rows:
            row_splitter = QSplitter(Qt.Horizontal)
            self._rows[row] = row_splitter

            # Keep rows in ascending order inside the outer splitter.
            insert_index = sorted(self._rows.keys()).index(row)
            self._row_splitter.insertWidget(insert_index, row_splitter)

        return self._rows[row]

    def clear_tiles(self):
        """Remove all tiles and row splitters (useful before rebuilding
        the layout, e.g. after a settings change)."""
        for row_splitter in self._rows.values():
            row_splitter.setParent(None)
            row_splitter.deleteLater()
        self._rows.clear()
        self._tiles.clear()

    # ------------------------------------------------------------------
    # Auto-refresh
    # ------------------------------------------------------------------
    def start_refresh(self, interval_sec: int):
        """Start (or restart) polling the DB every interval_sec seconds."""
        if interval_sec <= 0:
            raise ValueError("interval_sec must be positive")
        self.refresh_interval = interval_sec
        self.timer.start(interval_sec * 1000)  # QTimer uses milliseconds

    def stop_refresh(self):
        """Stop auto-refresh polling."""
        self.timer.stop()

    def refresh_data(self):
        """Re-query the DB and re-render all tiles with fresh data.

        Called automatically on each timer tick; can also be called
        manually to force an immediate refresh.
        """
        if self.db is None:
            return

        try:
            data = self.db.query()
        except Exception as exc:
            # Don't let a transient DB error kill the refresh loop.
            print(f"[DashboardWidget] refresh failed: {exc}")
            return

        self._render_tiles(data)

    def _render_tiles(self, data):
        """Push fresh data into each tile. Assumes each tile widget
        exposes an `update_data(data)` method (e.g. ChartCanvas.update_data).
        Adjust this if your chart widgets use a different render method."""
        for widget in self._tiles.values():
            if hasattr(widget, "update_data"):
                widget.update_data(data)
            elif hasattr(widget, "render"):
                widget.render(data)
            else:
                print(f"[DashboardWidget] tile {widget} has no known "
                      f"update method; skipping")


if __name__ == "__main__":
    # Minimal manual smoke test
    import sys
    from PyQt5.QtWidgets import QApplication, QLabel

    app = QApplication(sys.argv)
    dashboard = DashboardWidget()
    dashboard.add_tile(QLabel("Tile (0,0)"), 0, 0)
    dashboard.add_tile(QLabel("Tile (0,1)"), 0, 1)
    dashboard.add_tile(QLabel("Tile (1,0)"), 1, 0)
    dashboard.resize(800, 600)
    dashboard.show()
    sys.exit(app.exec_())