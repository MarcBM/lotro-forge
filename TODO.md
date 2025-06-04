## High Priority (Beta Launch)
- 🚧 **Implement basic authentication system**
-   ✅ Create user account management (User and UserSession models implemented)
-   ✅ Set up login/logout functionality (Complete with modal UI and session management)
-   ❌ Implement access control (logged-in users only)
-     - ❌ Protect builder routes with authentication
-     - ❌ Protect database routes with authentication  
-     - ❌ Redirect unauthenticated users appropriately
-   ✅ Create admin interface for managing beta tester accounts (Admin-only user creation endpoint)
-   ✅ Create master user account (Vuldyn admin account created)
-   ❌ **Account management frontend needed:**
-     - ❌ User profile/account settings page
-     - ❌ Password change functionality
-     - ❌ Account information display and editing
-     - ❌ User dashboard or settings interface
-   📋 **Authentication features completed:**
-     - Session-based authentication with secure cookies
-     - Password hashing with bcrypt
-     - User roles (USER, BETA_TESTER, ADMIN)
-     - Login/logout modal UI with visual feedback
-     - Authentication status checking and display
-     - Success/error notifications for login/logout
- Deploy website to lotroforge.com domain
  - Research and implement hosting solution
  - Set up domain configuration
  - Configure SSL certificates
  - Ensure proper security measures
- Set up CI/CD pipeline
  - Configure GitHub Actions for automated deployment
  - Set up deployment workflow for main branch
  - Implement automated testing before deployment
  - Configure environment variables and secrets

## Medium Priority (Post-Beta Launch)
- Change branch management to do development off the main branch, use the main branch for releases
- Implement a way to watch the lotro-companion github and perhaps automate importer scripts to run following a change to specific places
- Replace static API documentation with interactive Swagger UI for better API exploration and testing

## Low Priority (UI/UX Improvements)
- Fix display of the builder to look roughly the same on larger screens
- Fix EV display on item DBs to be global, not relative to only currently loaded results
- Remove left/right slot filters from equipment database explorer to simplify slot selection