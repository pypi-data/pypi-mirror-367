#!/usr/bin/env node

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";
import { z } from "zod";
import screenshot from "screenshot-desktop";
import { writeFileSync } from "fs";
import { join } from "path";
import { tmpdir } from "os";

// Schema for screenshot tool arguments
const ScreenshotArgsSchema = z.object({
  displayId: z.number().optional().describe("Display ID to screenshot (optional, defaults to all displays)"),
  filename: z.string().optional().describe("Custom filename for the screenshot (optional)"),
  format: z.enum(["png", "jpg"]).optional().default("png").describe("Image format (png or jpg)"),
});

class ScreenshotMCPServer {
  private server: Server;

  constructor() {
    this.server = new Server(
      {
        name: "screenshot-mcp-server",
        version: "1.0.0",
      },
      {
        capabilities: {
          tools: {},
        },
      }
    );

    this.setupToolHandlers();
    this.setupErrorHandling();
  }

  private setupErrorHandling(): void {
    this.server.onerror = (error) => {
      console.error("[MCP Error]", error);
    };

    process.on("SIGINT", async () => {
      await this.server.close();
      process.exit(0);
    });
  }

  private setupToolHandlers(): void {
    // List available tools
    this.server.setRequestHandler(ListToolsRequestSchema, async () => {
      return {
        tools: [
          {
            name: "take_screenshot",
            description: "Take a screenshot of specified display(s). Can capture all displays or a specific display by ID.",
            inputSchema: {
              type: "object",
              properties: {
                displayId: {
                  type: "number",
                  description: "Display ID to screenshot (optional, defaults to all displays)",
                },
                filename: {
                  type: "string",
                  description: "Custom filename for the screenshot (optional)",
                },
                format: {
                  type: "string",
                  enum: ["png", "jpg"],
                  default: "png",
                  description: "Image format (png or jpg)",
                },
              },
            },
          },
          {
            name: "list_displays",
            description: "List all available displays with their information",
            inputSchema: {
              type: "object",
              properties: {},
            },
          },
        ],
      };
    });

    // Handle tool calls
    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      const { name, arguments: args } = request.params;

      try {
        switch (name) {
          case "take_screenshot":
            return await this.takeScreenshot(args);
          case "list_displays":
            return await this.listDisplays();
          default:
            throw new Error(`Unknown tool: ${name}`);
        }
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : String(error);
        return {
          content: [
            {
              type: "text",
              text: `Error: ${errorMessage}`,
            },
          ],
        };
      }
    });
  }

  private async takeScreenshot(args: any) {
    const validatedArgs = ScreenshotArgsSchema.parse(args || {});
    const { displayId, filename, format } = validatedArgs;

    try {
      let screenshots;
      
      if (displayId !== undefined) {
        // Screenshot specific display
        screenshots = await screenshot({ screen: displayId, format });
      } else {
        // Screenshot all displays
        screenshots = await screenshot.all({ format });
      }

      // Handle single screenshot vs multiple screenshots
      const screenshotArray = Array.isArray(screenshots) ? screenshots : [screenshots];
      const results = [];

      for (let i = 0; i < screenshotArray.length; i++) {
        const img = screenshotArray[i];
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
        const displaySuffix = screenshotArray.length > 1 ? `_display_${i}` : '';
        const finalFilename = filename 
          ? `${filename}${displaySuffix}.${format}`
          : `screenshot_${timestamp}${displaySuffix}.${format}`;
        
        const filePath = join(tmpdir(), finalFilename);
        writeFileSync(filePath, img);
        
        results.push({
          displayId: displayId !== undefined ? displayId : i,
          filename: finalFilename,
          path: filePath,
          size: img.length,
          format: format,
        });
      }

      const resultText = results.length === 1 
        ? `Screenshot saved: ${results[0].filename} (${results[0].size} bytes) at ${results[0].path}`
        : `${results.length} screenshots saved:\n${results.map(r => `- ${r.filename} (Display ${r.displayId}, ${r.size} bytes) at ${r.path}`).join('\n')}`;

      return {
        content: [
          {
            type: "text",
            text: resultText,
          },
        ],
      };
    } catch (error) {
      throw new Error(`Failed to take screenshot: ${error instanceof Error ? error.message : String(error)}`);
    }
  }

  private async listDisplays() {
    try {
      // Get display information
      const displays = await screenshot.listDisplays();
      
      const displayInfo = displays.map((display, index) => ({
        id: index,
        name: display.name || `Display ${index}`,
        width: display.width,
        height: display.height,
        primary: display.primary || false,
      }));

      const displayText = displayInfo.map(d => 
        `Display ${d.id}: ${d.name} (${d.width}x${d.height})${d.primary ? ' [PRIMARY]' : ''}`
      ).join('\n');

      return {
        content: [
          {
            type: "text",
            text: `Available displays (${displayInfo.length}):\n${displayText}`,
          },
        ],
      };
    } catch (error) {
      throw new Error(`Failed to list displays: ${error instanceof Error ? error.message : String(error)}`);
    }
  }

  async run(): Promise<void> {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    console.error("Screenshot MCP server running on stdio");
  }
}

const server = new ScreenshotMCPServer();
server.run().catch(console.error);
