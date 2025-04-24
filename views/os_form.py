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
        
        # Campos de datas
        self.de_data_abertura = QDateEdit(QDate.currentDate())
        self.de_data_abertura.setCalendarPopup(True)
        form_layout.addRow("Data de Abertura:", self.de_data_abertura)
        
        self.de_data_entrega = QDateEdit(QDate.currentDate())
        self.de_data_entrega.setCalendarPopup(True)
        form_layout.addRow("Data de Entrega:", self.de_data_entrega)
        
        # Demais campos
        self.te_descricao = QTextEdit()
        form_layout.addRow("Descrição:", self.te_descricao)
        
        self.te_servicos = QTextEdit()
        form_layout.addRow("Serviços Realizados:", self.te_servicos)
        
        self.te_pecas = QTextEdit()
        form_layout.addRow("Peças Utilizadas:", self.te_pecas)
        
        self.sb_valor = QDoubleSpinBox()
        self.sb_valor.setMaximum(100000)
        self.sb_valor.setPrefix("R$ ")
        self.sb_valor.setDecimals(2)
        form_layout.addRow("Valor Total:", self.sb_valor)
        
        self.cb_status = QComboBox()
        self.cb_status.addItems(["Aberta", "Em Andamento", "Concluída", "Cancelada"])
        form_layout.addRow("Status:", self.cb_status)
        
        self.te_observacoes = QTextEdit()
        form_layout.addRow("Observações:", self.te_observacoes)
        
        # Botão de salvar
        self.btn_salvar = QPushButton("Salvar")
        self.btn_salvar.clicked.connect(self.salvar_os)
        form_layout.addRow(self.btn_salvar)
        
        layout.addLayout(form_layout)
        self.setLayout(layout)
        
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
                    self.carregar_veiculos()
                    
                    veiculo_idx = self.cb_veiculo.findData(os_data[1])
                    if veiculo_idx >= 0:
                        self.cb_veiculo.setCurrentIndex(veiculo_idx)
                
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
    
    def salvar_os(self):
        cliente_id = self.cb_cliente.currentData()
        veiculo_id = self.cb_veiculo.currentData()
        data_abertura = self.de_data_abertura.date().toString("yyyy-MM-dd HH:mm:ss")
        data_entrega = self.de_data_entrega.date().toString("yyyy-MM-dd")
        descricao = self.te_descricao.toPlainText()
        servicos = self.te_servicos.toPlainText()
        pecas = self.te_pecas.toPlainText()
        valor = self.sb_valor.value()
        status = self.cb_status.currentText()
        observacoes = self.te_observacoes.toPlainText()
        
        try:
            conn = sqlite3.connect('sistema_os.db')
            cursor = conn.cursor()
            
            if self.os_id:
                cursor.execute('''
                    UPDATE ordens_servico SET
                        veiculo_id=?, data_abertura=?, data_entrega=?, descricao=?,
                        servicos=?, pecas=?, valor_total=?, status=?, observacoes=?
                    WHERE id=?
                ''', (veiculo_id, data_abertura, data_entrega, descricao, servicos, pecas, valor, status, observacoes, self.os_id))
            else:
                cursor.execute('''
                    INSERT INTO ordens_servico (
                        veiculo_id, data_abertura, data_entrega, descricao,
                        servicos, pecas, valor_total, status, observacoes
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (veiculo_id, data_abertura, data_entrega, descricao, servicos, pecas, valor, status, observacoes))
            
            conn.commit()
            self.os_salva.emit()
            self.close()
        except sqlite3.Error as e:
            QMessageBox.warning(self, "Erro", f"Erro ao salvar OS:\n{str(e)}")
        finally:
            if conn:
                conn.close()
    