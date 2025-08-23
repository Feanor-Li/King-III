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
import FormData from 'form-data';
import fetch from 'node-fetch';
const sessions = new Map();
export function startHttpTransport(config) {
    const httpServer = createServer();
    httpServer.on('request', (req, res) => __awaiter(this, void 0, void 0, function* () {
        const url = new URL(req.url, `http://${req.headers.host}`);
        console.log('🔍 Incoming request to:', url.pathname);
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
            case '/receive_message':
                yield handleReceiveMessage(req, res);
                break;
            case '/detect_objects':
                yield handleDetectObjects(req, res);
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
function handleReceiveMessage(req, res) {
    return __awaiter(this, void 0, void 0, function* () {
        if (req.method !== 'POST') {
            res.statusCode = 405;
            res.end('Method Not Allowed');
            return;
        }
        
        try {
            let body = '';
            for await (const chunk of req) {
                body += chunk;
            }
            
            const message = JSON.parse(body);
            console.log('📨 Received message from Python server:', JSON.stringify(message, null, 2));
            
            // Process the message (you can add your logic here)
            const processedMessage = {
                received_at: new Date().toISOString(),
                original_message: message,
                processed_by: 'dedalus_mcp_server',
                status: 'success'
            };
            
            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({
                status: 'message_received',
                data: processedMessage
            }));
            
        } catch (error) {
            console.error('Error processing message:', error);
            res.statusCode = 400;
            res.end(JSON.stringify({ error: 'Invalid JSON message' }));
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

function handleDetectObjects(req, res) {
    return __awaiter(this, void 0, void 0, function* () {
        if (req.method !== 'POST') {
            res.statusCode = 405;
            res.end('Method Not Allowed');
            return;
        }
        
        try {
            console.log('🎯 MCP Server: Received object detection request');
            
            // Parse multipart form data
            let body = Buffer.alloc(0);
            for await (const chunk of req) {
                body = Buffer.concat([body, chunk]);
            }
            
            // Forward the request to Python server
            const formData = new FormData();
            
            // Extract file from the request body (assuming it's multipart/form-data)
            const boundary = req.headers['content-type']?.split('boundary=')[1];
            if (!boundary) {
                throw new Error('No boundary found in content-type');
            }
            
            // For now, let's extract the file data manually
            const bodyStr = body.toString();
            const fileMatch = bodyStr.match(/filename="([^"]+)"/);
            const fileName = fileMatch ? fileMatch[1] : 'image.jpg';
            
            // Extract binary data between boundaries
            const parts = bodyStr.split(`--${boundary}`);
            let fileData = null;
            for (const part of parts) {
                if (part.includes('filename=')) {
                    const headerEnd = part.indexOf('\r\n\r\n');
                    if (headerEnd !== -1) {
                        const binaryStart = headerEnd + 4;
                        const binaryEnd = part.lastIndexOf('\r\n--');
                        if (binaryEnd !== -1) {
                            fileData = Buffer.from(part.slice(binaryStart, binaryEnd), 'binary');
                        }
                    }
                    break;
                }
            }
            
            if (!fileData) {
                throw new Error('Could not extract file data from request');
            }
            
            formData.append('file', fileData, fileName);
            
            console.log('🚀 MCP Server: Forwarding request to Python server...');
            
            const pythonResponse = yield fetch('http://localhost:8080/detect_objects', {
                method: 'POST',
                body: formData,
                headers: formData.getHeaders()
            });
            
            if (!pythonResponse.ok) {
                throw new Error(`Python server responded with ${pythonResponse.status}: ${pythonResponse.statusText}`);
            }
            
            const result = yield pythonResponse.json();
            console.log('✅ MCP Server: Got response from Python server');
            
            // Return the result to the user
            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({
                status: 'object_detection_complete',
                data: result,
                processed_by: 'mcp_server_proxy',
                timestamp: new Date().toISOString()
            }));
            
        } catch (error) {
            console.error('❌ MCP Server: Error in object detection proxy:', error);
            res.statusCode = 500;
            res.end(JSON.stringify({ 
                error: 'Object detection failed', 
                details: error.message,
                processed_by: 'mcp_server_proxy'
            }));
        }
    });
}
