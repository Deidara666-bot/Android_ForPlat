# Irisan tegak v0.40

Dicatat dari `/card v0.40.9`, 2026-10-02. Keluaran nyata, AVD #1 (`avd1-api36`, `emulator-5554`). Satu kasus baru
`SLICE-V040`, satu akuisisi profil `baseline_v030`. Backend, agen, dan `npm run dev` dijalankan sebagai skrip.
Tanpa daftar package dan tanpa isi bukti.

## Lingkungan
```text
git HEAD (sebelum commit kartu) : 37ed890c73222a9954c121a5286206f85f7efcfe   (branch feature/v0.40)
adb                              : Android Debug Bridge version 1.0.41, Version 37.0.1-15733141
alembic head                     : a7c41d9e5b02
case_id                          : d69d0efc-95e4-4b30-a7cb-427a7a2bd6c4
session_id                       : 6fb2b800-9ef7-4590-9595-bde3213dd3f6   (status completed)
```
Nilai build dan zona waktu perangkat (dari artefak `package_state.device_metadata`):
```text
ro.build.version.release : 16
ro.build.version.sdk     : 36
ro.build.fingerprint     : google/sdk_gphone64_x86_64/emu64xa:16/BE2A.250530.026.F3/13894323:userdebug/dev-keys
persist.sys.timezone     : Asia/Bangkok
acquisition_sessions.timezone (sesi ini) : Asia/Bangkok   (diisi otomatis, audit session_timezone_set)
```

## Langkah 2 — fakta ternormalisasi
```text
event_type                  | epistemic_class    | count
package_observed_installed  | identity_attribute | 248
uid_observed                | identity_attribute | 248
```
Tepat 2 baris, N sama (248), N ≥ 1.

## Langkah 3 — artefak
```text
parser_name                    | parse_status | count
package_state.device_metadata  | parsed       | 4
package_state.inventory        | parsed       | 248
```
Total `package_state.device_metadata` = 4. Artefak `failed` = **0** (tidak ada baris yang tidak sesuai bentuk).

## Langkah 4 — waktu
```text
select count(*) ... where event_time is not null or temporal_semantics <> 'current_state'  →  0
```

## Langkah 5 — pemrosesan ulang dan integritas
```text
python -m app.services.normalization_service --evidence-id <id inventaris>
{"artifacts_created": 0, "facts_created": 0, "skipped_reason": "sudah diproses"}
jumlah setelah ulang : 252 artefak (248 + 4), 496 fakta (248 x 2)  — tetap
sha256_server (collect_package_inventory) : fad458c4f9644bc8fb4c724cfb64e971ef783f900010a67bc7730ce2d08b523f
sha256sum berkas di backend/var/evidence  : fad458c4f9644bc8fb4c724cfb64e971ef783f900010a67bc7730ce2d08b523f   (sama)
```
Kedua bukti: `availability_status = acquired`, `sha256_agent = sha256_server`.

## Audit sesi ini
```text
job_issued x2 · upload_accepted x2 · session_timezone_set x1 (Asia/Bangkok, sumber persist.sys.timezone)
```

## Uji gagal
```text
BEGIN; UPDATE normalized_events SET event_type='permission_observed_granted' WHERE case_id=...; ROLLBACK;
ERROR: new row for relation "normalized_events" violates check constraint "ck_normalized_events_class_matches_type"
```
Ditolak oleh basis data, dan jumlah fakta tetap 496 setelah `ROLLBACK`. **Selisih dari teks kartu:** kartu menduga galat
menyebut `ck_normalized_events_event_type`. `permission_observed_granted` melanggar dua CHECK sekaligus (`event_type` dan
pasangan kelas–tipe dari `v0.40.5`); PostgreSQL melaporkan satu nama saja, yaitu urutan alfabet pertama
(`class_matches_type`). Hasilnya tetap penolakan, hanya nama constraint yang berbeda (dicatat di `progress.md`, `v0.40.5`).

## Belum diverifikasi oleh agen (langkah USER)
Tampilan `http://localhost:5173/cases/d69d0efc-95e4-4b30-a7cb-427a7a2bd6c4/events`: panel asal-usul satu fakta
`package_observed_installed` dan kecocokan SHA-256 server dengan bukti.
