/* ============================================================
   Arquivo: 01_modelo_fisico_CORRIGIDO.sql
   Autor(es): Adriano Mota, Erika Lai e Gabriela Rodrigues
   Trabalho: Sistema de Locadora de Carros
   Curso/Turma: DS- 213
   SGBD: (PostgreSQL/MySQL) Versão: 8.0.43
   Objetivo: Criação do modelo físico (DDL)
   Execução esperada: rodar primeiro, em BD vazio
============================================================*/

/* ============================================================
   ARQUIVO: 01_SETUP_COMPLETO.sql
   OBJETIVO: Criação (DDL) e Inserção (DML) de todas as tabelas.
============================================================*/

DROP DATABASE IF EXISTS locadoraCarros;
CREATE DATABASE locadoraCarros CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE locadoraCarros;

-- 1. ESTRUTURA DE TABELAS

CREATE TABLE filial (
    id_filial INT PRIMARY KEY AUTO_INCREMENT,
    nome VARCHAR(100) NOT NULL,
    endereco VARCHAR(150) NOT NULL
);

CREATE TABLE funcionario (
    id_func INT PRIMARY KEY AUTO_INCREMENT,
    nome VARCHAR(100) NOT NULL,
    cargo VARCHAR(50),
    telefone VARCHAR(20),
    login VARCHAR(50) NOT NULL UNIQUE,
    senha VARCHAR(60) NOT NULL,
    id_filial INT NOT NULL,
    FOREIGN KEY (id_filial) REFERENCES filial(id_filial)
);

CREATE TABLE categoria_veiculo (
    id_categoria INT PRIMARY KEY AUTO_INCREMENT ,
    nome VARCHAR(50) NOT NULL,
    preco_diaria DECIMAL(10,2) NOT NULL
);

CREATE TABLE veiculo (
    id_veiculo INT PRIMARY KEY AUTO_INCREMENT,
    placa VARCHAR(12) NOT NULL UNIQUE,
    modelo VARCHAR(50) NOT NULL,
    marca VARCHAR(20),
    ano INT NOT NULL,
    cor VARCHAR(20),
    quilometragem INT,
    status ENUM('disponivel','alugado','manutencao') DEFAULT 'disponivel',
    imagem_url VARCHAR(255), 
    avaliacao DECIMAL(2, 1), 
    descricao TEXT, 
    id_categoria INT,
    id_filial INT,
    FOREIGN KEY (id_categoria) REFERENCES categoria_veiculo(id_categoria),
    FOREIGN KEY (id_filial) REFERENCES filial(id_filial)
);

CREATE TABLE veiculo_especificacao (
    id INT PRIMARY KEY AUTO_INCREMENT,
    id_veiculo INT NOT NULL,
    icone VARCHAR(10),
    detalhe VARCHAR(100),
    FOREIGN KEY (id_veiculo) REFERENCES veiculo(id_veiculo)
);

CREATE TABLE cliente (
    id_cliente INT PRIMARY KEY AUTO_INCREMENT,
    nome VARCHAR(80) NOT NULL,
    cpf VARCHAR(14) UNIQUE NOT NULL,
    email VARCHAR(100) NOT NULL,
    telefone VARCHAR(20) NOT NULL,
    endereco VARCHAR(200) NOT NULL
);

CREATE TABLE reserva (
    id_reserva INT PRIMARY KEY AUTO_INCREMENT,
    id_cliente INT NOT NULL,
    id_veiculo INT NOT NULL,
    id_seguro INT,
    data_ini DATE NOT NULL,
    data_fim DATE,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status ENUM('ativa','cancelada','finalizada') DEFAULT 'ativa',
    valor_total DECIMAL(10,2),
    FOREIGN KEY (id_cliente) REFERENCES cliente(id_cliente),
    FOREIGN KEY (id_veiculo) REFERENCES veiculo(id_veiculo)
);

CREATE TABLE servicos_extra (
    id_servico INT PRIMARY KEY AUTO_INCREMENT,
    nome VARCHAR(50) NOT NULL,
    valor_diaria DECIMAL(10,2) NOT NULL
);

CREATE TABLE reserva_servico (
    id_reserva INT,
    id_servico INT,
    quantidade INT DEFAULT 1,
    PRIMARY KEY (id_reserva, id_servico),
    FOREIGN KEY (id_reserva) REFERENCES reserva(id_reserva),
    FOREIGN KEY (id_servico) REFERENCES servicos_extra(id_servico)
);

CREATE TABLE pagamento (
    id_pagamento INT PRIMARY KEY AUTO_INCREMENT,
    id_reserva INT NOT NULL,
    valor_pago DECIMAL(10,2) NOT NULL,
    data_pagamento DATETIME NOT NULL,
    metodo VARCHAR(30) NOT NULL,
    comprovante VARCHAR(200) NOT NULL,
    FOREIGN KEY (id_reserva) REFERENCES reserva(id_reserva)
);

-- (Omitindo tabelas motoristas, seguro, entrega, ocorrencia para focar na reserva)

-- 2. INSERÇÃO DE DADOS MÍNIMOS

INSERT INTO filial (nome, endereco) VALUES ('Filial Centro', 'Rua Central, 100');

INSERT INTO funcionario (nome, cargo, telefone, login, senha, id_filial) VALUES
('Admin', 'Gerente', '(11)90000-0001', 'admin', 'admin123', 1); -- SENHA SIMPLES PARA TESTE

INSERT INTO cliente (nome, cpf, email, telefone, endereco) VALUES
('Cliente Padrão', '111.111.111-11', 'cliente@email.com', '(11)98888-0001', 'Rua Alfa, 10');

INSERT INTO categoria_veiculo (id_categoria, nome, preco_diaria) VALUES
(1, 'Star Especial (LD)', 218.95),
(2, 'Econômico Especial C/Ar (CE)', 93.95),
(3, 'Suv Automático (SX)', 161.95);

INSERT INTO veiculo (id_veiculo, placa, modelo, marca, ano, quilometragem, status, id_categoria, id_filial, imagem_url, avaliacao, descricao) VALUES 
(1, 'JEP0L01', 'COMPASS', 'JEEP', 2024, 0, 'disponivel', 1, 1, 'https://i.imgur.com/g8n1jPb.png', 4.8, 'Um SUV sofisticado e potente com motor 1.3 Turbo. Ideal para quem busca luxo, espaço e performance, tanto na cidade quanto em viagens longas.'),
(2, 'BYD0E02', 'DOLPHIN', 'BYD', 2024, 0, 'disponivel', 2, 1, 'https://i.imgur.com/V9QcR0R.png', 4.2, 'O carro elétrico perfeito para o dia a dia. Econômico, ágil e fácil de estacionar. Uma opção inteligente para uso urbano.'),
(3, 'BMW0X03', 'X1', 'BMW', 2024, 0, 'disponivel', 3, 1, 'https://i.imgur.com/rL4Gz11.png', 4.7, 'Luxo e performance em um SUV compacto e elegante. Experimente o conforto e a dirigibilidade premium da BMW.'),
(4, 'VWN0M04', 'NIVUS', 'VW', 2023, 0, 'manutencao', 3, 1, 'https://i.imgur.com/L8zQYj0.png', 4.5, 'Design moderno e motor turbo. Este carro está atualmente em manutenção e não disponível para clientes.');

INSERT INTO veiculo_especificacao (id_veiculo, icone, detalhe) VALUES
(1, '⚙️', 'Automático'), (1, '❄️', 'Ar Cond.'), (1, '👥', '5 Ocupantes'),
(2, '⚙️', 'Automático'), (2, '⚡', 'Elétrico'), (2, '👥', '5 Ocupantes'),
(3, '⚙️', 'Automático'), (3, '❄️', 'Ar Dual Zone'), (3, '⛽', 'Gasolina'),
(4, '⚙️', 'Automático'), (4, '⛽', 'Flex'), (4, '👥', '5 Ocupantes');

INSERT INTO servicos_extra (nome, valor_diaria) VALUES
('Cadeirinha para Criança', 25.00),
('GPS - Navegador', 15.00),
('Proteção de Pneus', 10.00);