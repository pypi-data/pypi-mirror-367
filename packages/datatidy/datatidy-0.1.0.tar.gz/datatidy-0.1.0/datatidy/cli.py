"""Command-line interface for DataTidy."""

import argparse
import sys
from pathlib import Path
from .core import DataTidy


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="DataTidy: Configuration-driven data processing and cleaning"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Process command
    process_parser = subparsers.add_parser(
        "process", help="Process data using configuration"
    )
    process_parser.add_argument("config", help="Path to YAML configuration file")
    process_parser.add_argument(
        "-i", "--input", help="Input data file (overrides config)"
    )
    process_parser.add_argument("-o", "--output", help="Output file path")
    process_parser.add_argument(
        "--ignore-errors",
        action="store_true",
        help="Continue processing despite validation errors",
    )
    process_parser.add_argument(
        "--mode",
        choices=["strict", "partial", "fallback"],
        default="strict",
        help="Processing mode (default: strict)",
    )
    process_parser.add_argument("--error-log", help="Export error log to JSON file")
    process_parser.add_argument(
        "--show-summary", action="store_true", help="Show detailed processing summary"
    )
    process_parser.add_argument(
        "--show-recommendations",
        action="store_true",
        help="Show processing recommendations",
    )

    # Validate command
    validate_parser = subparsers.add_parser(
        "validate", help="Validate configuration file"
    )
    validate_parser.add_argument("config", help="Path to YAML configuration file")

    # Sample command
    sample_parser = subparsers.add_parser(
        "sample", help="Create sample configuration file"
    )
    sample_parser.add_argument("output", help="Output path for sample configuration")

    # Version command
    subparsers.add_parser("version", help="Show version information")

    args = parser.parse_args()

    if args.command == "process":
        process_command(args)
    elif args.command == "validate":
        validate_command(args)
    elif args.command == "sample":
        sample_command(args)
    elif args.command == "version":
        version_command()
    else:
        parser.print_help()


def process_command(args: argparse.Namespace) -> None:
    """Handle process command."""
    try:
        # Initialize DataTidy
        datatidy = DataTidy()

        # Load configuration
        print(f"🔧 Loading configuration from: {args.config}")
        datatidy.load_config(args.config)

        # Override settings if specified
        if datatidy.config and "global_settings" not in datatidy.config:
            datatidy.config["global_settings"] = {}

        if args.ignore_errors and datatidy.config:
            datatidy.config["global_settings"]["ignore_errors"] = True

        # Set processing mode
        if args.mode != "strict" and datatidy.config:
            datatidy.config["global_settings"]["processing_mode"] = args.mode
            datatidy.set_processing_mode(args.mode)

        # Process data with fallback capabilities
        input_data = args.input if args.input else None
        print(f"🚀 Processing data in {args.mode} mode...")

        # Use enhanced processing
        result = datatidy.process_data_with_fallback(input_data)

        if args.output:
            # Save processed data
            result.data.to_csv(args.output, index=False)
            print(f"💾 Processed data saved to: {args.output}")
        else:
            # Display first few rows
            print("📊 Processed data (first 10 rows):")
            print(result.data.head(10).to_string())

        # Show processing summary
        if args.show_summary or not result.success:
            summary = datatidy.get_processing_summary()
            print("\n📈 Processing Summary:")
            print(f"   Mode: {summary['processing_mode']}")
            print(f"   Success: {'✅' if summary['success'] else '❌'}")
            print(f"   Processing time: {summary['processing_time']:.2f}s")
            print(
                f"   Successful columns: {summary['successful_columns']}/{summary['total_columns']}"
            )

            if summary["failed_columns"] > 0:
                print(f"   Failed columns: {summary['failed_columns']}")
            if summary["skipped_columns"] > 0:
                print(f"   Skipped columns: {summary['skipped_columns']}")
            if summary["fallback_used"]:
                print("   🔄 Fallback processing was used")

        # Show recommendations
        if args.show_recommendations or (
            result.failed_columns and args.mode == "strict"
        ):
            recommendations = datatidy.get_processing_recommendations()
            if recommendations:
                print("\n💡 Recommendations:")
                for rec in recommendations:
                    print(f"   {rec}")

        # Export error log if requested
        if args.error_log:
            datatidy.export_error_log(args.error_log)
            print(f"📋 Error log exported to: {args.error_log}")

        # Show errors in console if any
        if result.error_log:
            print(f"\n⚠️  Processing Issues ({len(result.error_log)} total):")
            for error in result.error_log[:5]:  # Show first 5 errors
                print(f"   - {error['column']}: {error['error_message']}")
            if len(result.error_log) > 5:
                print(
                    f"   ... and {len(result.error_log) - 5} more (see --error-log for details)"
                )

        if result.success:
            print("✅ Processing completed successfully!")
        else:
            print("⚠️  Processing completed with issues")
            if args.mode == "strict":
                sys.exit(1)

    except Exception as e:
        print(f"❌ Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


def validate_command(args: argparse.Namespace) -> None:
    """Handle validate command."""
    try:
        datatidy = DataTidy()
        datatidy.load_config(args.config)

        if datatidy.validate_config():
            print(f"Configuration '{args.config}' is valid!")
        else:
            print(f"Configuration '{args.config}' is invalid!", file=sys.stderr)
            sys.exit(1)

    except Exception as e:
        print(f"Validation error: {str(e)}", file=sys.stderr)
        sys.exit(1)


def sample_command(args: argparse.Namespace) -> None:
    """Handle sample command."""
    try:
        output_path = Path(args.output)

        # Check if file already exists
        if output_path.exists():
            response = input(f"File '{args.output}' already exists. Overwrite? (y/N): ")
            if response.lower() != "y":
                print("Operation cancelled.")
                return

        # Create sample configuration
        DataTidy.create_sample_config(args.output)
        print(f"Sample configuration created at: {args.output}")

    except Exception as e:
        print(f"Error creating sample: {str(e)}", file=sys.stderr)
        sys.exit(1)


def version_command() -> None:
    """Handle version command."""
    from . import __version__

    print(f"DataTidy version {__version__}")


if __name__ == "__main__":
    main()
