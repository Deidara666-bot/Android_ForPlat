import uuid
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


@router.get("/{case_id}", response_model=CaseOut, summary="Read one case")
def get_case(case_id: uuid.UUID, db: Annotated[Session, Depends(get_db)]) -> Case:
    case = CaseService(db).get(case_id)
    if case is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="case tidak ditemukan")
    return case


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
