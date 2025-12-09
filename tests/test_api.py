def test_health_check(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert "database" in data
    assert "etl_last_run_status" in data

def test_get_data_empty(client):
    response = client.get("/api/v1/data")
    assert response.status_code == 200
    data = response.json()
    assert data["data"] == []
    assert data["meta"]["total"] == 0
