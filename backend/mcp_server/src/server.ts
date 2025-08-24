import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import {
    CallToolRequestSchema,
    ListToolsRequestSchema,
    InitializedNotificationSchema,
} from "@modelcontextprotocol/sdk/types.js";
import { ParseImgClient } from './client.js';
import {
    parseImgToolDefinition,
    handleParseImgTool,
    detectObjectToolDefinition,
    handleDetectObjectTool,
} from './tools/index.js';

export function createStandaloneServer(apiKey: string): Server {
    const serverInstance = new Server(
        {
            name: "org/CamPro",
            version: "0.2.0",
        },
        {
            capabilities: {
                tools: {},
            },
        }
    );

    const service_client = new ParseImgClient();

    serverInstance.setNotificationHandler(InitializedNotificationSchema, async () => {
        console.log('CamPro MCP client initialized');
    });

    serverInstance.setRequestHandler(ListToolsRequestSchema, async () => ({
        tools: [parseImgToolDefinition, detectObjectToolDefinition],
    }));

    serverInstance.setRequestHandler(CallToolRequestSchema, async (request) => {
        const { name, arguments: args } = request.params;
        
        switch (name) {
            case "CamPro_ParseImg":
                return await handleParseImgTool(service_client, args);
            case "CamPro_DetectObj":
                return await handleDetectObjectTool(service_client, args);
            default:
                return {
                    content: [{ type: "text", text: `Unknown tool: ${name}` }],
                    isError: true,
                };
        }
    });

    return serverInstance;
}

export class CamProServer {
    private apiKey: string;

    constructor(apiKey: string) {
        this.apiKey = apiKey;
    }

    getServer(): Server {
        return createStandaloneServer(this.apiKey);
    }
}