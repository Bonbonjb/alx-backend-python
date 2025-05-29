#!/usr/bin/env python3
"""Test suite for client.py"""

import unittest
from unittest.mock import patch, Mock
from parameterized import parameterized, parameterized_class
from client import GithubOrgClient
from fixtures import org_payload, repos_payload, expected_repos, apache2_repos


class TestGithubOrgClient(unittest.TestCase):
    """Unit tests for GithubOrgClient"""

    @parameterized.expand([
        ("google",),
        ("abc",)
    ])
    @patch('client.get_json', autospec=True)
    def test_org(self, org_name, mock_get_json):
        """Test GithubOrgClient.org returns correct value."""
        mock_get_json.return_value = {"payload": True}
        client = GithubOrgClient(org_name)
        result = client.org
        self.assertEqual(result, {"payload": True})
        mock_get_json.assert_called_once_with(client.ORG_URL.format(org=org_name))

    def test_public_repos_url(self):
        """Test GithubOrgClient._public_repos_url property."""
        client = GithubOrgClient("test_org")
        with patch.object(GithubOrgClient, "org", new_callable=property) as mock_org:
            mock_org.return_value = {"repos_url": "https://api.github.com/repos/test_org"}
            self.assertEqual(client._public_repos_url, "https://api.github.com/repos/test_org")

    @patch('client.get_json')
    def test_public_repos(self, mock_get_json):
        """Test GithubOrgClient.public_repos returns expected repos."""
        client = GithubOrgClient("test_org")

        payload = [
            {"name": "repo1", "license": {"key": "mit"}},
            {"name": "repo2", "license": {"key": "apache-2.0"}},
            {"name": "repo3", "license": {"key": "bsd"}}
        ]
        mock_get_json.return_value = payload
        with patch.object(GithubOrgClient, "_public_repos_url",
                          new_callable=property) as mock_public_repos_url:
            mock_public_repos_url.return_value = "https://api.github.com/repos/test_org"

            # No license filter
            repos = client.public_repos()
            self.assertEqual(repos, ["repo1", "repo2", "repo3"])

            # License filter
            repos_licensed = client.public_repos(license="apache-2.0")
            self.assertEqual(repos_licensed, ["repo2"])

            mock_public_repos_url.assert_called_once()
            mock_get_json.assert_called_once_with("https://api.github.com/repos/test_org")

    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other_license"}}, "my_license", False),
    ])
    def test_has_license(self, repo, license_key, expected):
        """Test GithubOrgClient.has_license static method."""
        result = GithubOrgClient.has_license(repo, license_key)
        self.assertEqual(result, expected)


@parameterized_class([
    {
        "org_payload": org_payload,
        "repos_payload": repos_payload,
        "expected_repos": expected_repos,
        "apache2_repos": apache2_repos,
    }
])
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """Integration tests for GithubOrgClient.public_repos"""

    @classmethod
    def setUpClass(cls):
        cls.get_patcher = patch('client.requests.get')
        cls.mock_get = cls.get_patcher.start()

        def side_effect(url, *args, **kwargs):
            mock_resp = Mock()
            if url == f"https://api.github.com/orgs/{cls.org_payload['payload']['login']}":
                mock_resp.json.return_value = cls.org_payload["payload"]
            elif url == cls.org_payload["payload"]["repos_url"]:
                mock_resp.json.return_value = cls.repos_payload["payload"]
            else:
                mock_resp.json.return_value = {}
            return mock_resp

        cls.mock_get.side_effect = side_effect

    @classmethod
    def tearDownClass(cls):
        cls.get_patcher.stop()

    def setUp(self):
        # Assign patcher to instance attribute to satisfy tests expecting self.get_patcher
        self.get_patcher = self.__class__.get_patcher

    def test_public_repos(self):
        client = GithubOrgClient(self.org_payload["payload"]["login"])
        repos = client.public_repos()
        self.assertEqual(repos, self.expected_repos)

    def test_public_repos_with_license(self):
        client = GithubOrgClient(self.org_payload["payload"]["login"])
        repos = client.public_repos(license="apache-2.0")
        self.assertEqual(repos, self.apache2_repos)
    def test_public_repos_with_license(self):
        """Test public_repos filters repos by license key."""
        client = GithubOrgClient(self.org_payload["payload"]["login"])
        repos = client.public_repos(license="apache-2.0")
        self.assertEqual(repos, self.apache2_repos)
