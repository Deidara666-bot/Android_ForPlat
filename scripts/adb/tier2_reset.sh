#!/usr/bin/env bash
# Put a Tier-2 environment back to its baseline before one acquisition session (REF §TIER2).
# Host-side script: resetting is not an agent operation and the backend never triggers it.
#
# Usage: bash scripts/adb/tier2_reset.sh <env> [serial]
#   env     avd1-api36 | avd2-api<N> | a10-api<N>
#   serial  adb serial; optional when exactly one matching device is connected
#
# AVD:        snapshot `clean` is loaded (the user creates it once, in the emulator).
# Galaxy A10: the phone is rebooted.
# Either way the script returns only when the device reports sys.boot_completed=1.
# Exit codes: 0 reset done; 1 reset failed; 2 unknown environment; 3 no single device found.

set -u
ADB="${ADB:-adb}"
env_label="${1:-}"
serial="${2:-}"
BOOT_TIMEOUT_SECONDS="${BOOT_TIMEOUT_SECONDS:-180}"

case "$env_label" in
  avd1-api36 | avd2-api[0-9][0-9]) kind="avd" ;;
  a10-api[0-9][0-9]) kind="a10" ;;
  *)
    echo "tier2_reset: unknown environment '$env_label' (nothing was touched)" >&2
    exit 2
    ;;
esac

if [ -z "$serial" ]; then
  candidates=()
  while read -r name state _; do
    [ "$state" = "device" ] || continue
    case "$kind:$name" in
      avd:emulator-*) candidates+=("$name") ;;
      a10:emulator-*) ;;
      a10:*) candidates+=("$name") ;;
    esac
  done < <("$ADB" devices | tail -n +2)
  if [ "${#candidates[@]}" -ne 1 ]; then
    echo "tier2_reset: expected exactly one $kind device, found ${#candidates[@]} (pass the serial)" >&2
    exit 3
  fi
  serial="${candidates[0]}"
fi

if [ "$kind" = "avd" ]; then
  out="$("$ADB" -s "$serial" emu avd snapshot load clean 2>&1)"
  if ! printf '%s\n' "$out" | grep -qx "OK"; then
    echo "tier2_reset: snapshot 'clean' could not be loaded on $serial" >&2
    printf '%s\n' "$out" >&2
    exit 1
  fi
else
  "$ADB" -s "$serial" reboot || { echo "tier2_reset: reboot failed on $serial" >&2; exit 1; }
fi

"$ADB" -s "$serial" wait-for-device
deadline=$((SECONDS + BOOT_TIMEOUT_SECONDS))
while [ "$SECONDS" -lt "$deadline" ]; do
  booted="$("$ADB" -s "$serial" shell getprop sys.boot_completed 2>/dev/null | tr -d '\r')"
  if [ "$booted" = "1" ]; then
    echo "tier2_reset: $env_label on $serial is back at its baseline"
    exit 0
  fi
  sleep 2
done
echo "tier2_reset: $serial did not report sys.boot_completed=1 within ${BOOT_TIMEOUT_SECONDS}s" >&2
exit 1
