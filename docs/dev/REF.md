# REF — nilai terkunci untuk kartu v0.05–v0.40

Satu-satunya rujukan nilai yang dipakai kartu. Kartu menulis `REF §X`; buka hanya seksi itu.
Diturunkan dari `context/02_ARSITEKTUR_*` dan `context/01_BREAKDOWN_*` v3.3. Urutan berlaku:
`docs/core_deviations.md` → core → REF. Beda REF vs core yang tidak tercatat di register → berhenti dan laporkan.
Keputusan plan (bukan dari core) ditandai `[plan]`.

## §SHELL — cara menjalankan perintah

- Claude Code di Windows memakai **Git Bash**. Semua blok `bash` di kartu dijalankan Claude.
- Path proyek mengandung spasi → selalu kutip path. Jangan tulis path absolut di kode.
- Python venv: `backend/.venv`, `agent/.venv`. Panggil lewat interpreter venv:
  - Windows: `.venv/Scripts/python.exe -m <tool>` · Linux: `.venv/bin/python -m <tool>`.
  - Singkatan di kartu: `PY` = interpreter venv komponen yang sedang dikerjakan.
- Buat venv: `py -3.13 -m venv .venv` (Windows) / `python3.13 -m venv .venv`.
- Gerbang mutu: `bash scripts/dev/check.sh <backend|agent|frontend|all>` → harus `CHECK OK`.
- `.env` dibuat `bash scripts/dev/init-env.sh`. ⛔ Jangan membaca/menampilkan isi `.env`.
- `docker compose exec` dengan argumen path diawali `/`: tambahkan `MSYS_NO_PATHCONV=1` di Git Bash.
- JWT untuk `curl` (tanpa menampilkan token, v0.10.4+):
  `JWT=$(cd backend && PY -m app.cli.dev_token --email pemeriksa@lab.local) && curl -H "Authorization: Bearer $JWT" ...`
  (env var tidak bertahan antar perintah → gabungkan dalam satu baris). Email pemeriksa dev: `pemeriksa@lab.local`.
  Di kartu disingkat `JWT=$(...dev_token...)`.
- Server dev dijalankan di background: backend `PY -m uvicorn app.main:app --port 8000`
  (dari `backend/`), frontend `npm run dev` (dari `frontend/`).

## §GIT — konvensi per kartu

- Satu milestone = satu branch `feature/v0.XX` dari `main`. Satu kartu = satu atau dua commit.
- Pesan commit: `type(scope): ringkasan [v0.XX.N]` (Inggris). Tag hanya di akhir milestone: `v0.XX`.
- Kartu terakhir milestone: `/finish-branch` lalu `/milestone v0.XX` (user menyetujui tag).

## §VER — versi & pin (§E, §K.1, §L, §M)

| Komponen | Versi |
|---|---|
| Python | 3.13.x · Node 24 LTS (npm 11) · PostgreSQL image `postgres:18.6` |
| Android Studio | Quail 3 2026.1.3 · SDK Platform 36 · Build-Tools 36.0.0 · Platform-Tools 37.0.1 (DEV-04) |
| AVD #1 | Pixel 6 · Android 16 / API 36 · **Google APIs** · x86_64 · tanpa akun · tanpa SIM · nama `avd1-api36` |

`backend/requirements.txt` (persis):
```text
fastapi[standard]==0.141.1
uvicorn[standard]==0.52.4
SQLAlchemy==2.0.52
alembic==1.19.1
psycopg[binary]==3.3.4
pydantic==2.13.4
pydantic-settings==2.15.0
PyYAML==6.0.3
pytest==9.1.1
aiofiles
httpx
pytest-asyncio
PyJWT
pwdlib[argon2]
```
`agent/requirements.txt` (persis):
```text
httpx
websockets
pydantic==2.13.4
pydantic-settings==2.15.0
tenacity
psutil
pytest==9.1.1
pytest-asyncio
```
`requirements-dev.txt` (kedua komponen): `ruff` · `mypy`. Setelah install: `PY -m pip freeze > requirements.lock.txt`.
⛔ Tanpa library ADB pihak ketiga. ⛔ Dependency baru di luar daftar ini → tanya user.

Frontend (versi eksak, `--save-exact`): `react@19.2.8` `react-dom@19.2.8` `react-router@8.3.0`
`vite@8.2.2` (dev). HTTP pakai `fetch`. ⛔ Tanpa axios, UI kit, state manager.

`pyproject.toml` (backend & agent):
```toml
[tool.ruff]
line-length = 100
target-version = "py313"
[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B"]
[tool.mypy]
python_version = "3.13"
warn_unused_ignores = true
disallow_untyped_defs = true
[tool.pytest.ini_options]
testpaths = ["tests"]
```

## §ENV — kunci `.env.example` (nama kunci terkunci; §S)

```text
# backend/.env.example
APP_ENV=development
DATABASE_URL=postgresql+psycopg://forensic_app:local-dev-only@localhost:5432/android_forensic
EVIDENCE_ROOT=./var/evidence
JWT_SECRET=change-me
CORS_ORIGINS=http://localhost:5173
# agent/.env.example
BACKEND_BASE_URL=http://localhost:8000
BACKEND_WS_URL=ws://localhost:8000/ws/agent
AGENT_TOKEN=change-me
ADB_PATH=adb
AGENT_ID=dev-agent-01
POLL_INTERVAL_SECONDS=2
# frontend/.env.example
VITE_API_BASE_URL=http://localhost:8000
VITE_WS_BASE_URL=ws://localhost:8000
```
- Password `DATABASE_URL` = `local-dev-only` (DEV-03).
- Config wajib **gagal keras** bila kunci hilang, dan menolak nilai rahasia `change-me` kecuali `APP_ENV=test`.
- DB test = nama DB `DATABASE_URL` + `_test` (diturunkan di `conftest.py`, bukan kunci baru).

## §DB — PostgreSQL dev

`docker-compose.yml` (root) — hanya service `postgres`:
```yaml
services:
  postgres:
    image: postgres:18.6
    container_name: android-forensic-postgres
    restart: unless-stopped
    environment:
      POSTGRES_DB: android_forensic
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: local-dev-admin
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql
      - ./infra/postgres/init:/docker-entrypoint-initdb.d:ro
volumes:
  postgres_data:
```
`infra/postgres/init/01-app-role.sql`:
```sql
CREATE ROLE forensic_app LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE PASSWORD 'local-dev-only';
ALTER DATABASE android_forensic OWNER TO forensic_app;
CREATE DATABASE android_forensic_test OWNER forensic_app;
```
- Mount `/var/lib/postgresql`, bukan `…/data` (image 18+; DEV-01). Admin terpisah dari user aplikasi
  non-superuser (DEV-02). ⛔ Agen/backend/frontend tidak dikontainerkan.
- Init script hanya jalan pada volume baru. Password di sini khusus dev lokal.
- psql cepat: `docker compose exec -T postgres psql -U forensic_app -d android_forensic -At -c "<SQL>"`.
  Di kartu disingkat `psql -c "<SQL>"`.

## §ENUM — himpunan tertutup (didefinisikan sekali di `backend/app/core/constants.py` sebagai `StrEnum`)

| Enum | Nilai (urutan tetap) · padanan UI |
|---|---|
| `AvailabilityStatus` | `acquired` diperoleh · `unavailable` tidak tersedia · `denied` ditolak · `unsupported` tidak didukung · `failed` gagal |
| `EpistemicClass` | `identity_attribute` atribut identitas · `capability_state` kapabilitas · `execution_observed` eksekusi teramati · `data_present` keberadaan data |
| `EvidenceState` | `observed_true` · `observed_false` · `unknown_unavailable` |
| `TemporalSemantics` | `historical_event` · `current_state` · `aggregated_window` · `unknown` |
| `SourceGroup` | `APP_SYSTEM_STATE` (G1) · `SENSITIVE_COMMUNICATION` (G2) · `NETWORK_ACTIVITY` (G3) · atau `NULL` untuk bukti konteks `[plan]` |
| `ParseStatus` `[plan]` | `parsed` · `failed` · `empty` |
| `ConnectionState` `[plan]` | `connected` · `disconnected` · `unknown` |
| `SessionStatus` `[plan]` | `pending` · `running` · `completed` · `failed` |
| `AgentState` `[plan]` | `starting` · `config_loaded` · `adb_validated` · `registered` · `connected` · `disconnected` · `stopped` |
| `PrivilegeState` `[plan]` | `non_root` · `root_detected` · `unknown` |

- Urutan klasifikasi kegagalan akuisisi (mengikat): `unsupported` → `denied` → `unavailable` → `failed` (sisa).
  Semua non-`acquired` → nanti `unknown_unavailable` → `UNKNOWN`, **tidak pernah** `FALSE`.
- DB: kolom enum = `TEXT` + `CHECK (kolom IN (...))` bernama `ck_<tabel>_<kolom>`.

## §OPS — ID operasi allowlist (§V) & perintah

Tepat 8, tertutup: `collect_device_metadata` · `collect_package_inventory` · `collect_package_detail` ·
`collect_usage_state` · `collect_accessibility_state` · `collect_sensitive_provider_data` ·
`collect_network_stats` · `pull_subject_apk`.

| ID | Dipetakan di | Argumen adb (sesudah `-s <serial>`) | `source_group` |
|---|---|---|---|
| `collect_device_metadata` | v0.30.3 | `shell getprop` | `NULL` (konteks) |
| `collect_package_inventory` | v0.30.3 | `shell pm list packages -U` | `APP_SYSTEM_STATE` |
| 6 lainnya | v0.45+ | — (galat `OperationNotMappedError`) | — |

- ID di luar 8 → `OperationNotAllowedError`. Dua galat **berbeda tipe**.
- String perintah ADB hanya boleh ada di `agent/src/device/adb_commands.py`, sebagai `list[str]`.
- Label `raw_source` (§OPS2) di backend hanya di `backend/app/core/raw_sources.py`. Grep larangan mengecualikan
  berkas itu dan `adb_commands.py` (v0.45.5).
- Setiap sesi diawali `collect_device_metadata`: backend menambahkannya sebagai `sequence` 1 bila profil/operasi tidak
  memuatnya (v0.45.8). Zona waktu sesi hanya dari bukti sesi itu.
- Satu sesi = paling banyak satu subjek: `parameters.package_name` dipakai semua operasi berparameter di sesi itu (v0.45.8).
- Deteksi perangkat (`adb devices -l`) dan `adb version` **bukan** operasi allowlist.

## §ENT — entitas & kolom (tabel snake_case jamak `[plan]`: hindari kata tercadang `user`, `case`)

Semua `id` = UUID (`server_default gen_random_uuid()`); semua waktu `timestamptz` UTC.

| Tabel (model) | Kolom | Lahir |
|---|---|---|
| `users` (User) | id, email UNIQUE, password_hash, created_at | v0.10.2 |
| `cases` (Case) | id, case_number UNIQUE, title, created_by → users.id, created_at | v0.10.2 |
| `devices` (Device) | id, serial UNIQUE, manufacturer, model, android_version, api_level, device_build, connection_state, last_agent_id → agents.id NULL, last_seen_at | v0.10.2 |
| `agents` (Agent) | id, agent_id UNIQUE, token_hash NULL, version, last_seen_at NULL | v0.10.2 |
| `case_devices` (CaseDevice) | case_id, device_id (PK gabungan) | v0.10.2 |
| `acquisition_sessions` | id, case_id, device_id, agent_id, agent_version, android_version, api_level, device_build, platform_tools_version, profile, commands_reported JSONB, started_at, ended_at, timezone, status, availability_status NULL, error NULL | v0.30.1 |
| `acquisition_operations` | id, session_id, sequence, operation_id, parameters JSONB, status — ⛔ tanpa kolom perintah | v0.30.1 |
| `evidence` (Evidence) | **tepat 19**: id, case_id, device_id, acquisition_session_id, operation_id, source_group, source_name, raw_source, stored_path, sha256_agent, sha256_server, size_bytes, acquired_at, availability_status, availability_reason, tool_version, android_version, device_build, privilege_state | v0.30.1 |
| `audit_logs` (AuditLog) | id, occurred_at, actor_type (`user`/`agent`/`system`), actor_id, event_type, object_type, object_id, reason, details JSONB | v0.30.6 |
| `artifacts` (Artifact) | **tepat 10**: id, evidence_id, artifact_type, parser_name, parser_version, subject_key NULL, raw_value, parsed_value_json JSONB, parse_status, parse_note | v0.40.2 |
| `normalized_events` (NormalizedEvent) | **tepat 17**: id, case_id, artifact_id, event_type, epistemic_class, subject_package NULL, subject_uid NULL, object_type, object_value, predicate_value NULL, event_time NULL, observed_at, window_start NULL, window_end NULL, temporal_semantics, evidence_state, context_json JSONB | v0.40.4 |

- `evidence.availability_reason` wajib bila status ≠ `acquired` (CHECK `ck_evidence_reason_required`).
- Nullable di `evidence`: `source_group`, `stored_path`, `sha256_agent`, `sha256_server`, `size_bytes`,
  `availability_reason`, `tool_version`, `android_version`, `device_build`, `privilege_state`
  (baris non-`acquired` / mismatch tidak punya berkas tersimpan). Kolom lain NOT NULL.
- ⛔ Jangan membuat tabel sebelum milestone lahirnya. ⛔ Jangan mengubah migrasi yang sudah di-commit.
- Hipotesis/aturan/KB (`RuleProfileEvaluation`, dst.) baru v0.50+.

## §EVT — katalog `event_type` (§Y.3.1a) — tepat 25, tertutup

| Kelas | event_type |
|---|---|
| `identity_attribute` (6) | `package_observed_installed` · `uid_observed` · `apk_identity_observed` · `apk_endpoint_reference_observed` · `scenario_subject_binding_observed` · `synthetic_exclusion_marker_observed` |
| `capability_state` (8) | `permission_observed_requested` · `sensitive_communication_capability_observed_granted` · `sensitive_communication_capability_observed_declared` · `accessibility_service_observed_declared` · `special_access_capability_observed_enabled` · `special_access_capability_observed_declared` · `event_trigger_capability_observed_declared` · `service_observed_declared` |
| `execution_observed` (7) | `event_trigger_execution_observed` · `app_usage_observed` · `activity_observed_resumed` · `process_observed_running` · `uid_network_activity_observed` · `local_endpoint_request_observed` · `lab_network_flow_observed` |
| `data_present` (4) | `sms_record_observed` · `contact_record_observed` · `call_log_record_observed` · `notification_context_observed` |

⛔ Bukan anggota katalog (meski muncul di contoh core, DEV-05): `permission_observed_granted`,
`accessibility_service_observed_enabled`, `overlay_permission_observed_active`.

## §API — rute (prefiks `/api`, semua kecuali health & login butuh auth)

| Rute | Auth | Lahir |
|---|---|---|
| `GET /api/health` | — | v0.10.3 |
| `POST /api/auth/login` · `GET /api/auth/me` | — · JWT | v0.10.4 |
| `GET/POST /api/cases` | JWT | v0.10.4 |
| `POST /api/agents/register` · `GET /api/agents` | JWT | v0.20.2 |
| `GET /api/devices` | JWT | v0.20.6 |
| `WS /ws/agent` (header `Authorization: Bearer <agent token>`) | agent | v0.20.5 |
| `WS /ws/dashboard?token=<JWT>` | JWT | v0.20.7 |
| `POST /api/acquisitions` · `GET /api/acquisitions/{session_id}` | JWT | v0.30.4 |
| `POST /api/evidence/upload` (multipart) | agent token | v0.30.5 |
| `GET /api/evidence/{evidence_id}` (tanpa `stored_path`) | JWT | v0.30.7 |
| `GET /api/cases/{case_id}` · `/artifacts` · `/events` | JWT | v0.40.7 |

Pesan WebSocket (JSON, field `type`): agent→backend `heartbeat`, `device_report`, `job_status`;
backend→agent `job` = `{type, session_id, sequence, operation, case_id, device_id, serial, parameters}` — ⛔ tanpa field lain.
- `sequence` = `acquisition_operations.sequence`; `serial` = `devices.serial`, pola `^[A-Za-z0-9._:-]{1,64}$`, ⛔ awalan `-`.
  Agen menjalankan hanya bila `serial` ada di daftar perangkat `device`; ⛔ agen memilih perangkat atau menghitung urutan sendiri.
- `job_status` = `{type, session_id, sequence, part, parts_total, operation, serial, sha256_agent, size_bytes, returncode, error}`
  (+ `availability_status`, `availability_reason` mulai v0.30.6; + `raw_source` mulai v0.45.6). Backend mencocokkan lewat `(session_id, sequence)`.
- `part` = urutan perintah dalam satu operasi (REF §OPS2), mulai 1; v0.30: `part = parts_total = 1`.
- Mulai v0.45.6: semua part dijalankan, masing-masing tepat satu status. Part yang bergantung pada part sebelumnya
  (`pull_subject_apk` part ≥ 2) tanpa prasyarat `acquired` → `failed`, alasan `prasyarat part <n> tidak diperoleh`,
  perintahnya tidak dijalankan. Operasi selesai saat `part == parts_total`; `failed` bila ada part bukan `acquired`.
Bita bukti **selalu** lewat `POST /api/evidence/upload`, tidak pernah WebSocket.

## §SVC — nama layanan (§X)

`AuthService` · `CaseService` · `AgentService` · `DeviceService` · `AcquisitionService` ·
`EvidenceStorageService` · `IntegrityService` · `AuditService` · `WebSocketConnectionManager` ·
`ArtifactService` · `NormalizationService`. Route tipis → service → model.

## §UI — halaman & komponen (§AC) sampai v0.40

- v0.10: `/login`, `/dashboard` · `AppShell`.
- v0.20: `AgentStatus`, `DeviceCard` di dashboard.
- v0.40: `/cases/:id/events` · `EventTimeline`, `ArtifactTable`.
- Teks UI Indonesia; pemakai = **pemeriksa** (⛔ *investigator*). ⛔ Label/warna/skor vonis
  (*malware*, berbahaya, mencurigakan). `event_time` null → "Waktu kejadian tidak tersedia".

## §PATH — lokasi runtime (semua di-ignore Git)

`backend/var/evidence/` (EVIDENCE_ROOT) · `agent/var/raw/` (bukti mentah sisi agen sebelum unggah).
Nama berkas bukti disusun server/agen dari `<session_id>/<sequence>-<operation_id>-<part>.bin`, ⛔ bukan dari input.

## §FIX — fixture sintetis (dipakai test; aman di-commit)

`backend/tests/fixtures/parsing/package_inventory_synthetic.txt`:
```text
package:com.synthetic.alpha uid:10101
package:com.synthetic.beta uid:10102
package:android uid:1000
```
`backend/tests/fixtures/parsing/device_metadata_synthetic.txt`:
```text
[ro.build.version.release]: [16]
[ro.build.version.sdk]: [36]
[ro.build.fingerprint]: [synthetic/sdk_gphone64_x86_64/emu64x:16/SYN.000000/1:userdebug/dev-keys]
[ro.product.model]: [sdk_gphone64_x86_64]
[persist.sys.timezone]: [Etc/UTC]
```
`backend/tests/fixtures/parsing/package_inventory_malformed_synthetic.txt`:
```text
package:com.synthetic.alpha uid:10101
paket-rusak-tanpa-uid
```

---

# Tambahan v0.45–v1.00

Seksi di bawah dipakai kartu `v0.45`–`v1.00` (status **draf**, disegarkan per milestone lewat
`/plan-milestone`). Seksi di atas tidak berubah.

## §OPS2 — perintah 6 operasi sisa (kandidat; difinalkan Tier-2 di milestone yang sama)

Satu operasi boleh menjalankan beberapa perintah berurutan → satu berkas bukti per perintah (`part`, REF §API) `[plan]`.
`<pkg>` = `parameters.package_name` (regex `^[A-Za-z0-9_.]{1,200}$`). Argumen sesudah `-s <serial>`.

| ID | part | Argumen | `raw_source` | Lahir |
|---|---|---|---|---|
| `collect_package_detail` | 1 | `shell dumpsys package <pkg>` | `dumpsys package` | v0.45 |
| `collect_accessibility_state` | 1 | `shell settings get secure enabled_accessibility_services` | `settings secure a11y` | v0.45 |
| | 2 | `shell settings get secure enabled_notification_listeners` | `settings secure nls` | |
| | 3 | `shell appops get <pkg> SYSTEM_ALERT_WINDOW` | `appops overlay` | |
| `collect_usage_state` | 1 | `shell dumpsys usagestats` | `dumpsys usagestats` | v0.45 |
| | 2 | `shell dumpsys activity activities` | `dumpsys activity` | |
| | 3 | `shell ps -A -o PID,UID,USER,NAME` | `ps` | |
| `pull_subject_apk` | 1 | `shell pm path <pkg>` | `pm path` | v0.45 |
| | 2 | `pull <path> <berkas lokal agen>` — `<path>` dari keluaran part 1 milik agen sendiri, regex `^/(data/app\|system\|product\|system_ext)/[^\s]+\.apk$`; ⛔ path dari backend | `apk file` | |
| | 3..n | ekstraktor §STATIC atas APK hasil part 2 (dijalankan agen) | `static:<nama berkas>` | |
| `collect_sensitive_provider_data` | 1 | `shell content query --uri content://sms` | `content sms` | v0.70 |
| | 2 | `shell content query --uri content://contacts/phones` | `content contacts` | |
| | 3 | `shell content query --uri content://call_log/calls` | `content call_log` | |
| `collect_network_stats` | 1 | `shell dumpsys netstats detail` | `dumpsys netstats` | v0.70 |

`source_group`: `collect_sensitive_provider_data` → `SENSITIVE_COMMUNICATION`; `collect_network_stats` →
`NETWORK_ACTIVITY`; sisanya `APP_SYSTEM_STATE`. ⛔ APK malware nyata (S-C) tidak pernah lewat `pull_subject_apk`.

## §STATIC — ekstraktor APK statis `[plan]` (K2 di MAP)

Logika: `agent/src/static_analysis/extractor.py` `extract(apk, out_dir) -> list[Path]` (urutan tabel di bawah);
CLI pembungkus untuk VM S-C: `scripts/static/extract_apk.py <apk> <folder_keluar>`. Python stdlib + alat SDK
(list argumen, ⛔ shell), ⛔ memasang/menjalankan APK.
Build-tools dicari dari `ANDROID_SDK_ROOT` → `ANDROID_HOME` → `%LOCALAPPDATA%/Android/Sdk`, versi 36.x.
Di `pull_subject_apk`, 7 berkas ini = part 3..9 (`raw_source` `static:<nama>`), `parts_total = 9`.

| Berkas bundel | Isi |
|---|---|
| `apk.sha256` | SHA-256 APK (hex) |
| `badging.txt` | `aapt2 dump badging <apk>` |
| `permissions.txt` | `aapt2 dump permissions <apk>` |
| `manifest.txt` | `aapt2 dump xmltree --file AndroidManifest.xml <apk>` |
| `certs.txt` | `apksigner verify --print-certs <apk>` (gagal verifikasi tetap dicatat) |
| `strings_urls.txt` | URL/domain/IP dari `classes*.dex` + `res/`, regex, urut unik, maks 5000 baris |
| `bundle.json` | `{apk_sha256, extractor_version, tool_versions, created_at, files:{nama: sha256}}` |

- S-A/S-B: dijalankan agen setelah `pull_subject_apk` (keluaran jadi bukti part 3..9). APK > 50 MiB → unggah part 2
  ditolak (413) → `failed`, dicatat apa adanya.
- S-C: dijalankan **di VM terisolasi** oleh user; hanya folder bundel (tanpa APK) yang diimpor lewat
  `POST /api/static-bundles` (v0.90). Keluaran `evidence_mode = apk_static`.

## §COV — cakupan fakta → sumber (v0.45.6–.7) `[plan]`

Cakupan dinilai per part `(operation_id, raw_source)`, bukan per operasi. Lingkup **perangkat** = berlaku untuk tiap subjek
di sesi itu; **subjek** = hanya `parameters.package_name` sesi itu. Sumber = sesi terbaru di kasus yang memuat part itu
(lingkup subjek: sesi dengan subjek itu).

| event_type (object_value) | Operasi · `raw_source` | Lingkup | Negatif (v0.45.7) |
|---|---|---|---|
| `package_observed_installed`, `uid_observed` | `collect_package_inventory` · `pm list packages -U` | perangkat | — |
| `sensitive_communication_capability_observed_granted` | `collect_package_detail` · `dumpsys package` | subjek | izin vocab tidak granted |
| `event_trigger_capability_observed_declared` | `collect_package_detail` · `dumpsys package` | subjek | action vocab tidak dideklarasikan |
| fakta deklaratif lain `collect_package_detail` | `collect_package_detail` · `dumpsys package` | subjek | — |
| `special_access_capability_observed_enabled` (`accessibility_service`) | `collect_accessibility_state` · `settings secure a11y` | perangkat | subjek tak ada di daftar |
| … (`notification_listener`) | `collect_accessibility_state` · `settings secure nls` | perangkat | subjek tak ada di daftar |
| … (`draw_over_other_apps`) | `collect_accessibility_state` · `appops overlay` | subjek | mode `ignore`/`deny` saja (`default` → tanpa fakta) |
| `app_usage_observed` | `collect_usage_state` · `dumpsys usagestats` | perangkat | — |
| `activity_observed_resumed` | `collect_usage_state` · `dumpsys activity` | perangkat | — |
| `process_observed_running` | `collect_usage_state` · `ps` | perangkat | — |
| fakta dari bundel statis | `pull_subject_apk` · `static:<nama>` | subjek | action vocab tidak dideklarasikan |

- Tanpa baris `evidence` untuk part itu → `not_acquired`; status bukan `acquired` → `availability_<status>`;
  ada artefak `failed` → `parse_incomplete`. FALSE hanya bila `acquired` + semua artefak `parsed`/`empty`.
- Fakta negatif hanya untuk subjek sesi, ⛔ untuk paket inventaris lain.

## §TIER2 — protokol Tier-2 lewat agen (§11.1) `[plan]`

- Runner host: `scripts/experiments/tier2_run.py --env <label> --profile <tier2_g1|tier2_g2g3|tier2_confirm> --reps 3`.
- Fase (§AJ.2): **formatif** `tier2_g1` (v0.45.9) & `tier2_g2g3` (v0.70.3) hanya `avd1-api36`; **konfirmatif**
  `tier2_confirm` (= operasi `tier2_g1` ∪ `tier2_g2g3`, subjek simulator `authoring`) di ketiga label (v0.90.8). Keputusan user 2026-09-30.
  Per ulangan: reset lingkungan (`scripts/adb/tier2_reset.sh <label>`) → `POST /api/acquisitions`
  (lewat agen, operasi allowlist) → tunggu sesi selesai → catat. ⛔ Reset bukan operasi agen dan tidak
  dipicu backend.
- Reset: AVD → `adb -s <serial> emu avd snapshot load clean` (snapshot `clean` dibuat sekali oleh user);
  Galaxy A10 → `adb -s <serial> reboot` + tunggu `sys.boot_completed=1`.
- Label lingkungan: `avd1-api36`, `avd2-api<N>`, `a10-api<N>` (N = `ro.build.version.sdk` Galaxy A10, dibaca di v0.90.7).
  Runner memverifikasi `api` label = sdk perangkat yang tersambung; beda atau perangkat tidak ada → berhenti sebelum reset.
- CSV `experiments/feasibility_tier2/results/<profile>_<env>.csv`, kolom:
  `artifact_id,env,subject,rep,android_version,api,build,device_or_emulator,operation_id,command,privilege_state,test_action,expected_evidence,actual_result,availability_status,availability_reason,raw_output_ref,temporal_semantics,git_commit,adb_version,acquired_at`.
- `actual_result` (per baris): `observed` (sumber terurai penuh + datum Tier-1 ada; nilai `null` setting terbaca utuh juga
  `observed`) · `not_observed` (sumber terurai, datum kosong) · `not_evaluated` (Tier-2 belum bisa menilai artefak ini) ·
  `parse_incomplete` · status non-acquired · `not_acquired`.
- Status per artefak per lingkungan (per subjek): hitung ulangan `observed` → 3/3 = konsisten · 1–2/3 = `CONDITIONAL` ·
  0/3 = dipilah §11.1 `unavailable`/`denied`/`unsupported`/`failed` + alasan (⛔ tidak diciutkan, ⛔ label lain):
  `not_observed` → `unavailable` (sumber terakses, datum tidak muncul); `parse_incomplete` → `failed`.
  Batas platform (mis. unggah > 50 MiB, HTTP 413) → `failed` + alasan "batas platform", bukan sifat perangkat; artefak dinilai
  dari subjek lain bila ada. Ringkasan di `docs/tier2_<profile>.md`.
- `not_evaluated` tidak masuk hitungan 3/3–0/3; dilaporkan terpisah dengan alasan dan kartu yang menilainya.
  G1-B8 = `not_evaluated` sampai atribusi boot/package-event divalidasi (v0.80, simulator); ketersediaan sumbernya = G1-A10.
- Pemetaan artefak Tier-1 → operasi: G1-A1/A2 `collect_package_inventory`/`pull_subject_apk` · G1-A3 `pull_subject_apk` ·
  G1-A4..A9, G1-B7 `collect_package_detail` · G1-A10, A11, B8 `collect_usage_state` · G1-B1..B3 `collect_accessibility_state` ·
  G2-C1, C3, C4 `collect_sensitive_provider_data` · G3-D1 `collect_network_stats`.

## §ENUM2 — himpunan tertutup v0.45+ (tambahkan ke `backend/app/core/constants.py`)

| Enum | Nilai |
|---|---|
| `ConditionState` | `TRUE` · `FALSE` · `UNKNOWN` (UI: terpenuhi · tidak terpenuhi · tidak diketahui) |
| `Outcome` | `matched` · `not_matched` · `insufficient_evidence` (UI: terpenuhi · tidak terpenuhi · bukti tidak memadai) |
| `EvaluationStatus` | `evaluated` · `skipped_not_applicable` |
| `ConditionRole` | `required` · `optional` · `contextual` · `exclusionary` |
| `ClaimLevel` | `identity` · `capability` · `observed_activity` · `contextual_cooccurrence` |
| `EvidenceMode` | `installed_runtime` · `apk_static` |
| `RunPurpose` | `authoring` · `holdout` · `benign_control` · `production` |
| `RuleStatus` | `design_baseline` · `authoring_candidate` · `frozen_for_holdout` |
| `InterpretationStatus` `[plan]` | `normal` · `constrained` |
| `ReferenceRole` | `artifact_semantics` · `behavior_relevance` · `interpretation_limit` · `technique_mapping` |
| `VerificationStatus` | `verified_design` · `verified` |
| `TimeBinding` | `current` · `not_applicable` · `case_window` · `observation_time` · `bucket_overlap` |
| `Operator` | `exists` · `equals` · `in` · `greater_than` · `delta_greater_than` · `overlaps_window` |
| `UnknownReason` `[plan]` | `availability_unavailable` · `availability_denied` · `availability_unsupported` · `availability_failed` · `not_acquired` · `parse_incomplete` · `coverage_incomplete` · `conflicting_evidence` · `no_applicable_profile` |
| `ReconstructionStatus` `[plan]` | `built` · `gate_not_met` |

## §VOCAB — kosakata `object_value` yang dibaca YAML (§14.2)

| event_type | `object_value` |
|---|---|
| `sensitive_communication_capability_observed_granted` / `_declared` | `android.permission.READ_SMS`, `RECEIVE_SMS`, `SEND_SMS`, `READ_CONTACTS`, `READ_CALL_LOG` (nama lengkap) |
| `permission_observed_requested` | nama permission lengkap (termasuk `android.permission.SYSTEM_ALERT_WINDOW`) |
| `special_access_capability_observed_enabled` / `_declared` | `accessibility_service` · `draw_over_other_apps` · `notification_listener` |
| `event_trigger_capability_observed_declared` | `android.intent.action.BOOT_COMPLETED`, `LOCKED_BOOT_COMPLETED`, `PACKAGE_ADDED`, `PACKAGE_REPLACED` (nama lengkap) |
| `uid_network_activity_observed` | UID sebagai teks; `context_json.total_bytes` (int) dipakai operator numerik |
| `accessibility_service_observed_declared`, `service_observed_declared` | nama komponen `pkg/.Kelas` |

Fakta negatif (`predicate_value=false`, `evidence_state=observed_false`) hanya untuk predikat tertutup di tabel ini,
dan hanya bila sumbernya `acquired` + terurai penuh untuk subjek itu (v0.45.6).

## §ENT2 — entitas v0.45+ (tabel jamak; kolom inti §AA.2; tambahan `[plan]` ditandai *)

| Tabel | Kolom | Lahir |
|---|---|---|
| `kb_sources` | id (teks `KB-…`), title, publisher, url, accessed_at, extracted_claim, version_scope, reference_role, quality_note, verification_status, active | v0.50 |
| `rule_metadata` | id, family_id, profile_id NULL (baris keluarga), version, status, applicability JSONB, claim_level NULL, incident_scope, content_hash, source_path*, loaded_at* | v0.50 |
| `rule_references` | rule_metadata_id, source_id (PK gabungan) | v0.50 |
| `rule_element_references` | id, rule_metadata_id, rule_element_key, source_id, reference_role, extracted_claim, version_scope, verification_status | v0.50 |
| `correlation_runs`* | id, case_id, evidence_mode, run_purpose, window_start NULL, window_end NULL, subjects JSONB, rule_set_hash, kb_hash, code_commit, created_at | v0.60 |
| `rule_family_evaluations` | id, correlation_run_id, family_id, rule_metadata_id*, subject_package*, subject_uid*, evidence_mode, run_purpose, outcome, matched_profile_ids JSONB, interpretation_status, reason NULL | v0.60 |
| `rule_profile_evaluations` | id, correlation_run_id, family_evaluation_id*, rule_id (→ rule_metadata), profile_id, subject_package*, subject_uid*, evidence_mode, run_purpose, evaluation_status, outcome NULL, interpretation_status, reason NULL, evaluated_at | v0.60 |
| `rule_condition_results` | id, profile_evaluation_id, condition_key (`profile_id.condition_id`), role, operator, selector_json, state, reason NULL, conflict_reason NULL | v0.60 |
| `rule_condition_facts` | condition_result_id, normalized_event_id (PK gabungan) | v0.60 |
| `correlation_findings` | id, family_evaluation_id, profile_evaluation_id UNIQUE, claim_level, interpretation_status, blocked_from_reconstruction, subject_package, subject_uid, window_start, window_end, summary | v0.60 |
| `reconstruction_runs` | id, correlation_run_id, subject_package, subject_uid, window_start, window_end, status | v0.70 |
| `reconstruction_findings` | reconstruction_run_id, finding_id, sequence_order, relation_type | v0.70 |
| `investigation_hypotheses` | id, reconstruction_run_id UNIQUE, statement, support_scope, missing_evidence JSONB, created_at — ⛔ tanpa UPDATE | v0.70 |
| `reports` | id, case_id, correlation_run_id, generated_at, content_hash, format | v1.00 |

`correlation_runs.subjects` = daftar package yang dievaluasi; default = package yang punya bukti
`collect_package_detail` (runtime) atau bundel statis (apk_static) di kasus itu.

## §YAML — lokasi & salinan aturan

- `backend/app/research/knowledge_base/data/sources.yaml` — 11 entri `01_BREAKDOWN` §12.1.
- `backend/app/research/rules/data/apk_fraud/APKF-K0N/family.yaml` — **salin apa adanya** blok YAML
  `01_BREAKDOWN` §14.2.N (buka hanya seksi itu: `grep -n "^### 14.2" context/01_BREAKDOWN_*.md`).
- Batas perubahan & commit: `.claude/rules/rules-kb-yaml.md` + skill `/rule-change`.

## §API2 — rute v0.45+

| Rute | Auth | Lahir |
|---|---|---|
| `GET /api/cases/{case_id}/coverage` (cakupan per sumber/subjek) | JWT | v0.45 |
| `GET /api/rules` · `GET /api/rules/{family_id}` · `GET /api/kb/sources` | JWT | v0.50 |
| `POST /api/cases/{case_id}/analyze` `{evidence_mode, run_purpose, window_start?, window_end?, subjects?}` | JWT | v0.60 |
| `GET /api/correlation-runs/{run_id}` · `GET /api/cases/{case_id}/evaluations?run=` · `GET /api/cases/{case_id}/findings?run=` | JWT | v0.60 |
| `GET /api/cases/{case_id}/reconstructions?run=` · `GET /api/trace/profile-evaluations/{id}` · `GET /api/trace/findings/{id}` | JWT | v0.70 |
| `POST /api/static-bundles` (multipart: `bundle.zip` + `case_id`) | JWT | v0.90 |
| `GET /api/cases/{case_id}/report?run=` (HTML) | JWT | v1.00 |

## §SIM — simulator & skenario `[plan]` (nilai final = data OPEN, diisi v0.80)

- Proyek `android-test-apps/safe-evidence-simulator/`; applicationId dasar `org.forplat.safesim`
  + suffix flavor `.authoring` · `.holdout` · `.control`. Keystore holdout lokal, ⛔ tidak di-commit.
- ID skenario: authoring `SA-K0N-<kelas>-NN` (kelas A/B/C/D1/D2/E/F), holdout `HO-NN`, benign `SB-<nama>-NN`.
- `ground_truth.json` = kontrak `02_ARSITEKTUR` §N.6 + `run_purpose`, `evidence_mode`, `rule_versions`,
  `expected_conditions` (`{condition_key: state}`), `expected_profiles`, `expected_families`.
- Endpoint lokal: `android-test-apps/local-endpoint/server.py` (stdlib `http.server`), dengar di `0.0.0.0:8765`,
  diakses emulator via `10.0.2.2:8765`; log JSON-lines per request → fakta `local_endpoint_request_observed`.
- Seed sintetis: `scripts/adb/seed_synthetic.sh <serial> <data.json>` (`adb emu sms send`, `content insert`).

## §UI2 — halaman & komponen v0.60+ (§AC)

v0.60: `/cases/:id/evaluations` · `EvaluationTable`, `FamilyProfilePanel`, `ConditionResultTable`, `ClaimLevelBadge`,
`MissingEvidenceBadge`, `ConflictEvidenceBadge`. · v0.70: `/cases/:id/findings`, `/cases/:id/reconstruction` ·
`FindingCard`, `EvidenceTracePanel` (tiga basis), `RuleReferencePanel`, `ReferenceRolePanel`, `ReconstructionTimeline`.
· v1.00: `/cases`, `/cases/:id`, `/cases/:id/device`, `/cases/:id/acquisition`, `/cases/:id/evidence`,
`/cases/:id/report` · `CaseTable`, `CaseSummary`, `AcquisitionPanel`, `AcquisitionProgress`, `EvidenceTable`, `ReportPreview`.
