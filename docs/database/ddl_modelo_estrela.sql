-- =========================================
-- DW - ELEIÇÕES TSE
-- MODELO ESTRELA
-- =========================================

SET search_path TO eleicao;

CREATE OR REPLACE VIEW dim_eleicao AS
SELECT
    e.cd_eleicao,
    e.ano_eleicao,
    e.nm_tipo_eleicao,
    e.nr_turno,
    e.ds_eleicao,
    e.dt_eleicao,
    a.tp_abrangencia
FROM eleicao e
LEFT JOIN abrangencia a
    ON a.cd_abrangencia = e.cd_abrangencia;
--
CREATE OR REPLACE VIEW dim_tempo AS
SELECT DISTINCT
    e.dt_eleicao,
    EXTRACT(YEAR FROM e.dt_eleicao) AS ano,
    EXTRACT(MONTH FROM e.dt_eleicao) AS mes,
    EXTRACT(DAY FROM e.dt_eleicao) AS dia,
    EXTRACT(QUARTER FROM e.dt_eleicao) AS trimestre
FROM eleicao e;
--
CREATE OR REPLACE VIEW dim_uf AS
SELECT
    u.sg_uf,
    u.nm_uf,
    r.cd_regiao,
    r.nm_regiao
FROM uf u
LEFT JOIN regiao r
    ON r.cd_regiao = u.cd_regiao;
--
CREATE OR REPLACE VIEW dim_municipio AS
SELECT
    m.cd_municipio_tse,
    m.nm_municipio,
    m.sg_uf,
    u.nm_uf,
    r.nm_regiao
FROM municipio m
LEFT JOIN uf u
    ON u.sg_uf = m.sg_uf
LEFT JOIN regiao r
    ON r.cd_regiao = u.cd_regiao;
--
CREATE OR REPLACE VIEW dim_cargo AS
SELECT
    cd_cargo,
    ds_cargo
FROM cargo;
--
CREATE OR REPLACE VIEW dim_partido AS
SELECT
    nr_partido,
    sg_partido,
    nm_partido
FROM partido;
--
CREATE OR REPLACE VIEW dim_federacao AS
SELECT
    nr_federacao,
    sg_federacao,
    nm_federacao,
    ds_composicao_federacao
FROM federacao;
--
CREATE OR REPLACE VIEW dim_tipo_bem AS
SELECT
    cd_tipo_bem,
    ds_tipo_bem
FROM tipo_bem;
--
CREATE OR REPLACE VIEW fato_eleicao AS
SELECT

    c.id_candidatura,

    -- eleição
    e.cd_eleicao,
    e.ano_eleicao,
    e.dt_eleicao,

    -- localização
    c.sg_uf,
    c.cd_municipio_tse,

    -- cargo
    c.cd_cargo,
    cg.ds_cargo,

    -- partido
    c.nr_partido,
    p.sg_partido,

    -- federação
    c.nr_federacao,
    f.sg_federacao,

    -- candidato
    cand.cd_genero,
    g.ds_genero,

    cand.cd_grau_instrucao,
    gi.ds_grau_instrucao,

    cand.cd_cor_raca,
    cr.ds_cor_raca,

    cand.cd_estado_civil,
    ec.ds_estado_civil,

    cand.cd_ocupacao,
    oc.ds_ocupacao,

    EXTRACT(
        YEAR FROM AGE(
            e.dt_eleicao,
            cand.dt_nascimento
        )
    )::INT AS idade,

    -- situação
    c.cd_sit_tot_turno,
    st.ds_sit_tot_turno,

    c.cd_situacao_candidatura,
    sc.ds_situacao_candidatura,

    -- métricas
    1 AS qt_candidatos,

    CASE
        WHEN UPPER(st.ds_sit_tot_turno)
             LIKE '%ELEITO%'
        THEN 1
        ELSE 0
    END AS qt_eleitos

FROM candidatura c

INNER JOIN eleicao e
    ON e.cd_eleicao = c.cd_eleicao

INNER JOIN candidato cand
    ON cand.sq_candidato = c.sq_candidato

LEFT JOIN cargo cg
    ON cg.cd_cargo = c.cd_cargo

LEFT JOIN partido p
    ON p.nr_partido = c.nr_partido

LEFT JOIN federacao f
    ON f.nr_federacao = c.nr_federacao

LEFT JOIN genero g
    ON g.cd_genero = cand.cd_genero

LEFT JOIN grau_instrucao gi
    ON gi.cd_grau_instrucao = cand.cd_grau_instrucao

LEFT JOIN cor_raca cr
    ON cr.cd_cor_raca = cand.cd_cor_raca

LEFT JOIN estado_civil ec
    ON ec.cd_estado_civil = cand.cd_estado_civil

LEFT JOIN ocupacao oc
    ON oc.cd_ocupacao = cand.cd_ocupacao

LEFT JOIN situacao_turno st
    ON st.cd_sit_tot_turno = c.cd_sit_tot_turno

LEFT JOIN situacao_candidatura sc
    ON sc.cd_situacao_candidatura = c.cd_situacao_candidatura;
--
CREATE OR REPLACE VIEW fato_bens AS
SELECT

    b.id_bem,

    b.id_candidatura,

    e.cd_eleicao,
    e.ano_eleicao,

    c.sg_uf,
    c.cd_municipio_tse,

    c.cd_cargo,
    cg.ds_cargo,

    c.nr_partido,
    p.sg_partido,

    c.nr_federacao,
    f.sg_federacao,

    cand.cd_genero,
    g.ds_genero,

    cand.cd_grau_instrucao,
    gi.ds_grau_instrucao,

    cand.cd_cor_raca,
    cr.ds_cor_raca,

    b.cd_tipo_bem,
    tb.ds_tipo_bem,

    b.nr_ordem_bem,

    b.vr_bem,

    1 AS qt_bens

FROM bem_candidato b

INNER JOIN candidatura c
    ON c.id_candidatura = b.id_candidatura

INNER JOIN eleicao e
    ON e.cd_eleicao = c.cd_eleicao

INNER JOIN candidato cand
    ON cand.sq_candidato = c.sq_candidato

LEFT JOIN cargo cg
    ON cg.cd_cargo = c.cd_cargo

LEFT JOIN partido p
    ON p.nr_partido = c.nr_partido

LEFT JOIN federacao f
    ON f.nr_federacao = c.nr_federacao

LEFT JOIN genero g
    ON g.cd_genero = cand.cd_genero

LEFT JOIN grau_instrucao gi
    ON gi.cd_grau_instrucao = cand.cd_grau_instrucao

LEFT JOIN cor_raca cr
    ON cr.cd_cor_raca = cand.cd_cor_raca

LEFT JOIN tipo_bem tb
    ON tb.cd_tipo_bem = b.cd_tipo_bem;
--
--
--1. Taxa de Sucesso
CREATE OR REPLACE VIEW kpi_taxa_sucesso AS
SELECT
    ano_eleicao,
    sg_uf,
    SUM(qt_eleitos) AS eleitos,
    SUM(qt_candidatos) AS candidatos,
    ROUND(
        100.0 * SUM(qt_eleitos)
        / NULLIF(SUM(qt_candidatos),0)
    ,2) AS taxa_sucesso
FROM fato_eleicao
GROUP BY
    ano_eleicao,
    sg_uf;
--
--2. Percentual Feminino
CREATE OR REPLACE VIEW kpi_perc_feminino AS
SELECT
    ano_eleicao,
    sg_uf,

    ROUND(
        100.0 *
        SUM(
            CASE
                WHEN ds_genero = 'FEMININO'
                THEN 1
                ELSE 0
            END
        )
        / COUNT(*)
    ,2) AS perc_feminino

FROM fato_eleicao

GROUP BY
    ano_eleicao,
    sg_uf;
--
--3. Percentual Masculino
CREATE OR REPLACE VIEW kpi_perc_masculino AS
SELECT
    ano_eleicao,
    sg_uf,

    ROUND(
        100.0 *
        SUM(
            CASE
                WHEN ds_genero = 'MASCULINO'
                THEN 1
                ELSE 0
            END
        )
        / COUNT(*)
    ,2) AS perc_masculino

FROM fato_eleicao

GROUP BY
    ano_eleicao,
    sg_uf;
--
--4. Sucesso Feminino
CREATE OR REPLACE VIEW kpi_sucesso_feminino AS
SELECT
    ano_eleicao,
    sg_uf,

    COUNT(*) AS total_mulheres,

    SUM(qt_eleitos) AS mulheres_eleitas,

    ROUND(
        100.0 * SUM(qt_eleitos)
        / COUNT(*)
    ,2) AS taxa_sucesso_feminino

FROM fato_eleicao

WHERE ds_genero = 'FEMININO'

GROUP BY
    ano_eleicao,
    sg_uf;
--
--5. Sucesso Masculino
CREATE OR REPLACE VIEW kpi_sucesso_masculino AS
SELECT
    ano_eleicao,
    sg_uf,

    COUNT(*) AS total_homens,

    SUM(qt_eleitos) AS homens_eleitos,

    ROUND(
        100.0 * SUM(qt_eleitos)
        / COUNT(*)
    ,2) AS taxa_sucesso_masculino

FROM fato_eleicao

WHERE ds_genero = 'MASCULINO'

GROUP BY
    ano_eleicao,
    sg_uf;
--
--6. Eficiência por Partido
CREATE OR REPLACE VIEW kpi_eficiencia_partido AS
SELECT
    ano_eleicao,
    sg_uf,
    sg_partido,

    COUNT(*) AS candidatos,

    SUM(qt_eleitos) AS eleitos,

    ROUND(
        100.0 * SUM(qt_eleitos)
        / COUNT(*)
    ,2) AS eficiencia

FROM fato_eleicao

GROUP BY
    ano_eleicao,
    sg_uf,
    sg_partido;
--
--7. Partido com Mais Candidatos
CREATE OR REPLACE VIEW kpi_top_partido_candidatos AS
SELECT *
FROM (

    SELECT
        ano_eleicao,
        sg_uf,
        sg_partido,

        COUNT(*) AS total_candidatos,

        ROW_NUMBER() OVER(
            PARTITION BY
                ano_eleicao,
                sg_uf
            ORDER BY
                COUNT(*) DESC
        ) AS posicao

    FROM fato_eleicao

    GROUP BY
        ano_eleicao,
        sg_uf,
        sg_partido

) x

WHERE posicao = 1;
--
--8. Percentual Ensino Superior

CREATE OR REPLACE VIEW kpi_perc_superior AS
SELECT
    ano_eleicao,
    sg_uf,

    ROUND(
        100.0 *
        SUM(
            CASE
                WHEN ds_grau_instrucao ILIKE '%SUPERIOR%'
                THEN 1
                ELSE 0
            END
        )
        / COUNT(*)
    ,2) AS perc_superior

FROM fato_eleicao

GROUP BY
    ano_eleicao,
    sg_uf;
--
--9. Sucesso por Escolaridade
CREATE OR REPLACE VIEW kpi_sucesso_escolaridade AS
SELECT
    ano_eleicao,
    sg_uf,
    ds_grau_instrucao,

    COUNT(*) AS candidatos,

    SUM(qt_eleitos) AS eleitos,

    ROUND(
        100.0 * SUM(qt_eleitos)
        / COUNT(*)
    ,2) AS taxa_sucesso

FROM fato_eleicao

GROUP BY
    ano_eleicao,
    sg_uf,
    ds_grau_instrucao;
--
--10. Percentual por Raça
--
CREATE OR REPLACE VIEW kpi_perc_raca AS
SELECT
    ano_eleicao,
    sg_uf,
    ds_cor_raca,

    COUNT(*) AS candidatos,

    ROUND(
        100.0 * COUNT(*)
        /
        SUM(COUNT(*)) OVER(
            PARTITION BY
                ano_eleicao,
                sg_uf
        )
    ,2) AS percentual

FROM fato_eleicao

GROUP BY
    ano_eleicao,
    sg_uf,
    ds_cor_raca;
--
--11. Sucesso por Raça
CREATE OR REPLACE VIEW kpi_sucesso_raca AS
SELECT
    ano_eleicao,
    sg_uf,
    ds_cor_raca,

    COUNT(*) AS candidatos,

    SUM(qt_eleitos) AS eleitos,

    ROUND(
        100.0 * SUM(qt_eleitos)
        / COUNT(*)
    ,2) AS taxa_sucesso

FROM fato_eleicao

GROUP BY
    ano_eleicao,
    sg_uf,
    ds_cor_raca;
--
--12. Idade Média
CREATE OR REPLACE VIEW kpi_idade_media AS
SELECT
    ano_eleicao,
    sg_uf,

    ROUND(
        AVG(idade)
    ,2) AS idade_media

FROM fato_eleicao

GROUP BY
    ano_eleicao,
    sg_uf;
--
--13. Idade Média dos Eleitos
CREATE OR REPLACE VIEW kpi_idade_media_eleitos AS
SELECT
    ano_eleicao,
    sg_uf,

    ROUND(
        AVG(idade)
    ,2) AS idade_media_eleitos

FROM fato_eleicao

WHERE qt_eleitos = 1

GROUP BY
    ano_eleicao,
    sg_uf;
--
--14. Candidatos por Cargo
CREATE OR REPLACE VIEW kpi_candidatos_cargo AS
SELECT
    ano_eleicao,
    sg_uf,
    ds_cargo,

    COUNT(*) AS total_candidatos

FROM fato_eleicao

GROUP BY
    ano_eleicao,
    sg_uf,
    ds_cargo;
--
--15. Taxa de Sucesso por Cargo
CREATE OR REPLACE VIEW kpi_taxa_sucesso_cargo AS
SELECT
    ano_eleicao,
    sg_uf,
    ds_cargo,

    COUNT(*) AS candidatos,

    SUM(qt_eleitos) AS eleitos,

    ROUND(
        100.0 * SUM(qt_eleitos)
        / COUNT(*)
    ,2) AS taxa_sucesso

FROM fato_eleicao

GROUP BY
    ano_eleicao,
    sg_uf,
    ds_cargo;



