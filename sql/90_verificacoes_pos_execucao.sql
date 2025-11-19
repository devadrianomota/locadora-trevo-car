/* ============================================================
   Arquivo: 90_verificacoes_pos_execucao.sql
   Autor(es): Adriano Mota, Erika Lai, Gabriela Rodrigues
   Trabalho: Sistema de Locadora de Carros
   Curso/Turma: DS- 213
   SGBD: MySQL Versão: 8.0.43
   Objetivo: Checagens rápidas para validar a base de dados após a execução completa dos scripts
   Execução esperada: rodar após 21_procedures.sql
========================================================== */

USE locadoraCarros;

-- 1. SELECT COUNT(*) por tabela
-- O que comprova: Que todas as tabelas foram populadas e que a contagem de registros está correta após as inserções básicas (02) e de teste (03).
SELECT 'filial' AS tabela, COUNT(*) AS total_registros FROM filial
UNION ALL
SELECT 'cliente', COUNT(*) FROM cliente
UNION ALL
SELECT 'veiculo', COUNT(*) FROM veiculo
UNION ALL
SELECT 'reserva', COUNT(*) FROM reserva
UNION ALL
SELECT 'ocorrencia', COUNT(*) FROM ocorrencia
UNION ALL
SELECT 'reserva_servico', COUNT(*) FROM reserva_servico;

-- 2. Maiores e menores valores em colunas críticas (Valor total de reservas)
-- O que comprova: A faixa de valores das reservas inseridas.
SELECT 
    MAX(valor_total) AS maior_valor_reserva,
    MIN(valor_total) AS menor_valor_reserva,
    AVG(valor_total) AS media_valor_reserva
FROM reserva
WHERE status = 'finalizada';

-- 3. Verificação de Integridade Lógica 1: Veículos em status 'alugado'
-- O que comprova: Que a Trigger 'tg_veiculo_alugado_on_retirada' funcionou e que as reservas ativas correspondem aos veículos alugados.
SELECT 
    V.modelo, 
    V.placa, 
    V.status 
FROM veiculo V
WHERE V.status = 'alugado';

-- 4. Verificação de Integridade Lógica 2: Ocorrências com valor_ocorrencia padrão (100.00)
-- O que comprova: Que a Trigger 'tg_valor_padrao_ocorrencia' funcionou para a ocorrência sem valor inserida no teste.
SELECT * FROM ocorrencia 
WHERE valor_ocorrencia = 100.00 AND tipo IN ('Arranhão', 'Avaria');