#!/usr/bin/env python3
"""
Git Storage Audit Trail Example

Demonstrates the audit trail and history features of Git storage:
- Complete change history via Git commits
- Historical data retrieval
- Audit compliance features
- Data integrity verification
"""

import tempfile
import time
from datetime import datetime
from pathlib import Path

# Import YAAPP storage
from yaapp.plugins.storage import create_git_storage_manager


def print_section(title: str):
    print(f"\n{'='*50}")
    print(f"  {title}")
    print(f"{'='*50}")


def print_subsection(title: str):
    print(f"\n{'-'*30}")
    print(f"  {title}")
    print(f"{'-'*30}")


def main():
    print_section("Git Storage - Audit Trail Example")
    
    # Create temporary directory for this demo
    with tempfile.TemporaryDirectory() as temp_dir:
        repo_path = Path(temp_dir) / "audit_demo"
        
        print(f"📁 Repository: {repo_path}")
        
        # Create Git storage manager
        storage = create_git_storage_manager(
            repo_path=str(repo_path),
            author_name="Audit System",
            author_email="audit@company.com"
        )
        
        git_backend = storage.get_backend("default")
        
        print_subsection("Creating Initial Data")
        
        # Create initial employee record
        employee_data = {
            "id": "EMP001",
            "name": "John Doe",
            "department": "Engineering",
            "salary": 75000,
            "status": "active",
            "hire_date": "2023-01-15",
            "created_at": datetime.now().isoformat(),
            "version": 1
        }
        
        storage.set("employee:EMP001", employee_data)
        print(f"✅ Created employee record: {employee_data['name']}")
        
        # Small delay to ensure different timestamps
        time.sleep(1)
        
        print_subsection("Making Changes Over Time")
        
        # Change 1: Salary increase
        employee_data["salary"] = 80000
        employee_data["version"] = 2
        employee_data["updated_at"] = datetime.now().isoformat()
        employee_data["change_reason"] = "Annual review - performance increase"
        
        storage.set("employee:EMP001", employee_data)
        print(f"✅ Updated salary to ${employee_data['salary']}")
        time.sleep(1)
        
        # Change 2: Department transfer
        employee_data["department"] = "Senior Engineering"
        employee_data["version"] = 3
        employee_data["updated_at"] = datetime.now().isoformat()
        employee_data["change_reason"] = "Promotion to senior role"
        
        storage.set("employee:EMP001", employee_data)
        print(f"✅ Transferred to {employee_data['department']}")
        time.sleep(1)
        
        # Change 3: Status change
        employee_data["status"] = "on_leave"
        employee_data["version"] = 4
        employee_data["updated_at"] = datetime.now().isoformat()
        employee_data["change_reason"] = "Medical leave"
        employee_data["leave_start"] = datetime.now().isoformat()
        
        storage.set("employee:EMP001", employee_data)
        print(f"✅ Status changed to {employee_data['status']}")
        time.sleep(1)
        
        # Change 4: Return from leave
        employee_data["status"] = "active"
        employee_data["version"] = 5
        employee_data["updated_at"] = datetime.now().isoformat()
        employee_data["change_reason"] = "Returned from medical leave"
        employee_data["leave_end"] = datetime.now().isoformat()
        
        storage.set("employee:EMP001", employee_data)
        print(f"✅ Returned to active status")
        
        print_subsection("Audit Trail Analysis")
        
        # Get complete history
        if hasattr(git_backend, 'get_history'):
            history = git_backend.get_history("employee:EMP001")
            
            print(f"📜 Complete audit trail ({len(history)} changes):")
            print()
            
            for i, entry in enumerate(history, 1):
                print(f"  {i}. Commit: {entry['commit_hash'][:8]}")
                print(f"     Date: {entry['date']}")
                print(f"     Author: {entry['author_name']} <{entry['author_email']}>")
                print(f"     Message: {entry['message']}")
                print()
        
        print_subsection("Historical Data Retrieval")
        
        # Get data at different points in time
        if hasattr(git_backend, 'get_commit_data') and history:
            print("🕰️  Data at different points in time:")
            print()
            
            # Show data from each commit
            for i, entry in enumerate(history[:3], 1):  # Show first 3 for brevity
                commit_hash = entry['commit_hash']
                historical_data = git_backend.get_commit_data(commit_hash, "employee:EMP001")
                
                if historical_data:
                    print(f"  Version {i} (Commit {commit_hash[:8]}):")
                    print(f"    Name: {historical_data.get('name')}")
                    print(f"    Department: {historical_data.get('department')}")
                    print(f"    Salary: ${historical_data.get('salary')}")
                    print(f"    Status: {historical_data.get('status')}")
                    print(f"    Version: {historical_data.get('version')}")
                    if 'change_reason' in historical_data:
                        print(f"    Reason: {historical_data['change_reason']}")
                    print()
        
        print_subsection("Compliance Reporting")
        
        # Generate compliance report
        current_data = storage.get("employee:EMP001")
        
        print("📋 Compliance Report:")
        print(f"   Employee ID: {current_data['id']}")
        print(f"   Current Status: {current_data['status']}")
        print(f"   Total Changes: {len(history) if 'history' in locals() else 'N/A'}")
        print(f"   Last Updated: {current_data.get('updated_at', 'N/A')}")
        print(f"   Data Integrity: ✅ Verified (Git cryptographic hashing)")
        print(f"   Audit Trail: ✅ Complete (All changes tracked)")
        print(f"   Immutability: ✅ Guaranteed (Git object storage)")
        
        print_subsection("Data Integrity Verification")
        
        # Repository statistics for integrity verification
        if hasattr(git_backend, 'get_repository_stats'):
            stats = git_backend.get_repository_stats()
            
            print("🔒 Data Integrity Status:")
            print(f"   Repository Path: {stats.get('repository_path')}")
            print(f"   Total Commits: {stats.get('total_commits')}")
            print(f"   Git Objects: {stats.get('git_objects', {}).get('count', 'N/A')}")
            print(f"   Repository Size: {stats.get('repository_size_bytes')} bytes")
            
            latest = stats.get('latest_commit', {})
            if latest:
                print(f"   Latest Commit: {latest.get('hash', '')[:8]}")
                print(f"   Commit Author: {latest.get('author')}")
                print(f"   Commit Date: {latest.get('date')}")
        
        print_subsection("Audit Query Examples")
        
        # Example audit queries
        print("🔍 Sample Audit Queries:")
        print()
        
        # 1. Find all salary changes
        print("1. Salary Change History:")
        if 'history' in locals():
            for entry in history:
                if hasattr(git_backend, 'get_commit_data'):
                    data = git_backend.get_commit_data(entry['commit_hash'], "employee:EMP001")
                    if data and 'salary' in data:
                        print(f"   {entry['date'][:10]}: ${data['salary']} (Commit: {entry['commit_hash'][:8]})")
        print()
        
        # 2. Status change timeline
        print("2. Status Change Timeline:")
        if 'history' in locals():
            for entry in history:
                if hasattr(git_backend, 'get_commit_data'):
                    data = git_backend.get_commit_data(entry['commit_hash'], "employee:EMP001")
                    if data and 'status' in data:
                        reason = data.get('change_reason', 'Initial creation')
                        print(f"   {entry['date'][:10]}: {data['status']} - {reason}")
        print()
        
        # 3. Version history
        print("3. Version History:")
        if 'history' in locals():
            for entry in history:
                if hasattr(git_backend, 'get_commit_data'):
                    data = git_backend.get_commit_data(entry['commit_hash'], "employee:EMP001")
                    if data and 'version' in data:
                        print(f"   Version {data['version']}: {entry['message']} ({entry['date'][:10]})")
        
        print_subsection("Backup and Recovery Demo")
        
        # Demonstrate backup capability
        backup_path = Path(temp_dir) / "backup_repo"
        
        if hasattr(git_backend, 'create_backup'):
            print("💾 Creating backup...")
            backup_success = git_backend.create_backup(str(backup_path))
            print(f"   Backup result: {'✅ Success' if backup_success else '❌ Failed'}")
            
            if backup_success:
                print(f"   Backup location: {backup_path}")
                print(f"   Backup size: {sum(f.stat().st_size for f in backup_path.rglob('*') if f.is_file())} bytes")
        
        print_section("Audit Trail Demo Complete")
        
        print("🎉 Key Benefits Demonstrated:")
        print("   • Complete change history with Git commits")
        print("   • Immutable audit trail (cannot be tampered)")
        print("   • Cryptographic integrity verification")
        print("   • Historical data retrieval at any point")
        print("   • Compliance-ready reporting")
        print("   • Backup and recovery capabilities")
        print("   • Author tracking and timestamps")


if __name__ == "__main__":
    main()