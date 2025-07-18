# To Do - Release 0.1a

## Items Ready for Work

### 23. Optimize Data Import Workflow for Production
**Priority:** HIGH  
**Description:** Completely rework the data import process to eliminate the need for storing raw lotro-companion repos in the deployed environment. The solution should:
- Import data during build time (Docker build process)
- Clone repos temporarily during build
- Run import scripts to process XML data into database
- Copy only needed icons to static folder
- Remove raw repos after processing
- Retain ability to automatically deploy new data when lotro-companion repos update
- Consider implementing as part of CI/CD pipeline or build-time process
- Target for 0.2a release

### 5. Set Up CI/CD Pipeline
**Priority:** High  
**Description:** Implement automated deployment using GitHub Actions with testing, environment variables, and deployment workflow for the main branch.

### 6. Improve Branch Management Strategy
**Priority:** Medium  
**Description:** Change development workflow to use main branch for releases and separate development branch for ongoing work.

### 7. Automate Data Import Monitoring
**Priority:** Medium  
**Description:** Implement monitoring of lotro-companion GitHub repository and potentially automate importer scripts when specific data changes are detected.

### 8. Replace Static API Documentation
**Priority:** Medium  
**Description:** Replace current static API documentation with interactive Swagger UI to improve API exploration and testing experience.

### 17. Set Up Icon Sprite System
**Priority:** Medium  
**Description:** Implement image importing system to stitch all individual icons together into one large PNG sprite sheet. Use CSS sprite techniques or other methods to extract and display specific icons from the larger image. This will reduce HTTP requests and improve page load performance by loading all icons in a single request.

### 19. Track Down Crit Defence Calculation on Shields
**Priority:** Medium  
**Description:** Investigate and document how critical defence is calculated on shields. This may involve special formulas or modifiers that differ from standard equipment stat calculations. Research the game mechanics and data structures to understand shield-specific crit defence behavior.

### 10. Fix EV Display in Item Database
**Priority:** Low  
**Description:** Change Essence Value (EV) display in item databases to show global values rather than relative to currently loaded results only.

### 14. Add Timeline Connections to Release Notes
**Priority:** Low  
**Description:** Implement visual timeline connections between release notes on the release notes page. Should show connecting lines only in the spaces between releases, not through the release content itself.

### 15. Optimize API Call Performance
**Priority:** Low  
**Description:** Investigate and optimize API call performance, specifically addressing scenarios where multiple calls are made to the same endpoint during page loads. Consider implementing request deduplication, caching strategies, or batching mechanisms to reduce redundant API calls and improve page load times.

### 16. Fix Essence Icon Display Alignment
**Priority:** Low  
**Description:** Essence icons in the database panel are displaying slightly off-center. Adjust CSS positioning/alignment to center the icons properly within their containers.

### 18. Add Global Tracking for Equipment Values
**Priority:** Low  
**Description:** Implement global tracking system for data values such as maxIlvl, minIlvl, and other statistical ranges. This would provide centralized management of these values across the application, making it easier to maintain consistency and update limits when needed.

### 20. Audit Data Model Structure Consistency
**Priority:** Medium  
**Description:** Conduct a comprehensive audit of data models as they are passed through the application to ensure consistency across all endpoints and services. Review the structure of JSON responses, database model serialization methods (to_json, to_list_json, get_stats_json), and API response formats. Focus on standardizing field names, data types, nested object structures, and response patterns across items, equipment, essences, and other data models. This audit should identify inconsistencies in how data is structured and formatted as it flows through different layers of the application.

### 21. Create Comprehensive Test Suite
**Priority:** Medium  
**Description:** Develop a comprehensive test suite including unit tests, integration tests, and API tests. The test suite should cover all major functionality including database operations, API endpoints, authentication, and web pages. Include proper test fixtures, mocking, and database setup for reliable testing. This will ensure code quality and prevent regressions during development.

### 22. Optimize CSS for Production
**Priority:** Medium  
**Description:** Replace Tailwind CSS CDN with a proper build system. Set up PostCSS and Tailwind CLI to generate optimized CSS that only includes used classes. This will improve performance, reduce bundle size, and eliminate dependency on external CDN. Consider using tools like Vite or Webpack for asset bundling and optimization.

---

**Next Work Item Number:** 23

