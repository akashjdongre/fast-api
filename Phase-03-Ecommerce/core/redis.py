import os
import redis.asyncio as redis
from config import settings

redis_url = settings.REDIS_URL
if not redis_url:
    redis_url = "redis://redis:6379/0"

# Allow the app container to use the Compose service name while local runs can still use localhost.
if "localhost" in redis_url and os.getenv("RUNNING_IN_DOCKER") == "1":
    redis_url = redis_url.replace("localhost", "redis", 1)

redis_client = redis.from_url(redis_url, decode_responses=True)