# Release Notes Templates

This directory contains blueprint templates for different types of releases in LOTRO Forge. These templates provide a consistent structure and formatting for release notes.

## Template Types

### Major Release Template (`major_release_template.html`)
Used for major version releases (X.0.0) that introduce significant new features or platform changes.

**Structure:**
- Version header with gradient styling and "MAJOR RELEASE" badge
- Release date
- Detailed release summary paragraph
- Release notes sections:
  - New Content
  - Changes
  - Bug Fixes

**Styling:** Enhanced with gradient backgrounds and larger fonts to emphasize importance.

### Feature Release Template (`feature_release_template.html`)
Used for feature releases (1.X.0) that add new functionality or significant improvements.

**Structure:**
- Version header with standard styling and "FEATURE RELEASE" badge
- Release date
- Release summary paragraph
- Release notes sections:
  - New Content
  - Changes
  - Bug Fixes

**Styling:** Clean, professional styling without excessive visual emphasis.

### Minor Release Template (`minor_release_template.html`)
Used for minor releases (1.3.X) that primarily contain bug fixes and small improvements.

**Structure:**
- Compact version header with "HOTFIX" badge
- Release date
- Release notes sections only:
  - Changes
  - Bug Fixes

**Styling:** Minimal, compact design appropriate for smaller releases.

## Using the Templates

1. Copy the appropriate template file
2. Replace all placeholder text in brackets `[PLACEHOLDER]`
3. Fill in the relevant sections with actual release content
4. Save with appropriate filename (e.g., `v1_2_0.html`)

## Placeholder Reference

### Common Placeholders
- `[VERSION]` - Version number (e.g., "1.2.0")
- `[RELEASE NAME]` - Descriptive name for the release
- `[RELEASE DATE]` - Release date in format "Released on Month DD, YYYY"

### Content Placeholders
- `[DETAILED RELEASE SUMMARY]` - Comprehensive paragraph describing the release
- `[RELEASE SUMMARY]` - Brief summary for feature releases
- `[New feature or content description]` - Individual new content items
- `[Change description]` - Individual changes
- `[Bug fix description]` - Individual bug fixes

## Styling Guidelines

- Use bullet points (•) for list items
- Keep content concise and user-focused
- Maintain consistency with the LOTRO Forge design system
- No emojis or excessive icons
- Focus on clear, informative content over visual elements 