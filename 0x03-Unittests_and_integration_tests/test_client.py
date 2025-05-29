#!/usr/bin/env python3
"""Unit tests for client module."""

import unittest
from parameterized import parameterized
from unittest.mock import patch, PropertyMock
from client import GithubOrgClient


class TestGithubOrgClient(unittest.TestCase):
    """Unit tests for GithubOrgClient class."""

    @parameterized.expand([
        ("google",),
        ("abc",),
    ])
    @patch('client.get_json')
    def test_org(self, org_name, mock_get_json):
        """Test that GithubOrgClient.org returns correct value."""
        mock_get_json.return_value = {"org": org_name}
        client = GithubOrgClient(org_name)
        result = client.org
        mock_get_json.assert_called_once_with(
            f"https://api.github.com/orgs/{org_name}"
        )
        self.assertEqual(result, {"org": org_name})

    def test_public_repos_url(self):
        """Test GithubOrgClient._public_repos_url property."""
        client = GithubOrgClient("test_org")
        with patch.object(
            GithubOrgClient, "org",
            new_callable=PropertyMock,
            return_value={"repos_url": "http://example.com/repos"}
        ):
            self.assertEqual(client._public_repos_url, "http://example.com/repos")

    @patch('client.get_json')
    def test_public_repos(self, mock_get_json):
        """Test GithubOrgClient.public_repos returns expected repos list."""
        test_payload = [
            {"name": "repo1", "license": {"key": "mit"}},
            {"name": "repo2", "license": {"key": "apache-2.0"}},
            {"name": "repo3", "license": None}
        ]
        mock_get_json.return_value = test_payload
        client = GithubOrgClient("test_org")

        with patch.object(
            GithubOrgClient, "_public_repos_url",
            new_callable=PropertyMock,
            return_value="http://example.com/repos"
        ) as mock_url:

            repos = client.public_repos()
            self.assertEqual(
                repos,
                ["repo1", "repo2", "repo3"]
            )

            mock_url.assert_called_once()
            mock_get_json.assert_called_once_with("http://example.com/repos")

    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other_license"}}, "my_license", False),
    ])
    def test_has_license(self, repo, license_key, expected):
        """Test GithubOrgClient.has_license with various license keys."""
        result = GithubOrgClient.has_license(repo, license_key)
        self.assertEqual(result, expected)
