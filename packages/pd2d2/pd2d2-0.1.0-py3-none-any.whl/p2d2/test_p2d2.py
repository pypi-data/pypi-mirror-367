import time

from toomanysessions import SessionedServer
from loguru import logger as log

from src.p2d2 import Database

if __name__ == "__main__":
    d = Database()
    log.warning(d.dummy.analytics.__dict__)
    api: SessionedServer = d._api
    api.thread.start()
    time.sleep(100)