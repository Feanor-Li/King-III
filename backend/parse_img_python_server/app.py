# app.py
import base64
import os
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from dedalus_labs import AsyncDedalus, DedalusRunner
from anthropic import Anthropic

load_dotenv()
dedalus_client = AsyncDedalus(api_key=os.getenv("api_key"))
runner = DedalusRunner(dedalus_client)
claude_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

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

@app.post("/img/claude")
async def parse_img(
    image: UploadFile = File(...)
):
    """
    Sends an uploaded image to Claude using a base64 image content block.
    """
    data = await image.read()
    image_base64 = base64.b64encode(data).decode('utf-8')
    media = image.content_type or "image/png"

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
                                "media_type": media,
                                "data": image_base64
                            }
                        },
                        {
                            "type": "text",
                            "text": "Analyze this photo and extract camera/photo parameters that would be useful for iPhone camera adjustments. Estimate values for: zoom level (1x, 2x, etc), brightness (-100 to 100), contrast (-100 to 100), highlights (-100 to 100), shadows (-100 to 100), saturation (-100 to 100), sharpness (-100 to 100), exposure compensation (-2 to 2), white balance (auto/sunny/cloudy/tungsten/fluorescent), focus mode (auto/manual), and any other relevant settings. Return in JSON format: {\"parameters\": [{\"name\": \"parameter_name\", \"value\": estimated_value, \"range\": \"min-max\", \"unit\": \"unit_type\"}]}"
                        }
                    ]
                }
            ]
        )
        
    text = response.content[0].text
    return JSONResponse({"text": text})

@app.post("/detect_objects")
async def detect_objects(file: UploadFile = File(...)):
    """
    Object detection on uploaded image using Claude
    Returns object locations and bounding boxes
    """
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
    return JSONResponse({"text": detection_result})