# app.py
import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from dedalus_labs import AsyncDedalus, DedalusRunner

load_dotenv()
client = AsyncDedalus(api_key=os.getenv("api_key"))
runner = DedalusRunner(client)

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