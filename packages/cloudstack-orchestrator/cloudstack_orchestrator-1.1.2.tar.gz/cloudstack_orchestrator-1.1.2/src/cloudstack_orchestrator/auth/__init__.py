"""Authentication module for CloudStack Orchestrator."""

from .github_oauth import GitHubDeviceFlow, GitHubAuthResult

__all__ = ["GitHubDeviceFlow", "GitHubAuthResult"]