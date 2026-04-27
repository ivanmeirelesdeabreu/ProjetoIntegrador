import pandas as pd
import glob
from pathlib import Path
from sqlalchemy import create_engine, text

# =========================
# 🔌 CONEXÃO
# =========================
engine = create_engine(
    "postgresql+psycopg2://2422120019_Ivan:2422120019_Ivan@dataiesb.iesbtech.com.br:5432/2422120019_Ivan",
    connect_args={"options": "-csearch_path=eleicao"}
)

# =========================
# 📂 LER TODOS OS CSVs
# =========================
base_dir = Path(__file__).resolve().parent
caminho = base_dir / ".." / "data" / "raw" / "consulta_cand_2024" / "*.csv"
arquivos = glob.glob(str(caminho))

if not arquivos:
    raise FileNotFoundError(f"Nenhum CSV encontrado em: {caminho}")

lista_df = []

for arq in arquivos:
    print(f"📥 Lendo: {arq}")
    df_temp = pd.read_csv(arq, sep=";", encoding="latin1")
    lista_df.append(df_temp)


df = pd.concat(lista_df, ignore_index=True)

print(f"✅ Total de registros: {len(df)}")

# =========================
# 🔥 PADRONIZA COLUNAS (ESSENCIAL)
# =========================
df.columns = [col.lower() for col in df.columns]

# =========================
# 🔧 TRATAMENTO DE DATAS
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

#df["dt_eleicao"] = pd.to_datetime(df["dt_eleicao"], errors="coerce")
#df["dt_nascimento"] = pd.to_datetime(df["dt_nascimento"], errors="coerce")

# =========================
# 🔧 TRATAMENTO UFS
# =========================
df["sg_uf"] = df["sg_uf"].fillna("").astype(str).str.strip().str[:2]
df["sg_uf_nascimento"] = df["sg_uf_nascimento"].fillna("").astype(str).str.strip().str[:2]

# =========================
# 🔧 TRATAMENTO para COLIGAÇÃO
# =========================
df["sq_coligacao"] = pd.to_numeric(df["sq_coligacao"], errors="coerce")
df = df.dropna(subset=["sq_coligacao"])

df["sq_coligacao"] = df["sq_coligacao"].astype("int64")
#df["sq_coligacao"] = pd.to_numeric(df["sq_coligacao"], errors="coerce")

# =========================
# 🔧 TRATAMENTO para COLUNAS NUMÉRICAS
# =========================

df["cd_eleicao"] = pd.to_numeric(df["cd_eleicao"], errors="coerce")
df["nr_partido"] = pd.to_numeric(df["nr_partido"], errors="coerce")
df["nr_federacao"] = pd.to_numeric(df["nr_federacao"], errors="coerce")
df["cd_cargo"] = pd.to_numeric(df["cd_cargo"], errors="coerce")
df["cd_genero"] = pd.to_numeric(df["cd_genero"], errors="coerce")
df["cd_grau_instrucao"] = pd.to_numeric(df["cd_grau_instrucao"], errors="coerce")
df["cd_estado_civil"] = pd.to_numeric(df["cd_estado_civil"], errors="coerce")
df["cd_cor_raca"] = pd.to_numeric(df["cd_cor_raca"], errors="coerce")
df["cd_ocupacao"] = pd.to_numeric(df["cd_ocupacao"], errors="coerce")
df["cd_situacao_candidatura"] = pd.to_numeric(df["cd_situacao_candidatura"], errors="coerce")
df["cd_sit_tot_turno"] = pd.to_numeric(df["cd_sit_tot_turno"], errors="coerce")

# =========================
# 🔁 FUNÇÃO UPSERT
# =========================
def insert_ignore(df, tabela, pk_cols):
    if df.empty:
        return
    
    schema = "eleicao"
    temp_table = f"tmp_{tabela}"

    df.to_sql(temp_table, engine, if_exists='replace', index=False, schema=schema)

    cols = list(df.columns)
    colunas = ", ".join(cols)
    conflito = ", ".join(pk_cols)

    sql = f"""
        INSERT INTO {tabela} ({colunas})
        SELECT {colunas} FROM {temp_table}
        ON CONFLICT ({conflito}) DO NOTHING;
        
        DROP TABLE {temp_table};
    """

    with engine.begin() as conn:
        conn.execute(text(sql))

    print(f"✅ Inserido: {tabela}")

# =========================
# 📌 DIMENSÕES
# =========================

insert_ignore(
    df[["cd_eleicao","ano_eleicao","nm_tipo_eleicao","nr_turno","ds_eleicao","dt_eleicao","tp_abrangencia"]]
    .drop_duplicates(),
    "eleicao",
    ["cd_eleicao"]
)

insert_ignore(
    df[["sg_uf","sg_ue","nm_ue"]].drop_duplicates(),
    "municipio",
    ["sg_uf","sg_ue"]
)

insert_ignore(
    df[["cd_cargo","ds_cargo"]].drop_duplicates(),
    "cargo",
    ["cd_cargo"]
)

insert_ignore(
    df[["nr_partido","sg_partido","nm_partido"]].drop_duplicates(),
    "partido",
    ["nr_partido"]
)

insert_ignore(
    df[["nr_federacao","nm_federacao","sg_federacao","ds_composicao_federacao"]]
    .drop_duplicates(),
    "federacao",
    ["nr_federacao"]
)

#insert_ignore(
#    df[["sq_coligacao","nm_coligacao","ds_composicao_coligacao"]]
#    .drop_duplicates(),
#    "coligacao",
#    ["sq_coligacao"]
#)

insert_ignore(
    df[[
        "sq_coligacao",
        "cd_eleicao",
        "sg_uf",
        "sg_ue",
        "nm_coligacao",
        "ds_composicao_coligacao"
    ]].drop_duplicates(),
    "coligacao",
    ["sq_coligacao","cd_eleicao","sg_uf","sg_ue"]
)

insert_ignore(
    df[["cd_genero","ds_genero"]].drop_duplicates(),
    "genero",
    ["cd_genero"]
)

insert_ignore(
    df[["cd_grau_instrucao","ds_grau_instrucao"]].drop_duplicates(),
    "grau_instrucao",
    ["cd_grau_instrucao"]
)

insert_ignore(
    df[["cd_estado_civil","ds_estado_civil"]].drop_duplicates(),
    "estado_civil",
    ["cd_estado_civil"]
)

insert_ignore(
    df[["cd_cor_raca","ds_cor_raca"]].drop_duplicates(),
    "cor_raca",
    ["cd_cor_raca"]
)

insert_ignore(
    df[["cd_ocupacao","ds_ocupacao"]].drop_duplicates(),
    "ocupacao",
    ["cd_ocupacao"]
)

insert_ignore(
    df[["cd_situacao_candidatura","ds_situacao_candidatura"]].drop_duplicates(),
    "situacao_candidatura",
    ["cd_situacao_candidatura"]
)

insert_ignore(
    df[["cd_sit_tot_turno","ds_sit_tot_turno"]].drop_duplicates(),
    "situacao_turno",
    ["cd_sit_tot_turno"]
)

# =========================
# 📌 FATO - CANDIDATO
# =========================

candidato = df[[
    "sq_candidato",
    "cd_eleicao",
    "sg_uf",
    "sg_ue",
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
    "sg_uf",
    "sg_ue",
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

insert_ignore(candidato, "candidato", ["sq_candidato"])

print("🚀 ETL finalizado com sucesso!")