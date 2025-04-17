from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QFormLayout, QLineEdit, 
                            QTextEdit, QComboBox, QDoubleSpinBox, QPushButton, 
                            QMessageBox, QDateEdit, QSpinBox, QHBoxLayout)
from PyQt5.QtCore import Qt, QDate, pyqtSignal
import sqlite3
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import os

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

class OSFormWindow(QWidget):
    os_salva = pyqtSignal()
    
    def __init__(self, os_id=None):
        super().__init__()
        self.os_id = os_id
        self.setWindowTitle("Nova Ordem de Serviço" if not os_id else "Editar Ordem de Serviço")
        self.setGeometry(200, 200, 600, 800)
        
        layout = QVBoxLayout()
        form_layout = QFormLayout()
        
        # Seção Cliente/Veículo
        self.cb_cliente = QComboBox()
        self.carregar_clientes()
        
        btn_novo_cliente = QPushButton("Novo Cliente")
        btn_novo_cliente.clicked.connect(self.abrir_form_cliente)
        
        hbox_cliente = QHBoxLayout()
        hbox_cliente.addWidget(self.cb_cliente)
        hbox_cliente.addWidget(btn_novo_cliente)
        form_layout.addRow("Cliente:", hbox_cliente)
        
        self.cb_veiculo = QComboBox()
        self.cb_cliente.currentIndexChanged.connect(self.carregar_veiculos)
        
        btn_novo_veiculo = QPushButton("Novo Veículo")
        btn_novo_veiculo.clicked.connect(self.abrir_form_veiculo)
        
        hbox_veiculo = QHBoxLayout()
        hbox_veiculo.addWidget(self.cb_veiculo)
        hbox_veiculo.addWidget(btn_novo_veiculo)
        form_layout.addRow("Veículo:", hbox_veiculo)
        
        # Datas
        self.de_data_abertura = QDateEdit(QDate.currentDate())
        self.de_data_abertura.setCalendarPopup(True)
        form_layout.addRow("Data Abertura:", self.de_data_abertura)
        
        self.de_data_entrega = QDateEdit()
        self.de_data_entrega.setCalendarPopup(True)
        form_layout.addRow("Data Entrega:", self.de_data_entrega)
        
        # Descrição do Problema
        self.te_descricao = QTextEdit()
        form_layout.addRow("Descrição do Problema:", self.te_descricao)
        
        # Serviços e Peças
        self.te_servicos = QTextEdit()
        form_layout.addRow("Serviços Realizados:", self.te_servicos)
        
        self.te_pecas = QTextEdit()
        form_layout.addRow("Peças Trocadas:", self.te_pecas)
        
        # Valor e Status
        self.sb_valor = QDoubleSpinBox()
        self.sb_valor.setPrefix("R$ ")
        self.sb_valor.setMaximum(99999.99)
        form_layout.addRow("Valor Total:", self.sb_valor)
        
        self.cb_status = QComboBox()
        self.cb_status.addItems(["Aberto", "Em Andamento", "Concluído", "Entregue"])
        form_layout.addRow("Status:", self.cb_status)
        
        # Observações
        self.te_observacoes = QTextEdit()
        form_layout.addRow("Observações:", self.te_observacoes)
        
        # Botões
        btn_salvar = QPushButton("Salvar")
        btn_salvar.clicked.connect(self.salvar_os)
        
        btn_gerar_pdf = QPushButton("Gerar PDF")
        btn_gerar_pdf.clicked.connect(self.gerar_pdf)
        
        layout.addLayout(form_layout)
        layout.addWidget(btn_salvar)
        layout.addWidget(btn_gerar_pdf)
        
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
    
    def abrir_form_cliente(self):
        self.form_cliente = ClienteFormWindow()
        self.form_cliente.cliente_salvo.connect(self.carregar_clientes)
        self.form_cliente.show()
    
    def abrir_form_veiculo(self):
        cliente_id = self.cb_cliente.currentData()
        if not cliente_id:
            QMessageBox.warning(self, "Aviso", "Selecione um cliente primeiro")
            return
            
        self.form_veiculo = VeiculoFormWindow(cliente_id)
        self.form_veiculo.veiculo_salvo.connect(self.carregar_veiculos)
        self.form_veiculo.show()
    
    def carregar_dados_os(self):
        try:
            conn = sqlite3.connect('sistema_os.db')
            cursor = conn.cursor()
            
            cursor.execute('''
            SELECT os.*, v.cliente_id 
            FROM ordens_servico os
            JOIN veiculos v ON os.veiculo_id = v.id
            WHERE os.id = ?
            ''', (self.os_id,))
            
            os_data = cursor.fetchone()
            
            if os_data:
                cliente_idx = self.cb_cliente.findData(os_data[10])
                if cliente_idx >= 0:
                    self.cb_cliente.setCurrentIndex(cliente_idx)
                
                self.cb_veiculo.currentIndexChanged.connect(
                    lambda: self.preencher_veiculo(os_data[1]))
                
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
    
    def preencher_veiculo(self, veiculo_id):
        veiculo_idx = self.cb_veiculo.findData(veiculo_id)
        if veiculo_idx >= 0:
            self.cb_veiculo.setCurrentIndex(veiculo_idx)
        self.cb_veiculo.currentIndexChanged.disconnect()
    
    def salvar_os(self):
        if not self.cb_veiculo.currentData():
            QMessageBox.warning(self, "Aviso", "Selecione um veículo válido.")
            return
            
        try:
            conn = sqlite3.connect('sistema_os.db')
            cursor = conn.cursor()
            
            os_data = (
                self.cb_veiculo.currentData(),
                self.de_data_abertura.date().toString('yyyy-MM-dd HH:mm:ss'),
                self.de_data_entrega.date().toString('yyyy-MM-dd') if self.de_data_entrega.date().isValid() else None,
                self.te_descricao.toPlainText(),
                self.te_servicos.toPlainText(),
                self.te_pecas.toPlainText(),
                self.sb_valor.value(),
                self.cb_status.currentText(),
                self.te_observacoes.toPlainText()
            )
            
            if self.os_id:
                cursor.execute('''
                UPDATE ordens_servico 
                SET veiculo_id=?, data_abertura=?, data_entrega=?, descricao_problema=?, 
                    servicos_realizados=?, pecas_trocadas=?, valor_total=?, status=?, observacoes=?
                WHERE id=?
                ''', os_data + (self.os_id,))
            else:
                cursor.execute('''
                INSERT INTO ordens_servico 
                (veiculo_id, data_abertura, data_entrega, descricao_problema, 
                 servicos_realizados, pecas_trocadas, valor_total, status, observacoes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', os_data)
            
            conn.commit()
            self.os_salva.emit()
            QMessageBox.information(self, "Sucesso", "Ordem de serviço salva com sucesso!")
            self.close()
        except sqlite3.Error as e:
            QMessageBox.warning(self, "Erro", f"Erro ao salvar OS:\n{str(e)}")
        finally:
            if conn:
                conn.close()
    
    def gerar_pdf(self):
        if not self.os_id:
            QMessageBox.warning(self, "Aviso", "Salve a OS antes de gerar o PDF.")
            return
            
        if not os.path.exists('generated_pdfs'):
            os.makedirs('generated_pdfs')
        
        pdf_path = f'generated_pdfs/os_{self.os_id}.pdf'
        c = canvas.Canvas(pdf_path, pagesize=A4)
        width, height = A4
        
        # Cabeçalho
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, height - 50, "ORDEM DE SERVIÇO")
        c.setFont("Helvetica", 12)
        c.drawString(width - 150, height - 50, f"Nº {self.os_id}")
        c.line(50, height - 70, width - 50, height - 70)
        
        # Dados do Cliente e Veículo
        y_position = height - 100
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y_position, "DADOS DO CLIENTE")
        c.setFont("Helvetica", 10)
        
        try:
            conn = sqlite3.connect('sistema_os.db')
            cursor = conn.cursor()
            
            cursor.execute('''
            SELECT c.nome, c.cpf, c.telefone, c.email, c.endereco,
                   v.marca, v.modelo, v.ano, v.placa, v.km, v.cor
            FROM ordens_servico os
            JOIN veiculos v ON os.veiculo_id = v.id
            JOIN clientes c ON v.cliente_id = c.id
            WHERE os.id = ?
            ''', (self.os_id,))
            
            dados = cursor.fetchone()
            
            if dados:
                y_position -= 20
                c.drawString(50, y_position, f"Nome: {dados[0]}")
                c.drawString(300, y_position, f"CPF: {dados[1]}")
                
                y_position -= 15
                c.drawString(50, y_position, f"Telefone: {dados[2]}")
                c.drawString(300, y_position, f"Email: {dados[3]}")
                
                y_position -= 15
                c.drawString(50, y_position, f"Endereço: {dados[4]}")
                
                y_position -= 30
                c.setFont("Helvetica-Bold", 12)
                c.drawString(50, y_position, "DADOS DO VEÍCULO")
                c.setFont("Helvetica", 10)
                
                y_position -= 20
                c.drawString(50, y_position, f"Marca/Modelo: {dados[5]} {dados[6]}")
                c.drawString(300, y_position, f"Ano: {dados[7]}")
                
                y_position -= 15
                c.drawString(50, y_position, f"Placa: {dados[8]}")
                c.drawString(300, y_position, f"KM: {dados[9]}")
                
                y_position -= 15
                c.drawString(50, y_position, f"Cor: {dados[10]}")
        except sqlite3.Error as e:
            QMessageBox.warning(self, "Erro", f"Erro ao gerar PDF:\n{str(e)}")
        finally:
            if conn:
                conn.close()
        
        # Serviços
        y_position -= 30
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y_position, "DESCRIÇÃO DO SERVIÇO")
        c.setFont("Helvetica", 10)
        
        descricao = self.te_descricao.toPlainText()
        for linha in descricao.split('\n'):
            y_position -= 15
            if y_position < 100:
                c.showPage()
                y_position = height - 50
            c.drawString(50, y_position, linha)
        
        # Serviços Realizados
        y_position -= 30
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y_position, "SERVIÇOS REALIZADOS")
        c.setFont("Helvetica", 10)
        
        servicos = self.te_servicos.toPlainText()
        for linha in servicos.split('\n'):
            y_position -= 15
            if y_position < 100:
                c.showPage()
                y_position = height - 50
            c.drawString(50, y_position, linha)
        
        # Peças Trocadas
        y_position -= 30
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y_position, "PEÇAS TROCADAS")
        c.setFont("Helvetica", 10)
        
        pecas = self.te_pecas.toPlainText()
        for linha in pecas.split('\n'):
            y_position -= 15
            if y_position < 100:
                c.showPage()
                y_position = height - 50
            c.drawString(50, y_position, linha)
        
        # Valor e Assinatura
        y_position -= 50
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y_position, f"VALOR TOTAL: R$ {self.sb_valor.value():.2f}")
        
        y_position -= 50
        c.line(100, y_position, 250, y_position)
        c.drawString(100, y_position - 15, "Assinatura do Cliente")
        
        c.line(width - 250, y_position, width - 100, y_position)
        c.drawString(width - 250, y_position - 15, "Assinatura do Responsável")
        
        c.save()
        QMessageBox.information(self, "PDF Gerado", f"Ordem de serviço salva como:\n{pdf_path}")