/* ============================================================
   Arquivo: 03_insercoes_casos_teste.sql
   Autor(es): Adriano Mota, Erika Lai, Gabriela Rodrigues
   Trabalho: Sistema de Locadora de Carros
   Curso/Turma: DS- 213
   SGBD: MySQL Versão: 8.0.43
   Objetivo: Inserções para cenários específicos (cenários de teste para Triggers/Procedures).
   Execução esperada: rodar após 02_insercoes_basicas.sql
========================================================== */

USE locadoraCarros;

-- Cenário A: Nova reserva e retirada para teste de trigger
-- A Trigger 'tg_veiculo_alugado_on_retirada' (em 20_triggers.sql) deve mudar o status do Veículo (ID 4 - Corolla) de 'disponivel' para 'alugado' após esta inserção na entrega_veiculo.

INSERT INTO cliente (nome, cpf, email, telefone, endereco) VALUES
('Teste Trigger A','666.666.666-66','teste@trigger.com','(11)97777-0000','Rua Teste A, 1'); 

INSERT INTO reserva (id_cliente, id_veiculo, id_seguro, data_ini, data_fim, status, valor_total) VALUES
(6, 4, 2, '2025-12-10', '2025-12-15', 'ativa', 1250.00); 

INSERT INTO entrega_veiculo (id_reserva, quilometragem_retirada, data_retirada, local_retirada) 
VALUES (6, 20000, '2025-12-10 10:00:00', 'Filial Centro'); 


-- Cenário B: Nova Reserva (ID 7) para Teste de Procedure
--  A Procedure 'sp_finalizar_reserva' (em 21_procedures.sql) deve alterar o status da Reserva 7 de 'ativa' para 'finalizada' e o status do Veículo (ID 3 - HR-V) para 'disponivel'.
INSERT INTO cliente (nome, cpf, email, telefone, endereco) VALUES
('Teste Procedure B','777.777.777-77','teste@procedure.com','(11)96666-0000','Rua Teste B, 2'); -- ID 7

INSERT INTO reserva (id_cliente, id_veiculo, id_seguro, data_ini, data_fim, status, valor_total) VALUES
(7, 3, 3, '2025-12-15', '2025-12-18', 'ativa', 540.00); -- ID 7 (Veiculo 3 - HR-V)

INSERT INTO entrega_veiculo (id_reserva, quilometragem_retirada, data_retirada, local_retirada) 
VALUES (7, 25000, '2025-12-15 08:00:00', 'Filial Norte');


-- Cenário C: Ocorrência sem valor para Teste de Trigger
--  A Trigger 'tg_valor_padrao_ocorrencia' (em 20_triggers.sql) deve inserir um valor padrão de R$ 100.00 na coluna valor_ocorrencia após esta inserção.
-- A inserção abaixo será usada em 20_triggers.sql, mas a reserva (ID 6) já foi criada.
INSERT INTO ocorrencia (id_reserva, data_ocorrencia, tipo, descricao, valor_ocorrencia) 
VALUES (6, '2025-12-11 11:00:00', 'Pneu Furado','Pneu dianteiro esquerdo furado', NULL);