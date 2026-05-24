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
    "DS_ELEICAO": "ds_eleicao", "DT_ELEICAO": "dt_eleicao", "TP_ABRANGENCIA": "tp_abrangencia"
}

config_dimensoes = [
    ("municipio", ["CD_MUNICIPIO", "NM_MUNICIPIO", "SG_UF"], {"CD_MUNICIPIO": "cd_municipio", "NM_MUNICIPIO": "nm_municipio", "SG_UF": "sg_uf"}, "cd_municipio"),
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
    "CD_ELEICAO": "cd_eleicao", "SQ_CANDIDATO": "sq_candidato", "CD_MUNICIPIO": "cd_municipio",
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

# =========================================
# 3. TRANSFORMADORES E PIPELINE
# =========================================
class HigienizadorTSE(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None): return self
    def transform(self, X):
        X_copy = X.copy()
        cols_texto = X_copy.select_dtypes(include=['object', 'string']).columns
        for col in cols_texto:
            X_copy[col] = X_copy[col].str.strip().replace(['#NULO', '#NE', '-1', -1], np.nan)
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

# =========================================
# 5. PROCESSAMENTO COM SELEÇÃO DINÂMICA
# =========================================
def processar_arquivo(caminho_csv, tipo="candidato"):
    inicio_arquivo = time.time()
    print(f"\nIniciando: {caminho_csv.name} às {datetime.now().strftime('%H:%M:%S')}")
    
    df_bruto = pd.read_csv(caminho_csv, sep=';', encoding='latin1')
    
    # PASSO A: Eleição (Dinâmico para evitar KeyError em Bens)
    cols_e = [c for c in mapa_eleicao.keys() if c in df_bruto.columns]
    df_e = df_bruto[cols_e].drop_duplicates().rename(columns=mapa_eleicao)
    if 'dt_eleicao' in df_e.columns:
        df_e['dt_eleicao'] = pd.to_datetime(df_e['dt_eleicao'], format="%d/%m/%Y", errors="coerce")
    
    with engine.begin() as conn:
        for _, r in df_e.iterrows():
            params = r.to_dict()
            for k in mapa_eleicao.values():
                if k not in params: params[k] = None
            conn.execute(text("""INSERT INTO eleicao (cd_eleicao, ano_eleicao, nm_tipo_eleicao, nr_turno, ds_eleicao, dt_eleicao, tp_abrangencia) 
                VALUES (:cd_eleicao, :ano_eleicao, :nm_tipo_eleicao, :nr_turno, :ds_eleicao, :dt_eleicao, :tp_abrangencia) 
                ON CONFLICT (cd_eleicao) DO NOTHING"""), params)

    # PASSO B: Dimensões (Cargos, Partidos, etc.) [4]
    for tabela, cols, mapa, pk in config_dimensoes:
        if set(cols).issubset(df_bruto.columns):
            df_dim = df_bruto[cols].drop_duplicates().rename(columns=mapa)
            df_dim = filtrar_registros_existentes(df_dim, tabela, engine, pk)
            inserir_dados(df_dim, tabela, engine, caminho_csv.name)

    # PASSO C: Tabela Fato (Candidatos ou Bens) [5], [6]
    df_f = pipe_tse.fit_transform(df_bruto)
    mapa_alvo = mapa_candidato if tipo == "candidato" else mapa_bem
    pks_alvo = ["cd_eleicao", "sq_candidato"] if tipo == "candidato" else None
    
    cols_f = [c for c in mapa_alvo.keys() if c in df_f.columns]
    df_final = df_f[cols_f].rename(columns=mapa_alvo)
    
    if tipo == "candidato":
        if 'cd_municipio' not in df_final.columns: df_final['cd_municipio'] = None
        df_final = filtrar_registros_existentes(df_final, "candidato", engine, pks_alvo)
    
    inserir_dados(df_final, "candidato" if tipo == "candidato" else "bem_candidato", engine, caminho_csv.name)
    print(f"Finalizado: {caminho_csv.name} | Duração: {time.time() - inicio_arquivo:.2f}s")

def executar_etl():
    inicio_total = time.time()
    print(f"INÍCIO DO PROCESSO ETL: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
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