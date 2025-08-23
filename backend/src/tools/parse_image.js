var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
/**
 * Tool definition for [tool_name]
 */
export const parseImgToolDefinition = {
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
function isParseImgArgs(args) {
    return (typeof args === "object" &&
        args !== null &&
        "required_field" in args &&
        typeof args.required_field === "string");
}
/**
 * Handles [tool] tool calls
 */
export function handleParseImgTool(client, args) {
    return __awaiter(this, void 0, void 0, function* () {
        try {
            if (!args) {
                throw new Error("No arguments provided");
            }
            if (!isParseImgArgs(args)) {
                throw new Error("Invalid arguments for CamPro_[action]");
            }
            const result = yield client.performRequest(args);
            return {
                content: [{ type: "text", text: result }],
                isError: false,
            };
        }
        catch (error) {
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
    });
}
