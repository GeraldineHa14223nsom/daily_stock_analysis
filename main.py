#!/usr/bin/env python3
"""Daily Stock Analysis - Main entry point.

This module orchestrates the daily stock analysis pipeline:
- Fetches stock data from configured sources
- Runs technical and fundamental analysis
- Generates reports and notifications
"""

import os
import sys
import logging
import argparse
from datetime import datetime

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(f"logs/analysis_{datetime.now().strftime('%Y%m%d')}.log"),
    ],
)
logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Daily Stock Analysis Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--symbols",
        nargs="+",
        help="Stock symbols to analyze (e.g. AAPL TSLA MSFT)",
    )
    parser.add_argument(
        "--market",
        choices=["us", "cn", "hk"],
        default=os.getenv("DEFAULT_MARKET", "us"),
        help="Market to analyze (default: us)",
    )
    parser.add_argument(
        "--output",
        choices=["console", "email", "file", "all"],
        default=os.getenv("OUTPUT_MODE", "console"),
        help="Output mode for analysis results",
    )
    parser.add_argument(
        "--date",
        default=datetime.now().strftime("%Y-%m-%d"),
        help="Analysis date in YYYY-MM-DD format (default: today)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run analysis without sending notifications",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose/debug logging",
    )
    return parser.parse_args()


def setup_environment() -> None:
    """Validate required environment variables and create necessary directories."""
    os.makedirs("logs", exist_ok=True)
    os.makedirs("output", exist_ok=True)
    os.makedirs("data/cache", exist_ok=True)

    required_vars = []
    missing = [v for v in required_vars if not os.getenv(v)]
    if missing:
        logger.error("Missing required environment variables: %s", ", ".join(missing))
        sys.exit(1)


def run_analysis(args: argparse.Namespace) -> int:
    """Execute the stock analysis pipeline.

    Args:
        args: Parsed command-line arguments.

    Returns:
        Exit code (0 for success, non-zero for failure).
    """
    logger.info("Starting daily stock analysis for date: %s", args.date)
    logger.info("Market: %s | Output: %s | Dry-run: %s", args.market, args.output, args.dry_run)

    symbols = args.symbols or os.getenv("WATCH_SYMBOLS", "").split(",")
    symbols = [s.strip().upper() for s in symbols if s.strip()]

    if not symbols:
        logger.warning("No symbols specified. Add --symbols or set WATCH_SYMBOLS in .env")
        return 1

    logger.info("Analyzing %d symbol(s): %s", len(symbols), ", ".join(symbols))

    # Pipeline steps will be implemented in subsequent modules
    # 1. data_fetcher.fetch(symbols, args.market, args.date)
    # 2. analyzer.analyze(data)
    # 3. reporter.report(results, args.output, dry_run=args.dry_run)

    logger.info("Analysis pipeline completed successfully.")
    return 0


def main() -> None:
    """Main entry point."""
    args = parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    setup_environment()

    exit_code = run_analysis(args)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
