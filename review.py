"""AI-powered code review automation for GitHub pull requests."""

import os
from github import Github, GithubException
from github.PullRequest import PullRequest
from openai import OpenAI, OpenAIError

# Configuration
MAX_FILES = 30
SYSTEM_PROMPT = """Please review the following code and provide comprehensive feedback. 
Consider the following aspects:

**General Code Quality:**
- Code quality and adherence to best practices
- Potential bugs or edge cases
- Performance optimizations
- Readability and maintainability

**Security Considerations:**
Pay special attention to security vulnerabilities including:
- Input validation and sanitization
- Authentication and authorization mechanisms
- SQL injection prevention (proper ORM usage)
- XSS and CSRF protection (Django-specific)
- Sensitive data handling and exposure
- Dependency vulnerabilities

**Django/Python/JavaScript Specific Considerations:**
- Django framework best practices (proper use of ORM, views patterns, built-in features)
- Python standards compliance (PEP 8, type hints, docstrings)
- JavaScript best practices and modern patterns
- Error handling and input validation
- Code organization and separation of concerns

**Review Structure:**
For each suggestion, please provide:
- Specific issue identified with line references when applicable
- Recommended improvement with clear explanation
- Code example showing before/after implementation
- Security implications if applicable

Focus on actionable feedback that will help improve code quality, maintainability, and adherence to industry standards.
Prioritize suggestions that address security vulnerabilities, performance issues, or maintainability concerns.

You are a stern and experienced senior developer.

**Scoring:**
At the end of your review, provide an overall code quality score out of 10, considering all the aspects mentioned above."""


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


def request_code_review(diff: str, client: OpenAI) -> str:
    """Get code review from OpenAI for the provided diff."""
    if not diff.strip():
        raise ValueError("Cannot review empty diff")
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Here's the code to review:\n\n{diff}"}
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
        
        # Get PR
        pr = get_pull_request(g, repo_name, pr_id)
        
        # Get changes
        diff = fetch_files_from_pr(pr)
        
        # Get review
        review = request_code_review(diff, client)
        
        # Post review
        post_review(pr, review)
        
        print("Code review posted successfully")
        
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