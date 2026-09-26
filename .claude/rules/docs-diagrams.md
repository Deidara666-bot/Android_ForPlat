---
paths:
  - "docs/**"
---

# Aturan dokumentasi & diagram (`docs/`)

Dasar: `02_ARSITEKTUR` §AE (pohon `docs/`), §AO; `01_BREAKDOWN` §4.7, §22A; `BAB_03_WORKING` §7–§9.

## Peran `docs/`

Repo ini sekaligus **repositori penelitian berversi** yang dirujuk naskah (skripsi tidak memakai lampiran
formal). Isi target: `architecture.md`, `setup.md`, `acquisition_profiles.md`, `evidence_source_matrix.md`,
`normalized_event_schema.md`, `rule_authoring.md`, `test_protocol.md`, `sample_selection.md`,
`simulator_safety_contract.md`, `data_dictionary.md`, `diagrams/`, `changelog.md`, dan `progress.md`.

- `docs/progress.md` = satu-satunya papan status yang berubah tiap sesi (milestone, langkah berikutnya,
  data OPEN, catatan sinkronisasi remote).
- `docs/changelog.md` = catatan perubahan yang bermakna (skema, aturan/KB, freeze, rilis milestone).
- Dokumentasi mendeskripsikan yang **sudah dibangun**, merujuk seksi core untuk rancangan; jangan
  menyalin ulang dokumen core panjang-panjang.

## Bahasa

Indonesia akademik, istilah mengikuti padanan terkunci `01_BREAKDOWN` §4.7 (*fakta ternormalisasi*,
*keterlacakan dua arah*, *tanpa akses akar*, *pemeriksa*, dst.). Nama teknis (`event_type`, nama tabel)
ditulis dalam `code`. ⛔ Frasa vonis: "malware terdeteksi", "APK terbukti menipu", "eksfiltrasi",
"akses terjadi" tanpa bukti pada tingkat klaim yang benar.

## Diagram (`docs/diagrams/`)

- Sepuluh diagram `DGM-01` … `DGM-10` (spesifikasi `02_ARSITEKTUR` §AO). Setiap diagram: sumber `.drawio`
  yang bisa diedit + ekspor PNG resolusi tinggi, nama berkas `DGM-0X-<slug>.drawio` / `.png`.
- Konektor ortogonal, tidak menembus node, maks. lima node horizontal per baris, palet konsisten dan
  terbaca grayscale, terbaca di A4, ada judul + legenda.
- ERD (`DGM-07`) Crow's Foot, digambar ulang (bukan menambal ERD v2); tanpa notasi Chen/class diagram.
  Diagram sekuens tidak dipakai.
- Setiap perubahan entitas/alur di kode yang memengaruhi diagram dicatat di `progress.md` sebagai
  "diagram perlu disesuaikan".
