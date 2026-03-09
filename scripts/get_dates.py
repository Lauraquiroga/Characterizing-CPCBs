"""
Script to enrich the issue data with dates from GitHub API
Reads from issue_summary.csv containing all issues involved in the studied scenariosand writes to issue_dates.csv with additional columns:
State, OpenDate, CloseDate, MergeDate
Requires a GitHub Personal Access Token (PAT) with repo access, set in .env file as:
PAC=your_personal_access_token
"""

import os
from dotenv import load_dotenv
import csv
import requests

load_dotenv()  # Loads variables from .env into environment

GITHUB_TOKEN = os.getenv('PAC') # Get Personal Access Token
HEADERS = {'Authorization': f'token {GITHUB_TOKEN}'}

ISSUES = 'data/scenarios_dataset/issue_summary.csv'
"""
Headers: 
Id,Type,Issue,Scenario,Project,HasFix,Migrated
"""
ISSUE_DATES = 'data/scenarios_dataset/issue_dates.csv'
"""
Headers:
Id,Type,Issue,Scenario,Project,HasFix,Migrated,State,OpenDate,CloseDate,MergeDate
Note dates are in the format: ISO 8601 (YYYY-MM-DDTHH:MM:SSZ)
"""

def parse_issue_identifier(issue_str):
    """
    Parse issue identifier in format: owner/repo#id
    Returns: (owner, repo, id)
    """
    if not issue_str or issue_str == 'NA':
        return None, None, None
    
    try:
        # Split by '#' to separate repo path and issue number
        repo_path, issue_id = issue_str.split('#')
        owner, repo = repo_path.split('/')
        return owner, repo, issue_id
    except:
        return None, None, None

def get_issue_data(owner, repo, issue_id):
    """
    Get data for a bug report (issue) from GitHub API
    Returns: (state, open_date, close_date)
    """
    url = f'https://api.github.com/repos/{owner}/{repo}/issues/{issue_id}'
    try:
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 200:
            data = response.json()
            state = data.get('state', '')
            open_date = data.get('created_at', '')
            close_date = data.get('closed_at', '') if data.get('closed_at') else ''
            return state, open_date, close_date
        else:
            print(f"Error fetching issue {owner}/{repo}#{issue_id}: {response.status_code}")
            return '', '', ''
    except Exception as e:
        print(f"Exception fetching issue {owner}/{repo}#{issue_id}: {e}")
        return '', '', ''

def get_pr_data(owner, repo, pr_id):
    """
    Get data for a pull request from GitHub API
    Returns: (state, open_date, close_date, merge_date)
    """
    url = f'https://api.github.com/repos/{owner}/{repo}/pulls/{pr_id}'
    try:
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 200:
            data = response.json()
            state = data.get('state', '')
            open_date = data.get('created_at', '')
            close_date = data.get('closed_at', '') if data.get('closed_at') else ''
            merge_date = data.get('merged_at', '') if data.get('merged_at') else ''
            return state, open_date, close_date, merge_date
        else:
            print(f"Error fetching PR {owner}/{repo}#{pr_id}: {response.status_code}")
            return '', '', '', ''
    except Exception as e:
        print(f"Exception fetching PR {owner}/{repo}#{pr_id}: {e}")
        return '', '', '', ''

def get_commit_data(owner, repo, commit_sha):
    """
    Get data for a commit from GitHub API
    Returns: commit_date
    """
    url = f'https://api.github.com/repos/{owner}/{repo}/commits/{commit_sha}'
    try:
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 200:
            data = response.json()
            commit_date = data.get('commit', {}).get('committer', {}).get('date', '')
            return commit_date
        else:
            print(f"Error fetching commit {owner}/{repo}/{commit_sha}: {response.status_code}")
            return ''
    except Exception as e:
        print(f"Exception fetching commit {owner}/{repo}/{commit_sha}: {e}")
        return ''

def process_issues():
    """
    Process the issues from ISSUES file and enrich with GitHub API data
    """
    # Read input file (using utf-8-sig to handle BOM if present)
    with open(ISSUES, 'r', encoding='utf-8-sig') as infile:
        reader = csv.DictReader(infile)
        rows = list(reader)
    
    # Process each row and collect enriched data
    enriched_rows = []
    
    for i, row in enumerate(rows, 1):
        issue_type = row['Type']
        issue_str = row['Issue']
        
        # Create base enriched row with original data
        enriched_row = row.copy()
        enriched_row['State'] = ''
        enriched_row['OpenDate'] = ''
        enriched_row['CloseDate'] = ''
        enriched_row['MergeDate'] = ''
        
        # Parse issue identifier
        owner, repo, issue_id = parse_issue_identifier(issue_str)
        
        if issue_type == 'BR' and owner and repo and issue_id:
            # Bug Report - get issue data
            print(f"Processing BR {i}/{len(rows)}: {issue_str}")
            state, open_date, close_date = get_issue_data(owner, repo, issue_id)
            enriched_row['State'] = state
            enriched_row['OpenDate'] = open_date
            enriched_row['CloseDate'] = close_date
            
        elif issue_type == 'PR' and owner and repo and issue_id:
            # Pull Request - get PR data
            print(f"Processing PR {i}/{len(rows)}: {issue_str}")
            state, open_date, close_date, merge_date = get_pr_data(owner, repo, issue_id)
            enriched_row['State'] = state
            enriched_row['OpenDate'] = open_date
            enriched_row['CloseDate'] = close_date
            enriched_row['MergeDate'] = merge_date
            
        elif issue_type == 'C' and owner and repo and issue_id:
            # Commit - get commit data
            print(f"Processing Commit {i}/{len(rows)}: {issue_str}")
            commit_date = get_commit_data(owner, repo, issue_id)
            enriched_row['MergeDate'] = commit_date
            
        elif issue_type == 'NA':
            # Not applicable - leave fields empty
            print(f"Processing NA {i}/{len(rows)}: {issue_str}")
        
        enriched_rows.append(enriched_row)
    
    # Write enriched data to output file
    fieldnames = ['Id', 'Type', 'Issue', 'Scenario', 'Project', 'HasFix', 'Migrated',
                  'State', 'OpenDate', 'CloseDate', 'MergeDate']
    
    with open(ISSUE_DATES, 'w', encoding='utf-8', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(enriched_rows)
    
    print(f"\nProcessing complete! Enriched data written to {ISSUE_DATES}")
    print(f"Total rows processed: {len(enriched_rows)}")

if __name__ == '__main__':
    process_issues()