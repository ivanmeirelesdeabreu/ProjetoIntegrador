
from mapa_importacao import MapaImportacao
import pandas as pd

def tratar_ue(df):
    #print("passei no tratar_ue dentro de mapas....")
    #print(df.columns.tolist())

    if "sg_ue" in df.columns:

        sg_ue = df["sg_ue"].astype(str)

        mask_numero = sg_ue.str.isdigit()

        df.loc[mask_numero, "cd_municipio_tse"] = pd.to_numeric(
            sg_ue[mask_numero],
            errors="coerce"
        )

        df.loc[~mask_numero, "sg_uf"] = sg_ue[~mask_numero]

    elif "sg_uf" in df.columns:

        df["sg_uf"] = df["sg_uf"]

    return df[df["cd_municipio_tse"].notna()]

'''
def tratar_ue(df):

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


def tratar_ue(df):

    mask_numero = df["cd_municipio_tse"].astype(str).str.isdigit()

    # cria sg_ue para os não numéricos
    df.loc[~mask_numero, "sg_ue"] = df.loc[~mask_numero, "cd_municipio_tse"]

    # opcional: limpar cd_municipio_tse dos não numéricos
    df.loc[~mask_numero, "cd_municipio_tse"] = None

    return df
'''
# =========================================================
# MAPAS
# =========================================================

MAPAS = {

    # =====================================================
    # ABRANGENCIA
    # =====================================================

    "abrangencia": MapaImportacao(

        nome="abrangencia",

        tabela="abrangencia",

        pk=["tp_abrangencia"],

        mapa={

            "TP_ABRANGENCIA": "tp_abrangencia"
        }
    ),

    # =====================================================
    # ELEICAO
    # =====================================================

    "eleicao": MapaImportacao(

        nome="eleicao",

        tabela="eleicao",

        pk=["cd_eleicao"],

        mapa={

            "CD_ELEICAO": "cd_eleicao",

            "ANO_ELEICAO": "ano_eleicao",

            "NM_TIPO_ELEICAO": "nm_tipo_eleicao",

            "NR_TURNO": "nr_turno",

            "DS_ELEICAO": "ds_eleicao",

            "DT_ELEICAO": "dt_eleicao"

            # cd_abrangencia será resolvido depois
            # via lookup da tabela abrangencia
        }
    ),

    # =====================================================
    # MUNICIPIO
    # =====================================================

    "municipio": MapaImportacao(

        nome="municipio",

        tabela="municipio",

        pk=["cd_municipio_tse"],

        mapa={
            "SG_UF": "sg_uf",
            "SG_UE": "sg_ue",
            "NM_UE": "nm_municipio"

        },
        #filtro=lambda df: 
        #    df[df["cd_municipio_tse"].astype(str).str.isdigit() ]
        filtro=tratar_ue

    ),

    # =====================================================
    # CARGO
    # =====================================================

    "cargo": MapaImportacao(

        nome="cargo",

        tabela="cargo",

        pk=["cd_cargo"],

        mapa={

            "CD_CARGO": "cd_cargo",

            "DS_CARGO": "ds_cargo"
        }
    ),

    # =====================================================
    # PARTIDO
    # =====================================================

    "partido": MapaImportacao(

        nome="partido",

        tabela="partido",

        pk=["nr_partido"],

        mapa={

            "NR_PARTIDO": "nr_partido",

            "SG_PARTIDO": "sg_partido",

            "NM_PARTIDO": "nm_partido"
        }
    ),

    # =====================================================
    # FEDERACAO
    # =====================================================

    "federacao": MapaImportacao(

        nome="federacao",

        tabela="federacao",

        pk=["nr_federacao"],

        mapa={

            "NR_FEDERACAO": "nr_federacao",

            "NM_FEDERACAO": "nm_federacao",

            "SG_FEDERACAO": "sg_federacao",

            "DS_COMPOSICAO_FEDERACAO": "ds_composicao_federacao"
        }
    ),

    # =====================================================
    # GENERO
    # =====================================================

    "genero": MapaImportacao(

        nome="genero",

        tabela="genero",

        pk=["cd_genero"],

        mapa={

            "CD_GENERO": "cd_genero",

            "DS_GENERO": "ds_genero"
        }
    ),

    # =====================================================
    # GRAU INSTRUCAO
    # =====================================================

    "grau_instrucao": MapaImportacao(

        nome="grau_instrucao",

        tabela="grau_instrucao",

        pk=["cd_grau_instrucao"],

        mapa={

            "CD_GRAU_INSTRUCAO": "cd_grau_instrucao",

            "DS_GRAU_INSTRUCAO": "ds_grau_instrucao"
        }
    ),

    # =====================================================
    # ESTADO CIVIL
    # =====================================================

    "estado_civil": MapaImportacao(

        nome="estado_civil",

        tabela="estado_civil",

        pk=["cd_estado_civil"],

        mapa={

            "CD_ESTADO_CIVIL": "cd_estado_civil",

            "DS_ESTADO_CIVIL": "ds_estado_civil"
        }
    ),

    # =====================================================
    # COR RACIAL
    # =====================================================

    "cor_raca": MapaImportacao(

        nome="cor_raca",

        tabela="cor_raca",

        pk=["cd_cor_raca"],

        mapa={

            "CD_COR_RACA": "cd_cor_raca",

            "DS_COR_RACA": "ds_cor_raca"
        }
    ),

    # =====================================================
    # OCUPACAO
    # =====================================================

    "ocupacao": MapaImportacao(

        nome="ocupacao",

        tabela="ocupacao",

        pk=["cd_ocupacao"],

        mapa={

            "CD_OCUPACAO": "cd_ocupacao",

            "DS_OCUPACAO": "ds_ocupacao"
        }
    ),

    # =====================================================
    # SITUACAO CANDIDATURA
    # =====================================================

    "situacao_candidatura": MapaImportacao(

        nome="situacao_candidatura",

        tabela="situacao_candidatura",

        pk=["cd_situacao_candidatura"],

        mapa={

            "CD_SITUACAO_CANDIDATURA": "cd_situacao_candidatura",

            "DS_SITUACAO_CANDIDATURA": "ds_situacao_candidatura"
        }
    ),

    # =====================================================
    # SITUACAO TURNO
    # =====================================================

    "situacao_turno": MapaImportacao(

        nome="situacao_turno",

        tabela="situacao_turno",

        pk=["cd_sit_tot_turno"],

        mapa={

            "CD_SIT_TOT_TURNO": "cd_sit_tot_turno",

            "DS_SIT_TOT_TURNO": "ds_sit_tot_turno"
        }
    ),

    # =====================================================
    # CANDIDATO
    # =====================================================

    "candidato": MapaImportacao(

        nome="candidato",

        tabela="candidato",

        pk=["sq_candidato"],

        mapa={

            "SQ_CANDIDATO": "sq_candidato",
            "NR_CPF_CANDIDATO": "nr_cpf_candidato",
            "NM_CANDIDATO": "nm_candidato",
            "NR_TITULO_ELEITORAL_CANDIDATO": "nr_titulo_eleitoral",
            "CD_GENERO": "cd_genero",
            "CD_ESTADO_CIVIL": "cd_estado_civil",
            "CD_COR_RACA": "cd_cor_raca",
            "CD_OCUPACAO": "cd_ocupacao",
            "CD_GRAU_INSTRUCAO": "cd_grau_instrucao",
            "DT_NASCIMENTO": "dt_nascimento",
            "DS_EMAIL": "ds_email",
            "SG_UF_NASCIMENTO": "sg_uf_nascimento",
            "CD_MUNICIPIO_TSE": "cd_municipio_tse",
            "SG_UF": "sg_uf"

        }
    ),

    # =====================================================
    # CANDIDATURA
    # =====================================================

    "candidatura": MapaImportacao(

        nome="candidatura",

        tabela="candidatura",

        pk=[
            "sq_candidato",
            "cd_eleicao",
            "nr_turno",
            "cd_cargo"
        ],

        mapa={

            "SQ_CANDIDATO": "sq_candidato",

            "CD_ELEICAO": "cd_eleicao",

            "NR_TURNO": "nr_turno",

            "CD_CARGO": "cd_cargo",

            "NR_CANDIDATO": "nr_candidato",

            "NR_FEDERACAO": "nr_federacao",

            "NM_URNA_CANDIDATO": "nm_urna_candidato",

            "NR_PARTIDO": "nr_partido",

            "SG_UF": "sg_uf",

            "SG_UE": "sg_ue",

            "NM_UE": "nm_ue",

            "CD_SITUACAO_CANDIDATURA": "cd_situacao_candidatura",

            "CD_SIT_TOT_TURNO": "cd_sit_tot_turno",

            "ST_CANDIDATO_INSERIDO_URNA": "st_candidato_inserido_urna",

            "SQ_COLIGACAO": "sq_coligacao"
        }
    ),

    # =====================================================
    # TIPO BEM
    # =====================================================

    "tipo_bem": MapaImportacao(

        nome="tipo_bem",

        tabela="tipo_bem",

        pk=["cd_tipo_bem"],

        mapa={

            "CD_TIPO_BEM_CANDIDATO": "cd_tipo_bem",
            "DS_TIPO_BEM_CANDIDATO": "ds_tipo_bem"
        }
    ),

    # =====================================================
    # BEM CANDIDATO
    # =====================================================

    "bem_candidato": MapaImportacao(

        nome="bem_candidato",

        tabela="bem_candidato",

        pk=[
            "id_candidatura",
            "nr_ordem_bem"
        ],

        mapa={
            "ID_CANDIDATURA": "id_candidatura",
            "SQ_CANDIDATO": "sq_candidato",
            "CD_ELEICAO": "cd_eleicao",
            "NR_ORDEM_BEM_CANDIDATO": "nr_ordem_bem",
            "CD_TIPO_BEM_CANDIDATO": "cd_tipo_bem",
            "DS_BEM_CANDIDATO": "ds_bem",
            "VR_BEM_CANDIDATO": "vr_bem",
            "DT_ULT_ATUAL_BEM_CANDIDATO": "dt_ultima_atualizacao"
        }
    )
}

# =========================================================  
# ORDEM DE CARGA 
# =========================================================

ORDEM_CARGA = [
    "abrangencia",
    "cargo",
    "partido",
    "federacao",
    "genero",
    "grau_instrucao",
    "estado_civil",
    "cor_raca",
    "ocupacao",
    "situacao_candidatura",
    "situacao_turno",
    "municipio",
    "eleicao",
    "candidato",
    "candidatura",
    "tipo_bem",
    "bem_candidato"
]

TABELAS_UPSERT = [
    "candidato",
    "candidatura",
    "bem_candidato"
]


GRUPOS_BASE  = {
    "dimensoes": [
        "abrangencia",
        "eleicao",
        "cargo",
        "partido",
        "federacao",
        "genero",
        "grau_instrucao",
        "estado_civil",
        "cor_raca",
        "ocupacao",
        "situacao_candidatura",
        "situacao_turno",
        "municipio"

    ],
    "candidato_core": [
        "candidato",
        "candidatura"
    ],
    "bens": [
        "tipo_bem",
        "bem_candidato"
    ]
}

MAPAS_POR_TIPO  = {
    "candidato": GRUPOS_BASE["dimensoes"] + GRUPOS_BASE["candidato_core"],
    "bens": GRUPOS_BASE["bens"]
}





