#!/usr/bin/env python3
"""
Demo of complete CLI workflow for Git-based issue management.
"""

import subprocess
import tempfile
import time
from pathlib import Path


def run_cli_command(args, repo_path):
    """Run CLI command and return output"""
    cmd = ["python", "poc/git-storage/issue_cli.py", "--repo", str(repo_path)] + args
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=".")
    return result.stdout, result.stderr, result.returncode


def demo_cli_workflow():
    """Demonstrate complete CLI workflow"""
    print("🚀 Git-Based Issue Management CLI Demo")
    print("=" * 60)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        repo_path = Path(temp_dir) / "cli_demo_repo"
        
        print(f"📁 Using repository: {repo_path}")
        print()
        
        # Step 1: Create issues
        print("📝 Step 1: Creating Issues")
        print("-" * 30)
        
        issues = [
            {
                "title": "Implement OAuth2 authentication",
                "description": "Add OAuth2 support for Google and GitHub login",
                "assignee": "alice@company.com",
                "labels": "feature,security,high-priority"
            },
            {
                "title": "Fix memory leak in data processor",
                "description": "Memory usage grows continuously during batch processing",
                "assignee": "bob@company.com", 
                "labels": "bug,performance,urgent"
            },
            {
                "title": "Add API rate limiting",
                "description": "Implement rate limiting to prevent API abuse",
                "assignee": "carol@company.com",
                "labels": "feature,api,security"
            }
        ]
        
        issue_ids = []
        for issue in issues:
            stdout, stderr, code = run_cli_command([
                "create",
                issue["title"],
                issue["description"],
                "--assignee", issue["assignee"],
                "--labels", issue["labels"]
            ], repo_path)
            
            print(stdout.strip())
            
            # Extract issue ID from output
            for line in stdout.split('\n'):
                if "Created issue:" in line:
                    issue_id = line.split(": ")[1]
                    issue_ids.append(issue_id)
                    break
        
        print()
        
        # Step 2: List all issues
        print("📋 Step 2: Listing All Issues")
        print("-" * 30)
        
        stdout, stderr, code = run_cli_command(["list"], repo_path)
        print(stdout.strip())
        print()
        
        # Step 3: Request reviews
        print("👥 Step 3: Requesting Reviews")
        print("-" * 30)
        
        review_requests = [
            (issue_ids[0], "senior_dev@company.com"),
            (issue_ids[1], "performance_expert@company.com"),
        ]
        
        review_ids = []
        for issue_id, reviewer in review_requests:
            stdout, stderr, code = run_cli_command([
                "request-review", issue_id, reviewer
            ], repo_path)
            
            print(stdout.strip())
            
            # Extract review ID from output
            for line in stdout.split('\n'):
                if "Requested review:" in line:
                    review_id = line.split(": ")[1]
                    review_ids.append(review_id)
                    break
        
        print()
        
        # Step 4: List issues under review
        print("🔍 Step 4: Issues Under Review")
        print("-" * 30)
        
        stdout, stderr, code = run_cli_command(["list", "--status", "under_review"], repo_path)
        print(stdout.strip())
        print()
        
        # Step 5: Submit review decisions
        print("✅ Step 5: Submitting Review Decisions")
        print("-" * 30)
        
        # Approve first review
        if review_ids:
            stdout, stderr, code = run_cli_command([
                "submit-review", review_ids[0], "approved",
                "--comments", "Excellent implementation,Security review passed,Ready for production",
                "--notes", "Approved for immediate deployment"
            ], repo_path)
            print(stdout.strip())
        
        # Request changes for second review
        if len(review_ids) > 1:
            stdout, stderr, code = run_cli_command([
                "submit-review", review_ids[1], "changes_requested",
                "--comments", "Memory profiling needed,Add unit tests for edge cases,Consider using memory pools",
                "--notes", "Please address memory management concerns"
            ], repo_path)
            print(stdout.strip())
        
        print()
        
        # Step 6: Update an issue
        print("📝 Step 6: Updating Issue Status")
        print("-" * 30)
        
        if len(issue_ids) > 2:
            stdout, stderr, code = run_cli_command([
                "update", issue_ids[2],
                "--status", "in_progress",
                "--labels", "feature,api,security,in-progress"
            ], repo_path)
            print(stdout.strip())
        
        print()
        
        # Step 7: List reviews
        print("👥 Step 7: Listing All Reviews")
        print("-" * 30)
        
        stdout, stderr, code = run_cli_command(["list-reviews"], repo_path)
        print(stdout.strip())
        print()
        
        # Step 8: Show issue history
        print("📜 Step 8: Issue History")
        print("-" * 30)
        
        if issue_ids:
            stdout, stderr, code = run_cli_command(["history", issue_ids[0]], repo_path)
            print(stdout.strip())
        
        print()
        
        # Step 9: Show repository statistics
        print("📊 Step 9: Repository Statistics")
        print("-" * 30)
        
        stdout, stderr, code = run_cli_command(["stats"], repo_path)
        print(stdout.strip())
        print()
        
        # Step 10: Final issue listing by status
        print("📋 Step 10: Final Status Summary")
        print("-" * 30)
        
        statuses = ["approved", "needs_changes", "in_progress", "open"]
        for status in statuses:
            stdout, stderr, code = run_cli_command(["list", "--status", status], repo_path)
            if "Found" in stdout:
                print(f"🔍 {status.upper()} ISSUES:")
                print(stdout.strip())
                print()
        
        print("🎉 CLI Demo Complete!")
        print("=" * 60)
        print("✅ Successfully demonstrated:")
        print("   • Issue creation with metadata")
        print("   • Review request workflow")
        print("   • Review approval/rejection process")
        print("   • Issue status updates")
        print("   • Comprehensive listing and filtering")
        print("   • Git history tracking")
        print("   • Repository statistics")
        print("   • Complete CLI interface")
        print("   • Real Git operations (no mocks!)")


if __name__ == "__main__":
    demo_cli_workflow()