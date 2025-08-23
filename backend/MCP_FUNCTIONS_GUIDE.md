# 📖 MCP Server - Adding New Functions Guide

## 🏗️ **Architecture Overview**

Your MCP server follows this structure:
- **TypeScript Source**: `sample_project/src/` → **Compiled JavaScript**: `dist/sample_project/src/`
- **Server runs from**: `dist/sample_project/src/index.js`

## 📁 **Files to Modify for New Functions**

### **1. Add Route Registration**
**File**: `sample_project/src/transport/http.ts`

```typescript
// Add your new endpoint in the switch statement
switch (url.pathname) {
    case '/mcp':
        await handleMcpRequest(req, res, config);
        break;
    case '/receive_message':
        await handleReceiveMessage(req, res);
        break;
    case '/your_new_endpoint':  // ← ADD HERE
        await handleYourNewFunction(req, res);
        break;
    default:
        handleNotFound(res);
}
```

### **2. Create Handler Function**
**File**: `sample_project/src/transport/http.ts`

```typescript
// Add your handler function at the bottom of the file
async function handleYourNewFunction(req: IncomingMessage, res: ServerResponse): Promise<void> {
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
        
        const requestData = JSON.parse(body);
        console.log('🚀 New function called:', JSON.stringify(requestData, null, 2));
        
        // YOUR LOGIC HERE
        const result = {
            processed_at: new Date().toISOString(),
            input_data: requestData,
            processed_by: 'your_new_function',
            result: 'success'  // Your processing result
        };
        
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({
            status: 'function_executed',
            data: result
        }));
        
    } catch (error) {
        console.error('Error in new function:', error);
        res.statusCode = 400;
        res.end(JSON.stringify({ error: 'Processing failed' }));
    }
}
```

### **3. Add MCP Tools (Optional)**
**File**: `sample_project/src/tools/`

Create new tool files like:
- `sample_project/src/tools/your_tool.ts`
- Update `sample_project/src/tools/index.ts`

### **4. Update Server Registration (Optional)**
**File**: `sample_project/src/server.ts`

```typescript
// Add your tool to the tools list
serverInstance.setRequestHandler(ListToolsRequestSchema, async () => ({
    tools: [
        parseImgToolDefinition,
        yourNewToolDefinition,  // ← ADD HERE
    ],
}));

// Add your tool handler
serverInstance.setRequestHandler(CallToolRequestSchema, async (request) => {
    const { name, arguments: args } = request.params;
    
    switch (name) {
        case "CamPro_Parse_Img":
            return await handleParseImgTool(service_client, args);
        case "YourNewTool":  // ← ADD HERE
            return await handleYourNewTool(service_client, args);
        default:
            return {
                content: [{ type: "text", text: `Unknown tool: ${name}` }],
                isError: true,
            };
    }
});
```

## 🔨 **Build & Deploy Process**

### **Step 1: Modify TypeScript Files**
Edit files in `sample_project/src/`

### **Step 2: Build**
```bash
npm run build
```

### **Step 3: Restart Server**
```bash
PORT=9900 npm start
```

## 🧪 **Testing Your New Function**

### **Test HTTP Endpoint**
```bash
curl -X POST "http://localhost:9900/your_new_endpoint" \
  -H "Content-Type: application/json" \
  -d '{"test": "data"}'
```

### **Test from Python Server**
```python
import requests

response = requests.post(
    "http://localhost:9900/your_new_endpoint",
    json={"your": "data"},
    timeout=5
)
print(response.json())
```

## 📂 **File Structure Reference**

```
backend/
├── sample_project/src/          # TypeScript source
│   ├── transport/
│   │   └── http.ts             # ← Add routes & handlers here
│   ├── tools/                  # ← Add MCP tools here
│   │   ├── index.ts
│   │   └── your_tool.ts
│   ├── server.ts               # ← Register MCP tools here
│   └── index.ts                # Entry point
├── dist/sample_project/src/     # Compiled JavaScript (auto-generated)
└── package.json
```

## 🚀 **Quick Example: Add Calculator Function**

### **1. Add Route** (in `http.ts`)
```typescript
case '/calculate':
    await handleCalculator(req, res);
    break;
```

### **2. Add Handler** (in `http.ts`)
```typescript
async function handleCalculator(req: IncomingMessage, res: ServerResponse): Promise<void> {
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
        
        const data = JSON.parse(body);
        const { operation, a, b } = data;
        
        let result;
        switch (operation) {
            case 'add': result = a + b; break;
            case 'subtract': result = a - b; break;
            case 'multiply': result = a * b; break;
            case 'divide': result = b !== 0 ? a / b : 'Division by zero'; break;
            default: result = 'Unknown operation';
        }
        
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({
            status: 'calculation_complete',
            data: {
                operation,
                operands: [a, b],
                result,
                processed_by: 'calculator_function'
            }
        }));
        
    } catch (error) {
        res.statusCode = 400;
        res.end(JSON.stringify({ error: 'Invalid calculation request' }));
    }
}
```

### **3. Build & Test**
```bash
npm run build
PORT=9900 npm start

# Test
curl -X POST "http://localhost:9900/calculate" \
  -H "Content-Type: application/json" \
  -d '{"operation": "add", "a": 5, "b": 3}'
```

## ⚡ **Pro Tips**

1. **Always build after TypeScript changes**: `npm run build`
2. **Check logs in both terminals**: Python server + MCP server
3. **Use debug console.log**: Add `console.log('🔍 Debug:', data)`
4. **Test endpoints individually** before integrating
5. **Keep function names consistent** across files

## 🔧 **Common Issues**

- **404 Not Found**: Route not registered in switch statement
- **TypeScript errors**: Check syntax in `.ts` files
- **Server not restarting**: Kill process and restart manually
- **JSON parsing errors**: Validate request body format

## 📋 **Current Working Setup**

### **Existing Endpoints:**
- `/health` - Server health check
- `/mcp` - MCP protocol endpoint
- `/sse` - Server-sent events
- `/receive_message` - Receives object detection results from Python server

### **Current Communication Flow:**
```
Python FastAPI (8080) → MCP Server (9900)
Object Detection → /receive_message → Processing & Logging
```

---

**🎯 Your MCP server is now ready for custom functions!** 🚀