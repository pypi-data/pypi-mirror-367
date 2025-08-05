# MCP Configuration Guide

## 🔧 Multiple Installation Methods

Your Screenshot MCP Server supports multiple configuration approaches:

### 1. Traditional MCP.json Configuration

Create or edit `mcp.json` in your workspace:

```json
{
  "mcpServers": {
    "screenshot-mcp-server": {
      "command": "dotnet",
      "args": [
        "run",
        "--project",
        "H:\\Screenshot_mcp\\ScreenshotMcpServer.csproj"
      ],
      "description": "Windows Screenshot MCP Server",
      "env": {}
    }
  }
}
```

### 2. VS Code Settings Integration

Add to your VS Code `settings.json`:

```json
{
  "github.copilot.chat.mcp.servers": {
    "screenshot-mcp-server": {
      "command": "dotnet",
      "args": ["run", "--project", "H:\\Screenshot_mcp\\ScreenshotMcpServer.csproj"],
      "description": "Windows Screenshot MCP Server"
    }
  }
}
```

### 3. Global MCP Configuration

For system-wide availability, place `mcp.json` in:

**Windows:**
```
%APPDATA%\Code\User\mcp.json
```

**macOS:**
```
~/Library/Application Support/Code/User/mcp.json
```

**Linux:**
```
~/.config/Code/User/mcp.json
```

### 4. Project-specific Configuration

Place `mcp.json` in your project root for workspace-specific MCP servers.

## 🎯 Configuration Options

### Environment Variables
```json
{
  "mcpServers": {
    "screenshot-mcp-server": {
      "command": "dotnet",
      "args": ["run", "--project", "ScreenshotMcpServer.csproj"],
      "env": {
        "SCREENSHOT_OUTPUT_DIR": "C:\\Screenshots",
        "SCREENSHOT_FORMAT": "PNG"
      }
    }
  }
}
```

### Debug Mode
```json
{
  "mcpServers": {
    "screenshot-mcp-server": {
      "command": "dotnet",
      "args": ["run", "--project", "ScreenshotMcpServer.csproj", "--verbosity", "detailed"],
      "description": "Windows Screenshot MCP Server (Debug)"
    }
  }
}
```

### Release Build
```json
{
  "mcpServers": {
    "screenshot-mcp-server": {
      "command": "H:\\Screenshot_mcp\\bin\\Release\\net10.0-windows\\ScreenshotMcpServer.exe",
      "args": [],
      "description": "Windows Screenshot MCP Server (Release)"
    }
  }
}
```

## 🔄 Configuration Priority

VS Code MCP loads configurations in this order:

1. **Workspace `mcp.json`** (highest priority)
2. **VS Code settings.json**
3. **Global MCP configuration**
4. **URL-based installation** (one-time setup)

## 📝 Example Complete mcp.json

```json
{
  "mcpServers": {
    "screenshot-mcp-server": {
      "command": "dotnet",
      "args": [
        "run",
        "--project",
        "H:\\Screenshot_mcp\\ScreenshotMcpServer.csproj"
      ],
      "description": "Windows Screenshot MCP Server",
      "env": {
        "DOTNET_ENVIRONMENT": "Production"
      }
    },
    "other-mcp-server": {
      "command": "python",
      "args": ["-m", "other_mcp_server"],
      "description": "Another MCP Server"
    }
  }
}
```

## ✅ Verification

After configuration, restart VS Code and verify the server is loaded:

1. Open GitHub Copilot chat
2. Ask: "What MCP servers are available?"
3. You should see "screenshot-mcp-server" in the list

The traditional `mcp.json` approach gives you full control over server configuration and is perfect for development and custom deployments!
