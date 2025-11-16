#!/usr/bin/env python3
import unittest
from parameterized import parameterized, parameterized_class
from unittest.mock import patch, PropertyMock
from .client import GithubOrgClient
from . import client as client_module
from .fixtures import org_payload, repos_payload, expected_repos, apache2_repos


class TestGithubOrgClient(unittest.TestCase):
    @parameterized.expand([
        ("google",),
        ("abc",),
    ])
    @patch.object(client_module, "get_json")
    def test_org(self, org_name, mock_get_json):
        client = GithubOrgClient(org_name)
        client.org
        mock_get_json.assert_called_once_with(f"https://api.github.com/orgs/{org_name}")

    def test_public_repos_url(self):
        with patch.object(GithubOrgClient, "org", new_callable=PropertyMock) as mock_org:
            mock_org.return_value = {"repos_url": "http://example.com/org/repos"}
            client = GithubOrgClient("google")
            self.assertEqual(client._public_repos_url, "http://example.com/org/repos")

    @patch.object(client_module, "get_json")
    def test_public_repos(self, mock_get_json):
        mock_get_json.return_value = repos_payload
        with patch.object(GithubOrgClient, "_public_repos_url", new_callable=PropertyMock) as mock_url:
            mock_url.return_value = "http://example.com/org/repos"
            client = GithubOrgClient("google")
            self.assertEqual(client.public_repos(), expected_repos)
            mock_url.assert_called_once()
            mock_get_json.assert_called_once_with("http://example.com/org/repos")

    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other_license"}}, "my_license", False),
    ])
    def test_has_license(self, repo, license_key, expected):
        self.assertEqual(GithubOrgClient.has_license(repo, license_key), expected)


@parameterized_class(("org_payload", "repos_payload", "expected_repos", "apache2_repos"), [(org_payload, repos_payload, expected_repos, apache2_repos)])
class TestIntegrationGithubOrgClient(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        url_to_payload = {
            f"https://api.github.com/orgs/google": cls.org_payload,
            cls.org_payload.get("repos_url"): cls.repos_payload,
        }

        def mocked_get(url):
            class MockResponse:
                def __init__(self, payload):
                    self._payload = payload
                def json(self):
                    return self._payload
            return MockResponse(url_to_payload[url])

        cls.get_patcher = patch("requests.get", side_effect=mocked_get)
        cls.get_patcher.start()

    @classmethod
    def tearDownClass(cls):
        cls.get_patcher.stop()

    def test_public_repos(self):
        client = GithubOrgClient("google")
        self.assertEqual(client.public_repos(), self.expected_repos)

    def test_public_repos_with_license(self):
        client = GithubOrgClient("google")
        self.assertEqual(client.public_repos(license="apache-2.0"), self.apache2_repos)
