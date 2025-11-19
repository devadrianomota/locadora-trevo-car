/* ============================================================
   Arquivo: 11_queries_relatorios.sql
   Autor(es): Adriano Mota, Erika Lai, Gabriela Rodrigues
   Trabalho: Sistema de Locadora de Carros
   Curso/Turma: DS- 213
   SGBD: MySQL Versão: 8.0.43
   Objetivo: Consultas de relatório para a tomada de decisão
   Execução esperada: rodar após 03_insercoes_casos_teste.sql
========================================================== */

USE locadoraCarros;

-- Relatório 1: Receita Total Agregada por Mês e Ano de Pagamento
-- Problema a ser resolvido: Qual a performance financeira da locadora ao longo do tempo?
-- Porque a abordagem foi escolhida: Utiliza as funções YEAR() e MONTH() para agrupar os pagamentos e a função SUM() para totalizar o valor_pago, permitindo uma análise temporal da receita.

SELECT
    YEAR(data_pagamento) AS ano,
    MONTH(data_pagamento) AS mes,
    SUM(valor_pago) AS receita_total
FROM pagamento
GROUP BY ano, mes
ORDER BY ano DESC, mes DESC;

-- Relatório 2: Veículos com Ocorrências Recentes e Média de Quilometragem Rodada por Aluguel
/*
Problema a ser resolvido: Quais veículos estão gerando mais problemas ou desgaste, indicando a necessidade de manutenção preventiva?
Porque a abordagem foi escolhida: Faz um JOIN entre Veículo, Entrega_Veiculo e Ocorrencia. Calcula a média de KM rodados (quilometragem_devolucao - quilometragem_retirada) e lista os veículos que tiveram ocorrências no último mês (DATE_SUB).
*/
SELECT
    V.placa,
    V.modelo,
    V.marca,
    COUNT(O.id_ocorrencia) AS total_ocorrencias,
    AVG(EV.quilometragem_devolucao - EV.quilometragem_retirada) AS km_medio_por_aluguel
FROM veiculo V
LEFT JOIN entrega_veiculo EV ON V.id_veiculo = EV.id_reserva -- Assumindo que id_reserva em entrega_veiculo se refere ao veículo da reserva
LEFT JOIN ocorrencia O ON EV.id_reserva = O.id_reserva
WHERE O.data_ocorrencia >= DATE_SUB(CURDATE(), INTERVAL 1 MONTH) -- Ocorrências no último mês
GROUP BY V.placa, V.modelo, V.marca
HAVING COUNT(O.id_ocorrencia) > 0 OR km_medio_por_aluguel > 500 -- Critério de desgaste/problema
ORDER BY total_ocorrencias DESC, km_medio_por_aluguel DESC;

-- Relatório 3: Detalhamento de Reservas que Incluem Serviços Extras
/*
Problema a ser resolvido: Qual o valor adicional gerado pelos serviços extras e quais são os mais populares?
Porque a abordagem foi escolhida: Junta Reserva, Reserva_Servico e Servicos_Extra para mostrar o valor total da reserva somado aos extras, permitindo análise do ticket médio de serviços adicionais.
*/
SELECT
    R.id_reserva,
    C.nome AS cliente,
    R.valor_total AS valor_base_reserva,
    GROUP_CONCAT(SE.nome SEPARATOR ', ') AS servicos_adicionais,
    SUM(SE.valor_diaria * RS.quantidade) AS valor_total_servicos
FROM reserva R
JOIN cliente C ON R.id_cliente = C.id_cliente
JOIN reserva_servico RS ON R.id_reserva = RS.id_reserva
JOIN servicos_extra SE ON RS.id_servico = SE.id_servico
GROUP BY R.id_reserva, C.nome, R.valor_total
ORDER BY valor_total_servicos DESC;