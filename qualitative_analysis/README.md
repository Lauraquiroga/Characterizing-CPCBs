# Qualitative Analysis

This folder contains the artifacts produced during the qualitative analysis phase of the CPCB study. The analysis involved manually examining scenarios from the source dataset, filtering invalid cases, annotating bug resolution patterns, and developing a comprehensive taxonomy of resolution strategies and structural configurations.

## Folder Structure

### `filtering/`

Contains documentation of scenarios that were discarded during the filtering process.

**Files:**
- `discarded_scenarios.pdf` - Comprehensive list of discarded scenario IDs with their corresponding discard reasons. This document explains why certain scenarios were excluded from the final analysis (e.g., insufficient information, invalid bug links, out of scope, etc.).

### `intermediate_artifacts/`

Contains artifacts from the manual analysis of the dataset, including detailed annotations and diagrams used to understand each scenario.

**Files:**
- `scenario_annotations.pdf` - Detailed manual analysis documentation including:
  - Visual diagrams illustrating the relationships between projects and bugs in each scenario
  - Annotations explaining the timeline and flow of bug resolution
  - Documentation of issues (bug reports, pull requests, commits) involved in each scenario
  - Mapping of pairs from the original dataset to their corresponding scenarios
  - Analysis of the fix implementation and its propagation across projects

This artifact served as the foundation for identifying patterns that led to the development of the resolution strategy taxonomy.

### `taxonomy/`

Contains the developed taxonomies that emerged from the qualitative analysis, classifying bug resolution approaches and project relationship patterns.

**Files:**
- `ResolutionStrategies.pdf` - Complete taxonomy of the seven resolution strategies (RS1-RS7) identified in the study:
  - RS1: Wait-for-Upstream Fix
  - RS2: Downstream Fix
  - RS3: Coordinated Fix
  - RS4: Temporary Fix
  - RS5: Upstream Patch Adoption
  - RS6: Replacement Fix
  - RS7: No Fix
  
  Each strategy is documented with definitions, characteristics, and examples from the dataset.

- `structural_configurations.xlsx` - Taxonomy of structural configurations describing the different architectural patterns in which CPCBs manifest. This includes variations in:
  - Project relationships (upstream-downstream dependencies)
  - Issue configurations (where bugs are reported and fixed)

## Analysis Process

The qualitative analysis followed this workflow:   

1. **Initial Filtering** - Reviewed all pairs from the source dataset (cpcb_filtered_pairs.csv) and grouped them into scenarios, such that each scenario represts a distinct CPCB.     
2. **Scenario Annotation** - Created detailed diagrams and annotations for each scenario to understand the bug resolution timeline and relationships. Identified cases to discard based on data quality and relevance criteria.     
3. **Pattern Identification** - Analyzed annotated scenarios to identify recurring patterns in how bugs are resolved across projects.    
4. **Taxonomy Development** - Synthesized identified patterns into formal taxonomies for resolution strategies and structural configurations
5. **Validation** - Verified that all scenarios could be classified using the developed taxonomies

## Usage

These artifacts support:
- Understanding the rationale behind scenario inclusion/exclusion decisions
- Tracing the development of the resolution strategy taxonomy
- Validating scenario classifications
- Replicating or extending the qualitative analysis
- Training additional coders for inter-rater reliability studies