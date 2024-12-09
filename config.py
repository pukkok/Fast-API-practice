import os
from dotenv import load_dotenv

load_dotenv()

config = {
  "BASE_URL" : os.getenv("BASE_URL"),
  "SECRET_KEY" : os.getenv("SECRET_KEY"),
  "MONGODB_URI" : os.getenv("MONGODB_URI")
}