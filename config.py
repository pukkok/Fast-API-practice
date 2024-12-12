import os

# Configurations
class Config:
    MONGODB_URI = os.getenv("MONGODB_URI")
    BASE_URL = os.getenv("BASE_URL")
    SECRET_KEY = os.getenv("SECRET_KEY")