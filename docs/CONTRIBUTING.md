# Guia de Contribuição

Este documento define o padrão de contribuição do projeto.  
Siga estas diretrizes para garantir organização, rastreabilidade e qualidade.

---

## Fluxo de Trabalho

1. Criar Issue  
2. Criar branch vinculada  
3. Desenvolver  
4. Commit com `Refs #n`  
5. Abrir Pull Request (PR)  
6. Revisão  
7. Merge com `Closes #n`  

---

## Fluxo com comandos (passo a passo)

1. Atualizar a base do projeto 
git clone https://github.com/ivanmeirelesdeabreu/ProjetoIntegrador.git 
git checkout main  
git pull origin main  

git fetch origin
atualizar para um branch
git checkout 8-estruturação-e-documentação-de-metadados-da-fonte


2. Criar uma nova branch 
melhor ser criada no git-hub project (tarefa->create a branch)
git checkout -b tipo/nome-da-branch  

3. Adicionar arquivos  
git add .  

4. Realizar commit  
git commit -m "Descrição da alteração Refs #n"  

5. Enviar para o repositório remoto  
git push origin tipo/nome-da-branch  

6. Abrir Pull Request (PR)  
- Acessar o repositório no GitHub  
- Clicar em "Compare & pull request"  
- Descrever a alteração realizada  

7. Finalizar tarefa  
- Utilizar no PR:  
  Refs #n → tarefa em andamento  
  Closes #n → tarefa concluída  

---

## Padrão de Branches

Utilize o prefixo adequado conforme o tipo de tarefa:

feature/ → nova funcionalidade  
bugfix/ → correção de erro  
docs/ → documentação  
refactor/ → melhoria de código  

Exemplos:  
feature/matriz-kpi  
docs/contributing  
bugfix/erro-calculo  

---

## Diretrizes de Desenvolvimento

Organização das tarefas  
- Cada atividade deve estar vinculada a uma Issue  
- Sempre referenciar a Issue no commit e no PR  

Alteração de arquivos  
- Nunca trabalhar diretamente na main  
- Sempre utilizar branches  
- Organizar arquivos nas pastas corretas  
- Evitar subir arquivos grandes (ex: .zip, .csv grandes)  

Commits  
- Devem ser claros, objetivos e descritivos  
- Sempre referenciar a Issue  

Exemplo:  
git commit -m "Implementa cálculo de KPI Refs #4"  

Pull Request (PR)  
- Deve conter descrição do que foi feito  
- Informar se a tarefa está completa ou em revisão  

Exemplo:  
Implementa matriz de KPI baseada nos dados do projeto.  
Closes #4  

Revisão  
- Nenhuma tarefa deve ser considerada concluída sem revisão  
- Validar com todos os integrantes antes do merge  

---

## Estrutura de Dados

Dados brutos → /data/raw  
Dados tratados → /data/processed  
Scripts → /src ou /notebooks  

---

## Boas práticas

- Sempre atualizar a branch antes de iniciar o trabalho  
- Criar branch a partir da main atualizada  
- Evitar commits genéricos como:  
  git commit -m "teste"  
  git commit -m "ajuste"  

---

## Resumo

Issue → Branch → Commit → PR → Review → Merge