from src.config import Config
from src import connect, Config, App
from time import sleep
from dotenv import load_dotenv
from io import StringIO
import logging
import os
import traceback

if __name__ == '__main__':

    if 'DYNO' not in os.environ:
        try:
            f = open('env.txt', 'r')
            content = f.read()
            f.close()
            load_dotenv(stream=StringIO(content))
        except IOError:
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

        print(f"Waiting {config.SYNC_INTERVAL} seconds for the next run")
        sleep(config.SYNC_INTERVAL)
