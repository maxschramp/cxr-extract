# CXR Extract

Extract render elements from Corona Renderer CXR files.

## Features

- 🎯 Interactive selection of sequences and frames
- 🎨 Extract specific render elements or all at once
- 📁 Batch processing of multiple files
- 🔄 Automatic sequence detection
- ⚡ Fast batch extraction using CoronaImageCmd

## Installation

### From Source

```bash
git clone https://github.com/yourusername/cxr-extract.git
cd cxr-extract
pip install -e .
```

### Requirements

- Python 3.7+
- Corona Renderer (for CoronaImageCmd.exe)
- OpenEXR (optional, for element parsing)

## Usage

### Basic Usage

```bash
# Extract from a single file
cxr-extract scene.0001.cxr

# Extract from a directory
cxr-extract /path/to/renders/

# Specify output format
cxr-extract scene.0001.cxr --format jpg

# Add prefix to output folders
cxr-extract renders/ --prefix extracted
```

### Command-Line Options

```
usage: cxr-extract [-h] [-v] [--version] [--ciepath CIEPATH] [--prefix PREFIX]
                   [--format {exr,jpg}] [--overwrite]
                   input

positional arguments:
  input                 Input CXR file or directory

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         Enable verbose output
  --version             show program's version number and exit
  --ciepath CIEPATH     Path to CoronaImageCmd.exe
  --prefix PREFIX       Prefix for output folder name
  --format {exr,jpg}    Output format (default: exr)
  --overwrite           Overwrite existing files
```

## Interactive Mode

When running cxr-extract, you'll be prompted to:

1. **Select sequences** - Choose which sequences to process (if multiple found)
2. **Select frames** - Choose entire sequence or individual frames
3. **Select elements** - Choose which render elements to extract

## Output Structure

Extracted elements are saved in folders named after the sequence:

```
/path/to/renders/
├── output.0000.cxr
├── output.0001.cxr
└── output/                    # Output folder
    ├── output_BEAUTY.0000.exr
    ├── output_BEAUTY.0001.exr
    ├── output_Alpha.0000.exr
    └── output_Alpha.0001.exr
```

## Development

### Setup Development Environment

```bash
git clone https://github.com/yourusername/cxr-extract.git
cd cxr-extract
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
```

### Project Structure

```
cxr-extract/
├── src/
│   └── cxr_extract/
│       ├── __init__.py      # Package initialization
│       ├── core.py          # CXRFile class
│       ├── filesystem.py    # File collection
│       ├── extractor.py     # Extraction logic
│       ├── ui.py            # Interactive UI
│       └── cli.py           # CLI interface
├── tests/                   # Test files
├── setup.py                 # Package configuration
├── README.md               # This file
├── LICENSE                 # License file
└── .gitignore             # Git ignore rules
```

## License

MIT License - see LICENSE file for details

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
