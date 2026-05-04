import requests
import sys

# Replace with your actual deployed URLs
BACKEND_URL = "https://ats-scanner-your-app.koyeb.app"
FRONTEND_URL = "https://ats-scanner-your-app.vercel.app"

def check(name, fn):
    try:
        fn()
        print(f"✓ {name}")
    except Exception as e:
        print(f"✗ {name}: {e}")

def run_checks():
    print(f"Starting production verification for:")
    print(f"Backend: {BACKEND_URL}")
    print(f"Frontend: {FRONTEND_URL}\n")

    # Test 1 — Health check
    def check_health():
        r = requests.get(f"{BACKEND_URL}/health")
        assert r.status_code == 200
        assert r.json()["status"] in ["ok", "degraded"]
    check("Backend health", check_health)

    # Test 2 — Database connected
    check("Database", lambda: (
        r := requests.get(f"{BACKEND_URL}/health/db"),
        assert r.status_code == 200
    ))

    # Test 3 — Redis connected
    check("Redis", lambda: (
        r := requests.get(f"{BACKEND_URL}/health/redis"),
        assert r.status_code == 200
    ))

    # Test 4 — Qdrant connected
    check("Qdrant", lambda: (
        r := requests.get(f"{BACKEND_URL}/health/qdrant"),
        assert r.status_code == 200
    ))

    # Test 5 — Frontend loads
    check("Frontend", lambda: (
        r := requests.get(FRONTEND_URL),
        assert r.status_code == 200
    ))

    # Test 6 — Resume upload (smoke test)
    def check_upload():
        r = requests.post(
            f"{BACKEND_URL}/resume/upload",
            files={"file": ("test.txt", b"John Doe Python Developer", "text/plain")}
        )
        assert r.status_code == 200
        assert "job_id" in r.json()
    check("Resume upload smoke test", check_upload)

    print("\nAll checks complete.")

if __name__ == "__main__":
    run_checks()
