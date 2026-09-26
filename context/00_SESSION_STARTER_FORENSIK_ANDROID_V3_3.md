# SESSION STARTER — SKRIPSI FORENSIK ANDROID
## Consolidated Canonical v3.3 — `FROZEN`

> Tujuan file: bootstrap sesi AI baru tanpa mengulang diskusi konseptual dari nol.  
> Paket canonical yang dipakai bersama file ini:
> - `01_BREAKDOWN_PROYEK_FORENSIK_ANDROID_V3_3.md`
> - `02_ARSITEKTUR_SETUP_FORENSIK_ANDROID_V3_3.md`

---

# CATATAN PERUBAHAN v3.2 → v3.3 *(5 September 2026)* — 🔒 `FROZEN`

> **Amandemen substantif untuk BAB III Draft v3.** Judul, rumusan masalah, tujuan, batasan, serta BAB I–II tidak diubah. Versi ini mengunci cara menerjemahkan tiga kelompok sumber menjadi lima dimensi investigatif, portofolio lima keluarga Aturan Pola Korelasi Forensik (APKF), tiga kategori sampel, dan simulator bukti aman.

| Perubahan |
|---|
| Posisi penelitian ditegaskan sebagai **korelasi deterministik pascaakuisisi atas fakta Android ternormalisasi untuk mendukung rekonstruksi aplikasi APK penipuan**, bukan pendeteksi atau pengklasifikasi malware |
| B1–B6 pada rancangan lama diganti dalam kontrak aktif BAB III oleh **lima dimensi investigatif**; kode B lama hanya boleh muncul sebagai riwayat |
| Struktur G1–G3 dipertahankan tetapi keanggotaannya diperluas dan dipisahkan menjadi artefak inti, artefak penguat, serta *fallback* yang tidak dianggap ekuivalen otomatis |
| APKF ditetapkan sebagai **Aturan Pola Korelasi Forensik** dan diperluas menjadi lima keluarga berbasis profil bukti; kondisi alternatif dibatasi pada bukti yang setara secara semantik |
| Setiap aturan membawa `claim_level`; konflik fakta menghasilkan `UNKNOWN/conflicting_evidence`; rujukan dapat ditautkan ke elemen aturan dan peran interpretasinya |
| Bahan pengujian dibagi menjadi **simulator bukti aman**, **aplikasi pihak ketiga benign/kontrol**, dan **APK malware nyata untuk analisis statis saja** |
| Spesifikasi pengembangan simulator aman, *ground truth*, varian *authoring/holdout/benign-control*, serta pembekuan versi dan *hash* dikunci |
| BAB III tidak memakai lampiran formal; hanya tabel inti di badan bab, sedangkan artefak rinci disimpan dalam repositori penelitian berversi |
| Paket visual Draft v3 dikunci menjadi **10 diagram**, seluruhnya mempunyai sumber `.drawio` yang dapat diedit dan keluaran PNG resolusi tinggi |
| Target BAB III ditetapkan **31–35 halaman** dengan sekitar tujuh tabel inti dan tanpa diagram sekuens yang redundan |
| **Generate 1.5:** katalog awal APKF dikunci menjadi **16 profil**—K01=3, K02=4, K03=3, K04=3, K05=3—dengan lima blok YAML lengkap berstatus `design_baseline` pada `01_BREAKDOWN` §14.2 |
| Kontrak implementasi diperjelas: `predicate_value` menopang TRUE/FALSE eksplisit; aplikabilitas memakai dua sumbu `evidence_mode` dan `run_purpose`; profil tidak berlaku dicatat `skipped_not_applicable`; fixture eksklusioner tetap khusus validasi |

---

# CATATAN PERUBAHAN v3.1 → v3.2 *(4 September 2026)* — 🔒 `FROZEN`

> **Rekonsiliasi pascadraf BAB III.** Tidak mengubah judul, RQ, tujuan, batasan, struktur G1/G2/G3, atau metode validasi. Versi ini membersihkan identitas paket, menyelaraskan status aktif, dan menutup kontradiksi kontrak yang ditemukan saat membandingkan core dengan `BAB_03_WORKING_v1_0.md` dan `BAB_03_DRAFT_v1.docx`.

| Perubahan |
|---|
| Identitas dan seluruh rujukan aktif paket diperbarui ke **v3.2**; rantai versi dirapikan menjadi `v2.9 → v2.9.1 → v3.0 → v3.1 → v3.2` |
| Dokumen institusi asli **dihapus dari daftar referensi paket** atas keputusan peneliti |
| Status BAB III diperbarui dari “siap ditulis” menjadi **draf lengkap sedang diaudit dan direvisi** |
| `R-01` dan `R-02` ditegaskan tertutup; `R-03`, `R-04`, dan `R-05` berstatus **`NOT REQUIRED`** |
| Istilah aktif **dataset** diganti menjadi **repositori malware** atau **himpunan sampel purposif**; MalwareBazaar utama dan VX-Underground cadangan |
| `K-04` diselaraskan: *increment* 1–4 berada pada tahap d, *increment* 5 pada tahap e |
| Kontrak aturan dipertegas: setiap aturan mempunyai `reference_ids`; setiap eksekusi menghasilkan `RuleEvaluation`; hanya `matched` menghasilkan `CorrelationFinding` dan `InvestigationHypothesis` |
| Daftar OPEN disusutkan menjadi data pelaksanaan dan keputusan teknis yang memang belum tersedia |

---

# CATATAN PERUBAHAN v3.0 → v3.1 *(3 September 2026)*

> **Amandemen sah atas core beku** — pemicunya keputusan baru dari peneliti, bukan temuan audit.

| Perubahan |
|---|
| **`G-05` diamandemen** — perangkat pembanding menjadi **Samsung Galaxy A10** (2019, One UI, plafon Android 11 / API 30). Prasyarat `minSdk 28` aman pada versi mana pun; karakteristik **penyetelan ulang izin otomatis** Android 11 dicatat sebagai konsekuensi metodologis |
| Rumusan risiko OEM: MIUI → **One UI** |
| **`R-04` `NOT REQUIRED`** — klaim penghindaran emulator tidak dipakai; Shang dkk. (2025) hanya menopang pencatatan terpisah antar-lingkungan |
| **`R-05` `NOT REQUIRED`** — UML dan ERD artefak rancangan, cukup berlegenda jelas |
| **`R-01` DITUTUP** — Cockburn (2008) ●●● untuk definisi, Larman & Basili (2003) ●●● untuk legitimasi historis, SWEBOK v4.0 (2024) penopang kemutakhiran. SEBoK dicabut |
| Istilah ***holdout* dipertahankan** dengan definisi operasional di BAB III 3.6 |

⚠️ **Terbuka:** versi Android aktual perangkat pembanding, yang menentukan API AVD kedua.

---

# CATATAN PERUBAHAN v2.9.1 → v3.0 *(3 September 2026)* — 🔒 `FROZEN`

> **Seluruh keputusan BAB III 3.1–3.6 dikunci.** Kenaikan mayor, bukan errata.

| Sub-bab | Keputusan yang dikunci |
|---|---|
| **3.1** | Core `§AJ.0`–`§AJ.1` mencukupi; rujukan `§A` diganti **`§AF`**. Sisa: `R-01` |
| **3.2** | Tahap **a–f**; **tahap d = *increment* 1–4, tahap e = *increment* 5** — `D-1` tidak dibuka; Tier-2 formatif vs konfirmatif dibedakan; tabel *increment* tingkat tujuan + kolom tahap; **diagram dua jalur**; tanpa jadwal/milestone |
| **3.3** | **MalwareBazaar** utama, **VX-Underground** cadangan; **dua sampel purposif** `S1`/`S2`; istilah **repositori**, bukan dataset; **T2 — dipasang, tidak diluncurkan**; kendali jaringan per jenis sampel; **`G-05`** perangkat pembanding satu unit; **AVD kedua mengikuti versi perangkat**; laptop Lenovo IdeaPad Flex 5i; struktur 3.3.1–3.3.3 |
| **3.4** | Kebutuhan **fungsional dan non-fungsional** diturunkan dari **B1–B6**, bukan elisitasi pengguna; dua teknik pengumpulan; **`R-03` `NOT REQUIRED`**; Tier-1 pada halaman lanskap tanpa rubrik berskor; **protokol Tier-2** (`01_BREAKDOWN` §11.1); dua tabel seleksi sampel |
| **3.5** | Lima unit; **6 gambar, 5 tabel, 1 kutipan kode**; UML + ERD **tanpa DFD**; satu aktor Pemeriksa; ERD satu gambar dua zona; **`RuleEvaluation` · `RuleConditionResult` · `RuleConditionFact`**, `FindingEvidence` dicabut; hipotesis **imutabel per `CorrelationRun`** |
| **3.6** | **16 jalanan *authoring* + 6 *holdout*** disegel sebelum pembekuan; **uji konsistensi** (§18.3a); baseline manual **tanpa waktu**, disegel sebelum keluaran otomatis; **kriteria kelulusan per kelas**; rumusan **"kinerja" nonwaktu** |

**Perubahan struktural inti:** `02_ARSITEKTUR` **§AA.1** (jalur pencatatan evaluasi aturan, 27 entitas), **§Z.1**, **§Y.3.5a** (protokol sampel nyata), **§Y.3.6**; `01_BREAKDOWN` **§11.1**, **§14.0**, **§15.0**, **§18.1a**, **§18.3a**.

⛔ **Aturan pasca-pembekuan.** Temuan *holdout* yang tidak sesuai adalah **hasil untuk BAB IV**, bukan alasan mengubah aturan sampai semuanya lulus. Tanpa aturan ini, pembekuan hanyalah jeda sebelum putaran berikutnya.

⛔ **Kriteria berhenti mengaudit.** Core dibuka kembali hanya bila bertentangan dengan dirinya sendiri, atau ada keputusan baru dari peneliti/pembimbing. Core yang belum memuat rancangan final **bukan cacat**.

---

# CATATAN PERUBAHAN v2.9 → v2.9.1 *(2 September 2026)*

> **Errata kesiapan penulisan.** Ditemukan lewat tinjauan core **per sub-bab BAB III** — bukan audit menyeluruh, bukan keputusan penelitian baru.

| Perbaikan | Letak |
|---|---|
| Tumpang tindih tahap d/e/f pada pemetaan `K-04` ditutup | `02_ARSITEKTUR` §AJ.2 |
| Identitas citra emulator dikunci: **Google APIs**; kata "AOSP" dicabut | §O · §Y.3.5 |
| Perlakuan sampel dataset dikunci: **dipasang, tidak dieksekusi**; kendali jaringan ditetapkan | §Y.3.5 |
| **`G-05`** — perangkat fisik **satu unit**; sejak v3.1 **Samsung Galaxy A10** (2019, One UI) | §Y.3.5 |
| **Pemetaan `availability_status` → `evidence_state` → TRUE/FALSE/UNKNOWN** | §Y.3.6 *(baru)* |
| `expects_epistemic_class` diwajibkan; pemetaan nama fakta dan `source_group` | `01_BREAKDOWN` §14.0 |
| Definisi pembeda status ketersediaan; `CORE_FALLBACK` masuk enum; padanan dikunci | `01_BREAKDOWN` §8 · §4.7.3 |
| Cakupan validasi tingkat hipotesis ditetapkan | `01_BREAKDOWN` §15 |
| **`R-02` ditutup tanpa sumber baru** — ISTQB (2023) sudah ●●● dan terbit di naskah BAB II 2.1.14 | — |

⛔ **Kriteria berhenti mengaudit — baru v2.9.1.** Core dibuka kembali **hanya** bila core bertentangan dengan dirinya sendiri, atau ada keputusan baru dari Marco/pembimbing. **Core yang belum memuat rancangan final bukan cacat** — rancangan itu ditulis di dalam naskah BAB III, lalu dicatat balik ke sini sekali di akhir. Lima ronde audit tanpa satu halaman naskah membuktikan perlunya kriteria ini.

---

# CATATAN PERUBAHAN v2.8 → v2.9 *(2 September 2026)*

> **Stabilisasi final — tidak ada keputusan penelitian atau teknis baru.** Struktur, gaya penulisan, pembagian segmen, RQ, cakupan, G1/G2/G3, semantik aturan, arsitektur, dan rancangan validasi dipertahankan. Paket v2.9 berstatus **`FROZEN`**.

| Bagian | Perbaikan |
|---|---|
| §0 | Urutan otoritas disamakan dengan `BAB_03_WORKING` §1; rujukan versi diperbarui; catatan “butir 2” diperbaiki menjadi **butir 3** |
| §11–§12 | Status “dapat mulai ditulis” dipisahkan dari rincian yang perlu difinalkan saat menulis |
| §12 | Sengketa `B3-09` ditutup: `capability_state` → **“kapabilitas”**; fungsi aturan dikembalikan sebagai pemisah masukan–keluaran |
| §12 | Enam tahap a–f `K-04` dicatat tertutup tanpa mengubah lima *increment* `D-1` |
| §13–§14 | Instruksi beku dan rujukan paket v2.9 diterapkan |

**Garis beku:** core hanya dibuka kembali bila ada perubahan pada RQ/tujuan/batasan, cakupan insiden, baseline akuisisi, struktur G1/G2/G3, semantik aturan, metode validasi, kelayakan total satu kelompok, atau arahan pembimbing/institusi. Housekeeping dan pekerjaan penulisan tidak membuat versi kanonik baru.

---

# CATATAN PERUBAHAN v2.7 → v2.8 *(2 September 2026)*

> **Tidak ada keputusan penelitian baru.** v2.8 memperbaiki tempat-tempat yang **meringkas** keputusan tetapi tidak ikut diperbarui ketika keputusannya berubah.

| Bagian | Perbaikan |
|---|---|
| §6 | Catatan "§11 tetap membolehkan penggantian" dicabut — dikoreksi `01_BREAKDOWN` §4.1.2 sejak v2.6: kelompok tidak diganti diam-diam, `D-5` dibuka kembali secara eksplisit |
| §11 | Status sampel/lingkungan diperbarui; `CONCERN-D8` diturunkan menjadi bersyarat mengikuti `D-8 DEFER` |
| §12 | **Tiga butir berada di CLOSED dan OPEN sekaligus** — sampel, lingkungan, padanan `epistemic_class`. Diarsipkan dari OPEN |
| §12 | `B3-09` vs padanan `capability_state` dicatat sebagai **sengketa terbuka**, bukan diselesaikan diam-diam |

⚠️ **Akar penyebab yang ditangani v2.8.** Tiga ronde berturut-turut gagal dengan pola identik — keputusan ditambal di **tempat ia dinyatakan**, tidak di **tempat ia diringkas**. v2.8 disusun lewat penyisiran per kode keputusan (`D-n`, `G-n`, `R-n`, `M-n`) di keempat dokumen, bukan lewat daftar temuan.

---

# 0. URUTAN OTORITAS

Jika ada konflik informasi, gunakan urutan berikut:

1. **Keputusan langsung Marco dalam sesi berjalan** *(baru v2.6)*
2. Judul yang sudah diterima institusi
3. **Naskah bab yang sudah `DRAFT FINAL`** — `BAB_01_DRAFT_FINAL_2`, `BAB_02_DRAFT_FINAL`
4. `01_BREAKDOWN_PROYEK_FORENSIK_ANDROID_V3_3`
5. `02_ARSITEKTUR_SETUP_FORENSIK_ANDROID_V3_3`
6. `00_SESSION_STARTER_FORENSIK_ANDROID_V3_3`
7. `BAB_03_WORKING_v1_3.md` · `BAB_01_WORKING_v1.5.md` · `BAB_02_WORKING_v0.8.md`
8. Naskah bab senior — preseden format, bukan otoritas isi
9. Asumsi/ide AI

> ⚠️ **Daftar ini wajib identik dengan `BAB_03_WORKING` §1.** Pada v2.5 keduanya berbeda — satu 6 butir, satu 10 butir — sehingga dua urutan otoritas beredar bersamaan. Kelas kesalahan yang sama dengan insiden dua versi RQ.

AI tidak boleh mengubah keputusan yang sudah fixed hanya karena asumsi sendiri.

> ⭐ **Butir 3 baru pada v2.4.** Sebelumnya naskah bab tidak muncul dalam urutan otoritas sama sekali, padahal BAB I dan BAB II sudah `DRAFT FINAL`. Akibatnya sempat beredar **dua versi RQ** — satu di naskah BAB I, satu di `01_BREAKDOWN` §17 — dan yang stale justru berperingkat lebih tinggi.
>
> **Alasan naskah menang atas dokumen kanonik:** apa yang sudah tertulis di naskah adalah yang akan dibaca pembimbing dan penguji. Dokumen kanonik boleh lebih maju secara pemikiran, tetapi tidak boleh memerintahkan naskah yang sudah jadi tanpa melewati protokol perubahan.
>
> **Batasnya:** butir 3 hanya berlaku untuk bab berstatus `DRAFT FINAL`. Bab yang masih `WORKING` **tidak** ikut naik peringkat.
>
> **Konsekuensi langsung:** rumusan masalah, tujuan, batasan masalah, dan seluruh padanan istilah Indonesia yang sudah terbit (lihat `01_BREAKDOWN` §4.7) mengikuti naskah, bukan dokumen ini.

---

# 1. STATUS PROYEK

## 1.1 Judul — FIXED

**Pengembangan Platform Investigasi Forensik Android Berbasis Web Menggunakan Rule-Based Evidence Correlation untuk Mendukung Analisis Digital Forensik**

Judul sudah diterima. Jangan menawarkan judul baru kecuali diminta pembimbing/institusi.

## 1.2 Konsep sistem — FIXED

```text
Android Device
  ↓ USB
Local Agent
  ↓ Authorized ADB Acquisition
Backend
  ↓
Parsing / Normalization
  ↓
Rule-Based Evidence Correlation
  ↓
Behavior Finding / Investigation Hypothesis
  ↓
Web Dashboard / Report
```

Prinsip:

**Agent = execution/acquisition layer. Backend = analysis/research layer.**

Agent tidak melakukan malware reasoning.

## 1.3 Acquisition boundary — FIXED

Baseline:

**Authorized non-root ADB / software-logical acquisition pada controlled investigation environment.**

Tidak mengklaim:
- physical extraction;
- lockscreen bypass;
- exploit-based acquisition;
- chip-off/JTAG;
- sistem melakukan rooting terhadap evidence device;
- seluruh data Android selalu dapat diperoleh.

---

# 2. INCIDENT SCOPE — FIXED

**Incident Family: Aplikasi APK Penipuan pada Android**

Penelitian tidak dikunci ke:
- satu malware family;
- satu Banking Trojan;
- satu attack chain;
- satu aplikasi sosial tertentu.

Representative behavior boleh mencakup SMS-related capability, Accessibility-related capability, credential-oriented behavior, dropper behavior, atau external communication selama masih berada dalam incident family APK fraud.

---

# 3. MENTAL MODEL UTAMA

```text
INCIDENT
Apa kasusnya?
  ↓
FORENSIC QUESTION / HIGH-LEVEL BEHAVIOR
Apa yang ingin direkonstruksi?
  ↓
EVIDENCE / ARTIFACT
Apa yang dapat mendukung/menyangkalnya?
  ↓
EVIDENCE SOURCE GROUP
Dari domain sumber apa evidence berasal?
  ↓
FEASIBILITY
Bisakah evidence diperoleh secara reproducible?
  ↓
NORMALIZED EVENT
Bagaimana fact direpresentasikan konsisten?
  ↓
RULE-BASED CORRELATION
Bagaimana beberapa fact dikombinasikan?
  ↓
FINDING / HYPOTHESIS
Apa yang didukung evidence dan apa yang tetap unknown?
```

Jangan menyamakan:
- behavior;
- Evidence Source Group;
- artifact;
- raw source;
- normalized event;
- rule;
- hypothesis.

---

# 4. LIMA DIMENSI INVESTIGATIF — FIXED v3.3

Kelima dimensi berikut adalah subpertanyaan operasional untuk menata sumber bukti dan rekonstruksi. Dimensi ini **bukan** kondisi aturan, kelas malware, atau klaim bahwa perbuatan penipuan telah terjadi.

1. **Identitas dan keadaan instalasi** — aplikasi/package apa yang ditemukan, bagaimana identitas, versi, penandatangan, UID, dan konteks pemasangannya?
2. **Kapabilitas sensitif dan akses khusus** — izin, komponen, *overlay*, layanan aksesibilitas, atau akses khusus apa yang dideklarasikan, diberikan, atau diaktifkan?
3. **Eksekusi dan persistensi** — bukti apa yang mendukung bahwa package pernah aktif, digunakan, atau dipicu kembali oleh peristiwa sistem?
4. **Keberadaan data komunikasi sensitif dalam konteks perangkat** — SMS/MMS, kontak, catatan panggilan, atau konteks notifikasi apa yang tersedia dalam jendela pemeriksaan, tanpa otomatis mengatribusikan aksesnya kepada aplikasi?
5. **Aktivitas jaringan terkait package/UID** — aktivitas jaringan apa yang dapat ditautkan ke UID/package dan waktu relevan, tanpa otomatis menyebutnya eksfiltrasi?

Dimensi 1–3 terutama ditopang G1, dimensi 4 oleh G2, dan dimensi 5 oleh G3. Rekonstruksi kejadian dibangun dari beberapa temuan terverifikasi yang berbagi subjek, waktu, dan konteks; **bukan** dari satu artefak atau satu kondisi `required`.

> `[ARSIP v3.2]` Kode B0–B8 tidak lagi dipakai sebagai struktur aktif BAB III. Makna yang masih relevan telah diserap ke lima dimensi di atas; kode lama boleh dipertahankan hanya di riwayat versi atau catatan migrasi.

---

# 5. PRINSIP EPISTEMIK — WAJIB

```text
READ_SMS granted
≠ aplikasi terbukti membaca SMS

SMS OTP ada di device
≠ aplikasi terbukti membaca OTP

UID memiliki network traffic
≠ data terbukti dieksfiltrasi

Accessibility Service enabled
≠ Accessibility terbukti disalahgunakan

URL/domain ditemukan dalam APK
≠ URL/domain terbukti dihubungi saat incident

installer metadata
≠ exact social-engineering delivery channel
```

Current state tidak boleh diubah menjadi historical event tanpa timestamp evidence.

Missing evidence = `UNKNOWN/UNAVAILABLE`, bukan otomatis `FALSE`.

> ⭐ **Sejak v2.5 prinsip ini tertanam pada skema, bukan hanya diingat.** Tiap fakta ternormalisasi wajib membawa **label epistemik** — `capability_state` · `execution_observed` · `data_present` · `identity_attribute` — sehingga mesin aturan tidak dapat memperlakukan kapabilitas sebagai eksekusi. Lihat `01_BREAKDOWN` §4.4a.

---

# 6. EVIDENCE SOURCE STATUS SAAT INI

🔒 **Jumlah dan identitas kelompok tetap tiga.** Pengelompokan berbasis kanal sumber; label epistemik tetap melekat pada setiap fakta ternormalisasi. v3.3 memperluas isi kelompok tanpa membuat G baru.

Keanggotaan awal di bawah adalah portofolio Tier-1. Status empiris tiap artefak tetap ditentukan melalui Tier-2; kegagalan satu artefak tidak menggugurkan seluruh kelompok.

> `[KOREKSI v2.8]` ~~§11 tetap membolehkan **penggantian** bila satu kelompok gagal empiris~~ — perumusan itu berasal dari v2.5 dan sudah **dikoreksi pada v2.6**. Yang berlaku: bila satu kelompok **sepenuhnya** tidak layak, `D-5` **dibuka kembali secara eksplisit** sebagai keputusan baru — bukan diganti diam-diam. Lihat `01_BREAKDOWN` §4.1.2.

## G1 — Keadaan Aplikasi dan Sistem
Peran: identitas/instalasi, kapabilitas/akses khusus, eksekusi/persistensi, dan pengayaan statis APK.

- **inti:** daftar package, UID, versi, jalur APK, installer bila tersedia, izin diberikan, layanan/komponen aktif, *usage/activity* dan indikator pemicu sistem yang dapat diperoleh;
- **penguat:** informasi certificate/signature, komponen manifest, special-access state, dan konteks waktu;
- **pengayaan statis:** manifest, permission, receiver/service/provider, certificate, strings, URL/domain tertanam, serta konfigurasi APK;
- pengayaan statis hanya membuktikan identitas atau kapabilitas yang dideklarasikan, bukan tindakan runtime.

## G2 — Data Komunikasi Sensitif
Peran: keberadaan data komunikasi sensitif dan konteks waktunya.

- **inti:** SMS/MMS yang dapat diakuisisi secara sah dan terkendali;
- **penguat:** kontak dan catatan panggilan bila tersedia;
- **kondisional:** konteks notifikasi bila dapat diperoleh secara konsisten;
- pada pengujian digunakan data sintetis; keberadaan data tidak membuktikan aplikasi mengaksesnya.

## G3 — Aktivitas Jaringan
Peran: aktivitas jaringan yang dapat diatribusikan ke UID/package dan jendela waktu.

- **inti:** statistik jaringan per UID/package yang tersedia pada lingkungan uji;
- **penguat:** keadaan konektivitas dan konteks jaringan pada waktu pemeriksaan;
- **validasi simulator:** rekaman menuju *endpoint* lokal terkendali;
- *fallback* berbasis capture atau log lain hanya dipakai setelah kesetaraan maknanya dibuktikan; tidak dianggap pengganti otomatis.

---

# 7. DASAR PEMILIHAN EVIDENCE — FIXED METHODOLOGY

Evidence/source tidak dipilih hanya karena daftar aspek institusi.

Gunakan:
1. Incident relevance
2. Probative value
3. Attributability / correlatability
4. Acquisition feasibility
5. Reproducibility
6. Complementarity
7. Institutional alignment

---

# 8. FEASIBILITY MODEL

## Tier 1 — Documented/Theoretical
Berdasarkan:
- Android/Google/AOSP documentation;
- academic literature;
- MITRE ATT&CK Mobile;
- credible threat research.

Hasil:
- `STRONG`
- `CONDITIONAL`
- `WEAK_BASELINE`

## Tier 2 — Empirical
Dilakukan pada emulator/dummy device dengan actual ADB acquisition.

Hasil:
- `acquired`
- `unavailable`
- `denied`
- `unsupported`
- `failed`

Status sekarang: Tier-1 working assessment sudah ada di `01_BREAKDOWN`; Tier-2 belum dilakukan.

---

# 9. RULE SEMANTICS

**APKF** berarti **Aturan Pola Korelasi Forensik**. APKF adalah aturan deterministik yang menguji pola fakta ternormalisasi; APKF bukan tanda tangan malware dan bukan penggolong aplikasi sebagai penipuan.

Condition state:

```text
TRUE
FALSE
UNKNOWN
```

Rule outcome:

```text
matched
not_matched
insufficient_evidence
```

Kontrak kondisi dalam satu profil:

```text
semua required TRUE
→ matched

minimal satu required FALSE
→ not_matched

tidak ada required FALSE,
tetapi minimal satu required UNKNOWN
→ insufficient_evidence
```

Satu keluarga APKF boleh memiliki beberapa **profil bukti** agar dapat bekerja pada variasi artefak yang benar-benar setara secara semantik. Agregasi profil wajib:

```text
minimal satu profil matched
→ keluarga matched

semua profil not_matched
→ keluarga not_matched

tidak ada profil matched,
dan minimal satu profil insufficient_evidence
→ keluarga insufficient_evidence
```

Kondisi alternatif `any_of` hanya boleh berisi fakta dengan makna klaim yang sama. Bukti komplementer, kontekstual, atau eksklusioner harus diberi peran terpisah; bukti yang bertentangan tidak dipilih sepihak dan menghasilkan `UNKNOWN` dengan alasan `conflicting_evidence`.

Lima keluarga yang dikunci:

1. **APKF-K01 — kapabilitas komunikasi sensitif**;
2. **APKF-K02 — kapabilitas antarmuka istimewa/akses khusus**;
3. **APKF-K03 — persistensi atau eksekusi terpicu peristiwa**;
4. **APKF-K04 — eksekusi package relevan teramati**;
5. **APKF-K05 — aktivitas jaringan terkait UID/package**.

Katalog awal aktif berisi **16 profil**: K01=3, K02=4, K03=3, K04=3, dan K05=3. Rincian fakta wajib, konteks, tingkat klaim, batas interpretasi, serta lima YAML lengkap berada di `01_BREAKDOWN` §14.1.3–§14.2; kontrak eksekusinya berada di `02_ARSITEKTUR` §Z.0. BAB III memakai ringkasan portofolio, bukan menyalin seluruh YAML.

Aplikabilitas profil memakai dua sumbu: `evidence_mode` (`installed_runtime` atau `apk_static`) dan `run_purpose` (`authoring`, `holdout`, `benign_control`, atau `production`). Profil yang tidak cocok pada salah satu sumbu dicatat `skipped_not_applicable` dengan `outcome: null` dan tidak ikut agregasi. Status ini bukan keadaan aturan keempat.

Setiap aturan/profil harus punya:

```yaml
reference_ids:
  - KB-SRC-...
claim_level: identity | capability | observed_activity | contextual_cooccurrence
unknown_handling:
  required_unknown: insufficient_evidence
  optional_unknown: annotate
```

`reference_ids` wajib tidak kosong dan seluruh ID harus dapat diresolusikan ke entri `KB_Source` sebelum aturan dibekukan. Rujukan dapat ditempelkan pada elemen aturan dengan `rule_element_key` dan `reference_role`: `artifact_semantics`, `behavior_relevance`, `interpretation_limit`, atau `technique_mapping`. Setiap relasi rujukan menyimpan ringkasan klaim, cakupan versi, dan status verifikasi.

`claim_level` membatasi bahasa keluaran. Fakta identitas tidak boleh menghasilkan klaim eksekusi; kapabilitas tidak boleh dinaikkan menjadi tindakan; aktivitas jaringan tidak boleh dinaikkan menjadi eksfiltrasi tanpa bukti tambahan.

Kondisi `FALSE` harus ditopang fakta negatif eksplisit (`predicate_value: false`) dari sumber yang diperoleh, berhasil diurai, dan mempunyai cakupan selector lengkap. Ketiadaan baris pada sumber yang tidak lengkap adalah `UNKNOWN`, bukan `FALSE`. Fixture `synthetic_exclusion_marker_observed` hanya boleh digunakan pada *authoring/holdout* terkendali; ia membatasi rekonstruksi tanpa membalik fakta wajib yang benar.

Siklus status YAML adalah `design_baseline` → `authoring_candidate` → `frozen_for_holdout`. `design_baseline` sudah lengkap untuk desain BAB III. Status final empiris baru ditetapkan setelah implementasi dan minimum 20 kasus *authoring*, sebelum delapan bundel *holdout* dibuka.

Setiap eksekusi aturan selalu menghasilkan evaluasi profil dan keluarga. Setiap profil `matched` dapat menghasilkan satu `CorrelationFinding` yang tetap menunjuk evaluasi profil serta keluarganya; profil `not_matched`, `insufficient_evidence`, dan `skipped_not_applicable` tidak menghasilkan temuan. Hipotesis rekonstruksi memerlukan sekurang-kurangnya dua temuan dari **keluarga berbeda** yang memiliki subjek dan jendela waktu kompatibel; beberapa profil dari keluarga yang sama tidak dihitung sebagai beberapa keluarga. Rekonstruksi kejadian juga harus memuat sekurang-kurangnya satu temuan berkelas aktivitas teramati. Jika gerbang ini tidak terpenuhi, sistem berhenti pada temuan tingkat rendah.

Antarmuka dan laporan membedakan tiga dasar: **basis bukti** (fakta dan artefak), **basis aturan** (kondisi/profil yang dievaluasi), dan **basis pengetahuan** (rujukan serta batas interpretasi).

> `[ARSIP v2.7]` ~~Gunakan istilah Evidence Support Score / Correlation Score / Rule Match Score~~ — **dicabut oleh `D-6`.** Sistem tidak menghasilkan skor dalam bentuk apa pun. Keluaran mekanisme aturan terbatas pada tiga keadaan: `matched` · `not_matched` · `insufficient_evidence`.

---

# 10. VALIDATION FRAMEWORK

Katalog validasi mencakup tujuh kelas cakupan:
1. positif / keluaran cocok;
2. *near-miss* / fakta wajib salah;
3. benign/kontrol;
4. bukti opsional tidak tersedia;
5. bukti wajib tidak diketahui;
6. bukti berkonflik; dan
7. fakta eksklusioner sintetis.

Ketujuh kelas tersebut bukan produk Kartesius yang harus diulang untuk setiap profil. Katalog *authoring* minimum berisi 20 kasus inti, sedangkan *holdout* menargetkan delapan bundel bukti dengan vektor keluaran untuk kelima keluarga.

Rule authoring/development set dan holdout evaluation set harus dipisah.

Low-level capability rule boleh match pada app benign jika fact capability memang benar. Malicious interpretation berada pada higher-level correlation/hypothesis.

Katalog aktif: minimum 20 kasus *authoring* (empat per keluarga) dengan fixture konflik dan eksklusioner di dalamnya, serta target delapan bundel *holdout* yang membawa vektor keluaran untuk kelima keluarga. Kelas skenario adalah cakupan, bukan produk Kartesius untuk setiap profil.

## 10.1 Tiga kategori sampel — FIXED v3.3

| Kategori | Peran | Perlakuan |
|---|---|---|
| **S-A Simulator bukti aman** | sumber *ground truth* untuk skenario positif, negatif, `UNKNOWN`, konflik, *authoring*, dan *holdout* | dibangun sendiri, dipasang, dan dijalankan pada lingkungan terkendali; hanya endpoint lokal dan data sintetis |
| **S-B Aplikasi pihak ketiga benign/kontrol** | menguji anti-klaim-berlebih ketika kapabilitas sah ditemukan pada aplikasi nonmalware | kandidat dari sumber APK publik diverifikasi lebih dahulu, lalu dipasang/dijalankan secara terisolasi bila lolos; tidak diberi label penipuan |
| **S-C APK malware nyata** | pemeriksaan relevansi statis dan keterwakilan pola artefak | MalwareBazaar utama, VX-Underground cadangan; **analisis statis saja, tidak dipasang dan tidak dijalankan** |

Seleksi S-C memakai model kandidat: minimum enam, target delapan kandidat, lalu tiga sampel akhir yang mewakili komunikasi sensitif, aksesibilitas/*overlay*, serta persistensi/jaringan. Catat SHA-256, sumber, keluarga yang dikorroborasi, pemetaan APKF, artefak statis, kompatibilitas, duplikasi, dan alasan pilih/tolak. `minSdk`, `targetSdk`, dan ABI adalah data kompatibilitas, bukan alasan relevansi perilaku.

## 10.2 Simulator bukti aman — kontrak minimum

Simulator terdiri atas aplikasi Android, pengendali skenario pada host, dan endpoint lokal. Ia hanya membentuk artefak forensik yang diketahui tanpa mencuri kredensial, membaca data nyata, berkomunikasi dengan pihak ketiga, menyamar sebagai merek, melakukan obfuscation/evasion, mengeksploitasi perangkat, memperoleh izin otomatis, atau menjalankan persistensi tersembunyi.

Kemampuan yang boleh diimplementasikan: identitas package/UID; permission transparan; layanan aksesibilitas *no-op*; *overlay* berlabel uji; receiver `BOOT_COMPLETED` yang hanya membuat notifikasi/log terlihat; aktivitas penggunaan terkendali; lalu lintas ke endpoint lokal; dan data SMS/kontak sintetis yang disiapkan pengendali.

Setiap skenario mempunyai `ground_truth.json` berisi ID skenario, versi dan hash APK, keadaan awal, aksi dan waktu, artefak yang diharapkan, fakta/predikat yang diharapkan, keluaran keluarga APKF, batas klaim, serta bukti yang sengaja dibuat tidak tersedia. Varian minimal: `authoring`, `holdout`, dan `benign-control`.

Urutan pengembangan: (1) kontrak skenario dan oracle; (2) scaffold serta varian build; (3) identitas, izin, dan akses khusus; (4) eksekusi/persistensi yang terlihat; (5) data sintetis dan jaringan lokal; (6) pengendali host; (7) kasus authoring/benign/holdout; (8) pembekuan Git, APK, konfigurasi, dan hash.

Evaluasi menyatakan **kesesuaian spesifikasi pada skenario terkendali**, bukan akurasi deteksi malware populasi. Ukur kesesuaian kondisi, keluaran profil/keluarga, keterlacakan, penanganan `UNKNOWN`, konsistensi ulang, dan ketiadaan klaim berlebih.

## 10.3 Paket visual BAB III Draft v3

Sepuluh diagram wajib: tahap penelitian–increment; derivasi kebutuhan; arsitektur terpadu; use case Pemeriksa; flowchart akuisisi–normalisasi; flowchart APKF–rekonstruksi; ERD Crow’s Foot; jalur keterlacakan; wireframe hasil; dan tata kelola sampel/pembekuan. Seluruhnya mempunyai sumber `.drawio` dan PNG resolusi tinggi. Spesifikasi rinci berada di `01_BREAKDOWN` §22A dan `02_ARSITEKTUR` §AO.

---

# 11. CURRENT PHASE

*(diperbarui v3.3 — 5 September 2026)*

**Selesai:** BAB I `DRAFT FINAL` · BAB II `DRAFT FINAL` · substansiasi literatur · RQ `FINAL` (*working-freeze*).

**Prioritas saat ini: menyelesaikan paket sepuluh diagram, lalu menyusun BAB III Draft v3 berdasarkan core v3.3 dan `BAB_03_WORKING_v1_3.md`.** Draft v2 menjadi bahan, bukan baseline struktur. Generate 1.5 telah mengunci YAML `design_baseline`; *authoring* empiris baru dilakukan setelah rancangan BAB III difiksasi. Fokus berikutnya:

- menjaga 3.1 ringkas dan memisahkan alasan pemilihan model dari penerapannya di 3.2;
- memuat tiga kategori sampel dan protokol seleksi kandidat pada 3.3;
- memuat lima dimensi, G1–G3 yang diperluas, matriks Tier-1 inti, dan kebutuhan sistem pada 3.4;
- menyajikan arsitektur, alur akuisisi/normalisasi, APKF, keterlacakan, ERD, dan antarmuka secara visual di 3.5;
- menyusun pengujian *authoring/holdout*, fixture eksklusioner, konflik, konsistensi, dan baseline manual di 3.6;
- membatasi naskah pada 31–35 halaman, sekitar tujuh tabel inti, dan sepuluh diagram; tidak memakai lampiran formal.

`R-01` dan `R-02` sudah tertutup. `R-03`, `R-04`, dan `R-05` berstatus `NOT REQUIRED`. `D-8` tetap `DEFER`; *ablation* tidak ditulis atau dijalankan kecuali dibuka kembali secara eksplisit.

⚠️ **Tier-2 berubah status.** Pada v2.3 Tier-2 dinyatakan *bukan blocker untuk mulai menulis* — itu benar untuk BAB I dan II. **Untuk BAB III tidak lagi sepenuhnya benar:** 3.4 memerlukan protokol Tier-2 yang final, dan 3.3 memerlukan keputusan lingkungan serta bahan.

Yang tetap berlaku: **hasil** Tier-2 bukan prasyarat menulis BAB III, dan memang **tidak boleh** masuk BAB III — hasil adalah materi BAB IV. Yang dibutuhkan BAB III hanyalah **rancangan** pengujiannya.

---

# 12. CLOSED / WORKING / OPEN

## CLOSED
- Judul
- Android forensic domain
- Incident family APK Penipuan Android
- Web + local agent + ADB
- Authorized non-root ADB baseline
- Backend Rule-Based Evidence Correlation
- Explainable/reference-traceable reasoning
- Raw evidence integrity/provenance
- Penelitian bukan “detect all Android malware”
- **Rumusan masalah RQ1–RQ3, Tujuan, dan Batasan Masalah** — final pada naskah BAB I, *working-freeze* *(baru v2.4)*
- **BAB I dan BAB II** — `DRAFT FINAL` *(baru v2.4)*
- **Padanan istilah Indonesia yang sudah terbit** — `01_BREAKDOWN` §4.7.1 *(baru v2.4)*
- **`D-1` Model pengembangan *Incremental*** — 5 *increment*, urutan terkunci · `02_ARSITEKTUR` §AJ.0 *(v2.4.1)*
- **`D-6` Scoring dicabut dari MVP** · `01_BREAKDOWN` §13.3 *(v2.4.1)*
- **`D-7` Metrik kesesuaian per kelas skenario** — metrik klasifikasi dicabut · `01_BREAKDOWN` §18.1 *(v2.4.1)*
- **`D-8` Ablation `DEFER`** — tidak ditulis di BAB III, dicatat di BAB V. Fungsinya digantikan matriks cakupan `M-6` · `01_BREAKDOWN` §18.5 *(v2.7)*
- **Cakupan G1–G3 pada validasi** — G1 diuji lintas lima keluarga, G2 menjadi konteks K01/rekonstruksi, dan G3 menjadi inti K05; rancangan tiga aturan lama hanya riwayat *(diperbarui v3.3)*
- **Sampel & lingkungan v3.3** — simulator aman sebagai sumber *ground truth* dinamis; aplikasi pihak ketiga benign/kontrol dapat dijalankan setelah verifikasi; APK malware nyata dari **MalwareBazaar** atau **VX-Underground** dianalisis **statis saja** dan tidak dipasang/dijalankan
- **`G-05` Perangkat fisik** — satu unit, **Samsung Galaxy A10** (2019, One UI, plafon Android 11/API 30), berikut empat konsekuensi yang wajib dinyatakan di 3.3 *(v3.0; diamandemen v3.1)*
- **Pemetaan status ketersediaan → tiga keadaan** · **padanan enum** · **`expects_epistemic_class` pada tiga aturan APKF** · **cakupan validasi tingkat hipotesis** *(v3.0)*
- **`R-02`** — ditutup tanpa sumber baru *(v3.0)*
- **`R-01`** — ditutup: Cockburn (2008) dan Larman & Basili (2003) berstatus ●●●; SWEBOK v4.0 (2024) sebagai penopang kemutakhiran; SEBoK dicabut *(v3.1)*
- **`R-03`** — `NOT REQUIRED`; teknik pengumpulan diterangkan melalui operasi dan protokol penelitian, bukan klaim taksonomi baru *(v3.0)*
- **`R-04` dan `R-05`** — `NOT REQUIRED` *(v3.1)*
- **Padanan `epistemic_class`** — atribut identitas · **kapabilitas** · eksekusi teramati · keberadaan data *(final v2.9)*
- **`G-02` "keterlacakan dua arah"** · **`G-03` "tanpa akses akar"** — tanpa koreksi mundur ke BAB I *(v2.4.1)*
- **`D-5` Pengelompokan hibrida** — kelompok berbasis kanal + label epistemik wajib pada fakta; dasar jumlah tiga dirumuskan; nama Indonesia G1/G2/G3 ditetapkan · `01_BREAKDOWN` §4.1, §4.4a *(v2.5)*
- **`K-04` Tahapan 3.2 a–f** — enam tahap penelitian/proyek didefinisikan; *increment* 1–4 berada pada tahap d dan *increment* 5 pada tahap e *(dikoreksi v3.0)*
- **`B3-09`** — fungsi aturan dipastikan sebagai pemisah label epistemik masukan dan keadaan aturan keluaran; bukan larangan leksikal *(v2.9)*
- **Lima dimensi investigatif** — menggantikan B1–B6 sebagai struktur aktif BAB III *(v3.3)*
- **Lima keluarga APKF dengan 16 profil `design_baseline`** — termasuk YAML lengkap, agregasi profil, dua sumbu aplikabilitas, `claim_level`, konflik fakta, fakta negatif eksplisit, dan rujukan tingkat elemen *(v3.3 Generate 1.5)*
- **Strategi tanpa lampiran formal** dan paket **10 diagram editable `.drawio`** untuk Draft v3 *(v3.3)*

## WORKING-STABLE
- keanggotaan artefak rinci sampai hasil Tier-2 tersedia;
- evidence-selection criteria;
- Tier-1 feasibility model;
- validation framework;
- implementasi rule semantics TRUE/FALSE/UNKNOWN.

## OPEN
> `[ARSIP v2.6]` ~~exact final 3 primary source groups~~ — **ditutup oleh `D-5`.** Struktur G1/G2/G3 terkunci; keanggotaan artefak tetap milik Tier-2. Lihat `01_BREAKDOWN` §4.1.2.

- status empiris dan artefak final berdasarkan hasil Tier-2;
- penyesuaian *as-built* profil setelah *authoring* dalam batas kontrak; katalog 16 profil dan YAML desain awal sudah lengkap;
- versi Android aktual Samsung Galaxy A10 dan API AVD kedua;
- identitas serta SHA-256 tiga APK malware nyata terpilih dari sedikitnya enam kandidat;
- nama package, varian, versi, serta SHA-256 simulator aman dan aplikasi benign/kontrol terpilih;
- mekanisme terkendali untuk membangkitkan status `denied` dan `unsupported` pada H4/H6 sebelum penyegelan;
- perangkat lunak virtualisasi desktop yang benar-benar dipakai;
- hasil Tier-2, hasil skenario, hasil manual baseline, dan hasil evaluasi;
- implementasi endpoint lokal, pengendali host, dan seluruh `ground_truth.json` simulator;
- bentuk deployment final dan bentuk distribusi agen lokal.

Analisis statis APK **sudah diputuskan sebagai pengaya G1 dan sarana pemeriksaan pola pada sampel nyata**, bukan bukti tindakan runtime. Penggantian kelompok hanya dapat dilakukan dengan membuka `D-5` secara eksplisit bila satu kelompok terbukti tidak layak total.

> ✅ **RESOLUSI v2.9 — `B3-09` dan `capability_state`.** Padanan final adalah **“kapabilitas”**. `B3-09` melarang pencampuran label epistemik pada fakta dengan keadaan evaluasi aturan sebagai satu konsep; aturan ini **tidak** melarang kata tertentu. Prosa 3.4 dan 3.5 tidak lagi terhalang sengketa istilah.
>
> `[ARSIP v2.8]` Pada v2.8, **“keadaan kapabilitas”** diperlakukan sebagai pelanggaran `B3-09` dan sengketa dibuka. Pembacaan itu dikoreksi pada v2.9 tanpa mengubah kode `capability_state`, skema data, atau semantik teknis.

> `[ARSIP v2.8]` ~~sampel/bahan APK penipuan~~ · ~~lingkungan pengujian hibrida~~ · ~~padanan Indonesia empat label epistemik~~ → **peran ketiganya ditutup pada v2.7**, tetapi butirnya tertinggal di OPEN sehingga sempat berada di CLOSED **dan** OPEN sekaligus. Sisa yang benar-benar terbuka dipecah menjadi butir tersendiri di atas.

> `[ARSIP v2.5]` ~~`D-1` · `D-5` · `D-6` · `D-7` · `D-8`~~ → **dipindah ke CLOSED**, diputuskan 1 September 2026.

> `[ARSIP v2.4]` ~~final RQ wording~~ → **dipindah ke CLOSED.** RQ berstatus `FINAL` pada naskah BAB I dan berada dalam *working-freeze*.

---

# 13. INSTRUKSI UNTUK AI SESI BARU

- Paket core v3.3 berstatus **`FROZEN`**. Jangan membuka audit konseptual baru tanpa pemicu pada catatan perubahan v3.3.
- Jangan membuka ulang judul tanpa alasan institusional.
- Jangan menganggap Banking Trojan sebagai scope final.
- G1/G2/G3 **final secara struktural**; portofolio Tier-1 v3.3 menjadi baseline dan status empiris setiap artefak tetap milik Tier-2.
- Jangan memilih source hanya karena disebut institusi.
- Jangan menambah source group hanya demi “lebih lengkap”.
- Jangan menganggap permission = behavior.
- Jangan menganggap network activity = exfiltration.
- Jangan menganggap Accessibility enabled = abuse.
- Jangan menganggap SMS ada = APK membacanya.
- Jangan membuat historical timestamp dari current-state evidence.
- Jangan gunakan holdout untuk tuning.
- Jangan menyebut APKF sebagai detektor malware atau menyimpulkan “aplikasi penipuan” dari satu aturan kapabilitas.
- Jangan menggabungkan fakta yang tidak setara secara semantik di dalam `any_of`.
- Jangan menjalankan, memasang, atau membuka APK malware nyata; kategori tersebut hanya dianalisis statis.
- Jangan menambahkan perilaku berbahaya ke simulator; seluruh data, UI, dan jaringan harus transparan, sintetis, dan lokal.
- Jangan memindahkan rincian ke lampiran formal; artefak teknis rinci ditempatkan di repositori penelitian berversi.
- Jika mengusulkan perubahan scope/source, tandai sebagai alternatif dan jelaskan tradeoff.
---

# 14. TECHNICAL DOCUMENT COMPLETENESS NOTE — V3.3

`02_ARSITEKTUR_SETUP_FORENSIK_ANDROID_V3_3` adalah **target technical blueprint yang lengkap**, bukan hanya vertical-slice scaffold. Dokumen tersebut mencakup:
- software yang harus/opsional diinstall;
- verified version baseline;
- bahasa/framework/library/package;
- Android Studio/AVD setup;
- Python/Node/PostgreSQL setup;
- dependency manifests;
- target repository tree;
- minimum day-1 scaffold;
- environment variables;
- Docker/database bootstrap;
- development milestones.
- kontrak lima keluarga APKF dan profil bukti;
- katalog 16 profil awal, lima YAML `design_baseline`, dua sumbu aplikabilitas, dan siklus pembekuan sebelum *holdout*;
- model rujukan tingkat elemen, batas klaim, dan konflik fakta;
- tiga kategori sampel serta simulator bukti aman;
- spesifikasi sepuluh diagram BAB III Draft v3.

Jangan menyimpulkan bahwa file yang belum dibuat pada milestone awal tidak diperlukan pada target architecture.
