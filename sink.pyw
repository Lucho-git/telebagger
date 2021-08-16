import time
import asyncio


async def one():
    await asyncio.sleep(10)
    print('One | 10 secs')


async def two():
    await asyncio.sleep(5)
    print('Two | 5 secs')


async def three():
    await asyncio.sleep(20)
    print('Three | 20 secs')
