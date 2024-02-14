import asyncio
import os

from core import check

files = os.listdir(r'proxy')
direct = 'proxy/'
asyncio.run(check(direct, files))
