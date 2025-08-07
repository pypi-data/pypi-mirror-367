# OpenAI MCP Server

A Model Context Protocol server that provides tools to manage OpenAI API keys & spending.

> [!CAUTION]
> This server can access the OpenAI API and may represent a security risk. Exercise caution when using this MCP server to ensure this does not expose any sensitive data.

## Available Tools

TODO: Add tool info here

## Installation

### Using uv (recommended)

When using [`uv`](https://docs.astral.sh/uv/) no specific installation is needed. We will use [`uvx`](https://docs.astral.sh/uv/guides/tools/) to directly run *mcp-server-openai*.

### Using PIP

Alternatively you can install `mcp-server-openai` via pip:

```
pip install mcp-server-openai
```

After installation, you can run it as a script using:

```
python -m mcp_server_openai
```

## Configuration

### Configure for Claude.app

Add to your Claude settings:

<details>
<summary>Using uvx</summary>

```json
{
  "mcpServers": {
    "openai": {
      "command": "uvx",
      "args": ["mcp-server-openai"],
      "env": {
        "OPENAI_ADMIN_API_KEY": "your_openai_admin_api_key"
      }
    }
  }
}
```
</details>

<details>
<summary>Using docker</summary>

```json
{
  "mcpServers": {
    "openai": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "mcp/openai"],
      "env": {
        "OPENAI_ADMIN_API_KEY": "your_openai_admin_api_key"
      }
    }
  }
}
```
</details>

<details>
<summary>Using pip installation</summary>

```json
{
  "mcpServers": {
    "openai": {
      "command": "python",
      "args": ["-m", "mcp_server_openai"],
      "env": {
        "OPENAI_ADMIN_API_KEY": "your_openai_admin_api_key"
      }
    }
  }
}
```
</details>

## Debugging

You can use the MCP inspector to debug the server. For uvx installations:

```
npx @modelcontextprotocol/inspector uvx mcp-server-openai
```

Or if you've installed the package in a specific directory or are developing on it:

```
cd path/to/servers/src/openai
npx @modelcontextprotocol/inspector uv run mcp-server-openai
```

## Contributing

We encourage contributions to help expand and improve mcp-server-openai. Whether you want to add new tools, enhance existing functionality, or improve documentation, your input is valuable.

Pull requests are welcome! Feel free to contribute new ideas, bug fixes, or enhancements to make mcp-server-openai even more powerful and useful.

## License

mcp-server-openai is licensed under the MIT License. This means you are free to use, modify, and distribute the software, subject to the terms and conditions of the MIT License. For more details, please see the LICENSE file in the project repository.
