import io

def test_export_csv_success(client):
    """
    Test that the /export/csv endpoint returns a CSV file with status 200.
    """
    response = client.get('/export/csv')
    assert response.status_code == 200
    assert response.content_type.startswith('text/csv')
    # Optionally, check that the response contains CSV headers
    content = response.data.decode('utf-8')
    assert "id" in content  # Adapt to your CSV headers
    # You can also check for a known dummy value if your test DB is seeded

def test_export_csv_empty(client):
    """
    Test that the /export/csv endpoint returns a valid CSV even if there are no dummies.
    """
    # Optionally, clear the dummies table here if needed
    response = client.get('/export/csv')
    assert response.status_code == 200
    assert response.content_type.startswith('text/csv')
    content = response.data.decode('utf-8')
    # Should at least contain headers
    assert "id" in content  # Adapt to your CSV headers
