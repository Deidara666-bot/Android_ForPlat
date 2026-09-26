---
paths:
  - "experiments/**"
  - "scripts/experiments/**"
  - "scripts/adb/**"
---

# Aturan eksperimen, Tier-2, authoring, dan holdout

Dasar: `01_BREAKDOWN` §9.7, §11–§11.1, §15–§18; `02_ARSITEKTUR` §AG.11, §AG.13, §AL.

## Yang di-commit vs tidak

- Commit: protokol, definisi skenario, `ground_truth.json`, skrip uji, hasil tersanitasi (CSV/JSON
  ringkasan), matriks kandidat sampel (tanpa biner), `freeze_manifest.json`.
- ⛔ Jangan commit: `raw_outputs/`, `logs/private/`, dump SMS/kontak asli, APK, pcap, dump DB, token.

## Tier-2 (ketersediaan artefak)

- Tiga pengulangan **independen** per artefak inti, dengan keadaan AVD/perangkat di-reset tiap ulangan.
  3/3 = konsisten; 1–2/3 = `CONDITIONAL`; 0/3 = dipilah `unavailable`/`denied`/`unsupported`/`failed`.
- Dicatat **per lingkungan** (AVD API 36 Google APIs, AVD kedua, Galaxy A10) — tidak diciutkan.
- Rekaman minimum per percobaan: `artifact_id`, versi Android/API/build, device/emulator, perintah/API,
  `privilege_state`, aksi uji, bukti yang diharapkan, hasil aktual, `availability_status`, path keluaran
  mentah, semantik waktu, catatan, `git_commit`, versi `adb`.
- Artefak cadangan dievaluasi, tidak otomatis menggantikan inti (G2-C3 ≠ G2-C1, G3-D2 ≠ G3-D1).

## Authoring vs holdout

- Authoring: minimum 20 kasus (4 per keluarga), termasuk ≥2 fixture konflik dan ≥2 fixture eksklusioner
  lintas keluarga, dan D1 untuk setiap peran opsional yang dipakai. Boleh dipakai men-debug parser/aturan.
- Holdout: target 8 bundel, tiap bundel membawa vektor keluaran untuk kelima keluarga. Kriteria & vektor
  disegel **sebelum** freeze.
- Urutan mengikat: segel kriteria holdout → authoring → **freeze** (parser, skema, aturan, KB, konfigurasi,
  kode) → bangun & akuisisi holdout → baseline manual dicatat & **disegel** → analisis otomatis →
  uji konsistensi (3× per bundel) → pelaporan.
- ⛔ Claude tidak membuka/menjalankan analisis otomatis holdout sebelum user mengonfirmasi baseline manual
  sudah disegel. ⛔ Holdout tidak pernah dipakai untuk tuning.

## Pencatatan hasil

Setiap hasil menyimpan: `git_commit`, `git_tag`, `family_id`, `profile_id`, `rule_version`,
`parser_version`, `android_build`, `platform_tools_version`, `scenario_id`.
⛔ Jangan menimpa hasil lama — versi baru = berkas/folder baru.

## Evaluasi & pelaporan

- Istilah: **kesesuaian keluaran terhadap hasil yang diharapkan**. ⛔ Tidak ada precision, recall, F1,
  akurasi deteksi, atau satu angka agregat lintas kelas.
- Laporkan per kasus dan per kelas skenario (A/B/C/D1/D2/E/F); D1 dan D2 terpisah; holdout terpisah dari
  authoring. Persentase hanya dengan penyebut eksplisit, sebagai statistik deskriptif.
- Konsistensi dibandingkan secara **semantik** (kondisi, alasan UNKNOWN, fakta penopang, versi & keluaran
  aturan, ada/tidaknya temuan & isi hipotesis, relasi keterlacakan), bukan ID/timestamp.
- Hasil yang tidak sesuai dilaporkan apa adanya.
