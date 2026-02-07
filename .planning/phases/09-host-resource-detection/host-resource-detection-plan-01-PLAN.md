---
must_haves:
  - "System detects available CPU cores and RAM before startup"
  - "Runtime presets automatically adjust based on detected resources"
  - "Developer receives preset recommendations based on available resources"
  - "Resource detection works across common development platforms (Linux, macOS, Windows WSL)"
truths:
  - "Current system has low-power and high-performance runtime presets"
  - "Docker Compose orchestrates the local development environment"
  - "System needs to maintain backward compatibility with existing presets"
  - "Resource detection should happen before container startup"
artifacts:
  - "resource_detector.py - Script to detect host resources"
  - "preset_calculator.py - Logic to determine optimal presets"
  - "enhanced docker-compose.yml with dynamic resource allocation"
  - "Updated README documentation"
key_links:
  - ".planning/ROADMAP.md#phase-9-host-resource-detection-and-smart-presets"
  - ".planning/REQUIREMENTS.md#lwf-05-host-resource-detection-and-smart-presets"
  - "config/docker-compose.yml"
---

# Phase 9: Host Resource Detection and Smart Presets - PLAN 01

## Objective
Implement automatic host resource detection and smart preset recommendations for the Crime Incidents Philadelphia project. The system should detect available CPU cores and RAM before startup, automatically adjust runtime presets based on detected resources, and provide platform-compatible resource detection across Linux, macOS, and Windows WSL.

## Execution Context
- @config/docker-compose.yml
- @scripts/validate_local_stack.py
- @Makefile
- @.env.runtime.high-performance
- @.env.runtime.low-power
- @docs/resource_detection.md (to be created)

## Context
Based on the project state, phase 9 aims to implement LWF-05 requirements for host resource detection and smart presets. The system currently has low-power and high-performance runtime presets that need to be enhanced with automatic resource-based adjustments. The solution must work across common development platforms (Linux, macOS, Windows WSL) and maintain backward compatibility with existing functionality.

### Phase 9 Requirements:
- LWF-05-1: System detects available CPU cores and RAM before startup
- LWF-05-2: Runtime presets automatically adjust based on detected resources  
- LWF-05-3: Developer receives preset recommendations based on available resources
- LWF-05-4: Resource detection works across common development platforms (Linux, macOS, Windows WSL)

## Tasks

### Task 1: Create Resource Detection Module
- Create `scripts/resource_detector.py` with functions to detect:
  - Available CPU cores
  - Total system RAM
  - Available system RAM
- Implement cross-platform compatibility for Linux, macOS, and Windows WSL
- Add error handling for edge cases where resource detection fails

### Task 2: Develop Preset Calculation Logic
- Create `scripts/preset_calculator.py` with logic to:
  - Map detected resources to optimal preset configurations
  - Define thresholds for CPU and RAM to determine preset levels
  - Generate recommendations based on available resources
  - Handle cases where system resources are insufficient

### Task 3: Integrate Resource Detection with Docker Compose
- Modify the docker-compose workflow to run resource detection before startup
- Create a wrapper script that determines appropriate presets based on detected resources
- Update environment variables in docker-compose to reflect calculated presets
- Ensure backward compatibility with manual preset selection

### Task 4: Implement Cross-Platform Compatibility
- Test resource detection on Linux, macOS, and Windows WSL environments
- Handle platform-specific differences in resource detection methods
- Create platform-specific fallback mechanisms if primary detection fails
- Document any platform-specific limitations

### Task 5: Update Documentation and User Interface
- Update README.md with information about automatic resource detection
- Add documentation for the new preset recommendation system
- Update usage examples to reflect the new automatic behavior
- Create a troubleshooting section for resource detection issues

## Verification
- Run resource detection on multiple platforms (Linux, macOS, Windows WSL)
- Verify that presets are automatically adjusted based on detected resources
- Confirm that manual preset override still works when needed
- Test edge cases where system resources are minimal
- Validate that existing functionality remains intact

## Success Criteria
- System successfully detects CPU cores and RAM on all supported platforms
- Runtime presets automatically adjust based on detected resources
- Developers receive clear preset recommendations based on available resources
- Resource detection works consistently across Linux, macOS, and Windows WSL
- Backward compatibility maintained with existing preset system
- All existing functionality continues to work as expected

## Output
- Resource detection module with cross-platform compatibility
- Preset calculation logic integrated with Docker Compose workflow
- Updated documentation explaining the new automatic preset system
- Verified functionality across all supported development platforms