# ROADMAP

Model *Incremental* — urutan terkunci (akuisisi → parser → fakta → aturan → korelasi). Sumber: §AJ.
Status berjalan ada di `docs/progress.md`; berkas ini tidak berubah saat kartu selesai.

## Milestone

| Tag | Isi | Inc | Kartu | Berkas |
|---|---|---|---|---|
| `v0.05` | toolchain, scaffold, AVD #1, PostgreSQL naik (A10 → `v0.90.7`) | 1 | 5 | `v0.05.md` |
| `v0.10` | backend core + DB + migrasi + auth + React shell | 1 | 5 | `v0.10.md` |
| `v0.20` | agen: config, registrasi, allowlist, WS heartbeat, deteksi perangkat, dashboard | 1 | 7 | `v0.20.md` |
| `v0.30` | sesi akuisisi, 2 operasi allowlist, rantai SHA-256, bukti imutabel, audit | 1 | 8 | `v0.30.md` |
| `v0.40` | parser → Artifact → NormalizedEvent → tampil di UI (irisan tegak selesai) | 1 | 9 | `v0.40.md` |
| `v0.45` | seluruh artefak inti G1, Tier-2 formatif (AVD #1), 5 status → `evidence_state`, fakta negatif | 2 | 9 | `v0.45.md` (draf) |
| `v0.50` | Knowledge Base loader + validasi YAML | 3 | 5 | `v0.50.md` (draf) |
| `v0.60` | mesin aturan 3-keadaan, 5 keluarga APKF / 16 profil | 3 | 9 | `v0.60.md` (draf) |
| `v0.70` | G2 + G3, korelasi lintas sumber, rekonstruksi, UI keterlacakan | 4 | 9 | `v0.70.md` (draf) |
| `v0.80` | simulator aman + 20 kasus authoring | 5 | 10 | `v0.80.md` (draf) |
| `v0.90` | freeze + 8 holdout + kandidat statis + baseline manual + Tier-2 konfirmatif (AVD #1, AVD #2, A10) + hasil | 5 | 10 | `v0.90.md` (draf) |
| `v1.00` | prototipe terpadu, laporan, dokumentasi | — | 6 | `v1.00.md` (draf) |

Setelah `v0.10` pengembangan lokal sudah penuh (backend, DB, frontend jalan di laptop).
Setelah `v0.40` irisan tegak pertama selesai: satu fakta dari AVD tampil di UI dengan asal-usulnya.

Berkas **draf** (v0.45+) disegarkan lewat `/plan-milestone v0.XX` (mode *refresh*) sebelum kartu pertamanya.
Peta, jadwal, keputusan, dan daftar pangkas: `MAP.md`.

## Jalur VPS (setelah `v1.00` — keputusan user 2026-09-26)

Dikerjakan setelah pengembangan & pengujian lokal stabil; direncanakan sebagai milestone terpisah
lewat `/plan-milestone` ketika user memutuskan. Batas arsitektur yang sudah pasti:

- Pindah ke VPS: backend FastAPI, frontend build statis, PostgreSQL, penyimpanan bukti.
- **Tetap di laptop:** agen lokal + ADB + AVD/perangkat (agen butuh akses USB/ADB host, §H.1).
- Agen → VPS lewat HTTPS/WSS; wajib TLS, secret produksi baru (bukan `local-dev-*`), CORS domain VPS,
  user DB non-superuser, backup volume bukti. Data uji tetap sintetis.
- Keputusan terbuka yang ditutup saat itu: bentuk deployment dan distribusi agen (§AM butir 10).

## Kebutuhan tertutup per milestone (§11.2)

`v0.10` KF-01 kerangka, KNF-06, KNF-03 sebagian · `v0.20` KF-01 penuh, KNF-03 sebagian ·
`v0.30` KF-03, KNF-02, KNF-03 penuh, KF-02 sebagian · `v0.40` KF-04 sebagian besar.
