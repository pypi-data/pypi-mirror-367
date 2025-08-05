# VS Code MCP Installation Guide

## One-Click Installation

Copy and paste this URL into your browser address bar to install the Screenshot MCP Server directly in VS Code:

```
vscode:mcp/install?{"name":"screenshot-mcp-server","gallery":true,"command":"dotnet","args":["run","--project","https://github.com/metamintbtc/desktop_screenshot_mcp_server.git"],"url":"https://github.com/metamintbtc/desktop_screenshot_mcp_server","env":{}}
```

## Manual Installation Steps

### 1. Prerequisites
- Windows 10/11
- .NET 10 Runtime
- VS Code with GitHub Copilot extension
- Git (optional, for development)

### 2. Clone Repository
```bash
git clone https://github.com/metamintbtc/desktop_screenshot_mcp_server.git
cd desktop_screenshot_mcp_server
```

### 3. Build Project
```bash
dotnet build -c Release
```

### 4. Configure VS Code
Add to your VS Code settings.json:

```json
{
  "github.copilot.chat.mcp.servers": {
    "screenshot-mcp-server": {
      "command": "dotnet",
      "args": ["run", "--project", "C:/path/to/your/ScreenshotMcpServer.csproj"],
      "description": "Windows Screenshot MCP Server"
    }
  }
}
```

### 5. Restart VS Code
- Close and reopen VS Code
- The MCP server will be available in GitHub Copilot chat

## Usage Examples

Once installed, use natural language in Copilot chat:

- "Take a screenshot of all my monitors"
- "Capture just the primary screen"
- "Show me information about my displays" 
- "Simulate pressing Print Screen"

## Troubleshooting

### Server Not Starting
- Verify .NET 10 is installed: `dotnet --version`
- Check file paths in settings.json are correct
- Ensure project builds without errors: `dotnet build`

### Permission Issues
- Run VS Code as Administrator if needed
- Check Windows permissions for screenshot functionality

### Multiple Monitors Not Detected
- Verify all monitors are properly connected
- Check Windows display settings
- Restart the MCP server in VS Code

## Support

For issues or questions:
- [GitHub Issues](https://github.com/metamintbtc/desktop_screenshot_mcp_server/issues)
- [GitHub Discussions](https://github.com/metamintbtc/desktop_screenshot_mcp_server/discussions)
