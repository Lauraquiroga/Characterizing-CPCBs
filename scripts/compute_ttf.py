"""
Resolution Strategies:
RS4: Temporary Fix
RS1: Wait-for_upstream Fix
RS2: Downstream Fix
RS6: Replacement Fix
RS3: Coordinated Fix
RS5: Upstream Patch Adoption
RS7: No Fix

We calculate the TTF for each scenario in the SCENARIOS file, using the issue data from ISSUE_DATES file. We will then output a CSV file (TTF_OUTPUT) with the TTF for each scenario.
The TTF is calculated in seconds and the computation depends on both the resolution strategy and the structural configuration of the scenario.
In general terms:
For RS7 (No Fix): TTF = NA
For RS1: TTF = MergeDate of upstream fix - OpenDate of downstream issue
For RS3: TTF = max(MergeDate of downstream fix, MergeDate of upstream fix) - OpenDate of downstream issue
For RS4, RS2, RS6, RS5: TTF = MergeDate of downstream fix - OpenDate of downstream issue

However, the data actually available depends on the structural configuration.

To compute the TTF, we:
1. Read the scenarios from the SCENARIOS file 
2. If the scenario has FixStrategyD = RS7, we set TTF to NA and move to the next scenario.
3. For each scenario, identify the artifacts involved by matching the field ScenarioOriginal with the issue data in ISSUE_DATES file, field Scenario.
   Note that each scenario is going to involve multiple rows from the ISSUE_DATES file.
4. To get the OpenDate of downstream issue, we look for the row in ISSUE_DATES file where Project is 'd' and type is 'BR' with the oldest date in the OpenDate field.
5. If there is no row of type 'BR' with Project 'd', we look for the row with type 'PR' and Project 'd' with the oldest date in the OpenDate field.
6. To get the MergeDate of downstream fix, we look for the row in ISSUE_DATES file where Project is 'd' and type is 'PR' and HasFix is 1 with the newest date in the MergeDate field.
7. If there is no row with type 'PR' and Project 'd' and HasFix is 1, we look for the row with type 'C' and Project 'd' and HasFix is 1 with the newest date in the MergeDate field.
8. To get the MergeDate of upstream fix, we look for the row in ISSUE_DATES file where Project is 'u1' and type is 'PR' and HasFix is 1 with the newest date in the MergeDate field.
9. If there is no row with type 'PR' and Project 'u1' and HasFix is 1, we look for the row with type 'C' and Project 'u1' and HasFix is 1 with the newest date in the MergeDate field.
10. If there is no row with type 'C' and Project 'u1' and HasFix is 1, we look for the row with type 'PR' and Project 'u2' and HasFix is 1 with the newest date in the MergeDate field.
11. If there is no row with type 'PR' and Project 'u2' and HasFix is 1, we look for the row with type 'C' and Project 'u2' and HasFix is 1 with the newest date in the MergeDate field.
12. Once we have the OpenDate of downstream issue, the MergeDate of downstream fix and/or the MergeDate of upstream fix, we will compute the TTF based on the resolution strategy of the scenario
    Note: For RS1, we need the MergeDate of upstream fix and the OpenDate of downstream issue
          For RS3, we need the MergeDate of downstream fix, the MergeDate of upstream fix and the OpenDate of downstream issue
          For RS4, RS2, RS6, RS5, we need the MergeDate of downstream fix and the OpenDate of downstream issue



We exclude the following scenarios, which will be computed manually:
ScenarioOriginal = 45 -> fix is not on GitHub (Chromium bug tracker)
Scenario Original = 80 -> Fix is not linked but mentioned in the comments
ScenarioOriginal = 19 -> Merged by rebase, no merge date available
"""


SCENARIOS = 'dataset/scenarios/scenario_summary.csv'
"""
Headers:
ID,ScenarioOriginal,NumberProjects,Downstream,Upstream1,Upstream2,FixStrategyD,FixStrategyU1,StructuralConfig
"""
ISSUE_DATES = 'dataset/scenarios/issue_dates.csv'
"""
Headers:
Id,Type,Issue,Scenario,Project,HasFix,Migrated,State,OpenDate,CloseDate,MergeDate
"""

TTF_OUTPUT = 'dataset/scenarios/issue_ttf.csv'
"""
Headers:
Scenario,FixStrategy,StructuralConfig,TTF
"""


import csv
from datetime import datetime
import os

# Scenarios to exclude (computed manually)
EXCLUDED_SCENARIOS = [45, 80, 19]


def parse_date(date_str):
    """Parse date string to datetime object. Handle various formats."""
    if not date_str or date_str.strip() == '':
        return None
    
    try:
        # Try ISO format first
        return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
    except:
        try:
            # Try common date formats
            for fmt in ['%Y-%m-%dT%H:%M:%SZ', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d']:
                try:
                    return datetime.strptime(date_str, fmt)
                except:
                    continue
        except:
            pass
    
    return None


def get_downstream_open_date(issue_rows):
    """
    Get OpenDate of downstream issue.
    Priority: 'd' + 'BR' (oldest), then 'd' + 'PR' (oldest)
    """
    br_dates = []
    pr_dates = []
    
    for row in issue_rows:
        if row['Project'] == 'd':
            open_date = parse_date(row['OpenDate'])
            if open_date:
                if row['Type'] == 'BR':
                    br_dates.append(open_date)
                elif row['Type'] == 'PR':
                    pr_dates.append(open_date)
    
    if br_dates:
        return min(br_dates)
    elif pr_dates:
        return min(pr_dates)
    
    return None


def get_downstream_merge_date(issue_rows):
    """
    Get MergeDate of downstream fix.
    Priority: 'd' + 'PR' + HasFix=1 (newest), then 'd' + 'C' + HasFix=1 (newest)
    """
    pr_dates = []
    c_dates = []
    
    for row in issue_rows:
        if row['Project'] == 'd' and row['HasFix'] == '1':
            merge_date = parse_date(row['MergeDate'])
            if merge_date:
                if row['Type'] == 'PR':
                    pr_dates.append(merge_date)
                elif row['Type'] == 'C':
                    c_dates.append(merge_date)
    
    if pr_dates:
        return max(pr_dates)
    elif c_dates:
        return max(c_dates)
    
    return None


def get_upstream_merge_date(issue_rows):
    """
    Get MergeDate of upstream fix.
    Priority: 'u1' + 'PR' + HasFix=1 (newest), then 'u1' + 'C' + HasFix=1 (newest),
              then 'u2' + 'PR' + HasFix=1 (newest), then 'u2' + 'C' + HasFix=1 (newest)
    """
    u1_pr_dates = []
    u1_c_dates = []
    u2_pr_dates = []
    u2_c_dates = []
    
    for row in issue_rows:
        if row['HasFix'] == '1':
            merge_date = parse_date(row['MergeDate'])
            if merge_date:
                if row['Project'] == 'u1':
                    if row['Type'] == 'PR':
                        u1_pr_dates.append(merge_date)
                    elif row['Type'] == 'C':
                        u1_c_dates.append(merge_date)
                elif row['Project'] == 'u2':
                    if row['Type'] == 'PR':
                        u2_pr_dates.append(merge_date)
                    elif row['Type'] == 'C':
                        u2_c_dates.append(merge_date)
    
    if u1_pr_dates:
        return max(u1_pr_dates)
    elif u1_c_dates:
        return max(u1_c_dates)
    elif u2_pr_dates:
        return max(u2_pr_dates)
    elif u2_c_dates:
        return max(u2_c_dates)
    
    return None


def calculate_ttf(fix_strategy, downstream_open, downstream_merge, upstream_merge):
    """
    Calculate TTF based on resolution strategy.
    Returns TTF in seconds or 'NA' if not applicable/computable.
    """
    if fix_strategy == 'RS7':
        return 'NA'
    
    if fix_strategy == 'RS1':
        # TTF = MergeDate of upstream fix - OpenDate of downstream issue
        if upstream_merge and downstream_open:
            return int((upstream_merge - downstream_open).total_seconds())
        else:
            return 'NA'
    
    elif fix_strategy == 'RS3':
        # TTF = max(MergeDate of downstream fix, MergeDate of upstream fix) - OpenDate of downstream issue
        if downstream_merge and upstream_merge and downstream_open:
            max_merge = max(downstream_merge, upstream_merge)
            return int((max_merge - downstream_open).total_seconds())
        else:
            return 'NA'
    
    elif fix_strategy in ['RS4', 'RS2', 'RS6', 'RS5']:
        # TTF = MergeDate of downstream fix - OpenDate of downstream issue
        if downstream_merge and downstream_open:
            return int((downstream_merge - downstream_open).total_seconds())
        else:
            return 'NA'
    
    return 'NA'


def main():
    """Main function to compute TTF for all scenarios."""
    
    # Read issue dates data
    issue_data = {}
    with open(ISSUE_DATES, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            scenario = int(row['Scenario'])
            if scenario not in issue_data:
                issue_data[scenario] = []
            issue_data[scenario].append(row)
    
    print(f"Loaded issue data for {len(issue_data)} scenarios")
    
    # Read scenarios and compute TTF
    results = []
    with open(SCENARIOS, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            scenario_original = int(row['ScenarioOriginal'])
            fix_strategy = row['FixStrategyD']
            structural_config = row['StructuralConfig']
            
            # Skip excluded scenarios
            if scenario_original in EXCLUDED_SCENARIOS:
                print(f"Skipping scenario {scenario_original} (excluded)")
                results.append({
                    'Scenario': scenario_original,
                    'FixStrategy': fix_strategy,
                    'StructuralConfig': structural_config,
                    'TTF': 'EXCLUDED'
                })
                continue
            
            # Get issue rows for this scenario
            issue_rows = issue_data.get(scenario_original, [])
            
            if not issue_rows:
                print(f"Warning: No issue data found for scenario {scenario_original}")
                results.append({
                    'Scenario': scenario_original,
                    'FixStrategy': fix_strategy,
                    'StructuralConfig': structural_config,
                    'TTF': 'NA'
                })
                continue
            
            # Get required dates
            downstream_open = get_downstream_open_date(issue_rows)
            downstream_merge = get_downstream_merge_date(issue_rows)
            upstream_merge = get_upstream_merge_date(issue_rows)
            
            # Calculate TTF
            ttf = calculate_ttf(fix_strategy, downstream_open, downstream_merge, upstream_merge)
            
            results.append({
                'Scenario': scenario_original,
                'FixStrategy': fix_strategy,
                'StructuralConfig': structural_config,
                'TTF': ttf
            })
            
            print(f"Scenario {scenario_original}: FixStrategy={fix_strategy}, TTF={ttf}")
    
    # Write results to output file
    with open(TTF_OUTPUT, 'w', encoding='utf-8', newline='') as f:
        fieldnames = ['Scenario', 'FixStrategy', 'StructuralConfig', 'TTF']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    
    print(f"\nResults written to {TTF_OUTPUT}")
    print(f"Total scenarios processed: {len(results)}")
    
    # Summary statistics
    numeric_ttfs = [r['TTF'] for r in results if isinstance(r['TTF'], int)]
    if numeric_ttfs:
        print(f"Scenarios with computed TTF: {len(numeric_ttfs)}")
        print(f"Average TTF: {sum(numeric_ttfs) / len(numeric_ttfs):.2f} seconds")
        print(f"Min TTF: {min(numeric_ttfs)} seconds")
        print(f"Max TTF: {max(numeric_ttfs)} seconds")


if __name__ == '__main__':
    main()
