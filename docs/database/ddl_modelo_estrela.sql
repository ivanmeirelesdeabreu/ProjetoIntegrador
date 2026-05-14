-- =========================================
-- DW - ELEIÇÕES TSE
-- MODELO ESTRELA
-- =========================================

DROP SCHEMA IF EXISTS dw_eleicao CASCADE;

CREATE SCHEMA dw_eleicao;

SET search_path TO dw_eleicao;

-- =========================================
-- DIMENSÃO TEMPO
-- =========================================

CREATE OR REPLACE VIEW dw_eleicao.dim_tempo AS
SELECT DISTINCT

    e.dt_eleicao AS data_key,
    e.ano_eleicao AS ano_eleicao,

    EXTRACT(YEAR  FROM e.dt_eleicao) AS ano,
    EXTRACT(MONTH FROM e.dt_eleicao) AS mes,
    EXTRACT(DAY   FROM e.dt_eleicao) AS dia,

    EXTRACT(QUARTER FROM e.dt_eleicao) AS trimestre,

    CASE EXTRACT(MONTH FROM e.dt_eleicao)

        WHEN 1 THEN 'Janeiro'
        WHEN 2 THEN 'Fevereiro'
        WHEN 3 THEN 'Março'
        WHEN 4 THEN 'Abril'
        WHEN 5 THEN 'Maio'
        WHEN 6 THEN 'Junho'
        WHEN 7 THEN 'Julho'
        WHEN 8 THEN 'Agosto'
        WHEN 9 THEN 'Setembro'
        WHEN 10 THEN 'Outubro'
        WHEN 11 THEN 'Novembro'
        WHEN 12 THEN 'Dezembro'

    END AS nm_mes,

    CASE
        WHEN EXTRACT(MONTH FROM e.dt_eleicao) IN (1,2,3)
        THEN '1º Trimestre'

        WHEN EXTRACT(MONTH FROM e.dt_eleicao) IN (4,5,6)
        THEN '2º Trimestre'

        WHEN EXTRACT(MONTH FROM e.dt_eleicao) IN (7,8,9)
        THEN '3º Trimestre'

        ELSE '4º Trimestre'
    END AS nm_trimestre

FROM eleicao.eleicao e;

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
-- DIMENSÃO FEDERAÇÃO
-- =========================================

CREATE OR REPLACE VIEW dw_eleicao.dim_federacao AS
SELECT
    f.nr_federacao AS federacao_key,
    f.nm_federacao,
    f.sg_federacao,
    f.ds_composicao_federacao
FROM eleicao.federacao f;

-- =========================================
-- DIMENSÃO COLIGAÇÃO
-- =========================================

CREATE OR REPLACE VIEW dw_eleicao.dim_coligacao AS
SELECT
    c.sq_coligacao AS coligacao_key,
    c.cd_eleicao   AS eleicao_key,
    c.cd_municipio AS municipio_key,
    c.nm_coligacao,
    c.ds_composicao_coligacao
FROM eleicao.coligacao c;

-- =========================================
-- DIMENSÃO TIPO BEM
-- =========================================

CREATE OR REPLACE VIEW dw_eleicao.dim_tipo_bem AS
SELECT
    tb.cd_tipo_bem AS tipo_bem_key,
    tb.ds_tipo_bem
FROM eleicao.tipo_bem tb;

-- =========================================
-- FATO CANDIDATURA
-- =========================================

CREATE OR REPLACE VIEW dw_eleicao.fato_candidatura AS
SELECT

    -- IDENTIFICADOR
    c.sq_candidato,

    -- CHAVES DIMENSIONAIS
    c.cd_eleicao              AS eleicao_key,
    e.dt_eleicao              AS data_key,

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
    c.nr_federacao            AS federacao_key,
    c.sq_coligacao            AS coligacao_key,

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

    CASE
        WHEN c.cd_genero = 2
        THEN 1
        ELSE 0
    END AS qt_homens,

    CASE
        WHEN c.cd_genero = 4
        THEN 1
        ELSE 0
    END AS qt_mulheres,

    CASE
        WHEN c.nr_partido IS NOT NULL
        THEN 1
        ELSE 0
    END AS qt_com_partido,

    CASE
        WHEN c.nr_federacao IS NOT NULL
        THEN 1
        ELSE 0
    END AS qt_com_federacao,

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

-- =========================================
-- FATO BENS
-- =========================================

CREATE OR REPLACE VIEW dw_eleicao.fato_bens AS
SELECT

    b.id_bem,

    -- CHAVES
    b.sq_candidato            AS candidato_key,
    b.cd_tipo_bem             AS tipo_bem_key,
    b.ano_eleicao,

    c.cd_eleicao              AS eleicao_key,
    e.dt_eleicao              AS data_key,

    c.nr_partido              AS partido_key,
    c.cd_cargo                AS cargo_key,
    c.cd_municipio            AS municipio_key,

    -- DADOS
    b.nr_ordem_bem,
    b.ds_bem,

    -- MÉTRICAS
    1 AS qt_bens,

    b.vr_bem AS vr_total_bem,

    CASE
        WHEN b.vr_bem > 1000000
        THEN 1
        ELSE 0
    END AS qt_bens_milionarios,

    CASE
        WHEN b.vr_bem <= 1000000
        THEN 1
        ELSE 0
    END AS qt_bens_nao_milionarios

FROM eleicao.bem_candidato b

LEFT JOIN eleicao.candidato c
       ON c.sq_candidato = b.sq_candidato

LEFT JOIN eleicao.eleicao e
       ON e.cd_eleicao = c.cd_eleicao;