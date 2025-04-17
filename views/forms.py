from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QFormLayout, QLineEdit, 
                            QPushButton, QMessageBox, QSpinBox)
import sqlite3
from PyQt5.QtCore import pyqtSignal
class ClienteFormWindow(QWidget):
    cliente_salvo = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        form_layout = QFormLayout()
        
        self.le_nome = QLineEdit()
        self.le_cpf = QLineEdit()
        self.le_telefone = QLineEdit()
        self.le_email = QLineEdit()
        self.le_endereco = QLineEdit()
        
        form_layout.addRow("Nome:", self.le_nome)
        form_layout.addRow("CPF:", self.le_cpf)
        form_layout.addRow("Telefone:", self.le_telefone)
        form_layout.addRow("Email:", self.le_email)
        form_layout.addRow("Endereço:", self.le_endereco)
        
        btn_salvar = QPushButton("Salvar")
        btn_salvar.clicked.connect(self.salvar_cliente)
        
        layout.addLayout(form_layout)
        layout.addWidget(btn_salvar)
        self.setLayout(layout)
    
    def salvar_cliente(self):
        # Validação básica
        if not self.le_nome.text():
            QMessageBox.warning(self, "Aviso", "O nome é obrigatório")
            return
            
        try:
            conn = sqlite3.connect('sistema_os.db')
            cursor = conn.cursor()
            
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
            QMessageBox.information(self, "Sucesso", "Cliente cadastrado com sucesso!")
            self.cliente_salvo.emit()
            self.close()
            
        except sqlite3.Error as e:
            QMessageBox.warning(self, "Erro", f"Erro ao salvar cliente:\n{str(e)}")
        finally:
            if conn:
                conn.close()

class VeiculoFormWindow(QWidget):
    veiculo_salvo = pyqtSignal()
    
    def __init__(self, cliente_id):
        super().__init__()
        self.cliente_id = cliente_id
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        form_layout = QFormLayout()
        
        self.le_marca = QLineEdit()
        self.le_modelo = QLineEdit()
        self.sb_ano = QSpinBox()
        self.sb_ano.setRange(1900, 2100)
        self.le_placa = QLineEdit()
        self.sb_km = QSpinBox()
        self.sb_km.setRange(0, 999999)
        self.le_cor = QLineEdit()
        
        form_layout.addRow("Marca:", self.le_marca)
        form_layout.addRow("Modelo:", self.le_modelo)
        form_layout.addRow("Ano:", self.sb_ano)
        form_layout.addRow("Placa:", self.le_placa)
        form_layout.addRow("KM:", self.sb_km)
        form_layout.addRow("Cor:", self.le_cor)
        
        btn_salvar = QPushButton("Salvar")
        btn_salvar.clicked.connect(self.salvar_veiculo)
        
        layout.addLayout(form_layout)
        layout.addWidget(btn_salvar)
        self.setLayout(layout)
    
    def salvar_veiculo(self):
        # Validação básica
        if not self.le_marca.text() or not self.le_modelo.text():
            QMessageBox.warning(self, "Aviso", "Marca e modelo são obrigatórios")
            return
            
        try:
            conn = sqlite3.connect('sistema_os.db')
            cursor = conn.cursor()
            
            cursor.execute('''
            INSERT INTO veiculos (cliente_id, marca, modelo, ano, placa, km, cor)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                self.cliente_id,
                self.le_marca.text(),
                self.le_modelo.text(),
                self.sb_ano.value(),
                self.le_placa.text(),
                self.sb_km.value(),
                self.le_cor.text()
            ))
            
            conn.commit()
            QMessageBox.information(self, "Sucesso", "Veículo cadastrado com sucesso!")
            self.veiculo_salvo.emit()
            self.close()
            
        except sqlite3.Error as e:
            QMessageBox.warning(self, "Erro", f"Erro ao salvar veículo:\n{str(e)}")
        finally:
            if conn:
                conn.close()