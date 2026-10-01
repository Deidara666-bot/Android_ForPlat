# Progress — Android_ForPlat

> Papan status hidup. **Satu-satunya file kendali yang diperbarui tiap sesi** (lewat `/card` dan `/wrap-up`).
> Aturan tetap di `CLAUDE.md` dan `.claude/`; rencana di `docs/dev/`. Tanggal format `YYYY-MM-DD`.

**Terakhir diperbarui:** 2026-10-01

## Posisi saat ini

| | |
|---|---|
| Core kanonik | `context/*_V3_3.md` — `FROZEN` (5 Sep 2026) |
| *Increment* aktif | **1 — Irisan tegak minimum** |
| Milestone aktif | **`v0.10`** (`docs/dev/v0.10.md`), branch `feature/v0.10` (tag `v0.05` belum dibuat; butir §AK ditutup di `v0.10.5`) |
| Kartu terakhir | **`v0.10.3`** (2026-10-01) |
| Kartu berikutnya | **`/card v0.10.4`** (auth JWT, CORS terbatas, rute `cases`; butuh PostgreSQL hidup) |
| Jalur naskah paralel | Generate 2 — paket 10 diagram `DGM-01`…`DGM-10` (`docs/diagrams/`), lalu BAB III Draft v3 |

Peta milestone lengkap: `docs/dev/ROADMAP.md`. Tag yang sudah dibuat: —

## Selesai

- 2026-09-26 — Rules Claude Code (`CLAUDE.md`, `.claude/rules|skills|agents|hooks`), pre-commit guard,
  `.gitignore`/`.gitattributes`.
- 2026-09-26 — Otomasi git: `/setup`, `/integrate`, `/sync`; GitHub Action `mirror-gitlab` (aktif, terverifikasi).
- 2026-09-26 — Rencana v0.05–v0.40 disusun ulang & disinkronkan (`docs/dev/`: README, ROADMAP, REF, 5 milestone,
  35 kartu); skill `/card`, `/plan-milestone`; `scripts/dev/check.sh`, `scripts/dev/init-env.sh`.
- 2026-09-30 — `v0.05.1` (USER, laptop): toolchain terpasang (Node diupgrade ke 24.19.0 LTS; sisanya sudah
  ada atau lebih tinggi dari target); WSL2/Virtual Machine Platform diaktifkan sehingga Docker Desktop jalan.
- 2026-09-30 — `v0.05.2`: `docs/environment_baseline.md` dicatat; `.claude/settings.json` diperbarui (hook
  SessionStart, izin git diperluas, pagar `Edit(/docs/dev/**)`) — disetujui user.
- 2026-09-30 — `.claude/settings.json`: tambah 4 deny yang kelewat di `v0.05.2` (`Read(/experiments/holdout_cases/**)`,
  `Bash(git push * --force*)`, `Bash(git push * -f*)`, `Bash(git push *+*)`). Remote `gitlab` lokal +
  branch `gitlab-backup` dihapus — `/sync` sekarang mode mirror-only sesuai desain.
- 2026-09-30 — `/plan-milestone` (sesi cloud): draft kartu `v0.45`–`v1.00` + `docs/dev/MAP.md` masuk ke
  `docs/dev/`, status **draf, belum di-review** — jangan dieksekusi sebagai kartu final sebelum user review.

- 2026-09-30 — `v0.05.3`: kerangka §AF, venv `backend/.venv` & `agent/.venv` (Python 3.13.7, paket belum di-install),
  frontend Vite react-ts (react 19.2.8, react-router 8.3.0, vite 8.2.2 eksak), `.env` tiga komponen dibuat lokal.
  Vite scaffold jalan non-interaktif tanpa perlu input user.
- 2026-09-30 — `v0.05.4`: AVD `avd1-api36` (API 36, Google APIs, x86_64, `userdebug`) terbaca `adb`; baseline dicatat.
  Uji gagal `su -c id` dijalankan user manual: `su: invalid uid/gid '-c'` (gagal, bukan uid=0; lulus). Image `userdebug`
  punya biner `su` — larangan akar ditegakkan allowlist agen, bukan emulator.
- 2026-10-01 — `v0.05.6`: PostgreSQL 18.6 naik, `forensic_app` non-superuser, `android_forensic_test` ada, smoke di
  `docs/smoke/v0.05.md`. Konversi path Git Bash **AKTIF** (pakai `MSYS_NO_PATHCONV=1`). **Temuan:** mount
  `postgres_data:/var/lib/postgresql/data` di REF §DB dan core §R ditolak image 18.x; `docker-compose.yml` diubah ke
  `/var/lib/postgresql`. User setuju 2026-10-01.
- 2026-10-01 — `v0.10.1`: dependensi backend terpasang (`requirements.lock.txt`), `pyproject.toml`, `app/core/{config,constants,
  security,logging}`, 6 test unit lulus, `check.sh backend` OK, uji gagal `_probe.py` → `CHECK FAILED` lalu OK.
- 2026-10-01 — `v0.10.2`: `app/db`, 5 model operasional, Alembic (`e44e1f26d772`), dev DB di `head`, 7 test lulus (termasuk
  roundtrip migrasi di DB `_test`). Asumsi: kolom REF §ENT tanpa tanda NULL dibuat NOT NULL (termasuk `devices.last_seen_at`).
- 2026-10-01 — `v0.10.3`: `GET /api/health` menyentuh DB (200 / 503), `/docs` 200, 9 test lulus. **Temuan:** koneksi DB tanpa
  timeout membuat health menggantung saat PostgreSQL mati (uji gagal awal: tanpa respons); diperbaiki dengan
  `connect_timeout=3` di `app/db/session.py`. Dua butir §AK (`/api/health`, `/docs`, backend↔DB, Alembic) kini terbukti; smoke
  resmi di `docs/smoke/v0.10.md` (`v0.10.5`).

## Keputusan user (tercatat)

- 2026-09-26 — Model untuk eksekusi kartu (`/card`): **Sonnet**. `/plan-milestone` tetap disarankan model besar.
- 2026-09-26 — Migrasi VPS **setelah `v1.00`** (platform & infrastruktur lengkap dulu, semua pengembangan/pengujian
  lokal). Direncanakan sebagai milestone terpisah lewat `/plan-milestone` setelah tag `v1.00`.
- 2026-09-26 — Mirror GitHub → GitLab aktif: secret terpasang, workflow `mirror-gitlab` sukses (main `6c094de`);
  force push di GitLab `main` dimatikan kembali.
- 2026-09-30 — **Galaxy A10 dilepas dari jalur pengembangan** (MAP K6). Tier-2 formatif (`v0.45.9`, `v0.70.3`) hanya
  AVD #1; A10 + AVD #2 hanya di Tier-2 konfirmatif `v0.90.7`–`.8` (pembedaan formatif/konfirmatif `02_ARSITEKTUR` §AJ.2).
  `v0.05.5` dipindah ke `v0.90.7`; `v0.05.6` jalan tanpa itu; tag `v0.05` dibuat tanpa A10. Tambahan `[plan]`: parser
  ketat (struktur tak dikenali → `failed`). Tanpa amandemen core. Alasan: A10 belum tersedia dalam waktu dekat,
  dan pengembangan dikerjakan dulu sampai software jadi baru pengujian penelitian.
- 2026-10-01 — Core tidak diamandemen untuk beda tingkat implementasi; dicatat di `docs/core_deviations.md`
  (DEV-01..05, termasuk mount PostgreSQL). Substansi penelitian tetap lewat amandemen berkelompok. CLAUDE.md §1/§10 disesuaikan.

## Keputusan / aksi user yang tertunda

- Setujui tag `v0.05` (`/milestone v0.05`).
- Galaxy A10 harus tersedia paling lambat `v0.90.7`, dan versinya dibutuhkan sebelum BAB III 3.3 final. Bila tidak ada
  → keputusan amandemen `G-05` (ganti perangkat / lepas AVD #2 dari A10 / emulator saja dengan batasan dinyatakan).

## Data OPEN (jangan ditebak — isi hanya dari hasil nyata)

- [ ] Versi Android/API aktual Samsung Galaxy A10 → API AVD kedua (kartu v0.90.7, dipindah dari v0.05.5)
- [x] Perangkat lunak virtualisasi desktop yang dipakai → **WHPX** (Windows 11 Home, tanpa Hyper-V), diverifikasi
      `emulator -accel-check` 2026-09-30.
- [ ] Perintah ADB final per versi Android untuk tiap operasi allowlist (2 pertama di v0.30.3)
- [ ] Status Tier-2 tiap artefak per lingkungan (v0.45)
- [ ] Package, varian, versi, SHA-256 simulator aman
- [ ] Aplikasi benign/kontrol (S-B) yang lolos verifikasi
- [ ] ≥6 kandidat & 3 APK malware nyata akhir + SHA-256 (analisis statis saja)
- [ ] Mekanisme terkendali pembangkit status `denied` dan `unsupported`
- [ ] Implementasi endpoint lokal, pengendali host, manifest eksperimen, `ground_truth.json`
- [ ] Katalog & hash 8 bundel holdout
- [ ] Bentuk deployment final (VPS) dan distribusi agen

## Sinkronisasi remote

- 2026-09-30 — `/integrate`: `origin/claude/confident-knuth-ceknlx` (`b85f0ff`) digabung ke `main`, push ke
  GitHub sukses (`main` = `f29eb81`). Tidak ada branch `claude/*` lain yang menunggu.
- 2026-09-30 — `feature/v0.05` (kartu `v0.05.2`, commit `fdd1806`+`905f1f4`) digabung dengan `main` lalu
  di-push ke GitHub via `/sync` — sekarang terlihat dari sesi cloud mana pun.
- 2026-09-30 — Remote `gitlab` lokal + branch `gitlab-backup` dihapus (isinya cuma 3 commit lama dari web UI
  GitLab, sudah tercakup di `.gitlab-ci.yml` `main`). `/sync` kembali mode mirror-only default.
- 2026-09-30 — `/integrate` kedua: `origin/claude/confident-knuth-ceknlx` (`56a86fa`+`8959085`, draft kartu
  `v0.45`–`v1.00` dari `/plan-milestone`) digabung ke `main` (push `main` = `20c4275`), lalu `main` digabung
  ke `feature/v0.05` dan di-push (`feature/v0.05` = `675554e`). Tidak ada branch `claude/*` lain yang menunggu.

## Catatan diagram / naskah

- (kosong)
