var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { CallToolRequestSchema, ListToolsRequestSchema, InitializedNotificationSchema, } from "@modelcontextprotocol/sdk/types.js";
import { CamProClient } from './client.js';
import { parseImgToolDefinition, handleParseImgTool, } from './tools/index.js';
export function createStandaloneServer(apiKey) {
    const serverInstance = new Server({
        name: "org/CamPro",
        version: "0.2.0",
    }, {
        capabilities: {
            tools: {},
        },
    });
    const service_client = new CamProClient(apiKey);
    serverInstance.setNotificationHandler(InitializedNotificationSchema, () => __awaiter(this, void 0, void 0, function* () {
        console.log('CamPro MCP client initialized');
    }));
    serverInstance.setRequestHandler(ListToolsRequestSchema, () => __awaiter(this, void 0, void 0, function* () {
        return ({
            tools: [parseImgToolDefinition],
        });
    }));
    serverInstance.setRequestHandler(CallToolRequestSchema, (request) => __awaiter(this, void 0, void 0, function* () {
        const { name, arguments: args } = request.params;
        switch (name) {
            case "CamPro_[action]":
                return yield handleParseImgTool(service_client, args);
            default:
                return {
                    content: [{ type: "text", text: `Unknown tool: ${name}` }],
                    isError: true,
                };
        }
    }));
    return serverInstance;
}
export class CamProServer {
    constructor(apiKey) {
        this.apiKey = apiKey;
    }
    getServer() {
        return createStandaloneServer(this.apiKey);
    }
}
