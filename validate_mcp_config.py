#!/usr/bin/env python3
"""
Validate MCP server configuration without running it.
Checks imports, structure, and configuration.
"""

import sys
import ast
import os

def validate_mcp_server():
    """Validate the MCP server configuration."""
    print("🔍 Validating MCP Server Configuration")
    print("=" * 60)

    errors = []
    warnings = []

    # Read the MCP server file
    mcp_file = "/home/user/tamil-panchang-api/mcp_server.py"

    if not os.path.exists(mcp_file):
        print(f"❌ ERROR: {mcp_file} not found")
        return False

    with open(mcp_file, 'r') as f:
        content = f.read()

    # Check 1: Parse Python syntax
    print("\n1️⃣  Checking Python syntax...")
    try:
        ast.parse(content)
        print("   ✅ Valid Python syntax")
    except SyntaxError as e:
        print(f"   ❌ Syntax error: {e}")
        errors.append(f"Syntax error: {e}")
        return False

    # Check 2: Required imports
    print("\n2️⃣  Checking required imports...")
    required_imports = [
        'mcp.server',
        'mcp.server.sse',
        'starlette.applications',
        'starlette.routing',
        'starlette.middleware',
        'httpx',
        'uvicorn'
    ]

    for imp in required_imports:
        if imp in content:
            print(f"   ✅ {imp}")
        else:
            print(f"   ❌ Missing: {imp}")
            errors.append(f"Missing import: {imp}")

    # Check 3: CORS middleware
    print("\n3️⃣  Checking CORS configuration...")
    if 'CORSMiddleware' in content:
        print("   ✅ CORS middleware imported")
        if 'allow_origins=["*"]' in content or "allow_origins=['*']" in content:
            print("   ✅ CORS allows all origins")
        else:
            print("   ⚠️  Warning: CORS origins might be restricted")
            warnings.append("CORS origins might be restricted")
    else:
        print("   ❌ CORS middleware not found")
        errors.append("CORS middleware not configured")

    # Check 4: Routes
    print("\n4️⃣  Checking routes...")
    routes = {
        '/sse': 'Route("/sse"',
        '/health': 'Route("/health"',
        '/messages/': 'Mount("/messages/"'
    }

    for route, pattern in routes.items():
        if pattern in content:
            print(f"   ✅ {route} endpoint configured")
        else:
            print(f"   ❌ {route} endpoint missing")
            errors.append(f"Missing route: {route}")

    # Check 5: HTTP methods
    print("\n5️⃣  Checking HTTP methods...")
    if 'methods=["GET", "OPTIONS"]' in content or "methods=['GET', 'OPTIONS']" in content:
        print("   ✅ /sse accepts GET and OPTIONS")
    else:
        print("   ⚠️  /sse might not handle OPTIONS (CORS preflight)")
        warnings.append("/sse might not handle CORS preflight")

    # Check 6: Tool definitions
    print("\n6️⃣  Checking tool definitions...")
    tools = ['get_panchang', 'get_today_panchang']
    for tool in tools:
        if f'@server.call_tool()' in content or '@mcp.tool()' in content:
            if tool in content:
                print(f"   ✅ {tool} tool defined")
            else:
                print(f"   ❌ {tool} tool missing")
                errors.append(f"Missing tool: {tool}")
        else:
            print(f"   ⚠️  Tool decorator not found")
            break

    # Check 7: SSE Transport
    print("\n7️⃣  Checking SSE transport...")
    if 'SseServerTransport' in content:
        print("   ✅ SSE transport configured")
        if 'connect_sse' in content:
            print("   ✅ SSE connection handler present")
        else:
            print("   ❌ SSE connection handler missing")
            errors.append("SSE connection handler missing")
    else:
        print("   ❌ SSE transport not configured")
        errors.append("SSE transport not configured")

    # Check 8: FastAPI base URL
    print("\n8️⃣  Checking FastAPI integration...")
    if 'FASTAPI_BASE' in content:
        if 'http://localhost:8000' in content:
            print("   ✅ FastAPI base URL configured (localhost:8000)")
        else:
            print("   ⚠️  FastAPI base URL might be non-standard")
            warnings.append("FastAPI base URL is non-standard")
    else:
        print("   ❌ FastAPI base URL not defined")
        errors.append("FastAPI base URL not defined")

    # Summary
    print("\n" + "=" * 60)
    print("📊 Validation Summary")
    print("=" * 60)

    if errors:
        print(f"\n❌ Found {len(errors)} error(s):")
        for error in errors:
            print(f"   • {error}")

    if warnings:
        print(f"\n⚠️  Found {len(warnings)} warning(s):")
        for warning in warnings:
            print(f"   • {warning}")

    if not errors and not warnings:
        print("\n✅ All checks passed! MCP server configuration looks good.")
        return True
    elif not errors:
        print("\n✅ No critical errors found. Warnings should be reviewed.")
        return True
    else:
        print("\n❌ Configuration has errors that need to be fixed.")
        return False

if __name__ == "__main__":
    success = validate_mcp_server()
    sys.exit(0 if success else 1)
