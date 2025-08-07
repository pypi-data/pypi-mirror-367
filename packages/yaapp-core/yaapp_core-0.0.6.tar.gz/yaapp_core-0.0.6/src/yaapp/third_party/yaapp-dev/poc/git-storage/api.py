"""
FastAPI JSON/RPC API for Git-based blockchain storage.
Provides REST and RPC endpoints for storage operations and issue management.
"""

import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from git_storage import GitBlockchainStorage, IssueManager, StorageResult


# Pydantic models for API
class StoreRequest(BaseModel):
    key: str = Field(..., description="Unique key for the data")
    data: Any = Field(..., description="Data to store")
    metadata: Optional[Dict] = Field(None, description="Optional metadata")


class RetrieveRequest(BaseModel):
    key: str = Field(..., description="Key to retrieve")


class DeleteRequest(BaseModel):
    key: str = Field(..., description="Key to delete")


class ListKeysRequest(BaseModel):
    prefix: str = Field("", description="Key prefix filter")
    include_deleted: bool = Field(False, description="Include deleted keys")


class QueryRequest(BaseModel):
    filters: Dict[str, Any] = Field(..., description="Query filters")


class HistoryRequest(BaseModel):
    key: str = Field(..., description="Key to get history for")


class CreateIssueRequest(BaseModel):
    title: str = Field(..., description="Issue title")
    description: str = Field(..., description="Issue description")
    assignee: Optional[str] = Field(None, description="Issue assignee")


class UpdateIssueRequest(BaseModel):
    issue_id: str = Field(..., description="Issue ID")
    title: Optional[str] = Field(None, description="New title")
    description: Optional[str] = Field(None, description="New description")
    status: Optional[str] = Field(None, description="New status")
    assignee: Optional[str] = Field(None, description="New assignee")


class RequestReviewRequest(BaseModel):
    issue_id: str = Field(..., description="Issue ID")
    reviewer: str = Field(..., description="Reviewer email/username")


class SubmitReviewRequest(BaseModel):
    review_id: str = Field(..., description="Review ID")
    status: str = Field(..., description="Review status: approved, rejected, changes_requested")
    comments: Optional[List[str]] = Field(None, description="Review comments")
    decision_notes: Optional[str] = Field(None, description="Decision notes")


class ListIssuesRequest(BaseModel):
    status: Optional[str] = Field(None, description="Filter by status")


class ListReviewsRequest(BaseModel):
    issue_id: Optional[str] = Field(None, description="Filter by issue ID")


class RPCRequest(BaseModel):
    method: str = Field(..., description="RPC method name")
    params: Dict[str, Any] = Field(default_factory=dict, description="Method parameters")
    id: Optional[str] = Field(None, description="Request ID")


class RPCResponse(BaseModel):
    result: Any = None
    error: Optional[str] = None
    id: Optional[str] = None


# Initialize FastAPI app
app = FastAPI(
    title="Git Blockchain Storage API",
    description="REST and RPC API for Git-based blockchain storage with issue management",
    version="1.0.0"
)

# Initialize storage (using temporary directory for PoC)
STORAGE_PATH = Path(tempfile.gettempdir()) / "git-storage-poc"
storage = GitBlockchainStorage(str(STORAGE_PATH))
issue_manager = IssueManager(storage)


def handle_storage_result(result: StorageResult) -> Dict[str, Any]:
    """Convert StorageResult to API response"""
    if result.success:
        response = {"success": True, "data": result.data}
        if result.commit_hash:
            response["commit_hash"] = result.commit_hash
        if result.blob_hash:
            response["blob_hash"] = result.blob_hash
        return response
    else:
        raise HTTPException(status_code=400, detail=result.error)


# REST API Endpoints

@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "message": "Git Blockchain Storage API",
        "version": "1.0.0",
        "endpoints": {
            "storage": "/storage/*",
            "issues": "/issues/*",
            "rpc": "/rpc"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    stats_result = storage.get_stats()
    return {
        "status": "healthy" if stats_result.success else "unhealthy",
        "storage": stats_result.data if stats_result.success else None,
        "error": stats_result.error if not stats_result.success else None
    }


# Storage REST endpoints
@app.post("/storage/store")
async def store_data(request: StoreRequest):
    """Store data in Git blockchain storage"""
    result = storage.store(request.key, request.data, request.metadata)
    return handle_storage_result(result)


@app.post("/storage/retrieve")
async def retrieve_data(request: RetrieveRequest):
    """Retrieve data from Git blockchain storage"""
    result = storage.retrieve(request.key)
    return handle_storage_result(result)


@app.post("/storage/delete")
async def delete_data(request: DeleteRequest):
    """Delete data from Git blockchain storage"""
    result = storage.delete(request.key)
    return handle_storage_result(result)


@app.post("/storage/list")
async def list_keys(request: ListKeysRequest):
    """List all keys in storage"""
    result = storage.list_keys(request.prefix, request.include_deleted)
    return handle_storage_result(result)


@app.post("/storage/query")
async def query_data(request: QueryRequest):
    """Query data using filters"""
    result = storage.query(request.filters)
    return handle_storage_result(result)


@app.post("/storage/history")
async def get_history(request: HistoryRequest):
    """Get complete history of a key"""
    result = storage.get_history(request.key)
    return handle_storage_result(result)


@app.get("/storage/stats")
async def get_stats():
    """Get storage statistics"""
    result = storage.get_stats()
    return handle_storage_result(result)


# Issue Management REST endpoints
@app.post("/issues/create")
async def create_issue(request: CreateIssueRequest):
    """Create new issue"""
    result = issue_manager.create_issue(
        title=request.title,
        description=request.description,
        assignee=request.assignee
    )
    return handle_storage_result(result)


@app.get("/issues/{issue_id}")
async def get_issue(issue_id: str):
    """Get issue by ID"""
    result = issue_manager.get_issue(issue_id)
    return handle_storage_result(result)


@app.post("/issues/update")
async def update_issue(request: UpdateIssueRequest):
    """Update issue"""
    updates = {}
    if request.title is not None:
        updates['title'] = request.title
    if request.description is not None:
        updates['description'] = request.description
    if request.status is not None:
        updates['status'] = request.status
    if request.assignee is not None:
        updates['assignee'] = request.assignee
    
    result = issue_manager.update_issue(request.issue_id, **updates)
    return handle_storage_result(result)


@app.post("/issues/request-review")
async def request_review(request: RequestReviewRequest):
    """Request review for issue"""
    result = issue_manager.request_review(request.issue_id, request.reviewer)
    return handle_storage_result(result)


@app.post("/issues/submit-review")
async def submit_review(request: SubmitReviewRequest):
    """Submit review decision"""
    result = issue_manager.submit_review(
        review_id=request.review_id,
        status=request.status,
        comments=request.comments,
        decision_notes=request.decision_notes
    )
    return handle_storage_result(result)


@app.post("/issues/list")
async def list_issues(request: ListIssuesRequest):
    """List issues with optional status filter"""
    result = issue_manager.list_issues(request.status)
    return handle_storage_result(result)


@app.post("/reviews/list")
async def list_reviews(request: ListReviewsRequest):
    """List reviews with optional issue filter"""
    result = issue_manager.list_reviews(request.issue_id)
    return handle_storage_result(result)


# JSON-RPC endpoint
@app.post("/rpc")
async def rpc_endpoint(request: RPCRequest):
    """JSON-RPC endpoint for all operations"""
    try:
        method = request.method
        params = request.params
        
        # Storage operations
        if method == "storage.store":
            result = storage.store(params["key"], params["data"], params.get("metadata"))
        elif method == "storage.retrieve":
            result = storage.retrieve(params["key"])
        elif method == "storage.delete":
            result = storage.delete(params["key"])
        elif method == "storage.list":
            result = storage.list_keys(params.get("prefix", ""), params.get("include_deleted", False))
        elif method == "storage.query":
            result = storage.query(params["filters"])
        elif method == "storage.history":
            result = storage.get_history(params["key"])
        elif method == "storage.stats":
            result = storage.get_stats()
        
        # Issue management operations
        elif method == "issues.create":
            result = issue_manager.create_issue(
                title=params["title"],
                description=params["description"],
                assignee=params.get("assignee")
            )
        elif method == "issues.get":
            result = issue_manager.get_issue(params["issue_id"])
        elif method == "issues.update":
            result = issue_manager.update_issue(params["issue_id"], **params.get("updates", {}))
        elif method == "issues.request_review":
            result = issue_manager.request_review(params["issue_id"], params["reviewer"])
        elif method == "issues.submit_review":
            result = issue_manager.submit_review(
                review_id=params["review_id"],
                status=params["status"],
                comments=params.get("comments"),
                decision_notes=params.get("decision_notes")
            )
        elif method == "issues.list":
            result = issue_manager.list_issues(params.get("status"))
        elif method == "reviews.list":
            result = issue_manager.list_reviews(params.get("issue_id"))
        
        else:
            return RPCResponse(
                error=f"Unknown method: {method}",
                id=request.id
            )
        
        # Handle result
        if result.success:
            response_data = {"data": result.data}
            if result.commit_hash:
                response_data["commit_hash"] = result.commit_hash
            if result.blob_hash:
                response_data["blob_hash"] = result.blob_hash
            
            return RPCResponse(
                result=response_data,
                id=request.id
            )
        else:
            return RPCResponse(
                error=result.error,
                id=request.id
            )
    
    except Exception as e:
        return RPCResponse(
            error=str(e),
            id=request.id
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)