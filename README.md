# Characterizing Cross-Project Correlated Bug Resolution in the Python Ecosystem
ICSME 2026

## Overview

This repository contains the data and analysis scripts for studying Cross-Project Correlated Bugs (CPCBs) in the Python ecosystem. The research focuses on characterizing how bugs are resolved across multiple projects, particularly analyzing the relationship between upstream libraries and downstream dependents.
        
The study identifies seven resolution strategies for CPCBs:
- **RS1**: Wait-for-Upstream Fix
- **RS2**: Downstream Fix
- **RS3**: Coordinated Fix
- **RS4**: Temporary Fix
- **RS5**: Upstream Patch Adoption
- **RS6**: Replacement Fix
- **RS7**: No Fix

## Repository Structure

### Data

#### `data/source_dataset/`
Contains the primary CPCB dataset files:
- `cpcb_dataset.csv` - The complete CPCB dataset borrowed from Ma et al. (2017) [1]
- `cpcb_filtered_pairs.csv` - Filtered pairs of CPCBs used in our study

#### `data/scenarios/`
Contains processed scenario data and analysis results:
- `scenario_summary.csv` - Summary of all bug resolution scenarios with resolution strategies and structural configurations
- `issue_summary.csv` - All issues (bug reports, pull requests, commits) involved in studied scenarios
- `issue_dates.csv` - Issue data enriched with temporal information (state, open date, close date, merge date)
- `issue_ttf.csv` - Computed Time to Fix (TTF) for each scenario
- `ttf_averages.csv` - Average TTF grouped by resolution strategy and structural configuration

### Qualitative Analysis

#### `qualitative_analysis/`
Contains artifacts from the qualitative analysis phase:
- `filtering/` - Data filtering artifacts
- `intermediate_artifacts/` - Intermediate analysis artifacts
- `taxonomy/` - Bug resolution taxonomy artifacts

### Scripts

#### `scripts/get_dates.py`
Enriches issue data with temporal information from the GitHub API. Reads from `issue_summary.csv` and outputs `issue_dates.csv` with added date fields (State, OpenDate, CloseDate, MergeDate). All dates in the dataset follow ISO 8601 format (`YYYY-MM-DDTHH:MM:SSZ`).     

**Requirements:** GitHub Personal Access Token (PAT) stored in a `.env` file as `PAC=your_token`

#### `scripts/compute_ttf.py`
Calculates the Time to Fix (TTF) for each scenario based on:
- Resolution strategy (RS1-RS7)
- Structural configuration
- Available temporal data (issue open dates, fix merge dates)

TTF computation varies by resolution strategy:
- **RS1 (Wait-for-Upstream Fix)**: TTF = Upstream merge date - Downstream issue open date
- **RS2 (Downstream Fix), RS4 (Temporary Fix), RS5 (Upstream Patch Adoption), RS6 (Replacement Fix)**: TTF = Downstream merge date - Downstream issue open date
- **RS3 (Coordinated Fix)**: TTF = max(Downstream merge date, Upstream merge date) - Downstream issue open date
- **RS7 (No Fix)**: TTF = NA
        
TTF values are computed in seconds and can be converted to days for analysis.      

#### `scripts/ttf_averages.py`
Computes average TTF (in days) grouped by resolution strategy and structural configuration. Uses absolute values of TTF to focus on magnitude rather than direction. Excludes NA values (RS7 scenarios).



## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. For scripts that use the GitHub API (`get_dates.py`), create a `.env` file with your Personal Access Token:
   ```
   PAC=your_github_personal_access_token
   ```
## References     
1. Ma, W., Chen, L., Zhang, X., Zhou, Y., & Xu, B. (2017, May). How do developers fix cross-project correlated bugs? a case study on the github scientific python ecosystem. In 2017 IEEE/ACM 39th International Conference on Software Engineering (ICSE) (pp. 381-392). IEEE.       

