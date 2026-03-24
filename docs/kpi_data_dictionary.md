# 📊 Dicionário de Dados — TSE 2024

Fonte: Tribunal Superior Eleitoral (TSE)
Arquivo: `consulta_cand_2024_BRASIL.csv`

---

## 📁 Descrição Geral

Esta base contém informações cadastrais e eleitorais dos candidatos das eleições de 2024 no Brasil.

---

## 🧾 Campos da Base

| Coluna                          | Tipo    | Descrição |
|--------------------------------|---------|----------|
| DT_GERACAO                     | Data    | Data de geração do arquivo pelo TSE |
| HH_GERACAO                     | Texto   | Hora de geração do arquivo |
| ANO_ELEICAO                    | Inteiro | Ano da eleição |
| CD_TIPO_ELEICAO                | Inteiro | Código do tipo de eleição |
| NM_TIPO_ELEICAO                | Texto   | Nome do tipo de eleição |
| NR_TURNO                       | Inteiro | Número do turno da eleição |
| CD_ELEICAO                     | Inteiro | Identificador da eleição |
| DS_ELEICAO                     | Texto   | Descrição da eleição |
| DT_ELEICAO                     | Data    | Data oficial da votação |
| TP_ABRANGENCIA                 | Texto   | Tipo de abrangência da eleição |
| SG_UF                          | Texto   | Unidade federativa (UF) |
| SG_UE                          | Texto   | Código da unidade eleitoral |
| NM_UE                          | Texto   | Nome do município da candidatura |
| CD_CARGO                       | Inteiro | Código do cargo disputado |
| DS_CARGO                       | Texto   | Cargo disputado (Prefeito, Vereador, etc.) |
| SQ_CANDIDATO                   | Inteiro | Identificador único do candidato |
| NR_CANDIDATO                   | Inteiro | Número do candidato |
| NM_CANDIDATO                   | Texto   | Nome civil completo do candidato |
| NM_URNA_CANDIDATO              | Texto   | Nome utilizado na urna |
| NM_SOCIAL_CANDIDATO            | Texto   | Nome social do candidato |
| NR_CPF_CANDIDATO               | Texto   | CPF do candidato (pode estar mascarado) |
| DS_EMAIL                       | Texto   | Email do candidato |
| CD_SITUACAO_CANDIDATURA        | Inteiro | Código da situação da candidatura |
| DS_SITUACAO_CANDIDATURA        | Texto   | Situação da candidatura (Apto, Indeferido, etc.) |
| TP_AGREMIACAO                  | Texto   | Tipo de agremiação (Partido/Federação) |
| NR_PARTIDO                     | Inteiro | Número do partido |
| SG_PARTIDO                     | Texto   | Sigla do partido |
| NM_PARTIDO                     | Texto   | Nome completo do partido |
| NR_FEDERACAO                   | Inteiro | Número da federação |
| NM_FEDERACAO                   | Texto   | Nome da federação |
| SG_FEDERACAO                   | Texto   | Sigla da federação |
| DS_COMPOSICAO_FEDERACAO        | Texto   | Partidos que compõem a federação |
| SQ_COLIGACAO                   | Inteiro | Identificador da coligação |
| NM_COLIGACAO                   | Texto   | Nome da coligação |
| DS_COMPOSICAO_COLIGACAO        | Texto   | Composição da coligação |
| SG_UF_NASCIMENTO               | Texto   | UF de nascimento do candidato |
| DT_NASCIMENTO                  | Data    | Data de nascimento |
| NR_TITULO_ELEITORAL_CANDIDATO  | Texto   | Número do título eleitoral |
| CD_GENERO                      | Inteiro | Código do gênero |
| DS_GENERO                      | Texto   | Gênero do candidato |
| CD_GRAU_INSTRUCAO              | Inteiro | Código do grau de instrução |
| DS_GRAU_INSTRUCAO              | Texto   | Grau de instrução |
| CD_ESTADO_CIVIL                | Inteiro | Código do estado civil |
| DS_ESTADO_CIVIL                | Texto   | Estado civil |
| CD_COR_RACA                    | Inteiro | Código de cor/raça |
| DS_COR_RACA                    | Texto   | Cor/Raça |
| CD_OCUPACAO                    | Inteiro | Código da ocupação |
| DS_OCUPACAO                    | Texto   | Ocupação do candidato |
| CD_SIT_TOT_TURNO               | Inteiro | Código do resultado no turno |
| DS_SIT_TOT_TURNO               | Texto   | Resultado final (Eleito, Suplente, Não eleito) |

---

## 🔑 Chaves Importantes

* **SQ_CANDIDATO**: chave primária da base
* Combinação útil:

  * `SG_UF + NM_UE + DS_CARGO`

---

## ⚠️ Observações

* Campos `CD_*` representam códigos numéricos (podem ser usados como dimensões)
* Campos `DS_*` são descrições legíveis
* Nem todos os candidatos possuem coligação/federação
* CPF vem anonimizado

---

## 🧠 Uso no Projeto

Essa base pode ser usada para:

* Análise de perfil de candidatos
* Distribuição por partido e estado
* Indicadores eleitorais (KPIs)
* Modelagem dimensional (Data Warehouse)

---
