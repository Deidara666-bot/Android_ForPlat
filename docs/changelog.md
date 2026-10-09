# Changelog

Satu entri per tag milestone. Rincian kartu: `docs/progress.md`; bukti: `docs/smoke/`.

## v0.45 — 2026-10-09

Kelengkapan kelompok sumber G1 + Tier-2 formatif (AVD #1). Akhir Increment 2.

- Empat operasi G1 terpetakan dan terurai: `collect_package_detail`, `collect_accessibility_state`, `collect_usage_state`, `pull_subject_apk` (satu part per berkas APK, bundel statis 9 berkas). Parser ketat: struktur tak dikenali → artefak `failed` dengan catatan, tidak diurai sebagian.
- Fakta ternormalisasi G1 berlabel epistemik (identitas, deklarasi, kapabilitas aktif, penggunaan), semuanya `current_state` kecuali penggunaan aplikasi yang memakai zona waktu sesi; tidak ada `execution_observed` dari analisis statis.
- Cakupan sumber per bagian (`CoverageService`, `GET /api/cases/{id}/coverage`) dan fakta negatif eksplisit: hanya untuk subjek sesi, hanya bila sumber `acquired` dan terurai penuh; selain itu UNKNOWN beserta alasan.
- Lingkup pengguna Android 0: identitas dan negatif dari dump paket hanya bila terpasang untuk pengguna 0; pengguna lain hanya konteks (`other_users_installed`). Format blok pengguna lain diamati live di AVD #1 (fixture nyata).
- Unggah bukti streaming lewat karantina (batas 8 GiB per berkas, hash dihitung sambil menulis, pindah tanpa menimpa); split APK dan artefak konteks `native_libs` / `api_refs` tanpa fakta.
- Tier-2 G1 formatif, AVD #1 (API 36, 2 paket sistem, 3 ulangan dari snapshot `clean`): 15 artefak dinilai, 14 konsisten 3/3, `G1-A5` (installer) `unavailable` (sifat subjek); `G1-B8` `not_evaluated` dilaporkan terpisah. `denied` / `unsupported` tidak teramati. Ringkasan: `docs/tier2_g1.md`; data: `experiments/feasibility_tier2/results/tier2_g1_avd1-api36.csv`.
- 680 test backend + 214 test agen; `check.sh all` OK. Review `claim-auditor` + `forensic-integrity-reviewer`: 0 blocking; catatan non-blocking di `docs/progress.md`.
- Tidak digeneralisasi: hasil Tier-2 hanya AVD #1; lintas lingkungan di Tier-2 konfirmatif (`v0.90.8`).
- Tag ditempatkan di `main` setelah revisi lingkup pengguna 0 digabung; AVD #1 dipakai pada verifikasi akhir.

## v0.40 — 2026-10-02

Parser → Artifact → NormalizedEvent → UI. Akhir Increment 1 (irisan tegak minimum).

- Protokol `Parser` + registri eksplisit per operation ID (tanpa default/scan); parser `package_state.inventory` dan `package_state.device_metadata` (v1): baris rusak tetap `failed` dengan baris aslinya, decode gagal → 1 artefak `failed` dengan offset byte, kunci metadata hilang → `empty`.
- `artifacts` (tepat 10 kolom, `parse_note` wajib bila tidak `parsed`, migrasi `11d773cc1fb3`); `normalized_events` (tepat 17 kolom) + katalog tertutup 25 `event_type` (migrasi `0fc9d155262e`) + CHECK pasangan kelas–tipe (migrasi `a7c41d9e5b02`).
- Penormalisasi deterministik: `epistemic_class` dari katalog, satu klaim = satu fakta, keadaan saat ini → `event_time` null, bukti non-`acquired` / artefak `failed` → tanpa fakta (tidak pernah FALSE).
- `NormalizationService` dipicu setelah bukti `acquired` di-commit (galat → audit, bukti tetap); timezone sesi dari `persist.sys.timezone`, tidak menebak. CLI `python -m app.services.normalization_service`.
- `GET /api/cases/{id}`, `/artifacts`, `/events?event_type=` dengan asal-usul sampai SHA-256 bukti; tanpa `stored_path`, tanpa rute tulis. UI `/cases/:id/events` (`EventTimeline`, `ArtifactTable`).
- Irisan tegak di AVD #1: 252 artefak `parsed`, 496 fakta (248 + 248), 0 `failed`; panel asal-usul di browser menampilkan SHA-256 server yang sama dengan berkas bukti (diverifikasi pemeriksa dan dihitung ulang). Bukti: `docs/irisan_tegak_v0.40.md`.
- 235 test backend + 127 test agen; `check.sh all` OK. Review `claim-auditor` + `forensic-integrity-reviewer`: 0 blocking; 11 catatan non-blocking di `docs/progress.md`.
- Rencana direvisi saat berjalan (`68c3428`): `raw_value` wajib hanya untuk `parsed`.

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
