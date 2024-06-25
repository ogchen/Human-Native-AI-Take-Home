from app.db import DatabaseClient
from app.models import Dataset
from app.models import Organisation
from app.models import User

FAKE_USER_DB = {
    "ochen": {
        "username": "ochen",
        "full_name": "Oscar Chen",
        "email": "ochen@blogbot.com",
        "org_id": "fake_blog_bot_org_id",
    }
}

FAKE_ORG_DB = {
    "fake_aurora_org_id": {
        "id": "fake_aurora_org_id",
        "name": "Aurora Articles",
        "email": "info@auroraarticles.com",
    },
    "fake_blog_bot_org_id": {
        "id": "fake_blog_bot_org_id",
        "name": "Blog Bot",
        "email": "info@blogbot.com",
    }
}

FAKE_DATASET_DB = {
    "fake_aurora_dataset_id": {
        "org_id": "fake_aurora_org_id",
        "id": "fake_aurora_dataset_id",
        "name": "Aurora Articles Catalogue",
        "type": "text",
    },
    "some_other_dataset_id": {
        "org_id": "some_other_org_id",
        "id": "some_other_dataset_id",
        "name": "Some Other Catalogue",
        "type": "video",
    },
}

FAKE_DATA_DB = {
    "fake_aurora_dataset_id": {
        "fake_aurora_data_id_0": {
            "dataset_id": "fake_aurora_dataset_id",
            "id": "fake_aurora_data_id_0",
            "value": "Some text here",
        },
        "fake_aurora_data_id_1": {
            "dataset_id": "fake_aurora_dataset_id",
            "id": "fake_aurora_data_id_1",
            "value": "Some other text here",
        },
    }
}

FAKE_TOKEN_DB = {
    "dummy_token": {
        "username": "ochen",
    }
}


class FakeDatabaseClient(DatabaseClient):
    def get_user(self, username: str):
        user_dict = FAKE_USER_DB.get(username)
        if user_dict is not None:
            return User(**user_dict)

    def is_valid_token(self, token: str):
        return token in FAKE_TOKEN_DB

    def get_user_from_token(self, token: str):
        token_info = FAKE_TOKEN_DB.get(token)
        if token_info is not None:
            return self.get_user(token_info["username"])

    def verify_data_id(self, data_id: str, dataset_id: str):
        return dataset_id in FAKE_DATA_DB and data_id in FAKE_DATA_DB[dataset_id]

    def get_dataset(self, dataset_id: str):
        dataset = FAKE_DATASET_DB.get(dataset_id)
        if dataset is not None:
            return Dataset(**dataset)

    def is_permissioned_for_dataset(self, user: User, dataset_id: str):
        return user.org_id == "fake_blog_bot_org_id" and dataset_id == "fake_aurora_dataset_id"

    def get_org(self, org_id: str):
        org = FAKE_ORG_DB.get(org_id)
        if org is not None:
            return Organisation(**org)


def get_db():
    return FakeDatabaseClient()
