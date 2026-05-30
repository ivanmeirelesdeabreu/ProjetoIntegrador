-- =========================================
-- PROJETO: Análise de Candidatos TSE
-- DESCRIÇÃO: Criação do modelo relacional normalizado
-- =========================================

DROP SCHEMA IF EXISTS eleicao CASCADE;
CREATE SCHEMA eleicao;
SET search_path TO eleicao;


CREATE TABLE abrangencia (
    cd_abrangencia SERIAL PRIMARY KEY,
    tp_abrangencia VARCHAR(50) UNIQUE
);

CREATE TABLE eleicao (
    cd_eleicao bigint PRIMARY KEY,
    ano_eleicao INT,
    nm_tipo_eleicao VARCHAR(100),
    nr_turno INT,
    ds_eleicao VARCHAR(150),
    dt_eleicao DATE,
    cd_abrangencia INT,
    FOREIGN KEY (cd_abrangencia)
        REFERENCES abrangencia(cd_abrangencia)
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
    cd_municipio_tse bigint PRIMARY KEY,
    sg_uf CHAR(2),
    sg_ue VARCHAR(10),
    nm_municipio VARCHAR(150),

    FOREIGN KEY (sg_uf)
        REFERENCES uf(sg_uf)

);

CREATE TABLE cargo (
    cd_cargo INT PRIMARY KEY,
    ds_cargo VARCHAR(100)
);

CREATE TABLE partido (
    nr_partido INT PRIMARY KEY,
    sg_partido VARCHAR(20),
    nm_partido VARCHAR(150)
);

CREATE TABLE federacao (
    nr_federacao INT PRIMARY KEY,
    nm_federacao VARCHAR(150),
    sg_federacao VARCHAR(50),
    ds_composicao_federacao TEXT
);


CREATE TABLE genero (
    cd_genero INT PRIMARY KEY,
    ds_genero VARCHAR(50)
);


CREATE TABLE grau_instrucao (
    cd_grau_instrucao INT PRIMARY KEY,
    ds_grau_instrucao VARCHAR(100)
);

CREATE TABLE estado_civil (
    cd_estado_civil INT PRIMARY KEY,
    ds_estado_civil VARCHAR(50)
);

CREATE TABLE cor_raca (
    cd_cor_raca INT PRIMARY KEY,
    ds_cor_raca VARCHAR(50)
);

CREATE TABLE ocupacao (
    cd_ocupacao INT PRIMARY KEY,
    ds_ocupacao VARCHAR(150)
);

CREATE TABLE situacao_candidatura (
    cd_situacao_candidatura INT PRIMARY KEY,
    ds_situacao_candidatura VARCHAR(100)
);

CREATE TABLE situacao_turno (
    cd_sit_tot_turno INT PRIMARY KEY,
    ds_sit_tot_turno VARCHAR(100)
);


CREATE TABLE candidato (
	sq_candidato BIGINT PRIMARY KEY,
	
	nr_cpf_candidato VARCHAR(14),
	nm_candidato VARCHAR(200),

	nr_titulo_eleitoral VARCHAR(20),	
	cd_genero INT,	
	cd_estado_civil INT,
	cd_cor_raca INT,
	cd_ocupacao INT,	
	cd_grau_instrucao INT,
	dt_nascimento DATE,
	ds_email VARCHAR(150),	
	sg_uf_nascimento VARCHAR(2),
	cd_municipio_tse bigint NULL,
	sg_uf            VARCHAR(2) NULL,
	
    FOREIGN KEY (cd_municipio_tse) REFERENCES municipio(cd_municipio_tse),
    FOREIGN KEY (sg_uf) REFERENCES uf(sg_uf),
    FOREIGN KEY (cd_genero) REFERENCES genero(cd_genero),
    FOREIGN KEY (cd_estado_civil) REFERENCES estado_civil(cd_estado_civil),
    FOREIGN KEY (cd_grau_instrucao) REFERENCES grau_instrucao(cd_grau_instrucao),
    FOREIGN KEY (cd_cor_raca) REFERENCES cor_raca(cd_cor_raca),
    FOREIGN KEY (cd_ocupacao) REFERENCES ocupacao(cd_ocupacao)
);

      
CREATE TABLE candidatura (
    id_candidatura               BIGSERIAL PRIMARY KEY,
    sq_candidato                 BIGINT NOT NULL,
    cd_eleicao                   BIGINT NOT NULL,
    nr_turno                     INT NOT NULL,
    cd_cargo                     INT,
    nr_candidato                 VARCHAR(20),
    nr_federacao                 INT,
    nm_urna_candidato            VARCHAR(200),
    nr_partido                   INT,
    sg_uf                        VARCHAR(2) NULL,
    sg_ue                        VARCHAR(10),
    nm_ue 						 VARCHAR(200),
    cd_municipio_tse             bigint NULL,
    cd_situacao_candidatura      INT,
    cd_sit_tot_turno             INT,
    st_candidato_inserido_urna   VARCHAR(10),
    sq_coligacao                 BIGINT,	

    FOREIGN KEY (sq_candidato) REFERENCES candidato(sq_candidato),
    FOREIGN KEY (cd_municipio_tse) REFERENCES municipio(cd_municipio_tse),
    FOREIGN KEY (sg_uf) REFERENCES uf(sg_uf),
    FOREIGN KEY (cd_cargo) REFERENCES cargo(cd_cargo),
    FOREIGN KEY (nr_partido) REFERENCES partido(nr_partido),
    FOREIGN KEY (cd_eleicao) REFERENCES eleicao(cd_eleicao),
    FOREIGN KEY (cd_situacao_candidatura) REFERENCES situacao_candidatura(cd_situacao_candidatura),   
    FOREIGN KEY (nr_federacao) REFERENCES federacao(nr_federacao),
    FOREIGN KEY(cd_sit_tot_turno) REFERENCES situacao_turno(cd_sit_tot_turno),

    CONSTRAINT uk_candidatura UNIQUE (
        sq_candidato,
        cd_eleicao,
        nr_turno,
        cd_cargo
    )
);       


CREATE TABLE tipo_bem (
    cd_tipo_bem INT PRIMARY KEY,
    ds_tipo_bem VARCHAR(200)
);


CREATE TABLE bem_candidato (
    id_bem SERIAL PRIMARY KEY,
    id_candidatura BIGINT,    
    sq_candidato  BIGINT,
    cd_eleicao    bigint,    
    nr_ordem_bem INT NOT NULL,
    cd_tipo_bem INT,
    ds_bem TEXT,
    vr_bem NUMERIC(18,2),
    dt_ultima_atualizacao DATE,

    FOREIGN KEY (id_candidatura) REFERENCES candidatura(id_candidatura),
    FOREIGN KEY (cd_tipo_bem) REFERENCES tipo_bem(cd_tipo_bem),    
    CONSTRAINT uk_bem_candidatura UNIQUE (id_candidatura, nr_ordem_bem)

);
commit
