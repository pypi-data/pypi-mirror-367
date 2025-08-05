#!/usr/bin/env python3
"""
Screenshot MCP Server - Python UVX Wrapper
Starts the .NET Screenshot MCP Server via Python for cross-platform UVX installation
"""

import subprocess
import sys
import os
import shutil
import urllib.request
import zipfile
import tempfile
from pathlib import Path

def find_dotnet():
    """Find dotnet executable"""
    dotnet_paths = [
        "dotnet",
        "/usr/local/share/dotnet/dotnet",
        "/usr/share/dotnet/dotnet", 
        "C:/Program Files/dotnet/dotnet.exe",
        "C:/Program Files (x86)/dotnet/dotnet.exe"
    ]
    
    for path in dotnet_paths:
        if shutil.which(path):
            return path
    
    return None

def download_and_extract_server():
    """Download and extract the .NET server from GitHub"""
    repo_url = "https://github.com/metamintbtc/desktop_screenshot_mcp_server/archive/refs/heads/main.zip"
    
    # Create temp directory
    temp_dir = tempfile.mkdtemp(prefix="screenshot_mcp_")
    zip_path = os.path.join(temp_dir, "server.zip")
    
    print("📥 Downloading Screenshot MCP Server from GitHub...")
    urllib.request.urlretrieve(repo_url, zip_path)
    
    # Extract
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(temp_dir)
    
    # Find the extracted directory
    extracted_dir = os.path.join(temp_dir, "desktop_screenshot_mcp_server-main")
    return extracted_dir

def build_server(server_dir):
    """Build the .NET server"""
    dotnet = find_dotnet()
    if not dotnet:
        print("❌ .NET Runtime not found. Please install .NET 10 from https://dotnet.microsoft.com/download")
        sys.exit(1)
    
    print("🔨 Building Screenshot MCP Server...")
    result = subprocess.run([
        dotnet, "build", 
        os.path.join(server_dir, "ScreenshotMcpServer.csproj"),
        "-c", "Release"
    ], capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"❌ Build failed: {result.stderr}")
        sys.exit(1)
    
    return os.path.join(server_dir, "bin", "Release", "net10.0-windows", "ScreenshotMcpServer.exe")

def main():
    """Main entry point for UVX"""
    try:
        # Check if we're on Windows
        if os.name != 'nt':
            print("❌ Screenshot MCP Server requires Windows")
            sys.exit(1)
        
        # Download and build server
        server_dir = download_and_extract_server()
        server_exe = build_server(server_dir)
        
        # Run the server
        print("🚀 Starting Screenshot MCP Server...")
        subprocess.run([server_exe], check=True)
        
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
