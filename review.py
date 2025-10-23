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
                    "content": """Yo! Let's make review.py actually readable because we're gonna have to present this code and I don't want the professor roasting us 💀

                    We're learning Django/Python/JS and want to write code that doesn't look like we threw it together at 3am in the library (even if we did). Let's refactor this to follow actual software standards so we can flex our skills and maybe put this on our portfolio without cringing.

                    **Django Stuff - Let's Not Reinvent The Wheel:**
                    - Use Django's built-in features fr fr (forms, validators, all that)
                    - Fat Models, Thin Views - basically put the logic where it belongs
                    - Use the ORM properly so we're not just raw-dogging SQL queries
                    - Class-based views or function-based views - whichever makes more sense (no cap, sometimes simple is better)

                    **Make The Code Make Sense:**
                    - Add comments that actually help - not "this is a variable" type beat
                    - Name things properly so we remember what they do next week
                    - Break up functions that are doing way too much
                    - Type hints would be cool so VSCode stops yelling at us
                    - Follow PEP 8 because the linter won't stop complaining otherwise

                    **Error Handling - Because Stuff Breaks:**
                    - Add try/except blocks so the whole app doesn't crash when something goes wrong
                    - Print/log actual helpful error messages
                    - Validate user input (never trust users bestie)
                    - Handle edge cases we didn't think about at first

                    **Organization - Clean Room Energy:**
                    - Separate different concerns - don't mix everything together like a messy closet
                    - Extract magic numbers into constants with actual names
                    - Remove commented-out code and random print statements we left for debugging
                    - Organize imports at the top like we're supposed to
                    - Add docstrings so we remember what functions do when we review for finals
                    
                    **The College Student Special:**
                    - Make it easy to understand for when we're explaining it in our presentation
                    - Structure it so adding new features later won't be a nightmare
                    - Comment the tricky parts so we can explain our thought process
                    - Make sure it's something we'd be proud to show in a portfolio or interview
                    
                    Show me the refactored code with comments on what you changed and why. Don't go crazy with over-engineering - 
                    we want good code, not a 10-page class diagram. Keep it real but make it professional. Let's goooo"""
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
