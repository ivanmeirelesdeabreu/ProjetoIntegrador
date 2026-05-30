import pandas as pd
from sqlalchemy import text
from config import LOG_FILE
import time
from datetime import datetime

class TabelasApoio:
    
    def carregar_regioes():
        return pd.DataFrame([
            {"nm_regiao": "Norte"},
            {"nm_regiao": "Nordeste"},
            {"nm_regiao": "Centro-Oeste"},
            {"nm_regiao": "Sudeste"},
            {"nm_regiao": "Sul"},
            {"nm_regiao": "Brasil"}
        ])
   
    def carregar_ufs():
        return pd.DataFrame([
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
            {"sg_uf": "BR", "nm_uf": "Brasil", "nm_regiao": "Brasil"},
        ])
    
    @staticmethod
    def carregar_dados_estaticos(engine):
        # 1. Definir os DataFrames 
        df_regioes = TabelasApoio.carregar_regioes() 
        
        # 2. Inserir Regiões 
        try:
            with engine.begin() as conn:
                for _, row in df_regioes.iterrows():

                    conn.execute(text("""
                        INSERT INTO regiao (nm_regiao) 
                        VALUES (:nm_regiao)
                        ON CONFLICT (nm_regiao) DO NOTHING
                    """), row.to_dict())
        except Exception as e:
            with open(LOG_FILE, "a") as f: f.write(f"[{datetime.now()}] Erro carregando região: {str(e)}\n")                

        # 3. Recuperar IDs gerados pelo banco para fazer o MERGE
        df_db_regiao = pd.read_sql("SELECT cd_regiao, nm_regiao FROM regiao", engine)
        
        # 4. Preparar UFs e fazer o MERGE
        ufs_raw = TabelasApoio.carregar_ufs()
        
        # O MERGE: associa o cd_regiao (do banco) à UF pelo nome da região
        ufs_final = ufs_raw.merge(df_db_regiao, on="nm_regiao", how="inner")
        
        # Selecionar apenas as colunas que existem no DDL da tabela UF [2]
        ufs_final = ufs_final[["sg_uf", "nm_uf", "cd_regiao"]]

        # 5. Inserir UFs
        try:
            with engine.begin() as conn:
                for _, row in ufs_final.iterrows():
                    conn.execute(text("""
                        INSERT INTO uf (sg_uf, nm_uf, cd_regiao) 
                        VALUES (:sg_uf, :nm_uf, :cd_regiao)
                        ON CONFLICT (sg_uf) DO NOTHING
                    """), row.to_dict())
        except Exception as e:
            with open(LOG_FILE, "a") as f: f.write(f"[{datetime.now()}] Erro carregando uf: {str(e)}\n")           
        
        print("Regiões e UFs carregadas com sucesso.")    