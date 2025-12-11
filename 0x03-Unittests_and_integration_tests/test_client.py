#!/usr/bin/env python3
"""Test client module."""
import unittest
from parameterized import parameterized, parameterized_class
from unittest.mock import patch, PropertyMock
from .client import GithubOrgClient
from . import client
from .fixtures import org_payload, repos_payload, expected_repos, apache2_repos


class TestGithubOrgClient(unittest.TestCase):
    """Test GithubOrgClient class."""
    @parameterized.expand([
        ("google",),
        ("abc",),
    ])
    @patch.object(client, 'get_json')
    def test_org(self, org_name, mock_get_json):
        """Test org property."""
        client_obj = GithubOrgClient(org_name)
        client_obj.org
        url = f"https://api.github.com/orgs/{org_name}"
        mock_get_json.assert_called_once_with(url)

    def test_public_repos_url(self):
        """Test _public_repos_url property."""
        with patch.object(
                GithubOrgClient, "org", new_callable=PropertyMock
        ) as mock_org:
            repos_url = "http://example.com/org/repos"
            mock_org.return_value = {"repos_url": repos_url}
            client_obj = GithubOrgClient("google")
            self.assertEqual(client_obj._public_repos_url, repos_url)

    @patch.object(client, 'get_json')
    def test_public_repos(self, mock_get_json):
        """Test public_repos method."""
        mock_get_json.return_value = repos_payload
        with patch.object(
                GithubOrgClient, "_public_repos_url", new_callable=PropertyMock
        ) as mock_url:
            repos_url = "http://example.com/org/repos"
            mock_url.return_value = repos_url
            client_obj = GithubOrgClient("google")
            self.assertEqual(client_obj.public_repos(), expected_repos)
            mock_url.assert_called_once()
            mock_get_json.assert_called_once_with(repos_url)

    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other_license"}}, "my_license", False),
    ])
    def test_has_license(self, repo, license_key, expected):
        """Test has_license method."""
        result = GithubOrgClient.has_license(repo, license_key)
        self.assertEqual(result, expected)


@parameterized_class(
    ("org_payload", "repos_payload", "expected_repos", "apache2_repos"),
    [(org_payload, repos_payload, expected_repos, apache2_repos)]
)
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """Integration tests for GithubOrgClient."""
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures."""
        url_to_payload = {
            f"https://api.github.com/orgs/google": cls.org_payload,
            cls.org_payload.get("repos_url"): cls.repos_payload,
        }

        def mocked_get(url):
            """Mock requests.get."""
            class MockResponse:
                """Mock response class."""

                def __init__(self, payload):
                    """Initialize mock response."""
                    self._payload = payload

                def json(self):
                    """Return JSON payload."""
                    return self._payload
            return MockResponse(url_to_payload[url])

        cls.get_patcher = patch("requests.get", side_effect=mocked_get)
        cls.get_patcher.start()

    @classmethod
    def tearDownClass(cls):
        """Tear down test fixtures."""
        cls.get_patcher.stop()

    def test_public_repos(self):
        """Test public_repos integration."""
        client_obj = GithubOrgClient("google")
        self.assertEqual(client_obj.public_repos(), self.expected_repos)

    def test_public_repos_with_license(self):
        """Test public_repos with license filter."""
        client_obj = GithubOrgClient("google")
        result = client_obj.public_repos(license="apache-2.0")
        self.assertEqual(result, self.apache2_repos)
