from abc import ABC
from enum import auto
from enum import StrEnum
from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status
from pydantic import BaseModel
from typing import Annotated
from typing import List
from typing import Literal
from typing import Optional

from app.email import EmailClient
from app.email import get_email_client
from app.models import Dataset
from app.models import Organisation
from app.models import User
from app.db import DatabaseClient
from app.db import get_db
from app.token import verify_token
from app.users import get_user

router = APIRouter(prefix="/report", dependencies=[Depends(verify_token)])

class DataViolationCategoryEnum(StrEnum):
    PERSONAL_DATA = auto()
    COPYRIGHT_INFRINGEMENT = auto()
    INAPPROPRIATE_CONTENT = auto()
    OTHER = auto()


class DataViolationExample(BaseModel):
    data_id: str
    description: Optional[str] = None


class BaseReport(BaseModel, ABC):
    title: str
    description: str


class DataViolationReport(BaseReport):
    report_type: Literal["data_violation"]
    category: DataViolationCategoryEnum
    dataset_id: str
    examples: List[DataViolationExample]

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "title": "Personally Identifiable Information Issue",
                    "description": "There are various examples of personal details in the Aurora Articles dataset.",
                    "report_type": "data_violation",
                    "category": "personal_data",
                    "dataset_id": "fake_aurora_dataset_id",
                    "examples": [
                        {"data_id": "fake_aurora_data_id_0", "description": "Contains reference to phone numbers"},
                        {"data_id": "fake_aurora_data_id_1"},
                    ],
                }
            ]
        }
    }


class ValidatedDataViolationReport(DataViolationReport):
    dataset: Dataset


def generate_readable_report(reporter: User, reporter_org: Organisation, report: ValidatedDataViolationReport):
    title = f"[Data Violation Alert] Report received for dataset '{report.dataset.name}': '{report.title}'"
    body = f"""
A data violation issue has been reported.

Reporter: {reporter.full_name} - {reporter_org.name} ({reporter.email})
Category: {report.category}
Dataset: {report.dataset.name}
Description:
{report.description}
    """

    if len(report.examples) > 0:
        examples = "\n".join([f"    - ({example.data_id}): {example.description or 'No description'}" for example in report.examples])
        body += f"""
Examples:
{examples}
    """
    return {"title": title, "body": body}


def validate_report(
    report: DataViolationReport, db: Annotated[DatabaseClient, Depends(get_db)]
):
    dataset = db.get_dataset(report.dataset_id)
    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Encountered invalid dataset ID {report.dataset_id}",
        )
    for example in report.examples:
        if not db.verify_data_id(example.data_id, dataset.id):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Encountered invalid data ID {example.data_id}",
            )
    return ValidatedDataViolationReport(**report.model_dump(), dataset=dataset)


@router.post("/data_violation")
async def report(
    reporter: Annotated[User, Depends(get_user)],
    report: Annotated[ValidatedDataViolationReport, Depends(validate_report)],
    email_client: Annotated[EmailClient, Depends(get_email_client)],
    db: Annotated[DatabaseClient, Depends(get_db)],
):
    if not db.is_permissioned_for_dataset(reporter, report.dataset.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User is not permissioned for dataset.",
        )
    publisher_org = db.get_org(report.dataset.org_id)
    if publisher_org is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to find organisation details for dataset."
        )
    reporter_org = db.get_org(reporter.org_id)
    if reporter_org is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to find organisation details for reporter."
        )
    readable_report = generate_readable_report(reporter, reporter_org, report)
    email_client.send_email(recipient=publisher_org.email, **readable_report)
    return {"detail": "Successfully reported data violation."}
