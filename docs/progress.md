# Progress — Android_ForPlat

> Papan status hidup. **Satu-satunya file kendali yang diperbarui tiap sesi** (lewat `/card` dan `/wrap-up`).
> Aturan tetap di `CLAUDE.md` dan `.claude/`; rencana di `docs/dev/`. Tanggal format `YYYY-MM-DD`.

**Terakhir diperbarui:** 2026-09-26

## Posisi saat ini

| | |
|---|---|
| Core kanonik | `context/*_V3_3.md` — `FROZEN` (5 Sep 2026) |
| *Increment* aktif | **1 — Irisan tegak minimum** |
| Milestone aktif | **`v0.05`** (`docs/dev/v0.05.md`) |
| Kartu terakhir | — |
| Kartu berikutnya | **`v0.05.1`** (USER: instal toolchain), lalu `/card v0.05.2` |
| Jalur naskah paralel | Generate 2 — paket 10 diagram `DGM-01`…`DGM-10` (`docs/diagrams/`), lalu BAB III Draft v3 |

Peta milestone lengkap: `docs/dev/ROADMAP.md`. Tag yang sudah dibuat: —

## Selesai

- 2026-09-26 — Rules Claude Code (`CLAUDE.md`, `.claude/rules|skills|agents|hooks`), pre-commit guard,
  `.gitignore`/`.gitattributes`.
- 2026-09-26 — Otomasi git: `/setup`, `/integrate`, `/sync`; GitHub Action `mirror-gitlab` (aktif, terverifikasi).
- 2026-09-26 — Rencana v0.05–v0.40 disusun ulang & disinkronkan (`docs/dev/`: README, ROADMAP, REF, 5 milestone,
  35 kartu); skill `/card`, `/plan-milestone`; `scripts/dev/check.sh`, `scripts/dev/init-env.sh`.

## Keputusan user (tercatat)

- 2026-09-26 — Model untuk eksekusi kartu (`/card`): **Sonnet**. `/plan-milestone` tetap disarankan model besar.
- 2026-09-26 — Migrasi VPS **setelah `v1.00`** (platform & infrastruktur lengkap dulu, semua pengembangan/pengujian
  lokal). Direncanakan sebagai milestone terpisah lewat `/plan-milestone` setelah tag `v1.00`.
- 2026-09-26 — Mirror GitHub → GitLab aktif: secret terpasang, workflow `mirror-gitlab` sukses (main `6c094de`);
  force push di GitLab `main` dimatikan kembali.

## Keputusan / aksi user yang tertunda

- [ ] Setujui perubahan `.claude/settings.json` di kartu `v0.05.2` (hook SessionStart + izin git + pagar `docs/dev`).
      Diblok classifier auto mode saat Claude mencoba mengubah setting-nya sendiri, jadi perlu persetujuan user.

## Data OPEN (jangan ditebak — isi hanya dari hasil nyata)

- [ ] Versi Android/API aktual Samsung Galaxy A10 → API AVD kedua (kartu v0.05.5)
- [ ] Perangkat lunak virtualisasi desktop yang dipakai (asumsi kerja: WHPX/Hyper-V, v0.05.1)
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

- GitHub `main` = `6c094de` berisi semua rules + rencana; GitLab ikut lewat `mirror-gitlab`.
- Tidak ada branch `claude/*` yang menunggu `/integrate` selain yang membawa catatan ini.

## Catatan diagram / naskah

- (kosong)
