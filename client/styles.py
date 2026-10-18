DARK_THEME_QSS = """
QMainWindow { background-color: #121316; }
QWidget { color: #FFFFFF; font-family: 'Segoe UI', 'Ubuntu', sans-serif; font-size: 13px; }
QFrame.card { background-color: #1B1D22; border-radius: 14px; border: 1px solid #262930; }
QFrame.card-subtle { background-color: #15161A; border-radius: 10px; border: 1px solid #22252C; }
QFrame#sidebar { background-color: #17181D; border-right: 1px solid #23252C; }
QPushButton.sidebar-btn { background-color: transparent; border: none; border-radius: 8px; color: #8E929E; font-size: 16px; padding: 10px; }
QPushButton.sidebar-btn:hover { background-color: #24262E; color: #C4F135; }
QPushButton.sidebar-btn:checked { background-color: #262932; color: #C4F135; border-left: 2px solid #C4F135; }
QLabel.title { font-size: 22px; font-weight: 700; color: #FFFFFF; }
QLabel.subtitle { font-size: 12px; color: #808593; }
QLabel.metric-value { font-size: 20px; font-weight: 700; }
QListWidget { background-color: #16171B; border: 1px solid #262930; border-radius: 8px; padding: 4px; color: #E2E4E9; }
QListWidget::item { padding: 8px; border-radius: 6px; margin-bottom: 2px; }
QListWidget::item:hover { background-color: #23262E; }
QListWidget::item:selected { background-color: #2D313B; color: #C4F135; }
QTableWidget { background-color: #16171B; border: 1px solid #262930; border-radius: 8px; gridline-color: #202228; color: #FFFFFF; }
QTableWidget::item { padding: 6px; }
QHeaderView::section { background-color: #1B1D22; color: #7A7F8D; font-weight: 600; font-size: 11px; border: none; padding: 6px; }
QPushButton.primary-btn { background-color: #C4F135; color: #121316; font-weight: 700; font-size: 13px; border-radius: 10px; padding: 12px; border: none; }
QPushButton.primary-btn:hover { background-color: #D4F63D; }
QPushButton.secondary-btn { background-color: #24262E; color: #E5E7EB; border: 1px solid #30333D; border-radius: 8px; padding: 8px; font-weight: 600; }
QPushButton.secondary-btn:hover { background-color: #2E313B; border-color: #424654; }
QPushButton.table-btn { background-color: #24262E; color: #C4F135; border: 1px solid #323540; border-radius: 5px; padding: 3px 8px; font-size: 11px; font-weight: 600; }
QPushButton.table-btn:hover { background-color: #C4F135; color: #121316; }
"""
