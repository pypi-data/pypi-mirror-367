import * as vscode from 'vscode';

export function activate(context: vscode.ExtensionContext) {
    console.log('Screenshot MCP Server extension is now active!');
    
    // Register the MCP server configuration
    const disposable = vscode.commands.registerCommand('screenshotMcp.configure', () => {
        vscode.window.showInformationMessage('Screenshot MCP Server is ready to use with GitHub Copilot!');
    });

    context.subscriptions.push(disposable);
}

export function deactivate() {
    console.log('Screenshot MCP Server extension is now deactivated');
}
