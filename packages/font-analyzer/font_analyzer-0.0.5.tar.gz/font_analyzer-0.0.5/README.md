# 🎨 Font Analyzer

> **Professional font analysis and compliance validation tool**

[![UV](https://img.shields.io/badge/dependency--manager-UV-orange.svg)](https://docs.astral.sh/uv/)
[![Docker](https://img.shields.io/badge/docker-supported-blue.svg)](https://docker.com)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-production--ready-brightgreen.svg)](https://github.com/aykut-canturk/font-analyzer)

**Font Analyzer** is a comprehensive tool for discovering, analyzing, and validating fonts from websites and local files against custom compliance policies. Built with modern Python tooling including [UV](https://docs.astral.sh/uv/) for efficient dependency management and Docker for seamless deployment across environments.

Perfect for **font compliance auditing**, **license validation**, **security assessments**, and **enterprise font governance**.

---

## 🚀 Quick Start

### 📦 Method 1: Global Package Installation (Recommended)

Install the font-analyzer as a system-wide command-line tool:

```bash
# Clone the repository
git clone https://github.com/aykut-canturk/font-analyzer.git
cd font-analyzer

# Install with pip (creates global font-analyzer command)
pip install -e .

# Run from anywhere on your system
font-analyzer --url "https://github.com"
font-analyzer --font_path "/path/to/Roboto-Regular.ttf"
# Directly allow fonts by name or regex
font-analyzer --font_path "/path/to/font.ttf" --allowed_fonts "Roboto" "Open Sans" ".*Arial.*"
font-analyzer --url "https://github.com" --allowed_fonts "Roboto" "Open Sans" ".*Arial.*"
```

### ⚡ Method 2: UV Development Environment (Fast)

Use UV for modern Python dependency management:

```bash
# Install UV (if not already installed)
pip install uv

# Clone and setup
git clone https://github.com/aykut-canturk/font-analyzer.git
cd font-analyzer

# Install dependencies
uv sync

# Run with UV
uv run python -m font_analyzer.main --url "https://github.com"
uv run python -m font_analyzer.main --font_path "/path/to/Roboto-Regular.ttf"
uv run python -m font_analyzer.main --font_path "/path/to/font.ttf" --allowed_fonts "Roboto" "Open Sans" ".*Arial.*"
uv run python -m font_analyzer.main --url "https://github.com" --allowed_fonts "Roboto" "Open Sans" ".*Arial.*"
```


### 🐳 Method 3: Docker (Zero Dependencies)

Run without any local Python installation:

```bash
# Build and run
docker build -t font-analyzer .
docker run --rm font-analyzer --url "https://github.com"

# With local fonts
docker run --rm -v "/path/to/fonts:/app/fonts" font-analyzer --font_path "/app/fonts/Roboto-Regular.ttf"
# With allowed fonts
docker run --rm font-analyzer --url "https://github.com" --allowed_fonts "Roboto" "Open Sans" ".*Arial.*"
docker run --rm -v "/path/to/fonts:/app/fonts" font-analyzer --font_path "/app/fonts/Roboto-Regular.ttf" --allowed_fonts "Roboto" "Open Sans" ".*Arial.*"
```

### 🐍 Method 4: Traditional Python (Legacy)

For environments where UV is not available:

```bash
# Clone and setup virtual environment
git clone https://github.com/aykut-canturk/font-analyzer.git
cd font-analyzer
python -m venv .venv
.venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/macOS

# Install dependencies
pip install -e .

# Run
font-analyzer --url "https://github.com"
font-analyzer --url "https://github.com" --allowed_fonts "Roboto" "Open Sans" ".*Arial.*"
```

## 🚀 Features & Capabilities

| Feature | Description | Status |
|---------|-------------|--------|
| 🌐 **Website Font Discovery** | Automatically detect and download fonts from web pages | ✅ Production Ready |
| 📋 **Comprehensive Metadata** | Extract font family, style, version, copyright, and licensing info | ✅ Production Ready |
| ✅ **Policy-Based Validation** | Validate fonts against custom regex-based compliance patterns | ✅ Production Ready |
| 🔧 **Multi-Format Support** | Support for TTF, OTF, WOFF, WOFF2, and other web font formats | ✅ Production Ready |
| 📊 **Professional Reporting** | Detailed compliance reports with color-coded terminal output | ✅ Production Ready |
| 🐳 **Containerization** | Full Docker and Docker Compose support for any environment | ✅ Production Ready |
| ⚡ **Modern Tooling** | UV-powered dependency management for faster builds | ✅ Production Ready |
| 🎯 **Global CLI Tool** | Install as system-wide `font-analyzer` command | ✅ Production Ready |
| 📝 **Structured Logging** | Comprehensive logging with configurable output levels | ✅ Production Ready |
| ⚙️ **Flexible Configuration** | Environment variables, custom whitelists, and runtime options | ✅ Production Ready |

---

## 🔧 Installation Methods

### 📦 Method 1: Global Package Installation

**Best for**: System administrators and frequent users

```bash
# Clone and install globally
git clone https://github.com/aykut-canturk/font-analyzer.git
cd font-analyzer
pip install -e .

# Available system-wide
font-analyzer --help
cd ~
font-analyzer --url "https://github.com"
```

### ⚡ Method 2: UV Development Environment

**Best for**: Python developers and contributors

```bash
# Install UV (modern Python package manager)
pip install uv
# or
curl -LsSf https://astral.sh/uv/install.sh | sh  # Unix/macOS
# or  
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"  # Windows

# Setup project
git clone https://github.com/aykut-canturk/font-analyzer.git
cd font-analyzer
uv sync

# Use with UV prefix
uv run python -m font_analyzer.main --help
```

### 🐳 Method 3: Docker Deployment

**Best for**: Production environments and CI/CD

```bash
# Direct Docker usage
git clone https://github.com/aykut-canturk/font-analyzer.git
cd font-analyzer
docker build -t font-analyzer .
docker run --rm font-analyzer --help

# Docker Compose for complex scenarios
docker-compose up font-analyzer
```

### 🐍 Method 4: Traditional Python Virtual Environment

**Best for**: Legacy Python environments

```bash
# Traditional approach
git clone https://github.com/aykut-canturk/font-analyzer.git
cd font-analyzer
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Unix/macOS
pip install -e .
font-analyzer --help
```

---

## 📚 Usage Examples & Scenarios

### 🌐 Website Font Analysis

```bash
# Basic website analysis (Global Installation)
font-analyzer --url "https://github.com"
font-analyzer --url "https://github.com" --allowed_fonts "Roboto" "Open Sans" ".*Arial.*"

# With UV environment
uv run python -m font_analyzer.main --url "https://github.com" --allowed_fonts "Roboto" "Open Sans" ".*Arial.*"

# Using allowed fonts parameters
font-analyzer --url "https://github.com" --allowed_fonts "Roboto" "Open Sans" ".*Arial.*"
```

### 📁 Local Font File Analysis

```bash
# Single font analysis (Global Installation)
font-analyzer --font_path "/path/to/fontfile" --allowed_fonts "Roboto" "Open Sans" ".*Arial.*"

# With allowed fonts parameter
font-analyzer --font_path "/path/to/fontfile" --allowed_fonts "Roboto" "Open Sans" ".*Arial.*"

# With UV environment
uv run python -m font_analyzer.main --font_path "/path/to/fontfile" --allowed_fonts "Roboto" "Open Sans" ".*Arial.*"
```

### 🐳 Docker Usage Examples

```bash
# Website analysis with Docker
docker run --rm font-analyzer --url "https://github.com" --allowed_fonts "Roboto" "Open Sans" ".*Arial.*"

# Local file analysis with volume mount
docker run --rm -v /path/to/fonts:/app/fonts font-analyzer --font_path "/path/to/fontfile" --allowed_fonts "Roboto" "Open Sans" ".*Arial.*"

# With allowed fonts using Docker
docker run --rm \
  font-analyzer --url "https://github.com" --allowed_fonts "Roboto" "Open Sans" ".*Arial.*"
```

### 🔧 Environment Variable Usage

```bash
# Set environment variables (Windows)
set URL=https://github.com
set FONT_PATH=/path/to/fontfile
set ALLOWED_FONTS=Roboto,Open Sans,.*Arial.*
font-analyzer

# Set environment variables (Linux/macOS)
export URL=https://github.com
export FONT_PATH=/path/to/fontfile
export ALLOWED_FONTS=Roboto,Open Sans,.*Arial.*
font-analyzer
```

---

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `URL` | Website URL to analyze | `https://github.com` |
| `FONT_PATH` | Path to font file | `./fonts/font.woff` |
| `ALLOWED_FONTS` | Comma-separated list of allowed font patterns | `Roboto,Open Sans,.*Arial.*` |

---

## 📊 Output Examples

### ✅ Compliant Website

```bash
$ uv run python -m font_analyzer.main --url "https://github.com"

2025-07-18 15:30:12,346 - INFO - Loaded 12 allowed font patterns
2025-07-18 15:30:12,347 - INFO - Scraping fonts from URL: https://github.com
2025-07-18 15:30:13,456 - INFO - Downloaded: Inter-Regular.woff2
2025-07-18 15:30:13,789 - INFO - Downloaded: Inter-SemiBold.woff2

=== Metadata for Inter-Regular.woff2 (Inter) === ✓ ALLOWED (pattern: inter)
NameID 1: Inter
NameID 2: Regular
NameID 4: Inter Regular
NameID 6: Inter-Regular

✓ All fonts are in the whitelist!

╔══════════════════════════════════════════════════╗
║             📊 FONT ANALYSIS SUMMARY             ║
╠══════════════════════════════════════════════════╣
║ 🔍 Found Fonts             2                     ║
║ ✅ Allowed Fonts           2                     ║
║ ❌ Disallowed Fonts        0                     ║
║ 📈 Total Analyzed          2                     ║
╠══════════════════════════════════════════════════╣
║ ✅ STATUS: FULLY COMPLIANT                       ║
╚══════════════════════════════════════════════════╝

📊 Compliance Rate: 100.0%
Progress: [████████████████████████████████] 100.0%
Operation completed successfully.
```

### ⚠️ Non-Compliant Website

```bash
$ uv run python -m font_analyzer.main --url "https://github.com"

=== Metadata for CustomFont-Bold.woff (CustomFont) === ✗ NOT ALLOWED
=== Metadata for ProprietaryFont.ttf (ProprietaryFont) === ✗ NOT ALLOWED

✗ Some fonts are not in the whitelist!

╔══════════════════════════════════════════════════╗
║             📊 FONT ANALYSIS SUMMARY             ║
╠══════════════════════════════════════════════════╣
║ 🔍 Found Fonts             3                     ║
║ ✅ Allowed Fonts           1                     ║
║ ❌ Disallowed Fonts        2                     ║
║ 📈 Total Analyzed          3                     ║
╠══════════════════════════════════════════════════╣
║ ⚠️ STATUS: COMPLIANCE ISSUES FOUND               ║
╚══════════════════════════════════════════════════╝

❌ Disallowed Fonts:
   1. CustomFont
   2. ProprietaryFont

📊 Compliance Rate: 33.3%
Progress: [██████████░░░░░░░░░░░░░░░░░░░░░░] 33.3%
```

---

## 🏗️ Project Structure

```text
font-analyzer/
├── 📄 pyproject.toml              # Python project configuration & dependencies
├── 🔒 uv.lock                     # UV dependency lock file (reproducible builds)
├── 📘 README.md                   # Complete project documentation
├── 📄 LICENSE                     # MIT License file
├── 🔧 .uvrc                       # UV configuration settings
├── ⚙️ Makefile                    # Cross-platform build automation
├── 🐳 Dockerfile                  # Multi-stage Docker build
├── 🐳 docker-compose.yml          # Development Docker Compose
├── 🐳 docker-compose.prod.yml     # Production Docker Compose
├── 📁 scripts/
│   └── ⚙️ dev.bat                 # Windows development utilities
├── 📁 src/font_analyzer/          # Main application package
│   ├── 🐍 __init__.py             # Package initialization
│   ├── 🐍 main.py                 # CLI entry point & argument parsing
│   ├── 📁 config/                 # Configuration management
│   │   ├── 🐍 __init__.py
│   │   └── 🐍 settings.py         # Application settings & constants
│   ├── 📁 core/                   # Core analysis engine
│   │   ├── 🐍 __init__.py
│   │   ├── 🐍 analyzer.py         # Main font analysis orchestrator
│   │   ├── 🐍 metadata.py         # Font metadata extraction engine
│   │   └── 🐍 whitelist.py        # Policy validation & pattern matching
│   └── 📁 utils/                  # Utility modules
│       ├── 🐍 __init__.py
│       ├── 🐍 formatter.py        # Output formatting & styling
│       ├── 🐍 logger.py           # Structured logging utilities
│       └── 🐍 web_scraper.py      # Web scraping & font discovery
├── 📁 tests/                      # Test suite
│   └── 🐍 test_font_analyzer.py   # Comprehensive unit tests
├── 📁 fonts/                      # Font files
└── 📁 logs/                       # Application runtime logs
---

## 🎯 Use Cases & Benefits

### 🏢 Enterprise Use Cases

- **Font License Compliance**: Ensure only licensed fonts are used across web properties
- **Brand Consistency**: Validate adherence to brand guidelines and font policies  
- **Security Auditing**: Identify unauthorized or potentially malicious font files
- **Migration Planning**: Analyze existing font usage before platform migrations
- **Cost Optimization**: Track font licensing costs and usage patterns

### 🚀 Technical Benefits

- **⚡ Fast dependency management** with UV
- **🔒 Reproducible builds** with exact dependency locking
- **🎯 Better conflict resolution** preventing dependency hell
- **🔄 Efficient updates** and dependency management
- **📦 Unified tooling** for dependencies, virtual environments, and scripts

---

## 🧪 Testing & Quality

### Run Tests

```bash
# With UV
uv run python -m unittest tests.test_font_analyzer -v

# With coverage
uv run pytest tests/ -v --cov=src --cov-report=html --cov-report=term

# Traditional way
python -m pytest tests/ -v
```

### Code Quality

```bash
# Format code
uv run black src tests

# Lint code  
uv run flake8 src tests --max-line-length=88 --extend-ignore=E203,W503

# Type checking
uv run mypy src

# All checks at once
scripts\dev.bat dev-check  # Windows
make quality              # Linux/macOS
```

---

## 🤝 Contributing

We welcome contributions! Here's how to get started:

### Quick Start for Contributors

```bash
# Clone and setup development environment
git clone https://github.com/aykut-canturk/font-analyzer.git
cd font-analyzer
uv sync

# Install pre-commit hooks
uv run pre-commit install

# Make your changes and run tests
uv run python -m pytest tests/ -v
scripts\dev.bat dev-check  # Windows - run all quality checks
```

### Development Workflow

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Make** your changes
4. **Test** your changes (`uv run pytest tests/`)
5. **Format** code (`uv run black src tests`)
6. **Commit** changes (`git commit -m 'Add amazing feature'`)
7. **Push** to branch (`git push origin feature/amazing-feature`)
8. **Open** a Pull Request

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **[UV](https://docs.astral.sh/uv/)** - Modern Python package management
- **[FontTools](https://fonttools.readthedocs.io/)** - Font metadata extraction
- **[BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/)** - HTML parsing
- **[Colorama](https://pypi.org/project/colorama/)** - Colored terminal output
- **[Docker](https://docker.com)** - Containerization platform

---

## 📞 Support & Community

- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/aykut-canturk/font-analyzer/issues)
- 💡 **Feature Requests**: [GitHub Discussions](https://github.com/aykut-canturk/font-analyzer/discussions)
- 📧 **Email**: [canturk.aykut@gmail.com](mailto:canturk.aykut@gmail.com)
- 📚 **UV Documentation**: [docs.astral.sh/uv](https://docs.astral.sh/uv/)

---

---

**Font Analyzer** - *Professional font analysis and compliance validation*

Made with ❤️ by [Aykut Cantürk](https://github.com/aykut-canturk)

**[⭐ Star this repo](https://github.com/aykut-canturk/font-analyzer)** if you find it useful!
