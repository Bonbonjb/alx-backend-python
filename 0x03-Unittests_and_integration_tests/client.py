#!/usr/bin/env python3
"""Unit tests for client module."""

from unittest import TestCase
from parameterized import parameterized
from unittest.mock import patch
from client import GithubOrgClient


class TestGithubOrgClient(TestCase):
    """Test GithubOrgClient class."""

    @parameterized.expand([
        ("google",),
        ("abc",),
    ])
    @patch("client.get_json")
    def test_org(self, org_name, mock_get_json):
        """Test that org property returns the expected dictionary."""
        mock_get_json.return_value = {"login": org_name}
        client = GithubOrgClient(org_name)

        result = client.org

        mock_get_json.assert_called_once_with(f"https://api.github.com/orgs/{org_name}")
        self.assertEqual(result, {"login": org_name})

    def test_public_repos_url(self):
        """Test that _public_repos_url returns correct URL from org payload."""
        with patch.object(GithubOrgClient, "org", new_callable=property) as mock_org:
            mock_org.return_value = {
                "repos_url": "https://api.github.com/orgs/testorg/repos"
            }

            client = GithubOrgClient("testorg")
            result = client._public_repos_url

            self.assertEqual(result, "https://api.github.com/orgs/testorg/repos")
