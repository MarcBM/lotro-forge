# In Progress - Release 0.1a

## Currently Active Items

### 4. Deploy Website to lotroforge.com
**Priority:** High  
**Description:** Set up production hosting for the website including domain configuration, SSL certificates, and security measures. Research and implement appropriate hosting solution.

**Current Status:** Researching hosting options. fly.io is currently being treated as the best hosting option due to its developer-friendly deployment process, global edge network, and cost-effective pricing for small applications.

**Next Steps:** 
- Complete fly.io evaluation and setup
- Configure domain and SSL certificates
- Implement security measures
- Deploy initial alpha version

### 23. Optimize Data Import Workflow for Production
**Priority:** HIGH  
**Description:** Completely rework the data import process to eliminate the need for storing raw lotro-companion repos in the deployed environment.

**Current Status:** Planning phase - See DATA_PROCESSING_PLAN.md for comprehensive implementation plan.

**Next Steps:**
- Implement data curation system (Phase 1)
- Create sprite sheet generation (Phase 2)
- Refactor import system for curated data (Phase 3)
- Update templates for sprite usage (Phase 4)
- Modify deployment process (Phase 5)
- Create update workflow (Phase 6)

### 17. Set Up Icon Sprite System
**Priority:** Medium  
**Description:** Implement image importing system to stitch all individual icons together into one large PNG sprite sheet. Use CSS sprite techniques or other methods to extract and display specific icons from the larger image.

**Current Status:** Integrated into DATA_PROCESSING_PLAN.md as Phase 2 - Sprite Sheet System.

**Next Steps:**
- Implement sprite generation script
- Create CSS positioning system
- Update templates to use sprites
- Test performance improvements

---

**Note:** When moving items here from TODO.md, update the description to include current status and next steps. 