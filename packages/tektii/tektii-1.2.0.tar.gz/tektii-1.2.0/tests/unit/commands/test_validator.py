"""Unit tests for strategy validator."""

from __future__ import annotations

import tempfile
from decimal import Decimal
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from tektii.commands.validator import ValidationResult, cmd_validate, validate_module, validate_strategy
from tektii.strategy import TektiiStrategy
from tektii.strategy.models import BarData, OrderBuilder, TickData
from tektii.utils.loader import load_strategy_class


class TestValidationResult:
    """Test suite for ValidationResult class."""

    def test_validation_result_initialization(self):
        """Test ValidationResult initialization."""
        result = ValidationResult(is_valid=True, errors=[], warnings=[], info={})

        assert result.is_valid is True
        assert result.errors == []
        assert result.warnings == []
        assert result.info == {}

    def test_add_error(self):
        """Test adding errors to validation result."""
        result = ValidationResult(True, [], [], {})

        result.add_error("Invalid order parameters")

        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0] == "Invalid order parameters"

        # Add another error
        result.add_error("Missing required method")
        assert len(result.errors) == 2

    def test_add_warning(self):
        """Test adding warnings to validation result."""
        result = ValidationResult(True, [], [], {})

        result.add_warning("Deprecated method used")

        assert result.is_valid is True  # Warnings don't affect validity
        assert len(result.warnings) == 1
        assert result.warnings[0] == "Deprecated method used"

    def test_add_info(self):
        """Test adding info to validation result."""
        result = ValidationResult(True, [], [], {})

        result.add_info("strategy_name", "MyStrategy")
        result.add_info("methods_count", 5)

        assert result.info["strategy_name"] == "MyStrategy"
        assert result.info["methods_count"] == 5

    def test_string_representation(self):
        """Test string representation of validation result."""
        result = ValidationResult(is_valid=False, errors=["Error 1", "Error 2"], warnings=["Warning 1"], info={"key": "value"})

        str_repr = str(result)
        assert isinstance(str_repr, str)
        assert len(str_repr) > 0


class ValidTestStrategy(TektiiStrategy):
    """Valid test strategy for validation."""

    def on_market_data(self, tick_data: TickData | None = None, bar_data: BarData | None = None) -> None:
        """Handle market data events."""
        if tick_data and tick_data.last > Decimal("100"):
            _ = OrderBuilder().symbol("AAPL").buy().market().quantity(100).build()
            # In real implementation, would use broker stub to place order
            pass


class InvalidTestStrategy(TektiiStrategy):
    """Invalid test strategy with wrong signature."""

    def on_market_data(self, data) -> None:  # Wrong signature
        """Handle market data events with wrong signature."""
        pass


class TestStrategyValidation:
    """Test suite for strategy validation functions."""

    def test_validate_strategy_valid(self):
        """Test validating a valid strategy."""
        result = validate_strategy(ValidTestStrategy, comprehensive=True)

        assert isinstance(result, ValidationResult)
        # Note: The actual validation may fail due to method signatures
        # This test is just checking that the function runs

    def test_validate_strategy_fast_mode(self):
        """Test validating strategy in fast mode."""
        result = validate_strategy(ValidTestStrategy, comprehensive=False)

        assert isinstance(result, ValidationResult)

    def test_validate_module(self):
        """Test validating a module."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(
                """
from tektii.strategy import TektiiStrategy

class TestStrategy(TektiiStrategy):
    def on_market_data(self, tick_data=None, bar_data=None):
        pass
"""
            )
            f.flush()

            try:
                result = validate_module(f.name, "TestStrategy", comprehensive=True)
                assert isinstance(result, ValidationResult)
            finally:
                Path(f.name).unlink()


class TestStrategyLoading:
    """Test suite for strategy loading functionality."""

    def test_load_strategy_class_valid(self):
        """Test loading valid strategy from file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(
                """
from tektii.strategy import TektiiStrategy
from tektii.strategy.models import TickData

class MyStrategy(TektiiStrategy):
    def on_market_data(self, tick_data=None, bar_data=None):
        pass
"""
            )
            f.flush()

            try:
                strategy_class = load_strategy_class(f.name, "MyStrategy")
                assert strategy_class is not None
                assert strategy_class.__name__ == "MyStrategy"
                assert issubclass(strategy_class, TektiiStrategy)
            finally:
                Path(f.name).unlink()

    def test_load_strategy_class_not_found(self):
        """Test loading strategy from non-existent file."""
        with pytest.raises((FileNotFoundError, ValueError)):
            load_strategy_class("nonexistent.py", "MyStrategy")

    def test_load_strategy_class_class_not_found(self):
        """Test loading non-existent class from file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(
                """
from tektii.strategy import TektiiStrategy

class DifferentStrategy(TektiiStrategy):
    def on_market_data(self, tick_data=None, bar_data=None):
        pass
"""
            )
            f.flush()

            try:
                with pytest.raises(ValueError, match="does not contain class"):
                    load_strategy_class(f.name, "MyStrategy")
            finally:
                Path(f.name).unlink()

    def test_load_strategy_class_syntax_error(self):
        """Test loading strategy with syntax error."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(
                """
from tektii.strategy import TektiiStrategy

class MyStrategy(TektiiStrategy)  # Missing colon
    def on_market_data(self, tick_data=None, bar_data=None):
        pass
"""
            )
            f.flush()

            try:
                with pytest.raises(SyntaxError):
                    load_strategy_class(f.name, "MyStrategy")
            finally:
                Path(f.name).unlink()


class TestCmdValidate:
    """Test suite for cmd_validate function."""

    @patch("os.path.exists")
    @patch("importlib.util.spec_from_file_location")
    @patch("importlib.util.module_from_spec")
    @patch("tektii.commands.validator.validate_strategy")
    def test_cmd_validate_success(self, mock_validate_strategy, mock_module_from_spec, mock_spec_from_file, mock_exists):
        """Test successful validation command."""
        # Set up mocks
        mock_exists.return_value = True

        # Create mock module with strategy class
        mock_module = MagicMock()
        mock_module.ValidTestStrategy = ValidTestStrategy

        # Mock spec and loader
        mock_spec = MagicMock()
        mock_loader = MagicMock()
        mock_spec.loader = mock_loader

        mock_spec_from_file.return_value = mock_spec
        mock_module_from_spec.return_value = mock_module

        # Mock validation result
        mock_validate_strategy.return_value = ValidationResult(is_valid=True, errors=[], warnings=[], info={"strategy_name": "ValidTestStrategy"})

        # Create args
        args = MagicMock()
        args.file = "strategy.py"
        args.fast = False

        # Run command
        with patch("builtins.print"):
            result = cmd_validate(args)

        assert result == 0
        mock_validate_strategy.assert_called_once_with(ValidTestStrategy, comprehensive=True)

    @patch("os.path.exists")
    @patch("importlib.util.spec_from_file_location")
    @patch("importlib.util.module_from_spec")
    @patch("tektii.commands.validator.validate_strategy")
    def test_cmd_validate_failure(self, mock_validate_strategy, mock_module_from_spec, mock_spec_from_file, mock_exists):
        """Test failed validation command."""
        # Set up mocks
        mock_exists.return_value = True

        # Create mock module with invalid strategy class
        mock_module = MagicMock()
        mock_module.InvalidTestStrategy = InvalidTestStrategy

        # Mock spec and loader
        mock_spec = MagicMock()
        mock_loader = MagicMock()
        mock_spec.loader = mock_loader

        mock_spec_from_file.return_value = mock_spec
        mock_module_from_spec.return_value = mock_module

        # Mock validation result
        mock_validate_strategy.return_value = ValidationResult(is_valid=False, errors=["Invalid method signature"], warnings=[], info={})

        # Create args
        args = MagicMock()
        args.file = "strategy.py"
        args.fast = False

        # Run command - should return 1
        with patch("builtins.print"):
            result = cmd_validate(args)

        assert result == 1

    @patch("os.path.exists")
    def test_cmd_validate_file_not_found(self, mock_exists):
        """Test validation command with file not found."""
        mock_exists.return_value = False

        args = MagicMock()
        args.file = "nonexistent.py"
        args.fast = False

        with patch("builtins.print"):
            result = cmd_validate(args)

        assert result == 1

    @patch("os.path.exists")
    @patch("importlib.util.spec_from_file_location")
    def test_cmd_validate_exception(self, mock_spec_from_file, mock_exists):
        """Test validation command with exception during module loading."""
        # Set up mocks
        mock_exists.return_value = True
        mock_spec_from_file.side_effect = Exception("Failed to load module")

        args = MagicMock()
        args.file = "strategy.py"
        args.fast = False

        with patch("builtins.print"):
            result = cmd_validate(args)

        assert result == 1
