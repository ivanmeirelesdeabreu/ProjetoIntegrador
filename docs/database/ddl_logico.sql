CREATE TABLE IF NOT EXISTS "eleicao" (
	"cd_eleicao" bigint NOT NULL UNIQUE,
	"ano_eleicao" bigint NOT NULL,
	"nm_tipo_eleicao" varchar(100) NOT NULL,
	"nr_turno" bigint NOT NULL,
	"ds_eleicao" varchar(150) NOT NULL,
	"dt_eleicao" date NOT NULL,
	"tp_abrangencia" varchar(50) NOT NULL,
	"sg_uf" varchar(2) NOT NULL,
	"sg_ue" varchar(10) NOT NULL,
	PRIMARY KEY ("cd_eleicao")
);



CREATE TABLE IF NOT EXISTS "municipio" (
	"sg_uf" varchar(2) NOT NULL,
	"sg_ue" varchar(10) NOT NULL,
	"nm_ue" varchar(150) NOT NULL,
	PRIMARY KEY ("sg_uf", "sg_ue")
);



CREATE TABLE IF NOT EXISTS "cargo" (
	"cd_cargo" bigint NOT NULL,
	"ds_cargo" varchar(100) NOT NULL,
	PRIMARY KEY ("cd_cargo")
);



CREATE TABLE IF NOT EXISTS "partido" (
	"nr_partido" bigint NOT NULL,
	"sg_partido" varchar(20) NOT NULL,
	"nm_partido" varchar(150) NOT NULL,
	PRIMARY KEY ("nr_partido")

);



CREATE TABLE IF NOT EXISTS "federacao" (
	"nr_federacao" bigint NOT NULL,
	"nm_federacao" varchar(150) NOT NULL,
	"sg_federacao" varchar(50) NOT NULL,
	"ds_composicao_federacao" varchar(255) NOT NULL,
	PRIMARY KEY ("nr_federacao")
);



CREATE TABLE IF NOT EXISTS "coligacao" (
	"sq_coligacao" bigint NOT NULL,
	"nm_coligacao" varchar(150) NOT NULL,
	"ds_composicao_coligacao" varchar(255) NOT NULL,
	PRIMARY KEY ("sq_coligacao")
);


CREATE TABLE IF NOT EXISTS "candidato" (
	"ds_cor_raca" varchar(50) NOT NULL,
	"ds_ocupacao" varchar(150) NOT NULL,
	"cd_sit_tot_turno" bigint NOT NULL,
	"cd_situacao_candidatura" bigint NOT NULL,
	"cd_ocupacao" bigint NOT NULL,
	"cd_cor_raca" bigint NOT NULL,
	"cd_estado_civil" bigint NOT NULL,
	"cd_grau_instrucao" bigint NOT NULL,
	"cd_genero" bigint NOT NULL,
	"nr_titulo_eleitoral" varchar(20) NOT NULL,
	"sg_uf_nascimento" varchar(2) NOT NULL,
	"dt_nascimento" date NOT NULL,
	"ds_email" varchar(150) NOT NULL,
	"nr_cpf" varchar(14) NOT NULL,
	"nm_social" varchar(150) NOT NULL,
	"nm_urna" varchar(150) NOT NULL,
	"nm_candidato" varchar(150) NOT NULL,
	"nr_candidato" bigint NOT NULL,
	"sq_coligacao" bigint NOT NULL,
	"nr_federacao" bigint NOT NULL,
	"nr_partido" bigint NOT NULL,
	"cd_cargo" bigint NOT NULL,
	"sg_ue" varchar(10) NOT NULL,
	"sg_uf" varchar(2) NOT NULL,
	"cd_eleicao" bigint NOT NULL,
	"sq_candidato" bigint NOT NULL,

	PRIMARY KEY ("sq_candidato")

);



CREATE TABLE IF NOT EXISTS "grau_instrucao" (
	"cd_grau_instrucao" bigint NOT NULL,
	"ds_grau_instrucao" varchar(100) NOT NULL,
	PRIMARY KEY ("cd_grau_instrucao")

);



CREATE TABLE IF NOT EXISTS "estado_civil" (
	"cd_estado_civil" bigint NOT NULL,
	"ds_estado_civil" varchar(50) NOT NULL,
	PRIMARY KEY ("cd_estado_civil")

);

ALTER TABLE "eleicao" ADD CONSTRAINT "eleicao_fk7" FOREIGN KEY ("sg_uf","sg_ue") REFERENCES "municipio"("sg_uf","sg_ue");
ALTER TABLE "candidato" ADD CONSTRAINT "candidato_fk6" FOREIGN KEY ("cd_estado_civil") REFERENCES "estado_civil"("cd_estado_civil");
ALTER TABLE "candidato" ADD CONSTRAINT "candidato_fk7" FOREIGN KEY ("cd_grau_instrucao") REFERENCES "grau_instrucao"("cd_grau_instrucao");
ALTER TABLE "candidato" ADD CONSTRAINT "candidato_fk18" FOREIGN KEY ("sq_coligacao") REFERENCES "coligacao"("sq_coligacao");
ALTER TABLE "candidato" ADD CONSTRAINT "candidato_fk19" FOREIGN KEY ("nr_federacao") REFERENCES "federacao"("nr_federacao");
ALTER TABLE "candidato" ADD CONSTRAINT "candidato_fk20" FOREIGN KEY ("nr_partido") REFERENCES "partido"("nr_partido");
ALTER TABLE "candidato" ADD CONSTRAINT "candidato_fk21" FOREIGN KEY ("cd_cargo") REFERENCES "cargo"("cd_cargo");
ALTER TABLE "candidato" ADD CONSTRAINT "candidato_fk24" FOREIGN KEY ("cd_eleicao") REFERENCES "eleicao"("cd_eleicao");