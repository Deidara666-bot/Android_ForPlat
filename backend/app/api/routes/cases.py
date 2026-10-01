from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.case import Case
from app.models.user import User
from app.schemas.case import CaseCreate, CaseOut
from app.services.case_service import CaseService, DuplicateCaseNumberError

router = APIRouter(prefix="/cases", tags=["cases"], dependencies=[Depends(get_current_user)])


@router.get("", response_model=list[CaseOut], summary="List cases")
def list_cases(db: Annotated[Session, Depends(get_db)]) -> list[Case]:
    return CaseService(db).list()


@router.post(
    "", response_model=CaseOut, status_code=status.HTTP_201_CREATED, summary="Create a case"
)
def create_case(
    body: CaseCreate,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
) -> Case:
    try:
        return CaseService(db).create(body.case_number, body.title, user.id)
    except DuplicateCaseNumberError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="case_number already exists"
        ) from None
