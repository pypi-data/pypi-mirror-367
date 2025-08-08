"""
Core functionality for document conversion between .docx and .md formats.
"""

import logging
from pathlib import Path
from typing import List, Optional, Tuple, Union

import pypandoc


class ConversionError(Exception):
    """Custom exception for conversion errors."""

    pass


class DocxMdConverter:
    """Main converter class for .docx ⇄ .md conversion."""

    def __init__(self, log_level: str = "INFO"):
        """Initialize the converter.

        Args:
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        """
        self.logger = self._setup_logging(log_level)
        self._check_pandoc()

    def _setup_logging(self, level: str) -> logging.Logger:
        """Setup logging configuration."""
        logger = logging.getLogger(__name__)
        logger.setLevel(getattr(logging, level.upper()))

        # Create console handler if not exists
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    def _check_pandoc(self) -> None:
        """Check if pandoc is available."""
        try:
            version = pypandoc.get_pandoc_version()
            self.logger.info(f"Pandoc version: {version}")
        except OSError:
            raise ConversionError(
                "Pandoc is not installed. Please install pandoc first.\n"
                "Visit: https://pandoc.org/installing.html"
            )

    def convert_file(
        self,
        input_file: Union[str, Path],
        output_file: Union[str, Path],
        direction: str,
        template_path: Optional[Union[str, Path]] = None,
    ) -> bool:
        """Convert a single file.

        Args:
            input_file: Path to input file
            output_file: Path to output file
            direction: Conversion direction ('docx2md' or 'md2docx')
            template_path: Path to .docx template (for md2docx only)

        Returns:
            True if conversion successful, False otherwise
        """
        input_file = Path(input_file)
        output_file = Path(output_file)

        if not input_file.exists():
            self.logger.error(f"Input file does not exist: {input_file}")
            return False

        # Create output directory if it doesn't exist
        output_file.parent.mkdir(parents=True, exist_ok=True)

        try:
            if direction == "docx2md":
                self._convert_docx_to_md(input_file, output_file)
            elif direction == "md2docx":
                self._convert_md_to_docx(
                    input_file,
                    output_file,
                    Path(template_path) if template_path else None,
                )
            else:
                raise ConversionError(f"Invalid direction: {direction}")

            self.logger.info(f"Successfully converted: {input_file} -> {output_file}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to convert {input_file}: {str(e)}")
            return False

    def _convert_docx_to_md(self, input_file: Path, output_file: Path) -> None:
        """Convert .docx to .md using pandoc."""
        extra_args = [
            "--extract-media",
            str(output_file.parent / "media"),
            "--wrap=none",
        ]

        pypandoc.convert_file(
            str(input_file), "md", outputfile=str(output_file), extra_args=extra_args
        )

    def _convert_md_to_docx(
        self, input_file: Path, output_file: Path, template_path: Optional[Path] = None
    ) -> None:
        """Convert .md to .docx using pandoc."""
        extra_args = []

        if template_path:
            template_path = Path(template_path)
            if template_path.exists():
                extra_args.extend(["--reference-doc", str(template_path)])
            else:
                self.logger.warning(f"Template not found: {template_path}")

        pypandoc.convert_file(
            str(input_file), "docx", outputfile=str(output_file), extra_args=extra_args
        )

    def convert_directory(
        self,
        src_dir: Union[str, Path],
        dst_dir: Union[str, Path],
        direction: str,
        template_path: Optional[Union[str, Path]] = None,
    ) -> Tuple[int, int]:
        """Convert all files in directory recursively.

        Args:
            src_dir: Source directory path
            dst_dir: Destination directory path
            direction: Conversion direction ('docx2md' or 'md2docx')
            template_path: Path to .docx template (for md2docx only)

        Returns:
            Tuple of (successful_conversions, total_files)
        """
        src_dir = Path(src_dir)
        dst_dir = Path(dst_dir)

        if not src_dir.exists():
            raise ConversionError(f"Source directory does not exist: {src_dir}")

        # Determine file extension to search for
        if direction == "docx2md":
            file_pattern = "*.docx"
            output_ext = ".md"
        elif direction == "md2docx":
            file_pattern = "*.md"
            output_ext = ".docx"
        else:
            raise ConversionError(f"Invalid direction: {direction}")

        # Find all files to convert
        files_to_convert = list(src_dir.rglob(file_pattern))

        if not files_to_convert:
            self.logger.warning(f"No {file_pattern} files found in {src_dir}")
            return 0, 0

        successful_conversions = 0
        total_files = len(files_to_convert)

        self.logger.info(f"Found {total_files} files to convert")

        for input_file in files_to_convert:
            # Calculate relative path to preserve directory structure
            relative_path = input_file.relative_to(src_dir)
            output_file = dst_dir / relative_path.with_suffix(output_ext)

            if self.convert_file(input_file, output_file, direction, template_path):
                successful_conversions += 1

        self.logger.info(
            f"Conversion completed: {successful_conversions}/{total_files} files"
        )

        return successful_conversions, total_files

    def get_supported_directions(self) -> List[str]:
        """Get list of supported conversion directions."""
        return ["docx2md", "md2docx"]

    def validate_template(self, template_path: Union[str, Path]) -> bool:
        """Validate if template file is a valid .docx file.

        Args:
            template_path: Path to template file

        Returns:
            True if valid, False otherwise
        """
        template_path = Path(template_path)

        if not template_path.exists():
            self.logger.error(f"Template file does not exist: {template_path}")
            return False

        if template_path.suffix.lower() != ".docx":
            self.logger.error(f"Template must be a .docx file: {template_path}")
            return False

        return True
