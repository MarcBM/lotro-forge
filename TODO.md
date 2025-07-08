# To Do - Release 0.1a

## Items Ready for Work


### 2. Refactor Navigation Template
**Priority:** High  
**Description:** Clean up and improve the navigation template structure for better consistency across pages.

### 3. Refactor Templates Directory Structure
**Priority:** High  
**Description:** Reorganize templates directory, particularly moving baseline components into the builder section for better organization.

### 4. Deploy Website to lotroforge.com
**Priority:** High  
**Description:** Set up production hosting for the website including domain configuration, SSL certificates, and security measures. Research and implement appropriate hosting solution.

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

### 9. Fix Builder Display on Large Screens
**Priority:** Low  
**Description:** Ensure the character builder interface displays consistently and properly on larger screen sizes.

### 10. Fix EV Display in Item Database
**Priority:** Low  
**Description:** Change Essence Value (EV) display in item databases to show global values rather than relative to currently loaded results only.

### 11. Simplify Equipment Database Filters
**Priority:** Low  
**Description:** Remove left/right slot filters from equipment database explorer to streamline slot selection process.

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

---

**Next Work Item Number:** 20

