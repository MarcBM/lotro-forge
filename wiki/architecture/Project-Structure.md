# Project Structure

This document outlines the organization of the LOTRO Forge codebase.

## Directory Layout

```
lotro_forge/
├── lotro_forge/
│   ├── models/
│   │   ├── __init__.py
│   │   ├── item.py
│   │   └── stat.py
│   ├── parsers/
│   │   ├── __init__.py
│   │   └── item_parser.py
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── conftest.py
│   │   └── test_item_parser.py
│   ├── wiki/
│   │   ├── models/
│   │   ├── parsers/
│   │   ├── testing/
│   │   ├── architecture/
│   │   └── Home.md
│   └── __init__.py
├── scripts/
│   └── setup_dev.sh
├── .github/
│   └── workflows/
│       └── test.yml
├── .gitignore
├── DEVELOPMENT.md
├── README.md
├── RULES.md
├── pytest.ini
├── requirements.txt
└── setup.py
```

## Component Overview

### Core Modules

#### `models/`
- Data structures and business logic
- Item and stat definitions
- Type definitions and validation

#### `parsers/`
- XML parsing implementation
- Data conversion logic
- Validation and error handling

### Documentation

#### `wiki/`
- Project documentation
- Design decisions
- Implementation details
- Development guides

### Development

#### `scripts/`
- Development setup scripts
- Utility scripts
- Build tools

#### `.github/`
- CI/CD configuration
- GitHub Actions workflows
- Issue templates

### Configuration

#### Root Files
- `setup.py`: Package configuration
- `requirements.txt`: Dependencies
- `pytest.ini`: Test configuration
- `.gitignore`: Git ignore rules

## Module Details

### Models Module

#### Purpose
- Define data structures
- Implement business logic
- Handle validation

#### Key Files
- `item.py`: Item definitions
- `stat.py`: Stat handling

### Parsers Module

#### Purpose
- Parse XML data
- Convert to models
- Validate input

#### Key Files
- `item_parser.py`: Item parsing

### Tests Module

#### Purpose
- Unit tests
- Integration tests
- Test fixtures

#### Key Files
- `conftest.py`: Test configuration
- `test_*.py`: Test suites

## Development Workflow

### Setup
1. Clone repository
2. Run setup script
3. Install dependencies
4. Verify installation

### Development
1. Create feature branch
2. Implement changes
3. Write tests
4. Update documentation
5. Submit PR

### Testing
1. Run test suite
2. Check coverage
3. Verify CI/CD
4. Review results

## Future Structure

### Planned Additions
- `api/`: API endpoints
- `cli/`: Command-line interface
- `web/`: Web interface
- `plugins/`: Extension system

### Considerations
- Scalability
- Maintainability
- Extensibility
- Performance 