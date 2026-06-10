# Projeto Integrador Aplicado em Ciência de Dados e IA - I — Faculdade IESB

# Metodologia e Estrutura Tecnológica do Projeto

Para a construção da aplicação e processamento dos dados abertos do Tribunal Superior Eleitoral (TSE) relativos a candidatos e patrimonios, foi desenvolvido um ecossistema tecnológico robusto focado em escalabilidade, integridade de dados e análise analítica. 

O desenvolvimento foi estruturado em três pilares principais: desenvolvimento base, tratamento de dados (ETL) e visualização de indicadores.

## 1. Arquitetura de Software e Ferramentas Utilizadas

* **Gestão e Versionamento:** O **GitHub** foi a plataforma adotada para a hospedagem do código-fonte e controle de versão. Para além do repositório, utilizou-se a funcionalidade de projetos organizada em raias (colunas de fluxo de trabalho como *To Do*, *In Progress* e *Done*), o que permitiu uma gestão visual ágil, transparente e eficiente no desenvolvimento de cada atividade.
* **Desenvolvimento e Persistência:** A aplicação foi integrada ao ecossistema **Python** através do framework **Django**, utilizado pela sua robustez no gerenciamento de requisições, segurança nativa e facilidade de integração. Como camada de persistência, utilizou-se o banco de dados relacional **PostgreSQL**, ideal para suportar o volume e a complexidade das tabelas eleitorais.
* **Processamento e Limpeza (ETL):** Devido à natureza bruta dos dados públicos, a biblioteca **Pandas** desempenhou um papel fundamental. Através dela, os dados foram estruturados em *dataframes*, permitindo a identificação e tratamento de valores nulos, além da conversão precisa de tipos de dados — como a padronização de datas e campos monetários dos bens declarados —, garantindo a integridade da informação antes da inserção no banco de dados.
* **Visualização e Indicadores:** A entrega dos resultados foi desenhada em duas frentes de *Business Intelligence*. Internamente, a aplicação utilizou a biblioteca **Chart.js** para renderizar gráficos dinâmicos, interativos e leves na própria interface do usuário. Complementarmente, o **Power BI** foi adotado como ferramenta especialista para a modelagem de indicadores macro, permitindo uma exploração visual avançada e a geração de *dashboards* analíticos detalhados sobre o perfil dos candidatos e partidos.

## 2. Organização do Repositório (GitHub)

Para garantir a reprodutibilidade, governança dos dados e a colaboração contínua no desenvolvimento do projeto, o código-fonte e as documentações foram organizados em um repositório Git. A estrutura de diretórios segue as melhores práticas de projetos de engenharia de dados, dividindo-se da seguinte forma:

* **`data/raw`:** Diretório destinado ao armazenamento dos arquivos brutos (*raw data*) extraídos diretamente da base aberta do TSE. Manter esses arquivos isolados garante que a fonte original dos dados de candidatos e bens seja preservada sem modificações prévias para auditorias futuras.
* **`docs`:** Pasta central de documentação técnica do projeto. Nela encontram-se os arquivos de subdiretório do banco de dados contendo os scripts `ddl.sql` (responsáveis pela criação das tabelas, *views* e restrições no PostgreSQL), além do mapeamento e definição dos Indicadores-Chave de Desempenho (KPIs) selecionados para guiar as abordagens analíticas do trabalho.
* **`powerbi`:** Espaço reservado para os arquivos de desenvolvimento e relatórios do Power BI (`.pbix`). Este diretório centraliza os painéis construídos para o consumo dos indicadores macro e análises de desempenho dos partidos políticos e candidatos.
* **`references`:** Contém os materiais de referência iniciais do projeto, incluindo os escopos, as diretrizes e a solicitação inicial que originou o desenvolvimento do trabalho, servindo como base de validação dos requisitos.
* **`reports`:** Diretório focado nos relatórios gerados ao longo do projeto. Inclui os dicionários de dados e o dicionário de KPIs, essenciais para que os usuários finais e analistas entendam o significado e a regra de negócio por trás de cada campo e métrica calculada.
* **`src`:** Pasta que concentra o código-fonte (*source code*) da aplicação em Python e Django. É neste diretório que residem a lógica do sistema, as rotas, a configuração do framework e as rotinas automatizadas do pipeline de ETL desenvolvidas com o Pandas.

## Agradecimentos

Expressamos nosso agradecimento ao **Professor Regiano Alves** pela orientação, suporte técnico e direcionamento estratégico ao longo do desenvolvimento deste projeto. Suas contribuições foram fundamentais para a definição das abordagens analíticas, estruturação e amadurecimento da arquitetura de dados aqui implementada.
