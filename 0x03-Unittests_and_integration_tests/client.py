#!/usr/bin/env python3
from typing import Any, Dict, List
from .utils import get_json, memoize


class GithubOrgClient:
    def __init__(self, org_name: str) -> None:
        self._org_name = org_name

    @property
    def org(self) -> Dict[str, Any]:
        return get_json(f"https://api.github.com/orgs/{self._org_name}")

    @memoize
    def _public_repos_url(self) -> str:
        return self.org["repos_url"]

    def public_repos(self, license: str | None = None) -> List[str]:
        repos = get_json(self._public_repos_url)
        names = [repo["name"] for repo in repos]
        if license is None:
            return names
        return [r["name"] for r in repos if self.has_license(r, license)]

    @staticmethod
    def has_license(repo: Dict[str, Any], license_key: str) -> bool:
        license_info = repo.get("license") or {}
        return license_info.get("key") == license_key
