# LOTRO Forge

A tool for working with LOTRO item data and stat calculations.

## Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/MarcBM/lotro_forge.git
   cd lotro_forge
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Development

- Always work within the virtual environment (activate it using `source venv/bin/activate`)
- Install new dependencies with `pip install <package-name>` and update requirements.txt with `pip freeze > requirements.txt`
- The main code is in the `models/` and `parsers/` directories
- See `RULES.md` for important project rules and terminology

## Project Structure

```
lotro_forge/
├── models/          # Data models for items and stats
├── parsers/         # XML parsers for game data
├── scripts/         # Utility scripts
├── .gitignore      # Git ignore rules
├── README.md       # This file
├── RULES.md        # Project rules and terminology
└── requirements.txt # Project dependencies
```
