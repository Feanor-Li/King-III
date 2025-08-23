import asyncio, os
from dedalus_labs import AsyncDedalus, DedalusRunner
from dotenv import load_dotenv

load_dotenv()

async def main():
    # client = AsyncDedalus(api_key=os.getenv("ANTHROPIC_API_KEY"))
    client = AsyncDedalus(api_key="YOUR_API_KEY_HERE")
    runner = DedalusRunner(client)

    response = await runner.run(
        input="What was the score of the 2025 Wimbledon final?",
        model="openai/gpt-4o-mini"
    )

    print(response.final_output)

if __name__ == "__main__":
    asyncio.run(main())


