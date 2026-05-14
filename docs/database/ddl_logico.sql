-- =========================================
-- PROJETO: Análise de Candidatos TSE
-- DESCRIÇÃO: Criação do modelo relacional normalizado
-- =========================================

DROP SCHEMA IF EXISTS eleicao CASCADE;
CREATE SCHEMA eleicao;
SET search_path TO eleicao;


CREATE TABLE eleicao (
    cd_eleicao bigint PRIMARY KEY,
    ano_eleicao bigint,
    nm_tipo_eleicao VARCHAR(100),
    nr_turno bigint,
    ds_eleicao VARCHAR(150),
    dt_eleicao DATE,
    tp_abrangencia VARCHAR(50)
);

CREATE TABLE regiao (
    cd_regiao SERIAL PRIMARY KEY,
    nm_regiao VARCHAR(30) UNIQUE
);

CREATE TABLE uf (
    sg_uf CHAR(2) PRIMARY KEY,
    nm_uf VARCHAR(50),
    cd_regiao INT,

    FOREIGN KEY (cd_regiao)
        REFERENCES regiao(cd_regiao)
);

CREATE TABLE municipio (
    cd_municipio SERIAL PRIMARY KEY,

    sg_uf CHAR(2),
    sg_ue VARCHAR(10),
    nm_municipio VARCHAR(150),

    FOREIGN KEY (sg_uf)
        REFERENCES uf(sg_uf),

    UNIQUE (sg_uf, sg_ue)
);

CREATE TABLE cargo (
    cd_cargo bigint PRIMARY KEY,
    ds_cargo VARCHAR(100)
);

CREATE TABLE partido (
    nr_partido bigint PRIMARY KEY,
    sg_partido VARCHAR(20),
    nm_partido VARCHAR(150)
);

CREATE TABLE federacao (
    nr_federacao bigint PRIMARY KEY,
    nm_federacao VARCHAR(150),
    sg_federacao VARCHAR(50),
    ds_composicao_federacao TEXT
);

CREATE TABLE coligacao (
    sq_coligacao BIGINT,
    cd_eleicao bigint,
    cd_municipio bigint,
    nm_coligacao VARCHAR(150),
    ds_composicao_coligacao TEXT,
    PRIMARY KEY (sq_coligacao, cd_eleicao, cd_municipio),

    FOREIGN KEY (cd_eleicao) REFERENCES eleicao(cd_eleicao),
    FOREIGN KEY (cd_municipio) REFERENCES municipio(cd_municipio)
);

CREATE TABLE genero (
    cd_genero bigint PRIMARY KEY,
    ds_genero VARCHAR(50)
);


CREATE TABLE grau_instrucao (
    cd_grau_instrucao bigint PRIMARY KEY,
    ds_grau_instrucao VARCHAR(100)
);

CREATE TABLE estado_civil (
    cd_estado_civil bigint PRIMARY KEY,
    ds_estado_civil VARCHAR(50)
);

CREATE TABLE cor_raca (
    cd_cor_raca bigint PRIMARY KEY,
    ds_cor_raca VARCHAR(50)
);

CREATE TABLE ocupacao (
    cd_ocupacao bigint PRIMARY KEY,
    ds_ocupacao VARCHAR(150)
);

CREATE TABLE situacao_candidatura (
    cd_situacao_candidatura bigint PRIMARY KEY,
    ds_situacao_candidatura VARCHAR(100)
);

CREATE TABLE situacao_turno (
    cd_sit_tot_turno bigint PRIMARY KEY,
    ds_sit_tot_turno VARCHAR(100)
);

CREATE TABLE candidato (
    sq_candidato BIGINT PRIMARY KEY,
    
    cd_eleicao bigint,
    cd_municipio bigint,

    cd_cargo bigint,
    nr_partido bigint,
    nr_federacao bigint,
    sq_coligacao bigint,
    
    nr_candidato INT,
    nm_candidato VARCHAR(150),
    nm_urna VARCHAR(150),
    nm_social VARCHAR(150),
    nr_cpf VARCHAR(14),
    ds_email VARCHAR(150),
    
    dt_nascimento DATE,
    sg_uf_nascimento CHAR(2),
    nr_titulo_eleitoral VARCHAR(20),
    
    cd_genero bigint,
    cd_grau_instrucao bigint,
    cd_estado_civil bigint,
    cd_cor_raca bigint,
    cd_ocupacao bigint,
    
    cd_situacao_candidatura bigint,
    cd_sit_tot_turno bigint,

    FOREIGN KEY (cd_eleicao) REFERENCES eleicao(cd_eleicao),
    FOREIGN KEY (cd_municipio) REFERENCES municipio(cd_municipio),
    FOREIGN KEY (cd_cargo) REFERENCES cargo(cd_cargo),
    FOREIGN KEY (nr_partido) REFERENCES partido(nr_partido),
    FOREIGN KEY (nr_federacao) REFERENCES federacao(nr_federacao),
    FOREIGN KEY (sq_coligacao, cd_eleicao, cd_municipio) REFERENCES coligacao(sq_coligacao, cd_eleicao, cd_municipio),
    FOREIGN KEY (cd_genero) REFERENCES genero(cd_genero),
    FOREIGN KEY (cd_grau_instrucao) REFERENCES grau_instrucao(cd_grau_instrucao),
    FOREIGN KEY (cd_estado_civil) REFERENCES estado_civil(cd_estado_civil),
    FOREIGN KEY (cd_cor_raca) REFERENCES cor_raca(cd_cor_raca),
    FOREIGN KEY (cd_ocupacao) REFERENCES ocupacao(cd_ocupacao),
    FOREIGN KEY (cd_situacao_candidatura) REFERENCES situacao_candidatura(cd_situacao_candidatura),
    FOREIGN KEY (cd_sit_tot_turno) REFERENCES situacao_turno(cd_sit_tot_turno)
);

CREATE TABLE tipo_bem (
    cd_tipo_bem bigint PRIMARY KEY,
    ds_tipo_bem VARCHAR(200)
);

CREATE TABLE bem_candidato (
    id_bem SERIAL PRIMARY KEY,
    sq_candidato BIGINT,
    ano_eleicao INT,
    nr_ordem_bem INT,
    cd_tipo_bem BIGINT,
    ds_bem TEXT,
    vr_bem NUMERIC(18,2),
    dt_ultima_atualizacao DATE,

    FOREIGN KEY (sq_candidato)
        REFERENCES candidato(sq_candidato),

    FOREIGN KEY (cd_tipo_bem)
        REFERENCES tipo_bem(cd_tipo_bem),

    UNIQUE (sq_candidato, ano_eleicao, nr_ordem_bem)
);


CREATE INDEX idx_candidato_partido
ON eleicao.candidato(nr_partido);

CREATE INDEX idx_candidato_municipio
ON eleicao.candidato(cd_municipio);

CREATE INDEX idx_bem_candidato
ON eleicao.bem_candidato(sq_candidato);