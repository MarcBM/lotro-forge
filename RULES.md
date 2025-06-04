# 🤖 AI Code Assistant Guidelines

This document outlines the rules and guidelines for AI code assistants working on the LOTRO Forge project. It defines what you should and shouldn't do when helping with development.

## Core Principles

1. **Data Integrity**
   - Never modify source XML files from `lotro_companion`
   - Treat game data as immutable source of truth
   - Maintain clear separation between source data and application data
   - Use proper validation and error handling

2. **Code Organization**
   - Follow the established project structure
   - Keep related code in appropriate directories
   - Use consistent naming conventions
   - Document code changes clearly

3. **Development Workflow**
   - Work within the virtual environment
   - Provide commands but don't execute them
   - Suggest changes but don't make them directly
   - Wait for user approval before applying changes

## Project-Specific Rules

### Data Processing

1. **Import Framework**
   - All data import is handled through `scripts/importers/`
   - Each importer inherits from `BaseImporter`
   - Importers follow a four-step process:
     1. Validate source data
     2. Parse XML into intermediate format
     3. Transform into database models
     4. Import into database
   - Importers handle their own dependencies
   - Import process is transactional and logged
   - Source data is treated as read-only

2. **Item Data**
   - Use `ilvl` for item level (not "level")
   - Use `required_player_level` for player requirements
   - Distinguish between primitive (XML) and instantiated (in-game) items
   - Maintain stat scaling references in primitive form
   - Use concrete values only in instantiated form

3. **Database Operations**
   - Use transactions for all database operations
   - Include proper error handling
   - Log all operations
   - Validate data before import

### Code Style

1. **Python Code**
   - Use type hints for all function parameters and returns
   - Follow PEP 8 style guide
   - Use descriptive variable names
   - Include docstrings for all public functions

2. **Documentation**
   - Update relevant docs when making changes
   - Keep documentation in sync with code
   - Use clear, concise language
   - Include examples where helpful

3. **Testing**
   - Write tests for new functionality
   - Update tests when modifying existing code
   - Include both happy path and error cases
   - Test edge cases and data validation

### What Not to Do

1. **Never**
   - Modify source XML files
   - Execute commands directly
   - Make assumptions about data formats
   - Skip validation steps
   - Ignore error handling
   - Commit sensitive data

2. **Avoid**
   - Hardcoding values
   - Duplicating code
   - Making undocumented changes
   - Skipping tests
   - Using unclear variable names

## Communication Guidelines

1. **When Suggesting Changes**
   - Explain the reasoning
   - Show the proposed changes
   - Wait for approval
   - Apply changes only after confirmation

2. **When Providing Commands**
   - Show commands in code blocks
   - Explain what each command does
   - Note any prerequisites
   - Include expected output

3. **When Documenting**
   - Use clear, professional language
   - Include context and examples
   - Update all affected documentation
   - Keep documentation organized

## Project Context

- This is a LOTRO game data tool
- Data comes from `lotro_companion` repository
- Focus on data accuracy and performance
- Maintain clear separation of concerns
- Follow established patterns and conventions

## Related Documentation

- [Setup Guide](docs/setup.md) - Environment setup
- [Development Guide](docs/development.md) - Development workflow
- [Data Transformation Guide](docs/data-transformation.md) - Import process
- [Project Structure](docs/structure.md) - Code organization