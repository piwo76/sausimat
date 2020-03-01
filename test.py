import asyncio

from sausimat.sausimat import Sausimat

def run():
    sausimat = Sausimat()
    asyncio.run(sausimat.run())

run()