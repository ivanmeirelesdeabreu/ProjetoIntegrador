-- =========================================
-- DW - ELEIÇÕES TSE
-- MODELO ESTRELA
-- =========================================

--DROP SCHEMA IF EXISTS dw_eleicao CASCADE;

--CREATE SCHEMA dw_eleicao;

SET search_path TO eleicao;

-- =========================================
-- DIMENSÃO TEMPO
-- =========================================

CREATE OR REPLACE VIEW eleicao.dim_tempo AS
SELECT DISTINCT
    e.dt_eleicao,
    e.ano_eleicao,
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
-- FATO ELEIÇÃO
-- =========================================
--REFRESH MATERIALIZED VIEW eleicao.fato_eleicao;
--DROP MATERIALIZED VIEW IF EXISTS eleicao.fato_eleicao;
--CREATE MATERIALIZED VIEW eleicao.fato_eleicao AS


CREATE OR REPLACE VIEW eleicao.fato_eleicao AS 
SELECT 
    e.cd_eleicao, 
    e.ano_eleicao, 
    e.dt_eleicao,
    e.nr_turno, 
    e.cd_abrangencia,
    a.tp_abrangencia,
    c.cd_cargo, 
    c.sq_candidato, 
    c.nr_partido, 
    c.cd_municipio_tse, 
    c.nr_federacao, 
    c.sq_coligacao,
    -- CHAVES DE PERFIL (Para filtros diretos nas dimensões)
    c.cd_genero,
    c.cd_cor_raca,
    c.cd_grau_instrucao,
    c.cd_situacao_candidatura,
    c.cd_sit_tot_turno,
    -- MÉTRICAS
    CASE WHEN e.nr_turno = 1 THEN 1 ELSE 0 END AS qt_candidatos,
    CASE WHEN c.nr_partido IS NOT NULL THEN 1 ELSE 0 END AS qt_com_partido,
    CASE WHEN c.nr_federacao IS NOT NULL THEN 1 ELSE 0 END AS qt_com_federacao,
    CASE WHEN c.cd_sit_tot_turno IN (1,2,3) THEN 1 ELSE 0 END AS qt_eleitos,
    CASE WHEN c.cd_sit_tot_turno = 4 THEN 1 ELSE 0 END AS qt_nao_eleitos,
    CASE WHEN c.cd_sit_tot_turno = 5 THEN 1 ELSE 0 END AS qt_suplentes,
    CASE WHEN c.cd_situacao_candidatura > 0 THEN 1 ELSE 0 END AS qt_candidatura_valida,
    CASE WHEN c.cd_genero = 2 THEN 1 ELSE 0 END AS qt_homens,
    CASE WHEN c.cd_genero = 4 THEN 1 ELSE 0 END AS qt_mulheres,
    CASE WHEN c.nm_social IS NOT NULL THEN 1 ELSE 0 END AS qt_usa_nome_social    
    -- Removida a vírgula aqui antes do FROM
FROM eleicao.eleicao e 
LEFT JOIN eleicao.candidato c ON c.cd_eleicao = e.cd_eleicao
LEFT JOIN eleicao.abrangencia a ON a.cd_abrangencia = e.cd_abrangencia;

CREATE OR REPLACE VIEW eleicao.dim_eleicao AS
select
	e.cd_eleicao,
    e.nm_tipo_eleicao,
    e.ds_eleicao,
    e.cd_abrangencia
FROM eleicao.eleicao e;

-- =========================================
-- DIMENSÃO PARTIDO
-- =========================================

CREATE OR REPLACE VIEW eleicao.dim_partido AS
SELECT
    p.nr_partido,
    p.sg_partido,
    p.nm_partido
FROM eleicao.partido p;

-- =========================================
-- DIMENSÃO CARGO
-- =========================================

CREATE OR REPLACE VIEW eleicao.dim_cargo AS
SELECT
    c.cd_cargo,
    c.ds_cargo
FROM eleicao.cargo c;

-- =========================================
-- DIMENSÃO GÊNERO
-- =========================================

CREATE OR REPLACE VIEW eleicao.dim_genero AS
SELECT
    g.cd_genero,
    g.ds_genero
FROM eleicao.genero g;

-- =========================================
-- DIMENSÃO GRAU INSTRUÇÃO
-- =========================================

CREATE OR REPLACE VIEW eleicao.dim_instrucao AS
SELECT
    gi.cd_grau_instrucao,
    gi.ds_grau_instrucao
FROM eleicao.grau_instrucao gi;

-- =========================================
-- DIMENSÃO COR / RAÇA
-- =========================================

CREATE OR REPLACE VIEW eleicao.dim_cor_raca AS
SELECT
    cr.cd_cor_raca,
    cr.ds_cor_raca
FROM eleicao.cor_raca cr;

-- =========================================
-- DIMENSÃO OCUPAÇÃO
-- =========================================

CREATE OR REPLACE VIEW eleicao.dim_ocupacao AS
SELECT
    o.cd_ocupacao,
    o.ds_ocupacao
FROM eleicao.ocupacao o;

-- =========================================
-- DIMENSÃO ESTADO CIVIL
-- =========================================

CREATE OR REPLACE VIEW eleicao.dim_estado_civil AS
SELECT
    ec.cd_estado_civil,
    ec.ds_estado_civil
FROM eleicao.estado_civil ec;

-- =========================================
-- DIMENSÃO SITUAÇÃO CANDIDATURA
-- =========================================

CREATE OR REPLACE VIEW eleicao.dim_situacao_candidatura AS
SELECT
    sc.cd_situacao_candidatura,
    sc.ds_situacao_candidatura
FROM eleicao.situacao_candidatura sc;

-- =========================================
-- DIMENSÃO SITUAÇÃO TURNO
-- =========================================

CREATE OR REPLACE VIEW eleicao.dim_situacao_turno AS
SELECT
    st.cd_sit_tot_turno,
    st.ds_sit_tot_turno
FROM eleicao.situacao_turno st;

-- =========================================
-- DIMENSÃO REGIÃO
-- =========================================

CREATE OR REPLACE VIEW eleicao.dim_regiao AS
SELECT
    r.cd_regiao,
    r.nm_regiao
FROM eleicao.regiao r;

-- =========================================
-- DIMENSÃO UF
-- =========================================

CREATE OR REPLACE VIEW eleicao.dim_uf AS
SELECT
    u.sg_uf,
    u.nm_uf,
    u.cd_regiao
FROM eleicao.uf u;

-- =========================================
-- DIMENSÃO MUNICÍPIO
-- =========================================

CREATE OR REPLACE VIEW eleicao.dim_municipio AS
SELECT
    m.cd_municipio_tse,
    m.nm_municipio,
    m.sg_uf
FROM eleicao.municipio m;

-- =========================================
-- DIMENSÃO FEDERAÇÃO
-- =========================================

CREATE OR REPLACE VIEW eleicao.dim_federacao AS
SELECT
    f.nr_federacao,
    f.nm_federacao,
    f.sg_federacao,
    f.ds_composicao_federacao
FROM eleicao.federacao f;

-- =========================================
-- DIMENSÃO COLIGAÇÃO
-- =========================================

CREATE OR REPLACE VIEW eleicao.dim_coligacao AS
SELECT
    c.sq_coligacao,
    c.nm_coligacao,
    c.ds_composicao_coligacao
FROM eleicao.coligacao c;

-- =========================================
-- DIMENSÃO TIPO BEM
-- =========================================

CREATE OR REPLACE VIEW eleicao.dim_tipo_bem AS
SELECT
    tb.cd_tipo_bem,
    tb.ds_tipo_bem
FROM eleicao.tipo_bem tb;

-- =========================================
-- DIMENSÃO CANDIDATO
-- =========================================
CREATE OR REPLACE VIEW eleicao.dim_candidato AS 
SELECT 
	c.cd_eleicao,
    c.sq_candidato, 
    c.nr_candidato, 
    c.nm_candidato, 
    c.nm_urna, 
    c.nm_social, 
    c.sg_uf_nascimento,
    EXTRACT(YEAR FROM AGE(e.dt_eleicao, c.dt_nascimento)) AS idade
FROM eleicao.candidato c
LEFT JOIN eleicao.eleicao e ON e.cd_eleicao = c.cd_eleicao;

-- =========================================
-- FATO PRESTACAO CONTAS
-- =========================================
--REFRESH MATERIALIZED VIEW eleicao.fato_prestacao_contas;
--DROP MATERIALIZED VIEW IF EXISTS eleicao.fato_prestacao_contas;
--CREATE MATERIALIZED VIEW eleicao.fato_prestacao_contas AS

CREATE OR REPLACE VIEW eleicao.fato_prestacao_contas AS 
SELECT 
    b.id_bem,
    b.cd_eleicao,
    b.sq_candidato,
    b.cd_tipo_bem, 
    c.cd_municipio_tse,
    b.vr_bem,
    1 AS qt_bens,
    CASE WHEN b.vr_bem > 1000000 THEN 1 ELSE 0 END AS qt_bens_milionarios
FROM eleicao.bem_candidato b
LEFT JOIN eleicao.candidato c ON  b.sq_candidato = c.sq_candidato 
    AND b.cd_eleicao = c.cd_eleicao; 

