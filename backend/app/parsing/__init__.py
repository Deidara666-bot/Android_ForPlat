from app.normalization.vocabulary import (
    SPECIAL_ACCESS_ACCESSIBILITY,
    SPECIAL_ACCESS_NOTIFICATION_LISTENER,
)
from app.parsing.package_state.detail import PackageDetailParser
from app.parsing.package_state.device_metadata import DeviceMetadataParser
from app.parsing.package_state.inventory import InventoryParser
from app.parsing.registry import register
from app.parsing.settings_state.appops import AppOpsOverlayParser
from app.parsing.settings_state.secure import SecureListParser
from app.parsing.usage_stats.activity import ResumedActivityParser
from app.parsing.usage_stats.ps import ProcessTableParser
from app.parsing.usage_stats.usagestats import UsageStatsParser

register(InventoryParser())
register(DeviceMetadataParser())
register(PackageDetailParser())
register(SecureListParser("settings secure a11y", SPECIAL_ACCESS_ACCESSIBILITY))
register(SecureListParser("settings secure nls", SPECIAL_ACCESS_NOTIFICATION_LISTENER))
register(AppOpsOverlayParser())
register(UsageStatsParser())
register(ResumedActivityParser())
register(ProcessTableParser())
