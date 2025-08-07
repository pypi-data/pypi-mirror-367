#!/usr/bin/env python3
"""
Command-line interface for the real Git-based issue management system.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import List

from real_issue_manager import GitIssueManager


def create_issue(manager: GitIssueManager, args):
    """Create a new issue"""
    labels = args.labels.split(',') if args.labels else []
    
    issue = manager.create_issue(
        title=args.title,
        description=args.description,
        assignee=args.assignee,
        labels=labels
    )
    
    print(f"✅ Created issue: {issue.id}")
    print(f"   Title: {issue.title}")
    print(f"   Assignee: {issue.assignee}")
    print(f"   Labels: {', '.join(issue.labels)}")


def get_issue(manager: GitIssueManager, args):
    """Get issue details"""
    issue = manager.get_issue(args.issue_id)
    
    if not issue:
        print(f"❌ Issue {args.issue_id} not found")
        return
    
    print(f"📋 Issue: {issue.id}")
    print(f"   Title: {issue.title}")
    print(f"   Description: {issue.description}")
    print(f"   Status: {issue.status}")
    print(f"   Review Status: {issue.review_status}")
    print(f"   Assignee: {issue.assignee}")
    print(f"   Reviewer: {issue.reviewer}")
    print(f"   Labels: {', '.join(issue.labels)}")
    print(f"   Created: {issue.created_at}")
    print(f"   Updated: {issue.updated_at}")


def update_issue(manager: GitIssueManager, args):
    """Update an issue"""
    updates = {}
    
    if args.title:
        updates['title'] = args.title
    if args.description:
        updates['description'] = args.description
    if args.status:
        updates['status'] = args.status
    if args.assignee:
        updates['assignee'] = args.assignee
    if args.labels:
        updates['labels'] = args.labels.split(',')
    
    if not updates:
        print("❌ No updates specified")
        return
    
    issue = manager.update_issue(args.issue_id, **updates)
    
    if not issue:
        print(f"❌ Issue {args.issue_id} not found")
        return
    
    print(f"✅ Updated issue: {issue.id}")
    for key, value in updates.items():
        print(f"   {key}: {value}")


def list_issues(manager: GitIssueManager, args):
    """List issues"""
    issues = manager.list_issues(
        status=args.status,
        assignee=args.assignee
    )
    
    if not issues:
        print("📋 No issues found")
        return
    
    print(f"📋 Found {len(issues)} issue(s):")
    print()
    
    for issue in issues:
        status_icon = {
            'open': '🔓',
            'under_review': '👥',
            'approved': '✅',
            'rejected': '❌',
            'needs_changes': '🔄',
            'in_progress': '⚡',
            'closed': '🔒'
        }.get(issue.status, '❓')
        
        print(f"{status_icon} {issue.id}: {issue.title}")
        print(f"   Status: {issue.status} | Review: {issue.review_status}")
        print(f"   Assignee: {issue.assignee}")
        if issue.labels:
            print(f"   Labels: {', '.join(issue.labels)}")
        print()


def request_review(manager: GitIssueManager, args):
    """Request review for an issue"""
    review = manager.request_review(args.issue_id, args.reviewer)
    
    if not review:
        print(f"❌ Could not request review for issue {args.issue_id}")
        return
    
    print(f"✅ Requested review: {review.id}")
    print(f"   Issue: {args.issue_id}")
    print(f"   Reviewer: {args.reviewer}")


def submit_review(manager: GitIssueManager, args):
    """Submit a review decision"""
    comments = args.comments.split(',') if args.comments else []
    
    review = manager.submit_review(
        review_id=args.review_id,
        status=args.status,
        comments=comments,
        decision_notes=args.notes
    )
    
    if not review:
        print(f"❌ Review {args.review_id} not found")
        return
    
    print(f"✅ Submitted review: {review.id}")
    print(f"   Status: {review.status}")
    print(f"   Issue: {review.issue_id}")
    if comments:
        print(f"   Comments: {', '.join(comments)}")
    if args.notes:
        print(f"   Notes: {args.notes}")


def list_reviews(manager: GitIssueManager, args):
    """List reviews"""
    reviews = manager.list_reviews(
        issue_id=args.issue_id,
        reviewer=args.reviewer
    )
    
    if not reviews:
        print("👥 No reviews found")
        return
    
    print(f"👥 Found {len(reviews)} review(s):")
    print()
    
    for review in reviews:
        status_icon = {
            'pending': '⏳',
            'approved': '✅',
            'rejected': '❌',
            'changes_requested': '🔄'
        }.get(review.status, '❓')
        
        print(f"{status_icon} {review.id}: {review.status}")
        print(f"   Issue: {review.issue_id}")
        print(f"   Reviewer: {review.reviewer}")
        print(f"   Created: {review.created_at}")
        if review.reviewed_at:
            print(f"   Reviewed: {review.reviewed_at}")
        if review.comments:
            print(f"   Comments: {', '.join(review.comments)}")
        if review.decision_notes:
            print(f"   Notes: {review.decision_notes}")
        print()


def show_history(manager: GitIssueManager, args):
    """Show issue history"""
    history = manager.get_issue_history(args.issue_id)
    
    if not history:
        print(f"📜 No history found for issue {args.issue_id}")
        return
    
    print(f"📜 History for issue {args.issue_id}:")
    print()
    
    for entry in history:
        print(f"🔗 {entry['commit_hash'][:8]} - {entry['message']}")
        print(f"   Author: {entry['author_name']} <{entry['author_email']}>")
        print(f"   Date: {entry['date']}")
        print()


def show_stats(manager: GitIssueManager, args):
    """Show repository statistics"""
    stats = manager.get_repository_stats()
    
    print("📊 Repository Statistics:")
    print(f"   Path: {stats['repository_path']}")
    print(f"   Total Commits: {stats['total_commits']}")
    print(f"   Total Issues: {stats['total_issues']}")
    print(f"   Total Reviews: {stats['total_reviews']}")
    
    if 'latest_commit' in stats and stats['latest_commit']['hash']:
        latest = stats['latest_commit']
        print(f"   Latest Commit: {latest['hash'][:8]} - {latest['message']}")
        print(f"   Author: {latest['author']}")
        print(f"   Date: {latest['date']}")


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Git-based Issue Management System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create an issue
  %(prog)s create "Fix login bug" "Users cannot login with special characters" --assignee alice@company.com --labels bug,urgent
  
  # List open issues
  %(prog)s list --status open
  
  # Request review
  %(prog)s request-review issue_12345678 senior@company.com
  
  # Submit review
  %(prog)s submit-review review_87654321 approved --comments "Looks good,Ready to deploy" --notes "Approved for production"
  
  # Show issue history
  %(prog)s history issue_12345678
        """
    )
    
    parser.add_argument(
        '--repo', '-r',
        default='./issue_repo',
        help='Path to Git repository (default: ./issue_repo)'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Create issue
    create_parser = subparsers.add_parser('create', help='Create a new issue')
    create_parser.add_argument('title', help='Issue title')
    create_parser.add_argument('description', help='Issue description')
    create_parser.add_argument('--assignee', help='Issue assignee email')
    create_parser.add_argument('--labels', help='Comma-separated labels')
    
    # Get issue
    get_parser = subparsers.add_parser('get', help='Get issue details')
    get_parser.add_argument('issue_id', help='Issue ID')
    
    # Update issue
    update_parser = subparsers.add_parser('update', help='Update an issue')
    update_parser.add_argument('issue_id', help='Issue ID')
    update_parser.add_argument('--title', help='New title')
    update_parser.add_argument('--description', help='New description')
    update_parser.add_argument('--status', help='New status')
    update_parser.add_argument('--assignee', help='New assignee')
    update_parser.add_argument('--labels', help='New labels (comma-separated)')
    
    # List issues
    list_parser = subparsers.add_parser('list', help='List issues')
    list_parser.add_argument('--status', help='Filter by status')
    list_parser.add_argument('--assignee', help='Filter by assignee')
    
    # Request review
    review_parser = subparsers.add_parser('request-review', help='Request review for an issue')
    review_parser.add_argument('issue_id', help='Issue ID')
    review_parser.add_argument('reviewer', help='Reviewer email')
    
    # Submit review
    submit_parser = subparsers.add_parser('submit-review', help='Submit review decision')
    submit_parser.add_argument('review_id', help='Review ID')
    submit_parser.add_argument('status', choices=['approved', 'rejected', 'changes_requested'], help='Review status')
    submit_parser.add_argument('--comments', help='Review comments (comma-separated)')
    submit_parser.add_argument('--notes', help='Decision notes')
    
    # List reviews
    reviews_parser = subparsers.add_parser('list-reviews', help='List reviews')
    reviews_parser.add_argument('--issue-id', help='Filter by issue ID')
    reviews_parser.add_argument('--reviewer', help='Filter by reviewer')
    
    # Show history
    history_parser = subparsers.add_parser('history', help='Show issue history')
    history_parser.add_argument('issue_id', help='Issue ID')
    
    # Show stats
    stats_parser = subparsers.add_parser('stats', help='Show repository statistics')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialize issue manager
    try:
        manager = GitIssueManager(args.repo)
    except Exception as e:
        print(f"❌ Error initializing repository: {e}")
        sys.exit(1)
    
    # Execute command
    try:
        if args.command == 'create':
            create_issue(manager, args)
        elif args.command == 'get':
            get_issue(manager, args)
        elif args.command == 'update':
            update_issue(manager, args)
        elif args.command == 'list':
            list_issues(manager, args)
        elif args.command == 'request-review':
            request_review(manager, args)
        elif args.command == 'submit-review':
            submit_review(manager, args)
        elif args.command == 'list-reviews':
            list_reviews(manager, args)
        elif args.command == 'history':
            show_history(manager, args)
        elif args.command == 'stats':
            show_stats(manager, args)
        else:
            print(f"❌ Unknown command: {args.command}")
            sys.exit(1)
    
    except Exception as e:
        print(f"❌ Error executing command: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()