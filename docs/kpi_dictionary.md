# KPI Dictionary — Projeto Eleições 2024


Este documento define os principais indicadores analíticos (KPIs) derivados da base do TSE.

**Objetivo do projeto**: Analisar o perfil dos candidatos na eleição de 2024, nos seguintes KPIs:

## KPIs que vão ser trabalhados

### 7. Distribuição por Escolaridade

* **Dimensão**: DS_GRAU_INSTRUCAO
---
### 9. Idade Média dos Candidatos

* **Cálculo**:

```sql
AVG(IDADE)
#(IDADE = ANO_ELEICAO - ANO(DT_NASCIMENTO))
```
---
### 11. Taxa de Sucesso por Partido

* **Descrição**: Percentual de candidatos eleitos por partido
* **Cálculo**:

```sql
COUNT(ELEITOS) / COUNT(TOTAL_PARTIDO)
```
---
### 13. Índice de Competitividade Eleitoral

* **Descrição**: Número médio de candidatos por vaga
* **Cálculo**:

```sql
TOTAL_CANDIDATOS / TOTAL_VAGAS
```
---
### 14. Diversidade de Gênero por Partido

* **Descrição**: Proporção de gênero dentro de cada partido
---

## KPIs Gerais

### 1. Total de Candidatos

* **Descrição**: Quantidade total de candidatos registrados
* **Cálculo**:

```sql
COUNT(SQ_CANDIDATO)
```

---

### 2. Candidatos por Estado

* **Descrição**: Distribuição de candidatos por UF
* **Dimensão**: SG_UF
* **Cálculo**:

```sql
COUNT(SQ_CANDIDATO) GROUP BY SG_UF
```

---

### 3. Candidatos por Cargo

* **Descrição**: Quantidade de candidatos por tipo de cargo
* **Dimensão**: DS_CARGO
* **Cálculo**:

```sql
COUNT(*) GROUP BY DS_CARGO
```

---

### 4. Taxa de Candidaturas Deferidas

* **Descrição**: Percentual de candidaturas aceitas
* **Cálculo**:

```sql
COUNT(CASE WHEN DS_SITUACAO_CANDIDATURA = 'DEFERIDO' THEN 1 END)
/ COUNT(*) * 100
```

---

### 5. Taxa de Eleitos

* **Descrição**: Percentual de candidatos eleitos
* **Cálculo**:

```sql
COUNT(CASE WHEN DS_SIT_TOT_TURNO = 'ELEITO' THEN 1 END)
/ COUNT(*) * 100
```

---

## KPIs Demográficos

### 6. Distribuição por Gênero

* **Dimensão**: DS_GENERO
* **Cálculo**:

```sql
COUNT(*) GROUP BY DS_GENERO
```

---

### 8. Distribuição por Cor/Raça

* **Dimensão**: DS_COR_RACA

---

## KPIs Políticos

### 10. Candidatos por Partido

* **Dimensão**: SG_PARTIDO

---

### 12. Concentração de Candidatos por Município

* **Dimensão**: NM_UE

---

## KPIs Avançados (Analíticos)

### 15. Taxa de Rejeição de Candidaturas

* **Descrição**: Percentual de candidaturas indeferidas
* **Cálculo**:

```sql
COUNT(INDEFERIDO) / COUNT(*) * 100
```

---

## Observações

* KPIs podem ser usados em dashboards (Power BI, Tableau, etc.)
* Ideal criar uma tabela fato + dimensões (modelo estrela)
* Pode evoluir para análise preditiva (ex: chance de eleição)

---
