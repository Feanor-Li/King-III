import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import {
    CallToolRequestSchema,
    ListToolsRequestSchema,
    InitializedNotificationSchema,
} from "@modelcontextprotocol/sdk/types.js";
import { CamProClient } from './client.js';
import {
    parseImgToolDefinition,
    handleParseImgTool,
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

    const service_client = new CamProClient(apiKey);

    serverInstance.setNotificationHandler(InitializedNotificationSchema, async () => {
        console.log('CamPro MCP client initialized');
    });

    serverInstance.setRequestHandler(ListToolsRequestSchema, async () => ({
        tools: [parseImgToolDefinition],
    }));

    serverInstance.setRequestHandler(CallToolRequestSchema, async (request) => {
        const { name, arguments: args } = request.params;
        
        switch (name) {
            case "CamPro_[action]":
                return await handleParseImgTool(service_client, args);
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