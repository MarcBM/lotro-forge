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

## Database Setup

This project uses PostgreSQL as its database. Follow these steps to set up the database:

1. Install PostgreSQL:
   ```bash
   sudo apt update
   sudo apt install postgresql postgresql-contrib
   ```

2. Start the PostgreSQL service:
   ```bash
   sudo service postgresql start
   ```

3. Create the database and user:
   ```bash
   # Switch to postgres user
   sudo -u postgres psql

   # In the PostgreSQL prompt, create database and user:
   CREATE DATABASE lotro_forge;
   CREATE USER your_username WITH ENCRYPTED PASSWORD 'your_password';
   GRANT ALL PRIVILEGES ON DATABASE lotro_forge TO your_username;
   \q
   ```

4. Verify the installation:
   ```bash
   psql -d lotro_forge -U your_username
   ```

Note: Replace `your_username` and `your_password` with your preferred database credentials. Make sure to keep these credentials secure and never commit them to version control.

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
