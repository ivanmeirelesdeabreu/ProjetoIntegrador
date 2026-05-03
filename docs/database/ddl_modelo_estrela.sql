DROP SCHEMA IF EXISTS dw_eleicao CASCADE;
CREATE SCHEMA dw_eleicao;
SET search_path TO dw_eleicao;

CREATE OR REPLACE VIEW dw_eleicao.dim_eleicao AS
SELECT
    cd_eleicao AS eleicao_key,
    ano_eleicao,
    nm_tipo_eleicao,
    nr_turno,
    ds_eleicao,
    dt_eleicao,
    tp_abrangencia
FROM eleicao.eleicao;

CREATE OR REPLACE VIEW dw_eleicao.dim_partido AS
SELECT
    nr_partido AS partido_key,
    sg_partido,
    nm_partido
FROM eleicao.partido;


CREATE OR REPLACE VIEW dw_eleicao.dim_cargo AS
SELECT
    cd_cargo AS cargo_key,
    ds_cargo
FROM eleicao.cargo;

CREATE OR REPLACE VIEW dw_eleicao.dim_genero AS
SELECT
    cd_genero AS genero_key,
    ds_genero
FROM eleicao.genero;


CREATE OR REPLACE VIEW dw_eleicao.dim_instrucao AS
SELECT
    cd_grau_instrucao AS instrucao_key,
    ds_grau_instrucao
FROM eleicao.grau_instrucao;

CREATE OR REPLACE VIEW dw_eleicao.dim_cor_raca AS
SELECT
    cd_cor_raca AS cor_raca_key,
    ds_cor_raca
FROM eleicao.cor_raca;

CREATE OR REPLACE VIEW dw_eleicao.dim_ocupacao AS
SELECT
    cd_ocupacao AS ocupacao_key,
    ds_ocupacao
FROM eleicao.ocupacao;

CREATE OR REPLACE VIEW dw_eleicao.dim_estado_civil AS
SELECT
    cd_estado_civil AS estado_civil_key,
    ds_estado_civil
FROM eleicao.estado_civil;

CREATE OR REPLACE VIEW dw_eleicao.dim_situacao_candidatura AS
SELECT
    cd_situacao_candidatura AS situacao_candidatura_key,
    ds_situacao_candidatura
FROM eleicao.situacao_candidatura;

CREATE OR REPLACE VIEW dw_eleicao.dim_situacao_turno AS
SELECT
    cd_sit_tot_turno AS situacao_turno_key,
    ds_sit_tot_turno
FROM eleicao.situacao_turno;

CREATE OR REPLACE VIEW dw.dim_municipio AS
SELECT
    sg_uf || '-' || sg_ue AS municipio_key,

    sg_uf,
    sg_ue,
    nm_ue,

    CASE
        WHEN sg_uf IN ('AC','AP','AM','PA','RO','RR','TO')
            THEN 'Norte'

        WHEN sg_uf IN ('AL','BA','CE','MA','PB','PE','PI','RN','SE')
            THEN 'Nordeste'

        WHEN sg_uf IN ('DF','GO','MT','MS')
            THEN 'Centro-Oeste'

        WHEN sg_uf IN ('ES','MG','RJ','SP')
            THEN 'Sudeste'

        WHEN sg_uf IN ('PR','RS','SC')
            THEN 'Sul'

        ELSE 'Não Informado'
    END AS regiao

FROM eleicao.municipio;

CREATE OR REPLACE VIEW dw_eleicao.fato_candidatura AS
SELECT

    c.sq_candidato,

    -- Chaves
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

    c.sg_uf,
    c.sg_ue,
    c.sg_uf || '-' || c.sg_ue AS municipio_key,

    -- Métricas
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

    EXTRACT(
        YEAR FROM AGE(
            e.dt_eleicao,
            c.dt_nascimento
        )
    ) AS idade

FROM eleicao.candidato c

LEFT JOIN eleicao.eleicao e
       ON e.cd_eleicao = c.cd_eleicao;




