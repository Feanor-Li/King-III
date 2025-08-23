var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
import { createServer } from 'http';
import { StreamableHTTPServerTransport } from '@modelcontextprotocol/sdk/server/streamableHttp.js';
import { SSEServerTransport } from '@modelcontextprotocol/sdk/server/sse.js';
import { randomUUID } from 'crypto';
import { createStandaloneServer } from '../server.js';
const sessions = new Map();
export function startHttpTransport(config) {
    const httpServer = createServer();
    httpServer.on('request', (req, res) => __awaiter(this, void 0, void 0, function* () {
        const url = new URL(req.url, `http://${req.headers.host}`);
        switch (url.pathname) {
            case '/mcp':
                yield handleMcpRequest(req, res, config);
                break;
            case '/sse':
                yield handleSSERequest(req, res, config);
                break;
            case '/health':
                handleHealthCheck(res);
                break;
            default:
                handleNotFound(res);
        }
    }));
    const host = config.isProduction ? '0.0.0.0' : 'localhost';
    httpServer.listen(config.port, host, () => {
        logServerStart(config);
    });
}
function handleMcpRequest(req, res, config) {
    return __awaiter(this, void 0, void 0, function* () {
        const sessionId = req.headers['mcp-session-id'];
        if (sessionId) {
            const session = sessions.get(sessionId);
            if (!session) {
                res.statusCode = 404;
                res.end('Session not found');
                return;
            }
            return yield session.transport.handleRequest(req, res);
        }
        if (req.method === 'POST') {
            yield createNewSession(req, res, config);
            return;
        }
        res.statusCode = 400;
        res.end('Invalid request');
    });
}
function handleSSERequest(req, res, config) {
    return __awaiter(this, void 0, void 0, function* () {
        const serverInstance = createStandaloneServer(config.apiKey);
        const transport = new SSEServerTransport('/sse', res);
        try {
            yield serverInstance.connect(transport);
            console.log('SSE connection established');
        }
        catch (error) {
            console.error('SSE connection error:', error);
            res.statusCode = 500;
            res.end('SSE connection failed');
        }
    });
}
function createNewSession(req, res, config) {
    return __awaiter(this, void 0, void 0, function* () {
        const serverInstance = createStandaloneServer(config.apiKey);
        const transport = new StreamableHTTPServerTransport({
            sessionIdGenerator: () => randomUUID(),
            onsessioninitialized: (sessionId) => {
                sessions.set(sessionId, { transport, server: serverInstance });
                console.log('New [Service] session created:', sessionId);
            }
        });
        transport.onclose = () => {
            if (transport.sessionId) {
                sessions.delete(transport.sessionId);
                console.log('[Service] session closed:', transport.sessionId);
            }
        };
        try {
            yield serverInstance.connect(transport);
            yield transport.handleRequest(req, res);
        }
        catch (error) {
            console.error('Streamable HTTP connection error:', error);
            res.statusCode = 500;
            res.end('Internal server error');
        }
    });
}
function handleHealthCheck(res) {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({
        status: 'healthy',
        timestamp: new Date().toISOString(),
        service: '[service]-mcp',
        version: '0.2.0'
    }));
}
function handleNotFound(res) {
    res.writeHead(404, { 'Content-Type': 'text/plain' });
    res.end('Not Found');
}
function logServerStart(config) {
    const displayUrl = config.isProduction
        ? `Port ${config.port}`
        : `http://localhost:${config.port}`;
    console.log(`[Service] MCP Server listening on ${displayUrl}`);
    if (!config.isProduction) {
        console.log('Put this in your client config:');
        console.log(JSON.stringify({
            "mcpServers": {
                "[service]": {
                    "url": `http://localhost:${config.port}/mcp`
                }
            }
        }, null, 2));
        console.log('For backward compatibility, you can also use the /sse endpoint.');
    }
}
