import asyncio
from core.agents.jd_decoder_agent import JDDecoderAgent

async def test():
    agent = JDDecoderAgent(llm_provider="gemini")
    jd_data = {
        "title": "Kỹ sư",
        "content": "Tuyển kỹ sư điện tử, biết vẽ AutoCAD.",
    }
    result = agent.decode(jd_data)
    print(result)

asyncio.run(test())
