-- 1) Todos os clientes e a quantidade de veículos (LEFT JOIN + GROUP BY).
SELECT c.id_cliente, c.nome, COUNT(v.id_veiculo) AS total_veiculos
FROM clientes c
LEFT JOIN veiculos v ON v.id_cliente = c.id_cliente
GROUP BY c.id_cliente
ORDER BY c.nome;

-- 2) Veículos com o nome do proprietário (INNER JOIN).
SELECT v.placa, v.marca, v.modelo, c.nome AS proprietario
FROM veiculos v
INNER JOIN clientes c ON c.id_cliente = v.id_cliente
ORDER BY c.nome, v.modelo;

-- 3) Ordens de serviço com cliente e veículo (JOIN de três tabelas).
SELECT os.id_os, c.nome AS cliente, v.modelo, v.placa,
       os.status, os.valor_total, os.data_abertura
FROM ordens_servico os
INNER JOIN veiculos v ON v.id_veiculo = os.id_veiculo
INNER JOIN clientes c ON c.id_cliente = v.id_cliente
ORDER BY os.id_os DESC;

-- 4) Serviços que contêm a palavra "alinh" (LIKE).
SELECT id_servico, nome, preco
FROM servicos
WHERE nome LIKE '%alinh%'
ORDER BY nome;

-- 5) Quantidade e valor total das ordens agrupadas por status (GROUP BY).
SELECT status, COUNT(*) AS quantidade, SUM(valor_total) AS total
FROM ordens_servico
GROUP BY status
ORDER BY status;

-- 6) Catálogo com quantidade de vezes que cada serviço foi utilizado (LEFT JOIN).
SELECT s.nome, COUNT(os_s.id_os) AS vezes_utilizado
FROM servicos s
LEFT JOIN os_servicos os_s ON os_s.id_servico = s.id_servico
GROUP BY s.id_servico
ORDER BY vezes_utilizado DESC, s.nome;

-- 7) Itens de uma ordem: substitua o número 1 para consultar outra ordem.
SELECT s.nome, os_s.quantidade, os_s.valor_unitario,
       os_s.quantidade * os_s.valor_unitario AS subtotal
FROM os_servicos os_s
INNER JOIN servicos s ON s.id_servico = os_s.id_servico
WHERE os_s.id_os = 1;
