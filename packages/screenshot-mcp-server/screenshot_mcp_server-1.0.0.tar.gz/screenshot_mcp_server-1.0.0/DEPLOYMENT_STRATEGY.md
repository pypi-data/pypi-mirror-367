# 🔄 MCP Server Deployment Strategy

## 🎯 Problem: Remote Installation

Aktuell: Server läuft nur lokal via `dotnet run --project H:\...`
Ziel: Server verfügbar wie offizielle MCP Server

## 🚀 Lösungsoptionen:

### Option 1: UVX Package (Empfohlen ⚡)
```python
# pyproject.toml
[project]
name = "screenshot-mcp-server"
version = "1.0.0"
description = "Windows Screenshot MCP Server"
dependencies = []

[project.scripts]
screenshot-mcp-server = "screenshot_mcp_server:main"
```

**Installation URL:**
```
vscode:mcp/install?{"name":"screenshot-mcp-server","gallery":true,"command":"uvx","args":["screenshot-mcp-server"]}
```

### Option 2: NPM Package (Alternativ)
```json
{
  "name": "@metamintbtc/screenshot-mcp-server",
  "version": "1.0.0",
  "bin": {
    "screenshot-mcp-server": "./bin/screenshot-mcp-server.js"
  }
}
```

**Installation URL:**
```
vscode:mcp/install?{"name":"screenshot-mcp-server","gallery":true,"command":"npx","args":["-y","@metamintbtc/screenshot-mcp-server"]}
```

### Option 2: Docker Container
```dockerfile
FROM mcr.microsoft.com/dotnet/runtime:10.0-preview
COPY . /app
WORKDIR /app
ENTRYPOINT ["dotnet", "ScreenshotMcpServer.dll"]
```

**Installation URL:**
```
vscode:mcp/install?{"name":"screenshot-mcp-server","gallery":true,"command":"docker","args":["run","-i","--rm","metamintbtc/screenshot-mcp-server"]}
```

### Option 3: Hosted MCP Service
```
vscode:mcp/install?{"name":"screenshot-mcp-server","gallery":true,"url":"https://mcp.metamintbtc.com/sse"}
```

## 🎯 Empfohlener Weg: UVX Package

### Warum UVX? ⚡
✅ **Ultra-Fast** - Rust-basiert, extrem schnell
✅ **Zero Config** - Keine Python venv nötig  
✅ **Auto-Cleanup** - Temporäre Installation + Ausführung
✅ **Cross-Platform** - Funktioniert überall
✅ **Modern Standard** - Wie offizielle MCP Server 2025
✅ **Ein-Klick Installation** - Genau wie markitdown-mcp

### Implementation Plan:
1. **Python Wrapper** erstellen (startet .NET Server)
2. **PyPI Package** publishen
3. **Installation URL** generieren  
4. **Zur offiziellen Liste** hinzufügen

## ⚡ Next Steps:

1. Python UVX Wrapper implementieren
2. Package zu PyPI Registry pushen
3. Installation URL testen
4. Bei Microsoft für offizielle Liste bewerben
