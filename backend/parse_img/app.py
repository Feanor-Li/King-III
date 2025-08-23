# app.py
import os
import base64
import json
from dotenv import load_dotenv
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
import anthropic
from dedalus_labs import AsyncDedalus, DedalusRunner

load_dotenv()
client = AsyncDedalus(api_key=os.getenv("api_key"))
runner = DedalusRunner(client)

# Claude client for image processing
claude_client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

app = FastAPI()

@app.post("/chat")
async def chat(payload: dict):
    """
    Process Image
    """
    user_msg = payload.get("message", "")
    resp = await runner.run(
        input="Calculate 15 + 29",
        model="openai/gpt-4.1"
    )
    # Pull the first text output
    text = resp.final_output
    return JSONResponse({"text": text or ""})

@app.post("/detect_objects")
async def detect_objects(file: UploadFile = File(...)):
    """
    Object detection on uploaded image using Claude
    Returns object locations and bounding boxes
    """
    try:
        # Read the uploaded image
        image_bytes = await file.read()
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        
        # Get image media type
        media_type = file.content_type if file.content_type else "image/jpeg"
        
        # Use Claude to analyze the image for object detection
        response = claude_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type,
                                "data": image_base64
                            }
                        },
                        {
                            "type": "text",
                            "text": "Analyze this image and detect all objects. For each object found, provide the name and estimated bounding box coordinates in format: object_name: [x1, y1, x2, y2] where coordinates are percentages (0-100) of image dimensions. Return results in JSON format like: {\"objects\": [{\"name\": \"object_name\", \"bbox\": [x1, y1, x2, y2]}]}"
                        }
                    ]
                }
            ]
        )
        
        # Parse the response to extract object locations
        detection_result = response.content[0].text
        
        # Prepare JSON message for MCP server
        mcp_message = {
            "type": "object_detection_result",
            "data": {
                "objects_detected": detection_result,
                "filename": file.filename,
                "content_type": file.content_type,
                "timestamp": os.environ.get('TIMESTAMP', ''),
                "source": "python_fastapi_server"
            }
        }
        
        # Send to MCP server (assuming it's running on port 9900)
        try:
            import requests
            mcp_response = requests.post(
                "http://localhost:9900/receive_message",
                json=mcp_message,
                timeout=5
            )
            if mcp_response.status_code == 200:
                try:
                    print(f"MCP Server response: {mcp_response.json()}")
                except:
                    print(f"MCP Server response (text): {mcp_response.text}")
            else:
                print(f"MCP Server error: {mcp_response.status_code} - {mcp_response.text}")
            
            # For now, just log the message we would send
            print(f"Message to MCP: {json.dumps(mcp_message, indent=2)}")
            print(f"Sent to MCP server: {mcp_response.status_code}")
        except Exception as mcp_error:
            print(f"Failed to send to MCP: {str(mcp_error)}")
        
        return JSONResponse({
            "objects_detected": detection_result,
            "filename": file.filename,
            "content_type": file.content_type,
            "mcp_sent": True
        })
        
    except Exception as e:
        return JSONResponse({
            "error": f"Error processing image: {str(e)}"
        }, status_code=500)

@app.post("/test_mcp_communication")
async def test_mcp_communication():
    """
    Test MCP communication without Claude API
    """
    # Create a test message
    mcp_message = {
        "type": "test_message",
        "data": {
            "message": "Hello from Python FastAPI server!",
            "timestamp": "2025-08-23T20:00:00Z",
            "source": "python_fastapi_server",
            "test_objects": [
                {"name": "test_car", "bbox": [10, 20, 50, 80]},
                {"name": "test_person", "bbox": [60, 30, 90, 90]}
            ]
        }
    }
    
    # Send to MCP server
    try:
        import requests
        mcp_response = requests.post(
            "http://localhost:9900/receive_message",
            json=mcp_message,
            timeout=5
        )
        print(f"✅ Sent to MCP server: {mcp_response.status_code}")
        print(f"MCP Response: {mcp_response.text}")
        
        return JSONResponse({
            "status": "success",
            "mcp_response_code": mcp_response.status_code,
            "mcp_response": mcp_response.json() if mcp_response.status_code == 200 else mcp_response.text,
            "message_sent": mcp_message
        })
        
    except Exception as mcp_error:
        print(f"❌ Failed to send to MCP: {str(mcp_error)}")
        return JSONResponse({
            "status": "failed",
            "error": str(mcp_error),
            "message_attempted": mcp_message
        }, status_code=500)

