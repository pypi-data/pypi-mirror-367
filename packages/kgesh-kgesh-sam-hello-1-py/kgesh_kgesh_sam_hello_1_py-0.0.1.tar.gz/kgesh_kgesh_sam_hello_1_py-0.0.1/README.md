# Deploxy Python Quick Start

**[Deploxy](https://deploxy.com?utm_source=github_readme)** is a REAL proxy for deploying **Stdio MCP server to serverless** platform.

This is the Python version of the Deploxy quick start example, built with **fastMCP** for simplified MCP server development.

### What this guide covers

- Deploying your Python Stdio MCP Server to PyPI package with Deploxy.
- Transforming it into a secure, private MCP server.
- Keeping your source code safe while providing users with a lightweight proxy package to install.

## Installation and Usage

### Using uvx (recommended)

```bash
# Run directly without installation
uvx kgesh-kgesh-sam-hello-1-py

# Or install and run
uvx --from kgesh-kgesh-sam-hello-1-py say-hello
```

### Using pip

```bash
pip install kgesh-kgesh-sam-hello-1-py
say-hello
```

## Development

### Prerequisites

- Python 3.8 or higher
- pip or uv
- fastMCP library

### Setup

```bash
# Clone and enter the directory
cd quick-start-py

# Install dependencies
pip install -e .

# Or with uv
uv pip install -e .
```

### Running locally

```bash
# Run the server directly
python -m quick_start_py.main

# Or using the installed script
say-hello
```

## Deployment Steps

### Step 1: Prepare Your Project

First, ensure your project is ready to be published as a standard PyPI package.

1. **Configure `pyproject.toml`**: Make sure your `pyproject.toml` has the required `name`, `version`, and `project.scripts` properties set correctly.
2. **Build Your Project**: Install dependencies and test your build.
   ```bash
   pip install build
   python -m build
   ```

### Step 2: Check your PyPI package

To understand the problem Deploxy solves, let's first publish the package the traditional way.

```bash
# Build and publish to PyPI
python -m build
twine upload dist/*
```

Now, go to your package's page on PyPI (`https://pypi.org/project/YOUR_PACKAGE_NAME/`) and you will see that all your source code is publicly visible.

> **Important**: This step is for this quick start demonstration only. In a real production, you will **skip this step entirely**.

### Step 3: Create and Configure `.deploxy.json`

1. **Create the file**

   You have two options to create the `.deploxy.json` file.

   **Option 1: Use the CLI**

   Run the following command in your project root:

   ```bash
   npx @deploxy/cli init
   ```

   **Option 2: Use the Dashboard**

   Go to the [Deploy new project](https://www.deploxy.com/dashboard/new) to create a new project, then copy the generated JSON configuration into a `.deploxy.json` file in your project root.

2. **Add your Auth Token**: Open the file and add your `authToken`. If you don't have one, you can get it from the [Tokens page](https://www.deploxy.com/account/settings/tokens).

   ```json .deploxy.json
   {
     "authToken": "your-auth-token-here",
     "defaultDeployRegion": "us-east-1",
     "stdioArgsIndex": "--args",
     "mcpPath": "/mcp",
     "packageType": "py",
     "injectedEnv": {}
   }
   ```

### Step 4: Deploy with Deploxy

Now, instead of `twine upload`, run the `deploy` command.

> **Note**: If you completed [Step 2](#step-2-check-your-pypi-package) and published a version to PyPI, you must increment the `version` in your `pyproject.toml` before running `deploy`. Both PyPI and Deploxy require a new version for each deployment.

```bash
npx @deploxy/cli deploy
```

You can monitor the deployment status on the [Deploxy Dashboard](https://www.deploxy.com/dashboard).

Once deployment is complete, check your package page on PyPI again. You will see that the code has been replaced with the Deploxy proxy client.

That's it! Your Python package is now deployed with Deploxy, keeping your source code private while providing a secure proxy for your users.

---

## How It Works: The Deploxy Magic

When you deploy with Deploxy, you're not just publishing a package; you're creating a secure, private backend for your MCP server.

The code that end-users download and run via `uvx` is a lightweight **proxy client**. This proxy client takes user requests (like a **ToolCall**) and streams them to your actual MCP server, which is running securely in the serverless cloud.

### Understanding the `.deploxy.json` properties

- **`authToken`**: This is the token required to authenticate and deploy your package to Deploxy.

- **`defaultDeployRegion`**: This is the default AWS region where your MCP server will run if the end-user does not specify a particular region. To give your end-users the fastest experience, they can specify a region using the `--region` flag when they run your package (`uvx your-pkg --region us-east-1`). If the flag is omitted, this default region is used.

  > With the Deploxy Pro plan, the `--region` parameter is not needed. Requests are automatically routed to the nearest region for the end-user.

- **`stdioArgsIndex`**: This option specifies the arguments that are passed directly to your MCP server. For example, when an end-user runs `uvx your-pkg --args user-api-key`, your server can access `user-api-key` from `sys.argv`.

- **`injectedEnv`**: This is an object of environment variables that are accessible only within your MCP server (e.g., `os.getenv("DATABASE_URL")`). These are completely hidden from the end-user because they only interact with the proxy client, not your secure server code.

- **`mcpPath`** and **`packageType`**: You generally don't need to change these. For Python projects, `packageType` should be `"py"`.

> **Security Warning**: The `.deploxy.json` file contains your sensitive `authToken`. **Never commit this file to a public repository.** Ensure it is listed in your `.gitignore` file.