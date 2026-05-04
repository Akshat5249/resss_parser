import requests
import sys

# Update these URLs after deployment
BACKEND_URL = "https://ats-backend-XXXX.onrender.com"
FRONTEND_URL = "https://ats-scanner-XXXX.vercel.app"

def check(name, fn):
    try:
        fn()
        print(f"✓ {name}")
    except Exception as e:
        print(f"✗ {name}: {e}")
        # continue checking other services

def run_checks():
    print(f"Starting production verification for {BACKEND_URL}...\n")
    
    check("Backend health", lambda: (
        r := requests.get(f"{BACKEND_URL}/health", timeout=60),
        assert r.status_code == 200,
        assert r.json()["status"] == "ok"
    ))

    check("Database", lambda: (
        r := requests.get(f"{BACKEND_URL}/health/db", timeout=30),
        assert r.status_code == 200
    ))

    check("Redis", lambda: (
        r := requests.get(f"{BACKEND_URL}/health/redis", timeout=30),
        assert r.status_code == 200
    ))

    check("Qdrant", lambda: (
        r := requests.get(f"{BACKEND_URL}/health/qdrant", timeout=30),
        assert r.status_code == 200
    ))

    check("Frontend", lambda: (
        r := requests.get(FRONTEND_URL, timeout=30),
        assert r.status_code == 200
    ))

    check("Resume upload", lambda: (
        r := requests.post(
            f"{BACKEND_URL}/resume/upload",
            files={"file": ("test.txt", b"John Doe Python Developer", "text/plain")},
            timeout=60
        ),
        assert r.status_code == 200,
        assert "job_id" in r.json()
    ))

    print("\nAll checks complete.")

if __name__ == "__main__":
    if "ats-backend-XXXX" in BACKEND_URL:
        print("Please update BACKEND_URL and FRONTEND_URL in the script before running.")
        sys.exit(1)
    run_checks()
