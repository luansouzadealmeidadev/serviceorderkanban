import sqlite3
from datetime import datetime

def criar_banco_dados():
    conn = sqlite3.connect('sistema_os.db')
    cursor = conn.cursor()
    
    # Tabela de Clientes
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS clientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        cpf TEXT UNIQUE,
        telefone TEXT,
        email TEXT,
        endereco TEXT
    )''')
    
    # Tabela de Veículos
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS veiculos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente_id INTEGER NOT NULL,
        marca TEXT NOT NULL,
        modelo TEXT NOT NULL,
        ano INTEGER,
        placa TEXT UNIQUE,
        km INTEGER,
        cor TEXT,
        FOREIGN KEY (cliente_id) REFERENCES clientes (id) ON DELETE CASCADE
    )''')
    
    # Tabela de Ordens de Serviço
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS ordens_servico (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        veiculo_id INTEGER NOT NULL,
        data_abertura TEXT,
        data_entrega TEXT,
        descricao_problema TEXT,
        servicos_realizados TEXT,
        pecas_trocadas TEXT,
        valor_total REAL,
        status TEXT CHECK(status IN ('Aberto', 'Em Andamento', 'Concluído', 'Entregue')),
        observacoes TEXT,
        FOREIGN KEY (veiculo_id) REFERENCES veiculos (id)
    )''')
    
    conn.commit()
    conn.close()

if __name__ == '__main__':
    criar_banco_dados()