from fastapi import Depends
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from fastapi import status
from fastapi.security import HTTPBearer
from typing import Annotated

from app.db import DatabaseClient
from app.db import get_db

security = HTTPBearer()


def verify_token(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    db: Annotated[DatabaseClient, Depends(get_db)],
):
    token = credentials.credentials
    if not db.is_valid_token(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )
    return token
