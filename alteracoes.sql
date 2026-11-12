-- Exemplos de UPDATE e DELETE para praticar DML.
-- Os IDs abaixo correspondem aos dados de inclusoes.sql.

-- Altera o telefone de um cliente.
UPDATE clientes
SET telefone = '(11) 98888-1001'
WHERE id_cliente = 1;

-- Altera o preço de um serviço.
UPDATE servicos
SET preco = 199.90
WHERE id_servico = 1;

-- Atualiza o status da primeira ordem.
UPDATE ordens_servico
SET status = 'Concluída', updated_at = CURRENT_TIMESTAMP
WHERE id_os = 1;

-- Exclui um serviço de exemplo que não está vinculado a nenhuma ordem.
DELETE FROM servicos
WHERE id_servico = 5;

-- Confere os dados alterados.
SELECT id_cliente, nome, telefone FROM clientes WHERE id_cliente = 1;
SELECT id_servico, nome, preco FROM servicos WHERE id_servico = 1;
SELECT id_os, status, valor_total FROM ordens_servico WHERE id_os = 1;
