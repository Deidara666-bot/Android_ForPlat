from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.device import Device
from app.schemas.device import DeviceOut
from app.services.device_service import DeviceService

router = APIRouter(prefix="/devices", tags=["devices"], dependencies=[Depends(get_current_user)])


@router.get("", response_model=list[DeviceOut], summary="List known devices")
def list_devices(db: Annotated[Session, Depends(get_db)]) -> list[Device]:
    return DeviceService(db).list()
