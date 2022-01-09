from src import connect, Config
from dotenv import load_dotenv
from io import StringIO
import os

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

    # telegram = Telegram(config)

    # telegram.setup()

    # Sheets(config)
