#!/usr/bin/env node
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
import { config as loadEnv } from 'dotenv';
loadEnv();
import { loadConfig } from './config.js';
import { parseArgs } from './cli.js';
import { CamProServer } from './server.js';
import { runStdioTransport, startHttpTransport } from './transport/index.js';
/**
 * Transport selection logic:
 * 1. --stdio flag forces STDIO transport
 * 2. Default: HTTP transport for production compatibility
 */
function main() {
    return __awaiter(this, void 0, void 0, function* () {
        try {
            const config = loadConfig();
            const cliOptions = parseArgs();
            if (cliOptions.stdio) {
                // STDIO transport for local development
                const server = new CamProServer(config.apiKey);
                yield runStdioTransport(server.getServer());
            }
            else {
                // HTTP transport for production/cloud deployment
                const port = cliOptions.port || config.port;
                startHttpTransport(Object.assign(Object.assign({}, config), { port }));
            }
        }
        catch (error) {
            console.error("Fatal error running [Service] server:", error);
            process.exit(1);
        }
    });
}
main();
