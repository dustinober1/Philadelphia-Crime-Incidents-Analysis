# Roadmap: Crime Incidents Philadelphia

## Milestones

- ✅ **v1.0 Local Containerized Dev** — Phases 1-3 shipped February 7, 2026. Full archive: `.planning/milestones/v1.0-ROADMAP.md`
- ✅ **v1.1 Local Workflow Enhancements** — Phases 4-6 shipped February 7, 2026. Full archive: `.planning/milestones/v1.1-ROADMAP.md`
- 🔄 **v1.2 Deferred Workflow Enhancements** — Phases 7-9 shipping February 8, 2026. Full archive: `.planning/milestones/v1.2-ROADMAP.md`

## Current Milestone: v1.2 Deferred Workflow Enhancements

### Phase 7: Machine-Readable Output for Automation (LWF-03)
**Goal:** Enable seamless integration with CI/CD systems and automation tools.

**Success Criteria:**
- Developer can run smoke-check validation with JSON-formatted output for CI parsing
- System outputs structured status reports in JSON/YAML format
- Validation script provides exit codes that reflect validation outcomes
- Machine-readable output includes timing information for performance monitoring

**Requirements Mapped:**
- LWF-03-1: Developer can run smoke-check validation with JSON-formatted output for CI parsing
- LWF-03-2: System outputs structured status reports in JSON/YAML format
- LWF-03-3: Validation script provides exit codes that reflect validation outcomes
- LWF-03-4: Machine-readable output includes timing information for performance monitoring

**Research Flags:** None

### Phase 8: Additional API Endpoint Validation (LWF-04)
**Goal:** Enhance validation beyond basic health checks to verify critical functionality.

**Success Criteria:**
- Extended smoke checks validate specific high-value API endpoints
- Crime dataset endpoints return expected data structures
- API validation includes response time thresholds for performance verification
- Extended validation includes data integrity checks for recently processed datasets

**Requirements Mapped:**
- LWF-04-1: Developer can run extended smoke checks that validate specific high-value API endpoints
- LWF-04-2: System validates crime dataset endpoints return expected data structures
- LWF-04-3: API validation includes response time thresholds for performance verification
- LWF-04-4: Extended validation includes data integrity checks for recently processed datasets

**Research Flags:** None

### Phase 9: Host Resource Detection and Smart Presets (LWF-05)
**Goal:** Automatically optimize runtime configuration based on available system resources.

**Success Criteria:**
- System detects available CPU cores and RAM before startup
- Runtime presets automatically adjust based on detected resources
- Developer receives preset recommendations based on available resources
- Resource detection works across common development platforms (Linux, macOS, Windows WSL)

**Requirements Mapped:**
- LWF-05-1: System detects available CPU cores and RAM before startup
- LWF-05-2: Runtime presets automatically adjust based on detected resources
- LWF-05-3: Developer receives preset recommendations based on available resources
- LWF-05-4: Resource detection works across common development platforms (Linux, macOS, Windows WSL)

**Research Flags:** None

## Future Milestones

### v2 Scope (Deferred)
- Advanced metrics export in Prometheus format for monitoring systems
- Real-time event streaming for long-running operations
- Full API contract validation against OpenAPI specification
- Historical data validation across multiple time periods
- Dynamic resource adjustment during runtime
- Machine learning-based optimization for workload patterns

---
*Milestone v1.2 roadmap created: February 7, 2026*