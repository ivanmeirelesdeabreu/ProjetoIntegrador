# =========================================================
# CLASSE BASE
# =========================================================


class MapaImportacao:

    def __init__(self, nome, tabela, pk, mapa, filtro=None):

        self.nome = nome
        self.tabela = tabela
        self.pk = pk
        self.mapa = mapa
        self.filtro = filtro

    # -----------------------------------------------------

    def colunas_csv_existentes(self, df):

        return [
            c for c in self.mapa.keys()
            if c in df.columns
        ]

    # -----------------------------------------------------

    def mapa_ativo(self, df):

        return {
            k: v
            for k, v in self.mapa.items()
            if k in df.columns
        }

    # -----------------------------------------------------

    def preparar_dataframe(self, df, engine=None):

        mapa = self.mapa_ativo(df)

        if not mapa:
            return None

        colunas = list(mapa.keys())
        #print("Colunas CSV disponíveis:")
        #print(colunas)

        df_saida = ( df[colunas].rename(columns=mapa).copy() )
        #print("Colunas do DataFrame de saída:")
        #print(df_saida.columns)

        if self.filtro: 
            df_saida = self.filtro(df_saida)
        
        return df_saida    








