from src.config import Config
from src import connect, Config, App
from dotenv import load_dotenv
from threading import Event
import logging
import traceback
import sys
from http.client import IncompleteRead

exit = Event()


def main():
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s [%(levelname)s] %(message)s",
                        handlers=[
                            logging.StreamHandler(sys.stdout)
                        ])

    config = Config()

    connect(config)

    app = App(config)

    app._initialize()

    while not exit.is_set():
        try:
            app.sync()
        except IncompleteRead:
            logging.warning(
                'Failed to fetch following. Incomplete read. Shutting down ...')
            logging.exception(traceback.format_exc())
            exit.set()
        except Exception:
            logging.exception(traceback.format_exc())

        logging.info(
            f"Waiting {config.SYNC_INTERVAL} seconds for the next run")

        exit.wait(config.SYNC_INTERVAL)


def quit(signo, __frame):
    logging.info(f"Interrupted by shutdown signal. Shutting down")
    exit.set()


if __name__ == '__main__':

    import signal

    for sig in ['TERM', 'HUP', 'INT']:
        signal.signal(getattr(signal, 'SIG' + sig), quit)

    main()
