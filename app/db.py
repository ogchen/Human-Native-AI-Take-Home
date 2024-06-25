from app.models import Dataset
from app.models import Organisation
from app.models import User


class DatabaseClient:
    def get_user(self, username: str) -> User | None:
        raise NotImplementedError()

    def is_valid_token(self, token: str) -> bool:
        raise NotImplementedError()

    def get_user_from_token(self, token: str) -> User | None:
        raise NotImplementedError()

    def verify_data_id(self, data_id: str, dataset_id: str) -> bool:
        raise NotImplementedError()

    def get_dataset(self, dataset_id: str) -> Dataset | None:
        raise NotImplementedError()

    def is_permissioned_for_dataset(self, user: User, dataset_id: str) -> bool:
        raise NotImplementedError()

    def get_org(self, org_id: str) -> Organisation | None:
        raise NotImplementedError()


def get_db() -> DatabaseClient:
    raise NotImplementedError("Database client has not been implemented.")
