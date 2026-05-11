-- =========================================
-- DW - ELEIÇÕES TSE
-- MODELO ESTRELA
-- =========================================

DROP SCHEMA IF EXISTS dw_eleicao CASCADE;

CREATE SCHEMA dw_eleicao;

SET search_path TO dw_eleicao;

-- =========================================
-- DIMENSÃO ELEIÇÃO
-- =========================================

CREATE OR REPLACE VIEW dw_eleicao.dim_eleicao AS
SELECT
    e.cd_eleicao       AS eleicao_key,
    e.ano_eleicao,
    e.nm_tipo_eleicao,
    e.nr_turno,
    e.ds_eleicao,
    e.dt_eleicao,
    e.tp_abrangencia
FROM eleicao.eleicao e;

-- =========================================
-- DIMENSÃO PARTIDO
-- =========================================

CREATE OR REPLACE VIEW dw_eleicao.dim_partido AS
SELECT
    p.nr_partido AS partido_key,
    p.sg_partido,
    p.nm_partido
FROM eleicao.partido p;

-- =========================================
-- DIMENSÃO CARGO
-- =========================================

CREATE OR REPLACE VIEW dw_eleicao.dim_cargo AS
SELECT
    c.cd_cargo AS cargo_key,
    c.ds_cargo
FROM eleicao.cargo c;

-- =========================================
-- DIMENSÃO GÊNERO
-- =========================================

CREATE OR REPLACE VIEW dw_eleicao.dim_genero AS
SELECT
    g.cd_genero AS genero_key,
    g.ds_genero
FROM eleicao.genero g;

-- =========================================
-- DIMENSÃO GRAU INSTRUÇÃO
-- =========================================

CREATE OR REPLACE VIEW dw_eleicao.dim_instrucao AS
SELECT
    gi.cd_grau_instrucao AS instrucao_key,
    gi.ds_grau_instrucao
FROM eleicao.grau_instrucao gi;

-- =========================================
-- DIMENSÃO COR / RAÇA
-- =========================================

CREATE OR REPLACE VIEW dw_eleicao.dim_cor_raca AS
SELECT
    cr.cd_cor_raca AS cor_raca_key,
    cr.ds_cor_raca
FROM eleicao.cor_raca cr;

-- =========================================
-- DIMENSÃO OCUPAÇÃO
-- =========================================

CREATE OR REPLACE VIEW dw_eleicao.dim_ocupacao AS
SELECT
    o.cd_ocupacao AS ocupacao_key,
    o.ds_ocupacao
FROM eleicao.ocupacao o;

-- =========================================
-- DIMENSÃO ESTADO CIVIL
-- =========================================

CREATE OR REPLACE VIEW dw_eleicao.dim_estado_civil AS
SELECT
    ec.cd_estado_civil AS estado_civil_key,
    ec.ds_estado_civil
FROM eleicao.estado_civil ec;

-- =========================================
-- DIMENSÃO SITUAÇÃO CANDIDATURA
-- =========================================

CREATE OR REPLACE VIEW dw_eleicao.dim_situacao_candidatura AS
SELECT
    sc.cd_situacao_candidatura AS situacao_candidatura_key,
    sc.ds_situacao_candidatura
FROM eleicao.situacao_candidatura sc;

-- =========================================
-- DIMENSÃO SITUAÇÃO TURNO
-- =========================================

CREATE OR REPLACE VIEW dw_eleicao.dim_situacao_turno AS
SELECT
    st.cd_sit_tot_turno AS situacao_turno_key,
    st.ds_sit_tot_turno
FROM eleicao.situacao_turno st;

-- =========================================
-- DIMENSÃO REGIÃO
-- =========================================

CREATE OR REPLACE VIEW dw_eleicao.dim_regiao AS
SELECT
    r.cd_regiao AS regiao_key,
    r.nm_regiao
FROM eleicao.regiao r;

-- =========================================
-- DIMENSÃO UF
-- =========================================

CREATE OR REPLACE VIEW dw_eleicao.dim_uf AS
SELECT
    u.sg_uf      AS uf_key,
    u.nm_uf,
    u.cd_regiao  AS regiao_key
FROM eleicao.uf u;

-- =========================================
-- DIMENSÃO MUNICÍPIO
-- =========================================

CREATE OR REPLACE VIEW dw_eleicao.dim_municipio AS
SELECT
    m.cd_municipio AS municipio_key,
    m.sg_ue,
    m.nm_municipio,
    m.sg_uf        AS uf_key
FROM eleicao.municipio m;

-- =========================================
-- FATO CANDIDATURA
-- =========================================

CREATE OR REPLACE VIEW dw_eleicao.fato_candidatura AS
SELECT

    -- IDENTIFICADOR
    c.sq_candidato,

    -- CHAVES DIMENSIONAIS
    c.cd_eleicao              AS eleicao_key,
    c.nr_partido              AS partido_key,
    c.cd_cargo                AS cargo_key,
    c.cd_genero               AS genero_key,
    c.cd_grau_instrucao       AS instrucao_key,
    c.cd_cor_raca             AS cor_raca_key,
    c.cd_ocupacao             AS ocupacao_key,
    c.cd_estado_civil         AS estado_civil_key,
    c.cd_situacao_candidatura AS situacao_candidatura_key,
    c.cd_sit_tot_turno        AS situacao_turno_key,

    c.cd_municipio            AS municipio_key,

    -- DADOS DO CANDIDATO
    c.nr_candidato,
    c.nm_candidato,
    c.nm_urna,
    c.nm_social,
    c.sg_uf_nascimento,

    -- MÉTRICAS
    1 AS qt_candidatos,

    CASE
        WHEN c.cd_sit_tot_turno IN (1,2,3)
        THEN 1
        ELSE 0
    END AS qt_eleitos,

    CASE
        WHEN c.cd_sit_tot_turno = 4
        THEN 1
        ELSE 0
    END AS qt_nao_eleitos,

    CASE
        WHEN c.cd_sit_tot_turno = 5
        THEN 1
        ELSE 0
    END AS qt_suplentes,

    CASE
        WHEN c.cd_situacao_candidatura > 0
        THEN 1
        ELSE 0
    END AS qt_candidatura_valida,

    -- IDADE
    EXTRACT(
        YEAR FROM AGE(
            e.dt_eleicao,
            c.dt_nascimento
        )
    ) AS idade

FROM eleicao.candidato c

LEFT JOIN eleicao.eleicao e
       ON e.cd_eleicao = c.cd_eleicao;
