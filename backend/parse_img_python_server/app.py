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
claude = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

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
    image: UploadFile = File(...),
    prompt: str = Form("Describe this image:")
):
    """
    Sends an uploaded image to Claude using a base64 image content block.
    """
    data = await image.read()
    media = image.content_type or "image/png"

    resp = claude.messages.create(
        model="claude-opus-4-20250514",
        max_tokens=512,
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image",
                 "source": {"type": "base64", "media_type": media, "data": base64.b64encode(data).decode("utf-8")}
                }
            ]
        }]
    )
    text = resp.content[0].text
    return JSONResponse({"text": text})