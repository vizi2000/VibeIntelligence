"""
Zenith Coder Database Configuration
Following Directive 7: Performance & Scalability
Implements async database operations with connection pooling
"""

import logging
from typing import Optional, Dict, Any
from contextlib import asynccontextmanager

from databases import Database
from sqlalchemy import MetaData, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import asyncpg

from .config import settings
from .exceptions import DatabaseException

logger = logging.getLogger(__name__)

# Database URL from settings
DATABASE_URL = settings.DATABASE_URL

# Async database instance
database = Database(
    DATABASE_URL,
    min_size=5,
    max_size=settings.DATABASE_POOL_SIZE,
    ssl=settings.ENVIRONMENT == "production"
)

# SQLAlchemy setup
engine = create_engine(
    DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://"),
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    pool_pre_ping=True,  # Verify connections before use
    echo=settings.DEBUG
)

metadata = MetaData()
Base = declarative_base(metadata=metadata)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


async def init_db() -> None:
    """
    Initialize database connection with health check
    Following Directive 4: System Resilience
    """
    try:
        await database.connect()
        
        # Verify connection with simple query
        await database.fetch_one("SELECT 1")
        
        logger.info("✅ Database connection established successfully")
        
        # Log connection pool metrics (Directive 11: Monitoring)
        pool = database.connection()._pool
        logger.info(
            f"📊 Connection pool initialized: "
            f"min={pool._minsize}, max={pool._maxsize}, "
            f"current={pool._size}"
        )
        
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise DatabaseException("initialization", str(e))


async def close_db() -> None:
    """Gracefully close database connections"""
    try:
        await database.disconnect()
        logger.info("👋 Database connections closed")
    except Exception as e:
        logger.error(f"Error closing database: {e}")


@asynccontextmanager
async def get_db_session():
    """
    Async context manager for database sessions
    Implements proper error handling and cleanup
    """
    async with database.transaction():
        yield database


async def check_db_health() -> Dict[str, Any]:
    """
    Check database health for monitoring (Directive 11)
    Returns metrics for vibe dashboard
    """
    try:
        # Basic connectivity check
        result = await database.fetch_one("SELECT version()")
        version = result["version"]
        
        # Get connection pool stats
        pool = database.connection()._pool
        pool_stats = {
            "size": pool._size,
            "free": pool._free.qsize() if hasattr(pool._free, 'qsize') else 0,
            "min": pool._minsize,
            "max": pool._maxsize
        }
        
        # Check table count for basic health
        table_count = await database.fetch_one(
            "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public'"
        )
        
        return {
            "status": "healthy",
            "version": version,
            "pool_stats": pool_stats,
            "table_count": table_count["count"],
            "vibe_score": 10  # Healthy DB = good vibes
        }
        
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "vibe_score": 1  # Unhealthy DB = bad vibes
        }


# Eco-optimized query helpers (Directive 17)
async def execute_with_metrics(query: str, values: dict = None) -> Any:
    """
    Execute query with performance metrics for eco-scoring
    Tracks query execution time for optimization
    """
    import time
    
    start_time = time.time()
    
    try:
        if values:
            result = await database.execute(query=query, values=values)
        else:
            result = await database.execute(query=query)
        
        execution_time = time.time() - start_time
        
        # Log slow queries for optimization
        if execution_time > 1.0:  # 1 second threshold
            logger.warning(
                f"⚠️ Slow query detected ({execution_time:.2f}s): {query[:100]}..."
            )
            # In production, this would trigger eco-optimization suggestions
        
        return result
        
    except Exception as e:
        logger.error(f"Query execution failed: {e}")
        raise DatabaseException("query execution", str(e))


# Well-being feature: Database operation batching (Directive 19)
class BatchOperations:
    """
    Batch database operations to reduce stress on the system
    and improve developer flow by reducing wait times
    """
    
    def __init__(self):
        self.operations = []
    
    def add(self, query: str, values: dict = None):
        """Add operation to batch"""
        self.operations.append((query, values))
    
    async def execute(self):
        """Execute all operations in a transaction"""
        async with database.transaction():
            results = []
            for query, values in self.operations:
                result = await execute_with_metrics(query, values)
                results.append(result)
            
            # Clear batch after execution
            self.operations.clear()
            
            return results