from services import LLMService
import asyncio

service = LLMService()

async def main():
    input = "아스피린 먹어도 돼?"
    result = await service.consult_drug_safety(1, 1, input)
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
