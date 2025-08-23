var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
export function runStdioTransport(server) {
    return __awaiter(this, void 0, void 0, function* () {
        const transport = new StdioServerTransport();
        try {
            yield server.connect(transport);
            console.error("[Service] MCP Server running on stdio");
        }
        catch (error) {
            console.error("Failed to start STDIO transport:", error);
            throw error;
        }
    });
}
