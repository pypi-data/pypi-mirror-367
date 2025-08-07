"""
Git-based blockchain storage implementation using PyGit2.
Stores data as Git objects (blobs, trees, commits) for immutable, distributed storage.
"""

import json
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict

import pygit2


@dataclass
class StorageResult:
    """Result wrapper for storage operations"""
    success: bool
    data: Any = None
    error: str = None
    commit_hash: str = None
    blob_hash: str = None


class GitBlockchainStorage:
    """Git objects-based blockchain storage using PyGit2"""
    
    def __init__(self, repo_path: str, author_name: str = "YAPP", author_email: str = "yapp@system.local"):
        self.repo_path = Path(repo_path)
        self.author_name = author_name
        self.author_email = author_email
        
        # Initialize or open repository
        self._init_repository()
        
        # Create signature for commits
        self.signature = pygit2.Signature(author_name, author_email)
        
        # In-memory cache for performance
        self._cache = {}
        self._index_cache = {}
        
    def _init_repository(self):
        """Initialize Git repository if it doesn't exist"""
        if not self.repo_path.exists():
            self.repo_path.mkdir(parents=True, exist_ok=True)
            self.repo = pygit2.init_repository(str(self.repo_path))
            
            # Create initial commit
            tree_id = self.repo.TreeBuilder().write()
            self.repo.create_commit(
                'refs/heads/main',
                self.signature,
                self.signature,
                'Initial commit',
                tree_id,
                []
            )
        else:
            self.repo = pygit2.Repository(str(self.repo_path))
    
    def store(self, key: str, data: Any, metadata: Optional[Dict] = None) -> StorageResult:
        """Store data as Git blob object"""
        try:
            # Prepare data with metadata
            storage_data = {
                'key': key,
                'data': data,
                'metadata': metadata or {},
                'timestamp': datetime.now().isoformat(),
                'version': 1
            }
            
            # Serialize data
            serialized = json.dumps(storage_data, default=str, indent=2).encode('utf-8')
            
            # Create blob object
            blob_oid = self.repo.create_blob(serialized)
            
            # Update tree with new blob
            tree_oid = self._update_tree(key, blob_oid)
            
            # Create commit (blockchain block)
            commit_oid = self._create_commit(f"Store: {key}", tree_oid)
            
            # Update cache
            self._cache[key] = storage_data
            self._index_cache[key] = str(blob_oid)
            
            return StorageResult(
                success=True,
                data=storage_data,
                commit_hash=str(commit_oid),
                blob_hash=str(blob_oid)
            )
            
        except Exception as e:
            return StorageResult(success=False, error=str(e))
    
    def retrieve(self, key: str) -> StorageResult:
        """Retrieve data from Git blob object"""
        try:
            # Check cache first
            if key in self._cache:
                return StorageResult(success=True, data=self._cache[key])
            
            # Find blob in current tree
            blob_oid = self._find_blob_in_tree(key)
            if not blob_oid:
                return StorageResult(success=False, error=f"Key '{key}' not found")
            
            # Read blob data
            blob = self.repo[blob_oid]
            storage_data = json.loads(blob.data.decode('utf-8'))
            
            # Update cache
            self._cache[key] = storage_data
            
            return StorageResult(success=True, data=storage_data, blob_hash=str(blob_oid))
            
        except Exception as e:
            return StorageResult(success=False, error=str(e))
    
    def delete(self, key: str) -> StorageResult:
        """Delete data by creating tombstone record"""
        try:
            # Create tombstone record
            tombstone_data = {
                'key': key,
                'deleted': True,
                'deleted_at': datetime.now().isoformat(),
                'tombstone': True
            }
            
            # Store tombstone
            result = self.store(f"_deleted_{key}", tombstone_data)
            if not result.success:
                return result
            
            # Remove from cache
            self._cache.pop(key, None)
            self._index_cache.pop(key, None)
            
            return StorageResult(
                success=True,
                data={'deleted': True, 'key': key},
                commit_hash=result.commit_hash
            )
            
        except Exception as e:
            return StorageResult(success=False, error=str(e))
    
    def list_keys(self, prefix: str = "", include_deleted: bool = False) -> StorageResult:
        """List all keys in storage"""
        try:
            keys = []
            
            # Get current tree
            if self.repo.is_empty:
                return StorageResult(success=True, data=[])
            
            head_commit = self.repo[self.repo.head.target]
            tree = head_commit.tree
            
            for entry in tree:
                if entry.type == pygit2.GIT_OBJ_BLOB:
                    # Read blob to get key
                    blob = self.repo[entry.oid]
                    try:
                        storage_data = json.loads(blob.data.decode('utf-8'))
                        key = storage_data.get('key', entry.name)
                        
                        # Filter by prefix
                        if prefix and not key.startswith(prefix):
                            continue
                        
                        # Filter deleted items
                        if not include_deleted and (
                            storage_data.get('deleted', False) or 
                            key.startswith('_deleted_')
                        ):
                            continue
                        
                        keys.append(key)
                    except:
                        continue
            
            return StorageResult(success=True, data=sorted(keys))
            
        except Exception as e:
            return StorageResult(success=False, error=str(e))
    
    def query(self, filters: Dict[str, Any]) -> StorageResult:
        """Query data using filters"""
        try:
            results = []
            
            # Get all keys
            keys_result = self.list_keys()
            if not keys_result.success:
                return keys_result
            
            # Filter data
            for key in keys_result.data:
                data_result = self.retrieve(key)
                if data_result.success:
                    storage_data = data_result.data
                    
                    # Apply filters
                    if self._matches_filters(storage_data, filters):
                        results.append(storage_data)
            
            return StorageResult(success=True, data=results)
            
        except Exception as e:
            return StorageResult(success=False, error=str(e))
    
    def get_history(self, key: str) -> StorageResult:
        """Get complete history of a key"""
        try:
            history = []
            
            # Walk through all commits
            for commit in self.repo.walk(self.repo.head.target):
                tree = commit.tree
                
                # Look for key in this commit
                for entry in tree:
                    if entry.type == pygit2.GIT_OBJ_BLOB:
                        blob = self.repo[entry.oid]
                        try:
                            storage_data = json.loads(blob.data.decode('utf-8'))
                            if storage_data.get('key') == key:
                                history.append({
                                    'commit': str(commit.oid),
                                    'timestamp': commit.commit_time,
                                    'message': commit.message.strip(),
                                    'author': commit.author.name,
                                    'data': storage_data
                                })
                                break
                        except:
                            continue
            
            return StorageResult(success=True, data=history)
            
        except Exception as e:
            return StorageResult(success=False, error=str(e))
    
    def get_stats(self) -> StorageResult:
        """Get storage statistics"""
        try:
            stats = {
                'repository_path': str(self.repo_path),
                'total_commits': 0,
                'total_objects': 0,
                'cache_size': len(self._cache),
                'is_bare': self.repo.is_bare,
                'is_empty': self.repo.is_empty
            }
            
            if not self.repo.is_empty:
                # Count commits
                stats['total_commits'] = sum(1 for _ in self.repo.walk(self.repo.head.target))
                
                # Count objects
                for obj in self.repo:
                    stats['total_objects'] += 1
                
                # Get latest commit info
                head_commit = self.repo[self.repo.head.target]
                stats['latest_commit'] = {
                    'hash': str(head_commit.oid),
                    'message': head_commit.message.strip(),
                    'timestamp': head_commit.commit_time,
                    'author': head_commit.author.name
                }
            
            return StorageResult(success=True, data=stats)
            
        except Exception as e:
            return StorageResult(success=False, error=str(e))
    
    def _update_tree(self, key: str, blob_oid) -> str:
        """Update tree with new blob"""
        if self.repo.is_empty:
            # Create new tree
            tree_builder = self.repo.TreeBuilder()
        else:
            # Update existing tree
            head_commit = self.repo[self.repo.head.target]
            tree_builder = self.repo.TreeBuilder(head_commit.tree)
        
        # Add/update blob in tree
        tree_builder.insert(key, blob_oid, pygit2.GIT_FILEMODE_BLOB)
        
        return tree_builder.write()
    
    def _create_commit(self, message: str, tree_oid) -> str:
        """Create commit object (blockchain block)"""
        parents = [] if self.repo.is_empty else [self.repo.head.target]
        
        commit_oid = self.repo.create_commit(
            'refs/heads/main',
            self.signature,
            self.signature,
            message,
            tree_oid,
            parents
        )
        
        return commit_oid
    
    def _find_blob_in_tree(self, key: str) -> Optional[str]:
        """Find blob OID for key in current tree"""
        if self.repo.is_empty:
            return None
        
        try:
            head_commit = self.repo[self.repo.head.target]
            tree = head_commit.tree
            
            for entry in tree:
                if entry.name == key and entry.type == pygit2.GIT_OBJ_BLOB:
                    return entry.oid
            
            return None
        except:
            return None
    
    def _matches_filters(self, data: Dict, filters: Dict) -> bool:
        """Check if data matches filter criteria"""
        for key, value in filters.items():
            if key not in data:
                return False
            
            data_value = data[key]
            
            # Handle different filter types
            if isinstance(value, dict):
                # Range queries, etc.
                for op, op_value in value.items():
                    if op == '$eq' and data_value != op_value:
                        return False
                    elif op == '$ne' and data_value == op_value:
                        return False
                    elif op == '$gt' and data_value <= op_value:
                        return False
                    elif op == '$gte' and data_value < op_value:
                        return False
                    elif op == '$lt' and data_value >= op_value:
                        return False
                    elif op == '$lte' and data_value > op_value:
                        return False
                    elif op == '$in' and data_value not in op_value:
                        return False
                    elif op == '$contains' and op_value not in str(data_value):
                        return False
            else:
                # Direct equality
                if data_value != value:
                    return False
        
        return True


# Issue and Review entities for demonstration
@dataclass
class Issue:
    """Issue entity for demonstration"""
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


@dataclass
class Review:
    """Review entity for demonstration"""
    id: str
    issue_id: str
    reviewer: str
    status: str = "pending"  # pending, approved, rejected, changes_requested
    comments: List[str] = None
    decision_notes: Optional[str] = None
    created_at: Optional[str] = None
    approved_at: Optional[str] = None
    
    def __post_init__(self):
        if self.comments is None:
            self.comments = []
        if not self.created_at:
            self.created_at = datetime.now().isoformat()


class IssueManager:
    """Issue management with review workflow using Git storage"""
    
    def __init__(self, storage: GitBlockchainStorage):
        self.storage = storage
    
    def create_issue(self, title: str, description: str, **kwargs) -> StorageResult:
        """Create new issue"""
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
    
    def update_issue(self, issue_id: str, **updates) -> StorageResult:
        """Update issue"""
        result = self.storage.retrieve(issue_id)
        if not result.success:
            return result
        
        issue_data = result.data['data']
        issue_data.update(updates)
        issue_data['updated_at'] = datetime.now().isoformat()
        
        return self.storage.store(issue_id, issue_data, {'type': 'issue'})
    
    def request_review(self, issue_id: str, reviewer: str) -> StorageResult:
        """Request review for issue"""
        # Update issue status
        update_result = self.update_issue(
            issue_id,
            status="under_review",
            review_status="pending",
            reviewer=reviewer
        )
        
        if not update_result.success:
            return update_result
        
        # Create review record
        review_id = f"review_{uuid.uuid4().hex[:8]}"
        review = Review(
            id=review_id,
            issue_id=issue_id,
            reviewer=reviewer
        )
        
        return self.storage.store(review_id, asdict(review), {'type': 'review'})
    
    def submit_review(self, review_id: str, status: str, comments: List[str] = None, decision_notes: str = None) -> StorageResult:
        """Submit review decision"""
        # Get review
        result = self.storage.retrieve(review_id)
        if not result.success:
            return result
        
        review_data = result.data['data']
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
        if status == 'approved':
            self.update_issue(issue_id, review_status="approved", status="approved")
        elif status == 'rejected':
            self.update_issue(issue_id, review_status="rejected", status="needs_changes")
        
        return review_result
    
    def list_issues(self, status: str = None) -> StorageResult:
        """List issues with optional status filter"""
        filters = {'metadata.type': 'issue'}
        if status:
            filters['data.status'] = status
        
        return self.storage.query(filters)
    
    def list_reviews(self, issue_id: str = None) -> StorageResult:
        """List reviews with optional issue filter"""
        filters = {'metadata.type': 'review'}
        if issue_id:
            filters['data.issue_id'] = issue_id
        
        return self.storage.query(filters)