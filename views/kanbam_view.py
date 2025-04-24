from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QGroupBox,
    QListWidget, QLabel, QListWidgetItem, QAbstractItemView,
    QFrame
)
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QFont, QColor
import sqlite3

class KanbanCard(QWidget):
    def __init__(self, os_id, cliente, veiculo, valor):
        super().__init__()
        self.setup_ui(os_id, cliente, veiculo, valor)
        
    def setup_ui(self, os_id, cliente, veiculo, valor):
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)
        
        # Header
        lbl_id = QLabel(f"<b>OS #{os_id}</b>")
        lbl_id.setStyleSheet("color: #2c3e50; font-size: 12px;")
        
        # Cliente
        lbl_cliente = QLabel(cliente)
        lbl_cliente.setStyleSheet("color: #34495e; font-size: 11px;")
        
        # Veículo
        lbl_veiculo = QLabel(veiculo)
        lbl_veiculo.setStyleSheet("color: #7f8c8d; font-size: 10px;")
        
        # Valor
        valor_formatado = f"{valor:,.2f}" if valor else "0,00"
        lbl_valor = QLabel(f"<b>R$ {valor_formatado}</b>")
        if valor and valor > 5000:
            lbl_valor.setStyleSheet("color: #e74c3c; font-size: 12px;")
        else:
            lbl_valor.setStyleSheet("color: #27ae60; font-size: 12px;")
        
        layout.addWidget(lbl_id)
        layout.addWidget(lbl_cliente)
        layout.addWidget(lbl_veiculo)
        layout.addWidget(lbl_valor)
        
        self.setLayout(layout)
        self.setStyleSheet("""
            background-color: white;
            border-radius: 8px;
            border: 1px solid #dfe6e9;
        """)

class KanbanView(QWidget):
    atualizado = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.load_kanban_data()
    
    def setup_ui(self):
        self.layout_principal = QHBoxLayout()
        self.layout_principal.setContentsMargins(15, 15, 15, 15)
        self.layout_principal.setSpacing(20)
        
        # Configuração das colunas
        colunas = [
            ("Aberto", "#3498db"),
            ("Em Andamento", "#f39c12"),
            ("Concluído", "#2ecc71"),
            ("Entregue", "#9b59b6")
        ]
        
        for titulo, cor in colunas:
            coluna = self.criar_coluna(titulo, cor)
            self.layout_principal.addWidget(coluna)
        
        self.setLayout(self.layout_principal)
    
    def criar_coluna(self, titulo, cor):
        group_box = QGroupBox(titulo)
        group_box.setStyleSheet(f"""
            QGroupBox {{
                font-weight: bold;
                color: {cor};
                font-size: 14px;
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(8, 25, 8, 8)
        layout.setSpacing(10)
        
        # Frame do contador
        frame_contador = QFrame()
        frame_contador.setStyleSheet("background-color: #f8f9fa; border-radius: 4px;")
        layout_contador = QHBoxLayout()
        layout_contador.setContentsMargins(8, 4, 8, 4)
        
        lbl_total = QLabel("Total:")
        lbl_total.setStyleSheet("color: #7f8c8d;")
        
        total_widget = QLabel("R$ 0,00")
        total_widget.setStyleSheet("font-weight: bold; color: #2c3e50;")
        total_widget.setObjectName(f"lbl_total_{titulo.lower().replace(' ', '_')}")
        
        layout_contador.addWidget(lbl_total)
        layout_contador.addStretch()
        layout_contador.addWidget(total_widget)
        frame_contador.setLayout(layout_contador)
        
        # Lista de itens
        list_widget = QListWidget()
        list_widget.setDragDropMode(QAbstractItemView.DragDrop)
        list_widget.setStyleSheet("""
            QListWidget {
                background-color: transparent;
                border: none;
            }
            QListWidget::item {
                background-color: white;
                border-radius: 8px;
                margin: 6px 0;
                border: 1px solid #dfe6e9;
            }
            QListWidget::item:hover {
                border: 1px solid #3498db;
                background-color: #f1f9ff;
            }
        """)
        list_widget.setObjectName(f"lw_{titulo.lower().replace(' ', '_')}")
        
        layout.addWidget(frame_contador)
        layout.addWidget(list_widget)
        group_box.setLayout(layout)
        
        return group_box

    def load_kanban_data(self):
        conn = None
        try:
            conn = sqlite3.connect('sistema_os.db')
            cursor = conn.cursor()
            
            # Consulta para obter todas as OS com status e informações relevantes
            cursor.execute('''
            SELECT os.id, c.nome, v.marca || ' ' || v.modelo, os.valor_total, os.status
            FROM ordens_servico os
            JOIN veiculos v ON os.veiculo_id = v.id
            JOIN clientes c ON v.cliente_id = c.id
            ORDER BY os.data_abertura DESC
            ''')
            
            ordens = cursor.fetchall()
            
            # Limpa todas as listas primeiro
            for status in ["aberto", "em_andamento", "concluído", "entregue"]:
                list_widget = self.findChild(QListWidget, f"lw_{status}")
                if list_widget:
                    list_widget.clear()
                total_label = self.findChild(QLabel, f"lbl_total_{status}")
                if total_label:
                    total_label.setText("R$ 0,00")
            
            # Dicionário para acumular os totais por status
            totais = {
                "Aberto": 0.0,
                "Em Andamento": 0.0,
                "Concluída": 0.0,
                "Concluído": 0.0,
                "Entregue": 0.0,
                "Cancelada": 0.0
            }
            
            # Adiciona cada OS na coluna correspondente
            for os_id, cliente, veiculo, valor, status in ordens:
                # Normaliza o status (remove acentos e coloca em minúsculo para comparação)
                status_normalizado = status.lower().replace("ê", "e").replace("í", "i")
                
                # Mapeia os status do banco para os status do Kanban
                kanban_status = {
                    "aberta": "aberto",
                    "aberto": "aberto",
                    "em andamento": "em_andamento",
                    "concluída": "concluído",
                    "concluido": "concluído",
                    "entregue": "entregue",
                    "cancelada": "concluído"
                }.get(status_normalizado, "aberto")
                
                # Adiciona ao total do status
                if status in totais:
                    totais[status] += valor if valor else 0
                else:
                    # Se o status não existir no dicionário, adiciona ao "aberto"
                    totais["Aberto"] += valor if valor else 0
                
                # Encontra a QListWidget correspondente
                list_widget = self.findChild(QListWidget, f"lw_{kanban_status}")
                if list_widget:
                    # Cria o card da OS
                    card = KanbanCard(os_id, cliente, veiculo, valor)
                    
                    # Cria um item para a lista
                    item = QListWidgetItem()
                    item.setSizeHint(QSize(200, 100))
                    
                    # Adiciona o item à lista
                    list_widget.addItem(item)
                    list_widget.setItemWidget(item, card)
            
            # Atualiza os totais em cada coluna
            for kanban_status in ["aberto", "em_andamento", "concluído", "entregue"]:
                total_label = self.findChild(QLabel, f"lbl_total_{kanban_status}")
                if total_label:
                    # Soma todos os status que mapeiam para esta coluna
                    total = 0.0
                    if kanban_status == "aberto":
                        total = totais.get("Aberto", 0.0) + totais.get("Aberta", 0.0)
                    elif kanban_status == "em_andamento":
                        total = totais.get("Em Andamento", 0.0)
                    elif kanban_status == "concluído":
                        total = totais.get("Concluída", 0.0) + totais.get("Concluído", 0.0) + totais.get("Cancelada", 0.0)
                    elif kanban_status == "entregue":
                        total = totais.get("Entregue", 0.0)
                    
                    total_label.setText(f"R$ {total:,.2f}")
        
        except sqlite3.Error as e:
            print(f"Erro ao carregar dados do Kanban: {str(e)}")
        finally:
            if conn:
                conn.close()