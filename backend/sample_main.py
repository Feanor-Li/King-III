import os
import asyncio
from dedalus_labs import AsyncDedalus, DedalusRunner
from dotenv import load_dotenv

load_dotenv()

def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b


async def main():
    client = AsyncDedalus(api_key=os.getenv("api_key"))
    runner = DedalusRunner(client)

    response = await runner.run(
        input="Calculate 15 + 29",
        model="openai/gpt-4.1",
        tools=[add]
    )

    print(response.final_output)

if __name__ == "__main__":
    asyncio.run(main())