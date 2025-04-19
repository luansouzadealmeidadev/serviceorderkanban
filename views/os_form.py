from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QFormLayout, QLineEdit, 
                            QTextEdit, QComboBox, QDoubleSpinBox, QPushButton, 
                            QMessageBox, QDateEdit)
from PyQt5.QtCore import Qt, QDate, pyqtSignal
import sqlite3
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import os

class OSFormWindow(QWidget):
    os_salva = pyqtSignal()
    
    def __init__(self, os_id=None):
        super().__init__()
        self.os_id = os_id
        self.setWindowTitle("Nova Ordem de Serviço" if not os_id else "Editar Ordem de Serviço")
        self.setGeometry(200, 200, 600, 800)
        
        layout = QVBoxLayout()
        form_layout = QFormLayout()
        
        # Cliente e Veículo (apenas seleção)
        self.cb_cliente = QComboBox()
        self.carregar_clientes()
        form_layout.addRow("Cliente:", self.cb_cliente)
        
        self.cb_veiculo = QComboBox()
        self.cb_cliente.currentIndexChanged.connect(self.carregar_veiculos)
        form_layout.addRow("Veículo:", self.cb_veiculo)
        
        # Restante do formulário permanece igual...
        # ... (mantenha todo o resto do código original do OSFormWindow)
        
        if os_id:
            self.carregar_dados_os()
    
    def carregar_clientes(self):
        try:
            conn = sqlite3.connect('sistema_os.db')
            cursor = conn.cursor()
            cursor.execute("SELECT id, nome FROM clientes ORDER BY nome")
            clientes = cursor.fetchall()
            self.cb_cliente.clear()
            for cliente in clientes:
                self.cb_cliente.addItem(cliente[1], cliente[0])
        except sqlite3.Error as e:
            QMessageBox.warning(self, "Erro", f"Erro ao carregar clientes:\n{str(e)}")
        finally:
            if conn:
                conn.close()
    
    def carregar_veiculos(self):
        cliente_id = self.cb_cliente.currentData()
        if not cliente_id:
            return
            
        try:
            conn = sqlite3.connect('sistema_os.db')
            cursor = conn.cursor()
            cursor.execute("SELECT id, marca || ' ' || modelo FROM veiculos WHERE cliente_id = ?", (cliente_id,))
            veiculos = cursor.fetchall()
            self.cb_veiculo.clear()
            for veiculo in veiculos:
                self.cb_veiculo.addItem(veiculo[1], veiculo[0])
        except sqlite3.Error as e:
            QMessageBox.warning(self, "Erro", f"Erro ao carregar veículos:\n{str(e)}")
        finally:
            if conn:
                conn.close()
    
    def carregar_dados_os(self):
        try:
            conn = sqlite3.connect('sistema_os.db')
            cursor = conn.cursor()
            
            cursor.execute('''
            SELECT os.*, v.cliente_id, v.marca, v.modelo 
            FROM ordens_servico os
            JOIN veiculos v ON os.veiculo_id = v.id
            WHERE os.id = ?
            ''', (self.os_id,))
            
            os_data = cursor.fetchone()
            
            if os_data:
                # Encontra o índice do cliente
                cliente_idx = self.cb_cliente.findData(os_data[10])
                if cliente_idx >= 0:
                    self.cb_cliente.setCurrentIndex(cliente_idx)
                    # Força o carregamento dos veículos
                    self.carregar_veiculos()
                    
                    # Seleciona o veículo correto
                    veiculo_idx = self.cb_veiculo.findData(os_data[1])
                    if veiculo_idx >= 0:
                        self.cb_veiculo.setCurrentIndex(veiculo_idx)
                
                # Preenche os demais campos
                self.de_data_abertura.setDate(QDate.fromString(os_data[2], 'yyyy-MM-dd HH:mm:ss'))
                if os_data[3]:
                    self.de_data_entrega.setDate(QDate.fromString(os_data[3], 'yyyy-MM-dd'))
                self.te_descricao.setPlainText(os_data[4])
                self.te_servicos.setPlainText(os_data[5])
                self.te_pecas.setPlainText(os_data[6])
                self.sb_valor.setValue(os_data[7])
                self.cb_status.setCurrentText(os_data[8])
                self.te_observacoes.setPlainText(os_data[9] if os_data[9] else "")
        except sqlite3.Error as e:
            QMessageBox.warning(self, "Erro", f"Erro ao carregar OS:\n{str(e)}")
        finally:
            if conn:
                conn.close()
    
    # ... (mantenha todos os outros métodos originais do OSFormWindow)