# To Do - Release 0.1a

## Items Ready for Work



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



### 21. Create Comprehensive Test Suite
**Priority:** Medium  
**Description:** Develop a comprehensive test suite including unit tests, integration tests, and API tests. The test suite should cover all major functionality including database operations, API endpoints, authentication, and web pages. Include proper test fixtures, mocking, and database setup for reliable testing. This will ensure code quality and prevent regressions during development.

### 22. Optimize CSS for Production
**Priority:** Medium  
**Description:** Replace Tailwind CSS CDN with a proper build system. Set up PostCSS and Tailwind CLI to generate optimized CSS that only includes used classes. This will improve performance, reduce bundle size, and eliminate dependency on external CDN. Consider using tools like Vite or Webpack for asset bundling and optimization.

---

**Next Work Item Number:** 23

