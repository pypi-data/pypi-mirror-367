#!/usr/bin/env python3
"""Generic yaapp client for testing examples"""

import sys
import json
import requests
import argparse
from pathlib import Path
# Add src directory to path
sys.path.insert(0, "../../src")

def main():
    parser = argparse.ArgumentParser(description="Generic yaapp client")
    parser.add_argument("--server", default="http://localhost:8000", help="Server URL")
    parser.add_argument("function", help="Function to call")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    # Parse known args to allow dynamic parameters
    args, unknown = parser.parse_known_args()
    
    # Parse dynamic parameters
    params = {}
    i = 0
    while i < len(unknown):
        if unknown[i].startswith('--'):
            param_name = unknown[i][2:]  # Remove --
            if i + 1 < len(unknown) and not unknown[i + 1].startswith('--'):
                param_value = unknown[i + 1]
                # Try to parse as JSON, fallback to string
                try:
                    params[param_name] = json.loads(param_value)
                except json.JSONDecodeError:
                    params[param_name] = param_value
                i += 2
            else:
                params[param_name] = True
                i += 1
        else:
            i += 1
    
    # Make RPC call
    try:
        response = requests.post(
            f"{args.server}/_rpc",
            json={
                "function": args.function,
                "arguments": params
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if args.json:
                print(json.dumps(result, indent=2))
            else:
                if isinstance(result, str):
                    print(result)
                else:
                    print(json.dumps(result, indent=2))
        else:
            print(f"Error: HTTP {response.status_code}")
            print(response.text)
            sys.exit(1)
            
    except requests.exceptions.RequestException as e:
        print(f"Connection error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()