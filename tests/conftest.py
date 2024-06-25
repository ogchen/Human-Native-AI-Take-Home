import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock

from app.app import report_app
from app.db import DatabaseClient
from app.db import get_db
from app.email import EmailClient
from app.email import get_email_client

class MockDatabaseClient(DatabaseClient):
    def __init__(self):
        self.get_user = MagicMock(return_value=None)
        self.is_valid_token = MagicMock(return_value=True)
        self.get_user_from_token = MagicMock(return_value=None)
        self.verify_data_id = MagicMock(return_value=True)
        self.get_dataset = MagicMock(return_value=None)
        self.is_permissioned_for_dataset = MagicMock(return_value=False)
        self.get_org = MagicMock(return_value=None)

class MockEmailClient(EmailClient):
    def __init__(self):
        self.send_email = MagicMock()

@pytest.fixture
def mock_db_client():
    mock = MockDatabaseClient()
    report_app.dependency_overrides[get_db] = lambda: mock
    yield mock
    del report_app.dependency_overrides[get_db]

@pytest.fixture
def mock_email_client():
    mock = MockEmailClient()
    report_app.dependency_overrides[get_email_client] = lambda: mock
    yield mock
    del report_app.dependency_overrides[get_email_client]

@pytest.fixture
def test_client(mock_email_client, mock_db_client):
    return TestClient(report_app)
