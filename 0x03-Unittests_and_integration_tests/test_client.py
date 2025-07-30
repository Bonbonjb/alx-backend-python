#!/usr/bin/env python3
"""Unit tests for access_nested_map function in utils module.
"""
import unittest
from unittest.mock import patch, PropertyMock, MagicMock
from client import GithubOrgClient
from fixtures import TEST_PAYLOAD
from parameterized import parameterized, parameterized_class
from typing import (
    Dict
)


class TestGithubOrgClient(unittest.TestCase):
    """Test suite for the GithubOrgClient class."""

    @parameterized.expand([
        ("google", {"repos_url": "https://api.github.com/orgs/google"}),
        ("abc", {"repos_url": "https://api.github.com/orgs/abc"}),
    ])
    @patch('client.get_json')
    def test_org(
        self,
        org: str,
        mocked_payload: Dict,
        mock_get_json
    ) -> None:
        """
        Test that GithubOrgClient.org returns the correct value and
        that get_json is called once with the expected URL.
        """
        mock_get_json.return_value = mocked_payload
        client = GithubOrgClient(org)
        result = client.org

        expected_url = f"https://api.github.com/orgs/{org}"
        mock_get_json.assert_called_once_with(expected_url)

        mock_get_json.return_value = mocked_payload
        self.assertEqual(result, mocked_payload)

    def test_public_repos_url(self) -> None:
        """
        Test that the _public_repos_url property returns the correct URL.
        """
        with patch.object(
            GithubOrgClient,
            'org',
            new_callable=PropertyMock
        ) as mock_org:

            expected_url = "https://api.github.com/orgs/google"
            mock_org.return_value = {
                "repos_url": expected_url}

            client = GithubOrgClient("google")
            self.assertEqual(client._public_repos_url, expected_url)

    @patch('client.get_json')
    def test_public_repos(self, mock_get_json) -> None:
        """
        Test that public_repos returns the correct list of repository names.
        """
        with patch.object(
            GithubOrgClient,
            '_public_repos_url',
            new_callable=PropertyMock
        ) as mock_public_repo_url:

            expected_url = 'https://api.github.com/orgs/microsoft'
            mock_public_repo_url.return_value = expected_url
            mock_get_json.return_value = [
                {"name": "repo1", "license": {"key": "MIT"}},
                {"name": "repo2", "license": {"key": "GPL"}},
                {"name": "repo3", "license": None},
            ]

            client = GithubOrgClient("microsoft")
            result = client.public_repos(license="MIT")
            expected_result = ["repo1"]
            self.assertEqual(result, expected_result)

            mock_get_json.assert_called_once_with(expected_url)
            mock_public_repo_url.assert_called_once_with()

    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other_license"}}, "my_license", False),
    ])
    def test_has_license(
        self,
        repo: Dict,
        license_key: str,
        expected_value: bool
    ) -> None:
        """
        Test that has_license correctly checks for the presence of a license.
        """
        client = GithubOrgClient("test_org")
        result = client.has_license(repo, license_key)
        self.assertEqual(result, expected_value)


@parameterized_class((
    "org_payload",
    "repos_payload",
    "expected_repos",
    "apache2_repos"
), TEST_PAYLOAD)
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """Integration test for GithubOrgClient.public_repos with fixtures."""

    @classmethod
    def setUpClass(cls):
        """Start patching requests.get with side_effect."""
        cls.get_patcher = patch('requests.get')
        mock_get = cls.get_patcher.start()

        # Extract the org name from the repos_url (e.g. google or abc)
        cls.org_name = cls.org_payload["repos_url"].split("/")[-2]

        def side_effect(url):
            mock_response = MagicMock()
            if url == cls.org_payload["repos_url"]:
                mock_response.json.return_value = cls.repos_payload
            elif url == f"https://api.github.com/orgs/{cls.org_name}":
                mock_response.json.return_value = cls.org_payload
            else:
                mock_response.json.return_value = None
            return mock_response

        mock_get.side_effect = side_effect

    @classmethod
    def tearDownClass(cls):
        cls.get_patcher.stop()

    def test_public_repos(self):
        """
        Test that public_repos returns expected list
        of repos (no license filter).
        """
        client = GithubOrgClient(self.org_name)
        self.assertEqual(client.public_repos(), self.expected_repos)

    def test_public_repos_with_license(self):
        """
        Test that public_repos returns expected list
        filtered by apache-2.0 license.
        """
        with patch.object(
            GithubOrgClient,
            "has_license",
            side_effect=lambda repo, lic: repo["name"] in self.apache2_repos
        ):
            client = GithubOrgClient(self.org_name)
            self.assertEqual(
                client.public_repos(license="apache-2.0"),
                self.apache2_repos
            )


if __name__ == "__main__":
    unittest.main()
