# LOTRO Forge

> A comprehensive web application for LOTRO (Lord of the Rings Online) item data analysis, stat calculations, and character build planning.

![Tests](https://img.shields.io/badge/tests-passing-brightgreen)
![Python](https://img.shields.io/badge/python-3.12+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green)
![SQLite](https://img.shields.io/badge/SQLite-supported-blue)

## 🚀 Quick Start

1. **Clone and setup:**
   ```bash
   git clone https://github.com/MarcBM/lotro_forge.git
   cd lotro_forge
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Setup database and import data:**
   ```bash
   # See docs/setup.md for detailed database setup
   python -m scripts.importers.run_import --wipe
   ```

3. **Start the server:**
   ```bash
   python -m scripts.run_web
   # Visit: http://localhost:8000
   ```

## 📚 Documentation

- **[📋 Setup Guide](docs/setup.md)** - Installation, database setup, and configuration
- **[🛠️ Development Guide](docs/development.md)** - Development workflow, testing, and code quality
- **[🌐 API Documentation](docs/api.md)** - API endpoints, examples, and usage
- **[📊 Data Transformation](docs/data-transformation.md)** - XML to database import process and data quirks

## 🔧 Key Commands

```bash
# Development
python -m scripts.run_web              # Start web server
python scripts/run_tests.py unit       # Run tests
python -m scripts.importers.run_import # Import LOTRO data

# Testing
python scripts/run_tests.py unit --coverage  # With coverage
python -m pytest tests/unit/ -v              # Unit tests only

# Code Quality  
black .                                 # Format code
ruff check .                           # Lint code
```

## 🏗️ Tech Stack

- **Backend**: Python 3.12+, FastAPI, SQLAlchemy
- **Database**: SQLite with Alembic migrations
- **Frontend**: Jinja2 templates, vanilla JavaScript
- **Testing**: pytest with comprehensive test suite
- **Data**: LOTRO XML game data import system

## 🎮 About

LOTRO Forge is a web companion to LOTRO which helps players find the best possible character build for their situation. It uses official game data, provides accurate stat calculations, and employs a powerful build valuation technique to make sure you are getting the most out of your build choices.

**Disclaimer:** This project is not affiliated with or endorsed by Standing Stone Games or Middle-earth Enterprises.

---

**Need help?** Check the [documentation](docs/) or [open an issue](https://github.com/MarcBM/lotro_forge/issues).