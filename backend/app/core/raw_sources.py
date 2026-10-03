"""`raw_source` labels the backend knows (REF §OPS2, §STATIC).

The agent sends one label with every evidence file; the parser registry picks the parser of a
part by `(operation_id, raw_source)`. Labels are names of evidence sources, not commands, but
several contain the name of the tool that produced the file (for example `dumpsys`), so they
live only in this file; the repository's command-string grep excludes it, like `adb_commands.py`.
"""

# collect_accessibility_state
SETTINGS_SECURE_A11Y = "settings secure a11y"
SETTINGS_SECURE_NLS = "settings secure nls"
APPOPS_OVERLAY = "appops overlay"

# collect_usage_state
DUMPSYS_USAGESTATS = "dumpsys usagestats"
DUMPSYS_ACTIVITY = "dumpsys activity"
PS = "ps"

# pull_subject_apk: the pulled file itself and the seven bundle files of the static extractor
PM_PATH = "pm path"
APK_FILE = "apk file"
STATIC_APK_SHA256 = "static:apk.sha256"
STATIC_BADGING = "static:badging.txt"
STATIC_PERMISSIONS = "static:permissions.txt"
STATIC_MANIFEST = "static:manifest.txt"
STATIC_CERTS = "static:certs.txt"
STATIC_STRINGS_URLS = "static:strings_urls.txt"
STATIC_BUNDLE_JSON = "static:bundle.json"
