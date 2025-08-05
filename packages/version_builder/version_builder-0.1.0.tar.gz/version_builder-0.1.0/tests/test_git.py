from unittest.mock import patch

from src.version_builder.git import GitHelper


class TestGit:
    @patch("src.version_builder.git.Repo.init")
    @patch("src.version_builder.git.logger.info")
    def test_get_last_tag_empty(self, mock_logger, mock_repo):
        mock_repo.return_value.tags = []

        GitHelper().get_last_tag()
        assert mock_logger.call_count == 1
        assert mock_logger.mock_calls[0].args[0] == "No tags found"

    @patch("src.version_builder.git.Repo.init")
    @patch("src.version_builder.git.logger.info")
    def test_get_last_tag_empty(self, mock_logger, mock_repo):
        mock_repo.return_value.tags = ["v1.0.0", "v1.0.1"]

        GitHelper().get_last_tag()
        assert mock_logger.call_count == 2
        assert mock_logger.mock_calls[0].args[0] == "v1.0.0"
        assert mock_logger.mock_calls[1].args[0] == "v1.0.1"
