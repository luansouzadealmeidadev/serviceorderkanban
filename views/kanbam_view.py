from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QGroupBox, 
                            QListWidget, QLabel, QListWidgetItem, QAbstractItemView,
                            QFrame)
from PyQt5.QtCore import Qt, pyqtSignal
import sqlite3

class KanbanView(QWidget):
    atualizado = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.load_kanban_data()
    
    def setup_ui(self):
        layout = QHBoxLayout()
        
        # Coluna "Aberto"
        self.gb_aberto = QGroupBox("Aberto")
        layout_aberto = QVBoxLayout()
        
        # Frame para o contador
        frame_aberto = QFrame()
        layout_frame_aberto = QHBoxLayout()
        self.lbl_total_aberto = QLabel("Total: R$ 0,00")
        layout_frame_aberto.addWidget(self.lbl_total_aberto)
        frame_aberto.setLayout(layout_frame_aberto)
        
        self.lw_aberto = QListWidget()
        self.lw_aberto.setDragDropMode(QAbstractItemView.DragDrop)
        
        layout_aberto.addWidget(frame_aberto)
        layout_aberto.addWidget(self.lw_aberto)
        self.gb_aberto.setLayout(layout_aberto)
        layout.addWidget(self.gb_aberto)
        
        # Coluna "Em Andamento"
        self.gb_andamento = QGroupBox("Em Andamento")
        layout_andamento = QVBoxLayout()
        
        frame_andamento = QFrame()
        layout_frame_andamento = QHBoxLayout()
        self.lbl_total_andamento = QLabel("Total: R$ 0,00")
        layout_frame_andamento.addWidget(self.lbl_total_andamento)
        frame_andamento.setLayout(layout_frame_andamento)
        
        self.lw_andamento = QListWidget()
        self.lw_andamento.setDragDropMode(QAbstractItemView.DragDrop)
        
        layout_andamento.addWidget(frame_andamento)
        layout_andamento.addWidget(self.lw_andamento)
        self.gb_andamento.setLayout(layout_andamento)
        layout.addWidget(self.gb_andamento)
        
        # Coluna "Concluído"
        self.gb_concluido = QGroupBox("Concluído")
        layout_concluido = QVBoxLayout()
        
        frame_concluido = QFrame()
        layout_frame_concluido = QHBoxLayout()
        self.lbl_total_concluido = QLabel("Total: R$ 0,00")
        layout_frame_concluido.addWidget(self.lbl_total_concluido)
        frame_concluido.setLayout(layout_frame_concluido)
        
        self.lw_concluido = QListWidget()
        self.lw_concluido.setDragDropMode(QAbstractItemView.DragDrop)
        
        layout_concluido.addWidget(frame_concluido)
        layout_concluido.addWidget(self.lw_concluido)
        self.gb_concluido.setLayout(layout_concluido)
        layout.addWidget(self.gb_concluido)
        
        # Coluna "Entregue"
        self.gb_entregue = QGroupBox("Entregue")
        layout_entregue = QVBoxLayout()
        
        frame_entregue = QFrame()
        layout_frame_entregue = QHBoxLayout()
        self.lbl_total_entregue = QLabel("Total: R$ 0,00")
        layout_frame_entregue.addWidget(self.lbl_total_entregue)
        frame_entregue.setLayout(layout_frame_entregue)
        
        self.lw_entregue = QListWidget()
        self.lw_entregue.setDragDropMode(QAbstractItemView.DragDrop)
        
        layout_entregue.addWidget(frame_entregue)
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
        
        # Dicionário para armazenar totais
        totais = {
            'Aberto': 0,
            'Em Andamento': 0,
            'Concluído': 0,
            'Entregue': 0
        }
        
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
            
            # Acumula o valor total por status
            if status in totais:
                totais[status] += valor
            
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
        
        # Atualiza os labels com os totais
        self.lbl_total_aberto.setText(f"Total: R$ {totais['Aberto']:,.2f}")
        self.lbl_total_andamento.setText(f"Total: R$ {totais['Em Andamento']:,.2f}")
        self.lbl_total_concluido.setText(f"Total: R$ {totais['Concluído']:,.2f}")
        self.lbl_total_entregue.setText(f"Total: R$ {totais['Entregue']:,.2f}")
        
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
        self.load_kanban_data()  # Recarrega os dados para atualizar os totais