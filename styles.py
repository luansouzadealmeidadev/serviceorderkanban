from PyQt5.QtGui import QColor, QFont

# Cores modernas
PRIMARY_COLOR = "#2c3e50"
SECONDARY_COLOR = "#3498db"
ACCENT_COLOR = "#e74c3c"
BACKGROUND_COLOR = "#ecf0f1"
TEXT_COLOR = "#2c3e50"
CARD_COLOR = "#ffffff"

# Fontes
FONT_PRIMARY = QFont("Segoe UI", 10)
FONT_SECONDARY = QFont("Segoe UI", 9)
FONT_TITLE = QFont("Segoe UI", 12, QFont.Bold)

def apply_modern_style(app):
    style = f"""
    /* Geral */
    QWidget {{
        background-color: {BACKGROUND_COLOR};
        color: {TEXT_COLOR};
        font-family: "Segoe UI";
    }}
    
    /* Botões */
    QPushButton {{
        background-color: {SECONDARY_COLOR};
        color: white;
        border: none;
        padding: 8px 16px;
        border-radius: 4px;
        font-weight: bold;
        min-width: 80px;
    }}
    
    QPushButton:hover {{
        background-color: #2980b9;
    }}
    
    QPushButton:pressed {{
        background-color: {PRIMARY_COLOR};
    }}
    
    /* Abas */
    QTabWidget::pane {{
        border: 1px solid #bdc3c7;
        border-radius: 4px;
    }}
    
    QTabBar::tab {{
        background: #bdc3c7;
        color: {TEXT_COLOR};
        padding: 8px 16px;
        border-top-left-radius: 4px;
        border-top-right-radius: 4px;
        margin-right: 2px;
    }}
    
    QTabBar::tab:selected {{
        background: {SECONDARY_COLOR};
        color: white;
    }}
    
    /* Tabelas */
    QTableView {{
        background-color: white;
        alternate-background-color: #f8f9fa;
        gridline-color: #dee2e6;
        border-radius: 4px;
    }}
    
    QHeaderView::section {{
        background-color: {PRIMARY_COLOR};
        color: white;
        padding: 6px;
        border: none;
    }}
    
    /* Cards no Kanban */
    QListWidget {{
        background-color: transparent;
        border: none;
    }}
    
    QListWidget::item {{
        background-color: {CARD_COLOR};
        border-radius: 6px;
        margin: 4px;
        border: 1px solid #dfe6e9;
    }}
    
    QListWidget::item:hover {{
        border: 1px solid {SECONDARY_COLOR};
        background-color: #f1f9ff;
    }}
    
    /* GroupBox */
    QGroupBox {{
        border: 1px solid #bdc3c7;
        border-radius: 6px;
        margin-top: 10px;
        padding-top: 20px;
        font-weight: bold;
        color: {PRIMARY_COLOR};
    }}
    
    /* Inputs */
    QLineEdit, QTextEdit, QComboBox, QDateEdit, QSpinBox, QDoubleSpinBox {{
        background-color: white;
        border: 1px solid #bdc3c7;
        border-radius: 4px;
        padding: 5px;
    }}
    
    QLineEdit:focus, QTextEdit:focus {{
        border: 1px solid {SECONDARY_COLOR};
    }}
    
    /* ProgressBar */
    QProgressBar {{
        border: 1px solid #bdc3c7;
        border-radius: 4px;
        text-align: center;
    }}
    
    QProgressBar::chunk {{
        background-color: {SECONDARY_COLOR};
    }}
    """
    
    app.setStyleSheet(style)
    app.setFont(FONT_PRIMARY)