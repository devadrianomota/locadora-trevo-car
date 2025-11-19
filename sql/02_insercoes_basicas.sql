
/* ============================================================
   Arquivo: 02_insercoes_basicas.sql
   Autor(es): Adriano Mota, Erika Lai, Gabriela Rodrigues
   Trabalho: Sistema de Locadora de Carros
   Curso/Turma: DS- 213
   SGBD: (PostgreSQL/MySQL) Versão: 8.0.43
   Objetivo: Inserções básicas para popular todas as tabelas principais e visualizar o sistema
   Execução esperada: rodar após 01_modelo_fisico.sql
========================================================== */

USE locadoraCarros;

-- Filiais para alocar veículos e funcionários
INSERT INTO filial (nome, endereco) VALUES
('Filial Centro', 'Rua Central, 100'),
('Filial Norte', 'Av. Norte, 220'),
('Filial Sul', 'Rua Sul, 340'),
('Filial Leste', 'Av. Leste, 500'),
('Filial Oeste', 'Av. Oeste, 900');

-- Funcionários em diferentes filiais
INSERT INTO funcionario (nome, cargo, telefone, login, senha, id_filial) VALUES
('Paula Silva','Gerente','(11)90000-0001','paula','$2y$10$hash','1'),
('Carlos Souza','Atendente','(11)90000-0002','carlos','$2y$10$hash','1'),
('Ana Lima','Atendente','(11)90000-0003','ana','$2y$10$hash','2'),
('Marcos Dias','Mecânico','(11)90000-0004','marcos','$2y$10$hash','3'),
('Joana Reis','Atendente','(11)90000-0005','joana','$2y$10$hash','4');

-- Categorias de veículos e suas diárias
INSERT INTO categoria_veiculo (nome, preco_diaria) VALUES
('Econômico', 80.00),    
('Compacto', 100.00),    
('SUV', 180.00),         
('Executivo', 250.00),   
('Luxo', 450.00);       

-- Veículos em diferentes filiais e status
INSERT INTO veiculo (placa, modelo, marca, ano, cor, quilometragem, status, id_categoria, id_filial) VALUES
('AAA1A11','Ka','Ford',2018,'Branco',45000,'disponivel',1,1), 
('BBB2B22','Onix','Chevrolet',2019,'Prata',38000,'disponivel',2,1), 
('CCC3C33','HR-V','Honda',2020,'Preto',25000,'disponivel',3,2), 
('DDD4D44','Corolla','Toyota',2021,'Prata',20000,'disponivel',4,2), -- ID 4
('EEE5E55','A8','Audi',2019,'Preto',30000,'manutencao',5,3); -- ID 5 (em manutenção)

-- Clientes
INSERT INTO cliente (nome, cpf, email, telefone, endereco) VALUES
('Lucas Pereira','111.111.111-11','lucas@gmail.com','(11)98888-0001','Rua Alfa, 10'), -- ID 1
('Mariana Rocha','222.222.222-22','mariana@gail.com','(11)98888-0002','Rua Beta, 20'), -- ID 2
('Rafael Gomes','333.333.333-33','rafael@gmail.com','(11)98888-0003','Rua Gama, 30'), -- ID 3
('Beatriz Costa','444.444.444-44','beatriz@gmail.com','(11)98888-0004','Rua Delta, 40'), -- ID 4
('Tiago Martins','555.555.555-55','tiago@gmail.com','(11)98888-0005','Rua Épsilon, 50'); -- ID 5

-- Motoristas
INSERT INTO motoristas (nome, cnh, disponibilidade) VALUES
('Alex Santos','12345678901','sim'),
('Virginia Fonseca','98765432100','sim'),
('Mateus Prado','11223344556','nao'),
('Carol dos Santos','99887766554','sim'),
('Sergio Rereira','44332211009','sim');

-- Seguros
INSERT INTO seguro (tipo, valor_seguro) VALUES
('Básico', 0.00),        -- ID 1
('Total', 45.00),         -- ID 2
('Premium', 70.00),       -- ID 3
('Básico II', 0.00),      -- ID 4
('Total Plus', 55.00);    -- ID 5

-- Serviços extra (Catálogo)
INSERT INTO servicos_extra (nome, valor_diaria) VALUES
('GPS', 15.00),             -- ID 1
('Cadeirinha', 25.00),      -- ID 2
('Motorista', 150.00),      -- ID 3
('Lavagem Premium', 40.00), -- ID 4
('Wi-Fi Portátil', 20.00);  -- ID 5

-- Reservas
-- Formato de data AAAA-MM-DD
INSERT INTO reserva (id_cliente, id_veiculo, id_seguro, data_ini, data_fim, status, valor_total) VALUES
(1,1,2,'2025-11-20','2025-11-23','ativa',300.00), -- ID 1
(2,2,1,'2025-11-21','2025-11-24','ativa',240.00), -- ID 2
(3,3,2,'2025-11-10','2025-11-12','finalizada',800.00), -- ID 3
(4,4,1,'2025-12-01','2025-12-05','cancelada',0.00), -- ID 4
(5,5,2,'2025-11-01','2025-11-05','ativa',2000.00); -- ID 5

-- Associação serviços à reserva
INSERT INTO reserva_servico (id_reserva, id_servico, quantidade) VALUES
(1, 1, 1), -- Reserva 1: GPS
(1, 4, 1), -- Reserva 1: Lavagem Premium
(3, 2, 1), -- Reserva 3: Cadeirinha
(5, 5, 1), -- Reserva 5: Wi-Fi Portátil
(2, 1, 1); -- Reserva 2: GPS

-- Entregas de veiculos (datas e horas em AAAA-MM-DD HH:MM:SS)
INSERT INTO entrega_veiculo (id_reserva, quilometragem_retirada, quilometragem_devolucao, data_retirada, data_devolucao, local_retirada, local_devolucao) VALUES
(3, 24000, 24500, '2025-11-10 09:00:00', '2025-11-12 16:00:00', 'Filial Centro','Filial Centro'), -- Reserva 3 (finalizada)
(2, 38000, NULL, '2025-11-21 10:00:00', NULL, 'Filial Centro','Filial Norte'), -- Reserva 2 (ativa, só retirada)
(5, 30000, 30500, '2025-11-01 09:00:00','2025-11-05 16:00:00','Filial Centro','Filial Centro'), -- Reserva 5 (finalizada)
(1, 45000, NULL, '2025-11-20 10:00:00',NULL,'Filial Centro','Filial Norte'), -- Reserva 1 (ativa, só retirada)
(1, 45000, 45300, '2025-11-20 10:00:00','2025-11-23 10:00:00','Filial Centro','Filial Norte'); -- Dado adicional de teste para múltiplas retiradas (ID 1)

-- Pagamentos já efetivados
INSERT INTO pagamento (id_reserva, valor_pago, data_pagamento, metodo, comprovante) VALUES
(3, 800.00, '2025-11-12 17:00:00', 'cartao', 'transacao123'),
(1, 300.00, '2025-11-19 12:00:00', 'pix', 'pix-abc-123');

-- Ocorrências
INSERT INTO ocorrencia (id_reserva, data_ocorrencia, tipo, descricao, valor_ocorrencia) VALUES
(3, '2025-11-11 14:30:00', 'Arranhão','Arranhão na porta traseira direita', 150.00),
(5, '2025-11-03 09:00:00', 'Furto parcial','Roubo de objeto do veículo', 500.00);