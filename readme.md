# 📊 GitHub Team Retrospective

Ferramenta para gerar retrospectivas de time baseada em métricas do GitHub, analisando repositórios de uma organização. 

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