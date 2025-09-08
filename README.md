# ShopQuote - Integrated Manufacturing Quote System

A comprehensive web application for processing CAD files and generating manufacturing quotes with intelligent OCR and business rule compliance.

## 🏗️ Project Structure

This project follows a modular architecture designed for scalability and maintainability:

```
shopquote/
├── src/                    # Main application source code
│   ├── app.py             # Main Taipy application entry point
│   ├── config/            # Application configuration
│   ├── core/              # Core business logic
│   │   ├── io.py          # File I/O operations
│   │   ├── rules.py       # Business rules engine
│   │   └── validation.py  # Data validation
│   ├── processors/        # File processing modules
│   │   ├── pdf/           # PDF processing (OCR, text extraction)
│   │   ├── cad/           # CAD file processing (DXF, STEP)
│   │   └── __init__.py
│   ├── ui/                # User interface components
│   │   ├── pages/         # Taipy page definitions
│   │   ├── components/    # Reusable UI components
│   │   └── static/        # CSS, images, assets
│   └── utils/             # Shared utilities
│       ├── formatting.py  # Data formatting helpers
│       ├── logging.py     # Logging configuration
│       └── __init__.py
├── data/                  # Data files and resources
│   ├── csv/               # CSV data files
│   ├── templates/         # Document templates
│   └── samples/           # Sample files for testing
├── business_rules/        # Business rule definitions
│   ├── pdf_processing.txt # PDF-specific rules
│   ├── ui_formatting.txt  # UI formatting rules
│   ├── quote_export.txt   # Quote export rules
│   └── validation.txt     # Data validation rules
├── tests/                 # Test suite
│   ├── unit/              # Unit tests
│   ├── integration/       # Integration tests
│   ├── fixtures/          # Test data
│   └── conftest.py        # Test configuration
├── scripts/               # Utility scripts
│   ├── setup.py           # Development setup
│   ├── migrate.py         # Data migration scripts
│   └── deploy.py          # Deployment scripts
├── docs/                  # Documentation
│   ├── api/               # API documentation
│   ├── user_guide/        # User documentation
│   └── development/       # Developer documentation
├── docker/                # Docker configuration
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── nginx.conf
├── .github/               # GitHub configuration
│   ├── workflows/         # CI/CD pipelines
│   └── ISSUE_TEMPLATE/    # Issue templates
├── requirements.txt       # Python dependencies
├── pyproject.toml         # Project configuration
├── .gitignore            # Git ignore rules
└── README.md             # This file
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Tesseract OCR (for PDF processing)
- FreeCAD (optional, for STEP file processing)

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd shopquote
   ```

2. **Set up virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application:**
   ```bash
   python src/app.py
   ```

## 📋 Features

- **Intelligent File Processing**: Support for PDF, DXF, and STEP files
- **OCR Integration**: Automatic text extraction from scanned documents
- **Business Rule Engine**: Configurable processing rules and validation
- **Quote Generation**: Automated pricing calculations with markup
- **Web Interface**: Modern Taipy-based UI with responsive design
- **Export Capabilities**: Multiple output formats (TXT, PDF)
- **Audit Trail**: Comprehensive logging and session tracking

## 🔧 Development

### Project Organization Guidelines

**Whenever a new file needs to be created and there isn't a proper place for it in the existing structure, create a new folder that fits the logical grouping and update this guide accordingly to maintain consistency.**

#### Adding New Components

1. **Identify the component type:**
   - **Core Logic**: Add to `src/core/`
   - **UI Components**: Add to `src/ui/components/`
   - **File Processors**: Add to `src/processors/`
   - **Utilities**: Add to `src/utils/`
   - **Business Rules**: Add to `business_rules/`
   - **Tests**: Add to `tests/` with appropriate subdirectory

2. **Follow naming conventions:**
   - Use `snake_case` for Python files
   - Use `PascalCase` for class names
   - Use `UPPER_CASE` for constants
   - Prefix test files with `test_`

3. **Update documentation:**
   - Add docstrings to all public functions/classes
   - Update this README if adding new major components
   - Update API documentation in `docs/api/`

#### Code Quality Standards

- **Type Hints**: Use type annotations for all function parameters and return values
- **Documentation**: Include comprehensive docstrings following Google style
- **Testing**: Write unit tests for all new functionality
- **Linting**: Follow PEP 8 style guidelines
- **Imports**: Use absolute imports within the project

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/unit/test_processors.py

# Run with coverage
pytest --cov=src --cov-report=html
```

### Development Scripts

- `scripts/setup.py`: Development environment setup
- `scripts/migrate.py`: Database/data migration utilities
- `scripts/deploy.py`: Production deployment helpers

## 📊 Business Rules

The application follows comprehensive business rules defined in the `business_rules/` directory:

- **[PDF000]**: PDF Format Score Calculator - Evaluates document quality
- **[PDF001]**: Title Block Parser - Extracts structured data from engineering drawings
- **[PDF002]**: Outside Process Parser - Identifies finishing and outsourcing requirements
- **[QBX003]**: Summary View - Defines exact quote summary layout

## 🐳 Deployment

### Docker Deployment

```bash
# Build and run with Docker Compose
cd docker
docker-compose up -d
```

### Cloud Deployment

The application is configured for deployment on Render with the included `render.yaml` configuration.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Make your changes following the project structure guidelines
4. Add tests for new functionality
5. Ensure all tests pass: `pytest`
6. Submit a pull request

## 📝 License

This project is proprietary software. See LICENSE file for details.

## 🆘 Support

For support and questions:
- Check the `docs/` directory for detailed documentation
- Review existing issues on GitHub
- Create a new issue for bugs or feature requests

## 🔄 Version History

- **v1.0.0**: Initial release with core file processing capabilities
- **v1.1.0**: Added OCR integration and business rule engine
- **v1.2.0**: Enhanced UI with responsive design and improved user experience
- **v1.3.0**: Added comprehensive testing suite and CI/CD pipeline