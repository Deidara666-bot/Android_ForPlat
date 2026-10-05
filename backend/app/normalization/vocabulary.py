"""Closed `object_value` vocabularies read by the rules (REF §VOCAB, 01_BREAKDOWN §14.2)."""

SENSITIVE_COMMUNICATION_PERMISSIONS: frozenset[str] = frozenset(
    {
        "android.permission.READ_SMS",
        "android.permission.RECEIVE_SMS",
        "android.permission.SEND_SMS",
        "android.permission.READ_CONTACTS",
        "android.permission.READ_CALL_LOG",
    }
)

EVENT_TRIGGER_ACTIONS: frozenset[str] = frozenset(
    {
        "android.intent.action.BOOT_COMPLETED",
        "android.intent.action.LOCKED_BOOT_COMPLETED",
        "android.intent.action.PACKAGE_ADDED",
        "android.intent.action.PACKAGE_REPLACED",
    }
)

SPECIAL_ACCESS_ACCESSIBILITY = "accessibility_service"
SPECIAL_ACCESS_NOTIFICATION_LISTENER = "notification_listener"
SPECIAL_ACCESS_DRAW_OVER = "draw_over_other_apps"

# Permission that makes a declared service an accessibility service / notification listener,
# and the requested permission that stands for the overlay special access.
BIND_ACCESSIBILITY_PERMISSION = "android.permission.BIND_ACCESSIBILITY_SERVICE"
BIND_NOTIFICATION_LISTENER_PERMISSION = "android.permission.BIND_NOTIFICATION_LISTENER_SERVICE"
OVERLAY_PERMISSION = "android.permission.SYSTEM_ALERT_WINDOW"

# Usage events that mark an app coming to the foreground. Other events stay as artifacts only.
FOREGROUND_USAGE_EVENTS: frozenset[str] = frozenset({"ACTIVITY_RESUMED", "MOVE_TO_FOREGROUND"})
