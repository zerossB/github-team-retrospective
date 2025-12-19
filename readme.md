# 📊 GitHub Team Retrospective

Tool to generate team retrospectives based on GitHub metrics, analyzing an organization's repositories.

## ✨ Features

- 📈 **Commits**: Totals, by author, by repository, timeline, and lines of code
- 🔀 **Pull Requests**: Full analysis including average merge time
- 🏷️ **Releases**: Versions released and timeline
- 🐛 **Issues**: Created, resolved, and resolution time
- 👥 **Code Review**: Participation and engagement in reviews
- 🏆 **Rankings**: Most active contributors
- 📅 **Timeline**: Monthly activity
- 🎨 **HTML Report**: Interactive dashboard with charts

## 🚀 Installation

```bash
# Clone the repository
git clone <your-repo>
cd github-team-retrospective

# Install dependencies
pip install -r requirements.txt

# Configure the project
cp config.yaml.example config.yaml
```

## ⚙️ Configuration

### 1. Generate a GitHub Token

1. Go to https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Give it a descriptive name (e.g., "Team Retrospective")
4. Select the scopes:
   - `repo` (full access to private repositories)
   - `read:org` (read organization info)
5. Click "Generate token"
6. **Copy the token immediately** (it will not be shown again)

### 2. Configure config.yaml

```yaml
# Organization settings
organization: "bildvitta"

# Repository list (leave empty to analyze all)
repositories:
  - "repo1"
  - "repo2"
  - "repo3"
  # or leave empty: []

# GitHub token (or use the GITHUB_TOKEN env var)
github_token: "your_token_here"

# Analysis period (optional)
start_date: "2025-01-01"  # leave null to use current date
end_date: null  # null = today

# Report options
output_dir: "reports"
output_format: ["html", "markdown"]  # Output formats
```

### 3. Using Environment Variables (Recommended)

Instead of putting the token in config.yaml, use an environment variable:

```bash
# Linux/Mac
export GITHUB_TOKEN="your_token_here"

# Windows (CMD)
set GITHUB_TOKEN=your_token_here

# Windows (PowerShell)
$env:GITHUB_TOKEN="your_token_here"
```

Or create a `.env` file:

```bash
GITHUB_TOKEN=your_token_here
```

### 4. Using Local Repositories (Optional - Reduces API Calls)

To significantly reduce GitHub API calls, you can analyze commits from local Git repositories instead of fetching them via API. Other data (PRs, issues, releases) will still be fetched from the API.

Add to your `config.yaml`:

```yaml
options:
  # Local repositories path - use {repo_name} as placeholder
  local_repos_path: "/path/to/repos/{repo_name}"
  # Windows example: "C:/Projects/{repo_name}"
  # Linux/Mac example: "/home/user/projects/{repo_name}"
```

**Requirements:**
- Repositories must be cloned locally
- GitPython package must be installed (included in dependencies)
- The path must contain `{repo_name}` which will be replaced with each repository name

**Benefits:**
- Dramatically reduces API rate limit usage
- Faster commit analysis for large repositories
- Automatically falls back to API if local repo not found

## 📖 Usage

### Basic Mode

```bash
python src/main.py
```

### With Arguments

```bash
# Specify organization and repositories
python src/main.py --org bildvitta --repos "repo1,repo2,repo3"

# Specify period
python src/main.py --start-date 2025-01-01 --end-date 2025-12-15

# Analyze all organization repositories
python src/main.py --org bildvitta --all-repos

# Help
python src/main.py --help
```

## 📊 Metrics Collected

### Commits
- Total commits in the period
- Commits by author
- Commits by repository
- Lines added/removed
- Monthly commits timeline
- Activity by day of the week

### Pull Requests
- Total PRs (open, merged, closed)
- PRs by author and repository
- Average merge time
- PR size (lines changed)
- Approval rate

### Releases
- Total releases by repository
- Release timeline
- Release frequency

### Issues
- Issues created and closed
- Issues by author
- Average resolution time
- Open issues

### Code Review
- PR comments by reviewer
- Approved/rejected reviews
- Participation in code reviews
- Average response time

### Other
- Most active contributors
- Most used languages
- Most active repositories
- Activity heatmap

## 📁 Project Structure

```
github-team-retrospective/
├── README.md
├── requirements.txt
├── config.yaml.example
├── .gitignore
├── .env.example
├── src/
│   ├── __init__.py
│   ├── main.py              # Main script
│   ├── github_client.py     # GitHub API client
│   ├── metrics_collector.py # Metrics collection
│   ├── report_generator.py  # Report generation
│   └── utils.py             # Utility functions
├── templates/
│   └── report_template.html # Report template
└── reports/                 # Generated reports (auto-created)
```

## 🎨 Report Example

The generated HTML report includes:

- 📊 Overview dashboard
- 📈 Interactive charts (line, bar, pie)
- 📋 Ranking tables
- 🗓️ Activity timeline
- 🏆 Top contributors
- 📱 Responsive design

## 🔧 Troubleshooting

### Authentication Error

```
Error: Bad credentials
```

**Solution**: Check that your token is correct and has the required permissions (`repo` and `read:org`).

### Rate Limit Exceeded

```
Error: API rate limit exceeded
```

**Solution**: The GitHub API has request limits. The script will wait automatically. For authenticated tokens: 5000 requests/hour.

### Repository Not Found

```
Error: Repository not found
```

**Solution**: Confirm that:
- The repository name is correct
- Your token has access to the private repository
- You have read permission on the repository

### No Data in the Period

```
Warning: No data found for the specified period
```

**Solution**: Verify there is activity in the repositories for the specified period.

## 🔒 Security

⚠️ **IMPORTANT**: Never commit your GitHub token!

- Use environment variables
- Add `config.yaml` and `.env` to `.gitignore`
- Revoke unused tokens
- Use tokens with the minimum necessary permissions

## 🤝 Contributing

Contributions are welcome! Feel free to:

- Report bugs
- Suggest new metrics
- Improve documentation
- Submit pull requests

## 📝 License

MIT License - see LICENSE for details

## 👨‍💻 Author

Created to simplify team retrospectives and productivity analysis.

---

**💡 Tip**: Run the script monthly to track your team's progress throughout the year!
﻿# 📊 GitHub Team Retrospective

Tool to generate team retrospectives based on GitHub metrics, analyzing an organization's repositories. 

## ✨ Funcionalidades

- 📈 **Commits**: Total, por autor, por repositório, timeline e linhas de código
- 🔀 **Pull Requests**:  Análise completa incluindo tempo médio de merge
- 🏷️ **Releases**: Versões lançadas e timeline
- 🐛 **Issues**: Criadas, resolvidas e tempo de resolução
- 👥 **Code Review**: Participação e engajamento em reviews
- 🏆 **Rankings**: Contribuidores mais ativos
- 📅 **Timeline**: Atividade por mês
- 🎨 **Relatório HTML**: Dashboard interativo com gráficos

## 🚀 Instalação

```bash
# Clone o repositório
git clone <seu-repo>
cd github-team-retrospective

# Instale as dependências
pip install -r requirements.txt

# Configure o projeto
cp config.yaml.example config.yaml
```

## ⚙️ Configuração

### 1. Gerar Token do GitHub

1. Acesse: https://github.com/settings/tokens
2. Clique em "Generate new token (classic)"
3. Dê um nome descritivo (ex: "Team Retrospective")
4. Selecione os escopos: 
   - `repo` (acesso completo a repositórios privados)
   - `read:org` (ler informações da organização)
5. Clique em "Generate token"
6. **Copie o token imediatamente** (não será mostrado novamente)

### 2. Configurar o arquivo config.yaml

```yaml
# Configuração da organização
organization: "bildvitta"

# Lista de repositórios (deixe vazio para analisar todos)
repositories:
  - "repo1"
  - "repo2"
  - "repo3"
  # ou deixe vazio:  []

# Token do GitHub (ou use variável de ambiente GITHUB_TOKEN)
github_token: "seu_token_aqui"

# Período de análise (opcional)
start_date: "2025-01-01"  # deixe null para usar data atual
end_date: null  # null = hoje

# Opções de relatório
output_dir: "reports"
output_format: ["html", "markdown"]  # Formatos de saída
```

### 3. Usando Variável de Ambiente (Recomendado)

Em vez de colocar o token no config.yaml, use variável de ambiente:

```bash
# Linux/Mac
export GITHUB_TOKEN="seu_token_aqui"

# Windows (CMD)
set GITHUB_TOKEN=seu_token_aqui

# Windows (PowerShell)
$env:GITHUB_TOKEN="seu_token_aqui"
```

Ou crie um arquivo `.env`:

```bash
GITHUB_TOKEN=seu_token_aqui
```

## 📖 Uso

### Modo Básico

```bash
python src/main.py
```

### Com Argumentos

```bash
# Especificar organização e repositórios
python src/main.py --org bildvitta --repos "repo1,repo2,repo3"

# Especificar período
python src/main.py --start-date 2025-01-01 --end-date 2025-12-15

# Analisar todos os repositórios da org
python src/main.py --org bildvitta --all-repos

# Ajuda
python src/main.py --help
```

## 📊 Métricas Coletadas

### Commits
- Total de commits no período
- Commits por autor
- Commits por repositório
- Linhas adicionadas/removidas
- Timeline mensal de commits
- Atividade por dia da semana

### Pull Requests
- Total de PRs (abertos, mergeados, fechados)
- PRs por autor e repositório
- Tempo médio de merge
- Tamanho dos PRs (linhas alteradas)
- Taxa de aprovação

### Releases
- Total de releases por repositório
- Timeline de lançamentos
- Frequência de releases

### Issues
- Issues criadas e fechadas
- Issues por autor
- Tempo médio de resolução
- Issues em aberto

### Code Review
- Comentários em PRs por revisor
- Reviews aprovados/rejeitados
- Participação em code reviews
- Tempo médio de resposta

### Outros
- Contribuidores mais ativos
- Linguagens mais utilizadas
- Repositórios mais ativos
- Heatmap de atividades

## 📁 Estrutura do Projeto

```
github-team-retrospective/
├── README.md
├── requirements.txt
├── config.yaml.example
├── .gitignore
├── . env. example
├── src/
│   ├── __init__.py
│   ├── main. py              # Script principal
│   ├── github_client.py     # Cliente da API do GitHub
│   ├── metrics_collector.py # Coleta de métricas
│   ├── report_generator. py  # Geração de relatórios
│   └── utils.py             # Funções utilitárias
├── templates/
│   └── report_template.html # Template do relatório
└── reports/                 # Relatórios gerados (criado automaticamente)
```

## 🎨 Exemplo de Relatório

O relatório HTML gerado inclui: 

- 📊 Dashboard com visão geral
- 📈 Gráficos interativos (linha, barra, pizza)
- 📋 Tabelas de rankings
- 🗓️ Timeline de atividades
- 🏆 Top contribuidores
- 📱 Design responsivo

## 🔧 Troubleshooting

### Erro de Autenticação

```
Error: Bad credentials
```

**Solução**: Verifique se seu token está correto e tem as permissões necessárias (`repo` e `read:org`).

### Rate Limit Excedido

```
Error: API rate limit exceeded
```

**Solução**: A API do GitHub tem limite de requisições.  O script aguardará automaticamente.  Para tokens autenticados:  5000 requisições/hora.

### Repositório Não Encontrado

```
Error: Repository not found
```

**Solução**: Verifique se: 
- O nome do repositório está correto
- Seu token tem acesso ao repositório privado
- Você tem permissão de leitura no repositório

### Sem Dados no Período

```
Warning: No data found for the specified period
```

**Solução**: Verifique se há atividade nos repositórios no período especificado.

## 🔒 Segurança

⚠️ **IMPORTANTE**:  Nunca commite seu token do GitHub! 

- Use variáveis de ambiente
- Adicione `config.yaml` e `.env` ao `.gitignore`
- Revogue tokens não utilizados
- Use tokens com permissões mínimas necessárias

## 🤝 Contribuindo

Contribuições são bem-vindas! Sinta-se à vontade para: 

- Reportar bugs
- Sugerir novas métricas
- Melhorar a documentação
- Enviar pull requests

## 📝 Licença

MIT License - veja arquivo LICENSE para detalhes

## 👨‍💻 Autor

Criado para facilitar retrospectivas de time e análise de produtividade.

---

**💡 Dica**: Execute o script mensalmente para acompanhar a evolução do seu time ao longo do ano! 