import asyncio

sema = asyncio.Semaphore(2)

async def test():
    async with sema:
        print('0%')
        await asyncio.sleep(5)
        print('100%')

async def main():
    async with asyncio.TaskGroup() as tg:
        for _ in range(4):
            tg.create_task(test())

asyncio.run(main())
