from src import connect, Config, Telegram
from dotenv import load_dotenv

if __name__ == '__main__':
    load_dotenv()
    config = Config()

    connect(config)

    telegram = Telegram(config)

    telegram.setup()
