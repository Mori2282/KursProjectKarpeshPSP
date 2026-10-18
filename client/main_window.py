from typing import List
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QListWidget, QTableWidget, QTableWidgetItem, QFileDialog,
    QLabel, QMessageBox, QHeaderView, QAbstractItemView, QFrame
)
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QColor
from client.api_client import APIClient
from client.styles import DARK_THEME_QSS

class MainWindow(QMainWindow):
    AVAILABLE_FILTERS = [
        {"name": "denoise_gaussian", "display": "Gaussian Filter (k=5)", "params": {"kernel_size": 5, "sigma": 1.5}},
        {"name": "denoise_nlmeans", "display": "Fast NL-Means Denoise", "params": {"h": 10.0}},
        {"name": "grayscale", "display": "Grayscale Conversion", "params": {}},
        {"name": "clahe", "display": "Contrast CLAHE Tuner", "params": {"clip_limit": 3.0, "tile_grid_size": 8}},
        {"name": "kmeans", "display": "K-Means Quantize (k=8)", "params": {"k": 8}},
        {"name": "canny", "display": "Canny Edge Detector", "params": {"low_threshold": 50, "high_threshold": 150}},
        {"name": "sobel", "display": "Sobel Gradient Operator", "params": {"kernel_size": 3}},
    ]

    def __init__(self):
        super().__init__()
        self.setWindowTitle("VisionFlow Studio | Distributed Pipeline")
        self.resize(1180, 720)
        self.setStyleSheet(DARK_THEME_QSS)
        self.api = APIClient()
        self.selected_files: List[str] = []

        self.init_layout()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.sync_dashboard)
        self.timer.start(2500)

    def init_layout(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # 1. Сайдбар
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(64)
        sb_layout = QVBoxLayout(sidebar)
        sb_layout.setContentsMargins(8, 16, 8, 16)
        
        btn_profile = QPushButton("M")
        btn_profile.setStyleSheet("background-color: #C4F135; color: #121316; font-weight: 900; font-size: 15px; border-radius: 12px; height: 40px;")
        sb_layout.addWidget(btn_profile)
        sb_layout.addSpacing(20)

        for sym, act in [("▦", True), ("⚡", False), ("⚙", False)]:
            b = QPushButton(sym)
            b.setProperty("class", "sidebar-btn")
            b.setCheckable(True)
            b.setChecked(act)
            b.setFixedHeight(40)
            sb_layout.addWidget(b)

        sb_layout.addStretch()
        btn_exit = QPushButton("⏻")
        btn_exit.setProperty("class", "sidebar-btn")
        btn_exit.clicked.connect(self.close)
        sb_layout.addWidget(btn_exit)
        root.addWidget(sidebar)

        # 2. Главная зона
        content = QWidget()
        c_layout = QHBoxLayout(content)
        c_layout.setContentsMargins(20, 20, 20, 20)
        c_layout.setSpacing(18)

        # Левая часть главной зоны
        center_vbox = QVBoxLayout()
        center_vbox.setSpacing(16)

        lbl_greeting = QLabel("Hello Mori!")
        lbl_greeting.setProperty("class", "title")
        center_vbox.addWidget(lbl_greeting)

        # Метрики
        m_container = QWidget()
        m_layout = QHBoxLayout(m_container)
        m_layout.setContentsMargins(0, 0, 0, 0)
        
        self.card_workers = self._create_card("ACTIVE WORKERS", "4 Online", "#C4F135")
        self.card_queue = self._create_card("IN PIPELINE", "0 Tasks", "#FF8C42")
        self.card_done = self._create_card("COMPLETED", "0 Done", "#26D0CE")
        m_layout.addWidget(self.card_workers)
        m_layout.addWidget(self.card_queue)
        m_layout.addWidget(self.card_done)
        center_vbox.addWidget(m_container)

        # Рабочее пространство
        workspace = QFrame()
        workspace.setProperty("class", "card")
        ws_layout = QHBoxLayout(workspace)
        
        v_files = QVBoxLayout()
        v_files.addWidget(QLabel("1. Selected Images:"))
        self.list_files = QListWidget()
        v_files.addWidget(self.list_files)
        btn_f = QPushButton("Browse Files...")
        btn_f.setProperty("class", "secondary-btn")
        btn_f.clicked.connect(self.choose_files)
        v_files.addWidget(btn_f)
        ws_layout.addLayout(v_files)

        v_cat = QVBoxLayout()
        v_cat.addWidget(QLabel("2. Filter Catalog:"))
        self.list_available = QListWidget()
        for f in self.AVAILABLE_FILTERS:
            self.list_available.addItem(f["display"])
        v_cat.addWidget(self.list_available)
        btn_add = QPushButton("Add Filter ->")
        btn_add.setProperty("class", "secondary-btn")
        btn_add.clicked.connect(self.append_filter)
        v_cat.addWidget(btn_add)
        ws_layout.addLayout(v_cat)

        v_pipe = QVBoxLayout()
        v_pipe.addWidget(QLabel("3. Execution Sequence:"))
        self.list_pipeline = QListWidget()
        v_pipe.addWidget(self.list_pipeline)
        btn_clr = QPushButton("Clear Sequence")
        btn_clr.setProperty("class", "secondary-btn")
        btn_clr.clicked.connect(self.list_pipeline.clear)
        v_pipe.addWidget(btn_clr)
        ws_layout.addLayout(v_pipe)

        center_vbox.addWidget(workspace, 1)
        c_layout.addLayout(center_vbox, 65)

        # Правая панель
        panel = QFrame()
        panel.setProperty("class", "card")
        p_layout = QVBoxLayout(panel)
        
        lbl_control = QLabel("Quick Dispatch")
        lbl_control.setStyleSheet("font-size: 15px; font-weight: 700;")
        p_layout.addWidget(lbl_control)

        self.btn_dispatch = QPushButton("DISPATCH PIPELINE")
        self.btn_dispatch.setProperty("class", "primary-btn")
        self.btn_dispatch.clicked.connect(self.dispatch_batch)
        p_layout.addWidget(self.btn_dispatch)

        p_layout.addSpacing(10)
        p_layout.addWidget(QLabel("Last Tasks"))

        self.table_tasks = QTableWidget(0, 3)
        self.table_tasks.setHorizontalHeaderLabels(["Target", "Status", "Action"])
        self.table_tasks.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table_tasks.verticalHeader().setVisible(False)
        self.table_tasks.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        p_layout.addWidget(self.table_tasks, 1)

        c_layout.addWidget(panel, 35)
        root.addWidget(content)

    def _create_card(self, title: str, value: str, accent: str) -> QFrame:
        c = QFrame()
        c.setProperty("class", "card")
        l = QVBoxLayout(c)
        l.setContentsMargins(12, 10, 12, 10)
        t = QLabel(title)
        t.setStyleSheet("font-size: 10px; font-weight: 700; color: #7B808C;")
        v = QLabel(value)
        v.setProperty("class", "metric-value")
        v.setStyleSheet(f"color: {accent};")
        l.addWidget(t)
        l.addWidget(v)
        return c

    def choose_files(self):
        f, _ = QFileDialog.getOpenFileNames(self, "Select Images", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if f:
            self.selected_files = f
            self.list_files.clear()
            for path in f:
                self.list_files.addItem(path.split("/")[-1])

    def append_filter(self):
        row = self.list_available.currentRow()
        if row >= 0:
            self.list_pipeline.addItem(self.AVAILABLE_FILTERS[row]["display"])

    def dispatch_batch(self):
        if not self.selected_files or self.list_pipeline.count() == 0:
            QMessageBox.warning(self, "Attention", "Select files and configure steps.")
            return

        steps = []
        for i in range(self.list_pipeline.count()):
            txt = self.list_pipeline.item(i).text()
            item = next(f for f in self.AVAILABLE_FILTERS if f["display"] == txt)
            steps.append({"name": item["name"], "params": item["params"]})

        try:
            self.api.upload_images(self.selected_files, steps)
            QMessageBox.information(self, "Success", "Tasks submitted to worker pipeline!")
            self.selected_files.clear()
            self.list_files.clear()
            self.sync_dashboard()
        except Exception as e:
            QMessageBox.critical(self, "Failure", str(e))

    def sync_dashboard(self):
        try:
            tasks = self.api.get_all_tasks()
        except Exception:
            return

        in_progress = sum(1 for t in tasks if t["status"] in ("pending", "processing"))
        completed = sum(1 for t in tasks if t["status"] == "completed")

        self.card_queue.findChild(QLabel, "").setText(f"{in_progress} Tasks")
        self.card_done.findChild(QLabel, "").setText(f"{completed} Done")

        self.table_tasks.setRowCount(0)
        for t in tasks[:15]:
            r = self.table_tasks.rowCount()
            self.table_tasks.insertRow(r)
            self.table_tasks.setItem(r, 0, QTableWidgetItem(t["original_filename"][:14]))

            st = QTableWidgetItem(t["status"])
            if t["status"] == "completed":
                st.setForeground(QColor("#C4F135"))
            elif t["status"] == "processing":
                st.setForeground(QColor("#26D0CE"))
            elif t["status"] == "failed":
                st.setForeground(QColor("#FF4D4D"))
            self.table_tasks.setItem(r, 1, st)

            if t["status"] == "completed":
                btn = QPushButton("Save")
                btn.setProperty("class", "table-btn")
                btn.clicked.connect(lambda _, tid=t["id"], fn=t["original_filename"]: self.save_file(tid, fn))
                self.table_tasks.setCellWidget(r, 2, btn)
            elif t["status"] == "failed":
                btn_err = QPushButton("Log")
                btn_err.setProperty("class", "table-btn")
                btn_err.clicked.connect(lambda _, err=t.get("error_message"): QMessageBox.critical(self, "Error", str(err)))
                self.table_tasks.setCellWidget(r, 2, btn_err)

    def save_file(self, task_id: str, filename: str):
        p, _ = QFileDialog.getSaveFileName(self, "Save File", f"proc_{filename}", "Images (*.png *.jpg)")
        if p:
            try:
                self.api.download_image(task_id, p)
                QMessageBox.information(self, "Saved", "File written successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))
