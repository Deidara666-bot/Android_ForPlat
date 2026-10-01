import uuid

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.case import Case


class DuplicateCaseNumberError(Exception):
    pass


class CaseService:
    def __init__(self, db: Session) -> None:
        self._db = db

    def list(self) -> list[Case]:
        return list(self._db.scalars(select(Case).order_by(Case.created_at, Case.case_number)))

    def create(self, case_number: str, title: str, created_by: uuid.UUID) -> Case:
        case = Case(case_number=case_number, title=title, created_by=created_by)
        self._db.add(case)
        try:
            self._db.commit()
        except IntegrityError as exc:
            self._db.rollback()
            raise DuplicateCaseNumberError(case_number) from exc
        self._db.refresh(case)
        return case
