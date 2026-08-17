import concurrent.futures
import time

import requests


BASE_URL = "http://127.0.0.1:8000"


def test_api_health():
    response = requests.get(
        f"{BASE_URL}/",
        timeout=10
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, dict)


def test_api_companies_to_dashboard_flow():
    response = requests.get(
        f"{BASE_URL}/api/companies",
        timeout=15
    )

    assert response.status_code == 200

    data = response.json()

    assert "count" in data
    assert "data" in data

    assert data["count"] > 0
    assert len(data["data"]) > 0

    company = data["data"][0]

    assert "id" in company
    assert "company_name" in company


def test_screener_api_available():
    response = requests.get(
        f"{BASE_URL}/api/screener",
        timeout=15
    )

    assert response.status_code == 200


def test_company_data_contains_financial_fields():
    response = requests.get(
        f"{BASE_URL}/api/companies",
        timeout=15
    )

    assert response.status_code == 200

    companies = response.json()["data"]

    assert len(companies) > 0

    first = companies[0]

    # These are the fields your dashboard/API currently exposes.
    expected_fields = [
        "id",
        "company_name",
    ]

    for field in expected_fields:
        assert field in first


def test_ten_concurrent_screener_queries():
    def make_request(_):
        start = time.perf_counter()

        try:
            response = requests.get(
                f"{BASE_URL}/api/screener",
                timeout=30
            )

            elapsed = time.perf_counter() - start

            return {
                "status": response.status_code,
                "time": elapsed,
                "success": response.status_code == 200,
            }

        except Exception as exc:
            return {
                "status": None,
                "time": time.perf_counter() - start,
                "success": False,
                "error": str(exc),
            }

    start = time.perf_counter()

    with concurrent.futures.ThreadPoolExecutor(
        max_workers=10
    ) as executor:

        results = list(
            executor.map(make_request, range(10))
        )

    total_time = time.perf_counter() - start

    successful = [
        result for result in results
        if result["success"]
    ]

    failed = [
        result for result in results
        if not result["success"]
    ]

    response_times = [
        result["time"]
        for result in successful
    ]

    print("\nD43 LOAD TEST")
    print("-" * 40)
    print(f"Requests       : 10")
    print(f"Successful     : {len(successful)}")
    print(f"Failed         : {len(failed)}")
    print(f"Total time     : {total_time:.3f}s")

    if response_times:
        print(f"Average time   : {sum(response_times) / len(response_times):.3f}s")
        print(f"Max response   : {max(response_times):.3f}s")
        print(f"Min response   : {min(response_times):.3f}s")

    if failed:
        print("Failures:")
        for failure in failed:
            print(failure)

    # D43 acceptance criteria
    assert len(successful) == 10
    assert len(failed) == 0