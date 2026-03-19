# 📊 Dicionário de Dados — TSE 2024

Fonte: Tribunal Superior Eleitoral (TSE)
Arquivo: `consulta_cand_2024_BRASIL.csv`

---

## 📁 Descrição Geral

Esta base contém informações cadastrais e eleitorais dos candidatos das eleições de 2024 no Brasil.

---

## 🧾 Campos da Base

| Coluna                  | Tipo    | Descrição                                |
| ----------------------- | ------- | ---------------------------------------- |
| ANO_ELEICAO             | Inteiro | Ano da eleição                           |
| SG_UF                   | Texto   | Unidade federativa do candidato          |
| NM_UE                   | Texto   | Município da candidatura                 |
| DS_CARGO                | Texto   | Cargo disputado (Prefeito, Vereador)     |
| SQ_CANDIDATO            | Inteiro | Identificador único do candidato         |
| NR_CANDIDATO            | Inteiro | Número do candidato                      |
| NM_CANDIDATO            | Texto   | Nome completo                            |
| NM_URNA_CANDIDATO       | Texto   | Nome na urna                             |
| SG_PARTIDO              | Texto   | Sigla do partido                         |
| NM_PARTIDO              | Texto   | Nome do partido                          |
| DS_SITUACAO_CANDIDATURA | Texto   | Situação (Deferido, Indeferido, etc.)    |
| DS_SIT_TOT_TURNO        | Texto   | Resultado final (Eleito, Suplente, etc.) |
| DS_GENERO               | Texto   | Gênero                                   |
| DS_GRAU_INSTRUCAO       | Texto   | Grau de instrução                        |
| DS_COR_RACA             | Texto   | Cor/Raça                                 |
| DS_OCUPACAO             | Texto   | Ocupação                                 |
| DT_NASCIMENTO           | Data    | Data de nascimento                       |

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
