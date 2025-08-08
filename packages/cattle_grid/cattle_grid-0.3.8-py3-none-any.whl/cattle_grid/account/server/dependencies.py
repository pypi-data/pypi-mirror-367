from typing import Annotated

from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer

from cattle_grid.account.models import AuthenticationToken, Account

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/signin")


async def get_current_account(token: Annotated[str, Depends(oauth2_scheme)]) -> Account:
    from_db = await AuthenticationToken.get_or_none(token=token).prefetch_related(
        "account"
    )

    if from_db is None:
        raise HTTPException(401)

    return from_db.account


CurrentAccount = Annotated[Account, Depends(get_current_account)]
"""Annotation for the current account"""
