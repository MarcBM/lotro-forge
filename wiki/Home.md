# LOTRO Forge Documentation

Welcome to the LOTRO Forge documentation! This documentation covers the design decisions, implementation details, and technical specifications of the LOTRO Forge project.

## Core Systems

### Models
- [Item System](models/Item-System.md) - Design and implementation of the item data structures
  - [Item Definition](models/Item-Definition.md) - Details about the primitive form of items
  - [Item Instantiation](models/Item-Instantiation.md) - How items are instantiated with concrete values
  - [Stat System](models/Stat-System.md) - Stat handling and scaling

### Parsers
- [XML Parsing](parsers/XML-Parsing.md) - XML data handling and parsing strategies
  - [Item Parser](parsers/Item-Parser.md) - Implementation details of item parsing
  - [Validation](parsers/Validation.md) - Data validation strategies

## Development

### Setup and Tools
- [Development Guide](../DEVELOPMENT.md) - Setup and development instructions
- [Project Rules](../RULES.md) - Project guidelines and rules
- [Testing](testing/Testing-Guide.md) - Testing strategies and guidelines

### Architecture
- [Design Philosophy](architecture/Design-Philosophy.md) - Core design principles
- [Project Structure](architecture/Project-Structure.md) - Codebase organization

## Project Overview

LOTRO Forge is a tool designed to work with LOTRO item data, providing a robust and maintainable way to:
- Parse and validate item definitions from XML
- Handle item scaling and stat calculations
- Manage item instantiation with concrete values
- Support future extensions and features

## Quick Links

- [Development Setup](../DEVELOPMENT.md)
- [Project Rules](../RULES.md)
- [GitHub Repository](https://github.com/MarcBM/lotro_forge)
- [Issue Tracker](https://github.com/MarcBM/lotro_forge/issues) 