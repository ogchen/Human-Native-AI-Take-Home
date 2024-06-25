from fastapi import status

from app.models import Dataset
from app.models import Organisation
from app.models import User

import pytest

ENDPOINT = "/report/data_violation"


@pytest.fixture
def params():
    token = "valid_token"
    headers = {"Authorization": f"Bearer {token}"}
    publisher_org = {
        "id": "aurora_org_id",
        "name": "Aurora Articles",
        "email": "info@auroraarticles.com",
    }
    dataset = {
        "org_id": publisher_org["id"],
        "id": "aurora_dataset_id",
        "name": "Aurora Articles Catalogue",
        "type": "text",
    }
    reporter_org = {
        "id": "blog_bot_org_id",
        "name": "Blog Bot",
        "email": "info@blogbot.com",
    }
    reporter = {
        "username": "username",
        "full_name": "First Last",
        "email": "user@blogbot.com",
        "org_id": reporter_org["id"],
    }
    data = [
        {
            "dataset_id": dataset["id"],
            "id": "data_0",
            "value": "Some text here",
        },
        {
            "dataset_id": dataset["id"],
            "id": "data_1",
            "value": "Some other text here",
        },
    ]
    request = {
        "title": "Personally Identifiable Information Violation",
        "description": "I have found a data violation in the Aurora Articles dataset.",
        "report_type": "data_violation",
        "category": "personal_data",
        "dataset_id": dataset["id"],
        "examples": [
            {"data_id": data[0]["id"], "description": "Contains "},
            {"data_id": data[1]["id"]},
        ],
    }

    return {
        "token": token,
        "headers": headers,
        "request": request,
        "reporter": reporter,
        "reporter_org": reporter_org,
        "publisher_org": publisher_org,
        "dataset": dataset,
        "data": data,
    }


@pytest.fixture
def report_client(test_client, mock_db_client, params):
    mock_db_client.is_valid_token.side_effect = lambda token: params["token"] == token
    mock_db_client.is_permissioned_for_dataset.return_value = (
        lambda user, dataset_id: user.org_id == params["reporter_org"]["id"]
        and dataset_id == params["dataset"]["id"]
    )
    mock_db_client.get_dataset.side_effect = lambda dataset_id: {
        params["dataset"]["id"]: Dataset(**params["dataset"]),
    }.get(dataset_id)
    mock_db_client.get_org.side_effect = lambda org_id: {
        params["reporter_org"]["id"]: Organisation(**params["reporter_org"]),
        params["publisher_org"]["id"]: Organisation(**params["publisher_org"]),
    }.get(org_id)
    mock_db_client.get_user.side_effect = lambda username: {
        params["reporter"]["username"]: User(**params["reporter"]),
    }.get(username)
    mock_db_client.get_user_from_token.side_effect = lambda token: {
        params["token"]: User(**params["reporter"]),
    }.get(token)
    mock_db_client.verify_data_id.side_effect = lambda data_id, dataset_id: any(
        (d["id"] == data_id and d["dataset_id"] == dataset_id for d in params["data"])
    )
    return test_client


def test_report(report_client, mock_email_client, params):
    response = report_client.post(
        ENDPOINT, json=params["request"], headers=params["headers"]
    )
    assert response.status_code == status.HTTP_200_OK
    mock_email_client.send_email.assert_called_once()
    email_args = mock_email_client.send_email.call_args.kwargs
    assert email_args["recipient"] == params["publisher_org"]["email"]
    assert params["request"]["dataset_id"] in email_args["body"]
    for example in params["request"]["examples"]:
        assert example["data_id"] in email_args["body"]


def test_report_unauthenticated(report_client, mock_db_client, params):
    invalid_token = "invalid_token"
    response = report_client.post(
        ENDPOINT,
        json=params["request"],
        headers={"Authorization": f"Bearer {invalid_token}"},
    )
    mock_db_client.is_valid_token.assert_called_once_with(invalid_token)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_report_malformed_request(report_client, params):
    response = report_client.post(ENDPOINT, json={}, headers=params["headers"])
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_report_invalid_dataset_id(report_client, mock_db_client, params):
    params["request"]["dataset_id"] = "invalid dataset id"
    response = report_client.post(ENDPOINT, json=params["request"], headers=params["headers"])
    mock_db_client.get_dataset.assert_called_once_with(params["request"]["dataset_id"])
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

def test_report_invalid_data_id(report_client, mock_db_client, params):
    invalid_data_id = "invalid data id"
    params["request"]["examples"].append({"data_id": invalid_data_id, "description": ""})
    response = report_client.post(ENDPOINT, json=params["request"], headers=params["headers"])
    mock_db_client.verify_data_id.assert_called_with(invalid_data_id, params["request"]["dataset_id"])
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
