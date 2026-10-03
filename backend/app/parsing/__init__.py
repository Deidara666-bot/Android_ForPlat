from app.parsing.package_state.detail import PackageDetailParser
from app.parsing.package_state.device_metadata import DeviceMetadataParser
from app.parsing.package_state.inventory import InventoryParser
from app.parsing.registry import register

register(InventoryParser())
register(DeviceMetadataParser())
register(PackageDetailParser())
