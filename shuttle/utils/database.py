# Copyright 2023 iiPython

# Modules
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
