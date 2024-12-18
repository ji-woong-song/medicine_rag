from services import LLMService
import asyncio

service = LLMService()

async def main():
    input = "갑자기 머리가 빙글 빙글 도는 것 같은데 어떻게 해야할까?"
    func = await service.route_prompt(1, 1, input)
    result = await func(1, 1, input)
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
