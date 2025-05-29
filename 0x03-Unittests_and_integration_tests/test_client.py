#!/usr/bin/env python3
"""Unit and integration tests for client module."""

import unittest
from parameterized import parameterized, parameterized_class
from unittest.mock import patch, PropertyMock, Mock
from client import GithubOrgClient
from fixtures import org_payload, repos_payload, expected_repos, apache2_repos


class TestGithubOrgClient(unittest.TestCase):
    """Unit tests for GithubOrgClient."""

    @parameterized.expand([
        ("google",),
        ("abc",),
    ])
    @patch('client.get_json', autospec=True)
    def test_org(self, org_name, mock_get_json):
        """Test that org returns the expected value."""
        mock_get_json.return_value = {"login": org_name}
        client = GithubOrgClient(org_name)
        self.assertEqual(client.org, {"login": org_name})
        mock_get_json.assert_called_once_with(client.ORG_URL.format(org=org_name))

    def test_public_repos_url(self):
        """Test _public_repos_url property returns expected URL."""
        client = GithubOrgClient("test_org")
        with patch.object(GithubOrgClient, "org", new_callable=PropertyMock) as mock_org:
            mock_org.return_value = {"repos_url": "http://example.com/repos"}
            self.assertEqual(client._public_repos_url, "http://example.com/repos")

    @patch('client.get_json', autospec=True)
    def test_public_repos(self, mock_get_json):
        """Test public_repos returns expected list of repo names."""
        test_repos_payload = [
            {"name": "repo1", "license": {"key": "mit"}},
            {"name": "repo2", "license": {"key": "apache-2.0"}},
            {"name": "repo3", "license": None},
        ]
        mock_get_json.return_value = test_repos_payload
        client = GithubOrgClient("test_org")

        with patch.object(GithubOrgClient, "_public_repos_url", new_callable=PropertyMock) as mock_repos_url:
            mock_repos_url.return_value = "http://example.com/repos"
            repos = client.public_repos()
            self.assertEqual(repos, ["repo1", "repo2", "repo3"])
            mock_repos_url.assert_called_once()
            mock_get_json.assert_called_once_with("http://example.com/repos")

    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other_license"}}, "my_license", False),
    ])
    def test_has_license(self, repo, license_key, expected):
        """Test has_license returns expected boolean."""
        self.assertEqual(GithubOrgClient.has_license(repo, license_key), expected)


@parameterized_class([
    {
        "org_payload": org_payload,
        "repos_payload": repos_payload,
        "expected_repos": expected_repos,
        "apache2_repos": apache2_repos,
    }
])
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """Integration tests for GithubOrgClient.public_repos."""

    @classmethod
    def setUpClass(cls):
        """Set up patcher to mock requests.get for integration tests."""
        cls.get_patcher = patch('client.requests.get')
        cls.mock_get = cls.get_patcher.start()

        # Setup URLs based on fixture data
        cls.org_payload["url"] = f"https://api.github.com/orgs/{cls.org_payload['payload']['login']}"
        cls.repos_payload["url"] = cls.org_payload["payload"]["repos_url"]

        def get_json_side_effect(url, *args, **kwargs):
            mock_resp = Mock()
            if url == cls.org_payload["url"]:
                mock_resp.json.return_value = cls.org_payload["payload"]
            elif url == cls.repos_payload["url"]:
                mock_resp.json.return_value = cls.repos_payload["payload"]
            else:
                mock_resp.json.return_value = {}
            return mock_resp

        cls.mock_get.side_effect = get_json_side_effect

    @classmethod
    def tearDownClass(cls):
        """Stop patcher after tests."""
        cls.get_patcher.stop()

    def test_public_repos(self):
        """Test public_repos returns expected list of repo names."""
        client = GithubOrgClient(self.org_payload["payload"]["login"])
        repos = client.public_repos()
        self.assertEqual(repos, self.expected_repos)

    def test_public_repos_with_license(self):
        """Test public_repos filters repos by license key."""
        client = GithubOrgClient(self.org_payload["payload"]["login"])
        repos = client.public_repos(license="apache-2.0")
        self.assertEqual(repos, self.apache2_repos)
