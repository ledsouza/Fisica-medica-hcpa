# Aplicativo Web para Gestão do Serviço de Física Médica em Medicina Nuclear

Aplicativo desenvolvido para gestão e análise de dados do Serviço de Física Médica em Medicina Nuclear

| :books: Vitrine.Dev |     |
| -------------  | --- |
| :sparkles: Nome        | **Aplicativo Web para Gestão do Serviço de Física Médica em Medicina Nuclear**
| :label: Tecnologias | python, dotenv, pandas, plotly, numpy, pymongo, streamlit, yaml, boto3, terraform, docker, aws, gcp
| :rocket: URL         | [MNManagement](https://mnmanagement-xnb7n2zcnq-uc.a.run.app)

<!-- Inserir imagem com a #vitrinedev ao final do link -->
![](https://vitrinedev.s3.amazonaws.com/fmmnmanagement.png#vitrinedev)

## Detalhes do projeto

O aplicativo atualmente possui 3 funcionalidades principais:

### 1. Gestão de Usuários:
   - Permite acesso apenas aos usuários cadastrados, que têm permissão total no aplicativo.
   - Os usuários autenticados podem:
     - Redefinir senhas
     - Registrar novos usuários
     - Remover usuários
     - Atualizar detalhes do usuário
     - Registrar ou remover testes no banco de dados

### 2. Tratamento e Análise de Dados do PACS:
   - Os usuários podem importar dados do PACS para processamento e análise.
   - O tratamento de dados inclui anonimização, remoção de valores nulos ou fora do padrão, e aplicação de filtros personalizados.
   - São fornecidas estatísticas descritivas e visualizações gráficas para:
     - Atividade administrada em cada solicitação de exame
     - Distribuição da atividade administrada
     - Dose recebida pelos pacientes em cada solicitação de exame
     - Distribuição da dose recebida pelos pacientes
     - Correlação entre variáveis como atividade específica, atividade administrada, dose e peso.
   - Os dados processados e analisados estão disponíveis para download.

### 3. Gestão do Programa de Controle de Qualidade:
   - Apresenta uma dashboard com informações sobre os testes que devem ser realizados mensalmente.
   - Calcula indicadores de realização e arquivamento de testes em períodos selecionados pelo usuário.
   - Possui uma aba de arquivamento para gerenciar o desenvolvimento e armazenamento de relatórios dos testes realizados.
