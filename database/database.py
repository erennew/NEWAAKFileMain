# (©) RaviBots - Luffy Bot DB

import pymongo
from config import DB_URI, DB_NAME

dbclient = pymongo.MongoClient(DB_URI)
database = dbclient[DB_NAME]
user_data = database['users']

# Check if a user exists in DB
async def present_user(user_id: int):
    return bool(user_data.find_one({'_id': user_id}))

# Add new user
async def add_user(user_id: int):
    if not await present_user(user_id):
        user_data.insert_one({'_id': user_id})

# Return full user list
async def full_userbase():
    return [doc['_id'] for doc in user_data.find()]

# Remove user
async def del_user(user_id: int):
    user_data.delete_one({'_id': user_id})

# Get total user count
async def total_users():
    return user_data.count_documents({})
#user_data.create_index([('_id', pymongo.ASCENDING)], unique=True)
