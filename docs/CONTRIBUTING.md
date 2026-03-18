## Fluxo de Trabalho

1. Criar Issue
2. Criar branch vinculada
3. Desenvolver
4. Commit com Refs #n
5. Abrir PR
6. Revisão
7. Merge com Closes #n

## Diretrizes de Desenvolvimento

### 🔹 Organização das tarefas
- Cada atividade deve estar vinculada a uma Issue
- Nome da branch deve seguir o padrão:
  - feature/nome-da-tarefa
  - exemplo: feature/matriz-kpi

---

### 🔹 Alteração de arquivos
- Toda modificação deve ser feita em uma branch (não usar a main)
- Arquivos devem ser organizados nas pastas corretas
- Evitar subir arquivos grandes (ex: .zip, .csv grandes)

---

### 🔹 Commits
- Devem ser claros e objetivos
- Sempre referenciar a Issue:
  - Ex: "Implementa cálculo de KPI Refs #4"

---

### 🔹 Pull Request (PR)
- Deve conter descrição do que foi feito
- Informar se a tarefa está completa ou em revisão
- Usar:
  - Refs #n → quando ainda não finalizado
  - Closes #n → apenas quando concluído

---

### 🔹 Revisão
- Nenhuma tarefa deve ser considerada concluída sem revisão
- Validar com todos os integrantes antes do merge

---

### 🔹 Estrutura de dados
- Dados brutos devem ficar em /data/raw
- Dados tratados em /data/processed
- Scripts em /src ou /notebooks