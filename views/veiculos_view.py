import requests
import sqlite3
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QTableView, QPushButton, 
                             QHeaderView, QMessageBox, QHBoxLayout, QComboBox, 
                             QDialog, QFormLayout, QSpinBox, QDialogButtonBox, QLabel)
from PyQt5.QtSql import QSqlTableModel, QSqlDatabase
from PyQt5.QtCore import Qt

class VeiculosView(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        self.cb_clientes = QComboBox()
        self.carregar_clientes()
        self.cb_clientes.currentIndexChanged.connect(self.filtrar_veiculos)

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

        if cliente_id == 0:
            self.model.setFilter("")
        else:
            self.model.setFilter(f"cliente_id = {cliente_id}")

        self.model.select()

    def novo_veiculo(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Novo Veículo")

        layout = QFormLayout()

        self.cb_marca = QComboBox()
        self.cb_modelo = QComboBox()
        self.sb_ano = QSpinBox()
        self.sb_ano.setRange(1900, 2100)
        self.le_placa = QComboBox()
        self.sb_km = QSpinBox()
        self.sb_km.setRange(0, 999999)
        self.le_cor = QComboBox()

        layout.addRow("Marca:", self.cb_marca)
        layout.addRow("Modelo:", self.cb_modelo)
        layout.addRow("Ano:", self.sb_ano)
        layout.addRow("Placa:", self.le_placa)
        layout.addRow("KM:", self.sb_km)
        layout.addRow("Cor:", self.le_cor)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(lambda: self.salvar_veiculo(dialog))
        buttons.rejected.connect(dialog.reject)

        layout.addWidget(buttons)
        dialog.setLayout(layout)

        self.carregar_marcas()
        self.cb_marca.currentIndexChanged.connect(self.carregar_modelos)

        dialog.exec_()

    def carregar_marcas(self):
        try:
            response = requests.get("https://parallelum.com.br/fipe/api/v1/carros/marcas")
            response.raise_for_status()
            marcas = response.json()

            self.cb_marca.clear()
            self.marcas_ids = {}

            for marca in marcas:
                self.cb_marca.addItem(marca['nome'])
                self.marcas_ids[marca['nome']] = marca['codigo']
        except Exception as e:
            QMessageBox.warning(self, "Erro", f"Erro ao buscar marcas: {e}")

    def carregar_modelos(self):
        marca_nome = self.cb_marca.currentText()
        marca_codigo = self.marcas_ids.get(marca_nome)

        if not marca_codigo:
            return

        try:
            response = requests.get(f"https://parallelum.com.br/fipe/api/v1/carros/marcas/{marca_codigo}/modelos")
            response.raise_for_status()
            modelos = response.json()['modelos']

            self.cb_modelo.clear()
            for modelo in modelos:
                self.cb_modelo.addItem(modelo['nome'])
        except Exception as e:
            QMessageBox.warning(self, "Erro", f"Erro ao buscar modelos: {e}")

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
                self.cb_marca.currentText(),
                self.cb_modelo.currentText(),
                self.sb_ano.value(),
                self.le_placa.currentText(),
                self.sb_km.value(),
                self.le_cor.currentText()
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
