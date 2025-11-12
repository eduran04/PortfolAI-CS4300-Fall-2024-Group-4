"""Security report automation for GitHub pull requests."""

import json
import os
import re
import sys
from github import Github, GithubException
from github.PullRequest import PullRequest


def initialize() -> tuple[Github, str, str]:
    """Initialize GitHub client and return it with repository info."""
    try:
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
        
    except Exception as e:
        raise


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
    
    try:
        if not os.path.exists(file_path):
            return {'issues': issues, 'summary': summary}
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
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
    except (json.JSONDecodeError, KeyError, IOError) as e:
        print(f"Warning: Failed to parse Bandit output: {e}")
    
    return {'issues': issues, 'summary': summary}


def parse_pylint_text(file_path: str) -> dict:
    """Parse Pylint text output and return structured data."""
    issues = []
    summary = {'HIGH': 0, 'MEDIUM': 0, 'LOW': 0, 'total': 0}
    
    try:
        if not os.path.exists(file_path):
            return {'issues': issues, 'summary': summary}
        
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Pylint format: file:line:type:message
        pattern = re.compile(r'^([^:]+):(\d+):\s*(\w+):\s*(.+)$')
        
        for line in lines:
            match = pattern.match(line.strip())
            if match:
                file_path, line_num, msg_type, message = match.groups()
                # Categorize by type: error=HIGH, warning=MEDIUM, convention=LOW
                if msg_type in ['error', 'fatal']:
                    severity = 'HIGH'
                    summary['HIGH'] += 1
                elif msg_type == 'warning':
                    severity = 'MEDIUM'
                    summary['MEDIUM'] += 1
                else:
                    severity = 'LOW'
                    summary['LOW'] += 1
                
                summary['total'] += 1
                
                issues.append({
                    'file': file_path.replace('portfolai/', ''),
                    'line': int(line_num),
                    'type': msg_type,
                    'message': message
                })
    except (IOError, ValueError) as e:
        print(f"Warning: Failed to parse Pylint output: {e}")
    
    return {'issues': issues, 'summary': summary}


def parse_flake8_text(file_path: str) -> dict:
    """Parse Flake8 text output and return structured data."""
    issues = []
    summary = {'HIGH': 0, 'MEDIUM': 0, 'LOW': 0, 'total': 0}
    
    try:
        if not os.path.exists(file_path):
            return {'issues': issues, 'summary': summary}
        
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Flake8 format: file:line:col:code:message
        pattern = re.compile(r'^([^:]+):(\d+):(\d+):\s*(\w+)\s+(.+)$')
        
        for line in lines:
            match = pattern.match(line.strip())
            if match:
                file_path, line_num, col_num, code, message = match.groups()
                # Most Flake8 issues are style (LOW), but some are errors (MEDIUM)
                if code.startswith('E9') or code.startswith('F'):
                    severity = 'MEDIUM'
                    summary['MEDIUM'] += 1
                else:
                    severity = 'LOW'
                    summary['LOW'] += 1
                
                summary['total'] += 1
                
                issues.append({
                    'file': file_path.replace('portfolai/', ''),
                    'line': int(line_num),
                    'col': int(col_num),
                    'code': code,
                    'message': message
                })
    except (IOError, ValueError) as e:
        print(f"Warning: Failed to parse Flake8 output: {e}")
    
    return {'issues': issues, 'summary': summary}


def parse_safety_output(file_path_json: str, file_path_txt: str) -> dict:
    """Parse Safety JSON or text output and return structured data."""
    issues = []
    summary = {'HIGH': 0, 'MEDIUM': 0, 'LOW': 0, 'total': 0}
    
    # Try JSON first
    if os.path.exists(file_path_json):
        try:
            with open(file_path_json, 'r', encoding='utf-8') as f:
                content = f.read()
                # Safety JSON might have extra text, try to extract JSON
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    data = json.loads(json_match.group())
                    for vuln in data.get('vulnerabilities', []):
                        summary['HIGH'] += 1
                        summary['total'] += 1
                        issues.append({
                            'package': vuln.get('package', ''),
                            'installed': vuln.get('installed_version', ''),
                            'vulnerable': vuln.get('vulnerable_spec', ''),
                            'advisory': vuln.get('advisory', '')
                        })
        except (json.JSONDecodeError, KeyError, IOError):
            pass
    
    # Fallback to text parsing
    if not issues and os.path.exists(file_path_txt):
        try:
            with open(file_path_txt, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            for line in lines:
                if '|' in line and 'package' not in line.lower():
                    parts = [p.strip() for p in line.split('|')]
                    if len(parts) >= 3:
                        summary['HIGH'] += 1
                        summary['total'] += 1
                        issues.append({
                            'package': parts[0] if len(parts) > 0 else '',
                            'installed': parts[1] if len(parts) > 1 else '',
                            'vulnerable': parts[2] if len(parts) > 2 else '',
                            'advisory': parts[3] if len(parts) > 3 else ''
                        })
        except IOError:
            pass
    
    return {'issues': issues, 'summary': summary}


def format_security_report(bandit_data: dict, pylint_data: dict, 
                          flake8_data: dict, safety_data: dict) -> str:
    """Format security report as markdown."""
    # Calculate totals
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
    
    # Status emoji
    if total_high > 0:
        status_emoji = "🔴"
    elif total_medium > 0:
        status_emoji = "⚠️"
    elif total_low > 0:
        status_emoji = "🟡"
    else:
        status_emoji = "✅"
    
    # Build report
    report = ["## Security Report\n"]
    
    if total_issues == 0:
        report.append("**Overall Status:** ✅ No security issues found\n")
    else:
        report.append(
            f"**Overall Status:** {status_emoji} "
            f"{total_high} HIGH | {total_medium} MEDIUM | {total_low} LOW issues found\n"
        )
    
    # Summary table
    report.append("### Summary")
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
    report.append("")
    
    # Bandit details
    if bandit_data['issues']:
        report.append("### Bandit Security Issues")
        report.append("| File | Line | Severity | Test ID | Issue |")
        report.append("|------|------|----------|---------|-------|")
        for issue in bandit_data['issues'][:50]:  # Limit to 50 issues
            file_name = issue['file'].split('/')[-1] if '/' in issue['file'] else issue['file']
            report.append(
                f"| `{file_name}` | {issue['line']} | {issue['severity']} | "
                f"{issue['test_id']} | {issue['issue'][:60]}... |"
            )
        if len(bandit_data['issues']) > 50:
            report.append(f"\n*... and {len(bandit_data['issues']) - 50} more issues*")
        report.append("")
    
    # Pylint details (top issues only)
    if pylint_data['issues']:
        high_issues = [i for i in pylint_data['issues'] if i.get('type') in ['error', 'fatal']]
        if high_issues:
            report.append("### Pylint Critical Issues")
            report.append("| File | Line | Type | Message |")
            report.append("|------|------|------|---------|")
            for issue in high_issues[:30]:
                file_name = issue['file'].split('/')[-1] if '/' in issue['file'] else issue['file']
                report.append(
                    f"| `{file_name}` | {issue['line']} | {issue['type']} | "
                    f"{issue['message'][:60]}... |"
                )
            report.append("")
    
    # Flake8 details (errors only)
    if flake8_data['issues']:
        error_issues = [i for i in flake8_data['issues'] 
                       if i.get('code', '').startswith(('E9', 'F'))]
        if error_issues:
            report.append("### Flake8 Error Issues")
            report.append("| File | Line | Code | Message |")
            report.append("|------|------|------|---------|")
            for issue in error_issues[:30]:
                file_name = issue['file'].split('/')[-1] if '/' in issue['file'] else issue['file']
                report.append(
                    f"| `{file_name}` | {issue['line']} | {issue['code']} | "
                    f"{issue['message'][:60]}... |"
                )
            report.append("")
    
    # Safety details
    if safety_data['issues']:
        report.append("### Safety Dependency Vulnerabilities")
        report.append("| Package | Installed | Vulnerable | Advisory |")
        report.append("|---------|-----------|------------|----------|")
        for issue in safety_data['issues']:
            report.append(
                f"| {issue['package']} | {issue['installed']} | "
                f"{issue['vulnerable']} | {issue['advisory'][:40]}... |"
            )
        report.append("")
    
    return "\n".join(report)


def find_existing_comment(pr: PullRequest) -> object:
    """Find existing security report comment."""
    try:
        comments = pr.get_issue_comments()
        for comment in list(comments)[-20:]:  # Check last 20 comments
            if comment.body.startswith("## Security Report"):
                return comment
    except Exception:
        pass
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


def main() -> None:
    """Run the complete security report process."""
    pr = None
    has_high_severity = False
    
    try:
        # Initialize
        g, repo_name, pr_id = initialize()
        
        # Get PR
        pr = get_pull_request(g, repo_name, pr_id)
        
        # Parse security tool outputs
        # Note: script runs from portfolai directory
        bandit_data = parse_bandit_json('bandit.json')
        pylint_data = parse_pylint_text('pylint.txt')
        flake8_data = parse_flake8_text('flake8.txt')
        safety_data = parse_safety_output('safety.json', 'safety.txt')
        
        # Check for high severity issues
        has_high_severity = (
            bandit_data['summary']['HIGH'] > 0 or
            pylint_data['summary']['HIGH'] > 0 or
            safety_data['summary']['HIGH'] > 0
        )
        
        # Format and post report
        report = format_security_report(bandit_data, pylint_data, flake8_data, safety_data)
        post_security_report(pr, report)
        
        print("Security report posted successfully")
        
        # Exit with error code if high severity issues found
        if has_high_severity:
            print("WARNING: High severity security issues found!")
            sys.exit(1)
        
    except ValueError as e:
        if pr:
            try:
                message = (
                    f"## Security Report Failed\n\n"
                    f"**Error:** {e}\n\n"
                    f"Check workflow logs for details."
                )
                pr.create_issue_comment(message)
            except Exception:
                pass
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        if pr:
            try:
                message = (
                    f"## Security Report Failed\n\n"
                    f"**Error:** Unexpected error occurred\n\n"
                    f"Check workflow logs for details."
                )
                pr.create_issue_comment(message)
            except Exception:
                pass
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

