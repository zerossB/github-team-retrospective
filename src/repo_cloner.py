"""
Utilities to clone or update GitHub repositories locally for offline analysis.
"""

import logging
from pathlib import Path
from typing import Dict, Iterable

try:
    from git import Repo, GitCommandError, InvalidGitRepositoryError
    GITPYTHON_AVAILABLE = True
except ImportError:
    GITPYTHON_AVAILABLE = False

logger = logging.getLogger(__name__)


def _build_repo_path(base_template: str, repo_name: str) -> Path:
    """Resolve repository path using the template or appending the name."""
    if "{repo_name}" in base_template:
        return Path(base_template.replace("{repo_name}", repo_name)).expanduser()
    return Path(base_template).expanduser() / repo_name


def clone_or_update_repositories(
    organization: str, repo_names: Iterable[str], base_path_template: str, token: str
) -> Dict[str, str]:
    """
    Clone or pull the requested repositories.

    Args:
        organization: GitHub organization/owner name.
        repo_names: List of repository names to process.
        base_path_template: Directory template (supports {repo_name}).
        token: GitHub token for authentication.

    Returns:
        Mapping of repo name to action performed ("cloned" or "updated").
    """
    if not GITPYTHON_AVAILABLE:
        raise RuntimeError("GitPython is required for --clone-local. Install gitpython first.")

    results: Dict[str, str] = {}
    repo_names = list(repo_names)

    for repo_name in repo_names:
        target_path = _build_repo_path(base_path_template, repo_name)
        target_path.parent.mkdir(parents=True, exist_ok=True)
        repo_url = f"https://{token}@github.com/{organization}/{repo_name}.git" if token else f"https://github.com/{organization}/{repo_name}.git"

        if target_path.exists():
            try:
                repo = Repo(target_path)
                try:
                    repo.remotes.origin.set_url(repo_url)
                except Exception:
                    # Best-effort; keep going if set_url fails
                    pass

                repo.remotes.origin.pull()
                results[repo_name] = "updated"
                continue
            except InvalidGitRepositoryError:
                raise RuntimeError(f"Existing path is not a git repo: {target_path}")
            except GitCommandError as exc:
                logger.warning("Failed to pull %s: %s", repo_name, exc)
                results[repo_name] = "skipped (pull failed)"
                continue

        # Clone fresh copy
        try:
            Repo.clone_from(repo_url, target_path)
            results[repo_name] = "cloned"
        except GitCommandError as exc:
            logger.warning("Failed to clone %s: %s", repo_name, exc)
            results[repo_name] = "skipped (clone failed)"

    return results
