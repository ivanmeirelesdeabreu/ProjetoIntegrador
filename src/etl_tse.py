import pandas as pd
import time
from datetime import datetime
import glob
from pathlib import Path

from sqlalchemy import create_engine, text
from urllib.parse import quote_plus

from sklearn.pipeline import Pipeline

from config import LOG_FILE, RAW_DIR
from data_transformers import HigienizadorTSE, ProcessadorTipos 
from data_apoio import TabelasApoio
from etl_tse_completo_des import inserir_dados
from mapas import MAPAS, ORDEM_CARGA, TABELAS_UPSERT, ORDEM_CARGA, MAPAS_POR_TIPO

# =========================================
# 1. configurações de conexão
# =========================================
# Configurações da conexão com o banco de dados
'''
db_config = {
    "user": "2422120019_Ivan",
    "pass": "2422120019_Ivan",
    "host": "dataiesb.iesbtech.com.br",
    "port": "5432",
    "db": "2422120019_Ivan",
    "schema": "eleicao_des"
}
'''
db_config = {
    "user": "postgres",
    "pass": quote_plus("pstComunidade@9"),
    "host": "localhost",
    "port": "5432",
    "db": "tse",
    "schema": "eleicao"
}

user = db_config['user']
pwd = db_config['pass']
host = db_config['host']
port = db_config['port']
db = db_config['db']
schema = db_config['schema']

# 
#url = f"postgresql+psycopg2://{db_config['user']}:{db_config['pass']}@{db_config['host']}:{db_config['port']}/{db_config['db']}"
url = f"postgresql+psycopg2://{user}:{pwd}@{host}:{port}/{db}"
try:
    engine = create_engine(
        url,
        connect_args={"options": f"-csearch_path={schema}"}
    )
except Exception as e:
    #print(f"Erro conectando ao banco de dados: {str(e)}")
    with open(LOG_FILE, "a") as f: f.write(f"[{datetime.now()}] Erro conectando ao BD: {str(e)}\n")  


# =========================================
# 3. processamento dos arquivos
# =========================================
def tratar_ue(df):
    #print("passei no tratar_ue dentro de etl....")

    # caso exista SG_UE
    if "SG_UE" in df.columns:

        sg_ue = df["SG_UE"].astype(str)

        mask_numero = sg_ue.str.isdigit()

        # municípios
        df.loc[mask_numero, "cd_municipio_tse"] = sg_ue[mask_numero]

        # UFs antigas
        df.loc[~mask_numero, "sg_uf"] = sg_ue[~mask_numero]

    # arquivos sem SG_UE
    elif "SG_UF" in df.columns:

        df["sg_uf"] = df["SG_UF"]

    return df


'''
def tratar_ue(df):

    # garante string
    sg_ue = df["SG_UE"].astype(str)

    # identifica números
    mask_numero = sg_ue.str.isdigit()

    # município quando for número
    df.loc[mask_numero, "cd_municipio_tse"] = sg_ue[mask_numero]

    # uf quando NÃO for número
    df.loc[~mask_numero, "sg_uf"] = sg_ue[~mask_numero]

    return df
'''
def adicionar_id_candidatura(df_bens, engine):
    sql = """
            SELECT
                id_candidatura AS ID_CANDIDATURA,
                sq_candidato AS SQ_CANDIDATO,
                cd_eleicao AS CD_ELEICAO
            FROM candidatura
        """
    df_candidatura = pd.read_sql(sql, engine)
    #print(df_candidatura.to_string(index=False))
    #print(f"df_candidatura colunas: {df_candidatura.columns.str.upper().tolist()}")

    #exit()
    #df_candidatura.columns = df_candidatura.columns.str.upper()

    #print(f"Adicionando ID_CANDIDATURA: {df_bens} registros de bens x {df_candidatura} registros de candidatura")
    #print("antes do merge:")
    #print(df_bens.columns.tolist())
    #print(df_candidatura.columns.tolist())

    df_bens = df_bens.merge(
            df_candidatura[["sq_candidato", "id_candidatura", "cd_eleicao"]],
            on=["sq_candidato", "cd_eleicao"],
            how="left"
    )
    
    #("depois do merge:")
    #print(df_bens.columns.tolist())
    #print(df_candidatura.columns.tolist())

    return df_bens    


def inserir_dados(df, tabela, engine, nome_arquivo, pk=None, upsert=False):
    if df.empty:
        return
    try:

        df = df.astype(object)

        df = df.where(
            pd.notnull(df),
            None
        )

        registros = df.to_dict(orient="records")

        colunas = list(df.columns)
        colunas_sql = ", ".join(colunas)
        placeholders = ", ".join([f":{c}" for c in colunas])

        # ==================================================
        # UPSERT
        # ==================================================

        if upsert and pk:
            #print(f"Preparando UPSERT para {tabela} com PK {pk}")


            colunas_update = [
                c for c in colunas
                if c not in pk
            ]
            
            #print(colunas_update)

            update_sql = ", ".join([
                f"{c} = EXCLUDED.{c}"
                for c in colunas_update
            ])
            #print(update_sql)

            pk_sql = ", ".join(pk)
            sql = f"""
                INSERT INTO eleicao.{tabela}
                ({colunas_sql})
                VALUES ({placeholders})
                ON CONFLICT ({pk_sql})
                DO UPDATE SET
                {update_sql}

            """

        # ==================================================
        # INSERT IGNORE
        # ==================================================

        else:
            #print(colunas_sql)
            #print(placeholders)
            pk_sql = ", ".join(pk)
            sql = f"""
                INSERT INTO eleicao.{tabela}
                ({colunas_sql})
                VALUES ({placeholders})
                ON CONFLICT ({pk_sql})
                DO NOTHING
            """

        # ==================================================
        # EXECUTA
        # ==================================================

        with engine.begin() as conn:

            conn.execute(
                text(sql),
                registros
            )

        print(
            f"[OK - inserido] {tabela}: "
            f"{len(df)} registros"
        )

    except Exception as e:

        erro = (
            f"[{datetime.now()}] "
            f"Erro na tabela {tabela} "
            f"arquivo {nome_arquivo}: "
            f"{str(e)}"
        )

        #print(erro)

        with open(LOG_FILE, "a") as f: f.write(erro + "\n")

def processar_arquivo(caminho_csv, tipo="candidato"):

    PIPELINES = {
        "candidato": Pipeline([
            ('higieniza', HigienizadorTSE()),
            ('tipos', ProcessadorTipos())
        ]),
        "bens": Pipeline([
            ('higieniza', HigienizadorTSE()),
            ('tipos', ProcessadorTipos())
        ])
    }

    inicio_arquivo = time.time()
    print(f"\nIniciando: {caminho_csv.name} às {datetime.now().strftime('%H:%M:%S')}")

    # 1. leitura
    df_bruto = pd.read_csv(caminho_csv, sep=';', encoding='latin1')

    if df_bruto.empty:
        return

    # 2. pipeline por tipo
    pipe = PIPELINES[tipo]
    df_final = pipe.fit_transform(df_bruto)

    # 3. filtra mapas válidos do tipo
    mapas_validos = [
        nome for nome in ORDEM_CARGA
        if nome in MAPAS_POR_TIPO[tipo]
    ]

    dfs_processados = {}
    #print(f"Mapas a processar: {mapas_validos}")
    #print(df_final.columns)

    # 4. ETAPA ÚNICA: transformação + preparação

    for nome_mapa in mapas_validos:

        mapa_obj = MAPAS[nome_mapa]
  
        try:
            #if nome_mapa == "municipio":
            #   print(f"Mapa a processar: {mapas_validos}")
            #    print(df_final.columns)
            #    print(df_tabela.columns)
            #    exit()

            df_tabela = mapa_obj.preparar_dataframe(df_final)


            if df_tabela is None or df_tabela.empty:
                continue

            df_tabela = df_tabela.drop_duplicates()
   
            # regra especial bens (se existir nesse tipo)

            if nome_mapa == "bem_candidato":
                df_tabela = adicionar_id_candidatura(df_tabela, engine)

            dfs_processados[nome_mapa] = df_tabela

            print(f"[OK - processado] {nome_mapa}: {len(df_tabela)} registros")

        except Exception as e:
            print(f"[ERRO] {nome_mapa}: {e}")

    # 5. ETAPA ÚNICA: persistência (SEM RECALCULAR NADA)
    for nome_mapa in mapas_validos:

        if nome_mapa not in dfs_processados:
            continue

        df_tabela = dfs_processados[nome_mapa]
        mapa_obj = MAPAS[nome_mapa]
        #print(f"vou chamar inserir_dados:{df_tabela}")
        #print(f"vou chamar inserir_dados:{mapa_obj.tabela}")

        if nome_mapa == "candidato" or nome_mapa == "candidatura" or nome_mapa == "municipio":
            #print(df_tabela.columns)
            df_tabela = tratar_ue(df_tabela)
        

        inserir_dados(
            df=df_tabela,
            tabela=mapa_obj.tabela,
            engine=engine,
            nome_arquivo=caminho_csv.name,
            pk=mapa_obj.pk,
            upsert=(nome_mapa in TABELAS_UPSERT)
        )

    print(f"Finalizado: {caminho_csv.name}")

    duracao = time.time() - inicio_arquivo
    print(
        f"Duração: "
        f"{int(duracao//3600):02d}:"
        f"{int((duracao%3600)//60):02d}:"
        f"{duracao%60:05.2f}"
    )

    #print(f"Duração: {int((time.time()-inicio_arquivo)//3600):02d}:{int(((time.time()-inicio_arquivo)%3600)//60):02d}:{(time.time()-inicio_arquivo)%60:05.2f}")

# =========================================
# 4. executar o processo ETL
# =========================================

def executar_etl():
    inicio_total = time.time()
    print(f"INÍCIO DO PROCESSO ETL: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

    # CARGA ESTÁTICA AQUI 
    print(f"Carregando dados estáticos: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    TabelasApoio.carregar_dados_estaticos(engine)
    print(f"Fim do carregamento dos dados estáticos: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

    # Localização de pastas conforme chat
    pastas_cand = [p for p in RAW_DIR.iterdir() if p.is_dir() and p.name.startswith("consulta_cand_")]
    pastas_bens = [p for p in RAW_DIR.iterdir() if p.is_dir() and p.name.startswith("bem_candidato_")]

    for p in pastas_cand:
        # Ordena: False (0) vem antes de True (1). Logo, 'BRASIL' fica por último.
        arquivos = sorted(p.glob("*.csv"), key=lambda x: "BRASIL" in x.name.upper())
        for f in arquivos: 
            processar_arquivo(f, "candidato")

    for p in pastas_bens:
        arquivos = sorted(p.glob("*.csv"), key=lambda x: "BRASIL" in x.name.upper())
        for f in arquivos: 
              processar_arquivo(f, "bens")

       
    print(f"\n🏆 ETL CONCLUÍDO! Tempo Total: {(time.time() - inicio_total)/60:.2f} minutos")


if __name__ == "__main__":
    if LOG_FILE.exists(): LOG_FILE.unlink()
    executar_etl()
