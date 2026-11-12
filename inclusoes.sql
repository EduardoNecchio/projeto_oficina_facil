-- Dados fictícios para testar o banco Oficina Fácil.
-- Execute este arquivo somente depois de flask --app app init-db e apenas uma vez.

-- CLIENTES
INSERT INTO clientes (id_cliente, nome, telefone, email) VALUES
    (1, 'Ana Souza', '(11) 99999-1001', 'ana.souza@email.com'),
    (2, 'Bruno Lima', '(11) 99999-1002', 'bruno.lima@email.com'),
    (3, 'Carla Dias', '(11) 99999-1003', 'carla.dias@email.com');

-- VEÍCULOS
INSERT INTO veiculos (id_veiculo, id_cliente, marca, modelo, placa, ano) VALUES
    (1, 1, 'Toyota', 'Corolla', 'ABC1D23', 2022),
    (2, 1, 'Honda', 'Civic', 'DEF4G56', 2020),
    (3, 2, 'Chevrolet', 'Onix', 'GHI7J89', 2023),
    (4, 3, 'Volkswagen', 'Golf', 'KLM2N34', 2018);

-- SERVIÇOS
INSERT INTO servicos (id_servico, nome, descricao, preco) VALUES
    (1, 'Troca de óleo', 'Troca de óleo do motor e filtro', 189.90),
    (2, 'Alinhamento', 'Alinhamento de direção', 90.00),
    (3, 'Balanceamento', 'Balanceamento das rodas', 80.00),
    (4, 'Revisão básica', 'Inspeção dos principais itens do veículo', 250.00),
    (5, 'Higienização interna', 'Limpeza interna dos bancos e carpetes', 160.00);

-- ORDENS DE SERVIÇO
INSERT INTO ordens_servico (id_os, id_veiculo, status, valor_total, observacoes) VALUES
    (1, 1, 'Em andamento', 279.90, 'Cliente solicitou conferência dos pneus.'),
    (2, 3, 'Concluída', 250.00, 'Revisão realizada e veículo liberado.');

-- ITENS DAS ORDENS
INSERT INTO os_servicos (id_os, id_servico, quantidade, valor_unitario) VALUES
    (1, 1, 1, 189.90),
    (1, 2, 1, 90.00),
    (2, 4, 1, 250.00);

-- CONFERÊNCIA DOS REGISTROS
SELECT id_cliente, nome, email FROM clientes ORDER BY id_cliente;
SELECT id_veiculo, marca, modelo, placa, id_cliente FROM veiculos ORDER BY id_veiculo;
SELECT id_os, id_veiculo, status, valor_total FROM ordens_servico ORDER BY id_os;
