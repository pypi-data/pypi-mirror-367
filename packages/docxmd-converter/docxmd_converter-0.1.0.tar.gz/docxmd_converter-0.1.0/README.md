# DocxMD Converter

[![PyPI version](https://badge.fury.io/py/docxmd-converter.svg)](https://badge.fury.io/py/docxmd-converter)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A powerful Python package for converting between Microsoft Word (.docx) and Markdown (.md) files with template support and recursive directory processing.

## ✨ Features

- **Bidirectional conversion**: `.docx` ⇄ `.md`
- **Template support**: Use custom .docx templates for consistent formatting
- **Recursive processing**: Convert entire directory trees while preserving structure
- **Dual interfaces**: Both CLI and GUI applications
- **Cross-platform**: Works on Windows, macOS, and Linux
- **Batch processing**: Convert multiple files in one operation
- **Detailed logging**: Track conversion progress and errors

## 🚀 Quick Start

### Installation

```bash
pip install docxmd-converter
```

**Note**: This package requires [Pandoc](https://pandoc.org/) to be installed on your system.

#### Installing Pandoc

**On Ubuntu/Debian:**
```bash
sudo apt-get install pandoc
```

**On macOS:**
```bash
brew install pandoc
```

**On Windows:**
Download from [pandoc.org](https://pandoc.org/installing.html) or use Chocolatey:
```bash
choco install pandoc
```

### Command Line Usage

#### Convert .docx files to Markdown
```bash
docxmd --src ./documents --dst ./markdown --direction docx2md
```

#### Convert Markdown to .docx with template
```bash
docxmd --src ./markdown --dst ./documents --direction md2docx --template ./template.docx
```

#### Enable verbose logging
```bash
docxmd --src ./input --dst ./output --direction docx2md --verbose
```

### GUI Usage

Launch the graphical interface:
```bash
docxmd-gui
```

The GUI provides an intuitive interface with:
- Directory selection dialogs
- Conversion direction selection
- Template file picker
- Real-time conversion logging
- Progress tracking

## 📖 Detailed Usage

### CLI Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `--src` | ✅ | Source directory containing files to convert |
| `--dst` | ✅ | Destination directory for converted files |
| `--direction` | ✅ | Conversion direction: `docx2md` or `md2docx` |
| `--template` | ❌ | Path to .docx template (only for `md2docx`) |
| `--verbose` | ❌ | Enable detailed logging |

### Python API

```python
from docxmd_converter import DocxMdConverter

# Initialize converter
converter = DocxMdConverter()

# Convert a single file
success = converter.convert_file(
    input_file="document.docx",
    output_file="document.md",
    direction="docx2md"
)

# Convert entire directory
successful, total = converter.convert_directory(
    src_dir="./documents",
    dst_dir="./markdown",
    direction="docx2md"
)

print(f"Converted {successful}/{total} files")
```

### Using Templates

Templates allow you to maintain consistent formatting when converting from Markdown to Word:

1. Create a .docx file with your desired styles (fonts, colors, spacing, etc.)
2. Use it as a template in conversion:

```bash
docxmd --src ./markdown --dst ./documents --direction md2docx --template ./my_template.docx
```

The template's styles will be applied to:
- Headings (H1-H6)
- Body text
- Lists (ordered and unordered)
- Tables
- Code blocks

## 🏗️ Project Structure

```
docxmd_converter/
├── __init__.py          # Package initialization
├── cli.py              # Command-line interface
├── gui.py              # Graphical user interface
└── core.py             # Core conversion functionality
```

## 🔧 Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/yourusername/docxmd-converter.git
cd docxmd-converter

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .

# Install development dependencies
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
# Format code
black docxmd_converter/

# Sort imports
isort docxmd_converter/

# Lint code
flake8 docxmd_converter/
```

## 📋 Requirements

- Python 3.8+
- [Pandoc](https://pandoc.org/) (external dependency)
- pypandoc>=1.11
- python-docx>=0.8.11

## 🐛 Known Issues

- **Large files**: Very large .docx files may take considerable time to convert
- **Complex formatting**: Some advanced Word formatting may not translate perfectly to Markdown
- **Images**: Image handling depends on Pandoc's capabilities

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Pandoc](https://pandoc.org/) - The universal markup converter
- [python-docx](https://python-docx.readthedocs.io/) - Python library for .docx files
- [pypandoc](https://github.com/NicklasTegner/pypandoc) - Python wrapper for Pandoc

## 📞 Support

If you encounter any problems or have questions, please:

1. Check the [GitHub Issues](https://github.com/yourusername/docxmd-converter/issues)
2. Create a new issue if needed
3. Provide detailed information about your problem

## 🗺️ Roadmap

- [ ] Enhanced template customization through GUI
- [ ] Support for additional formats (PDF, HTML)
- [ ] Batch template application
- [ ] Integration with cloud storage services
- [ ] Plugin system for custom converters