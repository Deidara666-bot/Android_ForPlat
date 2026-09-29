# Progress — Android_ForPlat

> Papan status hidup. **Satu-satunya file kendali yang diperbarui tiap sesi** (lewat `/card` dan `/wrap-up`).
> Aturan tetap di `CLAUDE.md` dan `.claude/`; rencana di `docs/dev/`. Tanggal format `YYYY-MM-DD`.

**Terakhir diperbarui:** 2026-09-30

## Posisi saat ini

| | |
|---|---|
| Core kanonik | `context/*_V3_3.md` — `FROZEN` (5 Sep 2026) |
| *Increment* aktif | **1 — Irisan tegak minimum** |
| Milestone aktif | **`v0.05`** (`docs/dev/v0.05.md`), branch `feature/v0.05` |
| Kartu terakhir | **`v0.05.2`** (2026-09-30) |
| Kartu berikutnya | **`/card v0.05.3`** (scaffold §AF, venv, .env, frontend) |
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

## Keputusan user (tercatat)

- 2026-09-26 — Model untuk eksekusi kartu (`/card`): **Sonnet**. `/plan-milestone` tetap disarankan model besar.
- 2026-09-26 — Migrasi VPS **setelah `v1.00`** (platform & infrastruktur lengkap dulu, semua pengembangan/pengujian
  lokal). Direncanakan sebagai milestone terpisah lewat `/plan-milestone` setelah tag `v1.00`.
- 2026-09-26 — Mirror GitHub → GitLab aktif: secret terpasang, workflow `mirror-gitlab` sukses (main `6c094de`);
  force push di GitLab `main` dimatikan kembali.

## Keputusan / aksi user yang tertunda

- [ ] Hapus remote `gitlab` lokal + branch `gitlab-backup` (isinya cuma 3 commit lama dari web UI GitLab,
      sudah tidak ada nilai unik — `.gitlab-ci.yml` di `main` sudah mengandung isi yang sama). Ditunda atas
      permintaan user 2026-09-30; selama remote `gitlab` ada, `/sync` masuk mode "push" ganda ke mirror.

## Data OPEN (jangan ditebak — isi hanya dari hasil nyata)

- [ ] Versi Android/API aktual Samsung Galaxy A10 → API AVD kedua (kartu v0.05.5)
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
- Remote `gitlab` masih ada di clone lokal ini (harusnya mode mirror-only, lihat item tertunda di atas) —
  `/sync` sengaja hanya push ke `origin` sampai remote itu dibereskan.

## Catatan diagram / naskah

- (kosong)
