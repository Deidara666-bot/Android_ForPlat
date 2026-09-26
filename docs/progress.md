# Progress — Android_ForPlat

> Papan status hidup. **Satu-satunya file kendali yang diperbarui tiap sesi** (lewat `/wrap-up`).
> Aturan tetap ada di `CLAUDE.md` dan `.claude/`. Tanggal format `YYYY-MM-DD`.

**Terakhir diperbarui:** 2026-09-26

## Posisi saat ini

| | |
|---|---|
| Core kanonik | `context/*_V3_3.md` — `FROZEN` (5 Sep 2026) |
| *Increment* aktif | **1 — Irisan tegak minimum** (belum dimulai) |
| Milestone berikutnya | **`v0.05`** — toolchain + repo + AVD/ADB smoke test |
| Branch aktif | `main` (lokal sudah merge `claude/confident-knuth-ceknlx` putaran 1, belum di-push) |
| Jalur naskah paralel | Generate 2 — paket 10 diagram `DGM-01`…`DGM-10` (`docs/diagrams/`), lalu BAB III Draft v3 |

## Milestone (`02_ARSITEKTUR` §AJ.2–§AJ.3)

| Tag | Isi | *Increment* | Status |
|---|---|---|---|
| `v0.05` | toolchain + repo + AVD/ADB smoke test (§AK) | 1 | ⏳ |
| `v0.10` | backend health + PostgreSQL migration + React shell | 1 | ⏳ |
| `v0.20` | agent device detection + heartbeat | 1 | ⏳ |
| `v0.30` | AcquisitionSession + 1 allowlisted operation + hash/upload | 1 | ⏳ |
| `v0.40` | parser + Artifact + NormalizedEvent kelompok sumber #1 (tampil di UI) | 1 | ⏳ |
| `v0.45` | validasi Tier-2 kelompok sumber terpilih | 2 | ⏳ |
| `v0.50` | Knowledge Base loader + validasi YAML | 3 | ⏳ |
| `v0.60` | rule engine + TRUE/FALSE/UNKNOWN (5 keluarga, 16 profil) | 3 | ⏳ |
| `v0.70` | korelasi lintas sumber + hipotesis + UI keterlacakan | 4 | ⏳ |
| `v0.80` | simulator aman + kasus authoring/benign/UNKNOWN/konflik/eksklusioner | 5 | ⏳ |
| `v0.90` | freeze + 8 holdout + kandidat statis + baseline manual + hasil | 5 | ⏳ |
| `v1.00` | prototipe terpadu + laporan + dokumentasi | konsolidasi | ⏳ |

## Selesai

- 2026-09-26 — Rules pengembangan Claude Code: `CLAUDE.md`, `.claude/rules/*`, `.claude/skills/*`,
  `.claude/agents/*`, `.claude/settings.json`, `.githooks/pre-commit`, `.gitignore`, `.gitattributes`,
  `docs/progress.md`.
- 2026-09-26 — Otomasi git: `/setup`, `/integrate`, `/sync` mode mirror GitLab, script
  `.claude/hooks/session-start.sh` (belum didaftarkan — lihat "Keputusan user").
- Sebelumnya — `.gitlab-ci.yml` (SAST + secret detection) dan dokumen core di `context/`.

## Langkah berikutnya

1. Sesi Claude Code lokal berikutnya: `/integrate` (bawa putaran 2 `claude/confident-knuth-ceknlx` ke
   `main`) → `/sync main` (main lokal juga belum di-push). Opsional: `/setup <url-gitlab>`.
2. Instal toolchain sesuai urutan `02_ARSITEKTUR` §P (bagian user: download/instal). `/setup` mengecek hasilnya.
3. Buat scaffold hari pertama `02_ARSITEKTUR` §AF di branch `feature/day1-scaffold`.
4. Jalankan checklist smoke test §AK → `/milestone v0.05`.
5. Mulai vertical slice `v0.10`–`v0.40`.

## Keputusan user

- [ ] Daftarkan hook `SessionStart` + izin git otomatis di `.claude/settings.json`. Diblok classifier
      *auto mode* saat Claude mencoba mengubah setting-nya sendiri, jadi perlu keputusan/aksi user.

## Data OPEN (jangan ditebak — isi hanya dari hasil nyata)

- [ ] Versi Android/API aktual Samsung Galaxy A10 (`getprop ro.build.version.release` / `.sdk`) → menentukan API AVD kedua
- [ ] Perangkat lunak virtualisasi desktop yang dipakai
- [ ] Perintah ADB final per versi Android untuk tiap operasi allowlist
- [ ] Status Tier-2 tiap artefak per lingkungan
- [ ] Package, varian, versi, SHA-256 simulator aman
- [ ] Aplikasi benign/kontrol (S-B) yang lolos verifikasi
- [ ] ≥6 kandidat & 3 APK malware nyata akhir + SHA-256 (analisis statis saja)
- [ ] Mekanisme terkendali pembangkit status `denied` dan `unsupported`
- [ ] Implementasi endpoint lokal, pengendali host, manifest eksperimen, `ground_truth.json`
- [ ] Katalog & hash 8 bundel holdout
- [ ] Bentuk deployment final dan distribusi agen (Python runtime vs executable)

## Sinkronisasi remote

- GitLab: mode **mirror** (tersambung ke GitHub; tanpa remote lokal `gitlab`).
- `origin/claude/confident-knuth-ceknlx`: putaran 2 (otomasi) belum masuk `main`.
- `main` lokal: berisi merge putaran 1, belum di-push ke `origin`.

## Catatan diagram / naskah

- (kosong)
