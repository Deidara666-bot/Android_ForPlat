# Tier-2 G1 — uji ketersediaan formatif (AVD #1, API 36)

Dicatat dari `/card v0.45.9`, 2026-10-05. Ini hasil **formatif**: dipakai untuk membentuk aturan dan parser, bukan bukti
lintas lingkungan. Lintas lingkungan (AVD #2, Galaxy A10) dicatat di Tier-2 konfirmatif `v0.90.8`.
⛔ Hasil AVD #1 tidak digeneralisasi ke versi Android atau perangkat lain.

## Kondisi uji

| | |
|---|---|
| Lingkungan | `avd1-api36` — `emulator-5554`, Android 16 / API 36, `google/sdk_gphone64_x86_64/emu64xa:16/BE2A.250530.026.F3/13894323:userdebug/dev-keys` |
| Hak akses | `non_root` (semua baris) |
| Subjek | `com.android.settings` (APK `SettingsGoogle.apk`, 87.344.510 B) · `com.android.stk` (APK `Stk.apk`) — keduanya paket sistem bawaan AVD |
| Ulangan | 3 per subjek; snapshot `clean` dimuat ulang sebelum **setiap sesi** (6 reset) |
| Profil | `tier2_g1` (7 operasi: metadata otomatis + 6 operasi G1) |
| Kode | commit `b3b79da`; Android Debug Bridge 1.0.41 (Platform-Tools 37.0.1) |
| Data mentah | `experiments/feasibility_tier2/results/tier2_g1_avd1-api36.csv` (96 baris = 16 artefak × 2 subjek × 3 ulangan) |

## Status per artefak (15 artefak dinilai)

Pemetaan `actual_result` → status §11.1 mengikuti REF §TIER2: `observed` 3/3 = konsisten; `not_observed` → `unavailable`
(sumber terakses, datum tidak muncul).

| Artefak | Operasi | `settings` | `stk` | Status AVD #1 |
|---|---|---|---|---|
| G1-A1 package/UID/versi | `collect_package_inventory` | 3/3 | 3/3 | konsisten |
| G1-A2 path APK | `pull_subject_apk` | 3/3 | 3/3 | konsisten |
| G1-A3 berkas APK + SHA-256 | `pull_subject_apk` | 3/3 | 3/3 | konsisten |
| G1-A4 firstInstallTime / lastUpdateTime | `collect_package_detail` | 3/3 | 3/3 | konsisten |
| **G1-A5 installer / initiating / originating** | `collect_package_detail` | **0/3** | **0/3** | **`unavailable`** (pada 2 paket sistem; installer `null`) |
| G1-A6 tanda tangan / sertifikat | `collect_package_detail` | 3/3 | 3/3 | konsisten |
| G1-A7 komponen terdeklarasi | `collect_package_detail` | 3/3 | 3/3 | konsisten |
| G1-A8 izin diminta | `collect_package_detail` | 3/3 | 3/3 | konsisten |
| G1-A9 status izin diberikan | `collect_package_detail` | 3/3 | 3/3 | konsisten |
| G1-A10 UsageStats / UsageEvents | `collect_usage_state` | 3/3 | 3/3 | konsisten |
| G1-A11 status proses / aktivitas | `collect_usage_state` | 3/3 | 3/3 | konsisten |
| G1-B1 Accessibility Service aktif | `collect_accessibility_state` | 3/3 | 3/3 | konsisten |
| G1-B2 notification listener aktif | `collect_accessibility_state` | 3/3 | 3/3 | konsisten |
| G1-B3 status overlay / AppOps | `collect_accessibility_state` | 3/3 | 3/3 | konsisten |
| G1-B7 deklarasi receiver / service | `collect_package_detail` | 3/3 | 3/3 | konsisten |

Alasan `G1-A5` (`unavailable`, 6/6 ulangan): sumber (`dumpsys package`) diperoleh dan terurai penuh, tetapi datum installer
kosong (`null`) pada kedua paket sistem. Ini sifat **subjek** (paket bawaan tidak punya installer tercatat), bukan sifat
perangkat. Artefak ini belum teramati pada paket yang dipasang lewat installer; itu perlu subjek lain di Tier-2 konfirmatif.
Hasil ini bukan bukti bahwa installer "tidak ada" pada perangkat lain.

## Belum dinilai (di luar hitungan 3/3–0/3)

| Artefak | Alasan | Dinilai di |
|---|---|---|
| G1-B8 eksekusi boot / package-event teramati | Menilainya butuh atribusi event usage ke boot atau package-event, yang divalidasi dengan simulator. Ketersediaan sumbernya = G1-A10 (konsisten). Semua 6 baris `actual_result = not_evaluated` | `v0.80` |

## Catatan batas platform

- Sebelum batas unggah dinaikkan (revisi `v0.30.5`), APK `com.android.settings` (87 MB) gagal unggah (HTTP 413 pada 50 MiB).
  Itu batas platform, bukan sifat perangkat. Pada run ini batas 8 GiB dan `G1-A3` Settings 3/3 `acquired`.
- Jalur APK **split** tidak teramati di AVD #1: tidak ada paket split di perangkat ini. Jalur itu hanya teruji oleh test unit.

## Mekanisme `denied` dan `unsupported`

Tidak teramati di AVD #1: tidak ada baris dengan status `denied` atau `unsupported`. Mekanisme terkendali untuk
membangkitkannya masih data OPEN (tidak dibuat-buat).

## Perintah ADB final (API 36 yang diuji)

Argumen sesudah `-s <serial>`; `<pkg>` = `parameters.package_name`. Sumber tunggal string perintah:
`agent/src/device/adb_commands.py`.

| Operasi | part | Perintah |
|---|---|---|
| `collect_device_metadata` | 1 | `shell getprop` |
| `collect_package_inventory` | 1 | `shell pm list packages -U` |
| `collect_package_detail` | 1 | `shell dumpsys package <pkg>` |
| `collect_accessibility_state` | 1 | `shell settings get secure enabled_accessibility_services` |
| | 2 | `shell settings get secure enabled_notification_listeners` |
| | 3 | `shell appops get <pkg> SYSTEM_ALERT_WINDOW` |
| `collect_usage_state` | 1 | `shell dumpsys usagestats` |
| | 2 | `shell dumpsys activity activities` |
| | 3 | `shell ps -A -o PID,UID,USER,NAME` |
| `pull_subject_apk` | 1 | `shell pm path <pkg>` |
| | 2..1+S | `pull <path dari part 1> <berkas lokal agen>`, satu per APK |
| | sisanya | 9 berkas ekstraktor statis (dijalankan agen, bukan perintah adb) |

## Keterbatasan

- Dua subjek paket sistem pada satu AVD. Ini bukan sampel yang mewakili aplikasi pihak ketiga.
- Data hanya dari satu versi (Android 16 / API 36). Format keluaran versi lain belum terlihat.
- Kapabilitas ≠ perbuatan: hasil ini menyatakan apa yang **dapat diperoleh** dari perangkat, bukan apa yang dilakukan aplikasi.
