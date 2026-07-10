import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from PyQt5.QtWidgets import QApplication, QLabel
from src.dashboard import DashboardWidget

app = QApplication(sys.argv)
dash = DashboardWidget()
dash.resize(900, 600)


dash.add_tile(QLabel("Chart 1 (row0,col0)"), 0, 0)
dash.add_tile(QLabel("Chart 2 (row0,col1)"), 0, 1)
dash.add_tile(QLabel("KPI card (row1,col0)"), 1, 0)

dash.show()
sys.exit(app.exec_())