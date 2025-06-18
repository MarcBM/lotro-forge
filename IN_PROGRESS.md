# In Progress - Release 0.1a

## Currently Active Items

### 1. Refactor Page JavaScript
**Priority:** High  
**Description:** Move inline JavaScript from templates to separate .js files for better code organization and maintainability.

**Current Status:** Navigation, authentication, and notification systems have been successfully refactored with proper separation of concerns. JavaScript file structure has been optimized and consolidated. Fixed the navbar authentication display issue using a reactive component-based approach: authentication component maintains global state (`window.lotroAuth`) and dispatches custom events (`auth-state-changed`) when state changes; navigation component listens for these events and updates its reactive properties accordingly. The auth-section template uses clean, no-inline-JS references to navigation component properties. Authentication section properly shows logged-in user dropdown when authenticated and Sign-In button when not authenticated. Reorganized release notes access by removing from main navigation and adding to home page and footer with version number link. Created centralized icon system using Jinja2 macros to replace inline SVG paths with readable icon references (e.g., `{{ icon("user") }}`).

**Next Steps:** Conduct a full frontend audit to identify and refactor any remaining inline JavaScript throughout the application templates. Consider extending the icon system to other templates with SVG icons.

### 12. Make Footer/Navigation Float
**Priority:** Low  
**Description:** Implement floating footer and navigation elements for improved user interface experience.

**Current Status:** Initial implementation completed. Implemented proper sticky footer layout using flexbox with `flex-col min-h-screen` on the authentication wrapper div and `mt-auto` on the footer component. Fixed builder page layout conflicts to work with the new footer system. However, testing on the release notes page revealed that both footer and navbar are not currently floating - they should always be visible with the rest of the page existing in a scrollable viewport.

**Next Steps:** Fix the floating implementation so navbar and footer are always visible, with page content scrollable between them. Test on release notes page and other page types to ensure proper behavior across all scenarios.

### 13. Add Release Notes Display to Website
**Priority:** High  
**Description:** Create a public-facing page on the website to display release notes history, showing current release goals and completed milestones. This provides transparency to testers about development progress and upcoming features. Update the RELEASE_WORKFLOW documentation to make sure that release notes are added to the web page on completion of each release.

**Current Status:** Core implementation completed with comprehensive template system. Created main release notes page with two-column layout (fixed left sidebar for roadmap, scrollable right column for timeline), roadmap template, and three release template types (major, standard, minor) with proper visual hierarchy. Added navigation integration and example releases. However, release notes timeline needs UI refinement and roadmap needs editing to fit properly on 1080p monitors.

**Next Steps:** Refine release notes timeline UI design and optimize roadmap content/layout to fit within 1080p screen constraints. Create polished examples for each release tier (major, standard, minor) that can be easily copied as templates for future releases. Update RELEASE_WORKFLOW documentation to include web page update process.

---

**Note:** When moving items here from TODO.md, update the description to include current status and next steps. 