import os
import sys
import redis
from dotenv import load_dotenv

# Add parent directory to path to import settings if needed
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

def verify_redis():
    redis_url = os.getenv("REDIS_URL")
    if not redis_url:
        print("Error: REDIS_URL not found in environment.")
        sys.exit(1)

    try:
        # Use ssl_cert_reqs=None for Upstash if rediss:// is used
        if redis_url.startswith("rediss://"):
            client = redis.from_url(redis_url, ssl_cert_reqs=None)
        else:
            client = redis.from_url(redis_url)
            
        client.ping()
        print("✓ Upstash Redis connected.")
    except Exception as e:
        print(f"✗ Redis connection failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    verify_redis()
