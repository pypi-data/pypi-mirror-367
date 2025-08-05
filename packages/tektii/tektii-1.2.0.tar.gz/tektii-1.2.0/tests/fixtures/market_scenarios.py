"""Market scenario templates for comprehensive strategy testing."""

import time
from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from typing import Dict, List

from tektii.strategy.models.market_data import BarData, TickData


class ScenarioType(Enum):
    """Types of market scenarios."""

    FLASH_CRASH = "flash_crash"
    OPENING_AUCTION = "opening_auction"
    NEWS_EVENT = "news_event"
    END_OF_DAY = "end_of_day"
    CORPORATE_ACTION = "corporate_action"
    TRENDING = "trending"
    RANGE_BOUND = "range_bound"
    VOLATILE = "volatile"
    ILLIQUID = "illiquid"


@dataclass
class MarketScenario:
    """Market scenario definition."""

    name: str
    scenario_type: ScenarioType
    duration_seconds: int
    description: str
    ticks: List[TickData]
    bars: List[BarData]
    metadata: Dict[str, any]


class MarketScenarioGenerator:
    """Generate realistic market scenarios for testing."""

    @staticmethod
    def generate_flash_crash_scenario() -> MarketScenario:
        """Generate a flash crash scenario.

        Timeline:
        - 0-30s: Normal trading
        - 30-35s: Rapid price drop (-10%)
        - 35-40s: Trading halt
        - 40-60s: Gradual recovery
        """
        ticks = []
        base_time = int(time.time() * 1_000_000)

        # Normal trading phase
        for i in range(30):
            price = Decimal("100.00") + Decimal(str(i % 10 - 5)) * Decimal("0.01")
            tick = TickData(
                symbol="SPY",
                timestamp_us=base_time + i * 1_000_000,
                last=price,
                bid=price - Decimal("0.01"),
                ask=price + Decimal("0.01"),
                volume=10000,
            )
            ticks.append(tick)

        # Crash phase - 10% drop in 5 seconds
        crash_prices = [Decimal("100.00"), Decimal("98.00"), Decimal("95.00"), Decimal("92.00"), Decimal("90.00")]
        for i, price in enumerate(crash_prices):
            tick = TickData(
                symbol="SPY",
                timestamp_us=base_time + (30 + i) * 1_000_000,
                last=price,
                bid=price - Decimal("0.10"),  # Wide spread
                ask=price + Decimal("0.10"),
                volume=50000,  # High volume
            )
            ticks.append(tick)

        # Trading halt - same price for 5 seconds
        for i in range(5):
            tick = TickData(
                symbol="SPY",
                timestamp_us=base_time + (35 + i) * 1_000_000,
                last=Decimal("90.00"),
                bid=None,  # No quotes during halt
                ask=None,
                volume=0,
            )
            ticks.append(tick)

        # Recovery phase
        recovery_prices = [Decimal("90.50"), Decimal("91.00"), Decimal("92.00"), Decimal("93.00"), Decimal("94.00"), Decimal("95.00")]
        for i, price in enumerate(recovery_prices):
            tick = TickData(
                symbol="SPY",
                timestamp_us=base_time + (40 + i * 3) * 1_000_000,
                last=price,
                bid=price - Decimal("0.05"),
                ask=price + Decimal("0.05"),
                volume=30000,
            )
            ticks.append(tick)

        return MarketScenario(
            name="Flash Crash - May 6, 2010 Style",
            scenario_type=ScenarioType.FLASH_CRASH,
            duration_seconds=60,
            description="Simulates a flash crash with 10% drop, trading halt, and recovery",
            ticks=ticks,
            bars=[],  # Could generate 1-minute bars from ticks
            metadata={"max_drawdown": -0.10, "halt_duration": 5, "recovery_percent": 0.50, "trigger": "liquidity_crisis"},
        )

    @staticmethod
    def generate_opening_auction_volatility() -> MarketScenario:
        """Generate opening auction volatility scenario.

        Timeline:
        - Pre-market: Wide spreads, low volume
        - Open: Price discovery with volatility
        - Post-open: Stabilization
        """
        ticks = []
        base_time = int(time.time() * 1_000_000)

        # Pre-market (9:00-9:30 AM)
        for i in range(30):
            # Indicative prices with wide spreads
            mid_price = Decimal("150.00") + Decimal(str(i % 10 - 5)) * Decimal("0.10")
            tick = TickData(
                symbol="AAPL",
                timestamp_us=base_time + i * 60_000_000,  # 1 tick per minute
                last=mid_price,
                bid=mid_price - Decimal("0.50"),  # Wide pre-market spread
                ask=mid_price + Decimal("0.50"),
                volume=100,  # Low pre-market volume
            )
            ticks.append(tick)

        # Opening cross (9:30 AM) - high volatility
        opening_sequence = [
            (Decimal("149.00"), 50000),  # Initial print
            (Decimal("151.00"), 30000),  # Gap up
            (Decimal("150.00"), 40000),  # Pull back
            (Decimal("152.00"), 60000),  # Another surge
            (Decimal("151.50"), 35000),  # Stabilizing
        ]

        for i, (price, volume) in enumerate(opening_sequence):
            tick = TickData(
                symbol="AAPL",
                timestamp_us=base_time + 30 * 60_000_000 + i * 200_000,  # 200ms apart
                last=price,
                bid=price - Decimal("0.02"),
                ask=price + Decimal("0.02"),
                volume=volume,
            )
            ticks.append(tick)

        # Post-open stabilization
        stable_price = Decimal("151.50")
        for i in range(20):
            price = stable_price + Decimal(str(i % 5 - 2)) * Decimal("0.01")
            tick = TickData(
                symbol="AAPL",
                timestamp_us=base_time + 31 * 60_000_000 + i * 1_000_000,
                last=price,
                bid=price - Decimal("0.01"),
                ask=price + Decimal("0.01"),
                volume=5000,
            )
            ticks.append(tick)

        return MarketScenario(
            name="Opening Auction Volatility",
            scenario_type=ScenarioType.OPENING_AUCTION,
            duration_seconds=35 * 60,  # 35 minutes
            description="Pre-market indication, volatile open, and stabilization",
            ticks=ticks,
            bars=[],
            metadata={
                "opening_volatility": 0.02,  # 2% in first minute
                "pre_market_spread": 0.50,
                "opening_volume_spike": 10,  # 10x normal
                "stabilization_time": 60,  # seconds
            },
        )

    @staticmethod
    def generate_news_event_gap() -> MarketScenario:
        """Generate news event price gap scenario.

        Timeline:
        - Normal trading
        - News hits: immediate gap
        - High volatility price discovery
        - New equilibrium
        """
        ticks = []
        base_time = int(time.time() * 1_000_000)

        # Normal trading before news
        for i in range(20):
            price = Decimal("50.00") + Decimal(str(i % 3 - 1)) * Decimal("0.01")
            tick = TickData(
                symbol="NEWS",
                timestamp_us=base_time + i * 1_000_000,
                last=price,
                bid=price - Decimal("0.01"),
                ask=price + Decimal("0.01"),
                volume=1000,
            )
            ticks.append(tick)

        # News hits - 5% gap up
        # Initial reaction - very volatile
        news_prices = [
            Decimal("52.50"),  # Initial gap
            Decimal("53.00"),  # Overshoot
            Decimal("52.00"),  # Pull back
            Decimal("52.75"),  # Recovery
            Decimal("52.50"),  # Settling
        ]

        for i, price in enumerate(news_prices):
            tick = TickData(
                symbol="NEWS",
                timestamp_us=base_time + (20 + i) * 1_000_000,
                last=price,
                bid=price - Decimal("0.05"),  # Wide spread during news
                ask=price + Decimal("0.05"),
                volume=20000,  # High volume
            )
            ticks.append(tick)

        # Price discovery phase - high volatility
        for i in range(10):
            base = Decimal("52.50")
            volatility = Decimal("0.25")
            price = base + Decimal(str(i % 5 - 2)) * volatility / 5
            tick = TickData(
                symbol="NEWS",
                timestamp_us=base_time + (25 + i) * 1_000_000,
                last=price,
                bid=price - Decimal("0.02"),
                ask=price + Decimal("0.02"),
                volume=10000,
            )
            ticks.append(tick)

        # New equilibrium - less volatile
        for i in range(15):
            price = Decimal("52.50") + Decimal(str(i % 3 - 1)) * Decimal("0.02")
            tick = TickData(
                symbol="NEWS",
                timestamp_us=base_time + (35 + i) * 1_000_000,
                last=price,
                bid=price - Decimal("0.01"),
                ask=price + Decimal("0.01"),
                volume=3000,
            )
            ticks.append(tick)

        return MarketScenario(
            name="Breaking News Event",
            scenario_type=ScenarioType.NEWS_EVENT,
            duration_seconds=50,
            description="Earnings beat causes 5% gap with volatile price discovery",
            ticks=ticks,
            bars=[],
            metadata={"gap_percent": 0.05, "news_type": "earnings_beat", "max_volatility_window": 10, "volume_multiplier": 20},  # seconds
        )

    @staticmethod
    def generate_end_of_day_cleanup() -> MarketScenario:
        """Generate end of day market dynamics.

        Timeline:
        - 3:30-3:50 PM: Position squaring
        - 3:50-3:59 PM: MOC imbalance
        - 3:59-4:00 PM: Closing cross
        """
        ticks = []
        base_time = int(time.time() * 1_000_000)

        # Normal afternoon trading (3:30 PM start)
        base_price = Decimal("200.00")

        # Position squaring (3:30-3:50 PM) - increased volatility
        for i in range(20 * 60):  # 20 minutes of seconds
            # Gradually increasing volatility
            volatility = Decimal("0.05") * (1 + i / 1200)  # Increases over time
            price = base_price + Decimal(str(i % 20 - 10)) * volatility / 10

            if i % 5 == 0:  # Tick every 5 seconds
                tick = TickData(
                    symbol="CLOSE",
                    timestamp_us=base_time + i * 1_000_000,
                    last=price,
                    bid=price - Decimal("0.01"),
                    ask=price + Decimal("0.01"),
                    volume=2000 + i * 2,  # Increasing volume
                )
                ticks.append(tick)

        # MOC imbalance period (3:50-3:59 PM)
        # Simulate buy-side imbalance pushing price up
        for i in range(9 * 60):  # 9 minutes
            minute = i // 60
            imbalance_pressure = Decimal("0.10") * minute / 9  # Increasing pressure
            price = base_price + imbalance_pressure

            if i % 2 == 0:  # More frequent ticks
                tick = TickData(
                    symbol="CLOSE",
                    timestamp_us=base_time + (20 * 60 + i) * 1_000_000,
                    last=price,
                    bid=price - Decimal("0.01"),
                    ask=price + Decimal("0.02"),  # Wider ask due to buying
                    volume=5000 + minute * 1000,
                )
                ticks.append(tick)

        # Closing cross (3:59-4:00 PM) - final minute
        closing_sequence = [
            (Decimal("200.08"), 10000),
            (Decimal("200.09"), 15000),
            (Decimal("200.10"), 25000),  # Large prints
            (Decimal("200.10"), 50000),  # Closing print
        ]

        for i, (price, volume) in enumerate(closing_sequence):
            tick = TickData(
                symbol="CLOSE",
                timestamp_us=base_time + (29 * 60 + 45 + i * 5) * 1_000_000,
                last=price,
                bid=price if i < 3 else None,  # No bid/ask after close
                ask=price if i < 3 else None,
                volume=volume,
            )
            ticks.append(tick)

        return MarketScenario(
            name="End of Day Dynamics",
            scenario_type=ScenarioType.END_OF_DAY,
            duration_seconds=30 * 60,  # 30 minutes
            description="EOD position squaring, MOC imbalance, and closing cross",
            ticks=ticks,
            bars=[],
            metadata={
                "moc_imbalance": "buy_side",
                "imbalance_shares": 100000,
                "closing_volume_percent": 0.10,  # 10% of daily volume
                "final_print_size": 50000,
            },
        )

    @staticmethod
    def generate_corporate_action_adjustment() -> MarketScenario:
        """Generate corporate action (split/dividend) scenario.

        Example: 2:1 stock split
        """
        ticks = []
        base_time = int(time.time() * 1_000_000)

        # Pre-split trading
        pre_split_price = Decimal("300.00")
        for i in range(10):
            price = pre_split_price + Decimal(str(i % 3 - 1)) * Decimal("0.10")
            tick = TickData(
                symbol="SPLIT",
                timestamp_us=base_time + i * 1_000_000,
                last=price,
                bid=price - Decimal("0.01"),
                ask=price + Decimal("0.01"),
                volume=1000,
            )
            ticks.append(tick)

        # Split occurs overnight - price halves
        # Post-split trading - some confusion/volatility
        split_prices = [
            Decimal("150.00"),  # Correct price
            Decimal("148.00"),  # Some selling
            Decimal("152.00"),  # Realization and buying
            Decimal("150.50"),  # Stabilizing
        ]

        for i, price in enumerate(split_prices):
            tick = TickData(
                symbol="SPLIT",
                timestamp_us=base_time + (20 + i * 2) * 1_000_000,
                last=price,
                bid=price - Decimal("0.05"),  # Wider spread initially
                ask=price + Decimal("0.05"),
                volume=5000,  # Higher volume
            )
            ticks.append(tick)

        # Normal trading resumes
        for i in range(20):
            price = Decimal("150.00") + Decimal(str(i % 5 - 2)) * Decimal("0.05")
            tick = TickData(
                symbol="SPLIT",
                timestamp_us=base_time + (30 + i) * 1_000_000,
                last=price,
                bid=price - Decimal("0.01"),
                ask=price + Decimal("0.01"),
                volume=2000,  # Volume doubles due to split
            )
            ticks.append(tick)

        return MarketScenario(
            name="2:1 Stock Split",
            scenario_type=ScenarioType.CORPORATE_ACTION,
            duration_seconds=50,
            description="Stock split causing price adjustment and temporary volatility",
            ticks=ticks,
            bars=[],
            metadata={"action_type": "stock_split", "split_ratio": "2:1", "adjustment_factor": 0.5, "ex_date": "today", "volume_adjustment": 2.0},
        )

    @staticmethod
    def generate_trending_market() -> MarketScenario:
        """Generate a trending market scenario."""
        ticks = []
        base_time = int(time.time() * 1_000_000)

        # Strong uptrend with pullbacks
        base_price = Decimal("100.00")
        trend_strength = Decimal("0.10")  # 10 cents per minute

        for minute in range(60):
            # Trend component
            trend_price = base_price + trend_strength * minute

            # Intraday noise
            for second in range(60):
                if second % 5 == 0:  # Tick every 5 seconds
                    # Small pullbacks every 10 minutes
                    if minute % 10 == 0 and second < 30:
                        noise = -Decimal("0.20")
                    else:
                        noise = Decimal(str(second % 10 - 5)) * Decimal("0.01")

                    price = trend_price + noise
                    tick = TickData(
                        symbol="TREND",
                        timestamp_us=base_time + (minute * 60 + second) * 1_000_000,
                        last=price,
                        bid=price - Decimal("0.01"),
                        ask=price + Decimal("0.01"),
                        volume=1000 + minute * 10,  # Increasing volume in trend
                    )
                    ticks.append(tick)

        return MarketScenario(
            name="Strong Uptrend",
            scenario_type=ScenarioType.TRENDING,
            duration_seconds=3600,  # 1 hour
            description="Persistent uptrend with periodic pullbacks",
            ticks=ticks,
            bars=[],
            metadata={"trend_strength": 0.10, "pullback_frequency": 10, "trend_quality": 0.85},  # Per minute  # Minutes  # Trend vs noise ratio
        )

    @staticmethod
    def generate_range_bound_market() -> MarketScenario:
        """Generate a range-bound market scenario."""
        ticks = []
        base_time = int(time.time() * 1_000_000)

        # Oscillating between support and resistance
        support = Decimal("98.00")
        resistance = Decimal("102.00")
        mid_point = (support + resistance) / 2

        for minute in range(60):
            # Sine wave pattern
            import math

            cycle_position = math.sin(2 * math.pi * minute / 20)  # 20-minute cycles

            for second in range(60):
                if second % 3 == 0:  # Tick every 3 seconds
                    # Price oscillates between support and resistance
                    range_width = resistance - support
                    price = mid_point + (range_width / 2) * Decimal(str(cycle_position))

                    # Add small random noise
                    noise = Decimal(str(second % 7 - 3)) * Decimal("0.01")
                    price += noise

                    # Bounce off support/resistance
                    if price < support:
                        price = support + Decimal("0.01")
                    elif price > resistance:
                        price = resistance - Decimal("0.01")

                    tick = TickData(
                        symbol="RANGE",
                        timestamp_us=base_time + (minute * 60 + second) * 1_000_000,
                        last=price,
                        bid=price - Decimal("0.01"),
                        ask=price + Decimal("0.01"),
                        volume=500,  # Lower volume in range
                    )
                    ticks.append(tick)

        return MarketScenario(
            name="Range Bound Market",
            scenario_type=ScenarioType.RANGE_BOUND,
            duration_seconds=3600,  # 1 hour
            description="Price oscillating between support and resistance levels",
            ticks=ticks,
            bars=[],
            metadata={"support_level": 98.00, "resistance_level": 102.00, "range_width": 4.00, "cycle_period": 20},  # Minutes
        )

    @staticmethod
    def generate_volatile_market() -> MarketScenario:
        """Generate high volatility market scenario."""
        ticks = []
        base_time = int(time.time() * 1_000_000)

        # High volatility with no clear direction
        base_price = Decimal("50.00")

        import random

        random.seed(42)  # For reproducibility

        for minute in range(30):
            # Volatility clusters
            if minute % 5 < 2:  # High volatility periods
                volatility = Decimal("1.00")
            else:  # Lower volatility
                volatility = Decimal("0.20")

            for second in range(60):
                if second % 2 == 0:  # Frequent ticks
                    # Random walk with volatility
                    change = Decimal(str(random.gauss(0, float(volatility))))
                    price = base_price + change

                    # Ensure price stays positive
                    if price < Decimal("45.00"):
                        price = Decimal("45.00")
                    elif price > Decimal("55.00"):
                        price = Decimal("55.00")

                    tick = TickData(
                        symbol="VOLATILE",
                        timestamp_us=base_time + (minute * 60 + second) * 1_000_000,
                        last=price,
                        bid=price - volatility / 10,  # Spread proportional to volatility
                        ask=price + volatility / 10,
                        volume=int(1000 * float(volatility)),  # Volume increases with volatility
                    )
                    ticks.append(tick)

        return MarketScenario(
            name="High Volatility Market",
            scenario_type=ScenarioType.VOLATILE,
            duration_seconds=1800,  # 30 minutes
            description="Volatile market with clustering and wide price swings",
            ticks=ticks,
            bars=[],
            metadata={"volatility_regime": "high", "avg_true_range": 2.00, "volatility_clusters": True, "max_1min_move": 2.00},
        )

    @staticmethod
    def generate_illiquid_market() -> MarketScenario:
        """Generate illiquid market scenario."""
        ticks = []
        base_time = int(time.time() * 1_000_000)

        # Sparse trading with wide spreads
        last_price = Decimal("25.00")

        # Irregular tick timing
        tick_times = [0, 15, 23, 67, 89, 134, 178, 234, 267, 301, 356, 412, 489, 534, 598]

        for i, tick_time in enumerate(tick_times):
            # Wide and variable spreads
            spread = Decimal("0.10") + Decimal(str(i % 3)) * Decimal("0.05")

            # Price can move significantly between trades
            if i > 0:
                gap = Decimal(str(i % 5 - 2)) * Decimal("0.10")
                last_price += gap

            tick = TickData(
                symbol="ILLIQUID",
                timestamp_us=base_time + tick_time * 1_000_000,
                last=last_price,
                bid=last_price - spread / 2 if i % 4 != 0 else None,  # Sometimes no bid
                ask=last_price + spread / 2 if i % 3 != 0 else None,  # Sometimes no ask
                volume=10 * (i % 5 + 1),  # Very low volume
            )
            ticks.append(tick)

        return MarketScenario(
            name="Illiquid Market",
            scenario_type=ScenarioType.ILLIQUID,
            duration_seconds=600,  # 10 minutes
            description="Thinly traded market with wide spreads and gaps",
            ticks=ticks,
            bars=[],
            metadata={
                "avg_spread": 0.15,
                "avg_time_between_trades": 40,  # seconds
                "min_trade_size": 10,
                "max_trade_size": 50,
                "quote_availability": 0.75,  # 25% of time no quote
            },
        )

    @classmethod
    def generate_all_scenarios(cls) -> Dict[ScenarioType, MarketScenario]:
        """Generate all available scenarios.

        Returns:
            Dictionary mapping scenario type to scenario
        """
        return {
            ScenarioType.FLASH_CRASH: cls.generate_flash_crash_scenario(),
            ScenarioType.OPENING_AUCTION: cls.generate_opening_auction_volatility(),
            ScenarioType.NEWS_EVENT: cls.generate_news_event_gap(),
            ScenarioType.END_OF_DAY: cls.generate_end_of_day_cleanup(),
            ScenarioType.CORPORATE_ACTION: cls.generate_corporate_action_adjustment(),
            ScenarioType.TRENDING: cls.generate_trending_market(),
            ScenarioType.RANGE_BOUND: cls.generate_range_bound_market(),
            ScenarioType.VOLATILE: cls.generate_volatile_market(),
            ScenarioType.ILLIQUID: cls.generate_illiquid_market(),
        }


class ScenarioPlayer:
    """Plays back market scenarios for testing."""

    def __init__(self, scenario: MarketScenario):
        """Initialize with a scenario."""
        self.scenario = scenario
        self.current_index = 0
        self.start_time = None

    def start(self) -> None:
        """Start scenario playback."""
        self.start_time = time.time()
        self.current_index = 0

    def get_next_tick(self) -> TickData:
        """Get next tick if available based on elapsed time."""
        if self.start_time is None:
            self.start()

        elapsed = time.time() - self.start_time

        # Find ticks that should have been played
        while self.current_index < len(self.scenario.ticks):
            tick = self.scenario.ticks[self.current_index]
            tick_time = (tick.timestamp_us - self.scenario.ticks[0].timestamp_us) / 1_000_000

            if tick_time <= elapsed:
                self.current_index += 1
                return tick
            else:
                break

        return None

    def is_complete(self) -> bool:
        """Check if scenario playback is complete."""
        return self.current_index >= len(self.scenario.ticks)

    def get_progress(self) -> float:
        """Get playback progress as percentage."""
        return self.current_index / len(self.scenario.ticks) if self.scenario.ticks else 1.0
