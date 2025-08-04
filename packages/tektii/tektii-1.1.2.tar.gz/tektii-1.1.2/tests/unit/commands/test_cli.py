"""Unit tests for CLI main entry point."""

from __future__ import annotations

import sys
from unittest.mock import patch

import pytest

from tektii.cli import main


class TestCLI:
    """Test suite for CLI main entry point."""

    def test_cli_no_arguments(self, capsys):
        """Test CLI with no arguments shows help."""
        with patch.object(sys, "argv", ["tektii"]):
            with pytest.raises(SystemExit) as exc_info:
                main()

            # argparse exits with code 2 for missing required arguments
            assert exc_info.value.code == 2

            captured = capsys.readouterr()
            assert "usage:" in captured.err
            assert "Available commands" in captured.err

    def test_cli_help_flag(self, capsys):
        """Test CLI help flag."""
        with patch.object(sys, "argv", ["tektii", "--help"]):
            with pytest.raises(SystemExit) as exc_info:
                main()

            # Help exits with code 0
            assert exc_info.value.code == 0

            captured = capsys.readouterr()
            assert "Tektii Strategy SDK - Command Line Interface" in captured.out
            assert "Available commands" in captured.out
            assert "Examples:" in captured.out

    def test_cli_invalid_command(self, capsys):
        """Test CLI with invalid command."""
        with patch.object(sys, "argv", ["tektii", "invalid-command"]):
            with pytest.raises(SystemExit) as exc_info:
                main()

            assert exc_info.value.code == 2

            captured = capsys.readouterr()
            assert "invalid choice: 'invalid-command'" in captured.err

    def test_cli_new_command(self, capsys):
        """Test CLI new command routing (not implemented)."""
        with patch.object(sys, "argv", ["tektii", "new", "my_strategy"]):
            with pytest.raises(SystemExit) as exc_info:
                main()

            assert exc_info.value.code == 0
            captured = capsys.readouterr()
            assert "Not implemented yet" in captured.out

    def test_cli_new_command_with_options(self, capsys):
        """Test CLI new command with options (not implemented)."""
        with patch.object(sys, "argv", ["tektii", "new", "my_strategy", "--advanced", "--with-tests"]):
            with pytest.raises(SystemExit) as exc_info:
                main()

            assert exc_info.value.code == 0
            captured = capsys.readouterr()
            assert "Not implemented yet" in captured.out

    def test_cli_new_command_aliases(self, capsys):
        """Test CLI new command aliases (not implemented)."""
        # Test 'n' alias
        with patch.object(sys, "argv", ["tektii", "n", "my_strategy"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0
            captured = capsys.readouterr()
            assert "Not implemented yet" in captured.out

        # Test 'create' alias
        with patch.object(sys, "argv", ["tektii", "create", "my_strategy"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0
            captured = capsys.readouterr()
            assert "Not implemented yet" in captured.out

    @patch("sys.exit")
    @patch("tektii.cli.cmd_validate")
    def test_cli_validate_command(self, mock_cmd_validate, mock_exit):
        """Test CLI validate command routing."""
        mock_cmd_validate.return_value = 0
        with patch.object(sys, "argv", ["tektii", "validate", "strategy.py"]):
            main()

            mock_cmd_validate.assert_called_once()
            args = mock_cmd_validate.call_args[0][0]
            assert args.file == "strategy.py"
            assert not args.fast
            mock_exit.assert_called_with(0)

    @patch("sys.exit")
    @patch("tektii.cli.cmd_validate")
    def test_cli_validate_command_fast(self, mock_cmd_validate, mock_exit):
        """Test CLI validate command with fast option."""
        mock_cmd_validate.return_value = 0
        with patch.object(sys, "argv", ["tektii", "validate", "strategy.py", "--fast"]):
            main()

            mock_cmd_validate.assert_called_once()
            args = mock_cmd_validate.call_args[0][0]
            assert args.file == "strategy.py"
            assert args.fast
            mock_exit.assert_called_with(0)

    @patch("sys.exit")
    @patch("tektii.cli.cmd_test")
    def test_cli_test_command(self, mock_cmd_test, mock_exit):
        """Test CLI test command routing."""
        mock_cmd_test.return_value = 0
        with patch.object(sys, "argv", ["tektii", "test", "test_strategy.py"]):
            main()

            mock_cmd_test.assert_called_once()
            args = mock_cmd_test.call_args[0][0]
            assert args.file == "test_strategy.py"
            mock_exit.assert_called_with(0)

    @patch("sys.exit")
    @patch("tektii.cli.cmd_serve")
    def test_cli_serve_command(self, mock_cmd_serve, mock_exit):
        """Test CLI serve command routing."""
        mock_cmd_serve.return_value = 0
        with patch.object(sys, "argv", ["tektii", "serve", "strategy.py", "MyStrategy"]):
            main()

            mock_cmd_serve.assert_called_once()
            args = mock_cmd_serve.call_args[0][0]
            assert args.module == "strategy.py"
            assert args.class_name == "MyStrategy"
            assert args.port == 50051  # default port
            mock_exit.assert_called_with(0)

    @patch("sys.exit")
    @patch("tektii.cli.cmd_serve")
    def test_cli_serve_command_with_port(self, mock_cmd_serve, mock_exit):
        """Test CLI serve command with custom port."""
        mock_cmd_serve.return_value = 0
        with patch.object(sys, "argv", ["tektii", "serve", "strategy.py", "MyStrategy", "--port", "8080"]):
            main()

            mock_cmd_serve.assert_called_once()
            args = mock_cmd_serve.call_args[0][0]
            assert args.port == 8080
            mock_exit.assert_called_with(0)

    @patch("sys.exit")
    @patch("tektii.cli.cmd_push")
    def test_cli_push_command(self, mock_cmd_push, mock_exit):
        """Test CLI push command routing."""
        mock_cmd_push.return_value = 0
        with patch.object(sys, "argv", ["tektii", "push", "strategy.py", "MyStrategy"]):
            main()

            mock_cmd_push.assert_called_once()
            args = mock_cmd_push.call_args[0][0]
            assert args.module == "strategy.py"
            assert args.class_name == "MyStrategy"
            assert not args.save_config
            assert args.registry == "us-central1-docker.pkg.dev/tektii-prod/strategies"
            mock_exit.assert_called_with(0)

    @patch("sys.exit")
    @patch("tektii.cli.cmd_push")
    def test_cli_push_command_with_options(self, mock_cmd_push, mock_exit):
        """Test CLI push command with options."""
        mock_cmd_push.return_value = 0
        with patch.object(
            sys, "argv", ["tektii", "push", "strategy.py", "MyStrategy", "--save-config", "--registry", "custom-registry", "--tag", "v1.0.0"]
        ):
            main()

            mock_cmd_push.assert_called_once()
            args = mock_cmd_push.call_args[0][0]
            assert args.save_config
            assert args.registry == "custom-registry"
            assert args.tag == "v1.0.0"
            mock_exit.assert_called_with(0)

    def test_cli_command_help(self, capsys):
        """Test individual command help."""
        # Test new command help
        with patch.object(sys, "argv", ["tektii", "new", "--help"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0

            captured = capsys.readouterr()
            # The help for 'new' subcommand doesn't include the full description
            # It shows the usage and arguments instead
            assert "--advanced" in captured.out
            assert "--with-tests" in captured.out

    def test_cli_command_aliases_in_help(self, capsys):
        """Test that command aliases appear in help."""
        with patch.object(sys, "argv", ["tektii", "--help"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0

            captured = capsys.readouterr()
            assert "Command Aliases:" in captured.out
            assert "n, create  → new" in captured.out
            assert "v, check   → validate" in captured.out

    @patch("sys.exit")
    @patch("tektii.cli.cmd_validate")
    def test_cli_validate_aliases(self, mock_cmd_validate, mock_exit):
        """Test CLI validate command aliases."""
        mock_cmd_validate.return_value = 0
        # Test 'v' alias
        with patch.object(sys, "argv", ["tektii", "v", "strategy.py"]):
            main()
            mock_cmd_validate.assert_called_once()

        mock_cmd_validate.reset_mock()
        mock_exit.reset_mock()

        # Test 'check' alias
        with patch.object(sys, "argv", ["tektii", "check", "strategy.py"]):
            main()
            mock_cmd_validate.assert_called_once()

    @patch("sys.exit")
    @patch("tektii.cli.cmd_serve")
    def test_cli_serve_aliases(self, mock_cmd_serve, mock_exit):
        """Test CLI serve command aliases."""
        mock_cmd_serve.return_value = 0
        # Test 's' alias
        with patch.object(sys, "argv", ["tektii", "s", "strategy.py", "MyStrategy"]):
            main()
            mock_cmd_serve.assert_called_once()

        mock_cmd_serve.reset_mock()
        mock_exit.reset_mock()

        # Test 'run' alias
        with patch.object(sys, "argv", ["tektii", "run", "strategy.py", "MyStrategy"]):
            main()
            mock_cmd_serve.assert_called_once()

    @patch("sys.exit")
    @patch("tektii.cli.cmd_push")
    def test_cli_push_aliases(self, mock_cmd_push, mock_exit):
        """Test CLI push command aliases."""
        mock_cmd_push.return_value = 0
        # Test 'p' alias
        with patch.object(sys, "argv", ["tektii", "p", "strategy.py", "MyStrategy"]):
            main()
            mock_cmd_push.assert_called_once()

        mock_cmd_push.reset_mock()
        mock_exit.reset_mock()

        # Test 'deploy' alias
        with patch.object(sys, "argv", ["tektii", "deploy", "strategy.py", "MyStrategy"]):
            main()
            mock_cmd_push.assert_called_once()

    def test_cli_examples_in_help(self, capsys):
        """Test that examples appear in help."""
        with patch.object(sys, "argv", ["tektii", "--help"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0

            captured = capsys.readouterr()
            assert "Examples:" in captured.out
            assert "tektii new my_strategy --advanced --with-tests" in captured.out
            assert "tektii validate my_strategy.py --fast" in captured.out
            assert "tektii serve my_strategy.py MyStrategy --port 50051" in captured.out
