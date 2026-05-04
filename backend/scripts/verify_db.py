import os
import sys
import psycopg2
from dotenv import load_dotenv

# Add parent directory to path to import settings if needed
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

def verify_db():
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("Error: DATABASE_URL not found in environment.")
        sys.exit(1)

    try:
        conn = psycopg2.connect(database_url)
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM resume_jobs")
        count = cur.fetchone()[0]
        print(f"✓ Supabase connected. Tables exist. Found {count} records in resume_jobs.")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    verify_db()
