from app.core.raw_sources import SETTINGS_SECURE_A11Y, SETTINGS_SECURE_NLS
from app.normalization.vocabulary import (
    SPECIAL_ACCESS_ACCESSIBILITY,
    SPECIAL_ACCESS_NOTIFICATION_LISTENER,
)
from app.parsing.apk_static.certs import ApkCertificateParser
from app.parsing.apk_static.manifest import ApkManifestParser
from app.parsing.apk_static.simple import (
    ApkBadgingParser,
    ApkBundleManifestParser,
    ApkEndpointReferenceParser,
    ApkIdentityParser,
    ApkPermissionsParser,
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
register(SecureListParser(SETTINGS_SECURE_A11Y, SPECIAL_ACCESS_ACCESSIBILITY))
register(SecureListParser(SETTINGS_SECURE_NLS, SPECIAL_ACCESS_NOTIFICATION_LISTENER))
register(AppOpsOverlayParser())
register(UsageStatsParser())
register(ResumedActivityParser())
register(ProcessTableParser())
for _parser in (
    ApkIdentityParser(),
    ApkBadgingParser(),
    ApkPermissionsParser(),
    ApkManifestParser(),
    ApkCertificateParser(),
    ApkEndpointReferenceParser(),
    ApkBundleManifestParser(),
):
    register(_parser)
