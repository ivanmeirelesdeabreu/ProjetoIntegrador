import pandas as pd
import glob
from pathlib import Path
from sqlalchemy import create_engine, text

# =========================
# CONEXÃO
# =========================

engine = create_engine(
    "postgresql+psycopg2://2422120019_Ivan:2422120019_Ivan@dataiesb.iesbtech.com.br:5432/2422120019_Ivan",
    connect_args={"options": "-csearch_path=eleicao"}
)

# =========================
# REGIÕES
# =========================

regioes = pd.DataFrame([
    {"nm_regiao": "Norte"},
    {"nm_regiao": "Nordeste"},
    {"nm_regiao": "Centro-Oeste"},
    {"nm_regiao": "Sudeste"},
    {"nm_regiao": "Sul"}
])

# =========================
# UFs
# =========================

ufs = pd.DataFrame([
    {"sg_uf": "AC", "nm_uf": "Acre", "nm_regiao": "Norte"},
    {"sg_uf": "AL", "nm_uf": "Alagoas", "nm_regiao": "Nordeste"},
    {"sg_uf": "AP", "nm_uf": "Amapá", "nm_regiao": "Norte"},
    {"sg_uf": "AM", "nm_uf": "Amazonas", "nm_regiao": "Norte"},
    {"sg_uf": "BA", "nm_uf": "Bahia", "nm_regiao": "Nordeste"},
    {"sg_uf": "CE", "nm_uf": "Ceará", "nm_regiao": "Nordeste"},
    {"sg_uf": "DF", "nm_uf": "Distrito Federal", "nm_regiao": "Centro-Oeste"},
    {"sg_uf": "ES", "nm_uf": "Espírito Santo", "nm_regiao": "Sudeste"},
    {"sg_uf": "GO", "nm_uf": "Goiás", "nm_regiao": "Centro-Oeste"},
    {"sg_uf": "MA", "nm_uf": "Maranhão", "nm_regiao": "Nordeste"},
    {"sg_uf": "MT", "nm_uf": "Mato Grosso", "nm_regiao": "Centro-Oeste"},
    {"sg_uf": "MS", "nm_uf": "Mato Grosso do Sul", "nm_regiao": "Centro-Oeste"},
    {"sg_uf": "MG", "nm_uf": "Minas Gerais", "nm_regiao": "Sudeste"},
    {"sg_uf": "PA", "nm_uf": "Pará", "nm_regiao": "Norte"},
    {"sg_uf": "PB", "nm_uf": "Paraíba", "nm_regiao": "Nordeste"},
    {"sg_uf": "PR", "nm_uf": "Paraná", "nm_regiao": "Sul"},
    {"sg_uf": "PE", "nm_uf": "Pernambuco", "nm_regiao": "Nordeste"},
    {"sg_uf": "PI", "nm_uf": "Piauí", "nm_regiao": "Nordeste"},
    {"sg_uf": "RJ", "nm_uf": "Rio de Janeiro", "nm_regiao": "Sudeste"},
    {"sg_uf": "RN", "nm_uf": "Rio Grande do Norte", "nm_regiao": "Nordeste"},
    {"sg_uf": "RS", "nm_uf": "Rio Grande do Sul", "nm_regiao": "Sul"},
    {"sg_uf": "RO", "nm_uf": "Rondônia", "nm_regiao": "Norte"},
    {"sg_uf": "RR", "nm_uf": "Roraima", "nm_regiao": "Norte"},
    {"sg_uf": "SC", "nm_uf": "Santa Catarina", "nm_regiao": "Sul"},
    {"sg_uf": "SP", "nm_uf": "São Paulo", "nm_regiao": "Sudeste"},
    {"sg_uf": "SE", "nm_uf": "Sergipe", "nm_regiao": "Nordeste"},
    {"sg_uf": "TO", "nm_uf": "Tocantins", "nm_regiao": "Norte"},
])

# =========================
# LER TODOS OS CSVs
# =========================

base_dir = Path(__file__).resolve().parent
caminho = base_dir / ".." / "data" / "raw" / "consulta_cand_2024" / "*.csv"

arquivos = glob.glob(str(caminho))

if not arquivos:
    raise FileNotFoundError(f"Nenhum CSV encontrado em: {caminho}")

lista_df = []

for arq in arquivos:
    print(f"Lendo: {arq}")
    
    df_temp = pd.read_csv(
        arq,
        sep=";",
        encoding="latin1",
        low_memory=False
    )

    lista_df.append(df_temp)

df = pd.concat(lista_df, ignore_index=True)

print(f"Total de registros: {len(df)}")

# =========================
# PADRONIZA COLUNAS
# =========================

df.columns = [col.lower() for col in df.columns]

# =========================
# DATAS
# =========================

df["dt_nascimento"] = pd.to_datetime(
    df["dt_nascimento"],
    format="%d/%m/%Y",
    errors="coerce"
)

df["dt_eleicao"] = pd.to_datetime(
    df["dt_eleicao"],
    format="%d/%m/%Y",
    errors="coerce"
)

# =========================
# UFs
# =========================

df["sg_uf"] = (
    df["sg_uf"]
    .fillna("")
    .astype(str)
    .str.strip()
    .str[:2]
)

df["sg_uf_nascimento"] = (
    df["sg_uf_nascimento"]
    .fillna("")
    .astype(str)
    .str.strip()
    .str[:2]
)

# =========================
# COLIGAÇÃO
# =========================

df["sq_coligacao"] = pd.to_numeric(
    df["sq_coligacao"],
    errors="coerce"
)

df = df.dropna(subset=["sq_coligacao"])

df["sq_coligacao"] = df["sq_coligacao"].astype("int64")

# =========================
# CAMPOS NUMÉRICOS
# =========================

campos_numericos = [
    "cd_eleicao",
    "nr_partido",
    "nr_federacao",
    "cd_cargo",
    "cd_genero",
    "cd_grau_instrucao",
    "cd_estado_civil",
    "cd_cor_raca",
    "cd_ocupacao",
    "cd_situacao_candidatura",
    "cd_sit_tot_turno"
]

for campo in campos_numericos:
    df[campo] = pd.to_numeric(df[campo], errors="coerce")

# =========================
# UPSERT EM LOTES
# =========================

def insert_ignore_batch(df, tabela, pk_cols, batch_size=50000):

    if df.empty:
        return

    schema = "eleicao"

    for i in range(0, len(df), batch_size):

        chunk = df.iloc[i:i+batch_size]

        temp_table = f"tmp_{tabela}"

        chunk.to_sql(
            temp_table,
            engine,
            if_exists='replace',
            index=False,
            schema=schema
        )

        cols = list(chunk.columns)

        colunas = ", ".join(cols)

        conflito = ", ".join(pk_cols)

        sql = f"""
            INSERT INTO {tabela} ({colunas})
            SELECT {colunas}
            FROM {temp_table}
            ON CONFLICT ({conflito}) DO NOTHING;

            DROP TABLE {temp_table};
        """

        with engine.begin() as conn:
            conn.execute(text(sql))

        print(f"Lote {i} até {i+batch_size} inserido em {tabela}")

# =========================
# UPSERT
# =========================

def insert_ignore(df, tabela, pk_cols):

    if df.empty:
        return

    schema = "eleicao"

    temp_table = f"tmp_{tabela}"

    df.to_sql(
        temp_table,
        engine,
        if_exists='replace',
        index=False,
        schema=schema
    )

    cols = list(df.columns)

    colunas = ", ".join(cols)

    conflito = ", ".join(pk_cols)

    sql = f"""
        INSERT INTO {tabela} ({colunas})
        SELECT {colunas}
        FROM {temp_table}
        ON CONFLICT ({conflito}) DO NOTHING;

        DROP TABLE {temp_table};
    """

    with engine.begin() as conn:
        conn.execute(text(sql))

    print(f"Inserido: {tabela}")

# =========================
# REGIÕES
# =========================

insert_ignore(
    regioes,
    "regiao",
    ["nm_regiao"]
)

# =========================
# IDS REGIÕES
# =========================

query_regioes = """
SELECT
    cd_regiao,
    nm_regiao
FROM regiao
"""

df_regioes = pd.read_sql(query_regioes, engine)

ufs = ufs.merge(
    df_regioes,
    on="nm_regiao",
    how="left"
)

# =========================
# UFs
# =========================

insert_ignore(
    ufs[[
        "sg_uf",
        "nm_uf",
        "cd_regiao"
    ]],
    "uf",
    ["sg_uf"]
)

# =========================
#  ELEIÇÃO
# =========================

insert_ignore(
    df[[
        "cd_eleicao",
        "ano_eleicao",
        "nm_tipo_eleicao",
        "nr_turno",
        "ds_eleicao",
        "dt_eleicao",
        "tp_abrangencia"
    ]].drop_duplicates(),
    "eleicao",
    ["cd_eleicao"]
)

# =========================
#  MUNICÍPIO
# =========================

municipios = df[[
    "sg_uf",
    "sg_ue",
    "nm_ue"
]].drop_duplicates()

municipios.columns = [
    "sg_uf",
    "sg_ue",
    "nm_municipio"
]

insert_ignore(
    municipios,
    "municipio",
    ["sg_uf", "sg_ue"]
)

# =========================
#  IDS MUNICÍPIOS
# =========================

query_municipios = """
SELECT
    cd_municipio,
    sg_uf,
    sg_ue
FROM municipio
"""

df_municipios = pd.read_sql(
    query_municipios,
    engine
)

# =========================
#  PADRONIZA TIPOS PARA MERGE
# =========================

df["sg_ue"] = (
    df["sg_ue"]
    .fillna("")
    .astype(str)
    .str.strip()
)

df_municipios["sg_ue"] = (
    df_municipios["sg_ue"]
    .fillna("")
    .astype(str)
    .str.strip()
)
# =========================
#  MERGE
# =========================

df = df.merge(
    df_municipios,
    on=["sg_uf", "sg_ue"],
    how="left"
)

# =========================
#  CARGO
# =========================

insert_ignore(
    df[[
        "cd_cargo",
        "ds_cargo"
    ]].drop_duplicates(),
    "cargo",
    ["cd_cargo"]
)

# =========================
#  PARTIDO
# =========================

insert_ignore(
    df[[
        "nr_partido",
        "sg_partido",
        "nm_partido"
    ]].drop_duplicates(),
    "partido",
    ["nr_partido"]
)

# =========================
#  FEDERAÇÃO
# =========================

insert_ignore(
    df[[
        "nr_federacao",
        "nm_federacao",
        "sg_federacao",
        "ds_composicao_federacao"
    ]].drop_duplicates(),
    "federacao",
    ["nr_federacao"]
)

# =========================
#  COLIGAÇÃO
# =========================

insert_ignore(
    df[[
        "sq_coligacao",
        "cd_eleicao",
        "cd_municipio",
        "nm_coligacao",
        "ds_composicao_coligacao"
    ]].drop_duplicates(),
    "coligacao",
    ["sq_coligacao", "cd_eleicao", "cd_municipio"]
)

# =========================
#  GENERO
# =========================

insert_ignore(
    df[[
        "cd_genero",
        "ds_genero"
    ]].drop_duplicates(),
    "genero",
    ["cd_genero"]
)

# =========================
#  GRAU INSTRUÇÃO
# =========================

insert_ignore(
    df[[
        "cd_grau_instrucao",
        "ds_grau_instrucao"
    ]].drop_duplicates(),
    "grau_instrucao",
    ["cd_grau_instrucao"]
)

# =========================
#  ESTADO CIVIL
# =========================

insert_ignore(
    df[[
        "cd_estado_civil",
        "ds_estado_civil"
    ]].drop_duplicates(),
    "estado_civil",
    ["cd_estado_civil"]
)

# =========================
#  COR RAÇA
# =========================

insert_ignore(
    df[[
        "cd_cor_raca",
        "ds_cor_raca"
    ]].drop_duplicates(),
    "cor_raca",
    ["cd_cor_raca"]
)

# =========================
#  OCUPAÇÃO
# =========================

insert_ignore(
    df[[
        "cd_ocupacao",
        "ds_ocupacao"
    ]].drop_duplicates(),
    "ocupacao",
    ["cd_ocupacao"]
)

# =========================
#  SITUAÇÃO CANDIDATURA
# =========================

insert_ignore(
    df[[
        "cd_situacao_candidatura",
        "ds_situacao_candidatura"
    ]].drop_duplicates(),
    "situacao_candidatura",
    ["cd_situacao_candidatura"]
)

# =========================
#  SITUAÇÃO TURNO
# =========================

insert_ignore(
    df[[
        "cd_sit_tot_turno",
        "ds_sit_tot_turno"
    ]].drop_duplicates(),
    "situacao_turno",
    ["cd_sit_tot_turno"]
)

# =========================
# CANDIDATO
# =========================

candidato = df[[
    "sq_candidato",
    "cd_eleicao",
    "cd_municipio",
    "cd_cargo",
    "nr_partido",
    "nr_federacao",
    "sq_coligacao",
    "nr_candidato",
    "nm_candidato",
    "nm_urna_candidato",
    "nm_social_candidato",
    "nr_cpf_candidato",
    "ds_email",
    "dt_nascimento",
    "sg_uf_nascimento",
    "nr_titulo_eleitoral_candidato",
    "cd_genero",
    "cd_grau_instrucao",
    "cd_estado_civil",
    "cd_cor_raca",
    "cd_ocupacao",
    "cd_situacao_candidatura",
    "cd_sit_tot_turno"
]].copy()

candidato.columns = [
    "sq_candidato",
    "cd_eleicao",
    "cd_municipio",
    "cd_cargo",
    "nr_partido",
    "nr_federacao",
    "sq_coligacao",
    "nr_candidato",
    "nm_candidato",
    "nm_urna",
    "nm_social",
    "nr_cpf",
    "ds_email",
    "dt_nascimento",
    "sg_uf_nascimento",
    "nr_titulo_eleitoral",
    "cd_genero",
    "cd_grau_instrucao",
    "cd_estado_civil",
    "cd_cor_raca",
    "cd_ocupacao",
    "cd_situacao_candidatura",
    "cd_sit_tot_turno"
]

insert_ignore_batch(
    candidato,
    "candidato",
    ["sq_candidato"]
)

print("ETL FINALIZADO COM SUCESSO!")
