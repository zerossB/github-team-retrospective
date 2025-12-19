# 📊 GitHub Team Retrospective

Tool to generate team retrospectives based on GitHub metrics, analyzing an organization's repositories.

## ✨ Features

- 📈 **Commits**: Total, by author, by repository, timeline, and lines of code
- 🔀 **Pull Requests**: Complete analysis including average merge time
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

1. Go to: https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Give it a descriptive name (e.g., "Team Retrospective")
4. Select the scopes:
   - `repo` (full access to private repositories)
   - `read:org` (read organization information)
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

# GitHub token (or use GITHUB_TOKEN environment variable)
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

### 4. Configure Caching (Optional)

The system has file-based caching to reduce calls to the GitHub API. Configure in `config.yaml`:

```yaml
# Cache configuration (file-based cache)
cache:
  # Enable or disable cache
  enabled: true
  # Cache directory (relative or absolute path)
  dir: ".cache"
  # Time to live in hours (how long cached data is valid)
  ttl_hours: 24
```

**Benefits of caching:**

- Significantly reduce GitHub API calls
- Speed up subsequent executions for the same period
- Save repository metrics data locally
- Automatic caching with configurable expiration

**Cache management:**

```bash
# View cache statistics
python cache_cli.py stats

# View cache configuration
python cache_cli.py info

# Clear expired cache
python cache_cli.py clear

# Clear all cache
python cache_cli.py clear --all

# Clear cache older than X hours
python cache_cli.py clear --older-than 48
```

### 5. Using Local Repositories (Optional - Reduces API Calls)

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

## � Project Structure

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
│   ├── cache_manager.py     # Cache management
│   └── utils.py             # Utility functions
├── templates/
│   └── report_template.html # Report template
├── .cache/                  # Cache directory (auto-created)
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

**Solution**: Verify that:
- The repository name is correct
- Your token has access to the private repository
- You have read permission on the repository

### No Data in the Period

```
Warning: No data found for the specified period
```

**Solution**: Check if there is activity in the repositories for the specified period.

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

MIT License - see LICENSE file for details

## 👨‍💻 Author

Created to simplify team retrospectives and productivity analysis.

---

**💡 Tip**: Run the script monthly to track your team's progress throughout the year!