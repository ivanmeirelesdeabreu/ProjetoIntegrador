import pandas as pd
import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin
import unicodedata


class HigienizadorTSE(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None): return self
    def transform(self, X):

        invalidos = {
            '#NULO',
            '#NE',
            '-1',
            'NAO DIVULGAVEL',
            'NAO INFORMADO',
            'ZZ'
        }


        #invalidos = ['#NULO', '#NE', '-1', -1]
       
        X_copy = X.copy()
        cols_texto = X_copy.select_dtypes(include=['object', 'string']).columns
        for col in cols_texto:
            #X_copy[col] = X_copy[col].str.strip().str.upper().mask(lambda s: s.isin(invalidos), np.nan)
            X_copy[col] = (X_copy[col].astype(str).str.strip().str.upper())

           # remove acentos
            X_copy[col] = X_copy[col].apply(
                lambda x: unicodedata.normalize('NFKD', x)
                .encode('ASCII', 'ignore')
                .decode('ASCII')
                if pd.notnull(x) else x
            )

            X_copy[col] = X_copy[col].str.strip().str.upper()
            X_copy[col] = np.where(X_copy[col].isin(invalidos), np.nan, X_copy[col])

        return X_copy

class ProcessadorTipos(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None): return self
    def transform(self, X):
        X_copy = X.copy()

        for c in ["DT_ULTIMA_ATUALIZACAO", "DT_ULT_ATUAL_BEM_CANDIDATO", "DT_NASCIMENTO", "DT_ELEICAO"]:
            if c in X_copy.columns:
                X_copy[c] = pd.to_datetime(X_copy[c], format="%d/%m/%Y", errors="coerce")
        for c in ["VR_BEM_CANDIDATO"]:   
            if c in X_copy.columns:    
                X_copy[c] = pd.to_numeric(X_copy[c].astype(str).str.replace(",", "."), errors="coerce")
        return X_copy