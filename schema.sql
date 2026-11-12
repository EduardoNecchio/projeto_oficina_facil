-- Oficina Fácil - esquema relacional SQLite
-- ATENÇÃO: este arquivo recria o banco e apaga os dados existentes.
PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS os_servicos;
DROP TABLE IF EXISTS ordens_servico;
DROP TABLE IF EXISTS veiculos;
DROP TABLE IF EXISTS servicos;
DROP TABLE IF EXISTS clientes;

CREATE TABLE clientes (
    id_cliente INTEGER PRIMARY KEY AUTOINCREMENT,
    nome       TEXT NOT NULL CHECK (length(trim(nome)) > 0),
    telefone   TEXT,
    email      TEXT UNIQUE,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE veiculos (
    id_veiculo INTEGER PRIMARY KEY AUTOINCREMENT,
    id_cliente INTEGER NOT NULL,
    marca      TEXT NOT NULL CHECK (length(trim(marca)) > 0),
    modelo     TEXT NOT NULL CHECK (length(trim(modelo)) > 0),
    placa      TEXT NOT NULL UNIQUE CHECK (length(replace(placa, '-', '')) = 7),
    ano        INTEGER CHECK (ano IS NULL OR ano BETWEEN 1886 AND 2100),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente) ON DELETE RESTRICT
);

CREATE TABLE servicos (
    id_servico INTEGER PRIMARY KEY AUTOINCREMENT,
    nome       TEXT NOT NULL UNIQUE CHECK (length(trim(nome)) > 0),
    descricao  TEXT,
    preco      REAL NOT NULL CHECK (preco >= 0),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE ordens_servico (
    id_os          INTEGER PRIMARY KEY AUTOINCREMENT,
    id_veiculo     INTEGER NOT NULL,
    data_abertura  TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status         TEXT NOT NULL DEFAULT 'Aberta'
                   CHECK (status IN ('Aberta', 'Em andamento', 'Concluída', 'Cancelada')),
    valor_total    REAL NOT NULL DEFAULT 0 CHECK (valor_total >= 0),
    observacoes    TEXT,
    updated_at     TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_veiculo) REFERENCES veiculos(id_veiculo) ON DELETE RESTRICT
);

-- A tabela associativa resolve o relacionamento N:N entre ordens e serviços.
CREATE TABLE os_servicos (
    id_os         INTEGER NOT NULL,
    id_servico    INTEGER NOT NULL,
    quantidade    INTEGER NOT NULL DEFAULT 1 CHECK (quantidade > 0),
    valor_unitario REAL NOT NULL CHECK (valor_unitario >= 0),
    PRIMARY KEY (id_os, id_servico),
    FOREIGN KEY (id_os) REFERENCES ordens_servico(id_os) ON DELETE CASCADE,
    FOREIGN KEY (id_servico) REFERENCES servicos(id_servico) ON DELETE RESTRICT
);

CREATE INDEX idx_veiculos_cliente ON veiculos(id_cliente);
CREATE INDEX idx_ordens_veiculo ON ordens_servico(id_veiculo);
CREATE INDEX idx_ordens_status ON ordens_servico(status);
CREATE INDEX idx_os_servicos_servico ON os_servicos(id_servico);
