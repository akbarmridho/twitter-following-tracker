from src.config import Config
from src import connect, Config, App
from time import sleep
from dotenv import load_dotenv
import logging
import traceback

if __name__ == '__main__':
    load_dotenv()
    config = Config()

    connect(config)

    app = App(config)

    app._initialize()

    # handle app exception

    while True:
        try:
            app.sync()
        except Exception:
            logging.exception(traceback.format_exc())

        sleep(config.SYNC_INTERVAL)
