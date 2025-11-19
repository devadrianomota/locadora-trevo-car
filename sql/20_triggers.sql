/* ============================================================
   Arquivo: 20_triggers.sql
   Autor(es): Adriano Mota, Erika Lai, Gabriela Rodrigues
   Trabalho: Sistema de Locadora de Carros
   Curso/Turma: DS- 213
   SGBD: MySQL Versão: 8.0.43
   Objetivo: Criação de Triggers para validação e automação de regras de negócio
   Execução esperada: rodar após 03_insercoes_casos_teste.sql
========================================================== */

USE locadoraCarros;


DELIMITER $$

-- Trigger 1: Atualiza o status do veículo para 'alugado' no momento da retirada
-- Quando dispara: BEFORE INSERT na tabela 'entrega_veiculo'
-- Tabela: veiculo
-- O que faz: Garante que o status do veículo na tabela 'veiculo' seja alterado para 'alugado' assim que o registro de retirada é criado, prevenindo aluguel duplo.
CREATE TRIGGER tg_veiculo_alugado_on_retirada
BEFORE INSERT ON entrega_veiculo
FOR EACH ROW
BEGIN
    DECLARE v_id_veiculo INT;
    
    -- Obtém o id_veiculo da reserva
    SELECT id_veiculo INTO v_id_veiculo
    FROM reserva
    WHERE id_reserva = NEW.id_reserva;
    
    -- Atualiza o status do veículo para 'alugado'
    UPDATE veiculo
    SET status = 'alugado'
    WHERE id_veiculo = v_id_veiculo;
END$$

-- Trigger 2: Insere um valor padrão para ocorrências de danos sem valor definido
-- Quando dispara: BEFORE INSERT na tabela 'ocorrencia'
-- Tabela: ocorrencia
-- O que faz: Se uma ocorrência for do tipo 'Arranhão' ou 'Avaria' e o valor_ocorrencia for NULL ou 0, define um valor padrão de R$ 100.00.
CREATE TRIGGER tg_valor_padrao_ocorrencia
BEFORE INSERT ON ocorrencia
FOR EACH ROW
BEGIN
    IF NEW.tipo IN ('Arranhão', 'Avaria') AND (NEW.valor_ocorrencia IS NULL OR NEW.valor_ocorrencia = 0) THEN
        SET NEW.valor_ocorrencia = 100.00;
    END IF;
END$$

-- Retorna o delimitador ao padrão (ponto e vírgula)
DELIMITER ;


-- DML DE TESTE para os Triggers

-- TESTE 1: Trigger tg_veiculo_alugado_on_retirada
-- Veículo ID 4 (Corolla) está 'disponivel'. (Verificar em 03_insercoes_casos_teste.sql)
-- Inserir nova retirada para Reserva ID 6 (Veículo ID 4).

-- 1a. Verifica status ANTES da inserção (deve ser 'disponivel')
SELECT id_veiculo, modelo, status FROM veiculo WHERE id_veiculo = 4;

-- 1b. Executa a inserção (que disparará a Trigger)
INSERT INTO entrega_veiculo (id_reserva, quilometragem_retirada, data_retirada, local_retirada) 
VALUES (6, 20000, '2025-12-10 10:00:00', 'Filial Centro');

-- 1c. Verifica status DEPOIS da inserção (deve ser 'alugado')
SELECT id_veiculo, modelo, status FROM veiculo WHERE id_veiculo = 4;


-- TESTE 2: Trigger tg_valor_padrao_ocorrencia
-- Reserva ID 6 (do Cenário A)
-- Inserir ocorrência de 'Pneu Furado' com valor_ocorrencia = NULL

-- 2a. Verifica o total de ocorrências ANTES da inserção
SELECT COUNT(*) FROM ocorrencia;

-- 2b. Executa a inserção (que disparará a Trigger)
INSERT INTO ocorrencia (id_reserva, data_ocorrencia, tipo, descricao, valor_ocorrencia) 
VALUES (6, '2025-12-11 11:00:00', 'Arranhão','Retrovisor danificado', NULL);

-- 2c. Verifica o valor inserido (deve ser 100.00 e o total deve ser +1)
SELECT id_ocorrencia, tipo, valor_ocorrencia FROM ocorrencia WHERE id_reserva = 6 AND tipo = 'Arranhão';
