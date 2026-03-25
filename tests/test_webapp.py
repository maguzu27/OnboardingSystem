def test_invalid_token_returns_403(client):
    # Try to access the set-password page with a fake token
    response = client.get('/set-password/fake-expired-token')
    
    # It should return the 'Link Invalid' message with a 403 error
    assert response.status_code == 403
    assert b"Link Invalid or Expired" in response.data