"""
Environment variables for the Python MCP server.
When deploying to Deploxy, .deploxy.json file's "injectedEnv" object is injected into the process environment.

Example .deploxy.json file:
{
    "authToken": "YOUR_AUTH_TOKEN",
    "defaultDeployRegion": "us-east-1",
    "stdioArgsIndex": "--args",
    "mcpPath": "/mcp",
    "packageType": "py",
    "injectedEnv": {
        "DATABASE_URL": "YOUR_DATABASE_URL"
    }
}
"""

import os

ENV = {
    # These environment variables are injected by Deploxy automatically.
    "SERVERLESS_FUNCTION_REGION": os.getenv("SERVERLESS_FUNCTION_REGION"),
    "USER_REQUEST_COUNTRY": os.getenv("USER_REQUEST_COUNTRY"),
    "SAMPLE_ENV": os.getenv("SAMPLE_ENV"),
    
    # You can access the injected environment variables like this:
    # "DATABASE_URL": os.getenv("DATABASE_URL"),
}