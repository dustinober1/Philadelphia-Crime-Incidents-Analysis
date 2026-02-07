# Requirements: Crime Incidents Philadelphia v1.2

## Milestone Overview

**Version:** v1.2  
**Name:** Deferred Workflow Enhancements  
**Goal:** Address deferred workflow enhancements (LWF-03 to LWF-05) to further improve local development experience and system capabilities.

## Core Value

One `docker compose up` command reliably brings up the complete stack locally with small, resource-constrained containers, enhanced with improved development workflow tools.

## Requirements Categories

### LWF-03: Machine-Readable Output for Automation

**Category Goal:** Enable seamless integration with CI/CD systems and automation tools.

#### v1.2 Requirements (Must Have)

- [ ] Developer can run smoke-check validation with JSON-formatted output for CI parsing — Enable machine-readable validation results for automation
- [ ] System outputs structured status reports in JSON/YAML format — Allow external tools to parse system state
- [ ] Validation script provides exit codes that reflect validation outcomes — Enable CI systems to detect success/failure states
- [ ] Machine-readable output includes timing information for performance monitoring — Allow performance tracking in automated systems

#### v2 Scope (Deferred)

- [ ] Advanced metrics export in Prometheus format for monitoring systems — Integrate with enterprise monitoring solutions
- [ ] Real-time event streaming for long-running operations — Enable real-time dashboards and notifications

#### Out of Scope

- XML output format support — Focus on JSON/YAML for modern tooling
- Custom output format templating — Standard formats sufficient for current needs

### LWF-04: Additional API Endpoint Validation

**Category Goal:** Enhance validation beyond basic health checks to verify critical functionality.

#### v1.2 Requirements (Must Have)

- [ ] Developer can run extended smoke checks that validate specific high-value API endpoints — Verify critical functionality beyond basic health
- [ ] System validates crime dataset endpoints return expected data structures — Ensure data availability and format consistency
- [ ] API validation includes response time thresholds for performance verification — Verify acceptable performance under load
- [ ] Extended validation includes data integrity checks for recently processed datasets — Ensure pipeline output quality

#### v2 Scope (Deferred)

- [ ] Full API contract validation against OpenAPI specification — Comprehensive API compliance checking
- [ ] Historical data validation across multiple time periods — Verify data consistency over time

#### Out of Scope

- Validation of external data sources — Focus on internal API validation
- Real-world data accuracy verification — Validate data structure, not real-world correctness

### LWF-05: Host Resource Detection and Smart Presets

**Category Goal:** Automatically optimize runtime configuration based on available system resources.

#### v1.2 Requirements (Must Have)

- [ ] System detects available CPU cores and RAM before startup — Enable resource-aware configuration
- [ ] Runtime presets automatically adjust based on detected resources — Optimize performance for available hardware
- [ ] Developer receives preset recommendations based on available resources — Guide users to optimal configuration
- [ ] Resource detection works across common development platforms (Linux, macOS, Windows WSL) — Ensure broad compatibility

#### v2 Scope (Deferred)

- [ ] Dynamic resource adjustment during runtime — Adapt to changing system conditions
- [ ] Machine learning-based optimization for workload patterns — Predictive resource optimization

#### Out of Scope

- Automatic resource allocation without user oversight — Maintain user control over resource usage
- Complex preset configurations with more than 3-4 options — Keep configuration simple and manageable

### Development Workflow Enhancements

**Category Goal:** Improve overall developer experience with better tooling and documentation.

#### v1.2 Requirements (Must Have)

- [ ] Comprehensive documentation for LWF-03, LWF-04, and LWF-05 features — Clear guidance for developers
- [ ] Simplified command interface for common development tasks — Reduce cognitive load for routine operations
- [ ] Clear error messages with actionable suggestions — Reduce troubleshooting time
- [ ] Validation of configuration consistency across preset modes — Prevent configuration drift

#### v2 Scope (Deferred)

- [ ] Interactive setup wizard for initial configuration — Guided onboarding experience
- [ ] Advanced debugging tools integration — Enhanced troubleshooting capabilities

#### Out of Scope

- IDE plugin development — Focus on command-line tooling
- GUI configuration tools — Maintain CLI-first approach

## Validated Requirements (From Previous Milestones)

These requirements were validated in previous milestones and remain in scope:

- ✓ User can run analytics and data prep workflows through Python CLI and pipeline commands — existing
- ✓ User can access precomputed crime datasets through versioned FastAPI endpoints — existing
- ✓ User can use a web dashboard with maps/charts backed by API data — existing
- ✓ User can refresh/export API-ready artifacts from pipeline code — existing
- ✓ User can run the system with containerized components already present in repo tooling — existing
- ✓ Developer can start API, frontend, data refresh/export pipeline, and supporting services entirely locally with one `docker compose up` — v1.0
- ✓ Containers are split appropriately by service boundary (multiple containers as needed) — v1.0
- ✓ Container images are minimized for size using slim/multi-stage builds where practical — v1.0
- ✓ Runtime resource limits are enforced for CPU and memory per service in local compose configuration — v1.0
- ✓ Local startup/docs make local-only operation the default development path — v1.0
- ✓ Developer can run automated post-start smoke checks that verify API endpoint readiness and expected artifact availability after compose startup — v1.1
- ✓ Developer can choose low-power vs high-performance local runtime presets through clear compose profile conventions and documented resource defaults — v1.1
- ✓ Default startup path remains `docker compose up` while optional preset modes are explicitly documented and validated — v1.1

## Constraints

- **Hosting**: Local development only — no non-local hosting in this scope
- **Runtime Footprint**: Low memory/CPU and small image sizes — to keep local runs lightweight
- **Orchestration**: Docker Compose command parity — single-command bring-up is mandatory
- **Architecture**: Preserve existing service boundaries — avoid regressions in analysis/API/frontend capabilities
- **Automation Compatibility**: Must work with standard CI/CD tools — enable integration with existing workflows

## Success Criteria

v1.2 will be complete when:

1. All v1.2 requirements in LWF-03, LWF-04, and LWF-05 categories are satisfied
2. All validated requirements from previous milestones remain functional
3. Documentation for new features is complete and accurate
4. Performance benchmarks show acceptable response times for validation operations
5. Cross-platform compatibility is verified across Linux, macOS, and Windows WSL

## Traceability

- **Roadmap Link:** [.planning/ROADMAP.md](.planning/ROADMAP.md)
- **Phase Mapping:**
  - LWF-03 requirements → Phase 7: Machine-Readable Output for Automation
  - LWF-04 requirements → Phase 8: Additional API Endpoint Validation  
  - LWF-05 requirements → Phase 9: Host Resource Detection and Smart Presets
- **State Tracking:** [.planning/STATE.md](.planning/STATE.md)

---
*Requirements defined: February 6, 2026*
*For milestone: v1.2 Deferred Workflow Enhancements*
*Traceability added: February 7, 2026*