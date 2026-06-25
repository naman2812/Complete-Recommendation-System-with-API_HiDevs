import time
import requests
import concurrent.futures

API_URL = "http://127.0.0.1:8000"

HEADERS = {"X-API-Key": "capstone-auth-key-2026"}


def simulate_user(user_id):
    start_time = time.time()
    try:
        response = requests.get(
            f"{API_URL}/recommend/{user_id}?limit=5", headers=HEADERS
        )
        latency = time.time() - start_time
        return {
            "user_id": user_id,
            "status_code": response.status_code,
            "latency": latency,
            "success": response.status_code == 200,
        }
    except Exception as e:
        return {
            "user_id": user_id,
            "status_code": 500,
            "latency": time.time() - start_time,
            "success": False,
            "error": str(e),
        }


def run_load_test(num_concurrent_users=10):
    print(f"Starting load test with {num_concurrent_users} concurrent users...")

    # Check if API is up
    try:
        requests.get(f"{API_URL}/health")
    except:
        print(
            "Error: API is not running. Please start the API server first (uvicorn api.app:app)."
        )
        return

    # Simulate random user IDs from 1 to 10
    user_ids = [i for i in range(1, num_concurrent_users + 1)]

    start_time = time.time()
    results = []

    with concurrent.futures.ThreadPoolExecutor(
        max_workers=num_concurrent_users
    ) as executor:
        futures = [executor.submit(simulate_user, uid) for uid in user_ids]
        for future in concurrent.futures.as_completed(futures):
            results.append(future.result())

    total_time = time.time() - start_time

    successes = sum(1 for r in results if r["success"])
    failures = len(results) - successes
    avg_latency = sum(r["latency"] for r in results) / len(results)

    print("\n--- Load Test Results ---")
    print(f"Total Requests: {len(results)}")
    print(f"Successful: {successes}")
    print(f"Failed: {failures}")
    print(f"Average Latency: {avg_latency * 1000:.2f} ms")
    print(f"Total Time: {total_time:.2f} s")
    print(f"Throughput: {len(results) / total_time:.2f} requests/second")


if __name__ == "__main__":
    run_load_test()
