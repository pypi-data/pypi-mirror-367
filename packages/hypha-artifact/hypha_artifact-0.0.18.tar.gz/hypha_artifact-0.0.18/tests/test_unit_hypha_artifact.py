# pylint: disable=protected-access
# pyright: reportPrivateUsage=false
"""Unit tests for the HyphaArtifact module."""

from unittest.mock import MagicMock
import pytest
from pytest_mock import MockerFixture
from hypha_artifact import HyphaArtifact


@pytest.fixture(name="artifact")
def get_artifact(mocker: MockerFixture) -> HyphaArtifact:
    """Create a test artifact with a mocked async artifact."""
    mocker.patch("hypha_artifact.hypha_artifact.run_sync")
    mock_async_artifact = mocker.patch(
        "hypha_artifact.hypha_artifact.AsyncHyphaArtifact"
    )
    artifact = HyphaArtifact("test-artifact", "test-workspace", server_url="https://hypha.aicell.io")
    artifact._async_artifact = mock_async_artifact.return_value
    return artifact


class TestHyphaArtifactUnit:
    """Unit test suite for the HyphaArtifact class."""

    def test_edit(self, artifact: HyphaArtifact):
        """Test the edit method."""
        artifact.edit(stage=True)
        assert isinstance(artifact._async_artifact, MagicMock)
        artifact._async_artifact.edit.assert_called_once_with(
            None, None, None, None, None, None, True
        )

    def test_commit(self, artifact: HyphaArtifact):
        """Test the commit method."""
        artifact.commit()
        assert isinstance(artifact._async_artifact, MagicMock)
        artifact._async_artifact.commit.assert_called_once()

    def test_cat(self, artifact: HyphaArtifact):
        """Test the cat method."""
        artifact.cat("test.txt")
        assert isinstance(artifact._async_artifact, MagicMock)
        artifact._async_artifact.cat.assert_called_once_with("test.txt", False, "raise")

    def test_open(self, artifact: HyphaArtifact):
        """Test the open method."""
        artifact.open("test.txt", "w")
        assert isinstance(artifact._async_artifact, MagicMock)
        artifact._async_artifact.open.assert_called_once_with(
            "test.txt",
            "w",
        )

    def test_copy(self, artifact: HyphaArtifact):
        """Test the copy method."""
        artifact.copy("a.txt", "b.txt")
        assert isinstance(artifact._async_artifact, MagicMock)
        artifact._async_artifact.copy.assert_called_once_with(
            "a.txt", "b.txt", False, None, "raise"
        )

    def test_rm(self, artifact: HyphaArtifact):
        """Test the rm method."""
        artifact.rm("test.txt")
        assert isinstance(artifact._async_artifact, MagicMock)
        artifact._async_artifact.rm.assert_called_once_with("test.txt", False, None)

    def test_exists(self, artifact: HyphaArtifact):
        """Test the exists method."""
        artifact.exists("test.txt")
        assert isinstance(artifact._async_artifact, MagicMock)
        artifact._async_artifact.exists.assert_called_once_with("test.txt")

    def test_ls(self, artifact: HyphaArtifact):
        """Test the ls method."""
        artifact.ls("/")
        assert isinstance(artifact._async_artifact, MagicMock)
        artifact._async_artifact.ls.assert_called_once_with("/", True)

    def test_info(self, artifact: HyphaArtifact):
        """Test the info method."""
        artifact.info("test.txt")
        assert isinstance(artifact._async_artifact, MagicMock)
        artifact._async_artifact.info.assert_called_once_with("test.txt")

    def test_isdir(self, artifact: HyphaArtifact):
        """Test the isdir method."""
        artifact.isdir("test")
        assert isinstance(artifact._async_artifact, MagicMock)
        artifact._async_artifact.isdir.assert_called_once_with("test")

    def test_isfile(self, artifact: HyphaArtifact):
        """Test the isfile method."""
        artifact.isfile("test.txt")
        assert isinstance(artifact._async_artifact, MagicMock)
        artifact._async_artifact.isfile.assert_called_once_with("test.txt")

    def test_find(self, artifact: HyphaArtifact):
        """Test the find method."""
        artifact.find("/")
        assert isinstance(artifact._async_artifact, MagicMock)
        artifact._async_artifact.find.assert_called_once_with(
            "/", maxdepth=None, withdirs=False, detail=False
        )
