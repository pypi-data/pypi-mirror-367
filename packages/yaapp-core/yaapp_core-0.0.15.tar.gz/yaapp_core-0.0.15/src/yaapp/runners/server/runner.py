"""
Server runner for yaapp.
Provides FastAPI web server functionality.
"""

import inspect
from typing import Dict, Any


def help() -> str:
    """Return server help text with parseable options."""
    return """
🌐 SERVER: FastAPI server
  --host TEXT     Server host (default: localhost)
  --port INTEGER  Server port (default: 8000)
  --reload        Enable auto-reload
  --workers INT   Number of worker processes
    """


def _register_with_registry(yaapp_engine, registry_url: str, host: str, port: int):
    """Register this service with the registry."""
    try:
        import requests
        
        # Determine service name from loaded plugins
        service_name_result = _get_service_name(yaapp_engine)
        if service_name_result.is_err():
            print(f"⚠️ Registry: Failed to get service name: {service_name_result.as_error}")
            return
        service_name = service_name_result.unwrap()
        service_url = f"http://{host}:{port}"
        
        # Register with registry
        registration_data = {
            "name": service_name,
            "url": service_url,
            "status": "healthy",
            "metadata": {
                "plugins": list(yaapp_engine.registry.list_names()),
                "host": host,
                "port": port
            }
        }
        
        response = requests.post(
            f"{registry_url}/register",
            json=registration_data,
            timeout=5
        )
        
        if response.status_code == 200:
            print(f"📝 Registry: Registered {service_name} at {service_url} with {registry_url}")
        else:
            print(f"⚠️ Registry: Failed to register with {registry_url}: {response.status_code}")
            
    except ImportError:
        print("⚠️ Registry: requests library required for registry integration. Install with: pip install requests")
    except Exception as e:
        print(f"⚠️ Registry: Error registering with {registry_url}: {e}")

def _get_service_name(yaapp_engine):
    """Determine service name from loaded plugins."""
    from ...result import Result, Ok
    
    try:
        # Check if we have a showcase plugin loaded
        if hasattr(yaapp_engine, '_showcase_plugin') and yaapp_engine._showcase_plugin:
            return Ok(yaapp_engine._showcase_plugin)
        
        # Fallback: find non-common plugins
        plugins = yaapp_engine.registry.list_names()
        # No hardcoded auto plugins
        service_plugins = plugins  # All plugins are service plugins
        
        if service_plugins:
            return Ok(service_plugins[0])  # Use first non-common plugin as service name
        elif plugins:
            return Ok(plugins[0])  # Fallback to first plugin
        else:
            return Ok("yaapp-service")  # Default name
            
    except Exception as e:
        return Result.error(f"Failed to get service name: {str(e)}")

def _get_port_from_portalloc(yaapp_engine, kwargs):
    """Get port from portalloc plugin if available, otherwise use config/default."""
    from ...result import Result, Ok
    
    try:
        # Check explicit port first
        if 'port' in kwargs:
            return Ok(kwargs['port'])
        
        # Check config
        if hasattr(yaapp_engine, '_config') and yaapp_engine._config:
            try:
                config_port = yaapp_engine._config.server.port
                if config_port != 8000:  # If not default
                    return Ok(config_port)
            except AttributeError:
                # Config doesn't have server.port, continue to portalloc
                pass
        
        # Try portalloc using yaapp_engine.execute
        result = yaapp_engine.registry.get_item('portalloc')
        if result.is_ok():
            # Use yaapp_engine.execute to call portalloc.allocate_port
            import asyncio
            try:
                port_result = asyncio.run(yaapp_engine.execute('portalloc.allocate_port', service_name='server'))
                if port_result.is_ok():
                    port_info = port_result.unwrap()
                    if isinstance(port_info, dict) and 'port' in port_info and 'error' not in port_info:
                        allocated_port = port_info['port']
                        print(f"🔌 Server: Allocated port {allocated_port} from portalloc")
                        return Ok(allocated_port)
                    else:
                        print(f"⚠️ Server: Portalloc failed: {port_info}")
                else:
                    print(f"⚠️ Server: Portalloc execution failed: {port_result.as_error}")
            except Exception as e:
                print(f"⚠️ Server: Error executing portalloc: {e}")
        else:
            print("ℹ️ Server: Portalloc not available, using default port")
        
        # Fallback to default
        return Ok(8000)
        
    except Exception as e:
        return Result.error(f"Failed to get port: {str(e)}")


def run(yaapp_engine, **kwargs):
    """Execute the server runner."""
    from ...result import Result, Ok
    
    try:
        # Get config from yaapp_engine
        host = 'localhost'
        # port will be determined by portalloc
        reload = False
        
        if hasattr(yaapp_engine, '_config') and yaapp_engine._config:
            try:
                # Server config is in config.server, not discovered_sections
                server_config = yaapp_engine._config.server
                host = server_config.host
                port = server_config.port
                reload = server_config.reload
            except AttributeError:
                # Config doesn't have server config, use defaults
                pass
        
        # Override with kwargs if provided
        host = kwargs.get('host', host)
        # Get port from portalloc if available, otherwise use config/default
        port_result = _get_port_from_portalloc(yaapp_engine, kwargs)
        if port_result.is_err():
            print(f"❌ Server: Failed to get port: {port_result.as_error}")
            return Result.error(f"Failed to get port: {port_result.as_error}")
        port = port_result.unwrap()
        reload = kwargs.get('reload', reload)
        
        _start_server(yaapp_engine, host, port, reload)
        
        # Register with registry if specified
        registry_url = kwargs.get('registry')
        if registry_url:
            _register_with_registry(yaapp_engine, registry_url, host, port)
            
        return Ok(None)
        
    except Exception as e:
        return Result.error(f"Server runner failed: {str(e)}")


def _start_server(yaapp_engine, host: str, port: int, reload: bool):
    """Start FastAPI server with both RPC and REST endpoints."""
    print(f"🚀 Starting web server on {host}:{port}")
    
    try:
        import uvicorn
        from fastapi import FastAPI, Request
        from fastapi.responses import StreamingResponse
        from pydantic import BaseModel
    except ImportError:
        print("FastAPI required. Install with: pip install fastapi uvicorn pydantic")
        return
    
    # Create FastAPI app
    try:
        app = FastAPI(title="YApp API - Full REST + RPC")
    except Exception as e:
        print(f"❌ Server: Failed to create FastAPI app: {e}")
        return
    
    # Get command tree from yaapp_engine service
    try:
        command_tree = yaapp_engine.get_command_tree()
    except Exception as e:
        print(f"❌ Server: Failed to get command tree: {e}")
        return
    
    # Add REST endpoints
    _add_rest_endpoints(app, yaapp_engine, command_tree)
    
    # Add RPC endpoints (keep existing functionality)
    _add_rpc_endpoints(app, yaapp_engine)
    
    # Start server
    try:
        uvicorn.run(app, host=host, port=port, reload=reload)
    except Exception as e:
        print(f"❌ Server: Failed to start server: {e}")
        return



def _add_rest_endpoints(app, yaapp_engine, command_tree: dict, path_prefix: str = ""):
    """Add REST endpoints for each plugin and method."""
    from pydantic import BaseModel
    from fastapi import Request
    
    class DynamicRequest(BaseModel):
        model_config = {"extra": "allow"}
    
    # Add describe endpoint for current level
    describe_path = f"{path_prefix}/_describe"
    
    def make_describe_endpoint(tree):
        def describe_endpoint():
            """Describe available commands at this level."""
            return {"plugins": list(tree.keys())}
        return describe_endpoint
    
    app.get(describe_path)(make_describe_endpoint(command_tree))
    
    # Add endpoints for each command/plugin
    for command_name, command_info in command_tree.items():
        command_type = command_info.get('type', 'unknown')
        
        if command_type == 'command':
            # Direct function endpoint (e.g., /greet)
            command_path = f"{path_prefix}/{command_name}"
            
            def make_function_endpoint(cmd_name):
                async def function_endpoint(request: Request, body: DynamicRequest = None):
                    """Execute function with automatic streaming support."""
                    try:
                        # Get arguments from request body
                        args = body.model_dump() if body else {}
                        
                        # Check if streaming is requested via headers
                        accept_header = request.headers.get('accept', '')
                        is_streaming = 'text/event-stream' in accept_header
                        
                        # Execute function using yaapp-engine
                        result = await yaapp_engine.execute(cmd_name, **args)
                        
                        # Handle Result objects
                        if hasattr(result, 'is_ok') and hasattr(result, 'unwrap'):
                            if result.is_ok():
                                response_data = result.unwrap()
                                
                                # Handle streaming response
                                if is_streaming:
                                    return _create_streaming_response(response_data)
                                else:
                                    return response_data
                            else:
                                error_response = {"error": result.as_error}
                                if is_streaming:
                                    return _create_streaming_response(error_response)
                                else:
                                    return error_response
                        else:
                            # Fallback for non-Result return values
                            if is_streaming:
                                return _create_streaming_response(result)
                            else:
                                return result
                                
                    except Exception as e:
                        error_response = {"error": str(e)}
                        accept_header = request.headers.get('accept', '')
                        if 'text/event-stream' in accept_header:
                            return _create_streaming_response(error_response)
                        else:
                            return error_response
                
                return function_endpoint
            
            endpoint_func = make_function_endpoint(command_name)
            app.post(
                command_path,
                summary=f"Execute {command_name}",
                description=f"Execute {command_name} function"
            )(endpoint_func)
            
        elif command_type == 'group':
            # Group/class endpoints (e.g., /core/init)
            plugin_path = f"{path_prefix}/{command_name}"
            
            # Add plugin describe endpoint
            def make_plugin_describe(plugin_name, plugin_info):
                def plugin_describe():
                    return {
                        "plugin": plugin_name,
                        "type": plugin_info.get('type', 'unknown'),
                        "commands": list(plugin_info.get('commands', {}).keys()) if 'commands' in plugin_info else []
                    }
                return plugin_describe
            
            app.get(f"{plugin_path}/_describe")(make_plugin_describe(command_name, command_info))
            
            # Add method endpoints
            methods = command_info.get('commands', {})
            for method_name in methods:
                method_path = f"{plugin_path}/{method_name}"
                
                def make_method_endpoint(plugin_name, method_name):
                    async def method_endpoint(request: Request, body: DynamicRequest = None):
                        """Execute plugin method with automatic streaming support."""
                        try:
                            # Get arguments from request body
                            args = body.model_dump() if body else {}
                            
                            # Check if streaming is requested via headers
                            accept_header = request.headers.get('accept', '')
                            is_streaming = 'text/event-stream' in accept_header
                            
                            # Execute using yaapp_engine with dot notation
                            command_name = f"{plugin_name}.{method_name}"
                            result = await yaapp_engine.execute(command_name, **args)
                            
                            # Handle Result objects
                            if result.is_ok():
                                response_data = result.unwrap()
                                # Handle streaming response
                                if is_streaming:
                                    return _create_streaming_response(response_data)
                                else:
                                    return response_data
                            else:
                                error_response = {"error": result.as_error}
                            
                            if is_streaming:
                                return _create_streaming_response(error_response)
                            else:
                                return error_response
                                    
                        except Exception as e:
                            error_response = {"error": str(e)}
                            accept_header = request.headers.get('accept', '')
                            if 'text/event-stream' in accept_header:
                                return _create_streaming_response(error_response)
                            else:
                                return error_response
                    
                    return method_endpoint
                
                endpoint_func = make_method_endpoint(command_name, method_name)
                app.post(
                    method_path,
                    summary=f"Execute {command_name}.{method_name}",
                    description=f"Execute {method_name} method on {command_name} plugin"
                )(endpoint_func)


def _create_streaming_response(data):
    """Create streaming response for SSE."""
    from fastapi.responses import StreamingResponse
    
    async def generate():
        import json
        if hasattr(data, '__aiter__'):
            # Async generator
            async for item in data:
                yield f"data: {json.dumps(item)}\n\n"
        elif hasattr(data, '__iter__') and not isinstance(data, (str, bytes, dict)):
            # Regular generator/iterable
            for item in data:
                yield f"data: {json.dumps(item)}\n\n"
        else:
            # Single item
            yield f"data: {json.dumps(data)}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Cache-Control"
        }
    )


def _add_rpc_endpoints(app, yaapp_engine):
    """Add RPC endpoints (keep existing functionality)."""
    from pydantic import BaseModel
    
    class RPCRequest(BaseModel):
        function: str
        args: dict = {}
    
    @app.get("/_describe_rpc")
    def describe_rpc():
        """Describe available functions."""
        functions = {}
        for name, (metadata, exposer) in yaapp_engine.registry.list_items().items():
            obj = metadata.get('obj')
            if not obj:
                continue
            obj_type = 'unknown'
            if inspect.isclass(obj):
                obj_type = 'class'
            elif hasattr(obj, 'execute_call'):
                obj_type = 'custom_exposer'
            elif callable(obj):
                obj_type = 'function'
            else:
                obj_type = 'instance'
            
            functions[name] = {
                'type': obj_type,
                'obj_type': type(obj).__name__,
                'exposer_type': type(exposer).__name__,
                'has_execute_call': hasattr(obj, 'execute_call'),
                'methods': [m for m in dir(obj) if not m.startswith('_') and callable(getattr(obj, m))] if hasattr(obj, '__dict__') else []
            }
        return {"functions": functions}
    
    @app.post("/_rpc")
    async def rpc_endpoint(request: RPCRequest):
        """RPC function execution."""
        function_name = request.function
        arguments = request.args
        
        print(f"🔍 RPC: Received call for '{function_name}' with args {arguments}")
        
        # Use yaapp_engine.execute for all function calls (supports dot notation)
        try:
            result = await yaapp_engine.execute(function_name, **arguments)
            
            if result.is_ok():
                print(f"✅ RPC: Successfully executed '{function_name}'")
                return result.unwrap()
            else:
                print(f"❌ RPC: Failed to execute '{function_name}': {result.as_error}")
                return {"error": result.as_error}
        except Exception as e:
            error_msg = f"RPC execution failed: {str(e)}"
            print(f"❌ RPC: Failed to execute '{function_name}': {error_msg}")
            return {"error": error_msg}