#!/usr/bin/env python3
"""
Issues Management Example - Demonstrates yaapp plugin architecture

This example shows:
- Storage plugin providing data persistence  
- Issues plugin built on top of storage
- Clean plugin layering and loose coupling
- Result pattern for error handling
- Both CLI and web interfaces automatically generated
"""

import sys
from pathlib import Path

# Add src to path to import yaapp
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from yaapp import Yaapp
from yaapp.plugins.storage.plugin import create_memory_storage_manager

# Create the main app instance
app = Yaapp()

# Set up storage plugin
storage = create_memory_storage_manager()
app.expose(storage, name="storage")

# Import and set up issues plugin (it will use the global app)
from yaapp.plugins.issues.plugin import IssuesPlugin
issues = IssuesPlugin(app)
app.expose(issues, name="issues")

# Add some convenience functions
@app.expose
def setup_demo():
    """Set up demo data for testing."""
    # Create sample issues
    result1 = app.execute_function("issues.create", 
                                  title="Fix login bug", 
                                  description="Users can't log in with special characters in password",
                                  reporter="alice@company.com",
                                  priority="high")
    
    result2 = app.execute_function("issues.create",
                                  title="Add dark mode",
                                  description="Users want dark mode option in settings",
                                  reporter="bob@company.com", 
                                  priority="medium",
                                  assignee="carol@company.com")
    
    if result1 and result2:
        issue1_id = result1.unwrap()
        issue2_id = result2.unwrap()
        
        # Add a comment
        app.execute_function("issues.add_comment",
                           issue_id=issue1_id,
                           text="I can reproduce this with passwords containing @ symbols",
                           author="eve@company.com")
        
        return f"Created sample issues: {issue1_id}, {issue2_id}"
    else:
        return "Failed to create sample data"

@app.expose
def show_all_issues():
    """Show all issues in the system."""
    result = app.execute_function("issues.list")
    if result:
        issues = result.unwrap()
        return {
            "total_issues": len(issues),
            "issues": issues
        }
    else:
        return {"error": result.as_error}

@app.expose
def create_bug_report(title: str, description: str, reporter: str):
    """Create a new bug report (high priority issue)."""
    result = app.execute_function("issues.create",
                                 title=title,
                                 description=description, 
                                 reporter=reporter,
                                 priority="high")
    if result:
        issue_id = result.unwrap()
        return {"success": True, "issue_id": issue_id}
    else:
        return {"success": False, "error": result.as_error}

if __name__ == "__main__":
    app.run()