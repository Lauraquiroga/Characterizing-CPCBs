"""
This script computes the average Time to Fix (TTF) for each resolution strategy and structural configuration based on the TTF results from the TTF_RESULTS file.

The following rules are applied when computing the average TTF:
1. Scenarios with TTF = NA (corresponding to PF9 - No Fix scenarios) will be excluded from the average TTF computation.
2. The average TTF will be computed in days and rounded to the nearest day.
3. Since there are negative TTF values in the TTF_RESULTS file, the absolute value of the TTF is used instead of the raw TTF value when computing the average, as we are interested in the magnitude of the TTF rather than its direction (positive or negative).
"""

import csv
from collections import defaultdict

TTF_RESULTS = 'issue_ttf.csv'
"""
Headers:
Scenario,FixStrategy,StructuralConfig,TTF
"""

TTF_AVERAGES = 'ttf_averages.csv'
"""
Headers:
FixStrategy,StructuralConfig,AverageTTF
"""


def compute_average_ttf():
    # Dictionary to store TTF values for each (FixStrategy, StructuralConfig) combination
    ttf_data = defaultdict(list)
    
    # Read the TTF results file
    with open(TTF_RESULTS, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            ttf_value = row['TTF']
            
            # Skip rows with NA values
            if ttf_value == 'NA' or ttf_value == '':
                continue
            
            try:
                # Convert to float and take absolute value
                ttf = abs(float(ttf_value))
                fix_strategy = row['FixStrategy']
                structural_config = row['StructuralConfig']
                
                # Store the TTF value for this combination
                ttf_data[(fix_strategy, structural_config)].append(ttf)
            except ValueError:
                # Skip any rows with invalid TTF values
                continue
    
    # Compute averages and write to output file
    with open(TTF_AVERAGES, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['FixStrategy', 'StructuralConfig', 'AverageTTF'])
        
        # Sort by FixStrategy and StructuralConfig for consistent output
        for (fix_strategy, structural_config), ttf_values in sorted(ttf_data.items()):
            if ttf_values:  # Only compute average if there are values
                # Compute average in seconds, then convert to days
                average_ttf_seconds = sum(ttf_values) / len(ttf_values)
                average_ttf_days = round(average_ttf_seconds / 86400)  # 86400 seconds in a day
                writer.writerow([fix_strategy, structural_config, average_ttf_days])
    
    print(f"Average TTF values computed and saved to {TTF_AVERAGES}")
    print(f"Processed {len(ttf_data)} unique (FixStrategy, StructuralConfig) combinations")

if __name__ == '__main__':
    compute_average_ttf()