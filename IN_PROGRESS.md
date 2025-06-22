# In Progress - Release 0.1a

## Currently Active Items

### 1. Refactor Page JavaScript
**Priority:** High  
**Description:** Move inline JavaScript from templates to separate .js files for better code organization and maintainability.

**Current Status:** Navigation, authentication, and notification systems have been successfully refactored with proper separation of concerns. JavaScript file structure has been optimized and consolidated. Fixed the navbar authentication display issue using a reactive component-based approach: authentication component maintains global state (`window.lotroAuth`) and dispatches custom events (`auth-state-changed`) when state changes; navigation component listens for these events and updates its reactive properties accordingly. The auth-section template uses clean, no-inline-JS references to navigation component properties. Authentication section properly shows logged-in user dropdown when authenticated and Sign-In button when not authenticated. Reorganized release notes access by removing from main navigation and adding to home page and footer with version number link. Created centralized icon system using Jinja2 macros to replace inline SVG paths with readable icon references (e.g., `{{ icon("user") }}`).

**Next Steps:** Conduct a full frontend audit to identify and refactor any remaining inline JavaScript throughout the application templates. Consider extending the icon system to other templates with SVG icons.

---

**Note:** When moving items here from TODO.md, update the description to include current status and next steps. 