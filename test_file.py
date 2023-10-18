import json
import pytest
from fastapi.testclient import TestClient
from main import app 
import threading

client = TestClient(app)

@pytest.fixture
def sample_input():
    return [40.1, 8.1, 8.2, 30, 4.2, 31.51, 1, 41.27]

def test_insert_samples_and_metrics(sample_input):
    response = client.post("/insert_samples", json=sample_input)
    assert response.status_code == 200
    assert response.json() == {'message': 'Successfully altered histogram'}

    response = client.get("/metrics")
    assert response.status_code == 200
    response_data = json.loads(response.text)
    assert "statistics" in response_data


def insert_samples_in_parallel(client, sample_input):
    threads = []
    for _ in range(5):
        thread = threading.Thread(target=client.post, args=("/insert_samples", sample_input))
        thread = threading.Thread(target=client.get, args=("metrics"))
        threads.append(thread)
        

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

def test_multithreading_insert_samples(sample_input):
    insert_samples_in_parallel(client, sample_input)