-- Cada INSERT abaixo deve ser recusado por uma restrição do banco.
-- executar.py continua para o próximo comando mesmo quando um deles falha.

-- NOT NULL: nome obrigatório não informado
INSERT INTO clientes (email) VALUES ('sem-nome@email.com');

-- CHECK: nome vazio não é permitido
INSERT INTO clientes (nome) VALUES ('');

-- UNIQUE: e-mail repetido
INSERT INTO clientes (nome, email) VALUES ('Cliente duplicado', 'ana.souza@email.com');

-- FOREIGN KEY: cliente 99 não existe
INSERT INTO veiculos (id_cliente, marca, modelo, placa, ano)
VALUES (99, 'Marca', 'Modelo', 'ZZZ9Z99', 2020);

-- UNIQUE: placa repetida
INSERT INTO veiculos (id_cliente, marca, modelo, placa, ano)
VALUES (1, 'Outra marca', 'Outro modelo', 'ABC1D23', 2021);

-- CHECK: ano fora da faixa permitida
INSERT INTO veiculos (id_cliente, marca, modelo, placa, ano)
VALUES (1, 'Marca', 'Modelo', 'ZZZ9Z98', 1800);

-- CHECK: status não permitido
INSERT INTO ordens_servico (id_veiculo, status, valor_total)
VALUES (1, 'Pronta', 100);

-- CHECK: preço negativo
INSERT INTO servicos (nome, descricao, preco)
VALUES ('Serviço inválido', 'Preço negativo para testar CHECK', -10);
