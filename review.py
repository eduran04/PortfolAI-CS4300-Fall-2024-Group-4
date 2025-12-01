"""AI-powered code review automation for GitHub pull requests."""

import os
import re
from github import Github, GithubException
from github.PullRequest import PullRequest
from openai import OpenAI, OpenAIError

# Configuration
MAX_FILES = 30
WORKFLOW_DIR = ".github/workflows"

SYSTEM_PROMPT = """Review the code and provide actionable feedback. Focus on:

**Code Quality:**
- Bugs, edge cases, performance issues
- Readability and maintainability
- Best practices for Django/Python/JavaScript

**Security:**
- Input validation and sanitization
- SQL injection, XSS, CSRF protection
- Sensitive data exposure
- Issues flagged by Bandit scanner

**Testing:**
- Test coverage (target 80%+)
- Missing tests for new code
- Proper mocking and edge cases

**Format:**
For each issue, provide: line reference, clear explanation, and code example if helpful. 
Prioritize security, bugs, and test coverage gaps.

End with a code quality score (0-10) and whether it will pass CI/CD checks."""


def initialize() -> tuple[OpenAI, Github, str, str]:
    """Initialize OpenAI and GitHub clients and return them with repository info."""
    try:
        openai_key = os.getenv('OPENAI_API_KEY')
        if not openai_key:
            raise ValueError("OPENAI_API_KEY is not set")
        
        github_token = os.getenv('GITHUB_TOKEN')
        if not github_token:
            raise ValueError("GITHUB_TOKEN is not set")
        
        repo_name = os.getenv('GITHUB_REPOSITORY')
        if not repo_name:
            raise ValueError("GITHUB_REPOSITORY is not set")
        
        pr_id = os.getenv('GITHUB_PR_ID')
        if not pr_id:
            raise ValueError("GITHUB_PR_ID is not set")
        
        client = OpenAI(api_key=openai_key)
        g = Github(github_token)
        
        return client, g, repo_name, pr_id
        
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


def _extract_coverage_info(comment_body: str) -> list[str]:
    """Extract coverage information from a comment."""
    context = []
    
    coverage_match = re.search(r'(\d+\.?\d*)%', comment_body)
    if not coverage_match:
        return context
    
    coverage_pct = coverage_match.group(1)
    context.append(f"**Test Coverage:** {coverage_pct}% (from workflow comment)")
    
    try:
        if float(coverage_pct) < 80:
            context.append("WARNING: Coverage is below 80% threshold!")
    except ValueError:
        pass
    
    lines = comment_body.split('\n')
    keywords = ['coverage', 'missing', 'total', 'fail']
    relevant_lines = [line for line in lines 
                     if any(keyword in line.lower() for keyword in keywords)]
    
    if relevant_lines:
        context.append(f"Coverage details: {'; '.join(relevant_lines[:3])}")
    
    return context


def _get_coverage_from_comments(pr: PullRequest) -> list[str]:
    """Get coverage information from PR comments."""
    try:
        comments = pr.get_issue_comments()
        for comment in list(comments)[-10:]:
            body = comment.body.lower()
            if not ("coverage" in body or "pytest" in body or "test coverage" in body):
                continue
            return _extract_coverage_info(comment.body)
    except Exception:
        pass
    return []


def _get_workflow_status(repo, branch: str) -> list[str]:
    """Get workflow run status for a branch."""
    context = []
    try:
        runs = repo.get_workflow_runs(branch=branch)
        for run in list(runs)[:3]:
            if run.status != "completed":
                continue
            workflow_name = run.name
            if run.conclusion == "failure":
                context.append(f"FAILED: Workflow '{workflow_name}' failed")
            elif run.conclusion == "success":
                context.append(f"PASSED: Workflow '{workflow_name}' passed")
    except Exception:
        pass
    return context


def fetch_workflow_results(pr: PullRequest, repo) -> str:
    """Fetch workflow run results and coverage/security information from PR comments."""
    workflow_context = []
    
    coverage_info = _get_coverage_from_comments(pr)
    workflow_context.extend(coverage_info)
    
    workflow_status = _get_workflow_status(repo, pr.head.ref)
    workflow_context.extend(workflow_status)
    
    if not workflow_context:
        return None
    
    return "\n".join(workflow_context)


def fetch_files_from_pr(pr: PullRequest) -> str:
    """Fetch and format file changes from pull request."""
    try:
        files = pr.get_files()
        total_files = files.totalCount
        
        # Validate file count
        if total_files == 0:
            raise ValueError("PR has no file changes")
        if total_files > MAX_FILES:
            raise ValueError(f"PR has {total_files} files (max {MAX_FILES}). Split into smaller PRs.")
        
        # Collect file changes
        diff_parts = []
        for file in files:
            # Only include files with actual changes (patch can be None)
            if file.patch:
                diff_parts.append(f"File: {file.filename}\nChanges:\n{file.patch}\n")
        
        if not diff_parts:
            raise ValueError("No reviewable files found")
        
        diff = "\n".join(diff_parts)
        
        # Simple size check (approximate 400k chars ~= 100k tokens)
        if len(diff) > 400000:
            raise ValueError("Changes too large. Split into smaller PRs.")
        
        return diff
        
    except GithubException as e:
        raise ValueError(f"Failed to fetch files: {e}")


def request_code_review(diff: str, client: OpenAI, workflow_results: str = None) -> str:
    """Get code review from OpenAI for the provided diff."""
    if not diff.strip():
        raise ValueError("Cannot review empty diff")
    
    # Build user message with workflow context if available
    user_content = f"Here's the code to review:\n\n{diff}"
    if workflow_results:
        user_content += f"\n\n**ACTUAL WORKFLOW RESULTS:**\n{workflow_results}\n\n"
        user_content += "Please reference these actual results in your review. If coverage is below 80%, identify which parts of the code need tests. If workflows failed, address the specific issues."
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_content}
            ],
            max_completion_tokens=2048,
            timeout=60.0
        )
        
        review = response.choices[0].message.content
        
        # Validate response
        if not review or len(review) < 50:
            raise ValueError("Received insufficient review")
        
        return review
        
    except OpenAIError as e:
        raise ValueError(f"OpenAI error: {e}")


def post_review(pr: PullRequest, review: str) -> None:
    """Post review comment to pull request."""
    try:
        comment = f"## Automated Code Review\n\n{review}"
        pr.create_issue_comment(comment)
    except GithubException as e:
        raise ValueError(f"Failed to post review: {e}")


def post_error(pr: PullRequest, error: str) -> None:
    """Post error message to pull request."""
    try:
        message = (
            f"## Automated Code Review Failed\n\n"
            f"**Error:** {error}\n\n"
            f"Check workflow logs for details."
        )
        pr.create_issue_comment(message)
    except Exception:
        pass


def main() -> None:
    """Run the complete code review process."""
    pr = None
    
    try:
        # Initialize
        client, g, repo_name, pr_id = initialize()
        
        # Get PR and repo
        pr = get_pull_request(g, repo_name, pr_id)
        repo = g.get_repo(repo_name)
        
        # Get changes
        diff = fetch_files_from_pr(pr)
        
        # Fetch workflow results (coverage, security, etc.)
        workflow_results = fetch_workflow_results(pr, repo)
        
        # Get review (with workflow context if available)
        review = request_code_review(diff, client, workflow_results)
        
        # Post review
        post_review(pr, review)
        
        print("Code review posted successfully")
        if workflow_results:
            print("Workflow results included in review")
        
    except ValueError as e:
        if pr:
            post_error(pr, str(e))
        print(f"Error: {e}")
        exit(1)
    except Exception as e:
        if pr:
            post_error(pr, "Unexpected error occurred")
        print(f"Error: {e}")
        exit(1)


if __name__ == "__main__":
    main()