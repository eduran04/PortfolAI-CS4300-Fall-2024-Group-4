"""Security report automation for GitHub pull requests."""

import json
import os
import re
import sys
from github import Github, GithubException
from github.PullRequest import PullRequest


def initialize() -> tuple[Github, str, str]:
    """Initialize GitHub client and return it with repository info."""
    github_token = os.getenv('GITHUB_TOKEN')
    if not github_token:
        raise ValueError("GITHUB_TOKEN is not set")
    
    repo_name = os.getenv('GITHUB_REPOSITORY')
    if not repo_name:
        raise ValueError("GITHUB_REPOSITORY is not set")
    
    pr_id = os.getenv('GITHUB_PR_ID')
    if not pr_id:
        raise ValueError("GITHUB_PR_ID is not set")
    
    g = Github(github_token)
    return g, repo_name, pr_id


def get_pull_request(g: Github, repo_name: str, pr_id: str) -> PullRequest:
    """Fetch pull request from GitHub repository."""
    try:
        repo = g.get_repo(repo_name)
        pr = repo.get_pull(int(pr_id))
        return pr
    except ValueError:
        raise ValueError(f"Invalid PR ID: {pr_id}")
    except GithubException as e:
        raise ValueError(f"Failed to fetch PR: {e}")


def parse_bandit_json(file_path: str) -> dict:
    """Parse Bandit JSON output and return structured data."""
    issues = []
    summary = {'HIGH': 0, 'MEDIUM': 0, 'LOW': 0, 'total': 0}
    
    if not os.path.exists(file_path):
        return {'issues': issues, 'summary': summary}
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except (json.JSONDecodeError, KeyError, IOError) as e:
        print(f"Warning: Failed to parse Bandit output: {e}")
        return {'issues': issues, 'summary': summary}
    
    for result in data.get('results', []):
        severity = result.get('issue_severity', 'UNKNOWN').upper()
        if severity in summary:
            summary[severity] += 1
            summary['total'] += 1
        
        issues.append({
            'file': result.get('filename', '').replace('portfolai/', ''),
            'line': result.get('line_number', 0),
            'severity': severity,
            'test_id': result.get('test_id', ''),
            'issue': result.get('issue_text', ''),
            'confidence': result.get('issue_confidence', '').upper()
        })
    
    return {'issues': issues, 'summary': summary}


def _categorize_pylint_severity(msg_type: str) -> str:
    """Categorize Pylint message type to severity."""
    if msg_type in ['error', 'fatal']:
        return 'HIGH'
    if msg_type == 'warning':
        return 'MEDIUM'
    return 'LOW'


def parse_pylint_text(file_path: str) -> dict:
    """Parse Pylint text output and return structured data."""
    issues = []
    summary = {'HIGH': 0, 'MEDIUM': 0, 'LOW': 0, 'total': 0}
    
    if not os.path.exists(file_path):
        return {'issues': issues, 'summary': summary}
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except (IOError, ValueError) as e:
        print(f"Warning: Failed to parse Pylint output: {e}")
        return {'issues': issues, 'summary': summary}
    
    pattern = re.compile(r'^([^:]+):(\d+):\s*(\w+):\s*(.+)$')
    
    for line in lines:
        match = pattern.match(line.strip())
        if not match:
            continue
        
        file_path, line_num, msg_type, message = match.groups()
        severity = _categorize_pylint_severity(msg_type)
        summary[severity] += 1
        summary['total'] += 1
        
        issues.append({
            'file': file_path.replace('portfolai/', ''),
            'line': int(line_num),
            'type': msg_type,
            'message': message
        })
    
    return {'issues': issues, 'summary': summary}


def _categorize_flake8_severity(code: str) -> str:
    """Categorize Flake8 code to severity."""
    if code.startswith('E9') or code.startswith('F'):
        return 'MEDIUM'
    return 'LOW'


def parse_flake8_text(file_path: str) -> dict:
    """Parse Flake8 text output and return structured data."""
    issues = []
    summary = {'HIGH': 0, 'MEDIUM': 0, 'LOW': 0, 'total': 0}
    
    if not os.path.exists(file_path):
        return {'issues': issues, 'summary': summary}
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except (IOError, ValueError) as e:
        print(f"Warning: Failed to parse Flake8 output: {e}")
        return {'issues': issues, 'summary': summary}
    
    pattern = re.compile(r'^([^:]+):(\d+):(\d+):\s*(\w+)\s+(.+)$')
    
    for line in lines:
        match = pattern.match(line.strip())
        if not match:
            continue
        
        file_path, line_num, col_num, code, message = match.groups()
        severity = _categorize_flake8_severity(code)
        summary[severity] += 1
        summary['total'] += 1
        
        issues.append({
            'file': file_path.replace('portfolai/', ''),
            'line': int(line_num),
            'col': int(col_num),
            'code': code,
            'message': message
        })
    
    return {'issues': issues, 'summary': summary}


def _parse_safety_json(file_path: str) -> list:
    """Parse Safety JSON file and return list of issues."""
    issues = []
    if not os.path.exists(file_path):
        return issues
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except IOError:
        return issues
    
    json_match = re.search(r'\{.*\}', content, re.DOTALL)
    if not json_match:
        return issues
    
    try:
        data = json.loads(json_match.group())
    except (json.JSONDecodeError, KeyError):
        return issues
    
    for vuln in data.get('vulnerabilities', []):
        issues.append({
            'package': vuln.get('package', ''),
            'installed': vuln.get('installed_version', ''),
            'vulnerable': vuln.get('vulnerable_spec', ''),
            'advisory': vuln.get('advisory', '')
        })
    
    return issues


def _parse_safety_text(file_path: str) -> list:
    """Parse Safety text file and return list of issues."""
    issues = []
    if not os.path.exists(file_path):
        return issues
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except IOError:
        return issues
    
    for line in lines:
        if '|' not in line or 'package' in line.lower():
            continue
        
        parts = [p.strip() for p in line.split('|')]
        if len(parts) < 3:
            continue
        
        issues.append({
            'package': parts[0] if len(parts) > 0 else '',
            'installed': parts[1] if len(parts) > 1 else '',
            'vulnerable': parts[2] if len(parts) > 2 else '',
            'advisory': parts[3] if len(parts) > 3 else ''
        })
    
    return issues


def parse_safety_output(file_path_json: str, file_path_txt: str) -> dict:
    """Parse Safety JSON or text output and return structured data."""
    issues = []
    summary = {'HIGH': 0, 'MEDIUM': 0, 'LOW': 0, 'total': 0}
    
    issues = _parse_safety_json(file_path_json)
    if not issues:
        issues = _parse_safety_text(file_path_txt)
    
    for _ in issues:
        summary['HIGH'] += 1
        summary['total'] += 1
    
    return {'issues': issues, 'summary': summary}


def _get_status_text(total_high: int, total_medium: int, 
                     total_low: int) -> str:
    """Get status text based on issue counts."""
    if total_high > 0:
        return "CRITICAL"
    if total_medium > 0:
        return "WARNING"
    if total_low > 0:
        return "INFO"
    return "PASS"


def format_security_report(bandit_data: dict, pylint_data: dict,
                          flake8_data: dict, safety_data: dict) -> str:
    """Format security report as markdown."""
    total_high = (bandit_data['summary']['HIGH'] +
                  pylint_data['summary']['HIGH'] +
                  safety_data['summary']['HIGH'])
    total_medium = (bandit_data['summary']['MEDIUM'] +
                    pylint_data['summary']['MEDIUM'] +
                    flake8_data['summary']['MEDIUM'])
    total_low = (bandit_data['summary']['LOW'] +
                 pylint_data['summary']['LOW'] +
                 flake8_data['summary']['LOW'])
    total_issues = total_high + total_medium + total_low
    
    status_text = _get_status_text(total_high, total_medium, total_low)
    
    report = ["## Security Report\n"]
    
    if total_issues == 0:
        report.append("**Status:** PASS - No security issues found\n")
    else:
        status_line = (
            f"**Status:** {status_text} - "
            f"{total_high} HIGH | {total_medium} MEDIUM | "
            f"{total_low} LOW issues found\n"
        )
        report.append(status_line)
    
    report.append("| Tool | HIGH | MEDIUM | LOW | Total |")
    report.append("|------|------|--------|-----|-------|")
    report.append(
        f"| Bandit | {bandit_data['summary']['HIGH']} | "
        f"{bandit_data['summary']['MEDIUM']} | {bandit_data['summary']['LOW']} | "
        f"{bandit_data['summary']['total']} |"
    )
    report.append(
        f"| Pylint | {pylint_data['summary']['HIGH']} | "
        f"{pylint_data['summary']['MEDIUM']} | {pylint_data['summary']['LOW']} | "
        f"{pylint_data['summary']['total']} |"
    )
    report.append(
        f"| Flake8 | {flake8_data['summary']['HIGH']} | "
        f"{flake8_data['summary']['MEDIUM']} | {flake8_data['summary']['LOW']} | "
        f"{flake8_data['summary']['total']} |"
    )
    report.append(
        f"| Safety | {safety_data['summary']['HIGH']} | "
        f"{safety_data['summary']['MEDIUM']} | {safety_data['summary']['LOW']} | "
        f"{safety_data['summary']['total']} |"
    )
    
    return "\n".join(report)


def find_existing_comment(pr: PullRequest) -> object:
    """Find existing security report comment."""
    try:
        comments = pr.get_issue_comments()
    except Exception:
        return None
    
    for comment in list(comments)[-20:]:
        if comment.body.startswith("## Security Report"):
            return comment
    
    return None


def post_security_report(pr: PullRequest, report: str) -> None:
    """Post or update security report comment to pull request."""
    try:
        existing_comment = find_existing_comment(pr)
        
        if existing_comment:
            existing_comment.edit(report)
            print("Updated existing security report comment")
        else:
            pr.create_issue_comment(report)
            print("Posted new security report comment")
    except GithubException as e:
        raise ValueError(f"Failed to post security report: {e}")


def _post_error_comment(pr: PullRequest, error_msg: str) -> None:
    """Post error comment to PR."""
    if not pr:
        return
    
    try:
        message = (
            f"## Security Report Failed\n\n"
            f"**Error:** {error_msg}\n\n"
            f"Check workflow logs for details."
        )
        pr.create_issue_comment(message)
    except Exception:
        pass


def main() -> None:
    """Run the complete security report process."""
    pr = None
    
    try:
        g, repo_name, pr_id = initialize()
        pr = get_pull_request(g, repo_name, pr_id)
        
        bandit_data = parse_bandit_json('bandit.json')
        pylint_data = parse_pylint_text('pylint.txt')
        flake8_data = parse_flake8_text('flake8.txt')
        safety_data = parse_safety_output('safety.json', 'safety.txt')
        
        has_high_severity = (
            bandit_data['summary']['HIGH'] > 0 or
            pylint_data['summary']['HIGH'] > 0 or
            safety_data['summary']['HIGH'] > 0
        )
        
        report = format_security_report(
            bandit_data, pylint_data, flake8_data, safety_data
        )
        post_security_report(pr, report)
        
        print("Security report posted successfully")
        
        if has_high_severity:
            print("WARNING: High severity security issues found!")
            sys.exit(1)
        
    except ValueError as e:
        _post_error_comment(pr, str(e))
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        _post_error_comment(pr, "Unexpected error occurred")
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
