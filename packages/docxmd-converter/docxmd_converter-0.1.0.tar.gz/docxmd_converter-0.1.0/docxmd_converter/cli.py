"""
Command-line interface for DocxMD Converter.
"""

import argparse
import sys
from pathlib import Path

from .core import ConversionError, DocxMdConverter


def create_parser() -> argparse.ArgumentParser:
    """Create and configure argument parser."""
    parser = argparse.ArgumentParser(
        prog="docxmd",
        description="Convert between .docx and .md files with template support",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert all .docx files to .md
  docxmd --src ./documents --dst ./markdown --direction docx2md

  # Convert all .md files to .docx with template
  docxmd --src ./markdown --dst ./documents --direction md2docx \\
         --template ./template.docx

  # Enable debug logging
  docxmd --src ./input --dst ./output --direction docx2md --verbose
        """,
    )

    parser.add_argument(
        "--src",
        type=str,
        required=True,
        help="Source directory containing files to convert",
    )

    parser.add_argument(
        "--dst",
        type=str,
        required=True,
        help="Destination directory for converted files",
    )

    parser.add_argument(
        "--direction",
        type=str,
        required=True,
        choices=["docx2md", "md2docx"],
        help="Conversion direction: docx2md or md2docx",
    )

    parser.add_argument(
        "--template",
        type=str,
        help="Path to .docx template file (only for md2docx direction)",
    )

    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose logging"
    )

    parser.add_argument("--version", action="version", version="%(prog)s 0.1.0")

    return parser


def validate_args(args: argparse.Namespace) -> None:
    """Validate command-line arguments."""
    src_path = Path(args.src)
    if not src_path.exists():
        raise ConversionError(f"Source directory does not exist: {args.src}")

    if not src_path.is_dir():
        raise ConversionError(f"Source path is not a directory: {args.src}")

    # Validate template if provided
    if args.template:
        if args.direction != "md2docx":
            raise ConversionError("Template can only be used with md2docx direction")

        template_path = Path(args.template)
        if not template_path.exists():
            raise ConversionError(f"Template file does not exist: {args.template}")

        if template_path.suffix.lower() != ".docx":
            raise ConversionError(f"Template must be a .docx file: {args.template}")


def main() -> int:
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()

    try:
        # Validate arguments
        validate_args(args)

        # Setup converter
        log_level = "DEBUG" if args.verbose else "INFO"
        converter = DocxMdConverter(log_level=log_level)

        # Convert files
        successful, total = converter.convert_directory(
            src_dir=args.src,
            dst_dir=args.dst,
            direction=args.direction,
            template_path=args.template,
        )

        if successful == total:
            print(f"✅ Successfully converted all {total} files")
            return 0
        else:
            print(f"⚠️  Converted {successful}/{total} files (some errors occurred)")
            return 1

    except ConversionError as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\n❌ Conversion cancelled by user", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
