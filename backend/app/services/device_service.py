from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.constants import ConnectionState
from app.models.agent import Agent
from app.models.device import Device
from app.schemas.device import DeviceReportItem

_REQUIRED = ("manufacturer", "model", "android_version", "api_level", "device_build")


class DeviceService:
    def __init__(self, db: Session) -> None:
        self._db = db

    def apply_report(self, agent: Agent, items: list[DeviceReportItem]) -> None:
        """Upsert reported devices by serial. Devices this agent no longer reports become
        `disconnected`; rows are never deleted."""
        now = datetime.now(UTC)
        agent_pk = agent.id
        connected: set[str] = set()
        for item in items:
            if item.status != "device" or any(getattr(item, key) is None for key in _REQUIRED):
                continue  # unauthorized/offline or incomplete metadata: not (yet) usable
            connected.add(item.serial)
            device = self._db.scalar(select(Device).where(Device.serial == item.serial))
            is_new = device is None
            if device is None:
                device = Device(serial=item.serial)
            device.manufacturer = str(item.manufacturer)
            device.model = str(item.model)
            device.android_version = str(item.android_version)
            device.api_level = int(item.api_level or 0)
            device.device_build = str(item.device_build)
            device.connection_state = ConnectionState.connected.value
            device.last_agent_id = agent_pk
            device.last_seen_at = now
            if is_new:
                self._db.add(device)  # only once fully populated: avoids a half-built autoflush

        own = self._db.scalars(select(Device).where(Device.last_agent_id == agent_pk))
        for device in own:
            if device.serial not in connected:
                device.connection_state = ConnectionState.disconnected.value
        self._db.commit()

    def list(self) -> list[Device]:
        return list(self._db.scalars(select(Device).order_by(Device.serial)))
