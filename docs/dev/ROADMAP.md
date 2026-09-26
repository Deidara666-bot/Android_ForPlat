# ROADMAP

Model *Incremental* — urutan terkunci (akuisisi → parser → fakta → aturan → korelasi). Sumber: §AJ.
Status berjalan ada di `docs/progress.md`; berkas ini tidak berubah saat kartu selesai.

## Milestone

| Tag | Isi | Inc | Kartu | Berkas |
|---|---|---|---|---|
| `v0.05` | toolchain, scaffold, AVD #1, Galaxy A10 dibaca, PostgreSQL naik | 1 | 6 | `v0.05.md` |
| `v0.10` | backend core + DB + migrasi + auth + React shell | 1 | 5 | `v0.10.md` |
| `v0.20` | agen: config, registrasi, allowlist, WS heartbeat, deteksi perangkat, dashboard | 1 | 7 | `v0.20.md` |
| `v0.30` | sesi akuisisi, 2 operasi allowlist, rantai SHA-256, bukti imutabel, audit | 1 | 8 | `v0.30.md` |
| `v0.40` | parser → Artifact → NormalizedEvent → tampil di UI (irisan tegak selesai) | 1 | 9 | `v0.40.md` |
| `v0.45` | seluruh artefak inti G1, Tier-2 formatif, 5 status → `evidence_state`, fakta negatif, AVD #2 | 2 | — | via `/plan-milestone` |
| `v0.50` | Knowledge Base loader + validasi YAML | 3 | — | |
| `v0.60` | mesin aturan 3-keadaan, 5 keluarga APKF / 16 profil | 3 | — | |
| `v0.70` | G2 + G3, korelasi lintas sumber, rekonstruksi, UI keterlacakan | 4 | — | |
| `v0.80` | simulator aman + 20 kasus authoring | 5 | — | |
| `v0.90` | freeze + 8 holdout + kandidat statis + baseline manual + hasil | 5 | — | |
| `v1.00` | prototipe terpadu, laporan, dokumentasi | — | — | |

Setelah `v0.10` pengembangan lokal sudah penuh (backend, DB, frontend jalan di laptop).
Setelah `v0.40` irisan tegak pertama selesai: satu fakta dari AVD tampil di UI dengan asal-usulnya.

## Jalur VPS (belum dijadwalkan)

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
