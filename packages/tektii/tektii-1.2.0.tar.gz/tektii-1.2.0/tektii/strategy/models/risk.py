"""Risk and validation models for pre-trade checks.

This module contains models for risk analysis, validation errors/warnings,
and position risk metrics used in pre-trade checks and risk management.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any, Dict

from pydantic import BaseModel, Field, field_validator

from tektii.strategy.grpc import common_pb2
from tektii.strategy.models.conversions import decimal_from_proto_required, proto_from_decimal
from tektii.strategy.models.errors import ValidationErrorCode, ValidationWarningCode


class ValidationError(BaseModel):
    """Validation error that prevents order placement.

    Represents a critical issue that must be resolved before
    an order can be accepted.
    """

    field: str = Field(..., description="Field that failed validation")
    message: str = Field(..., description="Human-readable error message")
    code: ValidationErrorCode = Field(..., description="Error code for programmatic handling")

    @field_validator("code", mode="before")
    @classmethod
    def convert_code(cls, v: Any) -> ValidationErrorCode:
        """Convert code value to ValidationErrorCode."""
        if isinstance(v, ValidationErrorCode):
            return v
        elif isinstance(v, int):
            return ValidationErrorCode.from_proto(v)
        elif isinstance(v, str):
            return ValidationErrorCode.from_string(v)
        else:
            raise ValueError(f"Invalid validation error code: {v}")

    class Config:
        """Pydantic model configuration."""

        frozen = True

    def to_proto(self) -> common_pb2.ValidationError:
        """Convert to proto message.

        Returns:
            Proto ValidationError message
        """
        return common_pb2.ValidationError(
            field=self.field,
            message=self.message,
            code=self.code.value,  # Use int value for proto
        )

    @classmethod
    def from_proto(cls, proto: common_pb2.ValidationError) -> ValidationError:
        """Create from proto message.

        Args:
            proto: Proto ValidationError message

        Returns:
            ValidationError instance
        """
        return cls(
            field=proto.field,
            message=proto.message,
            code=int(proto.code),  # type: ignore[arg-type]  # Field validator converts
        )

    def __str__(self) -> str:
        """Human-readable string representation."""
        return f"[{self.code.value}] {self.field}: {self.message}"


class ValidationWarning(BaseModel):
    """Non-blocking validation warning.

    Represents a potential issue that doesn't prevent order placement
    but should be reviewed.
    """

    field: str = Field(..., description="Field that triggered warning")
    message: str = Field(..., description="Human-readable warning message")
    code: ValidationWarningCode = Field(..., description="Warning code for programmatic handling")

    @field_validator("code", mode="before")
    @classmethod
    def convert_code(cls, v: Any) -> ValidationWarningCode:
        """Convert code value to ValidationWarningCode."""
        if isinstance(v, ValidationWarningCode):
            return v
        elif isinstance(v, int):
            return ValidationWarningCode.from_proto(v)
        elif isinstance(v, str):
            return ValidationWarningCode.from_string(v)
        else:
            raise ValueError(f"Invalid validation warning code: {v}")

    class Config:
        """Pydantic model configuration."""

        frozen = True

    def to_proto(self) -> common_pb2.ValidationWarning:
        """Convert to proto message.

        Returns:
            Proto ValidationWarning message
        """
        return common_pb2.ValidationWarning(
            field=self.field,
            message=self.message,
            code=self.code.value,  # Use int value for proto
        )

    @classmethod
    def from_proto(cls, proto: common_pb2.ValidationWarning) -> ValidationWarning:
        """Create from proto message.

        Args:
            proto: Proto ValidationWarning message

        Returns:
            ValidationWarning instance
        """
        return cls(
            field=proto.field,
            message=proto.message,
            code=int(proto.code),  # type: ignore[arg-type]  # Field validator converts
        )

    def __str__(self) -> str:
        """Human-readable string representation."""
        return f"⚠️ [{self.code.value}] {self.field}: {self.message}"


class RiskCheckResult(BaseModel):
    """Pre-trade risk analysis results.

    Contains margin requirements, position limits, and risk metrics
    calculated before order placement.
    """

    # Margin analysis
    margin_required: Decimal = Field(..., description="Margin required for this order")
    margin_available: Decimal = Field(..., description="Available margin in account")
    buying_power_used: Decimal = Field(..., description="Buying power consumed by order")
    buying_power_remaining: Decimal = Field(..., description="Buying power after order")

    # Position limits
    position_limit: Decimal = Field(..., description="Maximum allowed position size")
    current_position: Decimal = Field(..., description="Current position size")
    resulting_position: Decimal = Field(..., description="Position size after order fills")

    # Risk metrics
    portfolio_var_before: Decimal = Field(..., description="Portfolio VaR before trade")
    portfolio_var_after: Decimal = Field(..., description="Portfolio VaR after trade")
    concentration_risk: Decimal = Field(..., description="Position concentration metric (0-1)")

    # Additional warnings that don't block the order
    warnings: Dict[str, str] = Field(default_factory=dict, description="Non-blocking warnings")

    class Config:
        """Pydantic model configuration."""

        frozen = True
        arbitrary_types_allowed = True

    @field_validator(
        "margin_required",
        "margin_available",
        "buying_power_used",
        "buying_power_remaining",
        "position_limit",
        "current_position",
        "resulting_position",
        "portfolio_var_before",
        "portfolio_var_after",
        "concentration_risk",
    )
    @classmethod
    def validate_decimal(cls, v: Any) -> Decimal:
        """Ensure all numeric fields are Decimal."""
        if isinstance(v, (int, float, str)):
            return Decimal(str(v))
        if isinstance(v, Decimal):
            return v
        raise ValueError(f"Cannot convert {type(v)} to Decimal")

    @property
    def has_sufficient_margin(self) -> bool:
        """Check if account has sufficient margin.

        Returns:
            True if margin is sufficient
        """
        return self.margin_available >= self.margin_required

    @property
    def has_sufficient_buying_power(self) -> bool:
        """Check if account has sufficient buying power.

        Returns:
            True if buying power is sufficient
        """
        return self.buying_power_remaining >= 0

    @property
    def within_position_limit(self) -> bool:
        """Check if resulting position is within limits.

        Returns:
            True if position is within limits
        """
        return abs(self.resulting_position) <= self.position_limit

    @property
    def margin_utilization(self) -> Decimal:
        """Calculate margin utilization percentage.

        Returns:
            Margin used as percentage of available
        """
        if self.margin_available == 0:
            return Decimal(0)
        return (self.margin_required / self.margin_available) * 100

    @property
    def var_increase(self) -> Decimal:
        """Calculate VaR increase from trade.

        Returns:
            Absolute increase in VaR
        """
        return self.portfolio_var_after - self.portfolio_var_before

    @property
    def var_increase_percentage(self) -> Decimal:
        """Calculate VaR increase as percentage.

        Returns:
            Percentage increase in VaR
        """
        if self.portfolio_var_before == 0:
            return Decimal(0)
        return (self.var_increase / self.portfolio_var_before) * 100

    @property
    def is_high_concentration(self) -> bool:
        """Check if position has high concentration risk.

        Returns:
            True if concentration risk > 0.2 (20%)
        """
        return self.concentration_risk > Decimal("0.2")

    def get_risk_summary(self) -> Dict[str, str]:
        """Get human-readable risk summary.

        Returns:
            Dictionary of risk metrics with descriptions
        """
        return {
            "margin_status": "✓ Sufficient" if self.has_sufficient_margin else "✗ Insufficient",
            "margin_utilization": f"{self.margin_utilization:.1f}%",
            "position_status": "✓ Within limits" if self.within_position_limit else "✗ Exceeds limits",
            "position_usage": f"{abs(self.resulting_position):.0f} / {self.position_limit:.0f}",
            "var_change": f"{self.var_increase_percentage:+.1f}%",
            "concentration": "⚠️ High" if self.is_high_concentration else "✓ Normal",
        }

    def to_proto(self) -> common_pb2.RiskCheckResult:
        """Convert to proto message.

        Returns:
            Proto RiskCheckResult message
        """
        return common_pb2.RiskCheckResult(
            margin_required=proto_from_decimal(self.margin_required),
            margin_available=proto_from_decimal(self.margin_available),
            buying_power_used=proto_from_decimal(self.buying_power_used),
            buying_power_remaining=proto_from_decimal(self.buying_power_remaining),
            position_limit=proto_from_decimal(self.position_limit),
            current_position=proto_from_decimal(self.current_position),
            resulting_position=proto_from_decimal(self.resulting_position),
            portfolio_var_before=proto_from_decimal(self.portfolio_var_before),
            portfolio_var_after=proto_from_decimal(self.portfolio_var_after),
            concentration_risk=proto_from_decimal(self.concentration_risk),
            warnings=self.warnings,
        )

    @classmethod
    def from_proto(cls, proto: common_pb2.RiskCheckResult) -> RiskCheckResult:
        """Create from proto message.

        Args:
            proto: Proto RiskCheckResult message

        Returns:
            RiskCheckResult instance
        """
        return cls(
            margin_required=decimal_from_proto_required(proto.margin_required),
            margin_available=decimal_from_proto_required(proto.margin_available),
            buying_power_used=decimal_from_proto_required(proto.buying_power_used),
            buying_power_remaining=decimal_from_proto_required(proto.buying_power_remaining),
            position_limit=decimal_from_proto_required(proto.position_limit),
            current_position=decimal_from_proto_required(proto.current_position),
            resulting_position=decimal_from_proto_required(proto.resulting_position),
            portfolio_var_before=decimal_from_proto_required(proto.portfolio_var_before),
            portfolio_var_after=decimal_from_proto_required(proto.portfolio_var_after),
            concentration_risk=decimal_from_proto_required(proto.concentration_risk),
            warnings=dict(proto.warnings) if proto.warnings else {},
        )

    def __str__(self) -> str:
        """Human-readable string representation."""
        summary = self.get_risk_summary()
        parts = [
            f"Margin: {summary['margin_status']} ({summary['margin_utilization']})",
            f"Position: {summary['position_status']} ({summary['position_usage']})",
            f"VaR: {summary['var_change']}",
            f"Concentration: {summary['concentration']}",
        ]

        if self.warnings:
            warning_str = ", ".join(f"{k}: {v}" for k, v in self.warnings.items())
            parts.append(f"Warnings: {warning_str}")

        return " | ".join(parts)


class PositionRisk(BaseModel):
    """Risk metrics for a single position.

    Contains position-specific risk calculations including VaR,
    beta, volatility, and exposure.
    """

    symbol: str = Field(..., description="Trading symbol")
    position_var: Decimal = Field(..., description="Position Value at Risk")
    beta: Decimal = Field(..., description="Beta relative to market")
    volatility: Decimal = Field(..., description="Historical volatility (annualized)")
    exposure: Decimal = Field(..., description="Dollar exposure (position value)")

    class Config:
        """Pydantic model configuration."""

        frozen = True
        arbitrary_types_allowed = True

    @field_validator("position_var", "beta", "volatility", "exposure")
    @classmethod
    def validate_decimal(cls, v: Any) -> Decimal:
        """Ensure all numeric fields are Decimal."""
        if isinstance(v, (int, float, str)):
            return Decimal(str(v))
        if isinstance(v, Decimal):
            return v
        raise ValueError(f"Cannot convert {type(v)} to Decimal")

    @property
    def volatility_percentage(self) -> Decimal:
        """Get volatility as percentage.

        Returns:
            Volatility as percentage (e.g., 25.5 for 25.5%)
        """
        return self.volatility * 100

    @property
    def var_percentage(self) -> Decimal:
        """Calculate VaR as percentage of exposure.

        Returns:
            VaR as percentage of position value
        """
        if self.exposure == 0:
            return Decimal(0)
        return (self.position_var / self.exposure) * 100

    @property
    def is_high_volatility(self) -> bool:
        """Check if position has high volatility.

        Returns:
            True if annualized volatility > 50%
        """
        return self.volatility > Decimal("0.5")

    @property
    def is_high_beta(self) -> bool:
        """Check if position has high market sensitivity.

        Returns:
            True if |beta| > 1.5
        """
        return abs(self.beta) > Decimal("1.5")

    def get_risk_level(self) -> str:
        """Categorize overall risk level.

        Returns:
            Risk level: "Low", "Medium", "High", or "Very High"
        """
        risk_score = 0

        if self.is_high_volatility:
            risk_score += 2
        elif self.volatility > Decimal("0.3"):
            risk_score += 1

        if self.is_high_beta:
            risk_score += 2
        elif abs(self.beta) > Decimal("1.2"):
            risk_score += 1

        if self.var_percentage > 10:
            risk_score += 2
        elif self.var_percentage > 5:
            risk_score += 1

        if risk_score >= 4:
            return "Very High"
        elif risk_score >= 2:
            return "High"
        elif risk_score >= 1:
            return "Medium"
        else:
            return "Low"

    def to_proto(self) -> common_pb2.PositionRisk:
        """Convert to proto message.

        Returns:
            Proto PositionRisk message
        """
        return common_pb2.PositionRisk(
            symbol=self.symbol,
            position_var=proto_from_decimal(self.position_var),
            beta=proto_from_decimal(self.beta),
            volatility=proto_from_decimal(self.volatility),
            exposure=proto_from_decimal(self.exposure),
        )

    @classmethod
    def from_proto(cls, proto: common_pb2.PositionRisk) -> PositionRisk:
        """Create from proto message.

        Args:
            proto: Proto PositionRisk message

        Returns:
            PositionRisk instance
        """
        return cls(
            symbol=proto.symbol,
            position_var=decimal_from_proto_required(proto.position_var),
            beta=decimal_from_proto_required(proto.beta),
            volatility=decimal_from_proto_required(proto.volatility),
            exposure=decimal_from_proto_required(proto.exposure),
        )

    def __str__(self) -> str:
        """Human-readable string representation."""
        risk_level = self.get_risk_level()
        risk_icon = {
            "Low": "🟢",
            "Medium": "🟡",
            "High": "🟠",
            "Very High": "🔴",
        }.get(risk_level, "⚪")

        return (
            f"{risk_icon} {self.symbol} Risk: {risk_level} "
            f"(VaR: ${self.position_var:,.0f} [{self.var_percentage:.1f}%], "
            f"β: {self.beta:.2f}, σ: {self.volatility_percentage:.1f}%, "
            f"Exposure: ${self.exposure:,.0f})"
        )
