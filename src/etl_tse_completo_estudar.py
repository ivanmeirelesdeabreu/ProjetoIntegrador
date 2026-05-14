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

# ============================================================
# 1. IMPORTAÇÕES
# ============================================================

import pandas as pd
import glob
from pathlib import Path
from sqlalchemy import create_engine, text
import time

# ============================================================
# 2. CONEXÃO COM O BANCO
# ============================================================

engine = create_engine(
    "postgresql+psycopg2://2422120019_Ivan:2422120019_Ivan@dataiesb.iesbtech.com.br:5432/2422120019_Ivan",
    connect_args={"options": "-csearch_path=eleicao"}
)

# ============================================================
# 3. DIRETÓRIOS DE DADOS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
RAW_DIR = BASE_DIR / ".." / "data" / "raw"

# Espera pastas como:
# data/raw/consulta_cand_2022/
# data/raw/consulta_cand_2024/
PASTA_CANDIDATOS = RAW_DIR.glob("consulta_cand_*")

# Espera pastas como:
# data/raw/bem_candidato_2022/
# data/raw/bem_candidato_2024/
PASTA_BENS = RAW_DIR.glob("bem_candidato_*")

# ============================================================
# 4. FUNÇÕES DE UPSERT (INSERT IGNORE)
# ============================================================

def insert_ignore(df, tabela, pk_cols):
    """
    Insere dados ignorando duplicidades (ON CONFLICT DO NOTHING)
    """

    if df.empty:
        return

    # --------------------------------------------------------
    # Converte NaN / NaT para None
    # --------------------------------------------------------
    df = df.astype(object)

    df = df.where(pd.notnull(df), None)

    cols = df.columns.tolist()

    col_str = ", ".join(cols)

    val_str = ", ".join([f":{c}" for c in cols])

    pk_str = ", ".join(pk_cols)

    sql = f"""
        INSERT INTO {tabela} ({col_str})
        VALUES ({val_str})
        ON CONFLICT ({pk_str}) DO NOTHING
    """

    with engine.begin() as conn:
        conn.execute(
            text(sql),
            df.to_dict(orient="records")
        )


def insert_ignore_batch(df, tabela, pk_cols, batch_size=2000):
    """
    Insere dados em blocos para grandes volumes
    """
    total = len(df)
    print(f"Inserindo {total} registros em {tabela}")

    for start in range(0, total, batch_size):
        end = start + batch_size

        print(
            f"[{tabela}] Inserindo registros "
            f"{start + 1} até {min(end, total)}..."
        )


        bloco = df.iloc[start:end]
        insert_ignore(bloco, tabela, pk_cols)
        print(f" - {tabela}: {min(end, total)}/{total}")

# ============================================================
# 5. CARGA DE REGIÕES E UFs (DIMENSÕES FIXAS)
# ============================================================

def carregar_regioes_ufs():

    # -----------------------------
    # REGIÕES
    # -----------------------------
    regioes = pd.DataFrame([
        {"nm_regiao": "Norte"},
        {"nm_regiao": "Nordeste"},
        {"nm_regiao": "Centro-Oeste"},
        {"nm_regiao": "Sudeste"},
        {"nm_regiao": "Sul"},
    ])

    insert_ignore(regioes, "regiao", ["nm_regiao"])

    # Recupera IDs das regiões
    query = "SELECT cd_regiao, nm_regiao FROM regiao"
    df_regiao = pd.read_sql(query, engine)

    # -----------------------------
    # UFs (DIMENSÃO FIXA)
    # -----------------------------
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

    # Relaciona UF com região
    ufs = ufs.merge(df_regiao, on="nm_regiao", how="left")

    insert_ignore(
        ufs[["sg_uf", "nm_uf", "cd_regiao"]],
        "uf",
        ["sg_uf"]
    )

def limpar_valores_tse(df):

    # --------------------------------------------------------
    # Remove espaços
    # --------------------------------------------------------
    df = df.apply(
        lambda col: col.str.strip()
        if col.dtype == "object"
        else col
    )

    # --------------------------------------------------------
    # Valores especiais do TSE
    # --------------------------------------------------------
    df.replace({
        "#NULO": None,
        "#NE": None,
        "-1": None,
        "-3": None,
        "-4": None,
        "": None,
        "Não divulgável": None,
        "NÃO DIVULGÁVEL": None
    }, inplace=True)

    return df 


# ============================================================
# 6. LEITURA E TRATAMENTO DOS CANDIDATOS
# ============================================================
def carregar_candidatos():
    """
    Lê todos os CSVs de todas as pastas consulta_cand_YYYY
    """

    dfs = []
    total_arquivos = 0

    for pasta in PASTA_CANDIDATOS:

        print(f"\nPasta: {pasta}")

        for arq in pasta.glob("*.csv"):

            total_arquivos += 1

            print(f"\nLendo candidatos: {arq}")

            df = pd.read_csv(
                arq,
                sep=";",
                encoding="latin1",
                dtype=str,
                low_memory=False
            )

            print(f"Linhas lidas: {len(df)}")

            df.columns = [c.lower() for c in df.columns]

            df = limpar_valores_tse(df)

            dfs.append(df)

            total_acumulado = sum(len(x) for x in dfs)

            print(f"Total acumulado: {total_acumulado}")

    print(f"\nArquivos lidos: {total_arquivos}")

    df = pd.concat(dfs, ignore_index=True)

    print(f"\nTOTAL FINAL CONCATENADO: {len(df)}")

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

    # Numéricos principais
    campos_num = [
        "sq_candidato",
        "cd_eleicao",
        "cd_cargo",
        "nr_partido",
        "nr_federacao",
        "sq_coligacao",
        "nr_candidato"
    ]

    for c in campos_num:
        if c in df.columns:
            df[c] = pd.to_numeric(
                df[c],
                errors="coerce"
            )

    return df

'''def carregar_candidatos():
    """
    Lê todos os CSVs de todas as pastas consulta_cand_YYYY
    """
    dfs = []

    for pasta in PASTA_CANDIDATOS:
        for arq in pasta.glob("*.csv"):
            print(f"Lendo candidatos: {arq}")
            df = pd.read_csv(arq, sep=";", encoding="latin1", dtype=str)
            df.columns = [c.lower() for c in df.columns]
            df = limpar_valores_tse(df)
            dfs.append(df)

    df = pd.concat(dfs, ignore_index=True)

    # Datas
    df["dt_nascimento"] = pd.to_datetime(df["dt_nascimento"], format="%d/%m/%Y", errors="coerce")
    df["dt_eleicao"] = pd.to_datetime(df["dt_eleicao"], format="%d/%m/%Y", errors="coerce")

    # Numéricos principais
    campos_num = [
        "sq_candidato", "cd_eleicao", "cd_cargo", "nr_partido",
        "nr_federacao", "sq_coligacao", "nr_candidato"
    ]
    for c in campos_num:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    return df
'''
# ============================================================
# 7. CARGA DAS ELEIÇÕES (DIMENSÃO)
# ============================================================

def inserir_eleicoes(df):

    print("Carregando eleições...")

    eleicoes = df[[
        "cd_eleicao",
        "ano_eleicao",
        "nm_tipo_eleicao"
    ]].drop_duplicates()

    eleicoes.columns = [
        "cd_eleicao",
        "ano_eleicao",
        "nm_tipo_eleicao"
    ]

    eleicoes.dropna(subset=["cd_eleicao"], inplace=True)

    insert_ignore(
        eleicoes,
        "eleicao",
        ["cd_eleicao"]
    )

    print(f"Eleições carregadas: {len(eleicoes)}")   

# ============================================================
# 7.5 CARGA DOS CANDIDATOS (EM BLOCOS)
# ============================================================

def inserir_candidatos(df):

    candidato = df[[
        "sq_candidato",
        "cd_eleicao",
        "nr_candidato",
        "nm_candidato",
        "nm_urna_candidato",
        "nm_social_candidato",
        "nr_cpf_candidato",
        "ds_email",
        "dt_nascimento",
        "sg_uf_nascimento"
    ]].copy()

    candidato.columns = [
        "sq_candidato",
        "cd_eleicao",
        "nr_candidato",
        "nm_candidato",
        "nm_urna",
        "nm_social",
        "nr_cpf",
        "ds_email",
        "dt_nascimento",
        "sg_uf_nascimento"
    ]

    candidato.dropna(subset=["sq_candidato"], inplace=True)
    # TESTE TEMPORÁRIO
    #candidato = candidato.head(10000)

    # --------------------------------------------------------
    # CONVERTE DATA
    # --------------------------------------------------------
    candidato["dt_nascimento"] = pd.to_datetime(
        candidato["dt_nascimento"],
        errors="coerce"
    )

    # --------------------------------------------------------
    # LIMPA UF
    # --------------------------------------------------------
    candidato["sg_uf_nascimento"] = (
        candidato["sg_uf_nascimento"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    # --------------------------------------------------------
    # UFs válidas segundo TSE
    # --------------------------------------------------------
    ufs_validas = [
        "AC","AL","AP","AM","BA","CE","DF","ES",
        "GO","MA","MT","MS","MG","PA","PB","PR",
        "PE","PI","RJ","RN","RS","RO","RR","SC",
        "SP","SE","TO","BR","VT","ZZ"
    ]

    candidato.loc[
        ~candidato["sg_uf_nascimento"].isin(ufs_validas),
        "sg_uf_nascimento"
    ] = None

    # --------------------------------------------------------
    # INSERT
    # --------------------------------------------------------
    insert_ignore_batch(
        candidato,
        "candidato",
        ["sq_candidato"]
    )


# ============================================================
# 8. LEITURA E TRATAMENTO DOS BENS
# ============================================================

def carregar_bens():
    dfs = []

    for pasta in PASTA_BENS:
        for arq in pasta.glob("*.csv"):
            print(f"Lendo bens: {arq}")
            df = pd.read_csv(arq, sep=";", encoding="latin1", dtype=str)
            df.columns = [c.lower() for c in df.columns]

            df["ano_eleicao"] = pd.to_numeric(df["ano_eleicao"], errors="coerce")

            df["vr_bem_candidato"] = (
                df["vr_bem_candidato"]
                .str.replace(".", "", regex=False)
                .str.replace(",", ".", regex=False)
                .astype(float)
            )

            df["dt_ult_atual_bem_candidato"] = pd.to_datetime(
                df["dt_ult_atual_bem_candidato"],
                format="%d/%m/%Y",
                errors="coerce"
            )
            df = limpar_valores_tse(df)

            dfs.append(df)

    return pd.concat(dfs, ignore_index=True)

# ============================================================
# 9. CARGA DOS TIPOS DE BENS (DIMENSÃO)
# ============================================================

def inserir_tipos_bem(df_bens):
    tipo_bem = df_bens[[
        "cd_tipo_bem_candidato",
        "ds_tipo_bem_candidato"
    ]].drop_duplicates()

    tipo_bem.columns = ["cd_tipo_bem", "ds_tipo_bem"]

    insert_ignore(tipo_bem, "tipo_bem", ["cd_tipo_bem"])

# ============================================================
# 10. CARGA DOS BENS DOS CANDIDATOS (FATO)
# ============================================================

def inserir_bens(df_bens):
    bens = df_bens[[
        "sq_candidato",
        "ano_eleicao",
        "nr_ordem_bem_candidato",
        "cd_tipo_bem_candidato",
        "ds_bem_candidato",
        "vr_bem_candidato",
        "dt_ult_atual_bem_candidato"
    ]].copy()

    bens.columns = [
        "sq_candidato",
        "ano_eleicao",
        "nr_ordem_bem",
        "cd_tipo_bem",
        "ds_bem",
        "vr_bem",
        "dt_ultima_atualizacao"
    ]

    bens.dropna(subset=["sq_candidato"], inplace=True)

    insert_ignore_batch(
        bens,
        "bem_candidato",
        ["sq_candidato", "ano_eleicao", "nr_ordem_bem"]
    )

# ============================================================
# 11. EXECUÇÃO PRINCIPAL DO ETL
# ============================================================

def main():
    inicio = time.time()

    print("======================================")
    print("=== INICIANDO ETL TSE ===")
    print("======================================")

    # --------------------------------------------------------
    # REGIÕES E UFs
    # --------------------------------------------------------
    print("Carregando regiões e UFs...")
    carregar_regioes_ufs()

    # --------------------------------------------------------
    # CANDIDATOS
    # --------------------------------------------------------
    print("Lendo arquivos de candidatos...")
    df_cand = carregar_candidatos()

    print(f"Total candidatos carregados: {len(df_cand)}")

    inserir_eleicoes(df_cand)

    print("Inserindo candidatos...")
    inserir_candidatos(df_cand)

    # --------------------------------------------------------
    # BENS
    # --------------------------------------------------------
    print("Lendo arquivos de bens...")
    df_bens = carregar_bens()

    print(f"Total bens carregados: {len(df_bens)}")

    print("Inserindo tipos de bens...")
    inserir_tipos_bem(df_bens)

    print("Inserindo bens...")
    inserir_bens(df_bens)
    fim = time.time()
    print(f"\nTempo total: {fim - inicio:.2f} segundos")

    print("======================================")
    print("=== ETL FINALIZADO COM SUCESSO ===")
    print("======================================")


if __name__ == "__main__":
    main()