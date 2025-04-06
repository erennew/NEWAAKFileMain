# (©) WeekendsBotz
import pymongo
from typing import List, Optional
from config import DB_URI, DB_NAME
from pymongo.errors import (
    ConnectionFailure,
    OperationFailure,
    DuplicateKeyError
)
import logging

# Initialize logger
logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        self._client: Optional[pymongo.MongoClient] = None
        self._db: Optional[pymongo.database.Database] = None
        self.user_data: Optional[pymongo.collection.Collection] = None
        
        # Connection settings
        self.connect_timeout = 5000  # 5 seconds
        self.server_selection_timeout = 5000
        self.max_pool_size = 100
        self.min_pool_size = 10
        
        self._initialize()

    def _initialize(self):
        """Initialize database connection with error handling"""
        try:
            self._client = pymongo.MongoClient(
                DB_URI,
                connectTimeoutMS=self.connect_timeout,
                serverSelectionTimeoutMS=self.server_selection_timeout,
                maxPoolSize=self.max_pool_size,
                minPoolSize=self.min_pool_size
            )
            
            # Test the connection
            self._client.admin.command('ping')
            self._db = self._client[DB_NAME]
            self.user_data = self._db['users']
            
            # Create indexes if they don't exist
            self._create_indexes()
            
        except ConnectionFailure as e:
            logger.error(f"Database connection failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Database initialization error: {e}")
            raise

    def _create_indexes(self):
        """Create necessary indexes"""
        try:
            self.user_data.create_index(
                [('_id', pymongo.ASCENDING)],
                name="user_id_index"
           )
            self.log(__name__).info("Database indexes created")
        except OperationFailure as e:
            self.log(__name__).warning(f"Index creation skipped: {e}")

    async def present_user(self, user_id: int) -> bool:
        """Check if user exists in database"""
        try:
            return bool(self.user_data.find_one({'_id': user_id}))
        except Exception as e:
            logger.error(f"Error checking user presence: {e}")
            return False

    async def add_user(self, user_id: int) -> bool:
        """Add new user to database"""
        try:
            if not await self.present_user(user_id):
                self.user_data.insert_one({'_id': user_id})
                return True
            return False
        except DuplicateKeyError:
            return False  # User already exists
        except Exception as e:
            logger.error(f"Error adding user: {e}")
            return False

    async def full_userbase(self) -> List[int]:
        """Get list of all user IDs"""
        try:
            return [doc['_id'] for doc in self.user_data.find({})]
        except Exception as e:
            logger.error(f"Error fetching userbase: {e}")
            return []

    async def del_user(self, user_id: int) -> bool:
        """Remove user from database"""
        try:
            result = self.user_data.delete_one({'_id': user_id})
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error deleting user: {e}")
            return False

    async def total_users(self) -> int:
        """Get total user count"""
        try:
            return self.user_data.count_documents({})
        except Exception as e:
            logger.error(f"Error counting users: {e}")
            return 0

    def close(self):
        """Cleanly close database connection"""
        try:
            if self._client:
                self._client.close()
        except Exception as e:
            logger.error(f"Error closing connection: {e}")

# Initialize database instance
db = Database()

# Legacy functions for backward compatibility
async def present_user(user_id: int) -> bool:
    return await db.present_user(user_id)

async def add_user(user_id: int) -> bool:
    return await db.add_user(user_id)

async def full_userbase() -> List[int]:
    return await db.full_userbase()

async def del_user(user_id: int) -> bool:
    return await db.del_user(user_id)

async def total_users() -> int:
    return await db.total_users()
