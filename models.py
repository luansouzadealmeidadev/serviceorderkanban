from datetime import datetime

class Cliente:
    def __init__(self, nome, cpf, telefone=None, email=None, endereco=None):
        self.nome = nome
        self.cpf = cpf
        self.telefone = telefone
        self.email = email
        self.endereco = endereco

class Veiculo:
    def __init__(self, cliente_id, marca, modelo, ano, placa, km=None, cor=None):
        self.cliente_id = cliente_id
        self.marca = marca
        self.modelo = modelo
        self.ano = ano
        self.placa = placa
        self.km = km
        self.cor = cor

class OrdemServico:
    def __init__(self, veiculo_id, descricao_problema, status='Aberto'):
        self.veiculo_id = veiculo_id
        self.data_abertura = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.descricao_problema = descricao_problema
        self.servicos_realizados = ""
        self.pecas_trocadas = ""
        self.valor_total = 0.0
        self.status = status
        self.observacoes = ""