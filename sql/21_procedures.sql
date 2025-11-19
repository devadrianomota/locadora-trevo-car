/* ============================================================
   Arquivo: 21_procedures.sql
   Autor(es): Adriano Mota, Erika Lai, Gabriela Rodrigues
   Trabalho: Sistema de Locadora de Carros
   Curso/Turma: DS- 213
   SGBD: MySQL Versão: 8.0.43
   Objetivo: Criação de Procedures e Functions úteis para automatizar processos de negócio
   Execução esperada: rodar após 20_triggers.sql
========================================================== */

USE locadoraCarros;

DELIMITER $$

-- Procedure 1: Finaliza a reserva e devolve o veículo
-- Motivação: Centralizar a lógica de finalização de uma reserva e liberação do veículo em uma única chamada.
-- Parâmetros: p_id_reserva (INT), p_quilometragem_devolucao (INT), p_local_devolucao (VARCHAR)
CREATE PROCEDURE sp_finalizar_reserva (
    IN p_id_reserva INT,
    IN p_quilometragem_devolucao INT,
    IN p_local_devolucao VARCHAR(100)
)
BEGIN
    DECLARE v_id_veiculo INT;
    
    -- 1. Atualiza a Reserva para 'finalizada' e registra a data/hora de devolução
    UPDATE reserva
    SET status = 'finalizada'
    WHERE id_reserva = p_id_reserva;
    
    -- 2. Atualiza os dados de devolução na tabela entrega_veiculo
    UPDATE entrega_veiculo
    SET 
        quilometragem_devolucao = p_quilometragem_devolucao,
        data_devolucao = NOW(),
        local_devolucao = p_local_devolucao
    WHERE id_reserva = p_id_reserva AND data_devolucao IS NULL; -- Apenas o registro de retirada ativa
    
    -- 3. Obtém o id_veiculo e atualiza seu status para 'disponivel'
    SELECT id_veiculo INTO v_id_veiculo
    FROM reserva
    WHERE id_reserva = p_id_reserva;
    
    UPDATE veiculo
    SET status = 'disponivel'
    WHERE id_veiculo = v_id_veiculo;
    
    SELECT CONCAT('Reserva ', p_id_reserva, ' finalizada e veículo ', v_id_veiculo, ' liberado.') AS Resultado;
END$$

-- Function 2: Calcula a duração de uma reserva em dias
-- Motivação: Simplificar o cálculo da cobrança diária em qualquer query.
-- Parâmetros: p_data_ini (DATE), p_data_fim (DATE)
-- Retorno: INT (Número de dias)
CREATE FUNCTION fn_calcular_dias_aluguel (
    p_data_ini DATE,
    p_data_fim DATE
)
RETURNS INT
DETERMINISTIC
BEGIN
    DECLARE dias INT;
    -- Calcula a diferença em dias. Adiciona 1 dia para inclusão da data final.
    SET dias = DATEDIFF(p_data_fim, p_data_ini) + 1; 
    RETURN dias;
END$$

DELIMITER ;


-- DML DE TESTE para Procedures e Functions

-- TESTE 1: Procedure sp_finalizar_reserva
-- Usar Reserva ID 7 (Cenário B) - Status 'ativa', Veículo ID 3 (HR-V) está 'alugado' (pela Trigger 20)

-- 1a. Verifica status ANTES (Reserva e Veículo ID 3)
SELECT id_reserva, status, id_veiculo FROM reserva WHERE id_reserva = 7;
SELECT id_veiculo, modelo, status FROM veiculo WHERE id_veiculo = 3;

-- 1b. Executa a Procedure
CALL sp_finalizar_reserva(7, 25300, 'Filial Norte');

-- 1c. Verifica status DEPOIS (Reserva deve ser 'finalizada', Veículo ID 3 deve ser 'disponivel')
SELECT id_reserva, status, id_veiculo FROM reserva WHERE id_reserva = 7;
SELECT id_veiculo, modelo, status FROM veiculo WHERE id_veiculo = 3;
SELECT quilometragem_devolucao, data_devolucao FROM entrega_veiculo WHERE id_reserva = 7;


-- TESTE 2: Function fn_calcular_dias_aluguel
-- Testa a Reserva ID 1: de '2025-11-20' até '2025-11-23' (4 dias)
SELECT 
    data_ini, 
    data_fim, 
    fn_calcular_dias_aluguel(data_ini, data_fim) AS dias_calculados
FROM reserva 
WHERE id_reserva = 1;

-- Teste para uma nova data (5 dias)
SELECT fn_calcular_dias_aluguel('2025-10-01', '2025-10-05') AS teste_5_dias;