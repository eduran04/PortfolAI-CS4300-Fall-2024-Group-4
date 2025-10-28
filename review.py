import os
from github import Github
from openai import OpenAI

def initialize():
    try:
        # Initialize OpenAI client
        client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

        # Get GitHub token and repository info from environment variables
        github_token = os.getenv('GITHUB_TOKEN')
        if not github_token:
            raise ValueError("GITHUB_TOKEN is not set")

        repo_name = os.getenv('GITHUB_REPOSITORY')
        if not repo_name:
            raise ValueError("GITHUB_REPOSITORY is not set")

        pr_id = os.getenv('GITHUB_PR_ID')
        if not pr_id:
            raise ValueError("GITHUB_PR_ID is not set")

        # Initialize Github instance
        g = Github(github_token)

        return client, g, repo_name, pr_id
    except Exception as e:
        raise ValueError(f"Failed to initialize: {e}")

def get_repo_and_pull_request(g, repo_name, pr_id):
    try:
        repo = g.get_repo(repo_name)
        pr = repo.get_pull(int(pr_id))
        return repo, pr
    except Exception as e:
        raise ValueError(f"Failed to fetch repo or pull request: {e}")

def fetch_files_from_pr(pr):
    try:
        files = pr.get_files()
        diff = ""
        for file in files:
            diff += f"File: {file.filename}\nChanges:\n{file.patch}\n\n"
        return diff
    except Exception as e:
        raise ValueError(f"Failed to fetch files from PR: {e}")

def request_code_review(diff, client):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system", 
                    "content": """Please review the following code and provide comprehensive feedback. 
                    Consider the following aspects:

                    **General Code Quality:**
                    - Code quality and adherence to best practices
                    - Potential bugs or edge cases
                    - Performance optimizations
                    - Readability and maintainability
                    - Security concerns

                    **Django/Python/JavaScript Specific Considerations:**
                    - Django framework best practices (proper use of ORM, views patterns, built-in features)
                    - Python standards compliance (PEP 8, type hints, docstrings)
                    - JavaScript best practices and modern patterns
                    - Error handling and input validation
                    - Code organization and separation of concerns

                    **Review Structure:**
                    For each suggestion, please provide:
                    - Specific issue identified
                    - Recommended improvement
                    - Clear explanation of why the change improves the code
                    - Code example if applicable

                    Focus on actionable feedback that will help improve code quality, maintainability, and adherence to industry standards.
                    Prioritize suggestions that address security vulnerabilities, performance issues, or maintainability concerns."""
                },
                {"role": "user", "content": f"Here's the code to review:\n\n{diff}"}
            ],
            max_completion_tokens=2048
        )
        return response.choices[0].message.content

    except Exception as e:
        raise ValueError(f"Failed to get code review from OpenAI: {e}")


def post_review_comments(pr, review_comments):
    try:
        pr.create_issue_comment(review_comments)
    except Exception as e:
        raise ValueError(f"Failed to post review comments: {e}")

def main():
    try:

        client, g, repo_name, pr_id = initialize()

        repo, pr = get_repo_and_pull_request(g, repo_name, pr_id)

        diff = fetch_files_from_pr(pr)

        review_comments = request_code_review(diff, client)

        post_review_comments(pr, review_comments)

        print("Code review posted successfully.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
