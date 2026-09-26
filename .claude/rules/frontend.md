---
paths:
  - "frontend/**"
---

# Aturan frontend (`frontend/`)

Dasar: `02_ARSITEKTUR` §M, §S.3, §AC.

## Stack

React 19 + TypeScript (strict) + Vite + React Router; HTTP pakai `fetch` native. Opsional yang sudah
disetujui core: `date-fns`, `lucide-react`, `@tanstack/react-query`, `recharts`, `prettier`.
⛔ Tidak menambah design system/UI kit berat atau state manager lain tanpa persetujuan user.
Commit `package.json` **dan** `package-lock.json`; jangan hapus lockfile; tanpa versi `^`/`latest`
untuk dependency inti setelah freeze.

## Struktur

`src/api` (klien per resource), `src/types` (tipe yang mencerminkan schema backend), `src/pages`,
`src/components`, `src/hooks`, `src/utils`, `src/styles`. Nama komponen mengikuti daftar §AC
(`EvaluationTable`, `FamilyProfilePanel`, `ConditionResultTable`, `EvidenceTracePanel`,
`MissingEvidenceBadge`, `ConflictEvidenceBadge`, `ClaimLevelBadge`, `RuleReferencePanel`,
`ReconstructionTimeline`, dst.). Rute mengikuti §AC (`/cases/:id/evaluations`, `/findings`,
`/reconstruction`, `/report`, ...).

## Penyajian hasil (inti riset — jangan disederhanakan)

- Tampilkan **semua** keadaan: `matched`, `not_matched`, `insufficient_evidence`,
  `skipped_not_applicable` — yang tidak terpenuhi tetap bisa dibuka detailnya.
- `UNKNOWN` selalu tampil bersama alasannya dan `availability_status` aslinya
  (*diperoleh / tidak tersedia / ditolak / tidak didukung / gagal*).
- Konflik menampilkan semua fakta yang bertentangan.
- Panel keterlacakan membedakan tiga basis: **basis bukti** (fakta, artefak, bukti mentah, hash, status
  akuisisi), **basis aturan** (keluarga, profil, kondisi, peran, keadaan, `claim_level`), **basis
  pengetahuan** (sumber, elemen aturan, peran rujukan, klaim, cakupan versi, status verifikasi).
- Rekonstruksi hanya menampilkan urutan yang didukung + bukti yang belum teramati.
- ⛔ Tidak ada skor, gauge risiko, warna "merah = malware", label "berbahaya/penipuan/terdeteksi".
  Warna badge menyatakan keadaan evaluasi, bukan vonis.

## Teks UI

Bahasa Indonesia dengan padanan terkunci `01_BREAKDOWN` §4.7: *terpenuhi / tidak terpenuhi / bukti tidak
memadai* (keluaran aturan), *terpenuhi / tidak terpenuhi / tidak diketahui* (kondisi), *kapabilitas*,
*eksekusi teramati*, *keberadaan data*, *atribut identitas*, *pemeriksa* (bukan *investigator*).
Simpan label di satu modul (mis. `src/utils/labels.ts`) supaya konsisten.

## Pemeriksaan

`npm run lint` dan `npm run build` wajib lulus sebelum merge. Konfigurasi dari `VITE_API_BASE_URL` dan
`VITE_WS_BASE_URL`; tanpa URL hardcoded.
