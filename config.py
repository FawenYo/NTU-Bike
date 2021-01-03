import os

import pymongo
from dotenv import load_dotenv

load_dotenv()


client = pymongo.MongoClient(os.getenv("MONGO_CLIENT"))
db = client["Database"]


LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")


GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

BORROW_RICH_MENU = os.getenv("BORROW_RICH_MENU")
RETURN_RICH_MENU = os.getenv("RETURN_RICH_MENU")
