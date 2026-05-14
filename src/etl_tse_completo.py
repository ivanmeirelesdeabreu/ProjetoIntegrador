"""
============================================================
ETL TSE – Candidatos e Bens (Multi-ano / Multi-UF)
Autor: Ivan Abreu, André Fraga e João Felipe
Descrição:
    - Importa candidatos de eleições passadas (multi-ano)
    - Importa bens declarados por candidatos (multi-ano)
    - Executa carga em blocos (batch) para grandes volumes
    - Modelo relacional normalizado (PostgreSQL)
============================================================
"""

import pandas as pd
import glob
import time
import uuid

from pathlib import Path
from sqlalchemy import create_engine, text

# =========================================
# CONEXÃO
# =========================================

engine = create_engine(
    "postgresql+psycopg2://2422120019_Ivan:2422120019_Ivan@dataiesb.iesbtech.com.br:5432/2422120019_Ivan",
    connect_args={"options": "-csearch_path=eleicao"}
)

# =========================================
# PASTAS DINÂMICAS
# =========================================

BASE_DIR = Path(__file__).resolve().parent

RAW_DIR = BASE_DIR / ".." / "data" / "raw"

PASTAS_CANDIDATOS = [
    pasta for pasta in RAW_DIR.iterdir()
    if pasta.is_dir() and pasta.name.startswith("consulta_cand_")
]

PASTAS_BENS = [
    pasta for pasta in RAW_DIR.iterdir()
    if pasta.is_dir() and pasta.name.startswith("bem_candidato_")
]

print("\nPastas de candidatos encontradas:")
for p in PASTAS_CANDIDATOS:
    print(p)

print("\nPastas de bens encontradas:")
for p in PASTAS_BENS:
    print(p)

# =========================================
# REGIÕES
# =========================================

regioes = pd.DataFrame([
    {"nm_regiao": "Norte"},
    {"nm_regiao": "Nordeste"},
    {"nm_regiao": "Centro-Oeste"},
    {"nm_regiao": "Sudeste"},
    {"nm_regiao": "Sul"}
])

# =========================================
# UFs
# =========================================

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
    {"sg_uf": "BR", "nm_uf": "Brasil", "nm_regiao": "Norte"},
    {"sg_uf": "ZZ", "nm_uf": "Exterior", "nm_regiao": "Norte"},
    {"sg_uf": "VT", "nm_uf": "Voto em trânsito", "nm_regiao": "Norte"},
])

# =========================================
# LIMPEZA TSE
# =========================================

def limpar_valores_tse(df):

    # valores realmente nulos
    df = df.replace("#NULO", None)
    df = df.replace("-1", None)

    # texto não existente
    df = df.replace("#NE", None)

    return df

# =========================================
# UPSERT RÁPIDO
# =========================================

def insert_ignore(df, tabela, pk_cols):

    if df.empty:
        return

    schema = "eleicao"

    temp_table = f"tmp_{tabela}_{uuid.uuid4().hex[:8]}"

    print(f"Inserindo {len(df)} registros em {tabela}")

    inicio = time.time()

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
        INSERT INTO {schema}.{tabela} ({colunas})
        SELECT {colunas}
        FROM {schema}.{temp_table}
        ON CONFLICT ({conflito}) DO NOTHING
    """

    with engine.begin() as conn:
        conn.execute(text(sql))
        conn.execute(text(f"DROP TABLE {schema}.{temp_table}"))

    fim = time.time()

    print(f"{tabela} concluído em {fim - inicio:.2f} segundos")

# =========================================
# INSERT EM LOTES
# =========================================

def insert_ignore_batch(df, tabela, pk_cols, batch_size=50000):

    total = len(df)

    for i in range(0, total, batch_size):

        chunk = df.iloc[i:i+batch_size]

        print(f"[{tabela}] Inserindo {i+1} até {min(i+batch_size, total)}")

        insert_ignore(chunk, tabela, pk_cols)

# =========================================
# CARREGAR CANDIDATOS
# =========================================

def carregar_candidatos():

    dfs = []

    for pasta in PASTAS_CANDIDATOS:

        arquivos = glob.glob(str(pasta / "*.csv"))

        for arq in arquivos:

            print(f"Lendo candidatos: {arq}")

            df_temp = pd.read_csv(
                arq,
                sep=";",
                encoding="latin1",
                low_memory=False,
                dtype=str
            )

            df_temp.columns = [c.lower() for c in df_temp.columns]

            df_temp = limpar_valores_tse(df_temp)

            dfs.append(df_temp)

    df = pd.concat(dfs, ignore_index=True)

    print(f"Total candidatos carregados: {len(df)}")

    # Datas

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

    # UFs

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

    # Numéricos

    campos_numericos = [
        "ano_eleicao",
        "cd_eleicao",
        "nr_turno",
        "cd_cargo",
        "sq_candidato",
        "nr_candidato",
        "nr_partido",
        "nr_federacao",
        "sq_coligacao",
        "cd_genero",
        "cd_grau_instrucao",
        "cd_estado_civil",
        "cd_cor_raca",
        "cd_ocupacao",
        "cd_situacao_candidatura",
        "cd_sit_tot_turno"
    ]

    for campo in campos_numericos:

        if campo in df.columns:
            df[campo] = pd.to_numeric(
                df[campo],
                errors="coerce"
            )

    return df

# =========================================
# CARREGAR BENS
# =========================================

def carregar_bens():

    dfs = []

    for pasta in PASTAS_BENS:

        arquivos = glob.glob(str(pasta / "*.csv"))

        for arq in arquivos:

            print(f"Lendo bens: {arq}")

            df_temp = pd.read_csv(
                arq,
                sep=";",
                encoding="latin1",
                low_memory=False,
                dtype=str
            )

            df_temp.columns = [c.lower() for c in df_temp.columns]

            df_temp = limpar_valores_tse(df_temp)

            dfs.append(df_temp)

    df = pd.concat(dfs, ignore_index=True)

    print(f"Total bens carregados: {len(df)}")

    campos_num = [
        "ano_eleicao",
        "sq_candidato",
        "nr_ordem_bem_candidato",
        "cd_tipo_bem_candidato"
    ]

    df["cd_tipo_bem_candidato"] = pd.to_numeric(
    df["cd_tipo_bem_candidato"],
    errors="coerce"
    )

    df["nr_ordem_bem_candidato"] = pd.to_numeric(
        df["nr_ordem_bem_candidato"],
        errors="coerce"
    )

    for campo in campos_num:

        if campo in df.columns:
            df[campo] = pd.to_numeric(
                df[campo],
                errors="coerce"
            )

    if "vr_bem_candidato" in df.columns:

        df["vr_bem_candidato"] = (
            df["vr_bem_candidato"]
            .astype(str)
            .str.replace(",", ".", regex=False)
        )

        df["vr_bem_candidato"] = pd.to_numeric(
            df["vr_bem_candidato"],
            errors="coerce"
        )

    if "dt_ultima_atualizacao" in df.columns:

        df["dt_ultima_atualizacao"] = pd.to_datetime(
            df["dt_ultima_atualizacao"],
            format="%d/%m/%Y",
            errors="coerce"
        )

    return df

# =========================================
# MAIN
# =========================================

def main():

    inicio_total = time.time()

    # =====================================
    # CANDIDATOS
    # =====================================

    df = carregar_candidatos()

    # =====================================
    # REGIÃO
    # =====================================

    insert_ignore(
        regioes,
        "regiao",
        ["nm_regiao"]
    )

    # =====================================
    # UF
    # =====================================

    regioes_db = pd.read_sql(
        "SELECT * FROM eleicao.regiao",
        engine
    )

    ufs_merge = ufs.merge(
        regioes_db,
        on="nm_regiao",
        how="left"
    )

    insert_ignore(
        ufs_merge[[
            "sg_uf",
            "nm_uf",
            "cd_regiao"
        ]],
        "uf",
        ["sg_uf"]
    )

    # =====================================
    # ELEIÇÃO
    # =====================================

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

    # =====================================
    # MUNICÍPIO
    # =====================================

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

    # =====================================
    # IDS MUNICÍPIOS
    # =====================================

    df_municipios = pd.read_sql(
        """
        SELECT
            cd_municipio,
            sg_uf,
            sg_ue
        FROM eleicao.municipio
        """,
        engine
    )

    # =====================================
    # PADRONIZA SG_UE PARA O MERGE
    # =====================================

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

    # =====================================
    # MERGE MUNICÍPIOS
    # =====================================

    df = df.merge(
        df_municipios,
        on=["sg_uf", "sg_ue"],
        how="left"
    )

    print("Municípios não encontrados:", df["cd_municipio"].isna().sum())

    # =====================================
    # DIMENSÕES
    # =====================================

    dimensoes = [

        ("cargo",
        ["cd_cargo", "ds_cargo"],
        ["cd_cargo"]),

        ("partido",
        ["nr_partido", "sg_partido", "nm_partido"],
        ["nr_partido"]),

        ("federacao",
        [
            "nr_federacao",
            "nm_federacao",
            "sg_federacao",
            "ds_composicao_federacao"
        ],
        ["nr_federacao"]),

        ("genero",
        ["cd_genero", "ds_genero"],
        ["cd_genero"]),

        ("grau_instrucao",
        ["cd_grau_instrucao", "ds_grau_instrucao"],
        ["cd_grau_instrucao"]),

        ("estado_civil",
        ["cd_estado_civil", "ds_estado_civil"],
        ["cd_estado_civil"]),

        ("cor_raca",
        ["cd_cor_raca", "ds_cor_raca"],
        ["cd_cor_raca"]),

        ("ocupacao",
        ["cd_ocupacao", "ds_ocupacao"],
        ["cd_ocupacao"]),

        ("situacao_candidatura",
        [
            "cd_situacao_candidatura",
            "ds_situacao_candidatura"
        ],
        ["cd_situacao_candidatura"]),

        ("situacao_turno",
        [
            "cd_sit_tot_turno",
            "ds_sit_tot_turno"
        ],
        ["cd_sit_tot_turno"]),
    ]

    for tabela, cols, pk in dimensoes:

        dados = df[cols].drop_duplicates()
        # Remove PKs nulas
        dados = dados.dropna(subset=pk)

        insert_ignore(
            dados,
            tabela,
            pk
        )

    # =====================================
    # COLIGAÇÃO
    # =====================================

    coligacao = df[[
    "sq_coligacao",
    "cd_eleicao",
    "cd_municipio",
    "nm_coligacao",
    "ds_composicao_coligacao"
    ]].drop_duplicates()

    coligacao = coligacao.dropna(
        subset=[
            "sq_coligacao",
            "cd_eleicao",
            "cd_municipio"
        ]
    )

    insert_ignore(
        coligacao,
        "coligacao",
        ["sq_coligacao", "cd_eleicao", "cd_municipio"]
    )

    # =====================================
    # CANDIDATO
    # =====================================

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
    
    candidato = candidato.dropna(subset=["sq_candidato"])

    #print(candidato.isnull().sum())

    insert_ignore_batch(
        candidato,
        "candidato",
        ["sq_candidato"]
    )

    # =====================================
    # BENS
    # =====================================

    df_bens = carregar_bens()

    # =====================================
    # TIPO BEM
    # =====================================

    tipo_bem = df_bens[[
        "cd_tipo_bem_candidato",
        "ds_tipo_bem_candidato"
    ]].drop_duplicates().copy()

    tipo_bem.columns = [
        "cd_tipo_bem",
        "ds_tipo_bem"
    ]

    tipo_bem = tipo_bem.dropna(subset=["cd_tipo_bem"])

    insert_ignore(
        tipo_bem,
        "tipo_bem",
        ["cd_tipo_bem"]
    )

    # =====================================
    # BEM CANDIDATO
    # =====================================

    bem = df_bens[[
        "sq_candidato",
        "ano_eleicao",
        "nr_ordem_bem_candidato",
        "cd_tipo_bem_candidato",
        "ds_bem_candidato",
        "vr_bem_candidato",
        "dt_ult_atual_bem_candidato"
    ]].copy()

    bem.columns = [
        "sq_candidato",
        "ano_eleicao",
        "nr_ordem_bem",
        "cd_tipo_bem",
        "ds_bem",
        "vr_bem",
        "dt_ultima_atualizacao"
    ]

    # =====================================
    # TIPOS
    # =====================================

    bem["vr_bem"] = (
        bem["vr_bem"]
        .astype(str)
        .str.replace(",", ".", regex=False)
    )

    bem["vr_bem"] = pd.to_numeric(
        bem["vr_bem"],
        errors="coerce"
    )

    bem["dt_ultima_atualizacao"] = pd.to_datetime(
        bem["dt_ultima_atualizacao"],
        format="%d/%m/%Y",
        errors="coerce"
    )

    # =====================================
    # REMOVE CANDIDATOS INEXISTENTES
    # =====================================

    sq_candidatos = pd.read_sql(
        "SELECT sq_candidato FROM eleicao.candidato",
        engine
    )

    bem = bem.merge(
        sq_candidatos,
        on="sq_candidato",
        how="inner"
    )

    # =====================================
    # INSERT
    # =====================================

    insert_ignore_batch(
        bem,
        "bem_candidato",
        ["sq_candidato", "ano_eleicao", "nr_ordem_bem"]
    )

    fim_total = time.time()

    print("\n====================================")
    print("ETL FINALIZADO COM SUCESSO")
    print(f"Tempo total: {fim_total - inicio_total:.2f} segundos")
    print("====================================")

# =========================================
# EXECUÇÃO
# =========================================

if __name__ == "__main__":
    main()