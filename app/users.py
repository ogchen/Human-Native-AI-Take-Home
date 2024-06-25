from fastapi import Depends
from fastapi import HTTPException
from fastapi import status
from typing import Annotated

from app.token import verify_token
from app.db import DatabaseClient
from app.db import get_db


async def get_user(
    token: Annotated[str, Depends(verify_token)],
    db: Annotated[DatabaseClient, Depends(get_db)],
):
    """
    Extracts user information from a token.
    """
    user = db.get_user_from_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )
    return user
