from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QTableView, QPushButton, 
                            QHeaderView, QMessageBox, QHBoxLayout, QFrame, 
                            QLabel, QDialog, QFormLayout, QLineEdit, 
                            QDialogButtonBox)
from PyQt5.QtSql import QSqlTableModel, QSqlDatabase
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
import qtawesome as qta
import sqlite3

class ClientesView(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        
        # Cabeçalho
        header = QFrame()
        header_layout = QHBoxLayout()
        
        lbl_title = QLabel("Clientes")
        lbl_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50;")
        
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        # Botões com ícones
        btn_novo = QPushButton(qta.icon("fa5s.plus"), "Novo Cliente")
        btn_novo.clicked.connect(self.novo_cliente)
        
        btn_editar = QPushButton(qta.icon("fa5s.edit"), "Editar")
        btn_editar.clicked.connect(self.editar_cliente)
        
        btn_excluir = QPushButton(qta.icon("fa5s.trash"), "Excluir")
        btn_excluir.clicked.connect(self.excluir_cliente)
        
        btn_layout.addWidget(btn_novo)
        btn_layout.addWidget(btn_editar)
        btn_layout.addWidget(btn_excluir)
        
        header_layout.addWidget(lbl_title)
        header_layout.addStretch()
        header_layout.addLayout(btn_layout)
        header.setLayout(header_layout)
        
        # Tabela
        self.tabela = QTableView()
        self.tabela.setSelectionBehavior(QTableView.SelectRows)
        self.tabela.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabela.verticalHeader().setVisible(False)
        self.carregar_dados()
        
        layout.addWidget(header)
        layout.addWidget(self.tabela)
        self.setLayout(layout)
    
    def carregar_dados(self):
        db = QSqlDatabase.addDatabase("QSQLITE")
        db.setDatabaseName("sistema_os.db")
        
        if not db.open():
            QMessageBox.critical(self, "Erro", "Não foi possível abrir o banco de dados")
            return
        
        self.model = QSqlTableModel()
        self.model.setTable("clientes")
        self.model.select()
        self.model.setEditStrategy(QSqlTableModel.OnFieldChange)
        
        self.tabela.setModel(self.model)
    
    def novo_cliente(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Novo Cliente")
        dialog.setWindowIcon(qta.icon("fa5s.user-plus"))
        
        layout = QFormLayout()
        
        self.le_nome = QLineEdit()
        self.le_cpf = QLineEdit()
        self.le_telefone = QLineEdit()
        self.le_email = QLineEdit()
        self.le_endereco = QLineEdit()
        
        layout.addRow("Nome:", self.le_nome)
        layout.addRow("CPF:", self.le_cpf)
        layout.addRow("Telefone:", self.le_telefone)
        layout.addRow("Email:", self.le_email)
        layout.addRow("Endereço:", self.le_endereco)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(lambda: self.salvar_cliente(dialog))
        buttons.rejected.connect(dialog.reject)
        
        layout.addWidget(buttons)
        dialog.setLayout(layout)
        dialog.exec_()
    
    def salvar_cliente(self, dialog):
        # Validação básica
        if not self.le_nome.text():
            QMessageBox.warning(self, "Aviso", "O nome é obrigatório")
            return
            
        conn = sqlite3.connect('sistema_os.db')
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
            INSERT INTO clientes (nome, cpf, telefone, email, endereco)
            VALUES (?, ?, ?, ?, ?)
            ''', (
                self.le_nome.text(),
                self.le_cpf.text(),
                self.le_telefone.text(),
                self.le_email.text(),
                self.le_endereco.text()
            ))
            conn.commit()
            self.carregar_dados()  # Recarrega os dados
            dialog.accept()
        except sqlite3.Error as e:
            QMessageBox.warning(self, "Erro", f"Erro ao salvar cliente:\n{str(e)}")
        finally:
            conn.close()
    
    def editar_cliente(self):
        selected = self.tabela.selectionModel().selectedRows()
        if not selected:
            QMessageBox.warning(self, "Aviso", "Selecione um cliente para editar")
            return
        
        # A edição é feita diretamente na tabela graças ao QSqlTableModel
        QMessageBox.information(self, "Editar", "Clique duas vezes na célula que deseja editar")
    
    def excluir_cliente(self):
        selected = self.tabela.selectionModel().selectedRows()
        if not selected:
            QMessageBox.warning(self, "Aviso", "Selecione um cliente para excluir")
            return
        
        reply = QMessageBox.question(
            self, 'Confirmar',
            'Tem certeza que deseja excluir este cliente e todos seus veículos?',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            model = self.tabela.model()
            for index in selected:
                model.removeRow(index.row())
            model.submitAll()
            self.carregar_dados()