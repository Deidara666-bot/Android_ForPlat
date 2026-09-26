---
paths:
  - "agent/**"
---

# Aturan agen lokal (`agent/`)

Dasar: `02_ARSITEKTUR` §L, §U, §V, §W, §AE (pohon `agent/`).

## Peran

Agen itu **tipis**: deteksi perangkat, eksekusi ADB ber-allowlist, penulisan bukti mentah, hashing,
unggah, heartbeat, status/progress, audit log lokal. ⛔ Tidak ada parsing semantik, normalisasi,
evaluasi aturan, atau penalaran malware di agen.

## Eksekusi ADB

- Backend hanya mengirim `operation` (ID) + `parameters`. Agen memetakan ID ke perintah yang
  **didefinisikan di kode agen** (`command_allowlist.py` / `acquisition_profiles.py`).
- ID operasi kandidat (§V): `collect_device_metadata`, `collect_package_inventory`,
  `collect_package_detail`, `collect_usage_state`, `collect_accessibility_state`,
  `collect_sensitive_provider_data`, `collect_network_stats`, `pull_subject_apk`.
  ID tak terdaftar → tolak, catat audit, jangan jalankan apa pun.
- Parameter divalidasi ketat sebelum dipakai (mis. `package_name` hanya `^[A-Za-z0-9_.]+$`, panjang
  dibatasi). Parameter tidak pernah disambung ke string perintah bebas.
- `subprocess.run([...], shell=False, timeout=..., capture_output=True)` dengan **list argumen**.
  ⛔ `shell=True`, `os.system`, f-string perintah shell.
- Path `adb` dari `ADB_PATH` (default `adb`), versi dicatat di setiap sesi.
- ⛔ Tidak ada rooting, `adb root`, `su`, exploit, bypass lockscreen, atau `adb install` sampel S-C.
  `privilege_detector.py` hanya **mendeteksi** status privilege.
- Tanpa library Python ADB khusus; deteksi perangkat cukup polling `adb devices -l`.

## Status ketersediaan

Setiap operasi menghasilkan tepat satu `availability_status`. Urutan klasifikasi kegagalan mengikat
(`01_BREAKDOWN` §8): `unsupported` → `denied` → `unavailable` → `failed` (sisa). Keluaran sukses yang
terurai = `acquired`. Alasan konkret masuk `availability_reason`; jangan diciutkan jadi satu label.

## Bukti & integritas

- Tulis stdout/stderr/berkas mentah **byte-exact** sebelum apa pun; lalu SHA-256 streaming
  (`hashlib.sha256`, baca per blok). Jangan mengubah encoding/line ending bukti.
- Unggah via HTTP; WebSocket hanya untuk status/job/progress/error, bukan bytes bukti.
- Retry jaringan boleh (`tenacity`), retry perintah akuisisi harus tercatat sebagai percobaan terpisah.

## Kode & test

- Dependency minimal (§L): `httpx`, `websockets`, `pydantic`, `pydantic-settings`, `tenacity`, `psutil`,
  `pytest`, `pytest-asyncio`. Dependency baru → tanya user.
- Konfigurasi via `pydantic-settings` dari `.env` (`BACKEND_BASE_URL`, `BACKEND_WS_URL`, `AGENT_TOKEN`,
  `ADB_PATH`, `AGENT_ID`, `POLL_INTERVAL_SECONDS`).
- Test unit **tidak butuh perangkat**: mock `subprocess` dan pakai fixture keluaran ADB di
  `agent/tests/fixtures/`. Test yang butuh AVD nyata diberi marker `@pytest.mark.device` dan dilewati
  default.
- Wajib ada test: ID operasi tak dikenal ditolak; parameter berbahaya (`;`, `&&`, spasi, `$()`) ditolak;
  hash konsisten; klasifikasi setiap `availability_status`.
