from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QGroupBox, 
                            QListWidget, QLabel, QListWidgetItem)
from PyQt5.QtCore import Qt, pyqtSignal
import sqlite3

class KanbanView(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.load_kanban_data()
    
    def setup_ui(self):
        layout = QHBoxLayout()
        
        # Coluna "Aberto"
        self.gb_aberto = QGroupBox("Aberto")
        layout_aberto = QVBoxLayout()
        self.lw_aberto = QListWidget()
        self.lw_aberto.setDragDropMode(QListWidget.DragDrop)
        layout_aberto.addWidget(self.lw_aberto)
        self.gb_aberto.setLayout(layout_aberto)
        layout.addWidget(self.gb_aberto)
        
        # Coluna "Em Andamento"
        self.gb_andamento = QGroupBox("Em Andamento")
        layout_andamento = QVBoxLayout()
        self.lw_andamento = QListWidget()
        self.lw_andamento.setDragDropMode(QListWidget.DragDrop)
        layout_andamento.addWidget(self.lw_andamento)
        self.gb_andamento.setLayout(layout_andamento)
        layout.addWidget(self.gb_andamento)
        
        # Coluna "Concluído"
        self.gb_concluido = QGroupBox("Concluído")
        layout_concluido = QVBoxLayout()
        self.lw_concluido = QListWidget()
        self.lw_concluido.setDragDropMode(QListWidget.DragDrop)
        layout_concluido.addWidget(self.lw_concluido)
        self.gb_concluido.setLayout(layout_concluido)
        layout.addWidget(self.gb_concluido)
        
        # Coluna "Entregue"
        self.gb_entregue = QGroupBox("Entregue")
        layout_entregue = QVBoxLayout()
        self.lw_entregue = QListWidget()
        self.lw_entregue.setDragDropMode(QListWidget.DragDrop)
        layout_entregue.addWidget(self.lw_entregue)
        self.gb_entregue.setLayout(layout_entregue)
        layout.addWidget(self.gb_entregue)
        
        self.setLayout(layout)
        
        # Conectar eventos de mudança
        self.lw_aberto.model().rowsMoved.connect(lambda: self.atualizar_status('Aberto', self.lw_aberto))
        self.lw_andamento.model().rowsMoved.connect(lambda: self.atualizar_status('Em Andamento', self.lw_andamento))
        self.lw_concluido.model().rowsMoved.connect(lambda: self.atualizar_status('Concluído', self.lw_concluido))
        self.lw_entregue.model().rowsMoved.connect(lambda: self.atualizar_status('Entregue', self.lw_entregue))
    
    def load_kanban_data(self):
        conn = sqlite3.connect('sistema_os.db')
        cursor = conn.cursor()
        
        # Limpa as listas
        self.lw_aberto.clear()
        self.lw_andamento.clear()
        self.lw_concluido.clear()
        self.lw_entregue.clear()
        
        # Busca todas as OS
        cursor.execute('''
        SELECT os.id, os.status, c.nome, v.marca || ' ' || v.modelo, os.valor_total
        FROM ordens_servico os
        JOIN veiculos v ON os.veiculo_id = v.id
        JOIN clientes c ON v.cliente_id = c.id
        ORDER BY os.data_abertura
        ''')
        
        for os_data in cursor.fetchall():
            os_id, status, cliente, veiculo, valor = os_data
            
            item = QListWidgetItem()
            widget = QWidget()
            layout = QVBoxLayout()
            
            lbl_id = QLabel(f"OS: {os_id}")
            lbl_cliente = QLabel(f"Cliente: {cliente}")
            lbl_veiculo = QLabel(f"Veículo: {veiculo}")
            lbl_valor = QLabel(f"Valor: R$ {valor:.2f}")
            
            for lbl in [lbl_id, lbl_cliente, lbl_veiculo, lbl_valor]:
                lbl.setAlignment(Qt.AlignCenter)
                layout.addWidget(lbl)
            
            widget.setLayout(layout)
            item.setSizeHint(widget.sizeHint())
            
            if status == 'Aberto':
                self.lw_aberto.addItem(item)
                self.lw_aberto.setItemWidget(item, widget)
            elif status == 'Em Andamento':
                self.lw_andamento.addItem(item)
                self.lw_andamento.setItemWidget(item, widget)
            elif status == 'Concluído':
                self.lw_concluido.addItem(item)
                self.lw_concluido.setItemWidget(item, widget)
            elif status == 'Entregue':
                self.lw_entregue.addItem(item)
                self.lw_entregue.setItemWidget(item, widget)
        
        conn.close()
    
    def atualizar_status(self, novo_status, list_widget):
        conn = sqlite3.connect('sistema_os.db')
        cursor = conn.cursor()
        
        for i in range(list_widget.count()):
            item = list_widget.item(i)
            widget = list_widget.itemWidget(item)
            lbl_id = widget.findChild(QLabel)
            
            if lbl_id:
                os_id = lbl_id.text().split(": ")[1]
                cursor.execute("UPDATE ordens_servico SET status=? WHERE id=?", (novo_status, os_id))
        
        conn.commit()
        conn.close()