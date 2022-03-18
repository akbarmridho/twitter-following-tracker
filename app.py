from src.config import Config
from src import connect, Config, App
from time import sleep
from dotenv import load_dotenv
from io import StringIO
from http.client import IncompleteRead
import logging
import traceback
import sys

if __name__ == '__main__':

    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s [%(levelname)s] %(message)s",
                        handlers=[
                            logging.FileHandler('logfile.log'),
                            logging.StreamHandler(sys.stdout)
                        ])

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

    while True:
        try:
            app.sync()
        except IncompleteRead:
            logging.warning(
                'Failed to fetch following. Incomplete read. Shutting down ...')
            logging.exception(traceback.format_exc())
            break
        except Exception:
            logging.exception(traceback.format_exc())

        logging.info(
            f"Waiting {config.SYNC_INTERVAL} seconds for the next run")
        sleep(config.SYNC_INTERVAL)
