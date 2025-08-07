#!/usr/bin/env python3
"""
Simple test to verify the Git storage concept without external dependencies.
This demonstrates the core logic and data structures.
"""

import json
import tempfile
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, asdict


@dataclass
class StorageResult:
    """Result wrapper for storage operations"""
    success: bool
    data: Any = None
    error: str = None
    commit_hash: str = None
    blob_hash: str = None


class MockGitStorage:
    """Mock implementation of Git storage for testing without pygit2"""
    
    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
        self.repo_path.mkdir(parents=True, exist_ok=True)
        
        # Mock storage using files
        self.objects_dir = self.repo_path / "objects"
        self.objects_dir.mkdir(exist_ok=True)
        
        self.refs_dir = self.repo_path / "refs"
        self.refs_dir.mkdir(exist_ok=True)
        
        # In-memory cache
        self._cache = {}
        self._commit_counter = 0
        
    def _generate_hash(self, data: str) -> str:
        """Generate mock hash for data"""
        import hashlib
        return hashlib.sha256(data.encode()).hexdigest()[:40]
    
    def _create_blob(self, data: str) -> str:
        """Create blob object (mock)"""
        blob_hash = self._generate_hash(data)
        blob_file = self.objects_dir / blob_hash
        blob_file.write_text(data)
        return blob_hash
    
    def _create_commit(self, message: str, blob_hash: str) -> str:
        """Create commit object (mock)"""
        self._commit_counter += 1
        commit_data = {
            "message": message,
            "blob": blob_hash,
            "timestamp": datetime.now().isoformat(),
            "author": "test_user",
            "commit_id": self._commit_counter
        }
        
        commit_hash = self._generate_hash(json.dumps(commit_data))
        commit_file = self.objects_dir / f"commit_{commit_hash}"
        commit_file.write_text(json.dumps(commit_data, indent=2))
        
        # Update HEAD
        head_file = self.refs_dir / "HEAD"
        head_file.write_text(commit_hash)
        
        return commit_hash
    
    def store(self, key: str, data: Any, metadata: Optional[Dict] = None) -> StorageResult:
        """Store data as mock Git objects"""
        try:
            storage_data = {
                'key': key,
                'data': data,
                'metadata': metadata or {},
                'timestamp': datetime.now().isoformat(),
                'version': 1
            }
            
            # Serialize and create blob
            serialized = json.dumps(storage_data, default=str, indent=2)
            blob_hash = self._create_blob(serialized)
            
            # Create commit
            commit_hash = self._create_commit(f"Store: {key}", blob_hash)
            
            # Update cache
            self._cache[key] = storage_data
            
            return StorageResult(
                success=True,
                data=storage_data,
                commit_hash=commit_hash,
                blob_hash=blob_hash
            )
            
        except Exception as e:
            return StorageResult(success=False, error=str(e))
    
    def retrieve(self, key: str) -> StorageResult:
        """Retrieve data from mock Git objects"""
        try:
            # Check cache first
            if key in self._cache:
                return StorageResult(success=True, data=self._cache[key])
            
            # Search through objects (simplified)
            for obj_file in self.objects_dir.glob("*"):
                if obj_file.name.startswith("commit_"):
                    continue
                
                try:
                    content = obj_file.read_text()
                    storage_data = json.loads(content)
                    
                    if storage_data.get('key') == key:
                        self._cache[key] = storage_data
                        return StorageResult(success=True, data=storage_data, blob_hash=obj_file.name)
                except:
                    continue
            
            return StorageResult(success=False, error=f"Key '{key}' not found")
            
        except Exception as e:
            return StorageResult(success=False, error=str(e))
    
    def list_keys(self) -> StorageResult:
        """List all keys in storage"""
        try:
            keys = []
            
            for obj_file in self.objects_dir.glob("*"):
                if obj_file.name.startswith("commit_"):
                    continue
                
                try:
                    content = obj_file.read_text()
                    storage_data = json.loads(content)
                    key = storage_data.get('key')
                    if key:
                        keys.append(key)
                except:
                    continue
            
            return StorageResult(success=True, data=sorted(set(keys)))
            
        except Exception as e:
            return StorageResult(success=False, error=str(e))
    
    def get_stats(self) -> StorageResult:
        """Get storage statistics"""
        try:
            stats = {
                'repository_path': str(self.repo_path),
                'total_objects': len(list(self.objects_dir.glob("*"))),
                'cache_size': len(self._cache),
                'total_commits': self._commit_counter
            }
            
            return StorageResult(success=True, data=stats)
            
        except Exception as e:
            return StorageResult(success=False, error=str(e))


@dataclass
class Issue:
    """Issue entity for testing"""
    id: str
    title: str
    description: str
    status: str = "open"
    review_status: str = "not_required"
    assignee: Optional[str] = None
    reviewer: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.updated_at:
            self.updated_at = datetime.now().isoformat()


class MockIssueManager:
    """Issue management using mock Git storage"""
    
    def __init__(self, storage: MockGitStorage):
        self.storage = storage
    
    def create_issue(self, title: str, description: str, **kwargs) -> StorageResult:
        """Create new issue"""
        import uuid
        issue_id = f"issue_{uuid.uuid4().hex[:8]}"
        
        issue = Issue(
            id=issue_id,
            title=title,
            description=description,
            **kwargs
        )
        
        return self.storage.store(issue_id, asdict(issue), {'type': 'issue'})
    
    def get_issue(self, issue_id: str) -> StorageResult:
        """Get issue by ID"""
        return self.storage.retrieve(issue_id)
    
    def request_review(self, issue_id: str, reviewer: str) -> StorageResult:
        """Request review for issue"""
        import uuid
        
        # Update issue status
        issue_result = self.storage.retrieve(issue_id)
        if not issue_result.success:
            return issue_result
        
        issue_data = issue_result.data['data']
        issue_data['status'] = 'under_review'
        issue_data['review_status'] = 'pending'
        issue_data['reviewer'] = reviewer
        issue_data['updated_at'] = datetime.now().isoformat()
        
        # Update issue
        self.storage.store(issue_id, issue_data, {'type': 'issue'})
        
        # Create review record
        review_id = f"review_{uuid.uuid4().hex[:8]}"
        review_data = {
            'id': review_id,
            'issue_id': issue_id,
            'reviewer': reviewer,
            'status': 'pending',
            'comments': [],
            'created_at': datetime.now().isoformat()
        }
        
        return self.storage.store(review_id, review_data, {'type': 'review'})
    
    def submit_review(self, review_id: str, status: str, comments: List[str] = None, decision_notes: str = None) -> StorageResult:
        """Submit review decision"""
        # Get review
        review_result = self.storage.retrieve(review_id)
        if not review_result.success:
            return review_result
        
        review_data = review_result.data['data']
        review_data['status'] = status
        review_data['comments'] = comments or []
        review_data['decision_notes'] = decision_notes
        
        if status in ['approved', 'rejected']:
            review_data['approved_at'] = datetime.now().isoformat()
        
        # Update review
        review_result = self.storage.store(review_id, review_data, {'type': 'review'})
        if not review_result.success:
            return review_result
        
        # Update issue based on review
        issue_id = review_data['issue_id']
        issue_result = self.storage.retrieve(issue_id)
        if issue_result.success:
            issue_data = issue_result.data['data']
            if status == 'approved':
                issue_data['review_status'] = 'approved'
                issue_data['status'] = 'approved'
            elif status == 'rejected':
                issue_data['review_status'] = 'rejected'
                issue_data['status'] = 'needs_changes'
            
            issue_data['updated_at'] = datetime.now().isoformat()
            self.storage.store(issue_id, issue_data, {'type': 'issue'})
        
        return review_result


def run_tests():
    """Run simple tests to verify the concept"""
    print("🧪 Running Git Storage Concept Tests")
    print("=" * 50)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Initialize storage
        storage = MockGitStorage(tmpdir)
        issue_manager = MockIssueManager(storage)
        
        tests_passed = 0
        tests_failed = 0
        
        def test(name: str, condition: bool, details: str = ""):
            nonlocal tests_passed, tests_failed
            if condition:
                print(f"✅ {name}")
                if details:
                    print(f"   {details}")
                tests_passed += 1
            else:
                print(f"❌ {name}")
                if details:
                    print(f"   {details}")
                tests_failed += 1
        
        # Test 1: Basic storage operations
        print("\n📦 Testing Basic Storage Operations")
        
        # Store data
        result = storage.store("test_key", {"name": "Alice", "role": "admin"})
        test("Store operation", result.success, f"Commit: {result.commit_hash[:8]}...")
        
        # Retrieve data
        result = storage.retrieve("test_key")
        test("Retrieve operation", result.success and result.data['data']['name'] == "Alice")
        
        # List keys
        result = storage.list_keys()
        test("List keys", result.success and "test_key" in result.data)
        
        # Test 2: Issue management
        print("\n🐛 Testing Issue Management")
        
        # Create issue
        result = issue_manager.create_issue("Test Bug", "This is a test bug report")
        test("Create issue", result.success)
        
        if result.success:
            issue_id = result.data['data']['id']
            
            # Get issue
            result = issue_manager.get_issue(issue_id)
            test("Get issue", result.success and result.data['data']['title'] == "Test Bug")
        
        # Test 3: Storage statistics
        print("\n📊 Testing Storage Statistics")
        
        result = storage.get_stats()
        test("Get statistics", result.success)
        
        if result.success:
            stats = result.data
            test("Statistics content", 
                 'total_objects' in stats and 'cache_size' in stats,
                 f"Objects: {stats.get('total_objects', 0)}, Cache: {stats.get('cache_size', 0)}")
        
        # Test 4: Performance characteristics
        print("\n⚡ Testing Performance")
        
        # Store multiple items
        start_time = time.time()
        for i in range(10):
            storage.store(f"perf_test_{i}", {"index": i, "data": f"test_data_{i}"})
        store_time = time.time() - start_time
        
        test("Batch store performance", store_time < 1.0, f"10 items in {store_time:.3f}s")
        
        # Retrieve multiple items
        start_time = time.time()
        for i in range(10):
            storage.retrieve(f"perf_test_{i}")
        retrieve_time = time.time() - start_time
        
        test("Batch retrieve performance", retrieve_time < 0.5, f"10 items in {retrieve_time:.3f}s")
        
        # Test 5: Data integrity
        print("\n🔒 Testing Data Integrity")
        
        # Store complex data
        complex_data = {
            "user": {"name": "Bob", "email": "bob@example.com"},
            "permissions": ["read", "write"],
            "metadata": {"created": datetime.now().isoformat()}
        }
        
        result = storage.store("complex_test", complex_data)
        test("Store complex data", result.success)
        
        # Retrieve and verify
        result = storage.retrieve("complex_test")
        test("Retrieve complex data", 
             result.success and result.data['data']['user']['name'] == "Bob")
        
        # Summary
        print("\n" + "=" * 50)
        print(f"📋 Test Summary: {tests_passed} passed, {tests_failed} failed")
        
        if tests_failed == 0:
            print("🎉 All tests passed! Git storage concept is working correctly.")
        else:
            print("⚠️  Some tests failed. Check the implementation.")
        
        return tests_failed == 0


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)