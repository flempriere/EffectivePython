# Script implementation of the slow coroutine demonstration
# This allows the debug behaviour of `asyncio` to be seen

import asyncio
import time


async def slow_coroutine():
    time.sleep(0.5)


asyncio.run(slow_coroutine(), debug=True)
