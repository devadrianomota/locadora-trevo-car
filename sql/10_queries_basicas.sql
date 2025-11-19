/* ============================================================
   Arquivo: 10_queries_basicas.sql
   Autor(es): Adriano Mota, Erika Lai, Gabriela Rodrigues
   Trabalho: Sistema de Locadora de Carros
   Curso/Turma: DS- 213
   SGBD: MySQL Versão: 8.0.43
   Objetivo: Consultas DML básicas para listagem, filtros e agregações.
   Execução esperada: rodar após 03_insercoes_casos_teste.sql
========================================================== */

USE locadoraCarros;

-- 1. Listagem simples: Seleciona todos os clientes
SELECT nome, cpf, email
FROM cliente
ORDER BY nome;

-- 2. JOIN entre 3 tabelas: Lista de Reservas Ativas com Cliente, Veículo e Categoria
SELECT
    R.id_reserva,
    C.nome AS cliente,
    V.modelo AS veiculo,
    CV.nome AS categoria,
    R.data_ini,
    R.data_fim
FROM reserva R
JOIN cliente C ON R.id_cliente = C.id_cliente
JOIN veiculo V ON R.id_veiculo = V.id_veiculo
JOIN categoria_veiculo CV ON V.id_categoria = CV.id_categoria
WHERE R.status = 'ativa';

-- 3. WHERE com filtro: Veículos atualmente disponíveis para locação
SELECT
    placa,
    modelo,
    marca,
    quilometragem
FROM veiculo
WHERE status = 'disponivel';

-- 4. Agregações com GROUP BY: Contagem de veículos por categoria
SELECT
    CV.nome AS categoria,
    COUNT(V.id_veiculo) AS total_veiculos
FROM categoria_veiculo CV
LEFT JOIN veiculo V ON CV.id_categoria = V.id_categoria
GROUP BY CV.nome
ORDER BY total_veiculos DESC;

-- 5. Consulta ordenada com ORDER BY e JOIN: Funcionários ordenados por Filial e Cargo
SELECT
    F.nome AS nome_funcionario,
    F.cargo,
    TEL.nome AS nome_filial
FROM funcionario F
JOIN filial TEL ON F.id_filial = TEL.id_filial
ORDER BY TEL.nome, F.cargo DESC;