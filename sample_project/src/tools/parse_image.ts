import { Tool, CallToolResult } from '@modelcontextprotocol/sdk/types.js';
import { CamProClient } from '../client.js';
import { ParseImgArgs } from '../types.js';

/**
 * Tool definition for [tool_name]
 */
export const parseImgToolDefinition: Tool = {
    name: "CamPro_Parse_Img",
    description: "Description of what this tool does and when to use it.",
    inputSchema: {
        type: "object",
        properties: {
            // Define input schema
        },
        required: ["required_field"],
    },
};

/**
 * Type guard for [tool] arguments
 */
function isParseImgArgs(args: unknown): args is ParseImgArgs {
    return (
        typeof args === "object" &&
        args !== null &&
        "required_field" in args &&
        typeof (args as { required_field: unknown }).required_field === "string"
    );
}

/**
 * Handles [tool] tool calls
 */
export async function handleParseImgTool(
    client: CamProClient, 
    args: unknown
): Promise<CallToolResult> {
    try {
        if (!args) {
            throw new Error("No arguments provided");
        }

        if (!isParseImgArgs(args)) {
            throw new Error("Invalid arguments for CamPro_[action]");
        }

        const result = await client.performRequest(args);
        
        return {
            content: [{ type: "text", text: result }],
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