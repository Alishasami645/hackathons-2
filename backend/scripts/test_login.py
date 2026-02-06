import traceback

try:
    from app.main import app
    from fastapi.testclient import TestClient

    client = TestClient(app)

    resp = client.post(
        "/api/auth/login",
        json={"email": "alis@gmail.com", "password": "12345678"},
        timeout=30,
    )

    print("STATUS", resp.status_code)
    print(resp.text)
except Exception as e:
    print("EXCEPTION:")
    traceback.print_exc()
