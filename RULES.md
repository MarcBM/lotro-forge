# LOTRO Forge Project Rules and Guidelines

## Data Processing Rules

### Import vs Runtime Processing
1. Data Import (scripts/import/)
   - Used for one-time or rare database operations
   - Imports data from lotro_companion into our database
   - Run manually or during deployment
   - Examples: initial setup, game updates, data fixes
   - Must follow the import framework architecture
   - Must include validation and error handling
   - Must use transactions for database operations

2. Runtime Parsing (parsers/)
   - Used during application runtime
   - Processes game data for immediate use
   - Converts XML/raw data into domain objects
   - Examples: item stats, character data, UI updates
   - Must be efficient and lightweight
   - Should cache results when appropriate
   - Should handle errors gracefully

### Source Data Rules
1. XML data files (e.g., `items.xml`) are source data files and should be treated as read-only
   - These files contain the original game data
   - Do not modify these files directly
   - Any changes to item data should be handled through the application's data structures
   - The application should parse and use these files, not modify them

### Code Quality Rules
1. Parser Maintenance
   - Any changes to parser files (e.g., `*_parser.py`) must be accompanied by:
     - Updated documentation (docstrings, comments)
     - Updated or new test cases
     - Example usage if the change affects the public API
   - Test coverage should include:
     - Happy path (valid data)
     - Error cases (invalid data, missing attributes)
     - Edge cases (empty files, malformed input)
   - Documentation should clearly explain:
     - What the parser does
     - How to use it
     - What errors to expect
     - Any assumptions or limitations
   - This rule applies to all parsers in the project, including but not limited to:
     - Item parsers
     - Stat scaling parsers
     - Value table parsers
     - Any future parsers added to the project

2. Importer Maintenance
   - Any changes to importer files must be accompanied by:
     - Updated documentation in scripts/import/README.md
     - Test cases for the import process
     - Validation of data integrity
   - Importers must:
     - Use transactions for database operations
     - Include proper error handling
     - Log all operations
     - Validate source data
   - This rule applies to all importers in the project

### Terminology
- Use `ilvl` (item level) to refer to an item's level, not "level"
- Use `required_player_level` to refer to the minimum player level needed to equip an item
- Distinguish between "primitive" item definitions (from XML) and "instantiated" items (as they exist in-game)

### Item Definition vs Instantiated Item
1. **ItemDefinition** (Primitive Form):
   - Represents the base definition of an item as it exists in XML data
   - Contains scaling references for stats, not concrete values
   - Has a `min_ilvl` (baseline item level)
   - Stats are stored as `ItemStat` objects with scaling references

2. **Item** (Instantiated Form):
   - Represents an item as it exists in-game
   - Has a specific `ilvl` that is fixed once acquired
   - Contains concrete stat values, not scaling references
   - Stats are stored as `ConcreteStat` objects with actual values

### Stat Handling
- Items in their primitive form (ItemDefinition) contain stat scaling references
- Once instantiated (Item), items have concrete stat values
- Stats do not change after an item is acquired (they are static)
- Stat values are calculated based on the item's ilvl when instantiated

### Item Level (ilvl) Rules
- Items have a baseline ilvl (`min_ilvl`)
- Items can drop at higher ilvls based on content difficulty
- Once an item is acquired, its ilvl is fixed
- The ilvl determines the concrete stat values

### Player Level Rules
- Items have a `required_player_level` that determines when they can be equipped
- This is separate from and independent of the item's ilvl
- Player level requirements are static and don't change

### Data Structure Guidelines
1. Use clear, descriptive names that distinguish between:
   - Item level concepts (ilvl, min_ilvl)
   - Player level concepts (required_player_level)
   - Stat scaling references (ItemStat)
   - Concrete stat values (ConcreteStat)

2. Maintain separation between:
   - Primitive item definitions (ItemDefinition)
   - Instantiated items (Item)
   - Stat scaling references
   - Concrete stat values

### Implementation Notes
- Stat scaling calculations are currently placeholder implementations
- XML parsing for item definitions is to be implemented
- Validation should be performed when instantiating items
- Dictionary representations should use consistent terminology

### Future Considerations
- Need to implement proper stat scaling calculations
- Need to implement XML parsing for item definitions
- May need to add validation for stat values
- May need to add methods for comparing items at different ilvls

## Project Structure
- Item-related code is located in `lotro_forge/models/item.py`
- Item definitions are stored in XML format
- The project uses Python dataclasses for data structures

## Development Guidelines
1. Maintain clear separation between primitive and instantiated forms
2. Use consistent terminology throughout the codebase
3. Document decisions and rules in code comments
4. Keep related work in the same chat session when possible
5. When starting new chats, reference this file for context

## Terminal Commands and Database
1. Terminal Commands
   - All terminal commands should be run by the user in their virtual environment
   - The assistant will provide the commands but not execute them
   - This ensures commands are run in the correct context and environment
   - Example commands will be shown in code blocks with explanations

2. Database Migrations
   - Use Alembic for database migrations
   - Migration files should be created in the `migrations` directory
   - Each migration should have a clear, descriptive name
   - Migrations should be reversible when possible
   - Test migrations both up and down before committing
   - Keep migrations focused and atomic (one logical change per migration)

3. Database Setup Steps
   - Database configuration is stored in `.env` file
   - Never commit `.env` file to version control
   - Use `alembic upgrade head` to apply migrations
   - Use `alembic downgrade -1` to rollback migrations
   - Always run migrations in the virtual environment 