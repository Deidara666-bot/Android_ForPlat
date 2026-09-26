# BREAKDOWN PROYEK SKRIPSI — CONSOLIDATED CANONICAL V3.3 — `FROZEN`
## Pengembangan Platform Investigasi Forensik Android Berbasis Web Menggunakan Rule-Based Evidence Correlation untuk Mendukung Analisis Digital Forensik

> Fungsi dokumen: single source of truth untuk framing penelitian, high-level behavior model, evidence terminology, evidence-selection methodology, feasibility matrix, source-group candidates, rule specification, validation design, evaluasi, novelty, dan status keputusan.
>
> ⛔ **RQ tidak lagi berada di dokumen ini** — lihat §17.

> Detail implementasi software berada di `02_ARSITEKTUR_SETUP_FORENSIK_ANDROID_V3_3`.

---

## CATATAN PERUBAHAN v3.2 → v3.3 *(5 September 2026)* — 🔒 `FROZEN`

> Amandemen ini mengunci desain BAB III Draft v3 tanpa mengubah BAB I, BAB II, judul, rumusan masalah, tujuan, atau batasan. Rancangan lama tiga aturan dan dua sampel disupersesi pada bagian aktif; riwayatnya tetap dipertahankan.

| Seksi | Perubahan |
|---|---|
| §12.1 · §14.1–§14.2 | **Generate 1.5:** registri sumber desain, katalog 16 profil awal, dan lima YAML keluarga APKF berstatus `design_baseline` ditambahkan sebelum produksi diagram |
| §13.2 · §14.0 | Kontrak selector/operator, efek fakta eksklusioner, dan batas perubahan saat *authoring* dikunci |
| §13.2.1 · §14.2 | Aplikabilitas profil dipisahkan menjadi dua sumbu: `evidence_mode` (`installed_runtime`/`apk_static`) dan `run_purpose` (`authoring`/`holdout`/`benign_control`/`production`) agar profil runtime tidak terlewat pada skenario validasi |
| §1 · §5 | Posisi penelitian dan lima dimensi investigatif dikunci; B0–B8 menjadi riwayat, bukan struktur aktif BAB III |
| §4 · §9–§10 | G1–G3 diperluas menjadi portofolio artefak inti/penguat/*fallback*; APK-statis diserap sebagai pengayaan G1 |
| §13–§14 | APKF ditetapkan sebagai **Aturan Pola Korelasi Forensik**; tiga aturan lama diganti lima keluarga berbasis profil bukti, dengan `claim_level`, konflik fakta, dan rujukan tingkat elemen |
| §11 · §15–§16 | Tiga kategori sampel, simulator bukti aman, seleksi kandidat APK malware statis, *ground truth*, *authoring*, *holdout*, fixture eksklusioner, dan konflik dikunci |
| §18 | Evaluasi dipusatkan pada kesesuaian spesifikasi, keterlacakan, `UNKNOWN`, konsistensi, dan anti-klaim-berlebih; bukan akurasi deteksi malware populasi |
| §22A | Strategi BAB III tanpa lampiran, sekitar tujuh tabel inti, target 31–35 halaman, dan spesifikasi sepuluh diagram ditambahkan |

---

## CATATAN PERUBAHAN v3.1 → v3.2 *(4 September 2026)* — 🔒 `FROZEN`

> **Rekonsiliasi pascadraf BAB III.** Tidak mengubah judul, RQ, tujuan, batasan, incident family, struktur G1/G2/G3, atau rancangan validasi. Perubahan membersihkan status aktif dan memperkeras kontrak yang sebelumnya tersirat atau saling bertentangan.

| Seksi | Perubahan |
|---|---|
| Kepala · §21–§22 | Identitas paket, rujukan silang, status pekerjaan, dan OPEN/CLOSED diselaraskan ke v3.2 |
| §4.7.3 | Padanan yang sudah dipakai pada draf BAB III dikunci: sumber/bukti mentah, pengurai, penormalisasi, mesin aturan, basis pengetahuan, agen lokal, dan sesi akuisisi |
| §9.4 · §9.7 | APK-static ditegaskan sebagai pengaya G1; garis dasar AOSP yang tersisa diganti menjadi emulator Google APIs; klaim isolasi OEM dibatasi |
| **§11.2** | Kontrak kebutuhan BAB III 3.4 ditambahkan: kebutuhan fungsional dan nonfungsional wajib diturunkan dari B1–B6 dan kontrol sistem |
| **§14.0 · §14** | `reference_ids` diwajibkan pada setiap aturan; semua ID harus terhubung ke `KB_Source`; contoh aturan dinaikkan ke versi 3 |
| §18.2–§18.3a | Keterlacakan dimulai dari `RuleEvaluation`; keberadaan/ketiadaan temuan dan hipotesis diperiksa untuk semua keluaran |
| §18.4 | Batas manual baseline ditetapkan atas paket bukti mentah yang sama; proses akuisisi dikeluarkan dari perbandingan |
| §18.5.2 | Instruksi *ablation* lama dijadikan arsip utuh; yang aktif hanya `D-8 DEFER` |

---

## CATATAN PERUBAHAN v3.0 → v3.1 *(3 September 2026)*

> **Amandemen sah atas core beku** — pemicunya keputusan baru dari peneliti, sesuai kriteria §16.

| Perubahan | Letak |
|---|---|
| **`G-05` diamandemen** — perangkat pembanding menjadi **Samsung Galaxy A10** (2019, One UI, plafon Android 11 / API 30) | §9.7 · `02_ARSITEKTUR` §Y.3.5 |
| Rumusan risiko OEM diganti dari MIUI ke **One UI** | §9.7 · §21 |
| **`R-04` ditutup `NOT REQUIRED`** — klaim empiris penghindaran emulator **tidak dipakai**. Keputusan tidak mengeksekusi sampel bersandar pada batas operasional, pengendalian risiko, ruang lingkup artefak yang dicari, dan aturan anti-klaim-berlebih. **Shang dkk. (2025) tetap dipakai, tetapi hanya untuk menopang pencatatan hasil secara terpisah antara emulator dan perangkat fisik** — sesuai isi sumbernya | §9.7 · BAB III 3.3 |
| **`R-05` ditutup `NOT REQUIRED`** — UML dan ERD adalah artefak rancangan, bukan klaim ilmiah yang wajib disitir. Syaratnya: simbol, kardinalitas, dan batas sistem memiliki legenda yang jelas | BAB III 3.5 |
| **Istilah *holdout* dipertahankan**, dengan definisi operasional pada kemunculan pertamanya di BAB III 3.6 | §15.0 · §16 · §18 |

---

## CATATAN PERUBAHAN v2.9.1 → v3.0 *(3 September 2026)* — 🔒 `FROZEN`

> **Kenaikan mayor, bukan errata.** Seluruh keputusan BAB III 3.1–3.6 ditetapkan lewat diskusi berurutan dan dikunci di sini. Perubahannya melampaui perbaikan rujukan: entitas basis data baru, protokol Tier-2, prosedur uji konsistensi, pemisahan *holdout*, dan cakupan validasi tingkat hipotesis.

| Seksi | Perubahan |
|---|---|
| §7 · §8 | Alur seleksi → **tetapkan tiga**; **definisi pembeda** lima status ketersediaan; **`CORE_FALLBACK`** masuk enum; padanan dikunci |
| §9.2a | "G1 sembilan artefak inti" → **sepuluh** |
| **§11.1** | ⭐ **Protokol Tier-2** — tiga pengulangan independen, cakupan `CORE_CANDIDATE`/`CORE_FALLBACK`, aturan pemberian status 3/3 · 1–2/3 · 0/3, pembeda sumber-terakses-kosong dari sumber-tak-terakses, `UNKNOWN` retensi sebagai keluaran sah, pencatatan per lingkungan, cadangan dievaluasi bukan otomatis |
| **§14.0** | ⭐ `expects_epistemic_class` diwajibkan; pemetaan nama kondisi ↔ `event_type` ↔ kelas epistemik; `source_group` ↔ G1/G2/G3 |
| §14 | Ketiga aturan APKF dilengkapi `expects_epistemic_class` |
| **§15.0** | ⭐ **16 jalanan uji *authoring*** (bukan 18 — `D1-b` hanya untuk APKF-001); **enam kasus *holdout* terpisah**, disegel sebelum pembekuan, bervektor keluaran untuk ketiga aturan |
| §15 | Cakupan validasi tingkat hipotesis: **keterlacakan dan ketaatan batas dukungan**, bukan ketepatan |
| §15.2 · §15.3 | Diterjemahkan |
| §16 | **Urutan pembekuan** ditetapkan; **baseline manual disegel sebelum keluaran otomatis dilihat**; ⛔ **aturan pasca-pembekuan** — temuan *holdout* yang tidak sesuai adalah hasil BAB IV, bukan alasan menyetel ulang sistem |
| **§18.1a** | ⭐ **Kriteria kelulusan** — kesesuaian keluaran per kelas, tanpa angka agregat, D1/D1-b/D2 terpisah |
| §18.2 | Jalur keterlacakan memakai `RuleEvaluation` → `RuleConditionResult` → `RuleConditionFact`; lima pemeriksaan |
| §18.3 | Anti-klaim-berlebih dipisahkan dari keterlacakan |
| **§18.3a** | ⭐ **Uji konsistensi** — tiga eksekusi atas bukti sama, perbandingan **semantik** enam butir, cakupan *holdout* |
| §18.4 | **Dimensi waktu dan konsistensi dicabut**; rumusan **"kinerja" nonwaktu** diwajibkan muncul di 3.6; sifatnya deskriptif |
| §18.5.1 | `M-6` mencakup 16 jalanan *authoring*; *holdout* terpisah |
| §21 · §22 | Status diselaraskan; core dibekukan |

⛔ **Kriteria berhenti mengaudit tetap berlaku.** Core dibuka kembali **hanya** bila ia bertentangan dengan dirinya sendiri, atau ada keputusan baru dari peneliti atau pembimbing. **Core yang belum memuat rancangan final bukan cacat** — rancangan itu ditulis di dalam naskah BAB III, lalu dicatat balik ke sini sekali di akhir.

---

## CATATAN PERUBAHAN v2.9 → v2.9.1 *(2 September 2026)*

> **Errata kesiapan penulisan.** Bukan keputusan penelitian baru, bukan audit menyeluruh. v2.9.1 menutup pertentangan internal yang ditemukan saat meninjau core **per sub-bab BAB III**, dan hanya itu.

| Seksi | Perbaikan |
|---|---|
| §7 | Alur seleksi *"Select ≤3"* → **tetapkan tiga** (`D-5`); jumlah bukan lagi hasil seleksi |
| §8 | **Definisi pembeda** lima status ketersediaan ditambahkan berikut urutan pemeriksaannya; **`CORE_FALLBACK` dimasukkan ke enum keputusan** — dipakai §9.2 dan §9.3 sejak v2.7 tanpa pernah terdaftar |
| §9.2a | "G1 sembilan artefak inti" → **sepuluh**, sejak `M-3` menaikkan G1-B1 |
| §4.7.3 | Padanan enum status ketersediaan **dikunci** — menutup kebutuhan yang §4.7.3 nyatakan sendiri sebagai prasyarat 3.4 |
| **§14.0** | ⭐ **Seksi baru.** `expects_epistemic_class` diwajibkan; pemetaan nama kondisi ↔ `event_type` ↔ kelas epistemik; pemetaan `source_group` ↔ G1/G2/G3 |
| §14 | Ketiga aturan APKF dilengkapi `expects_epistemic_class` — tanpa itu ketiganya **gagal dimuat** menurut `02_ARSITEKTUR` §Y.3.3 |
| §15 | **Cakupan validasi tingkat hipotesis ditetapkan** — dinilai keterlacakan dan ketaatan batas dukungan, bukan ketepatan |
| §15.2 · §15.3 | Diterjemahkan; §15.1 sudah Indonesia sejak v2.7 |
| §21 · §22 | `G-05` masuk; daftar OPEN dan fase berjalan disesuaikan |

⚠️ **Yang sengaja TIDAK dikerjakan.** Protokol Tier-2 operasional, ERD berikut kardinalitas, *use case*, pembagian *holdout*, dan prosedur baseline manual **tidak** ditambahkan ke dokumen kanonik. Bukan karena tidak perlu, melainkan karena semuanya adalah **isi BAB III 3.4, 3.5, dan 3.6**. Menuliskannya di sini lebih dulu berarti merancang dua kali, dan itulah yang memperpanjang lima ronde audit tanpa satu halaman naskah pun dihasilkan. Arahnya dibalik: **naskah dulu, dokumen kanonik menyusul mencatat hasilnya.**

---

## CATATAN PERUBAHAN v2.8 → v2.9 *(2 September 2026)*

### v2.9 — stabilisasi final

> **Tidak ada keputusan penelitian baru.** Struktur, gaya penulisan, pembagian segmen, RQ, cakupan, G1/G2/G3, skema fakta, spesifikasi aturan, dan rancangan validasi dipertahankan. Perubahan menutup kontradiksi tekstual serta dua keputusan lokal yang diperlukan untuk mulai menulis BAB III. Paket v2.9 berstatus **`FROZEN`**.

| Bagian | Perbaikan |
|---|---|
| Kepala · §21–§22 | Rujukan versi dan status fase penulisan diselaraskan dengan tiga dokumen lain |
| §4.4a · §4.7.3 | `capability_state` → **“kapabilitas”**; `B3-09` ditegaskan sebagai pemisah lapisan masukan–keluaran, bukan larangan leksikal |
| Kepala | Daftar pekerjaan terbuka dipisahkan dari penghalang untuk mulai menulis; `CONCERN-D8` lama tidak lagi dinyatakan wajib dibawa |
| §21 | Kandidat APK-statis dibatasi sebagai *enrichment*; penggantian kelompok mensyaratkan pembukaan `D-5` secara eksplisit |
| §22 | Kerangka seluruh 3.1–3.6 dapat mulai ditulis; rincian dataset, perangkat, dan sitasi difinalkan saat penulisan |

**Garis beku:** core hanya dibuka kembali bila ada perubahan pada RQ/tujuan/batasan, cakupan insiden, baseline akuisisi, struktur G1/G2/G3, semantik aturan, metode validasi, kelayakan total satu kelompok, atau arahan pembimbing/institusi. Housekeeping dan pekerjaan penulisan tidak membuat versi kanonik baru.

---

## CATATAN PERUBAHAN v2.3 → v2.8 *(2 September 2026)*

### v2.8 — sinkronisasi ringkasan

> **Tidak ada keputusan penelitian baru.** v2.8 memperbaiki tempat-tempat yang **meringkas** keputusan tetapi tidak ikut diperbarui ketika keputusannya berubah.

| Bagian | Perbaikan |
|---|---|
| §18.5 | **Dua heading bernomor `18.5.1`** — `M-6` dan `CONCERN-D8`. `CONCERN-D8` menjadi **§18.5.2**. Cacat sejenis dicatat sebagai kesalahan naskah senior *mat* pada `BAB_03_WORKING` §11.5 |
| §18.5.2 | Butir "Ketergantungan" ditandai arsip — ditulis saat `D-8` masih `DIKOMIT` |
| §4.7.3 | Dua baris duplikat (`data_present`, `identity_attribute`) dihapus; sengketa `B3-09` dicatat |
| §10 | Blockquote status v2.5 masih menyatakan §11 membolehkan "penggantian" — dikoreksi v2.6 |
| §21 | OPEN masih memuat "final three primary source groups" — ditutup `D-5` sejak v2.5; diarsipkan |
| §22 | "Tier-2 bukan blocker" — dikoreksi khusus BAB III mengikuti `00_SESSION_STARTER` §11 |
| Kepala | Tabel v2.4.1 dan "dua hal wajib dibawa" ditandai tersalip oleh keputusan v2.7 |

⚠️ **Akar penyebab yang ditangani v2.8.** Tiga ronde berturut-turut (v2.5, v2.6, v2.7) gagal dengan pola identik: keputusan ditambal di **tempat ia dinyatakan** — §11.7, §15.1, §18.5 — tidak di **tempat ia diringkas**: tabel keputusan, daftar OPEN/CLOSED, catatan sitasi, Pusat Kendali. v2.8 disusun lewat penyisiran per kode keputusan (`D-n`, `G-n`, `R-n`, `M-n`) di keempat dokumen, bukan lewat daftar temuan.

---

## CATATAN PERUBAHAN v2.3 → v2.7 *(2 September 2026)*

Revisi higiene menjelang penulisan BAB III. **Tidak ada keputusan penelitian baru yang diambil**; yang dilakukan adalah menutup kontradiksi, merekam istilah yang sudah terbit, dan menandai keputusan yang menggantung. Seluruh perubahan bersifat bedah — tidak ada bagian yang ditulis ulang.

| Patch | Bagian | Perubahan | Sifat |
|---|---|---|---|
| **P1** | §17 | Rumusan RQ dicabut, diganti penunjuk ke naskah BAB I. Versi lama diarsipkan dengan alasan penyimpangannya | Koreksi kontradiksi |
| **P2** | §4.7 *(baru)* | Glosarium padanan Indonesia: 17 istilah terkunci karena sudah terbit di naskah, 9 istilah terbuka, **3 inkonsistensi ditemukan** (G-01, G-02, G-03) | Perekaman + temuan |
| **P3** | §13.3 · §18.1 · §18.5 | Tiga keputusan menggantung ditandai `D-6`, `D-7`, `D-8`. **§18.1 adalah kontradiksi aktif terhadap K-07** | Penandaan |
| **P4** | Kepala dokumen | Versi + catatan perubahan | Kebersihan |

**v2.4.1** menutup enam dari keputusan itu. Rinciannya di bawah.

### v2.4.1 — enam keputusan ditutup

| Kode | Keputusan | Letak |
|---|---|---|
| `D-1` | Model pengembangan ***Incremental***; 5 *increment*; urutan terkunci oleh rantai pipeline riset | `02_ARSITEKTUR` §AJ.0–AJ.2 |
| `D-6` | ***Scoring* dicabut dari MVP.** Blok `scoring:` dihapus dari ketiga spesifikasi aturan §14 | §13.3 |
| `D-7` | **Metrik klasifikasi dicabut**, diganti kesesuaian per kelas skenario; D1 dan D2 dilaporkan terpisah. Ditambah **`SYARAT-D7`** atas catatan Marco | §18.1, §18.1.1 |
| `D-8` | ***Ablation* dikomit**, disertai **`CONCERN-D8`** yang wajib dikonfirmasi ke pembimbing | §18.5, §18.5.1 |
| `G-02` | BAB III–V memakai **"keterlacakan dua arah"**; BAB I tidak diedit | §4.7.2 |
| `G-03` | BAB III–V memakai **"tanpa akses akar"** (*non-root* dalam kurung pada kemunculan pertama) | §4.7.2 |

> ⛔ **`[TERSALIP v2.7]` — baris `D-8` pada tabel di atas adalah catatan sejarah v2.4.1, bukan status berlaku.** Status `D-8` sekarang **`DEFER`**: *ablation* **tidak ditulis di BAB III** dan tidak dijalankan; fungsinya digantikan matriks cakupan `M-6`. Lihat §18.5. *(penanda ditambahkan v2.8)*

### v2.5 — `D-5` ditutup

| Isi | Letak |
|---|---|
| **Dasar pengelompokan: hibrida** — kelompok berbasis kanal, dimensi epistemik jadi label wajib pada fakta | §4.1 |
| **Label epistemik** `capability_state` · `execution_observed` · `data_present` · `identity_attribute` — field wajib pada skema fakta ternormalisasi | §4.4a |
| **Dasar jumlah tiga** dirumuskan: himpunan minimum yang cukup menanggung B1–B6 | §4.1 |
| **Nama Indonesia G1/G2/G3** ditetapkan | §4.7.3 |
| **Status batas ≤3 dikoreksi** — bukan perintah institusi, melainkan batasan peneliti sendiri yang sudah terbit di BAB I | §4.1 |
| **Koreksi:** klaim bahwa pengelompokan epistemik memaksa empat kelompok **salah**; B3 dan B6 sejenis, tetap tiga | §4.1 |

### `[ARSIP v2.8]` Keputusan yang saat itu masih terbuka

*(diperbarui v2.8 — tiga baris pertama tertutup sebagian pada v2.7 dan dipecah menurut sisa yang benar-benar terbuka)*

| Isi | Diperlukan untuk finalisasi |
|---|---|
| **Nama dataset sampel** — *peran* sampel sudah dikunci di `02_ARSITEKTUR` §Y.3.5; yang belum ada nama datasetnya | BAB III 3.3, 3.4 |
| **Merek/tipe/versi Android dua perangkat fisik** — `02_ARSITEKTUR` §Y.3.5 menyatakannya indikatif, dikunci saat menulis 3.3 | BAB III 3.3 |
| **`R-01` naik ●●●** — kandidat pengganti Zein (SEBoK/buku teks) wajib dibaca sendiri | sitasi final BAB III 3.1 |
| **`R-02` · `R-03`** — sumber pengujian fungsional berbasis skenario; sumber teknik pengumpulan data | BAB III 3.6, 3.4 |
| Derajat dukungan tanpa skor — dirancang lewat syarat aturan | penulisan aturan |

> `[ARSIP v2.9]` ~~Sampel/bahan APK penipuan~~ · ~~Lingkungan pengujian hibrida~~ · ~~Padanan Indonesia empat label epistemik~~ — **perannya ditutup pada v2.7** (`02_ARSITEKTUR` §Y.3.5; §4.7.3). ~~Sengketa `B3-09` vs `capability_state`~~ ditutup pada v2.9 melalui padanan **“kapabilitas”**. Sisa yang benar-benar terbuka berada pada baris tersendiri di atas.

### `[ARSIP v2.8]` Dua hal yang saat itu wajib dibawa ke sesi berikutnya

1. **Rincian bahan dan perangkat** — nama dataset serta merek/tipe/versi Android perangkat fisik untuk memfinalkan 3.3 dan paragraf sampel 3.4.
2. **`R-01`–`R-03`** — verifikasi sumber difinalkan sambil menulis. `[TERSALIP v2.7]` ~~Zein dkk. (2023) wajib dibaca~~ — Zein dibuang; penggantinya SEBoK/buku teks yang benar-benar dibaca. `CONCERN-D8` bersifat **bersyarat**, hanya bila pembimbing mengangkat *ablation*.

---

# 0. KONTEKS AKADEMIK

## 0.1 Judul — FIXED

**Pengembangan Platform Investigasi Forensik Android Berbasis Web Menggunakan Rule-Based Evidence Correlation untuk Mendukung Analisis Digital Forensik**

## 0.2 Konteks institusi

Problem area institusi: **Aplikasi APK penipuan pada Android**.

Institusi menyebut aspek yang dapat diperdalam:
- cara kerja aplikasi;
- permission;
- SMS/contact access;
- network endpoint;
- artefak instalasi/eksekusi.

Institusi juga memberi batas/saran:
- satu platform;
- satu jenis insiden;
- maksimal tiga sumber artefak utama;
- satu metode pembanding.

**Interpretasi metodologis:** daftar aspek tersebut adalah arah/alignment constraint. Pemilihan evidence tetap harus memiliki justifikasi ilmiah dan teknis independen.

## 0.3 Batas penelitian

- dikerjakan solo;
- baseline authorized non-root ADB;
- emulator/dummy device untuk controlled testing;
- eksekusi malware asli bukan requirement inti;
- root/exploit/physical extraction bukan baseline.

---

# 1. PROBLEM FRAMING

## 1.1 Incident family — FIXED

**Aplikasi APK Penipuan pada Android**

Tidak dikunci ke satu malware family atau satu attack chain.

## 1.2 Fokus penelitian

Penelitian berfokus pada post-acquisition analysis:

> Bagaimana artefak Android yang heterogen dan memiliki tingkat keteramatan berbeda dapat diakuisisi secara terkendali, diubah menjadi fakta ternormalisasi, lalu dikorelasikan secara deterministik dan tertelusur untuk mendukung rekonstruksi aplikasi APK penipuan?

Lingkup bidangnya adalah **forensik digital Android pascaakuisisi**. Objek kasusnya adalah **aplikasi APK penipuan**, sedangkan kontribusi penelitiannya adalah model fakta, aturan korelasi, penanganan bukti tidak teramati, keterlacakan bukti–aturan–rujukan, dan pembentukan hipotesis investigasi. Platform bukan mesin vonis, pendeteksi, atau pengklasifikasi malware.

Output utama:
- normalized evidence;
- behavior finding;
- investigation hypothesis;
- matched rule;
- supporting evidence;
- reference provenance;
- source provenance;
- missing/unknown evidence.

---

# 2. ENGINEERING LAYER VS RESEARCH LAYER

## Engineering layer
- web dashboard;
- backend;
- local agent;
- ADB acquisition;
- database;
- evidence storage;
- WebSocket/REST;
- hashing;
- audit.

## Research layer
- evidence semantics;
- parsing;
- normalization;
- knowledge base;
- deterministic rules;
- evidence correlation;
- behavior reconstruction;
- explainability;
- missing-evidence handling.

Prinsip:

**Agent = execution/acquisition layer. Backend = analysis/research layer.**

---

# 3. RESEARCH PIPELINE

```text
Android Device
  ↓
Authorized ADB Acquisition
  ↓
Raw Evidence + Acquisition Metadata + SHA-256
  ↓
Parser
  ↓
Artifact / Fact
  ↓
Normalizer
  ↓
Normalized Event
  ↓
APKF Evaluation
  ↓
Correlation Finding
  ↓
Cross-Finding Reconstruction
  ↓
Investigation Hypothesis
  ↓
Dashboard / Report
```

---

# 4. TERMINOLOGY

## 4.1 Evidence Source Group — 🔒 `D-5` *(diputuskan 1 Sep 2026)*
Operational grouping atas evidence yang berasal dari domain sumber Android yang koheren dan mekanisme acquisition yang berkaitan.

Evidence Source Group:
- bukan artifact tunggal;
- bukan behavior;
- bukan hasil ML clustering;
- tidak wajib sama dengan satu parser.

### Dasar pengelompokan — hibrida

**Kelompok sumber bukti disusun berbasis kanal** (domain sumber Android dan mekanisme akuisisi). **Dimensi epistemik tidak membentuk kelompok**, melainkan dibawa sebagai **label wajib pada tiap fakta ternormalisasi** (§4.4a).

| Lapis | Dasar | Wujud |
|---|---|---|
| Struktural | kanal akuisisi | G1 · G2 · G3 |
| Epistemik | jenis klaim yang ditopang | label pada tiap fakta |

**Alasan memilih hibrida di atas pengelompokan epistemik murni:**

1. **Biaya migrasi.** Matriks kelayakan §9 disusun menurut mekanisme akuisisi; rencana Tier-2 §11 menguji per artefak per kanal; spesifikasi aturan §14 merujuk sumber per kanal. Definisi §4.1 sendiri berbasis kanal. Pindah ke epistemik murni menuntut ketiganya diturunkan ulang.
2. **Isolasi kegagalan.** Di bawah pengelompokan epistemik, kelompok "aktivitas teramati" akan memuat *UsageStats* **dan** `netstats` — dua profil kelayakan yang jauh berbeda. Bila Tier-2 meloloskan satu dan menggugurkan yang lain, kelompok itu separuh mati dan pelaporannya kacau. Di bawah kanal, kegagalan terisolasi pada satu kelompok.

> `[KOREKSI v2.5]` Pada pembahasan awal dinyatakan bahwa pengelompokan epistemik **memaksa menjadi empat kelompok**. **Pernyataan itu salah.** B3 (eksekusi aplikasi) dan B6 (aktivitas jaringan) menopang jenis klaim yang sama — sesuatu teramati terjadi — sehingga jatuh ke satu kelompok, dan hasilnya tetap tiga. Pengelompokan epistemik murni **sah secara struktural**; ia ditolak karena dua alasan di atas, bukan karena melanggar plafon.

### Dasar jumlah tiga — 🔒 wajib masuk BAB III 3.4

> **Status batas ≤3.** Bukan perintah institusi, melainkan **batasan yang ditetapkan peneliti sendiri** dan sudah tercetak pada naskah BAB I Batasan #3 berstatus `DRAFT FINAL`. Karena sudah terbit, batas itu mengikat; karena ditetapkan sendiri, ia **wajib dipertanggungjawabkan**, tidak cukup disebutkan.

Lima dimensi investigatif aktif berada pada §5: identitas/instalasi; kapabilitas/akses khusus; eksekusi/persistensi; konteks data komunikasi sensitif; dan aktivitas jaringan terkait package/UID.

| Jumlah | Akibat |
|---|---|
| 2 kelompok | Dimensi komunikasi sensitif atau aktivitas jaringan kehilangan kanal sumber utamanya |
| **3 kelompok** | **Kelima dimensi tertanggung:** G1 menopang dimensi 1–3, G2 menopang dimensi 4, dan G3 menopang dimensi 5 |
| 4 kelompok | APK-statis bertumpang tindih dengan G1 dan lebih tepat dipakai sebagai pengayaan identitas/kapabilitas, bukan kanal utama baru |

**Tiga bukan angka pilihan, melainkan himpunan minimum yang cukup.**

### Batas kekunciannya *(baru v2.6)*

> `[KOREKSI v2.6]` Pada v2.5, `D-5` dinyatakan final sementara §11 tetap membolehkan kelompok yang gagal Tier-2 **diganti**. Itu kontradiktif: mengganti G2 dengan APK-statis berarti mengubah struktur G1/G2/G3 itu sendiri.

| Lapis | Status |
|---|---|
| **Struktur G1/G2/G3** | 🔒 **Terkunci** sebagai garis dasar struktural |
| **Keanggotaan artefak** | Ditentukan Tier-2. Artefak yang gagal dicatat statusnya, tidak menggugurkan kelompok |
| **Satu kelompok sepenuhnya tidak layak** | ⚠️ **`D-5` dibuka kembali secara eksplisit** — bukan diganti diam-diam. Dicatat sebagai keputusan baru berikut dampaknya terhadap 3.4 dan 3.5 |

### Penguatan vs kelengkapan

Rancangan ini memilih **kelengkapan** — tiap kelompok menjawab pertanyaan berbeda. Penilaian *Complementarity* tinggi pada §10 dan penandaan *"potential overlap G1"* sebagai kelemahan kandidat APK-statis menegaskan pilihan itu.

**Penguatan tetap diwujudkan, tetapi di lapisan aturan**, melalui aturan yang mensyaratkan kondisi dari lebih dari satu kelompok sekaligus — bukan melalui skema pengelompokan.

Perbedaan antara temuan satu sumber dan lintas sumber ditampilkan melalui fakta penopang serta jalur keterlacakan, bukan skor. Profil aturan menyatakan peran bukti sebagai wajib, opsional, kontekstual, atau eksklusioner.

## 4.2 Raw Source
Output/objek akuisisi asli, misalnya:
- `dumpsys package`;
- `UsageStats`;
- SMS Content Provider;
- `dumpsys netstats`;
- APK file.

## 4.3 Artifact / Fact
Unit informasi hasil parsing, misalnya:
- package name;
- UID;
- `READ_SMS` granted;
- SMS record;
- UID txBytes.

## 4.4 Normalized Event
Representasi fact secara konsisten, misalnya:
- `package_observed_installed`;
- `permission_observed_granted`;
- `sms_record_observed`;
- `uid_network_activity_observed`.

## 4.4a Label Epistemik — 🔒 `D-5` *(baru v2.5)*

Setiap fakta ternormalisasi **wajib** membawa satu label epistemik yang menyatakan **jenis klaim yang ditopangnya**.

| Label | Menyatakan | Contoh fakta |
|---|---|---|
| `capability_state` | keadaan/kemampuan yang dimiliki, **bukan** perbuatan | `permission_observed_granted` · `accessibility_service_observed_enabled` |
| `execution_observed` | sesuatu teramati **pernah berjalan/terjadi** | `app_usage_observed` · `uid_network_activity_observed` |
| `data_present` | keberadaan data pada perangkat, **bukan** akses terhadapnya | `sms_record_observed` · `contact_record_observed` |
| `identity_attribute` | atribut identitas teknis | `package_observed_installed` · `uid_observed` |

**Mengapa wajib.** `00_SESSION_STARTER` §5 berstatus **WAJIB** dan menyatakan `READ_SMS granted` ≠ terbukti membaca SMS, serta *current state* tidak boleh diubah menjadi *historical event*. Sebelum v2.5 prinsip itu berupa daftar larangan yang harus diingat penulis aturan. Dengan label, prinsip tersebut **tertanam pada skema data** dan dibaca mesin aturan — disiplin berhenti bergantung pada kehati-hatian manusia.

**Yang ditutupnya.** G1 memuat identitas, kapabilitas, dan eksekusi sekaligus. Label memisahkan jenis klaim tersebut pada tingkat fakta—tempat aturan sebenarnya membaca—bukan pada tingkat kelompok yang hanya dibaca manusia.

> **Setengah sudah berlaku.** Konvensi penamaan §4.4 telah menyandang jenis klaim di dalam predikatnya (`..._observed_...`). v2.5 menaikkannya dari konvensi penamaan menjadi **field wajib pada skema**.

### ⛔ Label epistemik BUKAN keadaan aturan

| | Melekat pada | Isi | Nilai |
|---|---|---|---|
| **Label epistemik** | **fakta** — masukan | jenis klaim yang ditopang | `capability_state` · `execution_observed` · `data_present` · `identity_attribute` |
| **Keadaan aturan** | **aturan** — keluaran | hasil evaluasi | `matched` · `not_matched` · `insufficient_evidence` |

Kontrak keluaran tiga keadaan pada naskah BAB II 2.1.13 **tidak berubah**. Label epistemik tidak menambah keadaan keempat. Keduanya **tidak boleh dicampur sebagai satu konsep**; keduanya boleh disebut dalam kalimat yang sama bila hubungan masukan–keluarannya dinyatakan eksplisit.

🔒 Padanan Indonesia keempat label **ditetapkan final** — lihat §4.7.3.

## 4.5 Behavior Finding
Kesimpulan tingkat behavior/capability/activity yang didukung satu atau lebih facts.

## 4.6 Investigation Hypothesis
Inferensi investigatif yang menyertakan evidence pendukung, rule, provenance, reference, serta evidence yang masih missing/unknown.

---

## 4.7 PADANAN BAHASA INDONESIA — WAJIB *(baru v2.4)*

> **Fungsi.** Dokumen kanonik ini berbahasa teknis Inggris; naskah skripsi wajib berbahasa Indonesia akademik. Tanpa padanan yang dibakukan, BAB III akan memakai istilah yang berbeda dari BAB I–II, dan inkonsistensi lintas bab adalah cacat yang paling mudah ditemukan penguji.
>
> **Aturan pakai.** Baris `🔒 TERBIT` sudah muncul di **naskah final BAB I atau BAB II**. Istilah tersebut **tidak boleh diganti** di BAB III–V; naskah yang sudah terbit menang atas preferensi baru. Istilah yang pertama kali dipilih pada draf BAB III dikunci di §4.7.3 sebagai `🔒 v3.2` dan harus digunakan konsisten pada revisi berikutnya.

### 4.7.1 Terkunci — sudah terbit di naskah

| Istilah kerja (Inggris) | Padanan naskah | Terbit di |
|---|---|---|
| Evidence Source Group | **kelompok sumber bukti** | BAB I Batasan #3; BAB II 2.3 |
| artifact | **artefak** | BAB II 2.1.6 |
| fact | **fakta** | BAB II 2.3 |
| normalized fact | **fakta ternormalisasi** | BAB II 2.2; 2.3 |
| behavior finding | **temuan perilaku** | BAB I Tujuan 2; BAB II 2.3 |
| investigation hypothesis | **hipotesis investigasi** | BAB I Batasan #4; BAB II 2.3 |
| provenance | **asal-usul** | BAB I Tujuan 1; BAB II 2.3 |
| observability status | **status keteramatan** | BAB I Tujuan 1; BAB II 2.3 |
| missing / unobserved evidence | **bukti yang tidak teramati** | BAB I Tujuan 3; BAB II 2.1.13 |
| deterministic rule | **aturan deterministik** | BAB II 2.3 |
| declarative rule | **aturan deklaratif** | BAB II 2.3 |
| logical acquisition | **akuisisi logis** | BAB II 2.1.5 |
| reference (dasar aturan) | **rujukan** | BAB I Tujuan 2; BAB II 2.1.12 |
| `TRUE` / `FALSE` / `UNKNOWN` | **terpenuhi · tidak terpenuhi · tidak diketahui** | BAB II 2.1.13 |
| `matched` / `not_matched` / `insufficient_evidence` | **terpenuhi · tidak terpenuhi · bukti tidak memadai** | BAB II 2.1.13 |
| examiner (pelaksana analisis teknis) | **pemeriksa** | K-22, BAB II |
| investigator (fungsi formal penyidikan) | **penyidik** | K-22, BAB II |

⛔ **Istilah *investigator* tidak dipakai dalam naskah Indonesia** (K-22).

### 4.7.2 ⚠️ Tiga inkonsistensi yang ditemukan saat penyusunan glosarium

Ketiganya nyata dan sudah berada di dalam naskah. Harus diputuskan sebelum BAB III ditulis, karena BAB III akan memakai ketiga istilah ini berkali-kali.

| # | Persoalan | Keadaan |
|---|---|---|
| **G-01** | **`Normalized Event` vs "fakta ternormalisasi"** — §4.4 dokumen ini menyebut satuannya *event*; naskah BAB II yang terbit menyebutnya **fakta ternormalisasi**, bukan "peristiwa ternormalisasi". Penyebutan "peristiwa" di BAB III akan memperkenalkan istilah yang tidak pernah didefinisikan di BAB II | ⚠️ **Ikuti naskah: "fakta ternormalisasi".** §4.4 dokumen ini dipertahankan sebagai nama teknis internal (skema, kode, basis data), bukan istilah naskah |
| **G-02** | **"keterlacakan ganda" vs "penelusuran dua arah"** — BAB I Tujuan 2 (naskah final) memakai **"keterlacakan ganda"**; keputusan **K-19** di BAB II mencabutnya dan menetapkan **"penelusuran dua arah"**; prosa BAB II 2.1.12 memakai **"keterlacakan … dalam dua arah"**. Tiga varian di dua bab | 🔒 **DIPUTUSKAN 1 Sep 2026 — BAB III–V memakai "keterlacakan dua arah".** Bentuk ini memuat "keterlacakan" (BAB I Tujuan 2) sekaligus "dua arah" (K-19 dan prosa BAB II 2.1.12), sehingga sejalan dengan keduanya. **BAB I tidak diedit**; bila kelak dibuka untuk alasan lain, Tujuan 2 disesuaikan saat itu. Membuka bab final demi satu frasa yang maknanya sudah diuraikan di kalimatnya sendiri tidak sepadan dengan risikonya |
| **G-03** | **"non-*root*" vs "tanpa akses akar"** — BAB I memakai bentuk asing dimiringkan (*akuisisi non-root*); BAB II 2.1.5 memakai padanan Indonesia (*akuisisi logis tanpa akses akar*) | 🔒 **DIPUTUSKAN 1 Sep 2026 — BAB III–V memakai "tanpa akses akar"**, dengan **"*non-root*"** dalam kurung pada kemunculan pertama tiap bab. Sejalan dengan disiplin nol istilah Inggris tanpa dimiringkan, dan mengikuti bab yang lebih baru. **Tanpa koreksi mundur ke BAB I** |

### 4.7.3 Terkunci dari draf BAB III — 🔒 v3.2

| Istilah kerja | Padanan final | Catatan |
|---|---|---|
| raw source | **sumber mentah** | Objek/keluaran asli yang dibaca operasi akuisisi |
| raw evidence | **bukti mentah** | Berkas hasil akuisisi yang disimpan imutabel |
| parser | **pengurai** | Nama lapisan/modul arsitektur di 3.5 |
| normalizer | **penormalisasi** | Prosesnya disebut **penormalisasian** |
| rule engine / inference engine | **mesin aturan** | Implementasi mesin inferensi berbasis aturan pada BAB II 2.1.10 |
| knowledge base | **basis pengetahuan** | Konsisten dengan BAB II 2.1.11 |
| local agent | **agen lokal** | |
| acquisition session | **sesi akuisisi** | |
| `acquired` · `unavailable` · `denied` · `unsupported` · `failed` | **diperoleh · tidak tersedia · ditolak · tidak didukung · gagal** | 🔒 `TERKUNCI v3.0` — definisi pembeda di §8, pemetaan ke tiga keadaan di `02_ARSITEKTUR` §Y.3.6 |
| `identity_attribute` | **atribut identitas** | 🔒 `TERKUNCI v2.7` |
| `capability_state` | **kapabilitas** | 🔒 `TERKUNCI FINAL v2.9` — menyatakan kemampuan/keadaan yang dimiliki, bukan penggunaan atau eksekusi |
| `execution_observed` | **eksekusi teramati** | 🔒 `TERKUNCI v2.7` — "teramati" konsisten dengan "status keteramatan" yang terbit di BAB I |
| `data_present` | **keberadaan data** | 🔒 `TERKUNCI v2.7` — menegaskan *ada*, bukan *diakses* |

> `[ARSIP v2.8]` ~~dua baris usulan lama untuk `data_present` dan `identity_attribute`~~ — duplikat baris terkunci di atasnya; dihapus.

> ✅ **RESOLUSI FINAL v2.9 — `capability_state`.** Padanan yang dipakai adalah **“kapabilitas”**. Ketidakparalelan bentuknya disengaja: label ini tidak menyatakan sesuatu teramati dilakukan, melainkan kemampuan/keadaan yang tersedia. Kode `capability_state`, skema data, dan semantik teknis **tidak berubah**.
>
> `B3-09` tetap berlaku untuk mencegah **pencampuran lapisan**: label epistemik menerangkan jenis klaim pada fakta sebagai masukan; keadaan aturan menerangkan hasil evaluasi sebagai keluaran. Aturan itu bukan larangan leksikal terhadap kata *keadaan*.
>
> `[ARSIP v2.8]` Padanan **“keadaan kapabilitas”** sempat diperlakukan sebagai pelanggaran `B3-09` dan prosa 3.4/3.5 diblokir. Pembacaan itu dikoreksi melalui resolusi di atas.

**G1 · G2 · G3 — ditetapkan v2.5, diperluas v3.3**

| Kode | Nama Indonesia | Peran |
|---|---|---|
| **G1** | **Keadaan Aplikasi dan Sistem** | identitas/instalasi · kapabilitas/akses khusus · eksekusi/persistensi · pengayaan statis APK |
| **G2** | **Data Komunikasi Sensitif** | SMS/MMS · kontak/catatan panggilan · konteks notifikasi kondisional |
| **G3** | **Aktivitas Jaringan** | statistik UID/package · konteks konektivitas · validasi endpoint lokal terkendali |

---

# 5. LIMA DIMENSI INVESTIGATIF — 🔒 v3.3

Lima dimensi berikut adalah subpertanyaan operasional yang menghubungkan lingkup kasus, kelompok sumber bukti, fakta ternormalisasi, dan APKF. Dimensi bukan kondisi aturan dan bukan label kelas aplikasi.

## Dimensi 1 — Identitas dan keadaan instalasi

Pertanyaan: aplikasi/package apa yang ditemukan, bagaimana identitas teknis, versi, penandatangan, UID, jalur APK, dan konteks pemasangannya?

## Dimensi 2 — Kapabilitas sensitif dan akses khusus

Pertanyaan: izin, komponen, *overlay*, layanan aksesibilitas, *notification listener*, atau akses khusus apa yang dideklarasikan, diberikan, atau aktif?

## Dimensi 3 — Eksekusi dan persistensi

Pertanyaan: bukti apa yang mendukung bahwa package pernah aktif, digunakan, berjalan, atau dipicu kembali oleh peristiwa sistem?

## Dimensi 4 — Keberadaan data komunikasi sensitif dalam konteks perangkat

Pertanyaan: SMS/MMS, kontak, catatan panggilan, atau konteks notifikasi apa yang tersedia dalam jendela pemeriksaan? Keberadaan data tidak mengatribusikan akses kepada aplikasi.

## Dimensi 5 — Aktivitas jaringan terkait package/UID

Pertanyaan: aktivitas jaringan apa yang dapat ditautkan ke UID/package dan jendela waktu? Aktivitas tidak otomatis membuktikan endpoint tertentu, payload, atau eksfiltrasi.

### Pemetaan dimensi ke kelompok dan tingkat klaim

| Dimensi | Kelompok utama | Tingkat klaim maksimum tanpa bukti tambahan |
|---|---|---|
| 1 | G1 | identitas/keadaan instalasi |
| 2 | G1 | kapabilitas |
| 3 | G1 | aktivitas atau eksekusi teramati |
| 4 | G2 | keberadaan data/konteks |
| 5 | G3 | aktivitas jaringan teramati |

Rekonstruksi dibuat dengan menggabungkan `CorrelationFinding` yang kompatibel menurut package/UID, jendela waktu, dan konteks. Kondisi `required` hanya menentukan keluaran profil aturan tingkat rendah; ia **bukan** satu-satunya bahan rekonstruksi dan tidak sendirian menghasilkan klaim penipuan.

> `[ARSIP v3.2]` Model B0–B8 diserap ke lima dimensi ini. Asal pengiriman, endpoint pasti/eksfiltrasi, dan dampak finansial tetap konteks kondisional di luar klaim dasar platform.

---

# 6. EVIDENCE SEMANTICS / ANTI-OVERCLAIM

```text
permission granted
≠ access occurred

SMS/contact exists
≠ package accessed it

network activity
≠ endpoint contacted
≠ exfiltration

Accessibility enabled
≠ Accessibility abuse

endpoint/string embedded in APK
≠ endpoint contacted during incident

current state
≠ historical event
```

Jika historical timestamp tidak tersedia:
- `event_time = null`;
- gunakan `observed_at`;
- jangan mengarang waktu kejadian.

Missing evidence:
- `UNKNOWN/UNAVAILABLE`;
- bukan otomatis `FALSE`.

---

# 7. EVIDENCE-SELECTION METHODOLOGY

Pemilihan evidence tidak dilakukan hanya berdasarkan daftar aspek institusi.

Kriteria:

## 7.1 Incident relevance
Apakah evidence membantu menjawab forensic question yang relevan terhadap APK fraud berdasarkan literature/threat research?

## 7.2 Probative value
Apa yang secara spesifik dapat dibuktikan/disangkal?

## 7.3 Attributability / correlatability
Apakah dapat dikaitkan lewat:
- package;
- UID;
- time window;
- object/context?

## 7.4 Acquisition feasibility
Apakah accessible melalui authorized non-root ADB baseline?

## 7.5 Reproducibility
Apakah dapat dibuat ulang dan diuji pada controlled scenario?

## 7.6 Complementarity
Apakah menambah informasi non-redundant?

## 7.7 Institutional alignment
Apakah hasil selection tetap sesuai boundary institusi?

Selection flow:

```text
Literature / Threat Pattern
  ↓
Forensic Question
  ↓
Candidate Evidence
  ↓
Selection Criteria
  ↓
Tier-1 Feasibility
  ↓
Tetapkan 3 Primary Evidence Source Groups (D-5)
  ↓
Tier-2 Empirical Validation
```

> `[KOREKSI v3.0]` Alur ini sebelumnya berujung *"Select ≤3 Primary Evidence Source Groups"* — rumusan dari masa sebelum `D-5`. Sejak v2.5 jumlahnya **bukan lagi hasil seleksi**: strukturnya **tepat tiga** dan terkunci (§4.1). Yang masih ditentukan Tier-2 adalah **keanggotaan artefak**, bukan jumlah kelompok. Batas ≤3 pada naskah BAB I Batasan #3 tetap terpenuhi karena tiga ≤ tiga.

---

# 8. FEASIBILITY FRAMEWORK

## Tier 1 — Documented/Theoretical

Basis:
- Android/Google/AOSP documentation;
- academic literature;
- MITRE ATT&CK Mobile;
- credible threat research.

Status:
- `STRONG`
- `CONDITIONAL`
- `WEAK_BASELINE`

## Tier 2 — Empirical

Dilakukan melalui:
- Android Emulator;
- dummy device;
- actual ADB operations;
- controlled benign actions/test apps.

### Availability status — 🔒 definisi pembeda *(baru v3.0)*

> `[KOREKSI v3.0]` Sampai v2.9 kelima status hanya **didaftar**, tanpa definisi yang membedakannya. Akibatnya dua artefak yang gagal karena sebab berbeda dapat dicatat dengan status yang sama, dan BAB III 3.4 tidak punya aturan pemberian status yang dapat ditulis.

| Status | Padanan naskah | Definisi pembeda | Uji pembeda |
|---|---|---|---|
| `acquired` | **diperoleh** | Operasi berjalan dan keluarannya berhasil diurai menjadi fakta | Ada keluaran, dan pengurai berhasil |
| `unavailable` | **tidak tersedia** | Operasi berjalan normal, tetapi sumber tidak memuat data yang dicari | Operasi sukses, keluaran kosong atau tidak memuat subjek |
| `denied` | **ditolak** | Operasi ditolak oleh izin, kebijakan perangkat, atau pembatasan antarmuka OEM | Ada galat izin/kebijakan yang eksplisit |
| `unsupported` | **tidak didukung** | Operasi atau antarmuka tidak ada pada versi Android atau bawaan perangkat itu | Perintah/layanan tidak dikenali |
| `failed` | **gagal** | Operasi seharusnya tersedia tetapi gagal secara teknis — galat, waktu habis, keluaran rusak | Gagal, dan tiga sebab di atas sudah dikesampingkan |

**Urutan pemeriksaan mengikat:** `unsupported` → `denied` → `unavailable` → `failed`. `failed` adalah **sisa**, dipakai hanya setelah ketiga sebab lain dikesampingkan; menjadikannya keranjang serba-guna akan menghapus informasi yang justru dibutuhkan pelaporan per lingkungan (§9.7).

⛔ **Keempat status selain `acquired` bermuara ke `UNKNOWN`, tidak pernah ke `FALSE`.** Pemetaan lengkapnya di `02_ARSITEKTUR` §Y.3.6.

## Decision enum

Setiap evidence row hanya memiliki satu decision:
- `CORE_CANDIDATE`
- `CORE_FALLBACK`
- `OPTIONAL`
- `CONDITIONAL`
- `REJECT_BASELINE`
- `COMPARE_AS_ALTERNATIVE`

| Nilai | Arti |
|---|---|
| `CORE_CANDIDATE` | Artefak inti kelompok; diandalkan aturan pada garis dasar |
| **`CORE_FALLBACK`** | **Cadangan artefak inti**; dipakai bila artefak inti gagal Tier-2, dengan mutu bukti yang dinyatakan lebih rendah *(§9.2a, §9.3a)* |
| `OPTIONAL` | Menambah konteks; tidak pernah menjadi kondisi wajib |
| `CONDITIONAL` | Bergantung perangkat, versi, atau skenario |
| `REJECT_BASELINE` | Tidak dipakai pada garis dasar tanpa akses akar |
| `COMPARE_AS_ALTERNATIVE` | Dinilai sebagai kandidat alternatif, bukan anggota kelompok |

> `[KOREKSI v3.0]` **`CORE_FALLBACK` dipakai di §9.2 dan §9.3 sejak v2.7 tetapi tidak pernah dimasukkan ke enum ini.** Akibatnya matriks memuat nilai yang menurut §8 tidak sah. Ditambahkan berikut definisinya.

Nuance/limitation masuk ke `Note`, bukan compound decision.

---

# 9. TIER-1 FEASIBILITY MATRIX

## 9.1 G1 — Application / Package / Capability State

Peran: identitas/instalasi, kapabilitas/akses khusus, eksekusi/persistensi, dan pengayaan statis APK. Matriks tidak menganggap seluruh artefak wajib tersedia; profil APKF memilih fakta yang sesuai dengan tingkat klaimnya.

| Subfokus | Artefak utama |
|---|---|
| Identitas/instalasi | package, UID, versi, jalur APK, waktu instal/update, sumber instalasi, certificate |
| Kapabilitas/akses khusus | permission, komponen, Accessibility, overlay/AppOps, notification listener, role/device-admin state |
| Eksekusi/persistensi | UsageStats/UsageEvents, process/activity snapshot, receiver/service terpicu, indikator boot/package event bila tersedia |
| Pengayaan statis | manifest, permission/komponen deklaratif, certificate, strings, URL/domain, resources/config |

| ID | Artifact / Fact | Raw Source / Operation | Semantics | Time | Tier-1 | Decision | Note |
|---|---|---|---|---|---|---|---|
| G1-A1 | package name, UID, version | `pm list packages -U`, `dumpsys package <pkg>` | current package state | current | STRONG | CORE_CANDIDATE | Subject anchor untuk source lain. |
| G1-A2 | APK path | `pm path <pkg>` | package file location | current | STRONG | CORE_CANDIDATE | Locator untuk APK acquisition. |
| G1-A3 | APK file + SHA-256 | `adb pull` dari readable APK path | file evidence | current | CONDITIONAL | CORE_CANDIDATE | Readability perlu Tier-2; gagal acquire = unavailable, bukan false. |
| G1-A4 | firstInstallTime / lastUpdateTime | package state | install/update metadata | historical metadata | STRONG | CORE_CANDIDATE | Bukan delivery timestamp. |
| G1-A5 | installer / initiating / originating info | install-source metadata | provenance metadata | current metadata | CONDITIONAL | CONDITIONAL | Nullable/privilege-dependent. |
| G1-A6 | signing/certificate | package/APK metadata | signing identity | current | STRONG | CORE_CANDIDATE | Package name saja tidak cukup untuk trust. |
| G1-A7 | declared components | package/manifest state | declared capability | current | STRONG | CORE_CANDIDATE | Declaration ≠ runtime use. |
| G1-A8 | requested permissions | package/manifest | declared capability | current | STRONG | CORE_CANDIDATE | Requested ≠ granted/use. |
| G1-A9 | granted permission state | `dumpsys package` | current grant state | current | STRONG | CORE_CANDIDATE | Granted ≠ access occurred. |
| G1-A10 | UsageStats / UsageEvents | `dumpsys usagestats` / usage service | execution history | historical limited | CONDITIONAL | CORE_CANDIDATE | Retention-limited; expired = UNKNOWN. |
| G1-A11 | process/activity state | `ps`, `dumpsys activity` | snapshot | current | CONDITIONAL | OPTIONAL | Tidak membuktikan historical execution. |
| G1-B1 | enabled Accessibility Service | secure settings/system state | current capability | current | STRONG | **CORE_CANDIDATE** *(M-3, v2.7)* | Dipakai profil aktif APKF-K02; `enabled ≠ abuse` tetap berlaku. |
| G1-B2 | enabled notification listener | secure settings | current capability | current | CONDITIONAL | OPTIONAL | OEM/device-dependent. |
| G1-B3 | overlay/AppOps state | package/appops | current capability | current | CONDITIONAL | OPTIONAL | Current state only. |
| G1-B4 | SMS/default role holder | role service | current role context | current | CONDITIONAL | OPTIONAL | Context modifier, bukan hard benign verdict. |
| G1-B5 | historical AppOps access | appops/system tracking | historical access | partial | WEAK_BASELINE | CONDITIONAL | Experimental; jangan required sebelum Tier-2. |
| G1-B6 | device admin/special state | device policy/system service | current state | current | CONDITIONAL | OPTIONAL | Scenario-specific. |
| G1-B7 | receiver/service persistence declaration | manifest/package state | declared capability | current | STRONG | CORE_CANDIDATE | Deklarasi tidak membuktikan komponen pernah dipicu. |
| G1-B8 | observed boot/package-event execution | controlled log/UsageEvents or other validated source | observed execution | historical limited | CONDITIONAL | CORE_FALLBACK | Hanya digunakan bila sumber dan atribusinya lolos Tier-2. |

### G1 justification
Walau institusi menyebut permission/install, alasan independen G1 adalah bahwa investigation membutuhkan **subject anchor**: package/UID/identity, capability, dan temporal installation context untuk menghubungkan evidence dari source lain.

---

## 9.2 G2 — Sensitive Communication Data

Peran: keberadaan data komunikasi sensitif dan konteks waktunya. Seluruh data pengujian dinamis harus sintetis.

| ID | Artifact / Fact | Raw Source / Operation | Semantics | Time | Tier-1 | Decision | Note |
|---|---|---|---|---|---|---|---|
| G2-C1 | SMS record, sender, timestamp, content/metadata sesuai exposure | SMS Content Provider via shell | data existence | historical per record | CONDITIONAL | CORE_CANDIDATE | Device/OEM-dependent; SMS exists ≠ package accessed it. |
| G2-C2 | MMS metadata | MMS Content Provider | data existence | historical | CONDITIONAL | OPTIONAL | Secondary context. |
| G2-C3 | contacts | Contacts Content Provider | data existence | mostly current | CONDITIONAL | **CORE_FALLBACK** *(M-1, v2.7)* | Cadangan G2 bila C1 gagal Tier-2. Mutu bukti lebih rendah — lihat 9.2a. |
| G2-C4 | call log | Call Log Provider | data existence | historical | CONDITIONAL | OPTIONAL | Secondary context. |
| G2-C5 | notification context captured by simulator/validated source | controlled notification record | contextual data existence | historical limited | CONDITIONAL | OPTIONAL | Hanya bila sumber dibentuk transparan dan lolos Tier-2; bukan akses oleh APK. |
| G2-C6 | thread/conversation association | SMS/MMS provider identifiers | relational context | historical | CONDITIONAL | OPTIONAL | Menguatkan urutan komunikasi tanpa mengatribusikan pembacaan. |

### 9.2a Risiko artefak tunggal — `M-1` *(baru v2.7)*

**G2 memiliki satu artefak paling langsung: C1.** C3/C4/C5/C6 memperluas konteks tetapi tidak otomatis setara dengan SMS. Bila C1 gagal Tier-2, dimensi D4 masih dapat dijawab sebagian; penurunan mutu bukti wajib dinyatakan.

**Mitigasi:** C3 (kontak) ditetapkan **CORE_FALLBACK**, sehingga kegagalan C1 tidak otomatis meruntuhkan G2.

> **Batas mitigasi — wajib dinyatakan di BAB III 3.4, jangan ditutupi.**
>
> 1. **C3 bukan pengganti setara.** Rekaman SMS menjawab B4 jauh lebih langsung untuk insiden APK penipuan; kontak menjawabnya lebih pucat. `M-1` menurunkan risiko keruntuhan, **bukan menyamakan mutu bukti**.
> 2. **Jumlah baris bukan ukuran kekuatan kelompok.** G1 memang memiliki lebih banyak kandidat daripada G2/G3. Kekuatan klaim ditentukan oleh semantik dan keterlacakan, bukan banyaknya artefak.
> 3. **Risiko antarmuka OEM menumpuk di titik ini** — lihat §9.7.

### G2 justification
G2 memberi konteks data sensitif yang tidak tersedia dari capability state. Namun data existence tidak boleh dinaikkan menjadi access claim tanpa linkage evidence.

---

## 9.3 G3 — Network Activity

Peran: aktivitas jaringan yang dapat diatribusikan ke UID/package dan jendela waktu.

| ID | Artifact / Fact | Raw Source / Operation | Semantics | Time | Tier-1 | Decision | Note |
|---|---|---|---|---|---|---|---|
| G3-D1 | UID rx/tx bytes, packet/bucket statistics | `dumpsys netstats detail` / NetworkStats | network usage | historical bucketed | STRONG | CORE_CANDIDATE | Activity ≠ endpoint/exfiltration. |
| G3-D2 | active connectivity state | `dumpsys connectivity` | snapshot | current | CONDITIONAL | **CORE_FALLBACK** *(M-1, v2.7)* | Cadangan G3 bila D1 gagal. Hanya snapshot, bukan aktivitas historis. |
| G3-D3 | Wi-Fi/mobile context | wifi/telephony services | snapshot | current | CONDITIONAL | OPTIONAL | Bukan historical destination. |
| G3-D4 | current TCP/UDP socket state | `/proc/net/*` / alternative source | snapshot/restricted | current | WEAK_BASELINE | REJECT_BASELINE | Modern Android restriction + poor post-incident value. |
| G3-D5 | exact historical IP/domain endpoint | alternative acquisition required | endpoint identity | method-dependent | WEAK_BASELINE | CONDITIONAL | Best-effort; `netstats` tidak membuktikan destination. |
| G3-D6 | request/response ke endpoint lokal simulator | local-only endpoint log + controlled capture | observed controlled communication | historical | STRONG dalam simulator | VALIDATION_ONLY | Oracle dinamis; tidak digeneralisasi ke APK malware nyata. |
| G3-D7 | resolver/proxy/capture record pada jaringan lab | isolated lab capture | endpoint context | historical | CONDITIONAL | OPTIONAL | Hanya bila dapat diatribusikan ke skenario dan sinkron waktu. |

### 9.3a Risiko artefak tunggal — `M-1` *(baru v2.7)*

**G3 memakai D1 (`netstats`) sebagai artefak inti pascaakuisisi.** D2/D3 memberi konteks keadaan, sedangkan D6/D7 dipakai untuk memvalidasi simulator dalam jaringan lokal. Keduanya tidak menggantikan D1 secara otomatis.

> **Batas mitigasi.** D2 hanya snapshot konektivitas saat ini, **bukan aktivitas jaringan historis**. Bila D1 gagal, B6 hanya terjawab sebagian, dan itu wajib dilaporkan apa adanya — bukan disamarkan seolah tergantikan penuh.

### G3 justification
G3 memberi activity evidence yang dapat dikaitkan melalui UID/time. Exact endpoint tetap evidentiary question terpisah.

---

## 9.4 Pengayaan G1 — APK-Derived / Static Evidence

Analisis statis adalah bagian pengayaan G1, bukan kelompok keempat dan bukan bukti tindakan runtime.

| ID | Artifact / Fact | Raw Source / Operation | Semantics | Tier-1 | Decision | Note |
|---|---|---|---|---|---|---|
| G1-S1 | manifest permissions/components | APK extraction + static parser | declared design/capability | STRONG | CORE_ENRICHMENT | Declaration ≠ runtime use. |
| G1-S2 | certificate/signing metadata | APK static parsing | signing identity | STRONG | CORE_ENRICHMENT | Digunakan bersama hash dan package. |
| G1-S3 | hardcoded URL/domain/IP | strings/config/resources | embedded reference | CONDITIONAL | CORE_ENRICHMENT | String exists ≠ contacted. |
| G1-S4 | embedded config/assets | APK static extraction | design-time clue | CONDITIONAL | OPTIONAL | Semantic value bergantung sampel. |
| G1-S5 | minSdk/targetSdk/ABI | manifest/binary metadata | compatibility attribute | STRONG | SAMPLE_METADATA | Bukan indikator penipuan. |

Potential value:
- technical behavior context;
- endpoint clues;
- reproducibility.

Keputusan yang berlaku:
> APK-static adalah **pengaya G1** untuk identitas, deklarasi kapabilitas, sertifikat, dan petunjuk titik ujung. Ia juga menjadi satu-satunya perlakuan terhadap APK malware nyata. Ia **bukan kelompok keempat**, bukan pengganti G3, dan tidak boleh membentuk klaim aktivitas teramati.

---

## 9.5 Delivery / Download Evidence — Conditional Alternative

Potential:
- installer provenance;
- DownloadManager records;
- browser history;
- messaging attachment metadata;
- filesystem residue.

Current concern:
- app-specific;
- private storage/sandbox;
- variable acquisition feasibility;
- poor genericity.

Belum primary sampai literature + Tier-2 menunjukkan acquisition yang reproducible.

---

## 9.6 Supporting Context — Bukan Primary Source Group

| ID | Artifact | Raw Source | Function |
|---|---|---|---|
| CTX-1 | Android version/build | `getprop` | validation scope |
| CTX-2 | device time/timezone | `date`, properties | temporal anchoring |
| CTX-3 | user/profile state | `pm list users` | context |
| CTX-4 | Platform Tools version | local tool metadata | provenance |
| CTX-5 | acquisition timestamp | session metadata | provenance |
| CTX-6 | SHA-256 | local/server hashing | integrity |

---

## 9.7 Ketersediaan artefak per lingkungan — *(baru v2.7)*

Status Tier-2 dicatat **per lingkungan**, bukan tunggal. Dasar: Shang dkk. (2025) §4.2.2 — artefak emulator berbeda dari perangkat fisik.

| Lingkungan | Peran |
|---|---|
| **Emulator terisolasi** — citra Google APIs, tanpa akun, tanpa SIM *(dikunci v3.0, `02_ARSITEKTUR` §O)* | Garis dasar utama. Seluruh skenario dijalankan di sini |
| **Perangkat fisik dummy** — Samsung Galaxy A10, satu unit *(`G-05`, diamandemen v3.1)* | Pembanding ketersediaan artefak. **Hanya APK simulasi** |

> **Risiko antarmuka OEM.** Perangkat pembanding beroperasi dengan antarmuka One UI, sedangkan garis dasar memakai citra Google APIs tanpa antarmuka OEM. Perbedaan hasil dapat dipengaruhi antarmuka OEM, perangkat keras, konfigurasi, dan versi sistem; perbandingan ini **mengurangi**, tetapi tidak menghilangkan, faktor pembaur. Dua dampak yang diperkirakan:
>
> | Perilaku OEM | Menyentuh |
> |---|---|
> | Pembersihan data penggunaan lebih agresif | **G1-A10** — satu-satunya penopang B3 |
> | Pembatasan kueri penyedia SMS melalui ADB | **G2-C1** — satu-satunya penopang B4 |
>
> **Ketidaktersediaan pada perangkat OEM bukan kegagalan penelitian, melainkan temuan** — dicatat sebagai status ketersediaan per lingkungan dan tidak digeneralisasi menjadi sifat seluruh Android atau seluruh perangkat One UI. Garis dasar tetap emulator terisolasi dengan citra Google APIs.

---

# 10. SOURCE-GROUP JUSTIFICATION

Tiga kelompok bukan standar universal forensik Android. Mereka adalah **taksonomi operasional penelitian**, disusun berbasis kanal akuisisi sesuai `D-5` (§4.1).

> 🔒 **Status v2.5, dikoreksi v2.6.** Ketiga kelompok **final secara struktural** — dasar pengelompokan, jumlah, dan penamaannya terkunci. Yang **tetap terbuka** adalah artefak mana persisnya masuk tiap kelompok; itu milik Tier-2. Artefak yang gagal dicatat statusnya dan **tidak menggugurkan kelompok**.
>
> `[KOREKSI v2.8]` ~~§11 tetap membolehkan **penggantian** bila satu kelompok gagal empiris~~ — perumusan v2.5 yang sudah dikoreksi pada v2.6 di §4.1.2, tetapi tertinggal di sini. Yang berlaku: ketidaklayakan total **membuka `D-5` secara eksplisit** sebagai keputusan baru, bukan penggantian diam-diam.
>
> G1 menopang tiga dimensi yang berbeda, sedangkan G2 dan G3 masing-masing menopang satu dimensi utama. Ketimpangan jumlah kandidat itu disengaja dan ditangani melalui label epistemik serta peran bukti, bukan dengan memecah kelompok.

| Criterion | G1 App/System | G2 Sensitive Communication | G3 Network Activity | ALT APK Static |
|---|---|---|---|---|
| Incident relevance | High | High untuk SMS/contact patterns | High untuk external activity | High |
| Probative value | High untuk identity/capability | High untuk target/context | Medium-high untuk activity | High untuk design/context |
| Correlatability | High package/UID/time | Medium-high time/context | High UID/time | High package/hash |
| Baseline feasibility | High | Medium-high, device-dependent | High activity; endpoint weak | Needs Tier-2 |
| Reproducibility | High | High controlled | High | High |
| Complementarity | High | High | High | Potential overlap G1 |
| Institutional alignment | High | High | Partial: endpoint weak | Membantu cara kerja/endpoint clue |

Pemilihan artefak final menunggu Tier-2. **Dasar pengelompokan, jumlah, dan penamaan kelompok tidak lagi menunggu — terkunci pada v2.5 (`D-5`).**

---

# 11. TIER-2 EMPIRICAL TEST PLAN

Tier-2 bukan full platform development.

Minimum environment:
- Android Emulator;
- Android Platform Tools;
- controlled benign app/actions;
- manual ADB collection;
- experiment logging.

Minimal record:

```text
artifact_id
android_version
device_or_emulator
command_or_api
privilege_state
test_action
expected_evidence
actual_result
availability_status
raw_output_path
timestamp_semantics
notes
```

## 11.1 ⭐ Protokol Tier-2 — 🔒 *(baru v3.0)*

> **Yang ditutup.** Sampai v2.9 core menyatakan Tier-2 **ada** tetapi tidak pernah menetapkan **bagaimana**. Tanpa protokol, BAB III 3.4 tidak punya prosedur yang dapat ditulis dan hasil Tier-2 tidak dapat direplikasi.

### Pengulangan

| # | Ketentuan |
|---|---|
| 1 | **Tiga pengulangan independen.** Keadaan perangkat **dibangun ulang atau direset** tiap pengulangan — bukan menjalankan perintah yang sama tiga kali pada keadaan yang sama. Yang diuji adalah **keterulangan perolehan artefak**, bukan kestabilan perintah |
| 2 | Wajib untuk artefak ber-`CORE_CANDIDATE`, `CORE_ENRICHMENT`, dan `CORE_FALLBACK` yang dipakai profil aktif. Artefak `OPTIONAL` memberi konteks tambahan dan diuji bila sumber daya memungkinkan |

### Pemberian status

| Hasil | Status | Arti |
|---|---|---|
| **3/3** | Diperoleh konsisten | Layak dipakai pada garis dasar |
| **1–2/3** | Diperoleh tidak konsisten | `CONDITIONAL` — **bukan** otomatis tidak layak |
| **0/3** | Tidak diperoleh | Dipilah menjadi `unavailable` · `denied` · `unsupported` · `failed` (§8), tidak diciutkan jadi satu label |

### Ketentuan pembeda

| # | Ketentuan |
|---|---|
| 1 | ⭐ Bedakan **"sumber berhasil diakses tetapi rekaman target tidak muncul"** (`unavailable`) dari **"sumber tidak dapat diakses"** (`denied`/`unsupported`). Di sinilah Tier-2 paling mudah salah catat |
| 2 | `UNKNOWN` akibat **retensi atau kedaluwarsa** adalah keluaran yang **sah**, bukan kegagalan sistem. Justru di situ semantik tiga keadaan terlihat bekerja |
| 3 | Hasil dicatat **per lingkungan** (§9.7), tidak diciutkan menjadi satu nilai lintas lingkungan. Inilah yang memberi isi pada perbandingan emulator ↔ perangkat fisik |
| 4 | Cadangan **dievaluasi**, tidak otomatis menggantikan artefak inti yang gagal. **G2-C3 tidak setara G2-C1; G3-D2 tidak setara G3-D1** — mutu buktinya berbeda dan perbedaan itu wajib dinyatakan |
| 5 | Bila artefak inti gagal dan **tidak ada cadangan**, pertanyaan rekonstruksinya dilaporkan **tidak tertanggung** — tidak dipaksakan |
| 6 | Bila **seluruh** kelompok tidak layak, hal itu **memicu peninjauan** struktur kelompok `D-5`. ⛔ Protokol ini **tidak** membuka `D-5` sendiri; keputusan membuka tetap milik peneliti dan pembimbing. Memberi wewenang itu kepada protokol akan membalik urutan otoritas |

⚠️ **Berbeda dari uji konsistensi §18.3a.** Tier-2 mengulang **akuisisi** dengan keadaan dibangun ulang — yang diuji ketersediaan artefak. Uji konsistensi mengulang **analisis** atas berkas bukti yang sama — yang diuji determinisme mesin. Mencampur keduanya membuat dua-duanya kabur.

Priority:
1. package/UID/version;
2. install/update metadata;
3. requested/granted permissions;
4. Accessibility current state;
5. UsageStats/UsageEvents;
6. SMS provider;
7. Contacts provider;
8. UID network stats;
9. APK pull/static extraction;
10. endpoint strategy jika dibutuhkan.

A source group menjadi primary hanya jika:
- menjawab important forensic question;
- punya probative value;
- correlatable;
- core artifacts feasible/reproducible;
- semantics explicit;
- non-redundant;
- fit institutional boundary.

Artefak individual dapat diganti berdasarkan Tier-2 **tanpa mengubah struktur kelompok**. Bila satu kelompok **sepenuhnya** tidak layak, `D-5` dibuka kembali secara eksplisit — bukan diganti diam-diam (§4.1.2). *(diperbarui v2.7)*

## 11.2 ⭐ Kontrak kebutuhan BAB III 3.4 — 🔒 *(baru v3.2)*

Kebutuhan sistem **tidak berasal dari elisitasi pengguna**. Kebutuhan diturunkan secara terlacak dari rumusan masalah dan tujuan BAB I, lima dimensi §5, tiga kelompok sumber, prinsip forensik, serta kontrak aturan. BAB III 3.4 wajib memuat sekurang-kurangnya dua kelompok berikut.

### Kebutuhan fungsional minimum

| ID | Kebutuhan |
|---|---|
| `KF-01` | Sistem mengelola kasus, perangkat, agen lokal, dan sesi akuisisi secara terpisah |
| `KF-02` | Agen menjalankan operasi ADB ber-*allowlist* untuk memperoleh sumber G1/G2/G3 dan mencatat status ketersediaannya per lingkungan |
| `KF-03` | Sistem menghitung/verifikasi SHA-256, menyimpan bukti mentah secara imutabel, dan merekam metadata asal-usul |
| `KF-04` | Backend mengurai artefak dan menormalisasikannya menjadi fakta dengan `event_type`, `epistemic_class`, `evidence_state`, subjek, waktu, dan asal bukti |
| `KF-05` | Sistem memuat basis pengetahuan dan aturan YAML, memvalidasi profil, `expects_epistemic_class`, `claim_level`, rujukan tingkat elemen, serta versi aturan sebelum evaluasi |
| `KF-06` | Mesin aturan mengevaluasi kondisi dan profil dalam tiga keadaan, menangani konflik sebagai `UNKNOWN`, mengagregasikan profil ke keluarga, dan mencatat seluruh hasil kondisi |
| `KF-07` | Hanya evaluasi keluarga `matched` menghasilkan temuan; hipotesis disusun dari temuan yang kompatibel; seluruh keluaran ditelusuri ke fakta, bukti mentah, aturan, dan rujukan |
| `KF-08` | Antarmuka dan laporan menyajikan status akuisisi, bukti, fakta, evaluasi aturan, temuan, bukti yang tidak tersedia, serta keterlacakan dua arah |

### Kebutuhan nonfungsional minimum

| ID | Kebutuhan |
|---|---|
| `KNF-01` | **Deterministik dan dapat direproduksi:** masukan, versi aturan/KB, dan konfigurasi yang sama menghasilkan keluaran semantik yang sama |
| `KNF-02` | **Integritas dan auditabilitas:** bukti mentah tidak ditimpa; perubahan dan operasi penting tercatat |
| `KNF-03` | **Keamanan:** autentikasi, token agen, validasi unggahan, pembatasan CORS, dan larangan perintah ADB arbitrer |
| `KNF-04` | **Keterbatasan klaim:** sistem tidak mengubah kapabilitas menjadi perilaku, aktivitas jaringan menjadi eksfiltrasi, atau bukti hilang menjadi FALSE |
| `KNF-05` | **Kompatibilitas terbatas dan terdokumentasi:** versi Android, perangkat, AVD, alat, serta perbedaan lingkungan dicatat; hasil tidak digeneralisasi di luar lingkungan uji |
| `KNF-06` | **Kemudahan pemeliharaan:** kode, skema, aturan, basis pengetahuan, dan konfigurasi eksperimen memiliki versi dan dapat diuji per lapisan |

Wording akademik dan nomor tabel boleh disesuaikan saat revisi naskah, tetapi cakupan `KF-01`–`KF-08` dan `KNF-01`–`KNF-06` tidak boleh hilang tanpa keputusan baru.

## 11.3 Tiga kategori sampel dan seleksinya — 🔒 v3.3

| Kategori | Fungsi penelitian | Dinamis? | Sumber/asal |
|---|---|---|---|
| **S-A Simulator bukti aman** | *ground truth* untuk validasi aturan, `UNKNOWN`, konflik, dan rekonstruksi | ya, terkontrol | dikembangkan peneliti |
| **S-B Aplikasi benign/kontrol** | menguji anti-klaim-berlebih pada kapabilitas atau aktivitas yang sah | ya, setelah verifikasi dan isolasi | sumber APK publik atau aplikasi yang legal diperoleh |
| **S-C APK malware nyata** | memeriksa keterwakilan pola artefak statis pada sampel dunia nyata | **tidak** | MalwareBazaar utama; VX-Underground cadangan |

S-C memakai model kandidat: kumpulkan minimum enam dan target delapan kandidat; pilih tiga akhir setelah pemetaan terhadap lima keluarga APKF. Portofolio akhir harus, sejauh kandidat tersedia, mewakili (a) komunikasi sensitif, (b) aksesibilitas/*overlay*, dan (c) persistensi/jaringan. Catat `sha256`, sumber, identitas/family yang dikorroborasi, keluarga APKF yang relevan, artefak statis, `minSdk`, `targetSdk`, ABI, duplikasi, serta alasan pilih/tolak.

APK pihak ketiga tidak otomatis dianggap benign atau fraud hanya karena berasal dari situs distribusi. Hash, signature, package, versi, reputasi sumber, serta hasil pemindaian statis dicatat sebelum keputusan pemasangan. S-B dipakai sebagai kontrol; S-C tidak dipasang, tidak dijalankan, dan tidak dihubungkan ke jaringan.

Spesifikasi simulator aman dan proses pengembangannya berada di `02_ARSITEKTUR` §N dan §Y.3.5b. Simulator bukan malware dan dilarang memiliki pencurian kredensial/data nyata, impersonasi merek, obfuscation/evasion, eksploitasi, izin tersembunyi, komunikasi pihak ketiga, atau persistensi tersembunyi.

---

# 12. KNOWLEDGE BASE

Knowledge Base bukan database “malware verdict”.

Sources:
1. Android/Google technical documentation
2. AOSP source
3. MITRE ATT&CK Mobile
4. credible threat research
5. academic papers

Setiap entry minimal:
- title;
- publisher/author;
- URL/DOI;
- publication/access date;
- extracted claim;
- Android/version assumptions;
- quality notes.

## 12.1 Registri sumber desain APKF — 🔒 Generate 1.5

ID berikut adalah entri `KB_Source` yang wajib tersedia agar YAML `design_baseline` §14.2 dapat dimuat. Status `verified_design` berarti sumber primer sudah diperiksa untuk perancangan; klaim bibliografis final tetap mengikuti daftar pustaka naskah.

| ID | Sumber primer | Peran/label baku | URL |
|---|---|---|---|
| `KB-AND-PACKAGE` | Android Developers — `PackageManager` | `artifact_semantics` — identitas package terpasang | https://developer.android.com/reference/android/content/pm/PackageManager |
| `KB-AND-PERMISSION` | Android Developers — Permissions on Android | `artifact_semantics` — permission dan akses khusus | https://developer.android.com/guide/topics/permissions/overview |
| `KB-AND-ACCESSIBILITY` | Android Developers — `AccessibilityService` | `artifact_semantics` — deklarasi/pengaktifan layanan aksesibilitas | https://developer.android.com/reference/android/accessibilityservice/AccessibilityService |
| `KB-AND-OVERLAY` | Android Developers — `Settings.canDrawOverlays` | `artifact_semantics` — kemampuan menggambar di atas aplikasi lain | https://developer.android.com/reference/android/provider/Settings#canDrawOverlays(android.content.Context) |
| `KB-AND-NOTIFICATION` | Android Developers — `NotificationListenerService` | `artifact_semantics` — deklarasi/akses listener notifikasi | https://developer.android.com/reference/android/service/notification/NotificationListenerService |
| `KB-AND-BROADCAST` | Android Developers — Broadcasts overview | `artifact_semantics` — receiver dan pemicu peristiwa sistem | https://developer.android.com/develop/background-work/background-tasks/broadcasts |
| `KB-AND-USAGE` | Android Developers — `UsageStatsManager` | `artifact_semantics` — riwayat/statistik penggunaan aplikasi | https://developer.android.com/reference/android/app/usage/UsageStatsManager |
| `KB-AND-NETWORK` | Android Developers — `NetworkStatsManager` | `artifact_semantics` — statistik jaringan berbasis bucket | https://developer.android.com/reference/android/app/usage/NetworkStatsManager |
| `KB-MITRE-T1624` | MITRE ATT&CK Mobile — Event Triggered Execution | `technique_mapping` — pemicu terhadap eksekusi/persistensi | https://attack.mitre.org/techniques/T1624/ |
| `KB-MITRE-T1417-002` | MITRE ATT&CK Mobile — GUI Input Capture | `technique_mapping` — aksesibilitas/overlay sebagai kapabilitas relevan | https://attack.mitre.org/techniques/T1417/002/ |
| `KB-MITRE-T1644` | MITRE ATT&CK Mobile — Out of Band Data | `technique_mapping` — notifikasi/SMS sebagai kanal sensitif | https://attack.mitre.org/techniques/T1644/ |

Seluruh entri memakai `verification_status: verified_design` dan tanggal akses 5 September 2026. Sumber Android mendukung semantik artefak; MITRE mendukung relevansi perilaku. Keduanya tidak mengubah kapabilitas menjadi bukti penyalahgunaan.

Saat YAML dimuat, `reference_ids` tingkat keluarga membentuk `RuleElementReference` dengan `rule_element_key=family_id`; `reference_ids` tingkat kondisi membentuk kunci `profile_id.condition_id`. `reference_role` memakai label baku registri, kecuali elemen memberikan override eksplisit. Temuan dari profil `matched` hanya mewarisi rujukan keluarga dan kondisi yang benar-benar berkontribusi, lalu antarmuka mengelompokkannya sebagai **semantik artefak**, **relevansi/pemetaan perilaku**, dan **batas interpretasi**. Dengan demikian daftar rujukan pada temuan bukan daftar pustaka generik yang sama untuk semua keluaran.

---

# 13. RULE-BASED EVIDENCE CORRELATION

**APKF** adalah **Aturan Pola Korelasi Forensik**: aturan deterministik untuk menilai pola fakta ternormalisasi dalam lingkup investigasi aplikasi APK penipuan. APKF bukan tanda tangan malware, bukan pengklasifikasi aplikasi, dan bukan vonis bahwa penipuan telah terjadi.

## 13.1 Rule requirements
Rule harus:
- deterministic;
- reference-backed;
- auditable;
- evidence-traceable;
- missing-evidence-aware.

Rule tidak boleh:
- permission tunggal → malware verdict;
- Accessibility enabled → abuse;
- network activity → exfiltration;
- `INTERNET` permission → strong suspicious signal;
- package-name allowlist → satu-satunya hard benign exclusion.

## 13.2 Three-state semantics

```text
TRUE
FALSE
UNKNOWN
```

Outcome:

```text
matched
not_matched
insufficient_evidence
```

Contract:

```text
all required TRUE
→ matched

any required FALSE
→ not_matched

no required FALSE + at least one required UNKNOWN
→ insufficient_evidence
```

Rule schema:

```yaml
claim_level: identity | capability | observed_activity | contextual_cooccurrence
unknown_handling:
  required_unknown: insufficient_evidence
  optional_unknown: annotate
  exclusionary_unknown: do_not_exclude
```

Satu keluarga dapat memiliki beberapa profil bukti. Kondisi `any_of` dalam satu profil hanya boleh berisi fakta yang **setara secara semantik**. Bukti wajib, opsional, kontekstual, dan eksklusioner mempunyai peran terpisah.

Agregasi profil ke keluarga:

```text
ada profil matched                       → keluarga matched
semua profil not_matched                 → keluarga not_matched
tidak ada matched + ada insufficient     → keluarga insufficient_evidence
```

Bila fakta relevan saling bertentangan, mesin tidak memilih fakta yang menguntungkan aturan. Keadaan kondisi menjadi `UNKNOWN` dengan `reason=conflicting_evidence` dan konflik tetap tertelusur.

### 13.2.1 Semantik selector dan operator — 🔒 Generate 1.5

Setiap kondisi memilih fakta melalui kombinasi `fact`, `subject_binding`, `operator`, dan `where`. Operator baseline hanya:

| Operator | Makna |
|---|---|
| `exists` | sedikitnya satu fakta sesuai selector tersedia |
| `equals` | nilai fakta sama dengan nilai yang ditetapkan |
| `in` | nilai fakta termasuk himpunan nilai yang ditetapkan |
| `greater_than` | nilai numerik lebih besar dari batas tetap |
| `delta_greater_than` | selisih dua observasi berurutan lebih besar dari batas tetap |
| `overlaps_window` | interval fakta beririsan dengan jendela kasus |

Ketiadaan baris yang cocok hanya menjadi `FALSE` bila sumber relevan berstatus `acquired`, penguraian berhasil, dan cakupan selector memang diperiksa. Jika sumber tidak tersedia, ditolak, tidak didukung, gagal, di luar retensi, atau cakupan tidak dapat dipastikan, hasilnya `UNKNOWN`.

`exists`, `equals`, dan `in` membaca `predicate_value`, bukan sekadar keberadaan baris. Untuk selector dengan beberapa nilai sasaran, satu fakta positif yang cocok menghasilkan `TRUE`; `FALSE` hanya dihasilkan bila seluruh nilai sasaran yang diperiksa mempunyai fakta negatif eksplisit dan cakupannya lengkap; sisanya `UNKNOWN`. `greater_than` dan `delta_greater_than` menghasilkan `FALSE` ketika nilai teramati sah tidak melewati batas. `overlaps_window` menghasilkan `FALSE` hanya bila jendela yang dicari tercakup penuh dan tidak ada peristiwa beririsan; fakta di luar jendela tidak cukup untuk meniadakan peristiwa di dalam jendela.

Untuk menjaga keterlacakan `FALSE`, penormalisasi menghasilkan fakta negatif eksplisit dengan `predicate_value: false` hanya bagi predikat tertutup yang cakupan sumbernya lengkap. Kondisi `TRUE`/`FALSE` harus menunjuk fakta positif/negatif tersebut; ketiadaan baris tanpa fakta cakupan tidak boleh dijadikan `FALSE`.

Seluruh kondisi dalam satu profil menggunakan `subject_binding` yang sama. Kondisi lintas-UID atau lintas-package tidak boleh digabung menjadi satu kecocokan. Untuk profil historis, fakta juga harus memenuhi `time_binding` yang sama.

`applicability` diperiksa sebelum kondisi melalui **dua sumbu terpisah**. `evidence_mode` menyatakan bentuk bukti (`installed_runtime` atau `apk_static`), sedangkan `run_purpose` menyatakan tujuan eksekusi (`authoring`, `holdout`, `benign_control`, atau `production`). Profil harus cocok pada kedua sumbu. Profil yang tidak berlaku tidak diberi salah satu dari tiga *outcome*; evaluasinya dicatat sebagai `evaluation_status: skipped_not_applicable` dengan `outcome: null` dan dikeluarkan dari agregasi keluarga. Jika tidak ada profil yang berlaku, keluarga menghasilkan `insufficient_evidence` dengan alasan `no_applicable_profile`. Dengan demikian profil statis tidak mengubah hasil runtime, profil runtime tetap aktif pada *authoring/holdout*, dan profil `validation_only` tidak pernah aktif pada kasus produksi.

### 13.2.2 Efek kondisi eksklusioner — 🔒 Generate 1.5

Kondisi eksklusioner **tidak menghapus fakta yang benar** dan tidak mengubah kapabilitas teramati menjadi `not_matched`. Bila kondisi eksklusioner `TRUE`, keluaran profil tetap dihitung dari kondisi wajib, tetapi diberi `interpretation_status: constrained`; temuan tersebut tidak boleh dipakai untuk menaikkan hipotesis pada tingkat klaim yang diblokir. `UNKNOWN` pada kondisi eksklusioner hanya dicatat dan tidak dianggap sebagai pengecualian.

Baseline domain K01–K05 tidak memakai *hard benign allowlist*. Cabang eksklusioner diuji dengan fixture sintetis bertanda `validation_only`, sehingga pengujian mesin tidak memasukkan label eksperimen ke bukti produksi.

## 13.3 Scoring — 🔒 DICABUT `D-6` *(diputuskan 1 Sep 2026)*

> **Keputusan: skor dicabut dari MVP.** Keluaran mekanisme aturan terbatas pada tiga keadaan — `matched` · `not_matched` · `insufficient_evidence`. Tidak ada skor, tidak ada ambang, tidak ada peringkat.
>
> **Dasarnya.** Tidak ada satu pun bagian naskah yang bergantung pada skor: RQ1–RQ3 tidak menyebutnya, Tujuan tidak menyebutnya, naskah BAB II tidak menyebutnya. Sementara mempertahankannya menambah permukaan serangan terhadap postur **bukan mesin penilai otomatis** (BAB I Batasan #4; BAB II 2.3) dan terhadap **K-07**.
>
> **Yang sudah dieksekusi:** blok `scoring:` dihapus dari ketiga spesifikasi aturan §14 (APKF-001, APKF-002, APKF-003); *threshold tuning* dicabut dari §16.
>
> **Boleh muncul di BAB V** sebagai saran pengembangan lanjutan, tidak di BAB III.

> `[ARSIP v2.3]` Rumusan lama mewajibkan tiga skor — `Evidence Support Score`, `Correlation Score`, `Rule Match Score` — dengan catatan *"jangan sebut probability tanpa calibration"*. APKF-003 memuat `scoring: mode: weighted_support, threshold: null`: mekanisme ada, ambang kosong. Keadaan menggantung itu yang dicabut.

---

# 14. WORKING RULE SPECIFICATIONS

Struktur keluarga, peran bukti, agregasi profil, batas klaim, katalog 16 profil awal, dan YAML `design_baseline` di bawah **terkunci untuk penyusunan diagram dan BAB III**. *Authoring* menguji serta dapat memperbaiki rincian empiris menurut §14.3; ia tidak memberi izin mengubah fungsi keluarga secara diam-diam.

## 14.0 ⭐ Konvensi wajib untuk seluruh spesifikasi aturan — 🔒 *(baru v3.0)*

> `[KOREKSI v3.0]` Ketiga spesifikasi di bawah ditulis pada v2.3, **sebelum** `D-5` melahirkan `epistemic_class` (v2.5) dan sebelum `02_ARSITEKTUR` §Y.3.3 mewajibkan validasi saat pemuatan (v2.6). Akibatnya, menurut kontrak dokumen kanonik sendiri, **ketiganya tidak akan dapat dimuat**. Bagian ini menutup tiga kesenjangan sekaligus.

### (a) `expects_epistemic_class` wajib pada tiap kondisi

`02_ARSITEKTUR` §Y.3.3 menetapkan pemuat aturan memvalidasi kecocokan kelas epistemik **saat pemuatan**; aturan yang menyatakan kelas berbeda dari kelas `event_type` yang dirujuknya **gagal dimuat**. Karena itu tiap kondisi wajib menyandang field tersebut.

### (b) Pemetaan nama fakta ↔ `event_type`

Spesifikasi memakai nama kapital sebagai **nama kondisi yang terbaca manusia**; skema data memakai `event_type` ber-*snake_case*. Keduanya bukan hal yang sama, dan sampai v2.9 tidak ada yang menghubungkannya.

| Nama kondisi | `event_type` | `epistemic_class` | Padanan naskah |
|---|---|---|---|
| `PACKAGE_INSTALLED` | `package_observed_installed` | `identity_attribute` | atribut identitas |
| `PACKAGE_UID_MAPPING_AVAILABLE` | `uid_observed` | `identity_attribute` | atribut identitas |
| `PACKAGE_INSTALLED_RELEVANT_WINDOW` | `package_observed_installed` | `identity_attribute` | atribut identitas |
| `PERMISSION_REQUESTED` | `permission_observed_requested` | `capability_state` | kapabilitas |
| `PERMISSION_GRANTED` | `permission_observed_granted` | `capability_state` | kapabilitas |
| `SENSITIVE_PERMISSION_PRESENT` | `permission_observed_granted` | `capability_state` | kapabilitas |
| `ACCESSIBILITY_SERVICE_DECLARED` | `accessibility_service_observed_declared` | `capability_state` | kapabilitas |
| `ACCESSIBILITY_SERVICE_ENABLED` | `accessibility_service_observed_enabled` | `capability_state` | kapabilitas |
| `OVERLAY_PERMISSION_ACTIVE` | `overlay_permission_observed_active` | `capability_state` | kapabilitas |
| `EXECUTION_EVENT_RELEVANT_WINDOW` | `app_usage_observed` | `execution_observed` | eksekusi teramati |
| `NETWORK_ACTIVITY_OBSERVED` | `uid_network_activity_observed` | `execution_observed` | eksekusi teramati |
| `NETWORK_ACTIVITY_RELEVANT_WINDOW` | `uid_network_activity_observed` | `execution_observed` | eksekusi teramati |
| `SMS_DATA_PRESENT` | `sms_record_observed` | `data_present` | keberadaan data |
| `SENSITIVE_COMMUNICATION_CONTEXT_PRESENT` | `sms_record_observed` | `data_present` | keberadaan data |
| `APK_IDENTITY_AVAILABLE` | `apk_identity_observed` | `identity_attribute` | atribut identitas APK statis |
| `SENSITIVE_COMMUNICATION_CAPABILITY_GRANTED` | `sensitive_communication_capability_observed_granted` | `capability_state` | kapabilitas komunikasi sensitif aktif |
| `SENSITIVE_COMMUNICATION_CAPABILITY_DECLARED` | `sensitive_communication_capability_observed_declared` | `capability_state` | kapabilitas komunikasi sensitif deklaratif |
| `SPECIAL_ACCESS_CAPABILITY_ENABLED` | `special_access_capability_observed_enabled` | `capability_state` | kapabilitas akses khusus aktif |
| `SPECIAL_ACCESS_CAPABILITY_DECLARED` | `special_access_capability_observed_declared` | `capability_state` | kapabilitas akses khusus deklaratif |
| `EVENT_TRIGGER_CAPABILITY_DECLARED` | `event_trigger_capability_observed_declared` | `capability_state` | kapabilitas pemicu peristiwa deklaratif |
| `SERVICE_DECLARED` | `service_observed_declared` | `capability_state` | kapabilitas layanan deklaratif |
| `EVENT_TRIGGER_EXECUTION_OBSERVED` | `event_trigger_execution_observed` | `execution_observed` | eksekusi terpicu peristiwa |
| `ACTIVITY_RESUMED_OBSERVED` | `activity_observed_resumed` | `execution_observed` | aktivitas aplikasi teramati aktif |
| `PROCESS_RUNNING_OBSERVED` | `process_observed_running` | `execution_observed` | proses aplikasi teramati berjalan |
| `LOCAL_ENDPOINT_REQUEST_OBSERVED` | `local_endpoint_request_observed` | `execution_observed` | komunikasi terkendali ke endpoint lokal |
| `LAB_NETWORK_FLOW_OBSERVED` | `lab_network_flow_observed` | `execution_observed` | aliran jaringan pada lab terisolasi |
| `SCENARIO_SUBJECT_BINDING_AVAILABLE` | `scenario_subject_binding_observed` | `identity_attribute` | pengikat package/UID ke skenario validasi |
| `APK_ENDPOINT_REFERENCE_PRESENT` | `apk_endpoint_reference_observed` | `identity_attribute` | petunjuk endpoint deklaratif/statis |
| `SYNTHETIC_EXCLUSION_MARKER` | `synthetic_exclusion_marker_observed` | `identity_attribute` | fixture eksklusioner khusus validasi mesin |
| `CONTACT_DATA_PRESENT` | `contact_record_observed` | `data_present` | keberadaan data kontak |
| `CALL_LOG_DATA_PRESENT` | `call_log_record_observed` | `data_present` | keberadaan catatan panggilan |
| `NOTIFICATION_CONTEXT_PRESENT` | `notification_context_observed` | `data_present` | keberadaan konteks notifikasi |

⭐ **Perhatikan tiga baris `capability_state` untuk izin.** Justru di situlah `D-5` bekerja: `PERMISSION_GRANTED` **tidak dapat** dinyatakan `execution_observed`, sehingga aturan yang memperlakukan izin sebagai perbuatan gagal dimuat — bukan gagal dinilai belakangan.

### (c) Pemetaan `source_group` ↔ G1/G2/G3

| Nilai `source_group` | Kelompok | Nama Indonesia |
|---|---|---|
| `APP_SYSTEM_STATE` | **G1** | Keadaan Aplikasi dan Sistem |
| `SENSITIVE_COMMUNICATION` | **G2** | Data Komunikasi Sensitif |
| `NETWORK_ACTIVITY` | **G3** | Aktivitas Jaringan |

Nilai enum dipertahankan sebagai nama teknis; **G1/G2/G3 dan nama Indonesianya dipakai di naskah** — disiplin yang sama dengan `G-01`.

### (d) `reference_ids` wajib pada metadata aturan

Setiap aturan wajib mempunyai daftar `reference_ids` yang **tidak kosong**. Setiap ID harus dapat diresolusikan melalui `RuleReference` ke satu entri `KB_Source`; ID yang tidak ditemukan, duplikat, atau menunjuk sumber nonaktif membuat aturan gagal dimuat.

```yaml
reference_ids:
  - KB-AND-PACKAGE
```

ID pada YAML aktif §14.2 harus cocok dengan registri sumber desain §12.1; ia bukan pengganti sitasi bibliografis pada naskah. Sebelum `frozen_for_holdout`, setiap entri `KB_Source` juga wajib mempunyai klaim yang diekstrak, cakupan versi Android, peran rujukan, serta catatan mutu yang telah diverifikasi.

### (e) `claim_level`, profil, dan konflik wajib

Setiap profil wajib menyatakan `claim_level`. Keluaran profil memakai tingkat klaim tersebut; agregasi keluarga tidak boleh menaikkannya. Setiap evaluasi menyimpan `profile_id`, `matched_profile_ids`, dan `conflict_reason` bila ada.

### (f) Rujukan tingkat elemen

Selain metadata sumber, relasi rujukan dapat ditempelkan pada kondisi, profil, atau batas interpretasi melalui:

```yaml
references:
  - source_id: KB-SRC-...
    rule_element_key: APKF-K01.P01.C02
    reference_role: artifact_semantics
    extracted_claim: "..."
    version_scope: "..."
    verification_status: verified
```

Nilai `reference_role`: `artifact_semantics`, `behavior_relevance`, `interpretation_limit`, atau `technique_mapping`. Antarmuka membedakan basis bukti, basis aturan, dan basis pengetahuan.

## 14.1 Portofolio lima keluarga APKF — 🔒 v3.3

| Keluarga | Fokus | Contoh profil bukti | Kelompok | Tingkat klaim maksimum |
|---|---|---|---|---|
| **APKF-K01** | kapabilitas komunikasi sensitif | izin SMS; izin kontak/call-log; deklarasi statis pada sampel S-C | G1 + konteks G2 | kapabilitas; G2 hanya keberadaan data |
| **APKF-K02** | antarmuka istimewa/akses khusus | Accessibility aktif; overlay aktif; notification listener aktif | G1 | kapabilitas |
| **APKF-K03** | persistensi atau eksekusi terpicu peristiwa | receiver/service dideklarasikan; eksekusi boot/package-event teramati | G1 | kapabilitas atau aktivitas teramati sesuai profil |
| **APKF-K04** | eksekusi package relevan teramati | UsageStats/UsageEvents; activity resumed; process running | G1 | aktivitas teramati |
| **APKF-K05** | aktivitas jaringan terkait UID/package | statistik UID; profil endpoint lokal simulator; capture lab teratribusi | G1 + G3 | aktivitas jaringan teramati |

Ketiga variasi dalam satu baris adalah **profil**, bukan kondisi alternatif yang dicampur. Misalnya deklarasi statis receiver dan eksekusi receiver yang teramati berada di keluarga K03, tetapi menghasilkan tingkat klaim berbeda dan tidak boleh saling menggantikan untuk menyatakan eksekusi.

### 14.1.1 Struktur profil minimum

| Elemen | Fungsi |
|---|---|
| `required` | gerbang fakta minimum untuk temuan profil |
| `optional` | menambah konteks; `UNKNOWN` tidak menggagalkan profil |
| `contextual` | membantu rekonstruksi lintas temuan, tidak menentukan keluaran profil |
| `exclusionary` | menahan interpretasi tertentu bila benar; `UNKNOWN` tidak otomatis mengecualikan |
| `claim_level` | batas bahasa temuan yang boleh diterbitkan |
| `reference_ids`/`references` | dasar semantik, relevansi, teknik, dan batas interpretasi |

### 14.1.2 Rekonstruksi lintas keluarga

`required` menentukan apakah **profil tingkat rendah** terpenuhi. Rekonstruksi kejadian dilakukan setelahnya:

```text
temuan K01–K05
  → kelompokkan menurut package/UID
  → selaraskan jendela waktu
  → sertakan konteks G2 dan bukti yang tidak teramati
  → terapkan batas klaim serta bukti eksklusioner
  → susun hipotesis investigasi
```

Hipotesis dapat menyatakan urutan yang didukung, misalnya package ditemukan → kapabilitas aktif → eksekusi teramati → aktivitas jaringan teramati. Ia tidak boleh mengisi tahap yang tidak didukung atau menyebut pencurian/eksfiltrasi hanya karena urutan tersebut ada.

**Gerbang rekonstruksi:** sekurang-kurangnya dua temuan dari keluarga berbeda harus berbagi subject key dan jendela waktu yang kompatibel. Untuk menyatakan urutan kejadian, sedikitnya satu temuan harus berkelas `observed_activity`. Bila gerbang tidak terpenuhi, sistem hanya menerbitkan temuan tingkat rendah dan tidak memaksa hipotesis.

### 14.1.3 Katalog 16 profil `design_baseline` — 🔒 Generate 1.5

Katalog ini adalah rancangan awal yang cukup konkret untuk implementasi, diagram, dan BAB III. Kolom “batas keluaran” adalah bagian aturan, bukan catatan opsional.

| Profil | Aplikasi | Fakta wajib | Fakta opsional/kontekstual | Batas keluaran |
|---|---|---|---|---|
| `K01-P01` | package terpasang | identitas package; izin SMS aktif (`READ_SMS`, `RECEIVE_SMS`, atau `SEND_SMS`) | deklarasi izin; keberadaan SMS | hanya kapabilitas SMS; tidak membuktikan akses/pengiriman |
| `K01-P02` | package terpasang | identitas package; izin `READ_CONTACTS` atau `READ_CALL_LOG` aktif | deklarasi izin; keberadaan kontak/call log | hanya kapabilitas membaca data terkait |
| `K01-P03` | APK statis | identitas APK; deklarasi salah satu izin komunikasi sensitif | string/config relevan sebagai konteks bila tersedia | hanya kapabilitas deklaratif; tidak membuktikan instalasi/eksekusi |
| `K02-P01` | package terpasang | identitas package; layanan aksesibilitas aktif | deklarasi layanan; eksekusi teramati sebagai konteks | aktif ≠ disalahgunakan |
| `K02-P02` | package terpasang | identitas package; izin overlay aktif | deklarasi izin; eksekusi teramati sebagai konteks | dapat menggambar di atas aplikasi; tidak membuktikan phishing |
| `K02-P03` | package terpasang | identitas package; listener notifikasi aktif | deklarasi listener; konteks notifikasi | akses aktif; tidak membuktikan isi dibaca/disalahgunakan |
| `K02-P04` | APK statis | identitas APK; deklarasi aksesibilitas, overlay, atau listener notifikasi | komponen/permission spesifik | kapabilitas deklaratif saja |
| `K03-P01` | package terpasang | identitas package; receiver pemicu boot/package dideklarasikan | komponen service terkait | kapabilitas pemicu; bukan eksekusi |
| `K03-P02` | APK statis | identitas APK; receiver pemicu boot/package dideklarasikan | service/config terkait | desain deklaratif; bukan persistensi yang terjadi |
| `K03-P03` | package terpasang | identitas package; eksekusi akibat pemicu boot/package teramati | deklarasi receiver; fakta K04 terkait | eksekusi terpicu dalam jendela; tidak membuktikan niat |
| `K04-P01` | package terpasang | identitas package; `UsageEvents/UsageStats` menunjukkan penggunaan | UID dan waktu instalasi | penggunaan teramati dalam cakupan retensi |
| `K04-P02` | package terpasang | identitas package; activity teramati `resumed` | UID dan jendela kasus | activity aktif pada saat observasi |
| `K04-P03` | package terpasang | identitas package; process teramati berjalan | UID dan activity snapshot | proses berjalan pada saat observasi; bukan riwayat |
| `K05-P01` | package terpasang | identitas package; pemetaan UID; statistik/delta jaringan UID > 0 | konektivitas; endpoint statis sebagai konteks | aktivitas jaringan UID; bukan endpoint/payload/eksfiltrasi |
| `K05-P02` | simulator validasi | binding skenario–package/UID; request endpoint lokal teramati | netstats dan capture lokal | komunikasi terkendali; tidak digeneralisasi ke malware nyata |
| `K05-P03` | lab terisolasi | identitas package; UID; aktivitas UID; flow lab beririsan waktu | endpoint statis sebagai konteks | koeksistensi teratribusi pada skenario; payload/niat tidak disimpulkan |

`K01-P03`, `K02-P04`, dan `K03-P02` adalah jalur statis untuk S-C. Ketiganya tidak dapat menghasilkan `observed_activity`. `K05-P02` dan `K05-P03` berstatus `validation_only`; keduanya tidak menjadi jalan pintas untuk mengklaim bahwa malware nyata berkomunikasi.

### 14.1.4 Fixture eksklusioner sintetis

Fixture eksklusioner memakai `validation_only: true` dan fakta `synthetic_exclusion_marker_observed`. Ia disuntikkan oleh *fixture adapter* pada katalog pengujian, bukan oleh penormalisasi bukti produksi. Jika `TRUE`, profil yang sebenarnya cocok tetap mencatat fakta/capability, tetapi `interpretation_status` menjadi `constrained` dan temuan diblokir dari rekonstruksi tingkat lebih tinggi. Fixture tidak pernah dipakai untuk memberi label benign pada aplikasi dunia nyata.

## 14.2 YAML lima keluarga APKF — `design_baseline` Generate 1.5

Kelima blok berikut adalah kontrak rancangan awal yang aktif. Mereka menggantikan aturan monolitik §14A. Nilai `version: 1` adalah versi keluarga v3.3, bukan kelanjutan nomor APKF-001–003.

### 14.2.1 `APKF-K01` — Kapabilitas komunikasi sensitif

```yaml
schema_version: "3.3"
rule_family:
  family_id: APKF-K01
  version: 1
  status: design_baseline
  name: sensitive_communication_capability
  incident_scope: apk_fraud_investigation
  reference_ids: [KB-AND-PACKAGE, KB-AND-PERMISSION, KB-MITRE-T1644]
  aggregation: {any_matched: matched, all_not_matched: not_matched, otherwise: insufficient_evidence}
  unknown_handling: {required_unknown: insufficient_evidence, optional_unknown: annotate, contextual_unknown: annotate, exclusionary_unknown: do_not_exclude}
  conflict_handling: {condition_conflict: insufficient_evidence, reason: conflicting_evidence}
  profiles:
    - profile_id: APKF-K01-P01
      name: runtime_sms_capability
      applicability:
        evidence_modes: [installed_runtime]
        run_purposes: [authoring, holdout, benign_control, production]
      claim_level: capability
      subject_binding: [subject_package]
      time_binding: current
      conditions:
        required:
          - {condition_id: C01, fact: package_observed_installed, source_group: APP_SYSTEM_STATE, expects_epistemic_class: identity_attribute, operator: exists, reference_ids: [KB-AND-PACKAGE]}
          - {condition_id: C02, fact: sensitive_communication_capability_observed_granted, source_group: APP_SYSTEM_STATE, expects_epistemic_class: capability_state, operator: in, field: object_value, values: [android.permission.READ_SMS, android.permission.RECEIVE_SMS, android.permission.SEND_SMS], reference_ids: [KB-AND-PERMISSION, KB-MITRE-T1644]}
        optional:
          - {condition_id: C03, fact: permission_observed_requested, source_group: APP_SYSTEM_STATE, expects_epistemic_class: capability_state, operator: in, field: object_value, values: [android.permission.READ_SMS, android.permission.RECEIVE_SMS, android.permission.SEND_SMS], reference_ids: [KB-AND-PERMISSION]}
        contextual:
          - {condition_id: C04, fact: sms_record_observed, source_group: SENSITIVE_COMMUNICATION, expects_epistemic_class: data_present, operator: exists, reference_ids: [KB-MITRE-T1644]}
        exclusionary: []
      output:
        behavior_id: BHV-SENSITIVE-SMS-CAPABILITY
        summary_template: "Package memiliki kapabilitas SMS aktif: {matched_values}."
        limitations: ["Tidak membuktikan SMS telah dibaca, diterima, atau dikirim oleh package."]

    - profile_id: APKF-K01-P02
      name: runtime_contacts_calllog_capability
      applicability:
        evidence_modes: [installed_runtime]
        run_purposes: [authoring, holdout, benign_control, production]
      claim_level: capability
      subject_binding: [subject_package]
      time_binding: current
      conditions:
        required:
          - {condition_id: C01, fact: package_observed_installed, source_group: APP_SYSTEM_STATE, expects_epistemic_class: identity_attribute, operator: exists, reference_ids: [KB-AND-PACKAGE]}
          - {condition_id: C02, fact: sensitive_communication_capability_observed_granted, source_group: APP_SYSTEM_STATE, expects_epistemic_class: capability_state, operator: in, field: object_value, values: [android.permission.READ_CONTACTS, android.permission.READ_CALL_LOG], reference_ids: [KB-AND-PERMISSION]}
        optional:
          - {condition_id: C03, fact: permission_observed_requested, source_group: APP_SYSTEM_STATE, expects_epistemic_class: capability_state, operator: in, field: object_value, values: [android.permission.READ_CONTACTS, android.permission.READ_CALL_LOG], reference_ids: [KB-AND-PERMISSION]}
        contextual:
          - {condition_id: C04, fact: contact_record_observed, source_group: SENSITIVE_COMMUNICATION, expects_epistemic_class: data_present, operator: exists}
          - {condition_id: C05, fact: call_log_record_observed, source_group: SENSITIVE_COMMUNICATION, expects_epistemic_class: data_present, operator: exists}
        exclusionary: []
      output:
        behavior_id: BHV-CONTACT-CALLLOG-CAPABILITY
        summary_template: "Package memiliki kapabilitas data kontak/call-log aktif: {matched_values}."
        limitations: ["Tidak membuktikan data kontak atau call log telah diakses oleh package."]

    - profile_id: APKF-K01-P03
      name: static_sensitive_communication_declaration
      applicability:
        evidence_modes: [apk_static]
        run_purposes: [authoring, production]
      claim_level: capability
      subject_binding: [subject_package, apk_sha256]
      time_binding: not_applicable
      conditions:
        required:
          - {condition_id: C01, fact: apk_identity_observed, source_group: APP_SYSTEM_STATE, expects_epistemic_class: identity_attribute, operator: exists, reference_ids: [KB-AND-PACKAGE]}
          - {condition_id: C02, fact: sensitive_communication_capability_observed_declared, source_group: APP_SYSTEM_STATE, expects_epistemic_class: capability_state, operator: in, field: object_value, values: [android.permission.READ_SMS, android.permission.RECEIVE_SMS, android.permission.SEND_SMS, android.permission.READ_CONTACTS, android.permission.READ_CALL_LOG], reference_ids: [KB-AND-PERMISSION, KB-MITRE-T1644]}
        optional: []
        contextual: []
        exclusionary: []
      output:
        behavior_id: BHV-SENSITIVE-COMMUNICATION-DECLARED
        summary_template: "APK mendeklarasikan kapabilitas komunikasi sensitif: {matched_values}."
        limitations: ["Tidak membuktikan APK dipasang, permission diberikan, atau akses terjadi."]
```

### 14.2.2 `APKF-K02` — Antarmuka istimewa dan akses khusus

```yaml
schema_version: "3.3"
rule_family:
  family_id: APKF-K02
  version: 1
  status: design_baseline
  name: privileged_interface_capability
  incident_scope: apk_fraud_investigation
  reference_ids: [KB-AND-PACKAGE, KB-AND-PERMISSION, KB-AND-ACCESSIBILITY, KB-AND-OVERLAY, KB-AND-NOTIFICATION, KB-AND-USAGE, KB-MITRE-T1417-002, KB-MITRE-T1644]
  aggregation: {any_matched: matched, all_not_matched: not_matched, otherwise: insufficient_evidence}
  unknown_handling: {required_unknown: insufficient_evidence, optional_unknown: annotate, contextual_unknown: annotate, exclusionary_unknown: do_not_exclude}
  conflict_handling: {condition_conflict: insufficient_evidence, reason: conflicting_evidence}
  profiles:
    - profile_id: APKF-K02-P01
      name: accessibility_enabled
      applicability:
        evidence_modes: [installed_runtime]
        run_purposes: [authoring, holdout, benign_control, production]
      claim_level: capability
      subject_binding: [subject_package]
      time_binding: current
      conditions:
        required:
          - {condition_id: C01, fact: package_observed_installed, source_group: APP_SYSTEM_STATE, expects_epistemic_class: identity_attribute, operator: exists, reference_ids: [KB-AND-PACKAGE]}
          - {condition_id: C02, fact: special_access_capability_observed_enabled, source_group: APP_SYSTEM_STATE, expects_epistemic_class: capability_state, operator: equals, field: object_value, value: accessibility_service, reference_ids: [KB-AND-ACCESSIBILITY, KB-MITRE-T1417-002]}
        optional:
          - {condition_id: C03, fact: accessibility_service_observed_declared, source_group: APP_SYSTEM_STATE, expects_epistemic_class: capability_state, operator: exists, reference_ids: [KB-AND-ACCESSIBILITY]}
        contextual:
          - {condition_id: C04, fact: app_usage_observed, source_group: APP_SYSTEM_STATE, expects_epistemic_class: execution_observed, operator: overlaps_window, reference_ids: [KB-AND-USAGE]}
        exclusionary: []
      output:
        behavior_id: BHV-ACCESSIBILITY-CAPABILITY-ACTIVE
        summary_template: "Layanan aksesibilitas milik package teramati aktif."
        limitations: ["Aktif tidak membuktikan penyalahgunaan aksesibilitas."]

    - profile_id: APKF-K02-P02
      name: overlay_enabled
      applicability:
        evidence_modes: [installed_runtime]
        run_purposes: [authoring, holdout, benign_control, production]
      claim_level: capability
      subject_binding: [subject_package]
      time_binding: current
      conditions:
        required:
          - {condition_id: C01, fact: package_observed_installed, source_group: APP_SYSTEM_STATE, expects_epistemic_class: identity_attribute, operator: exists, reference_ids: [KB-AND-PACKAGE]}
          - {condition_id: C02, fact: special_access_capability_observed_enabled, source_group: APP_SYSTEM_STATE, expects_epistemic_class: capability_state, operator: equals, field: object_value, value: draw_over_other_apps, reference_ids: [KB-AND-OVERLAY, KB-MITRE-T1417-002]}
        optional:
          - {condition_id: C03, fact: permission_observed_requested, source_group: APP_SYSTEM_STATE, expects_epistemic_class: capability_state, operator: equals, field: object_value, value: android.permission.SYSTEM_ALERT_WINDOW, reference_ids: [KB-AND-OVERLAY]}
        contextual:
          - {condition_id: C04, fact: app_usage_observed, source_group: APP_SYSTEM_STATE, expects_epistemic_class: execution_observed, operator: overlaps_window, reference_ids: [KB-AND-USAGE]}
        exclusionary: []
      output:
        behavior_id: BHV-OVERLAY-CAPABILITY-ACTIVE
        summary_template: "Package teramati memiliki kemampuan menggambar di atas aplikasi lain."
        limitations: ["Tidak membuktikan overlay ditampilkan atau digunakan untuk phishing."]

    - profile_id: APKF-K02-P03
      name: notification_listener_enabled
      applicability:
        evidence_modes: [installed_runtime]
        run_purposes: [authoring, holdout, benign_control, production]
      claim_level: capability
      subject_binding: [subject_package]
      time_binding: current
      conditions:
        required:
          - {condition_id: C01, fact: package_observed_installed, source_group: APP_SYSTEM_STATE, expects_epistemic_class: identity_attribute, operator: exists, reference_ids: [KB-AND-PACKAGE]}
          - {condition_id: C02, fact: special_access_capability_observed_enabled, source_group: APP_SYSTEM_STATE, expects_epistemic_class: capability_state, operator: equals, field: object_value, value: notification_listener, reference_ids: [KB-AND-NOTIFICATION, KB-MITRE-T1644]}
        optional: []
        contextual:
          - {condition_id: C03, fact: notification_context_observed, source_group: SENSITIVE_COMMUNICATION, expects_epistemic_class: data_present, operator: exists, reference_ids: [KB-AND-NOTIFICATION, KB-MITRE-T1644]}
        exclusionary: []
      output:
        behavior_id: BHV-NOTIFICATION-LISTENER-CAPABILITY-ACTIVE
        summary_template: "Listener notifikasi milik package teramati aktif."
        limitations: ["Tidak membuktikan isi notifikasi dibaca, disimpan, atau disalahgunakan."]

    - profile_id: APKF-K02-P04
      name: static_privileged_interface_declaration
      applicability:
        evidence_modes: [apk_static]
        run_purposes: [authoring, production]
      claim_level: capability
      subject_binding: [subject_package, apk_sha256]
      time_binding: not_applicable
      conditions:
        required:
          - {condition_id: C01, fact: apk_identity_observed, source_group: APP_SYSTEM_STATE, expects_epistemic_class: identity_attribute, operator: exists, reference_ids: [KB-AND-PACKAGE]}
          - {condition_id: C02, fact: special_access_capability_observed_declared, source_group: APP_SYSTEM_STATE, expects_epistemic_class: capability_state, operator: in, field: object_value, values: [accessibility_service, draw_over_other_apps, notification_listener], reference_ids: [KB-AND-ACCESSIBILITY, KB-AND-OVERLAY, KB-AND-NOTIFICATION]}
        optional: []
        contextual: []
        exclusionary: []
      output:
        behavior_id: BHV-PRIVILEGED-INTERFACE-DECLARED
        summary_template: "APK mendeklarasikan antarmuka/akses khusus: {matched_values}."
        limitations: ["Tidak membuktikan APK dipasang, akses diaktifkan, atau antarmuka digunakan."]
```

### 14.2.3 `APKF-K03` — Persistensi atau eksekusi terpicu peristiwa

```yaml
schema_version: "3.3"
rule_family:
  family_id: APKF-K03
  version: 1
  status: design_baseline
  name: event_triggered_persistence_execution
  incident_scope: apk_fraud_investigation
  reference_ids: [KB-AND-PACKAGE, KB-AND-BROADCAST, KB-AND-USAGE, KB-MITRE-T1624]
  aggregation: {any_matched: matched, all_not_matched: not_matched, otherwise: insufficient_evidence}
  unknown_handling: {required_unknown: insufficient_evidence, optional_unknown: annotate, contextual_unknown: annotate, exclusionary_unknown: do_not_exclude}
  conflict_handling: {condition_conflict: insufficient_evidence, reason: conflicting_evidence}
  profiles:
    - profile_id: APKF-K03-P01
      name: installed_event_trigger_declaration
      applicability:
        evidence_modes: [installed_runtime]
        run_purposes: [authoring, holdout, benign_control, production]
      claim_level: capability
      subject_binding: [subject_package]
      time_binding: current
      conditions:
        required:
          - {condition_id: C01, fact: package_observed_installed, source_group: APP_SYSTEM_STATE, expects_epistemic_class: identity_attribute, operator: exists, reference_ids: [KB-AND-PACKAGE]}
          - {condition_id: C02, fact: event_trigger_capability_observed_declared, source_group: APP_SYSTEM_STATE, expects_epistemic_class: capability_state, operator: in, field: object_value, values: [android.intent.action.BOOT_COMPLETED, android.intent.action.LOCKED_BOOT_COMPLETED, android.intent.action.PACKAGE_ADDED, android.intent.action.PACKAGE_REPLACED], reference_ids: [KB-AND-BROADCAST, KB-MITRE-T1624]}
        optional:
          - {condition_id: C03, fact: service_observed_declared, source_group: APP_SYSTEM_STATE, expects_epistemic_class: capability_state, operator: exists}
        contextual: []
        exclusionary: []
      output:
        behavior_id: BHV-EVENT-TRIGGER-CAPABILITY-DECLARED
        summary_template: "Package mendeklarasikan pemicu peristiwa: {matched_values}."
        limitations: ["Deklarasi receiver tidak membuktikan receiver pernah dipicu atau menghasilkan persistensi."]

    - profile_id: APKF-K03-P02
      name: static_event_trigger_declaration
      applicability:
        evidence_modes: [apk_static]
        run_purposes: [authoring, production]
      claim_level: capability
      subject_binding: [subject_package, apk_sha256]
      time_binding: not_applicable
      conditions:
        required:
          - {condition_id: C01, fact: apk_identity_observed, source_group: APP_SYSTEM_STATE, expects_epistemic_class: identity_attribute, operator: exists, reference_ids: [KB-AND-PACKAGE]}
          - {condition_id: C02, fact: event_trigger_capability_observed_declared, source_group: APP_SYSTEM_STATE, expects_epistemic_class: capability_state, operator: in, field: object_value, values: [android.intent.action.BOOT_COMPLETED, android.intent.action.LOCKED_BOOT_COMPLETED, android.intent.action.PACKAGE_ADDED, android.intent.action.PACKAGE_REPLACED], reference_ids: [KB-AND-BROADCAST, KB-MITRE-T1624]}
        optional:
          - {condition_id: C03, fact: service_observed_declared, source_group: APP_SYSTEM_STATE, expects_epistemic_class: capability_state, operator: exists}
        contextual: []
        exclusionary: []
      output:
        behavior_id: BHV-STATIC-EVENT-TRIGGER-DECLARED
        summary_template: "APK mendeklarasikan pemicu peristiwa: {matched_values}."
        limitations: ["Tidak membuktikan APK dipasang, receiver dipicu, atau proses berjalan."]

    - profile_id: APKF-K03-P03
      name: event_trigger_execution_observed
      applicability:
        evidence_modes: [installed_runtime]
        run_purposes: [authoring, holdout, benign_control, production]
      claim_level: observed_activity
      subject_binding: [subject_package]
      time_binding: case_window
      conditions:
        required:
          - {condition_id: C01, fact: package_observed_installed, source_group: APP_SYSTEM_STATE, expects_epistemic_class: identity_attribute, operator: exists, reference_ids: [KB-AND-PACKAGE]}
          - {condition_id: C02, fact: event_trigger_execution_observed, source_group: APP_SYSTEM_STATE, expects_epistemic_class: execution_observed, operator: overlaps_window, reference_ids: [KB-AND-BROADCAST, KB-MITRE-T1624]}
        optional:
          - {condition_id: C03, fact: event_trigger_capability_observed_declared, source_group: APP_SYSTEM_STATE, expects_epistemic_class: capability_state, operator: exists, reference_ids: [KB-AND-BROADCAST]}
        contextual:
          - {condition_id: C04, fact: app_usage_observed, source_group: APP_SYSTEM_STATE, expects_epistemic_class: execution_observed, operator: overlaps_window, reference_ids: [KB-AND-USAGE]}
        exclusionary: []
      output:
        behavior_id: BHV-EVENT-TRIGGERED-EXECUTION-OBSERVED
        summary_template: "Eksekusi package teramati setelah pemicu: {object_value}."
        limitations: ["Menunjukkan hubungan waktu/pemicu yang teramati, bukan niat atau tindakan penipuan."]
```

### 14.2.4 `APKF-K04` — Eksekusi package relevan teramati

```yaml
schema_version: "3.3"
rule_family:
  family_id: APKF-K04
  version: 1
  status: design_baseline
  name: package_execution_observed
  incident_scope: apk_fraud_investigation
  reference_ids: [KB-AND-PACKAGE, KB-AND-USAGE]
  aggregation: {any_matched: matched, all_not_matched: not_matched, otherwise: insufficient_evidence}
  unknown_handling: {required_unknown: insufficient_evidence, optional_unknown: annotate, contextual_unknown: annotate, exclusionary_unknown: do_not_exclude}
  conflict_handling: {condition_conflict: insufficient_evidence, reason: conflicting_evidence}
  profiles:
    - profile_id: APKF-K04-P01
      name: usage_history_execution
      applicability:
        evidence_modes: [installed_runtime]
        run_purposes: [authoring, holdout, benign_control, production]
      claim_level: observed_activity
      subject_binding: [subject_package]
      time_binding: case_window
      conditions:
        required:
          - {condition_id: C01, fact: package_observed_installed, source_group: APP_SYSTEM_STATE, expects_epistemic_class: identity_attribute, operator: exists, reference_ids: [KB-AND-PACKAGE]}
          - {condition_id: C02, fact: app_usage_observed, source_group: APP_SYSTEM_STATE, expects_epistemic_class: execution_observed, operator: overlaps_window, reference_ids: [KB-AND-USAGE]}
        optional:
          - {condition_id: C03, fact: uid_observed, source_group: APP_SYSTEM_STATE, expects_epistemic_class: identity_attribute, operator: exists, reference_ids: [KB-AND-PACKAGE]}
        contextual: []
        exclusionary: []
      output:
        behavior_id: BHV-PACKAGE-USAGE-OBSERVED
        summary_template: "Penggunaan package teramati dalam jendela analisis."
        limitations: ["Ketepatan waktu dibatasi retensi dan granularitas sumber UsageStats/UsageEvents."]

    - profile_id: APKF-K04-P02
      name: resumed_activity_snapshot
      applicability:
        evidence_modes: [installed_runtime]
        run_purposes: [authoring, holdout, benign_control, production]
      claim_level: observed_activity
      subject_binding: [subject_package]
      time_binding: observation_time
      conditions:
        required:
          - {condition_id: C01, fact: package_observed_installed, source_group: APP_SYSTEM_STATE, expects_epistemic_class: identity_attribute, operator: exists, reference_ids: [KB-AND-PACKAGE]}
          - {condition_id: C02, fact: activity_observed_resumed, source_group: APP_SYSTEM_STATE, expects_epistemic_class: execution_observed, operator: exists}
        optional:
          - {condition_id: C03, fact: uid_observed, source_group: APP_SYSTEM_STATE, expects_epistemic_class: identity_attribute, operator: exists}
        contextual: []
        exclusionary: []
      output:
        behavior_id: BHV-ACTIVITY-RESUMED-OBSERVED
        summary_template: "Activity package teramati aktif saat observasi."
        limitations: ["Snapshot tidak membuktikan riwayat eksekusi sebelum waktu observasi."]

    - profile_id: APKF-K04-P03
      name: running_process_snapshot
      applicability:
        evidence_modes: [installed_runtime]
        run_purposes: [authoring, holdout, benign_control, production]
      claim_level: observed_activity
      subject_binding: [subject_package, subject_uid]
      time_binding: observation_time
      conditions:
        required:
          - {condition_id: C01, fact: package_observed_installed, source_group: APP_SYSTEM_STATE, expects_epistemic_class: identity_attribute, operator: exists, reference_ids: [KB-AND-PACKAGE]}
          - {condition_id: C02, fact: process_observed_running, source_group: APP_SYSTEM_STATE, expects_epistemic_class: execution_observed, operator: exists}
        optional:
          - {condition_id: C03, fact: activity_observed_resumed, source_group: APP_SYSTEM_STATE, expects_epistemic_class: execution_observed, operator: exists}
        contextual: []
        exclusionary: []
      output:
        behavior_id: BHV-PROCESS-RUNNING-OBSERVED
        summary_template: "Proses package/UID teramati berjalan saat observasi."
        limitations: ["Snapshot tidak menjelaskan pemicu, durasi, atau tindakan yang dilakukan proses."]
```

### 14.2.5 `APKF-K05` — Aktivitas jaringan terkait UID/package

```yaml
schema_version: "3.3"
rule_family:
  family_id: APKF-K05
  version: 1
  status: design_baseline
  name: uid_package_network_activity
  incident_scope: apk_fraud_investigation
  reference_ids: [KB-AND-PACKAGE, KB-AND-NETWORK]
  aggregation: {any_matched: matched, all_not_matched: not_matched, otherwise: insufficient_evidence}
  unknown_handling: {required_unknown: insufficient_evidence, optional_unknown: annotate, contextual_unknown: annotate, exclusionary_unknown: do_not_exclude}
  conflict_handling: {condition_conflict: insufficient_evidence, reason: conflicting_evidence}
  profiles:
    - profile_id: APKF-K05-P01
      name: uid_network_statistics
      applicability:
        evidence_modes: [installed_runtime]
        run_purposes: [authoring, holdout, benign_control, production]
      claim_level: observed_activity
      subject_binding: [subject_package, subject_uid]
      time_binding: bucket_overlap
      conditions:
        required:
          - {condition_id: C01, fact: package_observed_installed, source_group: APP_SYSTEM_STATE, expects_epistemic_class: identity_attribute, operator: exists, reference_ids: [KB-AND-PACKAGE]}
          - {condition_id: C02, fact: uid_observed, source_group: APP_SYSTEM_STATE, expects_epistemic_class: identity_attribute, operator: exists, reference_ids: [KB-AND-PACKAGE]}
          - {condition_id: C03, fact: uid_network_activity_observed, source_group: NETWORK_ACTIVITY, expects_epistemic_class: execution_observed, operator: greater_than, field: context_json.total_bytes, value: 0, reference_ids: [KB-AND-NETWORK]}
        optional:
          - {condition_id: C04, fact: uid_network_activity_observed, source_group: NETWORK_ACTIVITY, expects_epistemic_class: execution_observed, operator: delta_greater_than, field: context_json.total_bytes, value: 0, reference_ids: [KB-AND-NETWORK]}
        contextual:
          - {condition_id: C05, fact: apk_endpoint_reference_observed, source_group: APP_SYSTEM_STATE, expects_epistemic_class: identity_attribute, operator: exists}
        exclusionary: []
      output:
        behavior_id: BHV-UID-NETWORK-ACTIVITY-OBSERVED
        summary_template: "Aktivitas jaringan teramati pada UID yang dipetakan ke package."
        limitations: ["Tidak membuktikan endpoint, payload, tujuan komunikasi, atau eksfiltrasi."]

    - profile_id: APKF-K05-P02
      name: controlled_local_endpoint_request
      applicability:
        evidence_modes: [installed_runtime]
        run_purposes: [authoring, holdout]
      validation_only: true
      claim_level: observed_activity
      subject_binding: [scenario_id, subject_package, subject_uid]
      time_binding: case_window
      conditions:
        required:
          - {condition_id: C01, fact: scenario_subject_binding_observed, source_group: APP_SYSTEM_STATE, expects_epistemic_class: identity_attribute, operator: exists}
          - {condition_id: C02, fact: local_endpoint_request_observed, source_group: NETWORK_ACTIVITY, expects_epistemic_class: execution_observed, operator: overlaps_window}
        optional:
          - {condition_id: C03, fact: uid_network_activity_observed, source_group: NETWORK_ACTIVITY, expects_epistemic_class: execution_observed, operator: overlaps_window, reference_ids: [KB-AND-NETWORK]}
        contextual: []
        exclusionary: []
      output:
        behavior_id: BHV-CONTROLLED-LOCAL-COMMUNICATION-OBSERVED
        summary_template: "Simulator melakukan komunikasi terkendali ke endpoint lokal."
        limitations: ["Keluaran hanya oracle validasi dan tidak digeneralisasi ke APK malware nyata."]

    - profile_id: APKF-K05-P03
      name: attributed_lab_flow_cooccurrence
      applicability:
        evidence_modes: [installed_runtime]
        run_purposes: [authoring, holdout, benign_control]
      validation_only: true
      claim_level: contextual_cooccurrence
      subject_binding: [scenario_id, subject_package, subject_uid]
      time_binding: case_window
      conditions:
        required:
          - {condition_id: C01, fact: scenario_subject_binding_observed, source_group: APP_SYSTEM_STATE, expects_epistemic_class: identity_attribute, operator: exists}
          - {condition_id: C02, fact: uid_network_activity_observed, source_group: NETWORK_ACTIVITY, expects_epistemic_class: execution_observed, operator: overlaps_window, reference_ids: [KB-AND-NETWORK]}
          - {condition_id: C03, fact: lab_network_flow_observed, source_group: NETWORK_ACTIVITY, expects_epistemic_class: execution_observed, operator: overlaps_window}
        optional: []
        contextual:
          - {condition_id: C04, fact: apk_endpoint_reference_observed, source_group: APP_SYSTEM_STATE, expects_epistemic_class: identity_attribute, operator: exists}
        exclusionary: []
      output:
        behavior_id: BHV-LAB-NETWORK-COOCCURRENCE
        summary_template: "Aktivitas UID dan flow lab berkoeksistensi pada skenario/jendela yang sama."
        limitations: ["Koeksistensi tidak membuktikan payload, niat, atau eksfiltrasi; atribusi dibatasi pada skenario terkontrol."]
```

## 14.3 Batas perubahan saat *authoring* dan titik final

Status `design_baseline` berarti desain sudah cukup lengkap untuk diagram dan BAB III, tetapi belum merupakan hasil empiris. Saat *authoring*, perubahan tanpa amandemen core hanya boleh menyentuh:

- jalur parser/operasi akuisisi setelah Tier-2;
- nama field dalam `context_json` yang tidak mengubah makna fakta;
- batas waktu yang memang dinyatakan `case_configured`;
- penambahan profil ekuivalen untuk sumber artefak yang lolos Tier-2;
- koreksi teknis yang tidak menaikkan `claim_level`.

Perubahan terhadap keluarga, arti profil, fakta wajib, kelas epistemik, peran kondisi, agregasi, batas klaim, efek eksklusioner, atau gerbang rekonstruksi **wajib membuka core dan dicatat sebelum holdout**.

Setelah 20 kasus *authoring* selesai, versi final setiap YAML dinaikkan, seluruh `reference_ids` diverifikasi, lalu hash YAML, pemetaan normalisasi, KB, kode, dan konfigurasi dicatat dalam manifest pembekuan. Hanya artefak beku tersebut yang boleh digunakan pada delapan bundel *holdout*.

Siklus status yang sah adalah `design_baseline` → `authoring_candidate` → `frozen_for_holdout`. Status pertama adalah kontrak desain yang ditulis di BAB III; status terakhir baru tersedia setelah implementasi dan *authoring*, kemudian dilaporkan sebagai realisasi metode/hasil di BAB IV. Kegagalan *holdout* tidak mengembalikan status ke *authoring_candidate* untuk putaran pengujian yang sama.

## 14A. `[ARSIP v3.2]` Tiga contoh aturan lama

Tiga blok berikut dipertahankan hanya sebagai riwayat migrasi dan **tidak mengendalikan implementasi v3.3**. ID aktif memakai keluarga/profil §14.1, sedangkan kontrak YAML awal yang lengkap berada di §14.2. Hasil *authoring* hanya boleh memutakhirkan rincian yang diizinkan §14.3 dan harus dibekukan sebagai artefak YAML berversi di repositori penelitian.

---

## APKF-001 — SMS Access Capability

```yaml
rule:
  id: APKF-001
  version: 3
  status: draft
  name: sms_access_capability
  incident_scope: apk_fraud
  reference_ids:
    - KB-SRC-APKF-001-01

  conditions:
    required:
      - fact: PACKAGE_INSTALLED
        source_group: APP_SYSTEM_STATE
        expects_epistemic_class: identity_attribute
      - fact: PERMISSION_REQUESTED
        value: READ_SMS
        source_group: APP_SYSTEM_STATE
        expects_epistemic_class: capability_state
      - fact: PERMISSION_GRANTED
        value: READ_SMS
        source_group: APP_SYSTEM_STATE
        expects_epistemic_class: capability_state

    optional:
      - fact: SMS_DATA_PRESENT
        source_group: SENSITIVE_COMMUNICATION
        expects_epistemic_class: data_present
        note: "Sensitive-data context only; not proof package accessed the SMS."
      - fact: EXECUTION_EVENT_RELEVANT_WINDOW
        source_group: APP_SYSTEM_STATE
        expects_epistemic_class: execution_observed
      - fact: NETWORK_ACTIVITY_RELEVANT_WINDOW
        source_group: NETWORK_ACTIVITY
        expects_epistemic_class: execution_observed

    exclusionary: []

  unknown_handling:
    required_unknown: insufficient_evidence
    optional_unknown: annotate
    exclusionary_unknown: do_not_exclude

  correlation:
    subject_key: package_name
    max_time_window: configurable

  output:
    behavior_id: BHV-SMS-ACCESS-CAPABILITY
    match_states: [matched, not_matched, insufficient_evidence]
    hypothesis_hint: >
      Evidence supports that the installed package currently possesses
      READ_SMS capability. Optional evidence may strengthen incident context,
      but does not prove a specific SMS was read, collected, or transmitted.

```

Important:
> Legitimate SMS app boleh match low-level capability rule ini. Malicious/benign interpretation ada di higher-level correlation/hypothesis.

---

## APKF-002 — Accessibility Capability Active

```yaml
rule:
  id: APKF-002
  version: 3
  status: draft
  name: accessibility_capability_active
  incident_scope: apk_fraud
  reference_ids:
    - KB-SRC-APKF-002-01

  conditions:
    required:
      - fact: ACCESSIBILITY_SERVICE_DECLARED
        source_group: APP_SYSTEM_STATE
        expects_epistemic_class: capability_state
      - fact: ACCESSIBILITY_SERVICE_ENABLED
        source_group: APP_SYSTEM_STATE
        expects_epistemic_class: capability_state

    optional:
      - fact: OVERLAY_PERMISSION_ACTIVE
        source_group: APP_SYSTEM_STATE
        expects_epistemic_class: capability_state
      - fact: NETWORK_ACTIVITY_RELEVANT_WINDOW
        source_group: NETWORK_ACTIVITY
        expects_epistemic_class: execution_observed

    exclusionary: []

  unknown_handling:
    required_unknown: insufficient_evidence
    optional_unknown: annotate
    exclusionary_unknown: do_not_exclude

  correlation:
    subject_key: package_name
    max_time_window: null

  output:
    behavior_id: BHV-ACCESSIBILITY-CAPABILITY-ACTIVE
    match_states: [matched, not_matched, insufficient_evidence]
    hypothesis_hint: >
      Evidence supports that the package declares and currently has
      an enabled Accessibility Service. This establishes capability/state,
      not keylogging, input injection, credential theft, or abuse.

```

---

## APKF-003 — Post-Install Network Activity

```yaml
rule:
  id: APKF-003
  version: 3
  status: draft
  name: post_install_network_activity
  incident_scope: apk_fraud
  reference_ids:
    - KB-SRC-APKF-003-01

  conditions:
    required:
      - fact: PACKAGE_INSTALLED_RELEVANT_WINDOW
        source_group: APP_SYSTEM_STATE
        expects_epistemic_class: identity_attribute
      - fact: PACKAGE_UID_MAPPING_AVAILABLE
        source_group: APP_SYSTEM_STATE
        expects_epistemic_class: identity_attribute
      - fact: NETWORK_ACTIVITY_OBSERVED
        source_group: NETWORK_ACTIVITY
        expects_epistemic_class: execution_observed

    optional:
      - fact: SENSITIVE_PERMISSION_PRESENT
        source_group: APP_SYSTEM_STATE
        expects_epistemic_class: capability_state
      - fact: SENSITIVE_COMMUNICATION_CONTEXT_PRESENT
        source_group: SENSITIVE_COMMUNICATION
        expects_epistemic_class: data_present

    exclusionary: []

  unknown_handling:
    required_unknown: insufficient_evidence
    optional_unknown: annotate
    exclusionary_unknown: do_not_exclude

  correlation:
    subject_key: package_name
    secondary_key: uid
    max_time_window: configurable

  output:
    behavior_id: BHV-NETWORK-ACTIVITY-POST-INSTALL
    match_states: [matched, not_matched, insufficient_evidence]
    hypothesis_hint: >
      Evidence supports that a relevant installed package/UID has observable
      network activity within the analysis window. This does not establish
      destination endpoint, transmitted payload, or exfiltration.

```

`INTERNET` permission sengaja tidak dipakai sebagai strong suspicious required condition.

---

# 15. VALIDATION DESIGN — 🔒 v3.3

Validasi dipisahkan menjadi tiga objek: (1) fakta dan kondisi; (2) profil/keluarga APKF; dan (3) rekonstruksi/hipotesis. Istilah **akurasi** hanya boleh dipakai sebagai kesesuaian pada skenario terkendali dengan oracle yang diketahui, bukan akurasi deteksi APK penipuan pada populasi.

| Objek | Yang diperiksa | Dasar pembanding |
|---|---|---|
| Fakta/kondisi | nilai TRUE/FALSE/UNKNOWN, kelas epistemik, alasan, dan fakta penopang | `ground_truth.json` dan keluaran akuisisi |
| Profil/keluarga | keluaran profil, agregasi keluarga, konflik, dan batas klaim | vektor keluaran yang disegel |
| Rekonstruksi | keberadaan yang tepat, urutan yang didukung, bukti hilang, keterlacakan, dan tanpa lompatan klaim | oracle skenario + relasi package/UID/waktu |

## 15.1 Kelas skenario

| Kelas | Susunan | Keluaran yang diharapkan |
|---|---|---|
| **A — positif** | fakta wajib tersedia dan benar | `matched` pada profil sasaran |
| **B — *near-miss*** | sedikitnya satu fakta wajib tersedia tetapi salah | `not_matched` |
| **C — benign/kontrol** | kapabilitas atau aktivitas faktual ada pada aplikasi sah | temuan tingkat rendah boleh ada; tidak ada label penipuan/penyalahgunaan otomatis |
| **D1 — opsional hilang** | fakta wajib benar, fakta opsional tidak tersedia | `matched` dengan anotasi bukti tidak teramati |
| **D2 — wajib tidak diketahui** | tidak ada wajib salah, sedikitnya satu wajib `UNKNOWN` | `insufficient_evidence` |
| **E — konflik** | dua fakta relevan yang sah saling bertentangan | kondisi `UNKNOWN/conflicting_evidence`; konflik tertelusur |
| **F — eksklusioner** | fakta eksklusioner sintetis benar atau tidak tersedia | interpretasi tertahan bila benar; `UNKNOWN` tidak dianggap pengecualian |

Kelas di atas adalah dimensi cakupan, bukan produk Kartesius yang wajib dijalankan untuk setiap profil.

## 15.2 Katalog *authoring* dan *holdout*

- **Authoring minimum 20 kasus inti:** empat kasus per keluarga APKF yang mencakup positif, salah/near-miss, tidak diketahui, dan benign atau batas klaim.
- Fixture konflik dan eksklusioner **ditanamkan ke katalog 20 kasus**, sekurang-kurangnya masing-masing dua kasus lintas keluarga; tidak menambah keluarga baru.
- D1 opsional-hilang wajib muncul pada sekurang-kurangnya satu profil di tiap peran bukti opsional yang digunakan.
- **Holdout target delapan bundel bukti**, masing-masing membawa vektor keluaran untuk kelima keluarga. Bundel tidak dipakai memperbaiki pengurai, skema, aturan, basis pengetahuan, atau konfigurasi.

Kriteria dan vektor keluaran holdout disegel sebelum pembekuan. Perubahan setelah holdout dibuka membatalkan status holdout untuk versi tersebut.

## 15.3 Pembagian sampel dalam validasi

| Sasaran | S-A simulator | S-B benign/kontrol | S-C malware nyata statis |
|---|---|---|---|
| kondisi dan keluarga APKF | utama | anti-klaim-berlebih | relevansi profil statis saja |
| TRUE/FALSE/UNKNOWN/konflik | penuh | terbatas pada fakta yang tersedia | tidak dipaksakan untuk runtime |
| rekonstruksi dinamis | ya | hanya skenario kontrol | tidak |
| generalisasi malware | tidak | tidak | tidak |

Hasil pada S-C hanya menyatakan apakah artefak statis yang ditemukan dapat dipetakan ke profil kapabilitas/identitas yang relevan. Tidak ada klaim bahwa perilaku runtime telah terjadi.

## 15.4 Kriteria kelulusan

Setiap kasus dilaporkan sendiri. Tidak ada skor agregat lintas kelas. Lulus bila: kondisi sesuai oracle; agregasi profil/keluarga benar; `UNKNOWN` dan konflik ditangani sesuai kontrak; temuan mempunyai tingkat klaim yang benar; seluruh jalur bukti–aturan–rujukan dapat ditelusuri; dan rekonstruksi tidak mengisi tahap yang tidak didukung.

> `[ARSIP v3.2]` Rancangan 16 *authoring* + 6 *holdout* untuk APKF-001–003 disupersesi oleh portofolio lima keluarga dan katalog di atas.

---

# 16. AUTHORING VS HOLDOUT

## Authoring/development set
Boleh digunakan untuk:
- parser debugging;
- event schema validation;
- rule condition refinement;
- penajaman kondisi aturan.

> `[ARSIP v2.4.1]` ~~threshold tuning bila scoring digunakan~~ — dicabut bersama D-6.

## Freeze point
Setelah evidence semantics + Tier-2 feasibility + rule definition stabil.

> ⭐ **`[v3.0]` Urutan pembekuan yang mengikat.**
>
> ```text
> rancang protokol + segel kriteria holdout
>   → authoring (minimum 20 kasus lintas lima keluarga)
>     → PEMBEKUAN: pengurai, skema, aturan, KB, konfigurasi, kode
>       → bangun dan akuisisi bukti holdout
>         → baseline analisis manual dicatat dan disegel
>           → analisis otomatis holdout
>             → pengulangan uji konsistensi
>               → perbandingan dan pelaporan
> ```
>
> ⭐ **Baseline manual diselesaikan dan disegel sebelum keluaran otomatis dilihat.** Peneliti yang melakukan analisis manual setelah melihat keluaran platform akan terjangkar padanya. Pembutaan sempurna mustahil bagi peneliti tunggal, tetapi urutan ini adalah pembutaan terbaik yang dapat dicapai, dan ongkosnya nyaris nol.

## Holdout
Tidak boleh dipakai untuk tuning.

> ⛔ ⭐ **`[v3.0]` Aturan pasca-pembekuan — mengikat.**
>
> **Temuan *holdout* yang tidak sesuai adalah HASIL, dan tempatnya BAB IV.** Ia **bukan** alasan mengubah aturan, pengurai, skema, atau basis pengetahuan sampai semuanya lulus.
>
> Aturan ini ada karena tanpa dirinya pembekuan hanyalah jeda sebelum putaran berikutnya — kali ini dipicu hasil, bukan audit. Ketidaksesuaian yang dilaporkan apa adanya adalah temuan penelitian yang sah dan sering lebih informatif daripada kelulusan penuh; ketidaksesuaian yang dihapus dengan menyetel ulang sistem adalah kehilangan data.
>
> Bila perubahan tetap dinilai perlu, ia dilakukan **secara eksplisit sebagai versi baru**, dan seluruh kasus *holdout* kehilangan statusnya untuk versi tersebut.

Jika rule diubah setelah melihat holdout:
> kasus tersebut tidak lagi valid sebagai holdout untuk versi rule baru.

`ground_truth.json` minimal:
- `scenario_id`, kategori sampel, varian, dan status authoring/holdout;
- package, versi APK, SHA-256, versi aturan/KB/kode/konfigurasi;
- Android/device/AVD dan keadaan awal;
- aksi terkendali beserta cap waktunya;
- artefak, fakta, dan predikat yang diharapkan;
- keadaan kondisi serta keluaran profil/keluarga yang diharapkan;
- batas klaim, fakta eksklusioner, konflik, dan bukti yang sengaja dibuat tidak tersedia;
- referensi bukti mentah dan catatan penyimpangan aktual.

---

# 17. RESEARCH QUESTIONS — PENUNJUK

> ⛔ **Dokumen ini tidak lagi memuat rumusan RQ.**
>
> Rumusan masalah final berada pada **naskah BAB I** (`BAB_01_DRAFT_FINAL`), dengan catatan kerjanya di `BAB_01_WORKING` §12. Status: `FINAL`, dalam *working-freeze*.
>
> Untuk urusan RQ, naskah BAB I **menang atas dokumen ini**. Lihat urutan otoritas pada `00_SESSION_STARTER` §0.

**Perubahan RQ hanya dibahas bila:** muncul paper yang membatalkan celah penelitian · terbukti satu sumber evidence tidak layak · ketidaksesuaian RQ dengan rencana evaluasi · kontradiksi dengan literatur · permintaan pembimbing. Prosesnya: temuan → analisis dampak → opsi revisi → keputusan → sinkronisasi lintas bab.

> `[ARSIP v2.4]` **Rumusan lama (WORKING DRAFT v2.3) dicabut.** Versi lama menyimpang dari naskah final pada dua hal yang bukan kosmetik:
> 1. RQ3 lama memuat dimensi ***efficiency*** dan berbentuk **klaim komparatif** (*"meningkatkan … dibanding baseline analisis manual"*). Naskah final tidak memuat keduanya di dalam RQ; perbandingan terhadap baseline manual tetap ada, tetapi sebagai **metode evaluasi** (§18.4), bukan sebagai klaim di dalam rumusan masalah.
> 2. RQ3 lama tidak memuat dimensi **kemampuan menangani bukti yang tidak teramati** — yang justru merupakan inti kebaruan penelitian.
>
> Membiarkan dua versi RQ beredar berisiko membuat BAB III ditulis di atas rumusan yang salah.

---

# 18. EVALUATION

## 18.1 Ketepatan aturan dan korelasi — 🔒 `D-7` *(diputuskan 1 Sep 2026)*

**Keputusan: metrik klasifikasi dicabut, diganti penilaian kesesuaian per kelas skenario.**

```text
Untuk tiap skenario (§15 kelas A / B / C / D1 / D2 / E / F):
  keluaran aturan yang diharapkan  vs  keluaran aturan yang diamati
  → sesuai / tidak sesuai

Dilaporkan PER KELAS skenario, bukan sebagai satu angka tunggal.
Kelas D1, D2, E, dan F dilaporkan TERPISAH — di situlah penanganan
bukti tidak teramati, konflik, dan pengecualian diuji.
```

### 18.1.0 Alasan pencabutan *(diperbaiki v2.6)*

> `[KOREKSI v2.6]` Alasan v2.4.1 berbunyi *"empat-empatnya turunan confusion matrix, karena itu bertentangan dengan K-07"*. **Terlalu mutlak.** Sistem deterministik **tetap dapat** diukur dengan metrik klasifikasi bila unit prediksi dan keadaan sebenarnya terdefinisi jelas. Kesimpulannya berdiri, argumennya diganti.

1. **Platform ini bukan klasifikator biner** berbahaya/tidak berbahaya — naskah BAB I Batasan #4 dan BAB II 2.3.
2. **Objek evaluasinya kesesuaian keluaran aturan tiga keadaan**, bukan ketepatan penggolongan dua kelas.
3. **Kelas skenario A/B/C/D1/D2/E/F berfungsi berbeda**; menggabungkannya jadi satu metrik menghilangkan makna tiap kelas.
4. **Satu angka agregat menyembunyikan kegagalan pada D1, D2, E, dan F**, padahal di situlah penanganan bukti tidak teramati, konflik, dan pengecualian diuji.

Dukungan normatif tetap: naskah BAB II 2.1.14 dan **K-07**.

### 18.1.2 ⚠️ `insufficient-evidence rate` — tidak otomatis aman *(baru v2.6)*

> `[KOREKSI v2.6]` v2.4.1 menyatakannya *"tetap sah"* tanpa syarat. **Kurang tepat.** Pada skenario terkendali, jumlah kasus D2 **ditentukan peneliti**, sehingga rasionya dapat sekadar mencerminkan komposisi skenario — bukan kinerja sistem.

| # | Syarat pemakaian |
|---|---|
| 1 | Kesesuaian **D1 dan D2 dilaporkan terpisah**, tidak pernah digabung |
| 2 | Bila dinyatakan persentase, **penyebutnya didefinisikan eksplisit** |
| 3 | Diposisikan sebagai **statistik deskriptif**, bukan bukti kinerja umum |
| 4 | Naskah wajib menyatakan komposisi skenario ditentukan peneliti |

> `[ARSIP v2.3]` Metrik lama — `precision` · `recall` · `F1` · `false-positive rate` — dicabut. Empat-empatnya turunan langsung *confusion matrix*, bertentangan dengan **K-07** dan dengan kalimat yang **sudah terbit** pada naskah BAB II 2.1.14: *"metrik yang mengandaikan kesalahan acak tidak digunakan sejalan dengan sifat prosedural mekanisme yang diuji."*

### 18.1.1 ⭐ Syarat kerealistisan — `SYARAT-D7` *(catatan Marco)*

> **Persoalan yang diangkat:** pengujian harus menggambarkan kejadian nyata, sehingga bila kelak diuji dengan sampel sungguhan hasilnya tetap sahih.

Persoalan itu **sah, tetapi memuat dua hal berbeda** yang harus dipisah karena nasibnya tidak sama.

**(a) Kerealistisan skenario — dapat dipenuhi, dan wajib.**

Skenario tidak boleh dikarang. Tiap kelas skenario §15 wajib diturunkan dari **perilaku APK penipuan yang terdokumentasi** pada sumber basis pengetahuan (§12), bukan dari perilaku yang dibayangkan peneliti. Konsekuensi yang mengikat:

| Wajib | Isi |
|---|---|
| Asal skenario | Tiap skenario menyebut rujukan perilaku yang ditirunya |
| Ketertelusuran | Skenario → perilaku terdokumentasi → rujukan. Sejalur dengan keterlacakan aturan → rujukan |
| Larangan | Skenario yang tidak punya padanan terdokumentasi tidak boleh dipakai untuk mengklaim ketepatan |

Ini juga memperkuat §12: aturan **dan** skenario sama-sama bersandar pada rujukan.

**(b) Keberlakuan pada sampel sungguhan — tidak dapat dijanjikan, dan sudah dibatasi di naskah.**

Ini **validitas eksternal**, dan naskah BAB I Batasan #5 sudah menyatakan hasil **tidak digeneralisasi** ke luar lingkungan pengujian. Janji "hasilnya tetap sahih pada sampel sungguhan" **tidak boleh** ditulis di BAB III — itu klaim yang melampaui rancangan penelitian, dan justru jenis lompatan yang penelitian ini kritik pada pendekatan terdahulu.

Alasan teknisnya, bukan sekadar formalitas: **metode penilaian kesesuaian menuntut keadaan sebenarnya diketahui.** Pada skenario terkendali, peneliti yang menetapkan keadaan itu, sehingga "keluaran yang diharapkan" punya dasar. Pada sampel sungguhan, keadaan sebenarnya **tidak diketahui** — tidak ada yang tahu perilaku asli sampel tanpa analisis manual mendalam lebih dulu.

**Yang tetap dapat diuji pada sampel sungguhan** — dan boleh disebut di BAB V sebagai arah lanjutan:

| Dapat diuji tanpa keadaan sebenarnya | Tidak dapat |
|---|---|
| Keterlacakan — tiap temuan tetap tertelusur ke bukti dan rujukan | Ketepatan terhadap keluaran yang diharapkan |
| Konsistensi — masukan sama menghasilkan keluaran sama | |
| Perilaku tiga keadaan — bukti tidak teramati tetap dinyatakan | |

Untuk memperoleh keadaan sebenarnya pada sampel sungguhan, jalannya adalah **analisis manual** atas sampel yang sama — dan itu justru pembanding pada §18.4. Jadi arah lanjutannya sudah tersedia secara metodologis; yang tidak tersedia adalah **klaimnya sekarang**.

## 18.1a ⭐ Kriteria kelulusan — 🔒 *(baru v3.0)*

| # | Ketentuan |
|---|---|
| 1 | Istilah yang dipakai adalah **kesesuaian keluaran terhadap hasil yang diharapkan** — bukan *accuracy* dalam pengertian statistik, bukan metrik penggolongan |
| 2 | Kriteria ditetapkan **per kelas skenario**. ⛔ Tidak ada satu ambang tunggal maupun angka agregat lintas kelas — larangan `D-7` §18.1.2 |
| 3 | Kasus opsional hilang, wajib `UNKNOWN`, konflik, dan eksklusioner dilaporkan terpisah dari positif/benign; tidak dilebur ke angka rata-rata |
| 4 | Bila satu kelas memuat beberapa kasus, **tiap kasus dilaporkan sendiri**. ⛔ Dilarang menyembunyikan satu kegagalan di balik label "kelas lulus" |
| 5 | Kasus *holdout* dilaporkan sebagai kelompok tersendiri, tidak dilebur ke hasil *authoring* |

## 18.2 Traceability — *(diperbarui v3.0)*

Jalur penelusuran mengikuti model pencatatan §AA.1 `02_ARSITEKTUR`:

```text
RuleProfileEvaluation
→ RuleConditionResult
→ RuleConditionFact
→ NormalizedEvent
→ Artifact
→ Evidence
→ acquisition metadata

RuleProfileEvaluation
→ RuleMetadata
→ RuleElementReference / RuleReference
→ KB_Source

RuleFamilyEvaluation [hanya matched]
→ CorrelationFinding
→ ReconstructionFinding
→ ReconstructionRun
→ InvestigationHypothesis
```

`RuleProfileEvaluation` dan `RuleFamilyEvaluation` adalah titik awal untuk **semua** keluaran evaluasi. `CorrelationFinding` bukan titik awal universal karena tidak ada pada `not_matched` dan `insufficient_evidence`.

**Lima pemeriksaan per skenario:**

| # | Pemeriksaan | Lulus bila |
|---|---|---|
| 1 | Kelengkapan rekaman | Tiap kondisi yang dievaluasi punya satu `RuleConditionResult`, **termasuk pada evaluasi berkeluaran tidak terpenuhi dan bukti tidak memadai** |
| 2 | Fakta penopang | Tiap kondisi **TRUE dan FALSE** menunjuk sekurang-kurangnya satu fakta lewat `RuleConditionFact` |
| 3 | Asal-usul | Tiap fakta tertelusur ke artefak, bukti mentah, dan metadata akuisisinya |
| 4 | Alasan ketidaktersediaan | Tiap kondisi **UNKNOWN** membawa alasan dan **tidak** memiliki fakta semu |
| 5 | Rujukan | Keluarga, profil, kondisi, dan batas interpretasi tertelusur ke rujukan basis pengetahuan berikut peran rujukannya |

⚠️ Pemeriksaan **UNKNOWN** hanya mungkin karena §AA.1 mewajibkan evaluasi profil dan keluarga dibuat untuk **setiap** eksekusi. Sebelum kontrak pencatatan evaluasi diperkenalkan pada v3.0, skenario B dan D2 tidak meninggalkan rekaman apa pun untuk diperiksa.

## 18.3 Missing-evidence behavior
Nilai apakah:
- UNKNOWN direpresentasikan benar;
- system menghindari unsupported conclusion;
- missing evidence dijelaskan.

**Anti-klaim-berlebih diperiksa terpisah** *(v3.0)* — bukan sebagai bagian keterlacakan: hipotesis tidak boleh memuat pernyataan yang melampaui kelas epistemik fakta penopangnya. Kapabilitas tidak dinaikkan menjadi perbuatan, aktivitas jaringan tidak dinaikkan menjadi eksfiltrasi. **Skenario C adalah ujian terberatnya.**

## 18.3a ⭐ Uji konsistensi — 🔒 *(baru v3.0)*

> RQ3 dan naskah BAB I Tujuan #3 menyebut konsistensi secara eksplisit; sampai v2.9 core **tidak memiliki prosedurnya sama sekali**.

**Prosedur:** tiap kasus dijalankan **tiga kali atas berkas bukti yang sama**, dengan `CorrelationRun` baru setiap kali, *hash* masukan sama, versi kode/aturan/basis pengetahuan sama, dan keadaan analisis bersih.

**Cakupan:** seluruh bundel *holdout*. Tidak wajib mengulang kasus *authoring*.

⛔ **Yang dibandingkan adalah kesamaan semantik, bukan rekaman basis data.** ID `CorrelationRun`, cap waktu, dan urutan baris memang berubah tiap eksekusi; membandingkannya akan menghasilkan kegagalan palsu.

| # | Yang dibandingkan |
|---|---|
| 1 | Identitas dan keadaan tiap kondisi |
| 2 | Alasan pada tiap kondisi `UNKNOWN` |
| 3 | Hubungan kondisi dengan fakta penopangnya |
| 4 | Versi aturan dan keluaran tiap aturan |
| 5 | Keberadaan/ketiadaan `CorrelationFinding` dan `InvestigationHypothesis`; bila keduanya ada, isi hipotesis yang disusun sistem |
| 6 | Relasi keterlacakan |

Konsisten berarti **identik pada keenamnya**.

⭐ Uji ini hanya bermakna karena hipotesis bersifat **imutabel per `CorrelationRun`**. Bila hipotesis dapat disunting pemeriksa, membandingkan dua eksekusi atas masukan sama kehilangan artinya.

## 18.4 Manual baseline — *(diamandemen v3.0)*

`[ARSIP v2.9]` ~~Bandingkan: waktu · langkah/interaksi · finding · consistency · traceability.~~

### Unit dan batas perbandingan — 🔒 *(ditetapkan v3.2)*

- Kedua proses menerima **paket bukti mentah imutabel dan metadata akuisisi yang sama**, dengan nilai SHA-256 yang sama.
- Proses akuisisi berada **di luar** unit perbandingan. Perhitungan langkah dimulai setelah paket bukti tersedia.
- Pada baseline manual, peneliti boleh memakai alat baca/kueri umum untuk memeriksa keluaran mentah, tetapi **tidak melihat keluaran otomatis platform** sebelum catatan manual disegel.
- Pada platform, penguraian, normalisasi, evaluasi aturan, dan penyusunan laporan berjalan melalui fungsi sistem yang diteliti.
- Kedua proses berakhir ketika keluaran, hubungan ke bukti, perlakuan terhadap bukti hilang, dan alasan analisis sudah didokumentasikan.

Dengan batas ini, jumlah langkah/interaksi membandingkan **proses analisis atas bukti yang sama**, bukan perbedaan cara memperoleh bukti.

**Dimensi yang dibandingkan atas bukti yang sama:**

| # | Dimensi |
|---|---|
| 1 | Keluaran yang ditemukan |
| 2 | Langkah dan interaksi yang dibutuhkan |
| 3 | Keterlacakan ke bukti |
| 4 | Perlakuan terhadap bukti yang hilang |
| 5 | Bentuk dokumentasi alasan analisis |

⛔ **Dimensi waktu dicabut.** Peneliti adalah pengembang platform sekaligus pelaksana analisis manual; mengukur waktu sendiri menghasilkan angka yang tidak netral dan menjadi sasaran empuk. Naskah BAB I tidak pernah menjanjikan pengukuran waktu, sehingga pencabutan ini **tidak melanggar apa pun yang sudah terbit**.

⛔ **Dimensi konsistensi dicabut** dari baseline, kecuali analisis manual benar-benar diulang. Membandingkan konsistensi terhadap proses yang dijalankan sekali tidak terdefinisi.

⭐ **Rumusan "kinerja" — 🔒 wajib muncul di BAB III 3.6.** Naskah BAB I Batasan #5 yang sudah terbit berbunyi *"perbandingan **kinerja** dibatasi pada satu metode pembanding"*. Karena dimensi waktu dicabut, kata itu **wajib dimaknai secara eksplisit**, satu kalimat, di tempat baseline diperkenalkan: kinerja dinilai melalui **kesesuaian keluaran, keterlacakan, penanganan bukti hilang, langkah/interaksi, dan dokumentasi alasan — tanpa klaim kecepatan atau efisiensi.** Tanpa kalimat itu, penguji berhak membaca BAB III sebagai janji BAB I yang tidak ditepati.

⚠️ **Sifatnya deskriptif.** Baseline membedakan karakteristik kedua proses pada skenario terkendali; ia **bukan** bukti keunggulan platform dan **bukan** keadaan sebenarnya. Konflik peran peneliti dinyatakan sendiri sebagai keterbatasan.

⭐ **Urutannya mengikat:** baseline manual dicatat dan **disegel sebelum keluaran otomatis dilihat** (§16).

## 18.5 Ablation lintas kelompok sumber — 🔒 `DEFER` `D-8` *(diputuskan 2 Sep 2026)*

> ⛔ **KEPUTUSAN v2.7: `DEFER`.** *Ablation* **tidak ditulis di BAB III** dan tidak dijalankan. Dicatat di BAB V sebagai pengembangan lanjutan; dapat diangkat kembali bila pembimbing memintanya.
>
> **Alasan.** Fungsi *ablation* — menunjukkan tiap kelompok berkontribusi — tergantikan dua hal yang sudah ada:
> **(a)** kelas skenario D1/D2 yang mencabut bukti di tingkat sumber lalu mengamati perubahan keluaran;
> **(b)** spesifikasi aturan yang mensyaratkan fakta lintas kelompok, sehingga temuan tertentu **mustahil dihasilkan dari satu kelompok saja** — bukti struktural yang tidak menuntut eksekusi tambahan.
>
> ⚠️ **Prasyarat yang membuat `DEFER` sah — dipenuhi lewat `M-5`.** Pada v2.6, G2 **tidak pernah dijalankan di satu pun skenario**; men-*defer* *ablation* saat itu akan meninggalkan **nol bukti** bahwa G2 berkontribusi. `M-5` menutup lubang itu lebih dulu.
>
> `[ARSIP v2.4.1–v2.6]` Status **DIKOMIT** dicabut. Tiga dokumen kanonik sempat memuat tiga status berbeda; ini menyeragamkannya.

## 18.5.1 Cakupan kelompok × keluarga — diperbarui v3.3

Fungsi pembuktian cakupan tidak lagi memakai matriks 3 aturan × 6 kelas yang besar. BAB III cukup memakai tabel rancangan pengujian inti yang menunjukkan bahwa:

- G1 diuji pada kelima keluarga;
- G2 muncul sebagai konteks pada K01 dan rekonstruksi lintas temuan;
- G3 menjadi bukti inti K05 dan konteks rekonstruksi bagi keluarga relevan;
- tiap kelompok mempunyai kasus bukti tersedia dan tidak tersedia;
- fixture eksklusioner dan konflik terdapat di katalog *authoring*;
- holdout membawa vektor keluaran untuk kelima keluarga.

> `[ARSIP v3.2]` Matriks di bawah tidak masuk BAB III Draft v3; dipertahankan sebagai riwayat rancangan tiga aturan.

> ⭐ `[v3.0]` **Matriks ini mencakup keenam belas jalanan uji *authoring*.** Kasus *holdout* **dilaporkan terpisah** dan tidak dilebur ke dalamnya. Di BAB III, `M-6` menunjukkan **rancangan** cakupan; buktinya baru muncul di BAB IV.

**Tidak lagi wajib masuk BAB III 3.6.** Fungsinya diserap oleh tabel rancangan pengujian inti v3.3.

| Spesifikasi | A | B | C | D1 | D1-b | D2 |
|---|---|---|---|---|---|---|
| **APKF-001** | G1+G2 | G1 | G1+G2 | **G2 dicabut** | G1-A10+G3 dicabut | **G1 dicabut** |
| **APKF-002** | G1 | G1 | G1 | G3 dicabut | — | **G1 dicabut** |
| **APKF-003** | G1+G3 | G1+G3 | G1+G3 | konteks dicabut | — | **G3 dicabut** |

**Yang dibuktikan:** ketiga kelompok dipakai pada skenario positif, **dan** ketiganya punya kasus pencabutannya sendiri — G1 lewat D2, G2 lewat D1 APKF-001, G3 lewat D2 APKF-003. Itulah pertanyaan yang semula hendak dijawab *ablation*.

`[ARSIP v2.4.1]` Rancangan *ablation* lama:

**Keputusan: dikomit sebagai rancangan pengujian tetap.** Kata "opsional" dicabut.

```text
G1
G1 + G2
G1 + G3
G1 + G2 + G3
```

Tujuan:
> menguji nilai tambah korelasi lintas sumber, bukan mengandaikan semakin banyak sumber selalu lebih baik.

**Dasarnya.** Judul penelitian memuat *correlation*. Bila penguji meminta bukti bahwa korelasi tiga kelompok sumber memang bernilai lebih daripada satu, tanpa ablation tidak ada jawaban empiris — yang tersisa hanya klaim. Biayanya rendah: skenario yang sama dijalankan dengan himpunan bagian kelompok sumber.

### 18.5.2 Arsip `CONCERN-D8` — tidak aktif sejak v2.7

> `[ARSIP v2.4.1–v2.6]` Saat *ablation* masih berstatus `DIKOMIT`, bagian ini mewajibkan konfirmasi pembimbing karena *ablation* dapat disalahbaca sebagai metode pembanding kedua. Instruksi tersebut **tidak lagi aktif** setelah `D-8` berubah menjadi `DEFER`.

**Yang berlaku pada v3.3:**

1. *Ablation* tidak ditulis di BAB III dan tidak dijalankan.
2. Konfirmasi pembimbing bukan prasyarat untuk menyelesaikan 3.6.
3. Bila pembimbing kelak meminta pengujian tersebut, `D-8` dibuka kembali secara eksplisit dan istilah yang digunakan adalah **“pengujian konfigurasi kelompok sumber”**, bukan “metode pembanding” atau “baseline”.
4. Batasan satu metode pembanding pada BAB I tetap mengikat; satu-satunya baseline aktif adalah analisis manual §18.4.

---

# 19. NOVELTY / POSITIONING

Jangan mengklaim existing tools tidak memiliki:
- timeline;
- link analysis;
- correlation;
- AI;
- relationship analysis.

Posisi defensible:

> Korelasi deterministik pascaakuisisi atas fakta Android ternormalisasi untuk mendukung rekonstruksi aplikasi APK penipuan, dengan semantik fakta eksplisit, asal-usul bukti, penanganan TRUE/FALSE/UNKNOWN, pembedaan kapabilitas dari aktivitas, profil bukti yang tertelusur ke rujukan, dan hipotesis yang dibatasi oleh dukungan faktualnya.

Klaim penelitian dibatasi pada skenario dan lingkungan yang diuji. Sampel malware nyata memperkuat relevansi pola statis, bukan mengubah platform menjadi pendeteksi malware atau membuktikan validitas eksternal pada seluruh APK penipuan.

---

# 20. CHAIN OF CUSTODY / FORENSIC SOUNDNESS

Minimum:
- SHA-256 di agent;
- server re-hash;
- mismatch flagged/rejected;
- raw evidence immutable;
- parser tidak overwrite raw evidence;
- acquisition command/API dicatat;
- provenance;
- allowlisted operation;
- no arbitrary remote shell.

---

# 21. CLOSED / WORKING / OPEN

## CLOSED
- title;
- incident family;
- web + local agent + ADB;
- authorized non-root baseline;
- backend correlation;
- explainable/reference-traceable reasoning;
- raw evidence integrity.

## WORKING-STABLE
- status empiris artefak serta penyesuaian teknis profil yang diizinkan setelah *authoring*; makna keluarga, fakta wajib, peran kondisi, agregasi, dan batas klaim sudah dikunci;
- evidence-selection criteria;
- Tier-1 feasibility framework;
- rule semantics;
- validation architecture.

## OPEN
*(diperbarui v3.3 — disamakan dengan `00_SESSION_STARTER` §12)*

> `[ARSIP v2.8]` ~~final three primary source groups~~ — **ditutup oleh `D-5` sejak v2.5.** Struktur G1/G2/G3 terkunci; keanggotaan artefak tetap milik Tier-2. `00_SESSION_STARTER` sudah mengarsipkannya pada v2.6; butir ini tertinggal di sini.

- status empiris dan artefak final berdasarkan hasil Tier-2;
- penyesuaian *as-built* profil setelah *authoring* dalam batas §14.3; katalog 16 profil dan YAML `design_baseline` sudah lengkap;
- versi Android aktual Samsung Galaxy A10 dan API AVD kedua;
- identitas serta SHA-256 tiga APK malware nyata terpilih dari sedikitnya enam kandidat;
- nama package, versi, varian, serta SHA-256 simulator aman dan aplikasi benign/kontrol;
- mekanisme terkendali pembangkitan status `denied` dan `unsupported` pada H4/H6 sebelum penyegelan;
- perangkat lunak virtualisasi desktop yang benar-benar digunakan;
- hasil Tier-2, hasil skenario, hasil manual baseline, dan hasil evaluasi;
- implementasi endpoint lokal, pengendali host, dan `ground_truth.json` simulator;
- bentuk deployment final dan distribusi agen lokal;
- *(dihapus v2.6 — RQ berstatus FINAL pada naskah BAB I; lihat §17)*

APK-static adalah pengaya G1 dan satu-satunya perlakuan terhadap APK malware nyata. Desain manual baseline sudah ditetapkan pada §18.4; yang belum tersedia hanya pelaksanaan dan hasilnya. `R-01` dan `R-02` sudah tertutup; `R-03`, `R-04`, dan `R-05` berstatus `NOT REQUIRED`.

> `[DITUTUP v2.9]` ~~`B3-09` vs padanan `capability_state`~~ — padanan final **“kapabilitas”**, §4.7.3.

> ⚠️ **OPEN di atas adalah daftar data pelaksanaan dan keputusan teknis tersisa, bukan alasan membuka ulang rumusan masalah, kelompok sumber, atau metode validasi.** Garis beku v3.3 tetap berlaku.

---

# 22. CURRENT PHASE

*(diperbarui v3.3 — disamakan dengan `00_SESSION_STARTER` §11)*

**Selesai:** BAB I `DRAFT FINAL` · BAB II `DRAFT FINAL` · substansiasi celah penelitian · RQ `FINAL` (*working-freeze*).

**Sekarang: menyelesaikan Generate 1.5, lalu memproduksi paket diagram BAB III Draft v3 berdasarkan core v3.3 dan `BAB_03_WORKING_v1_3.md`.**

- **3.1:** selaraskan alasan *Incremental*: kebutuhan penelitian tingkat tinggi stabil, sedangkan keanggotaan/implementasi artefak dapat dipertajam oleh Tier-2 formatif;
- **3.2:** pertahankan tahap a–f dengan *increment* 1–4 pada d dan *increment* 5 pada e;
- **3.3:** tampilkan tiga kategori sampel, protokol seleksi kandidat, dan batas statis/dinamis;
- **3.4:** tampilkan lima dimensi, G1–G3 yang diperluas, Tier-1 inti, dan `KF/KNF` secara ringkas;
- **3.5:** selaraskan lima keluarga APKF, profil, `claim_level`, rujukan elemen, simulator, arsitektur, alur, ERD, keterlacakan, dan antarmuka;
- **3.6:** gunakan katalog minimum 20 *authoring*, delapan *holdout*, fixture konflik/eksklusioner, uji konsistensi, serta unit baseline manual §18.4.

Draft v3 tidak memakai lampiran formal. Masukkan hanya tabel inti dan sepuluh diagram §22A; artefak teknis rinci ditempatkan pada repositori penelitian berversi. Masukan faktual yang masih kosong berada di §21 dan tidak boleh diperkirakan.

> `[KOREKSI v2.8]` ~~Tier-2 empirical feasibility dapat berjalan paralel/minimal, tetapi bukan blocker untuk mulai menulis.~~ — benar untuk BAB I dan II, **tidak sepenuhnya benar untuk BAB III**: 3.4 memerlukan **protokol** Tier-2 yang final dan 3.3 memerlukan keputusan bahan serta lingkungan.
>
> Yang tetap berlaku: **hasil** Tier-2 bukan prasyarat menulis BAB III, dan memang **tidak boleh** masuk BAB III — hasil adalah materi BAB IV (`B3-06`). Yang dibutuhkan BAB III hanyalah **rancangan** pengujiannya.

> 🔒 **Status v3.3: `FROZEN` — dibekukan 5 September 2026.** Audit berikutnya diarahkan ke **naskah BAB III Draft v3**, kecuali muncul salah satu pemicu pembukaan core di bawah.
>
> ⛔ **Kriteria berhenti — ditetapkan v3.0.** Core dibuka kembali **hanya** oleh dua pemicu: (a) core bertentangan dengan dirinya sendiri, atau (b) keputusan penelitian baru dari Marco atau pembimbing. **Bukan pemicu:** core belum memuat rancangan yang final. Rancangan yang belum final ditulis **di dalam naskah**, lalu hasilnya dicatat balik ke sini sekali di akhir. Tanpa kriteria ini, tiap tinjauan akan selalu menemukan alasan untuk satu ronde lagi — lima ronde pertama membuktikannya.

---

# 22A. KONTRAK BENTUK BAB III DRAFT v3 — 🔒 v3.3

## Strategi kepadatan

- target panjang **31–35 halaman**;
- tidak memakai lampiran formal;
- sekitar **tujuh tabel inti**: alat/lingkungan; dimensi–kelompok; Tier-1 inti; status akuisisi–fakta–epistemik; portofolio APKF; seleksi sampel; dan rancangan pengujian/evaluasi;
- YAML lengkap, kamus data, katalog kasus, metadata sampel, keluaran uji, dan prosedur operasional rinci disimpan sebagai artefak repositori penelitian berversi;
- tabel dua kolom yang hanya menggantikan daftar harus diubah menjadi prosa atau daftar;
- satu konsep dijelaskan di satu tempat utama dan dirujuk dari bagian lain.

## Sepuluh diagram wajib

| No. | Diagram | Fungsi dan isi minimum |
|---|---|---|
| 1 | Tahap penelitian dan lima *increment* | membedakan tahap a–f dari siklus pengembangan; *increment* 1–4 pada tahap d dan *increment* 5 pada tahap e |
| 2 | Penurunan kebutuhan | lima dimensi → G1–G3 → Tier-1/Tier-2 → kebutuhan fungsional/nonfungsional |
| 3 | Arsitektur platform terpadu | aktor, web, backend, agen lokal, perangkat, modul akuisisi, penyimpanan, pengurai, penormalisasi, basis pengetahuan, APKF, rekonstruksi, keterlacakan, dan laporan dalam satu gambar lanskap |
| 4 | *Use case* pemeriksa | batas sistem dan fungsi Pemeriksa; tidak menampilkan detail implementasi |
| 5 | Flowchart akuisisi dan normalisasi | validasi sesi/perangkat → operasi allowlist → status akuisisi → hash/simpan → parsing → fakta/UNKNOWN → normalisasi |
| 6 | Flowchart evaluasi APKF dan rekonstruksi | pilih `evidence_mode` + `run_purpose` → saring profil → validasi aturan/rujukan → kondisi → TRUE/FALSE/UNKNOWN/konflik → agregasi keluarga → temuan → rekonstruksi berbatas klaim |
| 7 | ERD logis Crow’s Foot | entitas berbentuk tabel dengan PK/FK, kardinalitas, serta zona kasus/akuisisi, bukti/fakta, aturan/rujukan, evaluasi/keluaran |
| 8 | Jalur keterlacakan data | dua jalur dari evaluasi menuju bukti mentah dan menuju rujukan; jalur keluaran hanya untuk `matched` |
| 9 | Wireframe hasil evaluasi | daftar semua evaluasi, detail tiga keadaan, konflik/UNKNOWN, bukti penopang, rujukan, batas klaim, dan bagian laporan |
| 10 | Tata kelola sampel dan pembekuan | S-A/S-B/S-C, authoring, kandidat statis, freeze, holdout, baseline manual, analisis otomatis, dan pelaporan |

Setiap diagram dibuat dalam sumber `.drawio` yang dapat diedit dan PNG resolusi tinggi untuk DOCX. Gunakan konektor ortogonal, hindari garis berpotongan atau menembus node, jaga keterbacaan pada A4, sediakan legenda, dan ikuti notasi yang benar. Diagram arsitektur boleh satu halaman lanskap penuh. ERD harus digambar ulang dengan Crow’s Foot; notasi Chen dan class diagram tidak dipakai. Diagram sekuens lama dicabut karena fungsinya sudah ditanggung flowchart dan arsitektur.
