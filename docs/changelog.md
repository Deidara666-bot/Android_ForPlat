# Changelog

Satu entri per tag milestone. Rincian kartu: `docs/progress.md`; bukti: `docs/smoke/`.

## v0.05 — 2026-10-01

Toolchain, kerangka §AF, AVD #1, PostgreSQL. Increment 1.

- Toolchain terpasang (`docs/environment_baseline.md`); AVD `avd1-api36` (API 36, Google APIs) terbaca `adb`.
- Kerangka `agent/`, `backend/`, `frontend/` (Vite React-TS), `docker-compose.yml` (PostgreSQL 18.6, user aplikasi non-superuser).
- Butir smoke §AK yang ditunda dari kartu `v0.05.6` (`/api/health`, `/docs`, backend↔PostgreSQL, Alembic) tertutup oleh pekerjaan
  `v0.10` dan diverifikasi ulang saat tagging (`docs/smoke/v0.10.md`).
- Galaxy A10 tidak dipakai di milestone ini (`v0.05.5` dipindah ke `v0.90.7`).
- Deviasi implementasi: mount volume PostgreSQL `/var/lib/postgresql` (image 18.x), lihat `docs/core_deviations.md`.
- Tag ditempatkan di `main` setelah `v0.10.5` digabung; AVD dikonfirmasi user (emulator mati saat tagging).
