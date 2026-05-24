import pandas as pd
import numpy as np
import time
from pathlib import Path
from datetime import datetime
from sqlalchemy import create_engine, text
from sklearn.pipeline import Pipeline
from sklearn.base import BaseEstimator, TransformerMixin

# =========================================
# 1. CONFIGURAÇÕES E CONEXÃO
# =========================================
engine = create_engine(
    "postgresql+psycopg2://2422120019_Ivan:2422120019_Ivan@dataiesb.iesbtech.com.br:5432/2422120019_Ivan",
    connect_args={"options": "-csearch_path=eleicao"}
)

# Correção do __file__ para localizar os diretórios corretamente
BASE_DIR = Path(__file__).resolve().parent
RAW_DIR = BASE_DIR.parent / "data" / "raw"
LOG_FILE = BASE_DIR / "log_erros_importacao.txt"

# =========================================
# 2. MAPEAMENTOS E DIMENSÕES (Conforme DDL)
# =========================================
mapa_eleicao = {
    "CD_ELEICAO": "cd_eleicao", "ANO_ELEICAO": "ano_eleicao", 
    "NM_TIPO_ELEICAO": "nm_tipo_eleicao", "NR_TURNO": "nr_turno", 
    "DS_ELEICAO": "ds_eleicao", "DT_ELEICAO": "dt_eleicao", "cd_abrangencia": "cd_abrangencia"
}

config_dimensoes = [
    ("abrangencia", ["TP_ABRANGENCIA"], { "TP_ABRANGENCIA": "tp_abrangencia" }, "tp_abrangencia"),
    ("municipio", ["SG_UE", "NM_UE", "SG_UF"], {"SG_UE": "cd_municipio_tse", "NM_UE": "nm_municipio","SG_UF": "sg_uf"}, "cd_municipio_tse"),
    ("cargo", ["CD_CARGO", "DS_CARGO"], {"CD_CARGO": "cd_cargo", "DS_CARGO": "ds_cargo"}, "cd_cargo"),
    ("partido", ["NR_PARTIDO", "SG_PARTIDO", "NM_PARTIDO"], {"NR_PARTIDO": "nr_partido", "SG_PARTIDO": "sg_partido", "NM_PARTIDO": "nm_partido"}, "nr_partido"),
    ("federacao", ["NR_FEDERACAO", "NM_FEDERACAO", "SG_FEDERACAO", "DS_COMPOSICAO_FEDERACAO"], {"NR_FEDERACAO": "nr_federacao", "NM_FEDERACAO": "nm_federacao", "SG_FEDERACAO": "sg_federacao", "DS_COMPOSICAO_FEDERACAO": "ds_composicao_federacao"}, "nr_federacao"),
    ("ocupacao", ["CD_OCUPACAO", "DS_OCUPACAO"], {"CD_OCUPACAO": "cd_ocupacao", "DS_OCUPACAO": "ds_ocupacao"}, "cd_ocupacao"),
    ("grau_instrucao", ["CD_GRAU_INSTRUCAO", "DS_GRAU_INSTRUCAO"], {"CD_GRAU_INSTRUCAO": "cd_grau_instrucao", "DS_GRAU_INSTRUCAO": "ds_grau_instrucao"}, "cd_grau_instrucao"),
    ("estado_civil", ["CD_ESTADO_CIVIL", "DS_ESTADO_CIVIL"], {"CD_ESTADO_CIVIL": "cd_estado_civil", "DS_ESTADO_CIVIL": "ds_estado_civil"}, "cd_estado_civil"),
    ("genero", ["CD_GENERO", "DS_GENERO"], {"CD_GENERO": "cd_genero", "DS_GENERO": "ds_genero"}, "cd_genero"),
    ("cor_raca", ["CD_COR_RACA", "DS_COR_RACA"], {"CD_COR_RACA": "cd_cor_raca", "DS_COR_RACA": "ds_cor_raca"}, "cd_cor_raca"),
    ("situacao_candidatura", ["CD_SITUACAO_CANDIDATURA", "DS_SITUACAO_CANDIDATURA"], {"CD_SITUACAO_CANDIDATURA": "cd_situacao_candidatura", "DS_SITUACAO_CANDIDATURA": "ds_situacao_candidatura"}, "cd_situacao_candidatura"),
    ("situacao_turno", ["CD_SIT_TOT_TURNO", "DS_SIT_TOT_TURNO"], {"CD_SIT_TOT_TURNO": "cd_sit_tot_turno", "DS_SIT_TOT_TURNO": "ds_sit_tot_turno"}, "cd_sit_tot_turno"),
    ("tipo_bem", ["CD_TIPO_BEM_CANDIDATO", "DS_TIPO_BEM_CANDIDATO"], {"CD_TIPO_BEM_CANDIDATO": "cd_tipo_bem", "DS_TIPO_BEM_CANDIDATO": "ds_tipo_bem"}, "cd_tipo_bem")
]

mapa_candidato = {
    "CD_ELEICAO": "cd_eleicao", "SQ_CANDIDATO": "sq_candidato", "SG_UE": "cd_municipio_tse",
    "CD_CARGO": "cd_cargo", "NR_PARTIDO": "nr_partido", "NR_CANDIDATO": "nr_candidato",
    "NM_CANDIDATO": "nm_candidato", "NM_URNA_CANDIDATO": "nm_urna", "NR_CPF_CANDIDATO": "nr_cpf",
    "DS_EMAIL": "ds_email", "DT_NASCIMENTO": "dt_nascimento", "CD_GENERO": "cd_genero",
    "CD_GRAU_INSTRUCAO": "cd_grau_instrucao", "CD_ESTADO_CIVIL": "cd_estado_civil",
    "CD_COR_RACA": "cd_cor_raca", "CD_OCUPACAO": "cd_ocupacao", "NR_FEDERACAO": "nr_federacao",
    "CD_SITUACAO_CANDIDATURA": "cd_situacao_candidatura", "CD_SIT_TOT_TURNO": "cd_sit_tot_turno"
}

mapa_bem = {
    "CD_ELEICAO": "cd_eleicao", "SQ_CANDIDATO": "sq_candidato", "ANO_ELEICAO": "ano_eleicao",
    "NR_ORDEM_BEM_CANDIDATO": "nr_ordem_bem", "CD_TIPO_BEM_CANDIDATO": "cd_tipo_bem",
    "DS_BEM_CANDIDATO": "ds_bem", "VR_BEM_CANDIDATO": "vr_bem", "DT_ULT_ATUAL_BEM_CANDIDATO": "dt_ultima_atualizacao"
}

mapa_abrangencia = {
    "TP_ABRANGENCIA": "tp_abrangencia"
}

# =========================================
# 3. TRANSFORMADORES E PIPELINE
# =========================================
class HigienizadorTSE(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None): return self
    def transform(self, X):
        X_copy = X.copy()
        cols_texto = X_copy.select_dtypes(include=['object', 'string']).columns
        for col in cols_texto:
            X_copy[col] = X_copy[col].str.strip().str.upper().replace(['#NULO', '#NE', '-1', -1], np.nan)
        return X_copy

class ProcessadorTipos(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None): return self
    def transform(self, X):
        X_copy = X.copy()
        for c in ["DT_ULTIMA_ATUALIZACAO", "DT_ULT_ATUAL_BEM_CANDIDATO", "DT_NASCIMENTO", "DT_ELEICAO"]:
            if c in X_copy.columns:
                X_copy[c] = pd.to_datetime(X_copy[c], format="%d/%m/%Y", errors="coerce")
        if "VR_BEM_CANDIDATO" in X_copy.columns:
            X_copy["VR_BEM_CANDIDATO"] = pd.to_numeric(X_copy["VR_BEM_CANDIDATO"].astype(str).str.replace(",", "."), errors="coerce")
        return X_copy

pipe_tse = Pipeline([('higieniza', HigienizadorTSE()), ('tipos', ProcessadorTipos())])

# =========================================
# 4. FUNÇÕES DE CARGA (Sincronizadas)
# =========================================
def filtrar_registros_existentes(df, tabela, engine, pks):
    """Verifica duplicatas no banco antes da inserção [1]"""
    try:
        if isinstance(pks, str): pks = [pks]
        existentes = pd.read_sql(f"SELECT {', '.join(pks)} FROM {tabela}", engine)
        df_novo = df.merge(existentes, on=pks, how='left', indicator=True)
        return df_novo[df_novo['_merge'] == 'left_only'].drop(columns=['_merge'])
    except Exception: return df

def inserir_dados(df, tabela, engine, nome_arquivo):
    """Insere dados com tratamento de log [2]"""
    if df.empty: return
    try:
        with engine.begin() as conn:
            df.to_sql(tabela, conn, if_exists='append', index=False, method='multi', chunksize=5000)
    except Exception as e:
        with open(LOG_FILE, "a") as f: f.write(f"[{datetime.now()}] Erro {tabela} em {nome_arquivo}: {str(e)}\n")

def carregar_dados_estaticos(engine):
    # 1. Definir os DataFrames (como você já fez)
    df_regioes = pd.DataFrame([
        {"nm_regiao": "Norte"}, {"nm_regiao": "Nordeste"},
        {"nm_regiao": "Centro-Oeste"}, {"nm_regiao": "Sudeste"}, {"nm_regiao": "Sul"}
    ])
    
    # 2. Inserir Regiões (usando ON CONFLICT para evitar erros em re-execução)
    with engine.begin() as conn:
        for _, row in df_regioes.iterrows():
            conn.execute(text("""
                INSERT INTO regiao (nm_regiao) VALUES (:nm_regiao)
                ON CONFLICT (nm_regiao) DO NOTHING
            """), row.to_dict())

    # 3. Recuperar IDs gerados pelo banco para fazer o MERGE
    df_db_regiao = pd.read_sql("SELECT cd_regiao, nm_regiao FROM regiao", engine)

    # 4. Preparar UFs e fazer o MERGE
    ufs_raw = pd.DataFrame([
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

    # O MERGE: associa o cd_regiao (do banco) à UF pelo nome da região
    ufs_final = ufs_raw.merge(df_db_regiao, on="nm_regiao", how="inner")
    
    # Selecionar apenas as colunas que existem no DDL da tabela UF [2]
    ufs_final = ufs_final[["sg_uf", "nm_uf", "cd_regiao"]]

    # 5. Inserir UFs
    with engine.begin() as conn:
        for _, row in ufs_final.iterrows():
            conn.execute(text("""
                INSERT INTO uf (sg_uf, nm_uf, cd_regiao) 
                VALUES (:sg_uf, :nm_uf, :cd_regiao)
                ON CONFLICT (sg_uf) DO NOTHING
            """), row.to_dict())
    print("✅ Regiões e UFs carregadas com sucesso.")    

def obter_mapa_abrangencia(engine):
    """Busca o mapeamento de IDs da tabela abrangencia no banco."""
    try:
        df_ab = pd.read_sql("SELECT cd_abrangencia, tp_abrangencia FROM abrangencia", engine)
        return dict(zip(df_ab['tp_abrangencia'], df_ab['cd_abrangencia']))
    except Exception:
        return {}      

# =========================================
# 5. PROCESSAMENTO COM SELEÇÃO DINÂMICA
# =========================================
def processar_arquivo(caminho_csv, tipo="candidato"):
    inicio_arquivo = time.time()
    print(f"\nIniciando: {caminho_csv.name} às {datetime.now().strftime('%H:%M:%S')}")
    
    # 1. Leitura do arquivo bruto [3]
    df_bruto = pd.read_csv(caminho_csv, sep=';', encoding='latin1')
    
    # --- AJUSTE DE COMPATIBILIDADE 2022 (A base do problema) ---
    # Se o arquivo não tiver TP_ABRANGENCIA, criamos com base na SG_UE [2]
    if 'TP_ABRANGENCIA' not in df_bruto.columns:
        # Se SG_UE for 'BR' é Federal, senão é Estadual (para 2022)
        df_bruto['TP_ABRANGENCIA'] = df_bruto['SG_UE'].apply(
            lambda x: 'FEDERAL' if str(x).upper() == 'BR' else 'ESTADUAL'
        )
    
    # Garante que campos de Bens de 2024 existam para evitar erro no Pipeline/Mapeamento [4, 5]
    for col in ['VR_BEM_CANDIDATO', 'DT_ULT_ATUAL_BEM_CANDIDATO']:
        if col not in df_bruto.columns:
            df_bruto[col] = np.nan

    # PASSO A: Dimensões (Cargos, Partidos, etc.) [6]
    for tabela, cols, mapa, pk in config_dimensoes:
        if set(cols).issubset(df_bruto.columns):
            df_dim = df_bruto[cols].drop_duplicates().rename(columns=mapa)

            # Lógica específica para municípios (somente em eleições municipais) [6]
            if tabela == "municipio":
                df_dim = df_bruto[df_bruto["TP_ABRANGENCIA"] == "MUNICIPAL"][cols].drop_duplicates().rename(columns=mapa)
                df_dim = df_dim[df_dim["cd_municipio_tse"].notna()]

            df_dim = filtrar_registros_existentes(df_dim, tabela, engine, pk)
            inserir_dados(df_dim, tabela, engine, caminho_csv.name)

    # --- PASSO B: Eleição (Mapeando o ID da Abrangência) [1, 2] ---
    # Busca o "tradutor" de IDs da tabela abrangencia
    '''
    if 'TP_ABRANGENCIA' not in df_bruto.columns:
        # Aqui você REALMENTE CRIA os dados que o .map() vai usar depois
        df_bruto['TP_ABRANGENCIA'] = df_bruto['SG_UE'].apply(
            lambda x: 'FEDERAL' if str(x).upper() == 'BR' else 'ESTADUAL'
        )   
    mapa_ids_ab = obter_mapa_abrangencia(engine)
    
    
    # IMPORTANTE: Incluímos explicitamente 'TP_ABRANGENCIA' na seleção de colunas
    cols_e = [c for c in mapa_eleicao.keys() if c in df_bruto.columns or c == 'TP_ABRANGENCIA']
    df_e = df_bruto[cols_e].drop_duplicates().copy()
    
    # Agora o .map() encontrará a coluna TP_ABRANGENCIA e converterá para o ID [1]
    df_e['cd_abrangencia'] = df_e['TP_ABRANGENCIA'].map(mapa_ids_ab)
    '''

 # --- PASSO B: Processamento da Eleição (Sincronizado com novo DDL) ---

    # 1. COMPATIBILIDADE 2022: Criar a coluna de texto se ela não existir no CSV
    # Isso deve ser feito ANTES de selecionar as colunas para o df_e
    if 'TP_ABRANGENCIA' not in df_bruto.columns:
        df_bruto['TP_ABRANGENCIA'] = df_bruto['SG_UE'].apply(
            lambda x: 'FEDERAL' if str(x).upper() == 'BR' else 'ESTADUAL'
        )

    # 2. BUSCA DE IDs: Obtém o dicionário {'FEDERAL': 1, 'ESTADUAL': 2, ...}
    mapa_ids_ab = obter_mapa_abrangencia(engine)

    # 3. SELEÇÃO DE COLUNAS: 
    # Precisamos garantir que 'TP_ABRANGENCIA' esteja no df_e para podermos mapear seu valor
    cols_e = [c for c in mapa_eleicao.keys() if c in df_bruto.columns]
    if 'TP_ABRANGENCIA' not in cols_e:
        cols_e.append('TP_ABRANGENCIA')
    
    df_e = df_bruto[cols_e].drop_duplicates().copy()

    # 4. MAPEAMENTO: Converte o texto em ID numérico conforme seu DDL
    # Note que agora usamos a coluna que acabamos de garantir que existe no df_e
    df_e['cd_abrangencia'] = df_e['TP_ABRANGENCIA'].map(mapa_ids_ab)

    # 5. AJUSTE PARA O BANCO:
    # Renomeamos as colunas conforme o seu mapa_eleicao
    df_e = df_e.rename(columns=mapa_eleicao)
    
    # 6. LIMPEZA FINAL: 
    # Removemos a coluna de texto 'TP_ABRANGENCIA' (ou 'tp_abrangencia') 
    # porque sua tabela 'eleicao' agora só aceita o ID numérico
    colunas_para_remover = [c for c in ['TP_ABRANGENCIA', 'tp_abrangencia'] if c in df_e.columns]
    df_e = df_e.drop(columns=colunas_para_remover)

   
    # Renomeia para os nomes das colunas do banco (cd_eleicao, dt_eleicao, etc) [2]
    #df_e = df_e.rename(columns=mapa_eleicao)
    
    if 'dt_eleicao' in df_e.columns:
        df_e['dt_eleicao'] = pd.to_datetime(df_e['dt_eleicao'], format="%d/%m/%Y", errors="coerce")
    
    # Se o seu DDL agora espera cd_abrangencia (ID), removemos a coluna de texto original
    # Isso evita erro de "coluna tp_abrangencia não encontrada" no INSERT [1]
    #if 'tp_abrangencia' in df_e.columns:
    #    df_e = df_e.drop(columns=['tp_abrangencia'])

    # Filtra e insere a Eleição
    df_e = filtrar_registros_existentes(df_e, "eleicao", engine, "cd_eleicao")
    inserir_dados(df_e, "eleicao", engine, caminho_csv.name)

    # PASSO C: Tabela Fato (Candidatos ou Bens) [4, 5, 7, 8]
    df_f = pipe_tse.fit_transform(df_bruto)
    mapa_alvo = mapa_candidato if tipo == "candidato" else mapa_bem
    tabela_destino = "candidato" if tipo == "candidato" else "bem_candidato"
    pks_alvo = ["cd_eleicao", "sq_candidato"] if tipo == "candidato" else "id_bem"
    
    cols_f = [c for c in mapa_alvo.keys() if c in df_f.columns]
    df_final = df_f[cols_f].rename(columns=mapa_alvo)
    
    if tipo == "candidato":
        # Limpa município se não for eleição municipal [7]
        df_final.loc[df_bruto["TP_ABRANGENCIA"] != "MUNICIPAL", "cd_municipio_tse"] = None
        df_final = filtrar_registros_existentes(df_final, "candidato", engine, pks_alvo)
    
    inserir_dados(df_final, tabela_destino, engine, caminho_csv.name)
    print(f"Finalizado: {caminho_csv.name}")
    print(f"Duração: {int((time.time()-inicio_arquivo)//3600):02d}:{int(((time.time()-inicio_arquivo)%3600)//60):02d}:{(time.time()-inicio_arquivo)%60:05.2f}")

def executar_etl():
    inicio_total = time.time()
    print(f"INÍCIO DO PROCESSO ETL: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

    # CARGA ESTÁTICA AQUI (Nova chamada)
    carregar_dados_estaticos(engine)
    
    # Localização de pastas conforme chat
    pastas_cand = [p for p in RAW_DIR.iterdir() if p.is_dir() and p.name.startswith("consulta_cand_")]
    pastas_bens = [p for p in RAW_DIR.iterdir() if p.is_dir() and p.name.startswith("bem_candidato_")]
    
    for p in pastas_cand:
        for f in p.glob("*.csv"): processar_arquivo(f, "candidato")
    
    for p in pastas_bens:
        for f in p.glob("*.csv"): processar_arquivo(f, "bens")
        
    print(f"\n🏆 ETL CONCLUÍDO! Tempo Total: {(time.time() - inicio_total)/60:.2f} minutos")

if __name__ == "__main__":
    if LOG_FILE.exists(): LOG_FILE.unlink()
    executar_etl()