"""
Git utilities for the purpose of exploring, cloning, and parsing llama-deploy repositories.
Responsibilities are lower level git access, as well as some application specific config parsing.
"""

from dataclasses import dataclass
import re
import subprocess
from pathlib import Path
import tempfile

import yaml


def parse_github_repo_url(repo_url: str) -> tuple[str, str]:
    """
    Parse GitHub repository URL to extract owner and repo name.

    Args:
        repo_url: GitHub repository URL (various formats supported)

    Returns:
        Tuple of (owner, repo_name)

    Raises:
        ValueError: If URL format is not recognized
    """
    # Remove .git suffix if present
    url = repo_url.rstrip("/").removesuffix(".git")

    # Handle different GitHub URL formats
    patterns = [
        r"https://github\.com/([^/]+)/([^/]+)",
        r"git@github\.com:([^/]+)/([^/]+)",
        r"github\.com/([^/]+)/([^/]+)",
    ]

    for pattern in patterns:
        match = re.match(pattern, url)
        if match:
            return match.group(1), match.group(2)

    raise ValueError(f"Could not parse GitHub repository URL: {repo_url}")


def inject_basic_auth(url: str, basic_auth: str | None = None) -> str:
    """Inject basic auth into a URL if provided"""
    if basic_auth and "://" in url and "@" not in url:
        url = url.replace("https://", f"https://{basic_auth}@")
    return url


def _run_process(args: list[str], cwd: str | None = None) -> str:
    """Run a process and raise an exception if it fails"""
    result = subprocess.run(
        args, cwd=cwd, capture_output=True, text=True, check=True, timeout=30
    )
    if result.returncode != 0:
        raise subprocess.CalledProcessError(
            result.returncode, args, result.stdout, result.stderr
        )
    return result.stdout.strip()


class GitAccessError(Exception):
    """Error raised when a user reportable git error occurs, e.g connection fails, cannot access repository, timeout, ref not found, etc."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


@dataclass
class GitCloneResult:
    git_sha: str
    git_ref: str | None = None


def clone_repo(
    repository_url: str,
    git_ref: str | None = None,
    basic_auth: str | None = None,
    dest_dir: Path | str | None = None,
) -> GitCloneResult:
    """
    Clone a repository and checkout a specific ref, if provided. If user reportable access errors occur, raises a GitAccessError.

    Args:
        repository_url: The URL of the repository to clone
        git_ref: The git reference to checkout, if provided
        basic_auth: The basic auth to use to clone the repository
        dest_dir: The directory to clone the repository to, if provided

    Returns:
        GitCloneResult: A dataclass containing the git SHA and resolved git ref (e.g. main if None was provided)
    """
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            dest_dir = Path(temp_dir) if dest_dir is None else Path(dest_dir)
            authenticated_url = inject_basic_auth(repository_url, basic_auth)
            did_exist = (
                dest_dir.exists() and dest_dir.is_dir() and list(dest_dir.iterdir())
            )
            if not did_exist:
                # need to do a full clone to resolve any kind of ref without exploding in
                # complexity (tag, branch, commit, short commit)
                clone_args = [
                    "git",
                    "clone",
                    authenticated_url,
                    str(dest_dir.absolute()),
                ]
                _run_process(clone_args)

            if not git_ref:
                resolved_branch = _run_process(
                    ["git", "branch", "--show-current"],
                    cwd=str(dest_dir.absolute()),
                )
                if resolved_branch:
                    git_ref = resolved_branch
                else:
                    try:
                        resolved_tag = _run_process(
                            ["git", "describe", "--tags", "--exact-match"],
                            cwd=str(dest_dir.absolute()),
                        )
                        if resolved_tag:
                            git_ref = resolved_tag
                    except subprocess.CalledProcessError:
                        pass
            else:  # Checkout the ref
                if did_exist:
                    try:
                        _run_process(
                            ["git", "fetch", "origin"], cwd=str(dest_dir.absolute())
                        )
                    except subprocess.CalledProcessError:
                        raise GitAccessError("Failed to resolve git reference")
                try:
                    _run_process(
                        ["git", "checkout", git_ref], cwd=str(dest_dir.absolute())
                    )
                except subprocess.CalledProcessError as e:
                    # Check error message to determine if it's a network issue or ref not found
                    if "unable to access" in str(
                        e.stderr
                    ) or "fatal: unable to access repository" in str(e.stderr):
                        raise GitAccessError("Failed to resolve git reference")
                    else:
                        raise GitAccessError(f"Commit SHA '{git_ref}' not found")
            # if no ref, stay on whatever the clone gave us/current commit
            # return the resolved sha
            resolved_sha = _run_process(
                ["git", "rev-parse", "HEAD"], cwd=str(dest_dir.absolute())
            ).strip()
            return GitCloneResult(git_sha=resolved_sha, git_ref=git_ref)
    except subprocess.TimeoutExpired:
        raise GitAccessError("Timeout while cloning repository")


def validate_deployment_file(repo_dir: Path, deployment_file_path: str) -> bool:
    """
    Validate that the deployment file exists in the repository.

    Args:
        repo_dir: The directory of the repository
        deployment_file_path: The path to the deployment file, relative to the repository root

    Returns:
        True if the deployment file exists and appears to be valid, False otherwise
    """
    deployment_file = repo_dir / deployment_file_path
    if not deployment_file.exists():
        return False
    with open(deployment_file, "r") as f:
        try:
            loaded = yaml.safe_load(f)
            if not isinstance(loaded, dict):
                return False
            if "name" not in loaded:
                return False
            if not isinstance(loaded["name"], str):
                return False
            if "services" not in loaded:
                return False
            if not isinstance(loaded["services"], dict):
                return False
            return True  # good nuff for now. Eventually this should parse it into a model validated format
        except yaml.YAMLError:
            return False


async def validate_git_public_access(repository_url: str) -> bool:
    """Check if a git repository is publicly accessible using git ls-remote."""

    try:
        result = subprocess.run(
            ["git", "ls-remote", "--heads", repository_url],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,  # Don't raise on non-zero exit
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, Exception):
        return False


async def validate_git_credential_access(repository_url: str, basic_auth: str) -> bool:
    """Check if a credential provides access to a git repository."""

    auth_url = inject_basic_auth(repository_url, basic_auth)
    try:
        result = subprocess.run(
            ["git", "ls-remote", "--heads", auth_url],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, Exception):
        return False
