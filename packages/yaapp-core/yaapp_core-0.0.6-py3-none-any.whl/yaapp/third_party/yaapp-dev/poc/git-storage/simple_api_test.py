#!/usr/bin/env python3
"""
Simple API test using the mock storage implementation.
This demonstrates the FastAPI integration without external dependencies.
"""

import json
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from fastapi import FastAPI, HTTPException
    from fastapi.testclient import TestClient
    from pydantic import BaseModel, Field
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    print("⚠️  FastAPI not available, skipping API tests")

from simple_test import MockGitStorage, MockIssueManager, StorageResult


if FASTAPI_AVAILABLE:
    # Pydantic models
    class StoreRequest(BaseModel):
        key: str
        data: Any
        metadata: Optional[Dict] = None

    class RetrieveRequest(BaseModel):
        key: str

    class CreateIssueRequest(BaseModel):
        title: str
        description: str
        assignee: Optional[str] = None

    class RPCRequest(BaseModel):
        method: str
        params: Dict[str, Any] = {}
        id: Optional[str] = None

    class RPCResponse(BaseModel):
        result: Any = None
        error: Optional[str] = None
        id: Optional[str] = None

    # Create FastAPI app
    app = FastAPI(title="Mock Git Storage API", version="1.0.0")

    # Initialize storage
    STORAGE_PATH = Path(tempfile.gettempdir()) / "mock-git-storage"
    storage = MockGitStorage(str(STORAGE_PATH))
    issue_manager = MockIssueManager(storage)

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

    @app.get("/")
    async def root():
        return {"message": "Mock Git Storage API", "version": "1.0.0"}

    @app.get("/health")
    async def health_check():
        stats_result = storage.get_stats()
        return {
            "status": "healthy" if stats_result.success else "unhealthy",
            "storage": stats_result.data if stats_result.success else None
        }

    @app.post("/storage/store")
    async def store_data(request: StoreRequest):
        result = storage.store(request.key, request.data, request.metadata)
        return handle_storage_result(result)

    @app.post("/storage/retrieve")
    async def retrieve_data(request: RetrieveRequest):
        result = storage.retrieve(request.key)
        return handle_storage_result(result)

    @app.get("/storage/list")
    async def list_keys():
        result = storage.list_keys()
        return handle_storage_result(result)

    @app.get("/storage/stats")
    async def get_stats():
        result = storage.get_stats()
        return handle_storage_result(result)

    @app.post("/issues/create")
    async def create_issue(request: CreateIssueRequest):
        result = issue_manager.create_issue(
            title=request.title,
            description=request.description,
            assignee=request.assignee
        )
        return handle_storage_result(result)

    @app.get("/issues/{issue_id}")
    async def get_issue(issue_id: str):
        result = issue_manager.get_issue(issue_id)
        return handle_storage_result(result)

    @app.post("/rpc")
    async def rpc_endpoint(request: RPCRequest):
        try:
            method = request.method
            params = request.params
            
            if method == "storage.store":
                result = storage.store(params["key"], params["data"], params.get("metadata"))
            elif method == "storage.retrieve":
                result = storage.retrieve(params["key"])
            elif method == "storage.list":
                result = storage.list_keys()
            elif method == "storage.stats":
                result = storage.get_stats()
            elif method == "issues.create":
                result = issue_manager.create_issue(
                    title=params["title"],
                    description=params["description"],
                    assignee=params.get("assignee")
                )
            elif method == "issues.get":
                result = issue_manager.get_issue(params["issue_id"])
            else:
                return RPCResponse(error=f"Unknown method: {method}", id=request.id)
            
            if result.success:
                response_data = {"data": result.data}
                if result.commit_hash:
                    response_data["commit_hash"] = result.commit_hash
                if result.blob_hash:
                    response_data["blob_hash"] = result.blob_hash
                
                return RPCResponse(result=response_data, id=request.id)
            else:
                return RPCResponse(error=result.error, id=request.id)
        
        except Exception as e:
            return RPCResponse(error=str(e), id=request.id)


def run_api_tests():
    """Run API tests using TestClient"""
    if not FASTAPI_AVAILABLE:
        print("❌ FastAPI not available, cannot run API tests")
        return False
    
    print("🌐 Running Mock API Tests")
    print("=" * 40)
    
    client = TestClient(app)
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
    
    # Test 1: Basic endpoints
    print("\n🔌 Testing Basic Endpoints")
    
    response = client.get("/")
    test("Root endpoint", response.status_code == 200)
    
    response = client.get("/health")
    test("Health check", response.status_code == 200 and response.json()["status"] == "healthy")
    
    # Test 2: Storage REST API
    print("\n💾 Testing Storage REST API")
    
    # Store data
    store_data = {
        "key": "api_test",
        "data": {"name": "API Test", "value": 42},
        "metadata": {"type": "test"}
    }
    response = client.post("/storage/store", json=store_data)
    test("Store via REST", response.status_code == 200)
    
    if response.status_code == 200:
        result = response.json()
        test("Store response format", "commit_hash" in result and "success" in result)
    
    # Retrieve data
    retrieve_data = {"key": "api_test"}
    response = client.post("/storage/retrieve", json=retrieve_data)
    test("Retrieve via REST", response.status_code == 200)
    
    if response.status_code == 200:
        result = response.json()
        test("Retrieved data correct", 
             result["data"]["data"]["name"] == "API Test")
    
    # List keys
    response = client.get("/storage/list")
    test("List keys via REST", response.status_code == 200)
    
    # Get stats
    response = client.get("/storage/stats")
    test("Get stats via REST", response.status_code == 200)
    
    # Test 3: Issue Management API
    print("\n🐛 Testing Issue Management API")
    
    # Create issue
    issue_data = {
        "title": "API Test Issue",
        "description": "Created via API test",
        "assignee": "test@example.com"
    }
    response = client.post("/issues/create", json=issue_data)
    test("Create issue via REST", response.status_code == 200)
    
    if response.status_code == 200:
        result = response.json()
        issue_id = result["data"]["data"]["id"]
        
        # Get issue
        response = client.get(f"/issues/{issue_id}")
        test("Get issue via REST", response.status_code == 200)
        
        if response.status_code == 200:
            result = response.json()
            test("Issue data correct", 
                 result["data"]["data"]["title"] == "API Test Issue")
    
    # Test 4: JSON-RPC API
    print("\n🔄 Testing JSON-RPC API")
    
    # RPC store
    rpc_request = {
        "method": "storage.store",
        "params": {
            "key": "rpc_test",
            "data": {"rpc": True, "value": 123}
        },
        "id": "test_1"
    }
    response = client.post("/rpc", json=rpc_request)
    test("RPC store", response.status_code == 200)
    
    if response.status_code == 200:
        result = response.json()
        test("RPC response format", result["error"] is None and "result" in result)
    
    # RPC retrieve
    rpc_request = {
        "method": "storage.retrieve",
        "params": {"key": "rpc_test"},
        "id": "test_2"
    }
    response = client.post("/rpc", json=rpc_request)
    test("RPC retrieve", response.status_code == 200)
    
    if response.status_code == 200:
        result = response.json()
        test("RPC retrieved data", 
             result["result"]["data"]["data"]["rpc"] is True)
    
    # RPC issue creation
    rpc_request = {
        "method": "issues.create",
        "params": {
            "title": "RPC Issue",
            "description": "Created via RPC"
        },
        "id": "test_3"
    }
    response = client.post("/rpc", json=rpc_request)
    test("RPC create issue", response.status_code == 200)
    
    # Test 5: Error handling
    print("\n⚠️  Testing Error Handling")
    
    # Try to retrieve non-existent key
    retrieve_data = {"key": "nonexistent"}
    response = client.post("/storage/retrieve", json=retrieve_data)
    test("Handle missing key", response.status_code == 400)
    
    # Try unknown RPC method
    rpc_request = {
        "method": "unknown.method",
        "params": {},
        "id": "error_test"
    }
    response = client.post("/rpc", json=rpc_request)
    test("Handle unknown RPC method", response.status_code == 200)
    
    if response.status_code == 200:
        result = response.json()
        test("RPC error response", result["error"] is not None)
    
    # Summary
    print("\n" + "=" * 40)
    print(f"📋 API Test Summary: {tests_passed} passed, {tests_failed} failed")
    
    if tests_failed == 0:
        print("🎉 All API tests passed!")
    else:
        print("⚠️  Some API tests failed.")
    
    return tests_failed == 0


if __name__ == "__main__":
    success = run_api_tests()
    exit(0 if success else 1)