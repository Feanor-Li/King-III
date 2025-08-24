import { Tool, CallToolResult } from '@modelcontextprotocol/sdk/types.js';
import { ParseImgClient } from '../client.js';
import { ParseImgArgs, DetectObjectArgs } from '../types.js';

/**
 * Tool definition for [tool_name]
 */
export const parseImgToolDefinition: Tool = {
    name: "Parse_Image_Into_Rules_Of_Thirds",
    description: "Analyzes the image following rules of thirds of photography, that is iso, shutter speed and aperture. And provides suggestion for configuration if you want to reproduce the same effect.",
    inputSchema: {
        type: "object",
        properties: {
            prompt: { type: "string" },
            imagePath: { type: "string" },
        },
        required: ["prompt", "imagePath"],
    }
};

export const detectObjectToolDefinition: Tool = {
    name: "Detect_Object_Tool",
    description: "Detect the important objects in the image",
    inputSchema: {
        type: "object",
        properties: {
            file: {type: "string"}
        },
        required: ["file"]
    }
}

function isObjectRecord(v: unknown): v is Record<string, unknown> {
  return typeof v === "object" && v !== null;
}

/** Type guard for tool arguments */
export function isParseImgArgs(args: unknown): args is ParseImgArgs {
  if (!isObjectRecord(args)) return false;

  // keys must exist
  if (!("prompt" in args) || !("imagePath" in args)) return false;

  // types must be string
  const { prompt, imagePath } = args as { prompt: unknown; imagePath: unknown };
  if (typeof prompt !== "string" || typeof imagePath !== "string") return false;

  // (optional) non-empty checks
  if (prompt.trim().length === 0) return false;
  if (imagePath.trim().length === 0) return false;

  return true;
}

export function isDetectObjectArgs(args: unknown): args is DetectObjectArgs {
    if (!isObjectRecord(args)) return false;

    if (!("file" in args)) return false;

    const {file} = args as {file: unknown};
    if (typeof file !== "string") return false;

    return true;
}

/**
 * Handles [tool] tool calls
 */
export async function handleParseImgTool(
    client: ParseImgClient, 
    args: unknown
): Promise<CallToolResult> {
    try {
        if (!args) {
            throw new Error("No arguments provided");
        }

        if (!isParseImgArgs(args)) {
            throw new Error("Invalid arguments for CamPro_[action]");
        }

        const result = await client.parseImage(args);
        
        return {
            content: [{ type: "text", text: result.result }],
            isError: false,
        };
    } catch (error) {
        return {
            content: [
                {
                    type: "text",
                    text: `Error: ${error instanceof Error ? error.message : String(error)}`,
                },
            ],
            isError: true,
        };
    }
}

export async function handleDetectObjectTool(
    client: ParseImgClient,
    args: unknown
): Promise<CallToolResult> {
    try {
        if (!args) {
            throw new Error("No arguments provided");
        }

        if (!isDetectObjectArgs(args)) {
            throw new Error("Invalid arguments for CamPro_[action]");
        }

        const result = await client.detectObject(args);
        
        return {
            content: [{ type: "text", text: result.result }],
            isError: false,
        };
    } catch (error) {
        return {
            content: [
                {
                    type: "text",
                    text: `Error: ${error instanceof Error ? error.message : String(error)}`,
                },
            ],
            isError: true,
        };
    }
}