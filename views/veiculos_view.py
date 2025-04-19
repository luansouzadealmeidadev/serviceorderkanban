from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QTableView, QPushButton, 
                            QHeaderView, QMessageBox, QHBoxLayout, QComboBox)
from PyQt5.QtSql import QSqlTableModel, QSqlDatabase
from PyQt5.QtCore import Qt
import sqlite3

class VeiculosView(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Filtro por cliente
        self.cb_clientes = QComboBox()
        self.carregar_clientes()
        self.cb_clientes.currentIndexChanged.connect(self.filtrar_veiculos)
        
        # Botões
        btn_layout = QHBoxLayout()
        btn_novo = QPushButton("Novo Veículo")
        btn_novo.clicked.connect(self.novo_veiculo)
        btn_editar = QPushButton("Editar")
        btn_editar.clicked.connect(self.editar_veiculo)
        btn_excluir = QPushButton("Excluir")
        btn_excluir.clicked.connect(self.excluir_veiculo)
        
        btn_layout.addWidget(btn_novo)
        btn_layout.addWidget(btn_editar)
        btn_layout.addWidget(btn_excluir)
        
        # Tabela
        self.tabela = QTableView()
        self.tabela.setSelectionBehavior(QTableView.SelectRows)
        self.carregar_dados()
        
        layout.addWidget(self.cb_clientes)
        layout.addLayout(btn_layout)
        layout.addWidget(self.tabela)
        self.setLayout(layout)
    
    def carregar_clientes(self):
        conn = sqlite3.connect('sistema_os.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome FROM clientes ORDER BY nome")
        clientes = cursor.fetchall()
        
        self.cb_clientes.clear()
        self.cb_clientes.addItem("Todos os clientes", 0)
        for cliente in clientes:
            self.cb_clientes.addItem(cliente[1], cliente[0])
        
        conn.close()
    
    def carregar_dados(self):
        db = QSqlDatabase.addDatabase("QSQLITE")
        db.setDatabaseName("sistema_os.db")
        
        if not db.open():
            QMessageBox.critical(self, "Erro", "Não foi possível abrir o banco de dados")
            return
        
        self.model = QSqlTableModel()
        self.model.setTable("veiculos")
        self.model.select()
        self.model.setEditStrategy(QSqlTableModel.OnFieldChange)
        
        self.tabela.setModel(self.model)
        self.tabela.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    
    def filtrar_veiculos(self):
        cliente_id = self.cb_clientes.currentData()
        
        if cliente_id == 0:  # Todos os clientes
            self.model.setFilter("")
        else:
            self.model.setFilter(f"cliente_id = {cliente_id}")
        
        self.model.select()
    
    def novo_veiculo(self):
        from PyQt5.QtWidgets import QDialog, QFormLayout, QLineEdit, QSpinBox, QDialogButtonBox
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Novo Veículo")
        
        layout = QFormLayout()
        
        self.le_marca = QLineEdit()
        self.le_modelo = QLineEdit()
        self.sb_ano = QSpinBox()
        self.sb_ano.setRange(1900, 2100)
        self.le_placa = QLineEdit()
        self.sb_km = QSpinBox()
        self.sb_km.setRange(0, 999999)
        self.le_cor = QLineEdit()
        
        layout.addRow("Marca:", self.le_marca)
        layout.addRow("Modelo:", self.le_modelo)
        layout.addRow("Ano:", self.sb_ano)
        layout.addRow("Placa:", self.le_placa)
        layout.addRow("KM:", self.sb_km)
        layout.addRow("Cor:", self.le_cor)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(lambda: self.salvar_veiculo(dialog))
        buttons.rejected.connect(dialog.reject)
        
        layout.addWidget(buttons)
        dialog.setLayout(layout)
        dialog.exec_()
    
    def salvar_veiculo(self, dialog):
        cliente_id = self.cb_clientes.currentData()
        if cliente_id == 0:
            QMessageBox.warning(self, "Aviso", "Selecione um cliente antes de cadastrar o veículo")
            return
        
        conn = sqlite3.connect('sistema_os.db')
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
            INSERT INTO veiculos (cliente_id, marca, modelo, ano, placa, km, cor)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                cliente_id,
                self.le_marca.text(),
                self.le_modelo.text(),
                self.sb_ano.value(),
                self.le_placa.text(),
                self.sb_km.value(),
                self.le_cor.text()
            ))
            conn.commit()
            self.carregar_dados()
            dialog.accept()
        except sqlite3.Error as e:
            QMessageBox.warning(self, "Erro", f"Erro ao salvar veículo:\n{str(e)}")
        finally:
            conn.close()
    
    def editar_veiculo(self):
        selected = self.tabela.selectionModel().selectedRows()
        if not selected:
            QMessageBox.warning(self, "Aviso", "Selecione um veículo para editar")
            return
        
        # A edição é feita diretamente na tabela
    
    def excluir_veiculo(self):
        selected = self.tabela.selectionModel().selectedRows()
        if not selected:
            QMessageBox.warning(self, "Aviso", "Selecione um veículo para excluir")
            return
        
        reply = QMessageBox.question(
            self, 'Confirmar',
            'Tem certeza que deseja excluir este veículo?',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            model = self.tabela.model()
            for index in selected:
                model.removeRow(index.row())
            model.submitAll()
            self.carregar_dados()