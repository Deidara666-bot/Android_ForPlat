# REF — nilai terkunci untuk kartu v0.05–v0.40

Satu-satunya rujukan nilai yang dipakai kartu. Kartu menulis `REF §X`; buka hanya seksi itu.
Diturunkan dari `context/02_ARSITEKTUR_*` dan `context/01_BREAKDOWN_*` v3.3. Bila REF dan core
berbeda → core menang; berhenti dan laporkan. Keputusan plan (bukan dari core) ditandai `[plan]`.

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
| Android Studio | Quail 3 2026.1.3 · SDK Platform 36 · Build-Tools 36.0.0 · Platform-Tools 37.0.0 |
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
- `[plan]` Password `DATABASE_URL` disamakan dengan compose (`local-dev-only`); core §S.1 menulis `password` yang tidak cocok dengan §R.
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
      - postgres_data:/var/lib/postgresql/data
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
- `[plan]` Admin terpisah dari user aplikasi karena `POSTGRES_USER` image resmi selalu superuser,
  sedangkan §AD mewajibkan user aplikasi non-superuser. ⛔ Agen/backend/frontend tidak dikontainerkan.
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

⛔ Bukan anggota katalog (meski muncul di contoh core): `permission_observed_granted`,
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
backend→agent `job` = `{type, session_id, operation, case_id, device_id, parameters}` — ⛔ tanpa field lain.
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
Nama berkas bukti disusun server/agen dari `<session_id>/<sequence>-<operation_id>.bin`, ⛔ bukan dari input.

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
```
`backend/tests/fixtures/parsing/package_inventory_malformed_synthetic.txt`:
```text
package:com.synthetic.alpha uid:10101
paket-rusak-tanpa-uid
```
