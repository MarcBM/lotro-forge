# In Progress - Release 0.1a

## Currently Active Items

### 1. Refactor Page JavaScript
**Priority:** High  
**Description:** Move inline JavaScript from templates to separate .js files for better code organization and maintainability.

**Current Status:** Navigation, authentication, and notification systems have been successfully refactored with proper separation of concerns. JavaScript file structure has been optimized and consolidated.

**Next Steps:** Conduct a full frontend audit to identify and refactor any remaining inline JavaScript throughout the application templates.

### 12. Make Footer/Navigation Float
**Priority:** Low  
**Description:** Implement floating footer and navigation elements for improved user interface experience.

**Current Status:** Initial implementation completed. Implemented proper sticky footer layout using flexbox with `flex-col min-h-screen` on the authentication wrapper div and `mt-auto` on the footer component. Fixed builder page layout conflicts to work with the new footer system.

**Next Steps:** Requires testing across different page types and screen sizes to ensure the footer behaves correctly in all scenarios before marking as complete.

---

**Note:** When moving items here from TODO.md, update the description to include current status and next steps. 