from unittest.mock import patch

from src.version_builder.cli import CLI


class TestCLI:
    @patch("src.version_builder.cli.CLI.show_last_tag")
    @patch("src.version_builder.cli.argparse.ArgumentParser.print_help")
    @patch("src.version_builder.cli.argparse.ArgumentParser.parse_args")
    def test_call_without_arguments(
        self,
        mock_parse_args,
        mock_help,
        mock_show_last_tag,
    ):
        mock_parse_args.return_value.last_version = False

        cli = CLI()
        cli()

        mock_help.assert_called_once()
        mock_show_last_tag.assert_not_called()

    @patch("src.version_builder.cli.CLI.show_last_tag")
    @patch("src.version_builder.cli.argparse.ArgumentParser.print_help")
    @patch("src.version_builder.cli.argparse.ArgumentParser.parse_args")
    def test_call_with_last_version_argument(
        self,
        mock_parse_args,
        mock_help,
        mock_show_last_tag,
    ):
        mock_parse_args.return_value.last_version = True

        cli = CLI()
        cli()

        mock_show_last_tag.assert_called_once()
        mock_help.assert_not_called()

    @patch("src.version_builder.cli.GitHelper.get_last_tag")
    def test_show_last_tag_calls_git_method(self, mock_get_last_tag):
        cli = CLI()
        cli.show_last_tag()
        mock_get_last_tag.assert_called_once()
