# Copyright 2023 iiPython

# Modules
from redis import Redis
from pymongo import MongoClient

from shuttle.utils import config, logger

# Initialization
mongo_config = config.database
mongo_auth_config = mongo_config.get("authentication", {})

# Setup MongoDB client
logger.info("Connecting to MongoDB ....")
client = MongoClient(
    mongo_config["address"],
    mongo_config["port"],
    **mongo_auth_config,
)

# Database reference
db = client.shuttle

# Setup Redis connection
logger.info("Connecting to Redis ....")
redis = Redis(
    host = config.redis["address"],
    port = config.redis["port"],
    username = "default",
    password = config.redis["password"],
    decode_responses = True
)
if redis.ping():
    logger.info("Redis connection established!")
