from PyQt5.QtWidgets import (QMainWindow, QTabWidget, QWidget, QVBoxLayout, 
                            QPushButton, QTableWidget, QTableWidgetItem, 
                            QHeaderView)
from PyQt5.QtCore import Qt
from views.os_form import OSFormWindow
from views.kanbam_view import KanbanView
from views.clientes_view import ClientesView
from views.veiculos_view import VeiculosView
from database import criar_banco_dados
import sqlite3

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        criar_banco_dados()
        self.setWindowTitle("Sistema de Ordem de Serviço")
        self.setGeometry(100, 100, 1000, 600)
        
        self.central_widget = QTabWidget()
        self.setCentralWidget(self.central_widget)
        
        # Aba de Clientes
        self.tab_clientes = ClientesView()
        self.central_widget.addTab(self.tab_clientes, "Clientes")
        
        # Aba de Veículos
        self.tab_veiculos = VeiculosView()
        self.central_widget.addTab(self.tab_veiculos, "Veículos")
        
        # Aba de Ordens de Serviço
        self.tab_os = QWidget()
        self.setup_os_tab()
        self.central_widget.addTab(self.tab_os, "Ordens de Serviço")
        
        # Aba Kanban
        self.tab_kanban = KanbanView()
        self.central_widget.addTab(self.tab_kanban, "Kanban")
        
        self.load_os_data()
    
    def setup_os_tab(self):
        layout = QVBoxLayout()
        
        self.btn_nova_os = QPushButton("Nova Ordem de Serviço")
        self.btn_nova_os.clicked.connect(self.abrir_form_os)
        layout.addWidget(self.btn_nova_os)
        
        self.table_os = QTableWidget()
        self.table_os.setColumnCount(6)
        self.table_os.setHorizontalHeaderLabels(["ID", "Cliente", "Veículo", "Data", "Status", "Valor"])
        self.table_os.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_os.doubleClicked.connect(self.editar_os)
        layout.addWidget(self.table_os)
        
        self.tab_os.setLayout(layout)
    
    def abrir_form_os(self, os_id=None):
        self.form_os = OSFormWindow(os_id)
        self.form_os.os_salva.connect(self.load_os_data)
        self.form_os.show()
    
    def editar_os(self, index):
        row = index.row()
        os_id = self.table_os.item(row, 0).text()
        self.abrir_form_os(os_id)
    
    def load_os_data(self):
        conn = sqlite3.connect('sistema_os.db')
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT os.id, c.nome, v.marca || ' ' || v.modelo, os.data_abertura, os.status, os.valor_total
        FROM ordens_servico os
        JOIN veiculos v ON os.veiculo_id = v.id
        JOIN clientes c ON v.cliente_id = c.id
        ORDER BY os.data_abertura DESC
        ''')
        
        data = cursor.fetchall()
        self.table_os.setRowCount(len(data))
        
        for row_num, row_data in enumerate(data):
            for col_num, col_data in enumerate(row_data):
                item = QTableWidgetItem(str(col_data))
                item.setFlags(item.flags() ^ Qt.ItemIsEditable)
                self.table_os.setItem(row_num, col_num, item)
        
        conn.close()
        self.tab_kanban.load_kanban_data()