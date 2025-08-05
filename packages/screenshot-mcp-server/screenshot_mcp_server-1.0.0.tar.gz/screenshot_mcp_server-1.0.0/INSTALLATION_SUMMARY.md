# 🚀 Screenshot MCP Server - Ready to Install!

Your Windows Screenshot MCP Server is now ready and deployed to GitHub! Here are the installation options:

## ✨ One-Click Installation (VS Code 2025)

### Option 1: Direct MCP Install URL
Copy this URL and paste it in your browser:

```
vscode:mcp/install?{"name":"screenshot-mcp-server","gallery":true,"command":"dotnet","args":["run","--project","https://github.com/metamintbtc/desktop_screenshot_mcp_server.git"],"url":"https://github.com/metamintbtc/desktop_screenshot_mcp_server","env":{}}
```

### Option 2: GitHub Repository Link
📁 **Repository**: https://github.com/metamintbtc/desktop_screenshot_mcp_server

Users can install from VS Code:
1. Press `F1` in VS Code
2. Type "MCP: Install Server"  
3. Enter: `https://github.com/metamintbtc/desktop_screenshot_mcp_server.git`

## 🛠️ Manual Configuration

Add to VS Code settings.json:

```json
{
  "github.copilot.chat.mcp.servers": {
    "screenshot-mcp-server": {
      "command": "dotnet",
      "args": ["run", "--project", "C:/path/to/ScreenshotMcpServer.csproj"],
      "description": "Windows Screenshot MCP Server"
    }
  }
}
```

## 🎯 Features Available

Once installed, users can ask GitHub Copilot:

- **"Take a screenshot of all my screens"** → Captures all monitors
- **"Capture just the primary monitor"** → Screenshots main display  
- **"Show me information about my displays"** → Display details
- **"Simulate pressing Print Screen"** → Windows Print Screen emulation

## 📸 Screenshot Functionality

✅ **Multi-Monitor Support** - Captures all connected displays
✅ **Primary Screen Only** - Individual monitor screenshots  
✅ **Desktop Integration** - Saves to Desktop with timestamps
✅ **Print Screen Simulation** - Native Windows functionality
✅ **.NET 10** - Modern, high-performance implementation

## 🔗 Links

- **GitHub Repository**: https://github.com/metamintbtc/desktop_screenshot_mcp_server
- **Installation Guide**: [INSTALLATION.md](https://github.com/metamintbtc/desktop_screenshot_mcp_server/blob/main/INSTALLATION.md)
- **Full Documentation**: [README.md](https://github.com/metamintbtc/desktop_screenshot_mcp_server/blob/main/README.md)

---

**Your Screenshot MCP Server is ready to use! 🎉**

The server will automatically appear in the VS Code MCP Extensions section once installed, just like the official MCP servers you referenced!
