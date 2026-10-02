# Changelog

Satu entri per tag milestone. Rincian kartu: `docs/progress.md`; bukti: `docs/smoke/`.

## v0.30 — 2026-10-02

Sesi akuisisi, 2 operasi allowlist, rantai SHA-256, bukti imutabel. Increment 1.

- Model `acquisition_sessions`, `acquisition_operations`, `evidence` (tepat 19 kolom; `sha256_agent` dan `sha256_server` terpisah); CHECK status/sumber/alasan-wajib diuji dengan nama constraint; migrasi `7d73dea04b57`.
- Dua operasi dipetakan (`collect_device_metadata`, `collect_package_inventory`); enam ID sah lain tetap `OperationNotMappedError`. Job ke agen 8 field (`sequence`, `serial`), serial divalidasi (tolak awalan `-`); agen tidak memilih perangkat atau menghitung urutan.
- Rantai integritas (kontrak §W): agen tulis byte-exact (`xb`) → SHA-256 agen → unggah multipart → server hash ulang sendiri → banding → simpan read-only. Mismatch ditolak, baris `failed` menyimpan dua hash, tanpa berkas; unggah kedua tidak menimpa (409); nama berkas disusun server.
- `AuditService` + `audit_logs` (migrasi `50735e96c7aa`); 5 kejadian akuisisi/unggah, ditambah penolakan 401/422 pada rute akuisisi dan bukti (satu baris per kejadian per path per 60 detik, tanpa token/nilai). Klasifikasi ketersediaan `unsupported → denied → unavailable → failed`; hasil non-acquired menjadi baris `evidence` tanpa berkas dengan alasan.
- `GET /api/evidence/{id}` dan `GET /api/acquisitions/{id}`: rantai asal-usul dua arah (bukti ↔ sesi ↔ operasi ↔ perangkat ↔ kasus) dengan jumlah query tetap; tanpa `stored_path`, tanpa rute unduh.
- 138 test backend + 127 test agen; `check.sh all` OK. Review `claim-auditor` + `forensic-integrity-reviewer`: 0 blocking; 10 catatan non-blocking di `docs/progress.md`.
- Rencana direvisi saat berjalan (`1ef5ec5`): `sequence`/`serial` dibawa job. Bukti: `docs/smoke/v0.30.md`.

## v0.20 — 2026-10-02

Agen: registrasi, allowlist, WebSocket, deteksi perangkat, dasbor langsung. Increment 1.

- Registrasi agen: token acak, hanya SHA-256 tersimpan; `POST/GET /api/agents`, `GET /api/agents/me` (token agen), skrip `register-agent.sh`.
- Gerbang allowlist (kontrak): 8 ID operasi, `OperationNotAllowedError` ≠ `OperationNotMappedError`, `AcquisitionJob` `extra=forbid`,
  string ADB hanya di `adb_commands.py`, `shell=False`, privilege detector hanya membaca.
- `/ws/agent` (Bearer sebelum accept) + heartbeat + reconnect berbatas (audit); deteksi perangkat dengan metadata aman (bukan bukti),
  `GET /api/devices`; `AgentStateMachine`; `/ws/dashboard` dan dasbor `AgentStatus`/`DeviceCard` berubah tanpa refresh.
- Agen masih skrip Python (`python -m src.main`), belum dibungkus. 42 test backend + 31+ test agen lulus; `check.sh all` OK.
- Review `claim-auditor` + `forensic-integrity-reviewer`: 0 blocking; 10 catatan non-blocking di `docs/progress.md`.
- Bukti: `docs/smoke/v0.20.md` (dasbor diverifikasi pemeriksa).

## v0.10 — 2026-10-01

Backend core, DB, migrasi, auth, React shell. Increment 1.

- `app/core` (config gagal-keras, enum tertutup REF §ENUM, argon2 + JWT 60 menit, logging); 5 tabel operasional + migrasi
  Alembic `e44e1f26d772`.
- `GET /api/health` menyentuh PostgreSQL (200 / 503, `connect_timeout=3`), `/docs`; login JWT, `/api/auth/me`, rute `cases`
  (201/409), CORS terbatas (tanpa `*`).
- Frontend `/login` dan `/dashboard` (health); diverifikasi user di browser. 19 test lulus; `check.sh all` OK (agent: SKIP).
- Review `claim-auditor` + `forensic-integrity-reviewer`: 0 blocking; catatan non-blocking di `docs/progress.md`.
- Bukti: `docs/smoke/v0.10.md`.

## v0.05 — 2026-10-01

Toolchain, kerangka §AF, AVD #1, PostgreSQL. Increment 1.

- Toolchain terpasang (`docs/environment_baseline.md`); AVD `avd1-api36` (API 36, Google APIs) terbaca `adb`.
- Kerangka `agent/`, `backend/`, `frontend/` (Vite React-TS), `docker-compose.yml` (PostgreSQL 18.6, user aplikasi non-superuser).
- Butir smoke §AK yang ditunda dari kartu `v0.05.6` (`/api/health`, `/docs`, backend↔PostgreSQL, Alembic) tertutup oleh pekerjaan
  `v0.10` dan diverifikasi ulang saat tagging (`docs/smoke/v0.10.md`).
- Galaxy A10 tidak dipakai di milestone ini (`v0.05.5` dipindah ke `v0.90.7`).
- Deviasi implementasi: mount volume PostgreSQL `/var/lib/postgresql` (image 18.x), lihat `docs/core_deviations.md`.
- Tag ditempatkan di `main` setelah `v0.10.5` digabung; AVD dikonfirmasi user (emulator mati saat tagging).
