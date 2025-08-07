"""
Tests for the Router plugin.
"""

# import pytest  # Removed for compatibility
from yaapp import Yaapp
from yaapp.plugins.router.plugin import Router
from yaapp.result import Result


class TestRouter:
    """Test suite for Router plugin functionality."""
    
    def setup_method(self):
        """Set up test environment before each test."""
        self.yaapp = Yaapp()
        self.router = Router()
        self.yaapp.expose(self.router, name="router")
    
    def test_add_route(self):
        """Test adding a route."""
        def test_handler(request):
            return {"message": "test response"}
        
        result = self.router.add("/test", test_handler)
        assert result.is_ok()
        assert result.unwrap() is True
        
        # Verify route was added
        assert "/test" in self.router.routes
        assert self.router.routes["/test"] == test_handler
    
    def test_delete_route(self):
        """Test deleting a route."""
        def test_handler(request):
            return {"message": "test"}
        
        # Add route first
        self.router.add("/test", test_handler)
        assert "/test" in self.router.routes
        
        # Delete route
        result = self.router.delete("/test")
        assert result.is_ok()
        assert result.unwrap() is True
        
        # Verify route was deleted
        assert "/test" not in self.router.routes
    
    def test_delete_nonexistent_route(self):
        """Test deleting a route that doesn't exist."""
        result = self.router.delete("/nonexistent")
        assert not result.is_ok()
        assert "not found" in result.as_error
    
    def test_update_route(self):
        """Test updating a route handler."""
        def old_handler(request):
            return {"message": "old"}
        
        def new_handler(request):
            return {"message": "new"}
        
        # Add route first
        self.router.add("/test", old_handler)
        assert self.router.routes["/test"] == old_handler
        
        # Update route
        result = self.router.update("/test", new_handler)
        assert result.is_ok()
        assert result.unwrap() is True
        
        # Verify route was updated
        assert self.router.routes["/test"] == new_handler
    
    def test_update_nonexistent_route(self):
        """Test updating a route that doesn't exist."""
        def new_handler(request):
            return {"message": "new"}
        
        result = self.router.update("/nonexistent", new_handler)
        assert not result.is_ok()
        assert "not found" in result.as_error
    
    def test_route_exact_match(self):
        """Test routing with exact pattern match."""
        def test_handler(request):
            return {"message": "exact match", "data": request}
        
        self.router.add("/test", test_handler)
        
        request = {"method": "GET", "data": "test"}
        result = self.router.route("/test", request)
        
        assert result.is_ok()
        response = result.unwrap()
        assert response["message"] == "exact match"
        assert response["data"] == request
    
    def test_route_regex_match(self):
        """Test routing with regex pattern match."""
        def user_handler(request):
            return {"message": "user handler", "request": request}
        
        # Add route with regex pattern
        self.router.add(r"/user/\d+", user_handler)
        
        request = {"method": "GET", "user_id": "123"}
        result = self.router.route("/user/123", request)
        
        assert result.is_ok()
        response = result.unwrap()
        assert response["message"] == "user handler"
        assert response["request"] == request
    
    def test_route_no_match(self):
        """Test routing when no pattern matches."""
        def test_handler(request):
            return {"message": "test"}
        
        self.router.add("/test", test_handler)
        
        request = {"method": "GET"}
        result = self.router.route("/nomatch", request)
        
        assert not result.is_ok()
        assert "No route found" in result.as_error
        assert "/nomatch" in result.as_error
    
    def test_route_handler_exception(self):
        """Test routing when handler throws exception."""
        def failing_handler(request):
            raise ValueError("Handler failed")
        
        self.router.add("/fail", failing_handler)
        
        request = {"method": "GET"}
        result = self.router.route("/fail", request)
        
        assert not result.is_ok()
        assert "Handler error" in result.as_error
        assert "Handler failed" in result.as_error
    
    def test_route_first_match_wins(self):
        """Test that first matching route wins."""
        def handler1(request):
            return {"handler": "first"}
        
        def handler2(request):
            return {"handler": "second"}
        
        # Add overlapping patterns
        self.router.add(r"/test.*", handler1)
        self.router.add(r"/test/specific", handler2)
        
        request = {"method": "GET"}
        result = self.router.route("/test/specific", request)
        
        assert result.is_ok()
        response = result.unwrap()
        # First pattern should match
        assert response["handler"] == "first"
    
    def test_list_routes(self):
        """Test listing all routes."""
        def handler1(request):
            return {"message": "handler1"}
        
        def handler2(request):
            return {"message": "handler2"}
        
        # Add multiple routes
        self.router.add("/route1", handler1)
        self.router.add("/route2", handler2)
        
        result = self.router.list_routes()
        assert result.is_ok()
        
        routes = result.unwrap()
        assert "/route1" in routes
        assert "/route2" in routes
        assert len(routes) == 2
    
    def test_list_routes_empty(self):
        """Test listing routes when none exist."""
        result = self.router.list_routes()
        assert result.is_ok()
        
        routes = result.unwrap()
        assert len(routes) == 0
        assert routes == {}
    
    def test_multiple_routes_different_patterns(self):
        """Test multiple routes with different patterns."""
        def api_handler(request):
            return {"type": "api", "request": request}
        
        def web_handler(request):
            return {"type": "web", "request": request}
        
        def user_handler(request):
            return {"type": "user", "request": request}
        
        # Add different route patterns
        self.router.add(r"/api/.*", api_handler)
        self.router.add(r"/web/.*", web_handler)
        self.router.add(r"/user/\d+", user_handler)
        
        # Test API route
        request = {"data": "api_test"}
        result = self.router.route("/api/test", request)
        assert result.is_ok()
        assert result.unwrap()["type"] == "api"
        
        # Test web route
        result = self.router.route("/web/page", request)
        assert result.is_ok()
        assert result.unwrap()["type"] == "web"
        
        # Test user route
        result = self.router.route("/user/456", request)
        assert result.is_ok()
        assert result.unwrap()["type"] == "user"
        
        # Test no match
        result = self.router.route("/other/path", request)
        assert not result.is_ok()
    
    def test_route_with_complex_request(self):
        """Test routing with complex request data."""
        def complex_handler(request):
            return {
                "processed": True,
                "method": request.get("method"),
                "headers": request.get("headers"),
                "body": request.get("body")
            }
        
        self.router.add("/complex", complex_handler)
        
        complex_request = {
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "body": {"user": "test", "action": "create"}
        }
        
        result = self.router.route("/complex", complex_request)
        assert result.is_ok()
        
        response = result.unwrap()
        assert response["processed"] is True
        assert response["method"] == "POST"
        assert response["headers"]["Content-Type"] == "application/json"
        assert response["body"]["user"] == "test"
    
    def test_route_pattern_order_matters(self):
        """Test that route pattern order matters for matching."""
        def general_handler(request):
            return {"type": "general"}
        
        def specific_handler(request):
            return {"type": "specific"}
        
        # Add general pattern first, then specific
        self.router.add(r"/test/.*", general_handler)
        self.router.add(r"/test/specific", specific_handler)
        
        request = {"method": "GET"}
        result = self.router.route("/test/specific", request)
        
        assert result.is_ok()
        # General pattern should match first
        assert result.unwrap()["type"] == "general"
    
    def test_empty_router(self):
        """Test router behavior when empty."""
        request = {"method": "GET"}
        result = self.router.route("/any/path", request)
        
        assert not result.is_ok()
        assert "No route found" in result.as_error
    
    def test_route_with_none_request(self):
        """Test routing with None request."""
        def handler(request):
            return {"request_was_none": request is None}
        
        self.router.add("/test", handler)
        
        result = self.router.route("/test", None)
        assert result.is_ok()
        assert result.unwrap()["request_was_none"] is True
    
    def test_router_with_config(self):
        """Test router initialization with configuration."""
        config = {
            "routes": {
                "/api/.*": "api_handler",
                "/web/.*": "web_handler"
            },
            "default_handler": "not_found"
        }
        
        router = Router(config)
        
        # Test config access
        config_result = router.get_config()
        assert config_result.is_ok()
        assert config_result.unwrap() == config
    
    def test_reload_config(self):
        """Test reloading router configuration."""
        initial_config = {"setting1": "value1"}
        router = Router(initial_config)
        
        new_config = {"setting1": "new_value", "setting2": "value2"}
        result = router.reload_config(new_config)
        
        assert result.is_ok()
        assert result.unwrap() is True
        
        # Verify config was updated
        config_result = router.get_config()
        assert config_result.is_ok()
        assert config_result.unwrap() == new_config
    
    def test_router_without_config(self):
        """Test router initialization without configuration."""
        router = Router()
        
        config_result = router.get_config()
        assert config_result.is_ok()
        assert config_result.unwrap() == {}