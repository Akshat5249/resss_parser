import os
import sys
from qdrant_client import QdrantClient
from dotenv import load_dotenv

# Add parent directory to path to import settings if needed
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

def verify_qdrant():
    qdrant_url = os.getenv("QDRANT_URL")
    qdrant_api_key = os.getenv("QDRANT_API_KEY")
    
    if not qdrant_url:
        print("Error: QDRANT_URL not found in environment.")
        sys.exit(1)

    try:
        client = QdrantClient(
            url=qdrant_url,
            api_key=qdrant_api_key if qdrant_api_key else None
        )
        collections = client.get_collections()
        print(f"✓ Qdrant Cloud connected. Found {len(collections.collections)} collections.")
    except Exception as e:
        print(f"✗ Qdrant connection failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    verify_qdrant()
