# ARSITEKTUR & SETUP TEKNIS — KANONIK LENGKAP V3.3 — `FROZEN`
## Platform Investigasi Forensik Android Berbasis Web dengan Rule-Based Evidence Correlation
### Revisi Bahasa Indonesia + Status Biaya/Lisensi + Kontrol Versi (Git) Lengkap

> **Fungsi dokumen:** menjadi sumber utama untuk arsitektur software, stack pengembangan, software yang harus diinstal, versi baseline, bahasa/framework/library, biaya/lisensi, Android test environment, struktur repository, version control, alur acquisition, model data, security control, dan milestone development.

> Framing penelitian, feasibility matrix, working rules, dan validation methodology tetap berada di `01_BREAKDOWN_PROYEK_FORENSIK_ANDROID_V3_3`.

> **Snapshot versi/lisensi:** diverifikasi per **26 Agustus 2026**. Versi patch boleh berubah setelah tanggal ini. Setelah environment pertama berhasil, dependency harus dikunci melalui `requirements.txt`/lockfile dan `package-lock.json`; jangan mengejar update versi saat eksperimen/evaluasi sudah berjalan.

---

## CATATAN PERUBAHAN v3.2 → v3.3 *(5 September 2026)* — 🔒 `FROZEN`

| Seksi | Perubahan |
|---|---|
| Y.3 · Z · AA | **Generate 1.5:** katalog 16 profil `design_baseline`, kontrak selector/operator/applicability, fixture eksklusioner, serta atribut evaluasi yang diperlukan dikunci |
| AE · AG.11–AG.12 | Lima YAML keluarga menjadi baseline sebelum diagram; prosedur perubahan *authoring* dan pembekuan implementasi diperjelas |
| Z.0 · AA.2 | Aplikabilitas dikoreksi menjadi dua sumbu—`evidence_mode` dan `run_purpose`—agar profil runtime umum tetap dievaluasi pada simulator, *holdout*, kontrol benign, maupun penggunaan produksi yang sesuai |
| N · Y.3.5 | Aplikasi uji diganti menjadi **simulator bukti aman** dengan aplikasi Android, pengendali host, endpoint lokal, build variant, dan `ground_truth.json`; tiga kategori sampel dikunci |
| Y.3.3 · Z | Skema aturan diperluas menjadi lima keluarga/profil APKF, `claim_level`, agregasi profil, peran bukti, dan `conflicting_evidence` |
| AA | Model data menambahkan identitas keluarga/profil dan rujukan tingkat elemen; hipotesis disusun lintas temuan yang kompatibel |
| AC | Tampilan evaluasi membedakan basis bukti, basis aturan, basis pengetahuan, konflik, batas klaim, dan seluruh keadaan keluaran |
| AE · AJ | Struktur repositori, tahap pengembangan simulator, kandidat sampel statis, dan katalog 20 authoring/8 holdout diperbarui |
| AO | Spesifikasi teknis sepuluh diagram BAB III Draft v3 dan keluaran `.drawio`/PNG dikunci |

---

## CATATAN PERUBAHAN v3.1 → v3.2 *(4 September 2026)* — 🔒 `FROZEN`

> **Rekonsiliasi pascadraf BAB III.** Arsitektur utama, stack, jumlah kelompok sumber, serta baseline akuisisi tidak berubah. Versi ini membersihkan rujukan/status aktif dan memperkeras kontrak implementasi yang sebelumnya belum tersambung penuh.

| Seksi | Perubahan |
|---|---|
| Kepala · ringkasan aktif · AM | Identitas paket dan daftar keputusan aktif diselaraskan ke v3.2 |
| O · Y.3.5–Y.3.5a | Istilah sampel dibersihkan; pemilihan AVD dibuat berbasis kompatibilitas; klaim “isolasi” versi/OEM dibatasi; residu Android 8.1 dihapus |
| Y.3.3 · Z · AA.1 | `reference_ids` diwajibkan dan dihubungkan ke `RuleReference`/`KB_Source`; semua keluaran berawal pada `RuleEvaluation`; hanya `matched` menghasilkan temuan dan hipotesis |
| AB · AC | Blok kode Markdown yang rusak diperbaiki; endpoint evaluasi dan komponen antarmuka dipisahkan dari catatan penjelas |
| AE | `evaluations.py` ditambahkan; direktori *ablation* dikeluarkan dari target MVP sesuai `D-8 DEFER` |
| AJ | Pemetaan tahap d/e, status `R-01`, cakupan D1-b, dan istilah hasil evaluasi diselaraskan |

---

## CATATAN PERUBAHAN v3.0 → v3.1 *(3 September 2026)*

> **Amandemen sah atas core beku.** Pemicunya **keputusan baru dari peneliti**, bukan temuan audit — sesuai kriteria §16 `01_BREAKDOWN`.

| Seksi | Perubahan |
|---|---|
| §Y.3.5 | **`G-05` diamandemen** — perangkat pembanding menjadi **Samsung Galaxy A10** (2019, One UI, plafon Android 11 / API 30), menggantikan Xiaomi Redmi Note 5. Prasyarat `minSdk 28` menjadi aman pada versi mana pun. Karakteristik **penyetelan ulang izin otomatis** Android 11 dicatat sebagai konsekuensi metodologis |
| §Y.3.5 | Rumusan risiko OEM diganti dari MIUI ke **One UI**; peringatan terhadap G1-A10 tetap berlaku |

⚠️ **Yang belum tertutup:** versi Android aktual perangkat, yang menentukan API AVD kedua.

---

## CATATAN PERUBAHAN v2.9.1 → v3.0 *(3 September 2026)* — 🔒 `FROZEN`

> **Kenaikan mayor.** Keputusan BAB III 3.1–3.6 dipropagasikan ke kontrak teknis tanpa mengubah stack dasar.

| Seksi | Perubahan |
|---|---|
| Y.3.5a · Y.3.6 | Protokol sampel nyata dan pemetaan status ketersediaan ke keadaan kondisi ditambahkan |
| Z.1 · AA.1 | Jalur pencatatan evaluasi aturan ditambahkan; `RuleEvaluation`, `RuleConditionResult`, dan `RuleConditionFact` masuk; `FindingEvidence` dicabut |
| AB · AC | Endpoint dan tampilan evaluasi tiga keluaran dipropagasikan |
| AJ.2 | *Increment* 1–4 dipetakan ke tahap d dan *increment* 5 ke tahap e; Tier-2 formatif/konfirmatif dibedakan |

---

## CATATAN PERUBAHAN v2.9 → v2.9.1 *(2 September 2026)*

> **Errata kesiapan penulisan.** Struktur A–AO utuh; tidak ada keputusan penelitian baru.

| Seksi | Perbaikan |
|---|---|
| §AJ.2 | **Tumpang tindih tahap d/e/f ditutup** — tahap d dibatasi *increment* 1–4, *increment* 5 menjadi tahap e. **Tabel lima *increment* tidak disentuh**, `D-1` tidak dibuka. Ditambah pembedaan Tier-2 formatif vs konfirmatif |
| §O | **Identitas citra dikunci: Google APIs.** Kata "AOSP" pada §Y.3.5 dicabut — yang dimaksud sejak semula "bukan-OEM", bukan nama citra |
| §V | Contoh payload `collect_package_state` → `collect_package_detail`; ID sebelumnya tidak terdaftar pada *allowlist* |
| §Y.3.5 | **Perlakuan sampel dikunci: dipasang, tidak dieksekusi.** Bentuk kendali jaringan ditetapkan per jenis sampel. **`G-05`** — perangkat fisik satu unit, berikut empat konsekuensi dan prasyarat `minSdk` |
| **§Y.3.6** | ⭐ **Seksi baru — pemetaan `availability_status` → `evidence_state` → TRUE/FALSE/UNKNOWN.** Rantai ini putus sampai v2.9, sehingga 3.5 tidak dapat menerangkan dari mana `UNKNOWN` berasal |

⚠️ **Yang sengaja TIDAK dikerjakan:** relasi dan kardinalitas §AA, *use case*, aktor, batas sistem, dan DFD. Semuanya **gambar yang dibuat sambil menulis BAB III 3.5**, bukan cacat dokumen ini.

---

## CATATAN PERUBAHAN v2.8 → v2.9 *(2 September 2026)*

### v2.9 — stabilisasi final

> **Tidak ada keputusan teknis baru.** Seluruh bagian A–AO, stack, model data, operasi akuisisi, kontrak mesin aturan, struktur repositori, kontrol versi, lima *increment*, dan dua belas milestone dipertahankan. Paket v2.9 berstatus **`FROZEN`**.

| Bagian | Perbaikan |
|---|---|
| Kepala | Nomor versi dan rujukan silang disamakan dengan paket v2.9 |
| Kepala · §Y.3.5 | Ringkasan “satu pekerjaan tertunda” yang sudah tersalip v2.7 diperbaiki; peran lingkungan tetap terkunci, sedangkan nama dataset/perangkat/API dicatat sebagai rincian penulisan |
| §AJ.2 | Pemetaan enam tahap penelitian/proyek a–f untuk BAB III 3.2 ditambahkan; lima *increment* `D-1` tetap utuh pada tahap d |
| §AJ.2 | Status `R-01` ditegaskan sebagai pekerjaan sitasi, bukan perubahan model pengembangan |

**Garis beku:** core hanya dibuka kembali bila ada perubahan pada baseline akuisisi, struktur G1/G2/G3 yang berdampak teknis, kontrak data/aturan, metode validasi, kelayakan total satu kelompok, atau arahan pembimbing/institusi. Versi dependency, nama perangkat, dan housekeeping tidak membuat versi kanonik baru.

---

## CATATAN PERUBAHAN v2.3 → v2.8 *(2 September 2026)*

### v2.8 — sinkronisasi ringkasan *(2 September 2026)*

> **Tidak ada keputusan teknis baru.** v2.8 memperbaiki tempat-tempat yang **meringkas** keputusan tetapi tidak ikut diperbarui saat keputusannya berubah. Isi teknis dokumen ini tidak berubah.

| Bagian | Perbaikan |
|---|---|
| §AJ.2 | Catatan sitasi **Zein dkk. (2023)** dicabut — sumber lama `R-01` ditutup pada v2.7, Zein dibuang, dan kandidat SEBoK dipilih. Catatan lama menyuruh membaca sumber yang sudah tidak dipakai |
| Kepala dokumen | Nomor versi dan rujukan silang |

⚠️ **Akar penyebab yang ditangani v2.8.** Tiga ronde berturut-turut (v2.5, v2.6, v2.7) gagal dengan pola identik: keputusan ditambal di **tempat ia dinyatakan**, tidak di **tempat ia diringkas** — tabel keputusan, daftar OPEN/CLOSED, catatan sitasi, Pusat Kendali. v2.8 disusun lewat penyisiran per kode keputusan (`D-n`, `G-n`, `R-n`, `M-n`) di keempat dokumen, bukan lewat daftar temuan.

---

| Versi | Perubahan |
|---|---|
| **v2.4** | Nomor versi dan rujukan silang disamakan dengan dua dokumen kanonik lain. Isi teknis tidak berubah |
| **v2.4.1** | **§AJ.0–AJ.2 baru** — keputusan `D-1` masuk: model pengembangan dinamai ***Incremental***, urutan *increment* dinyatakan terkunci oleh rantai pipeline riset, dan 12 milestone dipetakan ke 5 *increment*. **§AJ kini menjadi sumber langsung BAB III 3.1 dan 3.2** |
| **v2.5** | Keputusan `D-5` masuk. **Satu perubahan skema:** tiap fakta ternormalisasi wajib membawa **label epistemik**. Rincian pada `01_BREAKDOWN` §4.4a; dampak teknis dicatat di bawah |

### Dampak `D-5` terhadap implementasi

| Lapis | Perubahan | Besaran |
|---|---|---|
| Agen lokal · akuisisi | **Tidak ada.** Tidak ada perintah ADB baru | — |
| Daftar artefak (§AL) | **Tidak ada.** Sebelas artefak prioritas Tier-2 tidak berubah | — |
| Pengurai | Mengisi label saat normalisasi | Kecil |
| Skema fakta ternormalisasi | **Satu field wajib** ditambahkan | Kecil |
| Basis data | **Satu kolom** ditambahkan | Kecil |
| Mesin aturan | Dapat membaca label sebagai syarat | Kecil |

⚠️ **Label epistemik bukan keadaan aturan.** Label melekat pada **fakta** (masukan); keadaan `matched` · `not_matched` · `insufficient_evidence` melekat pada **aturan** (keluaran). Kontrak keluaran tiga keadaan tidak berubah.

**Rincian pelaksanaan yang diisi saat revisi 3.3 atau sebelum eksperimen:**

| Isi | Status |
|---|---|
| Peran lingkungan hibrida — emulator sebagai garis dasar utama, perangkat fisik sebagai pembanding ketersediaan artefak | 🔒 **Terkunci v2.7**, §Y.3.5 |
| Versi Android aktual Galaxy A10, API AVD kedua, perangkat lunak virtualisasi, tiga APK malware terpilih, simulator, dan aplikasi kontrol | ⚠️ Data pelaksanaan; tidak mengubah arsitektur |

> `[TERSALIP v2.7]` ~~Lingkungan pengujian hibrida masih menunggu keputusan sampel/bahan; §O belum boleh dipakai untuk BAB III 3.3~~ — peran lingkungan sudah ditutup di §Y.3.5. §O dipakai bersama §Y.3.5; sampel menggunakan salah satu AVD tetap yang kompatibel sesuai aturan §O.

---

# A. CARA MEMBACA DOKUMEN INI

Dokumen ini sengaja membedakan dua hal:

1. **Target arsitektur MVP lengkap**  
   Struktur folder/file dan komponen yang dituju saat prototype sudah terintegrasi.

2. **Scaffold awal / vertical slice**  
   File minimum yang benar-benar perlu dibuat saat mulai development.

Jadi, struktur repository yang panjang **bukan berarti semua file harus dibuat kosong pada hari pertama**. Sebaliknya, scaffold awal yang kecil **bukan berarti arsitektur akhirnya hanya membutuhkan sedikit file**.

---

# B. PRINSIP DESAIN UTAMA

1. **Local Agent tipis**  
   Agent fokus pada device detection, ADB execution, evidence writing, hashing, upload, dan status/progress.

2. **Backend sebagai analysis/research layer**  
   Parsing, normalization, Knowledge Base, rule engine, correlation, hypothesis, dan report berada di backend.
   > `[ARSIP v2.6]` ~~scoring~~ — dicabut oleh `D-6`.

3. **Authorized non-root ADB sebagai baseline**  
   Tidak mengandalkan rooting, exploit, lock bypass, chip-off, JTAG, atau physical extraction.

4. **Raw evidence immutable**  
   Parser tidak pernah mengubah file evidence asli.

5. **Provenance eksplisit**  
   Artifact/event harus dapat ditelusuri sampai raw evidence dan acquisition session.

6. **Operasi ADB harus allowlisted**  
   Backend tidak boleh mengirim arbitrary shell command ke agent.

7. **Evidence availability eksplisit**  
   `acquired`, `unavailable`, `denied`, `unsupported`, atau `failed`.

8. **Rule semantics tiga-state**  
   `TRUE`, `FALSE`, `UNKNOWN`.

9. **Evidence Source Group configurable**  
   Penelitian boleh dibatasi maksimal tiga primary source groups, tetapi engine jangan di-hardcode hanya bisa tiga selamanya.

10. **Eksperimen reproducible**  
    Android/API/build, AVD/device profile, tool version, action, timestamp, rule version, dan Git commit harus dicatat.

11. **MVP diutamakan**  
    Jangan menambah Kafka, Neo4j, Elasticsearch, Kubernetes, Celery, Redis, ML framework, atau infrastruktur besar tanpa kebutuhan nyata.

---

# C. RINGKASAN STACK TEKNOLOGI YANG DIPAKAI

| Area | Pilihan Utama | Fungsi |
|---|---|---|
| Local Agent | Python 3.13 | ADB orchestration, acquisition, hash, upload |
| Backend | Python + FastAPI | API, WebSocket, parsing, normalization, rule/correlation |
| Database | PostgreSQL 18 | case/evidence/artifact/event/finding metadata |
| ORM | SQLAlchemy 2 | database access |
| Migration | Alembic | versioning schema database |
| Frontend | React 19 + TypeScript | dashboard web |
| Frontend build tool | Vite 8 | dev server/build |
| Android interface | ADB / Platform-Tools | komunikasi agent ↔ Android |
| Android test environment | Android Studio + Emulator/AVD | controlled device testing |
| Controlled test app | Kotlin | benign evidence generator |
| Rule / KB | YAML | rule dan knowledge metadata yang mudah diaudit |
| Version control | Git + GitHub Free private repo | source/history/backup/reproducibility |
| Raw evidence storage | Filesystem lokal terstruktur | MVP evidence storage |
| Container | Docker Compose | terutama PostgreSQL/dev service |
| API testing | FastAPI Swagger + Bruno | manual API testing |

---

# D. BAHASA DAN FORMAT YANG PERLU DIKUASAI

| Bahasa / Format | Dipakai Untuk | Tingkat Kebutuhan |
|---|---|---|
| Python | Agent, backend, parser, normalizer, rule engine, test automation | Wajib |
| TypeScript | React frontend | Wajib |
| SQL | PostgreSQL, debugging query, migration understanding | Dasar–menengah |
| YAML | Rule dan Knowledge Base | Wajib |
| JSON | API payload, explanation, experiment metadata | Wajib |
| PowerShell / shell | setup lokal, ADB experiment, script development | Dasar |
| Kotlin | controlled benign Android test apps | Dibutuhkan saat Tier-2 simulator app |
| HTML/CSS | tampilan frontend | Dasar |
| Git CLI | version control | Wajib |
| Markdown | dokumentasi proyek/eksperimen | Wajib |

Catatan:
- Lu **tidak perlu Java sebagai bahasa utama**. JDK diperlukan oleh toolchain Android.
- Lu **tidak perlu C/C++** untuk MVP.
- Lu **tidak perlu bahasa reverse engineering** seperti Smali sebagai requirement core.

---

# E. BASELINE VERSI YANG DIREKOMENDASIKAN

| Komponen | Baseline | Catatan |
|---|---|---|
| Python | **3.13.15** | Seri 3.13 dipilih untuk stabilitas ekosistem; 3.14.7 lebih baru tetapi tidak diperlukan. |
| Node.js | **24.19.0 LTS** | Pilih LTS, bukan Node 26 Current. |
| npm | **11.17.0** (bundled Node 24.19.0) | Lock dependency melalui `package-lock.json`. |
| PostgreSQL | **18.6** | Stable supported major. |
| Android Studio | **Quail 3 / 2026.1.3 Patch 1** | Stable channel. |
| Android SDK Platform | **Android 16 / API 36** | Primary AVD baseline. |
| Android SDK Platform-Tools | **37.0.0** | Baseline stabil. `37.0.1` masih tercatat Canary pada release notes. |
| Android SDK Build Tools | **36.0.0 / latest compatible 36.x** | Cocok dengan toolchain Android 16. |
| Android Gradle Plugin | **9.3.0** | Untuk controlled Kotlin simulator apps. |
| Gradle | **9.5.0** | Kompatibilitas AGP 9.3. |
| JDK | **17** | Minimum/default AGP 9.3; gunakan JBR/JDK bawaan Android Studio bila praktis. |
| Kotlin Android plugin | **2.3.21** | Baseline controlled Android app. |
| React | **19.2.8** | Stable npm latest saat snapshot. |
| Vite | **8.2.2** | Stable npm latest saat snapshot. |
| React Router | **8.3.0** | Optional tetapi berguna untuk routing. |

## E.1 Kebijakan versi

Lakukan:
- gunakan stable/LTS;
- freeze versi setelah environment pertama terbukti berjalan;
- commit `package-lock.json`;
- pin dependency Python setelah smoke test;
- catat versi tool pada experiment log;
- catat `git commit SHA` pada eksperimen.

Jangan:
- menjadikan preview/Canary sebagai baseline utama;
- menggunakan Android 17 Beta sebagai primary AVD;
- menggunakan dependency dinamis seperti `9.3.+`;
- upgrade dependency di tengah holdout evaluation tanpa membuat versi eksperimen baru.

---

# F. STATUS BIAYA, LISENSI, DAN APA YANG PERLU DIBAYAR

## F.1 Kesimpulan biaya untuk skripsi ini

Dengan pilihan stack yang direkomendasikan, **software license cost bisa Rp0** untuk penggunaan pribadi/mahasiswa.

Yang mungkin menimbulkan biaya hanyalah:
- hardware tambahan;
- cloud hosting jika dipilih;
- Genymotion paid jika memerlukan Android 16/fitur Pro;
- GitHub/GitLab/Docker/Postman paid plan jika suatu saat memerlukan fitur premium;
- layanan pihak ketiga berbayar yang tidak diperlukan oleh MVP.

## F.2 Tabel software/tool

| Komponen | Status Biaya | Sumber Terbuka? | Perlu Bayar untuk Skripsi Ini? | Catatan |
|---|---|---|---|---|
| Git | Gratis | Ya, GPLv2 | Tidak | Wajib untuk version control. |
| GitHub Free | Gratis $0 | Bukan OSS sebagai SaaS | Tidak | Unlimited public/private repositories untuk personal account; rekomendasi remote backup. |
| GitLab Free | Gratis $0 | Open-core/SaaS | Tidak | Alternatif GitHub; tidak perlu pakai keduanya. |
| VS Code | Gratis | Source `vscode` tersedia MIT; binary Microsoft memakai lisensi produk | Tidak | Boleh digunakan untuk development/testing tanpa biaya. |
| Python | Gratis | Ya, PSF License | Tidak | Bahasa utama agent/backend. |
| Node.js | Gratis | Ya | Tidak | Runtime frontend tooling. |
| PostgreSQL | Gratis | Ya, PostgreSQL License | Tidak | Database utama. |
| Android Studio | Gratis download/use | Campuran; tunduk Android SDK License | Tidak | IDE resmi + SDK Manager + Emulator. |
| Android SDK / ADB / Emulator | Gratis digunakan melalui SDK | Sebagian AOSP, sebagian komponen Google licensed | Tidak | Tidak ada subscription untuk penggunaan development normal. |
| Docker Engine | Gratis | Ya | Tidak | Linux/server path. |
| Docker Desktop | Gratis untuk personal, pendidikan, non-komersial OSS, dan bisnis kecil sesuai batas lisensi | Produk Desktop tidak sepenuhnya OSS | **Tidak untuk penggunaan mahasiswa/pendidikan** | Organisasi besar/government bisa wajib subscription. |
| DBeaver Community | Gratis | Ya | Tidak | Database GUI; pilih ini **atau** pgAdmin. |
| pgAdmin | Gratis | Ya, PostgreSQL License | Tidak | Alternatif DBeaver. |
| Bruno Open Source | Gratis | Ya | Tidak | API client yang Git-friendly; rekomendasi. |
| Postman Free | Ada free plan | Tidak | Tidak jika hanya kebutuhan dasar | Paid plan optional; Bruno lebih cocok untuk repo-centric workflow. |
| PyInstaller | Gratis | Ya | Tidak | Optional untuk packaging Agent menjadi `.exe`. |
| Wireshark | Gratis | Ya, GPLv2 | Tidak | Optional untuk controlled network testing. |
| Genymotion Desktop Personal | Gratis terbatas | Proprietary | Tidak jika sekadar personal use, **tetapi tidak cocok sebagai primary baseline Android 16 gratis** | Free edition saat ini tidak menyediakan Android terbaru; Android 16 memerlukan paid license. |
| Genymotion Educational | Berbayar | Proprietary | Tidak dibutuhkan | Optional bila memang mau memakai Genymotion Pro. |
| FastAPI/SQLAlchemy/Pydantic/etc. | Gratis | Ya | Tidak | Python ecosystem yang dipakai di backend. |
| React/Vite/TypeScript/etc. | Gratis | Ya | Tidak | Frontend ecosystem. |

## F.3 Status framework, bahasa, dan library inti

| Komponen | Jenis | Gratis? | Sumber Terbuka? | Lisensi / Status | Perlu Bayar? |
|---|---|---|---|---|---|
| Python | Bahasa/runtime | Ya | Ya | PSF License | Tidak |
| TypeScript | Bahasa/tooling | Ya | Ya | Apache-2.0 | Tidak |
| Kotlin | Bahasa/tooling | Ya | Ya | Apache-2.0 | Tidak |
| FastAPI | Framework backend | Ya | Ya | MIT | Tidak |
| Uvicorn | ASGI server | Ya | Ya | BSD-3-Clause | Tidak |
| SQLAlchemy | ORM | Ya | Ya | MIT | Tidak |
| Alembic | Migration | Ya | Ya | MIT | Tidak |
| psycopg | PostgreSQL driver | Ya | Ya | LGPL-3.0 | Tidak |
| Pydantic | Data validation | Ya | Ya | MIT | Tidak |
| pydantic-settings | Configuration | Ya | Ya | MIT | Tidak |
| PyYAML | YAML parser | Ya | Ya | MIT | Tidak |
| HTTPX | HTTP client/testing | Ya | Ya | BSD-3-Clause | Tidak |
| pytest | Testing | Ya | Ya | MIT | Tidak |
| Ruff | Linter/formatter Python | Ya | Ya | MIT | Tidak |
| mypy | Static type checker | Ya | Ya | MIT | Tidak |
| React | Frontend library | Ya | Ya | MIT | Tidak |
| Vite | Frontend build tool | Ya | Ya | MIT | Tidak |
| React Router | Routing | Ya | Ya | MIT | Tidak |
| TypeScript compiler | Frontend language tooling | Ya | Ya | Apache-2.0 | Tidak |
| ESLint | Lint JavaScript/TypeScript | Ya | Ya | MIT | Tidak |
| Prettier | Formatter | Ya | Ya | MIT | Tidak |
| date-fns | Date utility (opsional) | Ya | Ya | MIT | Tidak |
| lucide-react | Icons (opsional) | Ya | Ya | ISC | Tidak |
| TanStack Query | Server-state frontend (opsional) | Ya | Ya | MIT | Tidak |
| Recharts | Chart library (opsional) | Ya | Ya | MIT | Tidak |

**Kesimpulan:** framework/library core yang direkomendasikan tidak membutuhkan pembelian lisensi untuk penelitian ini.

## F.4 Rekomendasi jalur gratis

Gunakan:

```text
Git
+ GitHub Free Private Repository
+ VS Code
+ Python
+ Node.js LTS
+ Android Studio + Android Emulator
+ PostgreSQL
+ Docker Desktop Personal/Education (opsional tapi direkomendasikan)
+ DBeaver Community ATAU pgAdmin
+ Bruno Open Source
```

Dengan jalur ini tidak ada subscription software yang perlu dibeli untuk thesis MVP.

---

# G. SOFTWARE/APLIKASI YANG WAJIB DIINSTAL

## G.1 Git

Fungsi:
- source control;
- rule/KB history;
- experiment reproducibility;
- remote backup.

Verifikasi:

```bash
git --version
```

Setelah install:

```bash
git config --global user.name "Nama Lu"
git config --global user.email "email-yang-dipakai-untuk-git@example.com"
git config --global init.defaultBranch main
```

---

## G.2 VS Code

Fungsi:
- Python;
- TypeScript/React;
- YAML;
- Markdown;
- Git;
- Docker;
- SQL.

Extension yang direkomendasikan:
- Python
- Pylance
- Ruff
- ESLint
- Prettier
- YAML
- Docker (jika Docker dipakai)
- PostgreSQL/SQL extension optional
- GitLens optional

Tidak perlu membeli Visual Studio Professional/Enterprise.

---

## G.3 Python 3.13.15

Fungsi:
- local agent;
- FastAPI backend;
- parsers;
- normalizer;
- rule engine;
- tests.

Verifikasi:

```bash
python --version
python -m pip --version
```

**Jangan install dependency project secara global.** Gunakan virtual environment terpisah untuk `agent` dan `backend`.

---

## G.4 Node.js 24 LTS

Fungsi:
- React;
- TypeScript;
- Vite;
- ESLint;
- frontend package management.

Verifikasi:

```bash
node --version
npm --version
```

Target:

```text
node v24.19.0
npm 11.17.0
```

---

## G.5 Android Studio + Android SDK

Install stable:

```text
Android Studio Quail 3
2026.1.3 Patch 1
```

Di **SDK Manager**, install:

```text
Android SDK Platform 36
Android SDK Build-Tools 36.x
Android SDK Platform-Tools 37.0.0 stable
Android Emulator
Android SDK Command-line Tools (latest stable)
Android 16 / API 36 system image
```

Android Studio dipakai untuk:
- SDK Manager;
- Emulator/AVD;
- controlled benign Android test app.

Runtime platform lu **tidak membutuhkan Android Studio**. Runtime agent membutuhkan `adb`.

---

## G.6 PostgreSQL 18.6

Pilihan 1 — rekomendasi:
> PostgreSQL berjalan melalui Docker Compose.

Pilihan 2:
> install PostgreSQL native.

Jangan jalankan Docker PostgreSQL dan native PostgreSQL di port `5432` bersamaan kecuali sengaja mengubah konfigurasi.

Verifikasi native:

```bash
psql --version
```

---

## G.7 ADB / Platform-Tools

Setelah SDK Manager:

```bash
adb version
adb devices -l
```

`adb` harus ditemukan melalui:
- PATH; atau
- `.env` agent melalui `ADB_PATH`.

Catat `adb version` di experiment log.

---

# H. SOFTWARE YANG SANGAT DIREKOMENDASIKAN

## H.1 Docker Desktop / Docker Engine

Untuk skripsi pribadi/pendidikan, Docker Desktop dapat digunakan gratis berdasarkan lisensi Docker saat ini.

Fungsi:
- PostgreSQL reproducible;
- mudah reset database;
- memisahkan service development;
- memudahkan sesi AI baru/replikasi environment.

Untuk MVP, cukup container PostgreSQL. Agent tidak perlu dijalankan di container karena membutuhkan akses ADB host.

---

## H.2 DBeaver Community ATAU pgAdmin

Jangan install keduanya kecuali memang mau membandingkan.

Rekomendasi:
- **DBeaver Community** jika ingin UI general-purpose yang nyaman;
- **pgAdmin** jika ingin tool yang fokus PostgreSQL.

Keduanya gratis/open source.

---

## H.3 Bruno Open Source

Rekomendasi API client utama.

Kenapa Bruno:
- gratis;
- open source;
- local-first;
- collection disimpan sebagai file;
- cocok dengan Git;
- tidak perlu account untuk basic usage.

FastAPI juga otomatis memberikan Swagger UI:
- `/docs`
- `/redoc`

Jadi API testing sudah bisa dilakukan tanpa Postman.

---

# I. SOFTWARE OPSIONAL

## I.1 Postman

Ada Free plan untuk individual.

Gunakan hanya jika sudah familiar. Tidak wajib karena:
- Swagger UI sudah ada;
- Bruno lebih cocok untuk version-controlled API collection.

---

## I.2 Genymotion

Status:
- Free Personal Use tersedia tetapi terbatas;
- Android terbaru/fitur tertentu membutuhkan paid license;
- free edition saat ini tidak cocok sebagai primary Android 16 baseline.

Keputusan:
> Android Studio Emulator tetap primary.

Genymotion hanya alternative test environment jika kemudian ada alasan metodologis.

---

## I.3 PyInstaller

Dipakai nanti jika Local Agent ingin dibungkus:

```text
agent.exe
```

Tidak diperlukan di awal development.

---

## I.4 Wireshark

Dipakai hanya pada **controlled lab/test environment** untuk menguji behavior/network endpoint.

Bukan baseline passive post-incident acquisition.

---

# J. SOFTWARE YANG TIDAK PERLU UNTUK MVP

Tidak perlu install dari awal:
- Kafka
- RabbitMQ
- Redis
- Celery
- Neo4j
- Elasticsearch/OpenSearch
- Kubernetes
- MinIO
- Jenkins
- TensorFlow
- PyTorch
- full SIEM stack
- enterprise malware sandbox
- reverse engineering suite besar

Jika nanti ada requirement baru, evaluasi dulu sebelum menambah dependency.

---

# K. DEPENDENSI PYTHON UNTUK BACKEND

## K.1 Dependensi utama

Pin versi awal:

```text
fastapi[standard]==0.141.1
uvicorn[standard]==0.52.4
SQLAlchemy==2.0.52
alembic==1.19.1
psycopg[binary]==3.3.4
pydantic==2.13.4
pydantic-settings==2.15.0
PyYAML==6.0.3
pytest==9.1.1
```

Dependency pendukung:

```text
aiofiles
httpx
pytest-asyncio
PyJWT
pwdlib[argon2]
```

Kualitas pengembangan opsional:

```text
ruff
mypy
pre-commit
```

Semua package di atas dapat digunakan tanpa biaya lisensi software untuk proyek ini.

## K.2 Fungsi setiap dependensi

| Package | Fungsi |
|---|---|
| FastAPI | REST API, WebSocket integration, OpenAPI/Swagger |
| Uvicorn | ASGI server |
| SQLAlchemy | ORM/database access |
| Alembic | migration schema |
| psycopg | PostgreSQL driver |
| Pydantic | typed schema/validation |
| pydantic-settings | `.env` / config |
| PyYAML | load rule/KB YAML |
| aiofiles | async file I/O |
| HTTPX | HTTP client dan integration tests |
| PyJWT | JWT auth |
| pwdlib[argon2] | password hashing |
| pytest | testing |
| pytest-asyncio | async tests |
| Ruff | lint/format Python |
| mypy | optional static type checking |
| pre-commit | optional local quality gate |

---

# L. DEPENDENSI AGEN LOKAL

Set awal:

```text
httpx
websockets
pydantic==2.13.4
pydantic-settings==2.15.0
tenacity
psutil
pytest==9.1.1
pytest-asyncio
```

Dependensi build opsional:

```text
pyinstaller
```

Prinsip:
- ADB dipanggil menggunakan Python `subprocess`;
- tidak perlu library Python ADB khusus;
- agent jangan terlalu dependency-heavy.

Optional Windows-specific:
- `pywin32` hanya jika kemudian perlu native Windows USB/device events.

MVP detection cukup melalui polling:

```bash
adb devices -l
```

---

# M. DEPENDENSI ANTARMUKA WEB (FRONTEND)

Core:

```text
react@19.2.8
react-dom@19.2.8
vite@8.2.2
react-router@8.3.0
typescript
@vitejs/plugin-react
eslint
```

HTTP:
- rekomendasi awal: native `fetch`;
- optional: `axios` bila memang lebih nyaman.

Optional:
```text
date-fns
lucide-react
@tanstack/react-query
recharts
prettier
```

Jangan menambah heavy design system sebelum dashboard dasar selesai.

Buat project:

```bash
npm create vite@latest frontend -- --template react-ts
cd frontend
npm install
npm install react-router
```

Jika pakai Axios:

```bash
npm install axios
```

Setelah working:
- commit `package.json`;
- commit `package-lock.json`;
- jangan hapus lockfile.

---

# N. APLIKASI UJI ANDROID TERKONTROL

Kotlin digunakan untuk **simulator bukti aman**, bukan malware. Simulator menyediakan keadaan yang diketahui untuk memvalidasi akuisisi, normalisasi, lima keluarga APKF, `UNKNOWN`, konflik, eksklusi, dan rekonstruksi.

## N.1 Komponen

1. **Aplikasi Android simulator** — menghasilkan artefak G1 serta aktivitas uji yang terlihat.
2. **Pengendali skenario pada host** — menyiapkan keadaan AVD, data sintetis, aksi, cap waktu, akuisisi, dan pencatatan oracle.
3. **Endpoint lokal** — menerima lalu lintas uji hanya pada jaringan laboratorium/loopback dan menghasilkan log terkontrol untuk validasi G3.

## N.2 Struktur proyek

```text
android-test-apps/
├── safe-evidence-simulator/
│   ├── app/
│   ├── feature-identity/
│   ├── feature-special-access/
│   ├── feature-visible-trigger/
│   ├── feature-local-network/
│   └── scenarios/
├── scenario-controller/
│   ├── controller/
│   ├── seeders/
│   ├── acquisition/
│   └── validators/
├── local-endpoint/
├── benign-control-catalog/
└── README.md
```

Baseline build:

```text
Kotlin plugin : 2.3.21
AGP           : 9.3.0
Gradle        : 9.5.0
JDK           : 17
compileSdk    : 36
targetSdk     : 36
minSdk        : 28 (boleh disesuaikan)
```

## N.3 Perilaku yang diperbolehkan

- package/UID/versi dan metadata instalasi yang dapat ditelusuri;
- permintaan izin transparan dengan persetujuan pengguna;
- deklarasi layanan aksesibilitas **no-op** dan status aktif yang dipicu manual;
- *overlay* berlabel jelas **SIMULASI UJI**;
- receiver `BOOT_COMPLETED` yang hanya menghasilkan notifikasi/log terlihat;
- aktivitas penggunaan yang dipicu pengendali;
- permintaan HTTP ke endpoint lokal dengan payload sintetis dan nonrahasia;
- SMS/kontak sintetis yang ditanam melalui mekanisme lab yang sah, bukan dibaca diam-diam oleh aplikasi.

## N.4 Larangan keras

Simulator tidak boleh mempunyai pencurian kredensial, pengambilan data pribadi nyata, impersonasi merek/lembaga, komunikasi ke pihak ketiga, stealth, obfuscation/evasion, eksploitasi, *auto-grant*, penyalahgunaan aksesibilitas, *overlay* menipu, atau persistensi tersembunyi. Simulator tidak boleh dipresentasikan sebagai malware atau bukti bahwa penipuan aktual terjadi.

## N.5 Varian build dan skenario

| Varian | Fungsi | Boleh dipakai untuk penyempurnaan? |
|---|---|---|
| `authoring` | pengembangan pengurai, fakta, profil APKF, dan oracle | ya |
| `holdout` | evaluasi setelah pembekuan; package/signature/config berbeda | tidak |
| `benignControl` | kapabilitas/aktivitas sah untuk anti-klaim-berlebih | ya, hanya sebelum freeze |

Setiap skenario dapat mengaktifkan modul secara eksplisit melalui konfigurasi build atau pengendali. Tidak ada modul yang aktif tersembunyi.

## N.6 Kontrak `ground_truth.json`

```json
{
  "scenario_id": "SA-K05-A-01",
  "sample_category": "S-A",
  "variant": "authoring",
  "apk": {"package": "...", "version": "...", "sha256": "..."},
  "environment": {"android_api": 36, "device_profile": "..."},
  "initial_state": {},
  "actions": [{"id": "...", "at": "..."}],
  "expected_artifacts": [],
  "expected_facts": [],
  "expected_apkf": {},
  "claim_limits": [],
  "intentional_unavailability": [],
  "expected_conflicts": []
}
```

## N.7 Tahap pengembangan

1. kunci kontrak skenario, ID, oracle, dan larangan;
2. buat scaffold, modul bersama, dan build variant;
3. implementasikan identitas, izin, dan akses khusus yang transparan;
4. implementasikan aktivitas serta trigger yang selalu terlihat;
5. siapkan data komunikasi sintetis dan endpoint lokal;
6. hubungkan pengendali host dengan reset/seed/action/acquire;
7. buat katalog authoring, benign-control, konflik, eksklusioner, dan holdout;
8. verifikasi oracle, lalu bekukan commit Git, APK, konfigurasi, hash, aturan, dan basis pengetahuan.

Pengembangan simulator berada di dalam pekerjaan pengujian/integrasi yang sudah ada; ia **bukan increment keenam**.

---

# O. SETUP AVD / ANDROID EMULATOR

Primary reproducible baseline:

```text
Device profile : Pixel 6 atau satu fixed Pixel profile
OS             : Android 16
API            : 36
Image          : Google APIs
Architecture   : x86_64 pada host x86 / ARM64 pada host ARM
ADB            : enabled
```

Catat:
- device profile;
- API;
- build fingerprint;
- system image;
- snapshot name bila snapshot dipakai.

> ⭐ **`[KOREKSI v3.0]` Identitas citra lingkungan uji — 🔒 keputusan.**
>
> Sampai v2.9, §O menetapkan citra **Google APIs** sementara §Y.3.5 menyebut lingkungan **"Emulator AOSP terisolasi"**. Keduanya nama citra sistem yang berbeda di AVD Manager, sehingga BAB III 3.3 tidak punya satu identitas lingkungan yang dapat ditulis.
>
> **Yang berlaku: citra Google APIs, sesuai §O.** Alasannya `dumpsys usagestats` dan beberapa layanan sistem berperilaku lebih dekat ke perangkat nyata pada citra ini; citra AOSP murni justru menjauhkan garis dasar dari kondisi yang direkonstruksi.
>
> **Kata "AOSP" pada §Y.3.5 dicabut.** Yang dimaksud sejak semula adalah **bukan-OEM** — Android bawaan tanpa antarmuka vendor — bukan nama citra sistemnya. Frasa penggantinya: *"emulator terisolasi, citra Google APIs, tanpa akun, tanpa SIM"*.
>
> ⭐ **`[v3.0]` AVD kedua — 🔒 ditetapkan.** AVD kedua **mengikuti versi Android perangkat pembanding fisik** (§Y.3.5), bukan mengikuti era repositori sampel. Angkanya diisi saat 3.3 dirakit, setelah `ro.build.version.sdk` perangkat diperiksa.
>
> **Dasarnya adalah mengurangi faktor pembaur yang muncul setelah `G-05`.** Dengan dua AVD dan satu perangkat fisik, pengaruh versi dapat dibandingkan lebih terarah, tetapi antarmuka OEM tidak pernah menjadi satu-satunya perbedaan antara emulator dan perangkat fisik.
>
> | Perbandingan | Interpretasi yang sah |
> |---|---|
> | AVD API 36 ↔ AVD kedua | Mendukung pengamatan **pengaruh versi Android** pada dua emulator dengan profil dan konfigurasi yang disamakan sejauh mungkin |
> | AVD kedua ↔ perangkat fisik pada versi sama | Mengurangi pembaur versi dan memberi **indikasi gabungan** pengaruh OEM, perangkat keras, konfigurasi, dan perbedaan emulator–fisik |
>
> ⛔ Hasilnya tidak boleh disebut “mengisolasi OEM”. Klaim dibatasi pada perbedaan ketersediaan artefak di lingkungan yang diuji.
>
> ⚠️ Aturan kompatibilitas AVD hanya berlaku untuk simulator aman dan aplikasi benign/kontrol yang akan dijalankan. Pada APK malware nyata, `minSdk`, `targetSdk`, dan ABI dicatat sebagai metadata statis; tidak ada pemasangan.

## O.1 Android version tambahan

Jangan install semua sejak awal.

Setelah baseline jalan, baru pertimbangkan:
- Android 15 / API 35;
- Android 14 / API 34.

Hanya jika dibutuhkan untuk cross-version feasibility.

## O.2 Android 17

Android 17 masih beta pada snapshot ini.

Gunakan hanya sebagai:
- optional compatibility test;
- bukan primary baseline.

---

# P. URUTAN SETUP LAPTOP DARI NOL

Urutan install:

```text
1. Git
2. VS Code
3. Python 3.13
4. Node.js 24 LTS
5. Android Studio + SDK components
6. Docker Desktop (recommended)
7. DBeaver CE atau pgAdmin
8. Bruno
```

PostgreSQL:
- jika Docker dipakai → jalankan dari Docker Compose;
- jika tidak → install native.

Lalu:
1. buat repository;
2. setup Git remote;
3. buat Python venv;
4. create frontend Vite;
5. boot AVD;
6. test ADB;
7. start PostgreSQL;
8. start backend;
9. start frontend.

---

# Q. PYTHON VIRTUAL ENVIRONMENT

Rekomendasi:

```text
agent/.venv
backend/.venv
```

Windows PowerShell:

```powershell
cd backend
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Agent:

```powershell
cd agent
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Linux/macOS:

```bash
python3.13 -m venv .venv
source .venv/bin/activate
```

`.venv/` tidak boleh masuk Git.

---

# R. SETUP DATABASE DENGAN DOCKER COMPOSE

`docker-compose.yml`:

```yaml
services:
  postgres:
    image: postgres:18.6
    container_name: android-forensic-postgres
    restart: unless-stopped
    environment:
      POSTGRES_DB: android_forensic
      POSTGRES_USER: forensic_app
      POSTGRES_PASSWORD: local-dev-only
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

Start:

```bash
docker compose up -d postgres
```

Check:

```bash
docker compose ps
docker compose logs postgres
```

Stop:

```bash
docker compose down
```

Reset database volume hanya bila sengaja:

```bash
docker compose down -v
```

**Jangan gunakan password contoh untuk environment final/demo.**

---

# S. FILE `.ENV`

`.env` tidak boleh masuk Git.

Commit hanya:
```text
.env.example
```

## S.1 Backend

```text
APP_ENV=development
DATABASE_URL=postgresql+psycopg://forensic_app:password@localhost:5432/android_forensic
EVIDENCE_ROOT=./var/evidence
JWT_SECRET=change-me
CORS_ORIGINS=http://localhost:5173
```

## S.2 Agent

```text
BACKEND_BASE_URL=http://localhost:8000
BACKEND_WS_URL=ws://localhost:8000/ws/agent
AGENT_TOKEN=change-me
ADB_PATH=adb
AGENT_ID=dev-agent-01
POLL_INTERVAL_SECONDS=2
```

## S.3 Frontend

```text
VITE_API_BASE_URL=http://localhost:8000
VITE_WS_BASE_URL=ws://localhost:8000
```

---

# T. ARSITEKTUR SISTEM

```text
Pemeriksa → React Web → FastAPI/REST/WebSocket
                           ├─ layanan kasus/perangkat/sesi
                           ├─ orkestrasi agen lokal → ADB → AVD/perangkat dummy
                           ├─ unggah APK statis terverifikasi
                           ├─ integritas + bukti mentah imutabel
                           ├─ pengurai + penormalisasi fakta
                           ├─ basis pengetahuan + pemuat APKF
                           ├─ evaluasi profil/keluarga + konflik
                           ├─ temuan + rekonstruksi/hipotesis
                           ├─ keterlacakan + laporan
                           └─ PostgreSQL + penyimpanan berkas/versi aturan

Simulator aman ↔ pengendali host ↔ endpoint lokal
        └──────── menghasilkan paket bukti + ground truth ────────┘
```

Diagram BAB III menggabungkan konteks/deployment dan komponen internal dalam satu gambar lanskap, tetapi tetap memakai zona dan batas yang jelas agar tidak menjadi satu flowchart raksasa. Jalur aplikasi dinamis dan jalur APK malware statis bertemu setelah pemeriksaan integritas; jalur statis tidak melewati ADB execution.

Pemetaan teknis lima dimensi:

| Dimensi | Jalur utama |
|---|---|
| identitas/instalasi | G1 package, UID, versi, certificate, metadata instalasi, static APK |
| kapabilitas/akses khusus | G1 permission, component, Accessibility, overlay, special access |
| eksekusi/persistensi | G1 UsageEvents/activity dan trigger tervalidasi |
| data komunikasi sensitif | G2 SMS/MMS/kontak/call-log/notifikasi kondisional |
| jaringan package/UID | G3 netstats/konektivitas dan endpoint lokal simulator |

---

# U. AGEN LOKAL (LOCAL AGENT)

## U.1 Flow

```text
Start
↓
Load config
↓
Validate ADB path/version
↓
Authenticate/register backend
↓
Heartbeat
↓
Detect device
↓
Collect safe metadata
↓
Wait for allowlisted acquisition job
↓
Execute profile
↓
Write raw evidence
↓
SHA-256
↓
Upload
↓
Backend verify hash
↓
Report status
```

## U.2 Target modul

```text
main.py
config.py
logging_config.py
models.py
exceptions.py
device_detection.py
adb_controller.py
adb_commands.py
acquisition_profiles.py
command_allowlist.py
privilege_detector.py
hashing.py
evidence_writer.py
uploader.py
api_client.py
ws_client.py
heartbeat.py
auth.py
state_machine.py
audit_logger.py
```

`privilege_detector.py` hanya mendeteksi status privilege; tidak melakukan rooting.

---

# V. OPERASI AKUISISI

Kandidat ID operasi:

```text
collect_device_metadata
collect_package_inventory
collect_package_detail
collect_usage_state
collect_accessibility_state
collect_sensitive_provider_data
collect_network_stats
pull_subject_apk
```

Backend hanya mengirim operation ID + parameter.

Contoh:

```json
{
  "operation": "collect_package_detail",
  "case_id": "CASE-001",
  "device_id": "DEVICE-001",
  "parameters": {
    "package_name": "com.example.target"
  }
}
```

Agent memilih command lokal yang sudah didefinisikan.

> `[KOREKSI v3.0]` Contoh payload sebelumnya memakai `collect_package_state`, sebuah ID operasi yang **tidak terdaftar** pada daftar kandidat di atas. Diseragamkan menjadi `collect_package_detail`. ID operasi bersifat *allowlist*; ID yang tidak terdaftar tidak dapat dieksekusi agen.

**Dilarang:**

```text
adb shell <arbitrary-string-from-backend>
```

---

# W. INTEGRITAS EVIDENCE

```text
Acquire
↓
Write raw file
↓
SHA-256 agent
↓
Upload
↓
SHA-256 backend
↓
Compare
↓
Store immutable
```

Acquisition session menyimpan:
- case/device;
- agent ID/version;
- Android/API/build;
- Platform-Tools version;
- operation/profile;
- command/API;
- start/end time;
- timezone;
- availability status;
- hashes;
- error.

---

# X. MODUL BACKEND

Service engineering:

```text
AuthService
AgentService
CaseService
DeviceService
AcquisitionService
EvidenceStorageService
IntegrityService
AuditService
WebSocketConnectionManager
ReportService
```

Service research:

```text
ParserRegistry
ArtifactService
NormalizationService
KnowledgeBaseLoader
KnowledgeBaseValidator
RuleLoader
RuleValidator
RuleEngine
CorrelationEngine
HypothesisBuilder
TraceabilityService
```

Pipeline:

```text
Raw Evidence
→ source-specific parser
→ Artifact
→ Normalizer
→ NormalizedEvent
→ Rule/Correlation
→ Finding/Hypothesis
```

---

# Y. MODEL DATA UTAMA

## Y.1 Evidence

```text
id
case_id
device_id
acquisition_session_id
operation_id
source_group
source_name
raw_source
stored_path
sha256_agent
sha256_server
size_bytes
acquired_at
availability_status
availability_reason
tool_version
android_version
device_build
privilege_state
```

## Y.2 Artifact

```text
id
evidence_id
artifact_type
parser_name
parser_version
subject_key
raw_value
parsed_value_json
parse_status
parse_note
```

## Y.3 NormalizedEvent

```text
id
case_id
artifact_id
event_type
epistemic_class
subject_package
subject_uid
object_type
object_value
predicate_value
event_time
observed_at
window_start
window_end
temporal_semantics
evidence_state
context_json
```

### Y.3.1 `epistemic_class` — 🔒 `D-5` *(baru v2.6)*

**Nilai yang sah** — tertutup, tidak boleh diperluas tanpa membuka `D-5`:

| Nilai | Jenis klaim | Contoh `event_type` |
|---|---|---|
| `identity_attribute` | identitas/atribut teknis | `package_observed_installed` |
| `capability_state` | kemampuan dimiliki — **bukan** perbuatan | `permission_observed_granted` · `accessibility_service_observed_enabled` |
| `execution_observed` | sesuatu teramati pernah berjalan/terjadi | `app_usage_observed` · `uid_network_activity_observed` |
| `data_present` | data ada pada perangkat | `sms_record_observed` |

### Y.3.1a Katalog `event_type` APKF `design_baseline` — 🔒 Generate 1.5

| `event_type` | Kelas | Sumber/pembentukan utama |
|---|---|---|
| `package_observed_installed` | `identity_attribute` | package state |
| `uid_observed` | `identity_attribute` | package–UID mapping |
| `apk_identity_observed` | `identity_attribute` | parser APK statis + SHA-256 |
| `permission_observed_requested` | `capability_state` | package/manifest permission |
| `sensitive_communication_capability_observed_granted` | `capability_state` | normalisasi izin sensitif yang berstatus granted |
| `sensitive_communication_capability_observed_declared` | `capability_state` | normalisasi deklarasi izin pada APK/package |
| `accessibility_service_observed_declared` | `capability_state` | komponen manifest/package |
| `special_access_capability_observed_enabled` | `capability_state` | secure settings/AppOps/special access |
| `special_access_capability_observed_declared` | `capability_state` | manifest permission/komponen khusus |
| `event_trigger_capability_observed_declared` | `capability_state` | receiver + intent-filter manifest/package |
| `service_observed_declared` | `capability_state` | service manifest/package |
| `event_trigger_execution_observed` | `execution_observed` | sumber eksekusi teratribusi yang lolos Tier-2 |
| `app_usage_observed` | `execution_observed` | UsageStats/UsageEvents |
| `activity_observed_resumed` | `execution_observed` | activity snapshot |
| `process_observed_running` | `execution_observed` | process snapshot |
| `uid_network_activity_observed` | `execution_observed` | netstats/NetworkStats berbasis UID |
| `local_endpoint_request_observed` | `execution_observed` | endpoint lokal terkontrol |
| `lab_network_flow_observed` | `execution_observed` | capture/proxy/resolver lab terisolasi |
| `sms_record_observed` | `data_present` | SMS provider |
| `contact_record_observed` | `data_present` | Contacts provider |
| `call_log_record_observed` | `data_present` | Call Log provider |
| `notification_context_observed` | `data_present` | sumber notifikasi tervalidasi |
| `apk_endpoint_reference_observed` | `identity_attribute` | string/config/resource APK; hanya petunjuk statis |
| `scenario_subject_binding_observed` | `identity_attribute` | manifest eksperimen; hanya validasi |
| `synthetic_exclusion_marker_observed` | `identity_attribute` | fixture adapter; hanya validasi mesin |

Fakta generik seperti `sensitive_communication_capability_observed_granted` tetap menyimpan nilai permission asli di `object_value`. Penormalisasi tidak menghapus detail artefak sumber; `artifact_id` dan `context_json` mempertahankan permission, komponen, intent action, bucket, atau endpoint yang membentuk fakta.

### Y.3.2 Enam ketentuan operasional

> Menutup pertanyaan yang belum terjawab pada v2.5.

| # | Ketentuan | Alasan |
|---|---|---|
| **1** | **Nama field:** `epistemic_class` | Hindari "label" (berkonotasi ML) dan "state" (bertabrakan dengan `evidence_state`) |
| **2** | **Tepat satu nilai, `NOT NULL`** | Determinisme. Fakta tanpa kelas epistemik tidak boleh masuk basis data |
| **3** | **Fakta yang menopang dua jenis klaim dipecah menjadi dua fakta**, bukan satu fakta berlabel ganda | Menjaga ketentuan 2. Pemecahan dilakukan penormalisasi, bukan penulis aturan |
| **4** | **Ditetapkan penormalisasi secara deterministik dari `event_type`**, lewat tabel pemetaan tetap. Bukan oleh penulis aturan, bukan oleh pengguna | `epistemic_class` adalah sifat **jenis fakta**, bukan penilaian per kasus. Menjadikannya keputusan manusia akan memasukkan penafsiran ke lapisan data |
| **5** | ⭐ **Dibaca mesin aturan, bukan metadata dokumentatif** | Lihat Y.3.3. Bila hanya dokumentatif, `D-5` tidak memberi apa pun melebihi konvensi penamaan yang sudah ada |
| **6** | `predicate_value` wajib menyatakan hasil observasi eksplisit `true`/`false` untuk predikat tertutup yang dipakai YAML aktif | Kondisi `FALSE` harus tertelusur ke fakta negatif eksplisit; ketiadaan baris tidak boleh disamakan dengan hasil negatif |

Untuk sumber yang cakupannya lengkap—misalnya daftar package atau keadaan permission target—penormalisasi menghasilkan fakta positif maupun negatif bagi kosakata predikat yang dibekukan. Jika cakupan sumber tidak lengkap, penormalisasi tidak membuat fakta negatif; evaluator menghasilkan `UNKNOWN`. Dengan demikian `RuleConditionFact` dapat menunjuk fakta penopang untuk kondisi `TRUE` dan `FALSE`, sedangkan kondisi `UNKNOWN` tetap tidak mempunyai fakta semu.

### Y.3.3 Penegakan — validasi saat pemuatan aturan

Setiap kondisi aturan **wajib menyatakan `epistemic_class` yang diharapkannya**. Pemuat aturan memvalidasi kecocokan **saat pemuatan**, bukan saat evaluasi:

```yaml
conditions:
  - fact: permission_observed_granted
    expects_epistemic_class: capability_state
```

Bila `event_type` yang dirujuk memiliki `epistemic_class` berbeda dari yang dinyatakan, **pemuatan aturan gagal**.

**Inilah wujud konkret `D-5`.** Aturan yang keliru memperlakukan kapabilitas sebagai eksekusi **tidak dapat dimuat** — prinsip epistemik `00_SESSION_STARTER` §5 berhenti bergantung pada kehati-hatian penulis dan ditegakkan mesin. Pemeriksaan dilakukan saat pemuatan agar tetap deterministik dan tidak menambah beban evaluasi.

### Y.3.3a ⭐ Penegakan rujukan aturan — 🔒 *(baru v3.2)*

Metadata setiap aturan wajib mempunyai `reference_ids` yang tidak kosong:

```yaml
reference_ids:
  - KB-SRC-APKF-K01-01
```

Pemuat aturan melakukan tiga pemeriksaan sebelum aturan aktif:

1. daftar tidak kosong dan tidak memiliki ID duplikat;
2. setiap ID dapat diresolusikan ke entri `KB_Source` yang aktif;
3. untuk setiap ID terbentuk relasi terhadap versi `RuleMetadata`; referensi kondisi/profil/batas interpretasi membentuk `RuleElementReference` dengan `rule_element_key` dan `reference_role`.

Kompilasi kunci bersifat deterministik: rujukan keluarga memakai `family_id`, sedangkan rujukan kondisi memakai `profile_id.condition_id`. `reference_role` diambil dari label baku `KB_Source` dan boleh dioverride secara eksplisit pada elemen. Saat temuan diterbitkan, layanan keterlacakan hanya memproyeksikan rujukan keluarga serta kondisi yang berkontribusi pada profil `matched`, kemudian mengelompokkannya menurut `artifact_semantics`, `behavior_relevance`, `interpretation_limit`, atau `technique_mapping`.

Aturan gagal dimuat bila salah satu pemeriksaan gagal. `reference_ids` adalah penghubung teknis, sedangkan detail bibliografis tetap disimpan pada `KB_Source`; keduanya tidak boleh digabung sebagai teks bebas di dalam YAML aturan.

### Y.3.4 Dampak teknis — dicatat jujur

> `[KOREKSI v2.6]` Pernyataan v2.5 bahwa perubahan ini *"nol dampak ke cakupan kerja, cuma satu kolom"* **meremehkan**. Yang tersentuh:

migrasi skema basis data · penormalisasi (tabel pemetaan + logika pemecahan fakta) · validasi nilai enum · skema kondisi aturan (`expects_epistemic_class`) · pemuat aturan (validasi saat muat) · pengujian · kemungkinan tampilan keterlacakan.

Tetap dipertahankan karena menopang argumen inti penelitian, tetapi **bukan perubahan sepele**.

⚠️ **`epistemic_class` bukan keadaan aturan.** Melekat pada **fakta** (masukan); `matched` · `not_matched` · `insufficient_evidence` melekat pada **aturan** (keluaran). Kontrak keluaran tiga keadaan pada naskah BAB II 2.1.13 tidak berubah.

`temporal_semantics`:
- `historical_event`
- `current_state`
- `aggregated_window`
- `unknown`

`evidence_state`:
- `observed_true`
- `observed_false`
- `unknown_unavailable`

---

## Y.3.5 Perangkat dan lingkungan uji — 🔒 *(baru v2.7)*

### Lingkungan

| Lingkungan | Peran | Sampel yang dipasang |
|---|---|---|
| **Emulator terisolasi** — AVD, citra **Google APIs**, tanpa akun, tanpa SIM (§O) | Garis dasar utama untuk Tier-2 dan skenario | simulator aman dipasang/dijalankan; aplikasi benign/kontrol hanya setelah verifikasi |
| **Perangkat fisik dummy** | Pembanding ketersediaan artefak, bukan lingkungan pengujian kedua | simulator aman saja |
| **VM analisis statis terisolasi** | pemeriksaan APK malware nyata | berkas tidak dipasang dan tidak dijalankan |

> ⭐ **`[KOREKSI v3.0]` Perlakuan sampel nyata — 🔒 keputusan.**
>
> Sampai v2.9, kolom tabel ini berjudul **"Sampel yang dijalankan"** dan memuat sampel nyata, sementara tiga paragraf di bawahnya menyatakan pemeriksaan kerealistisan bertumpu pada artefak yang muncul **tanpa sampel perlu dijalankan**. Dua pernyataan itu tidak dapat dipakai bersamaan di 3.3.
>
> `[DISUPERSESI v3.3]` Keputusan “sampel nyata dipasang, tidak dieksekusi” tidak lagi berlaku. APK malware nyata dianalisis **statis saja** pada VM terisolasi dan tidak masuk AVD.
>
> `[ARSIP v3.0–v3.2]` Pemasangan luring tanpa peluncuran pernah dipakai untuk memperoleh metadata instalasi. v3.3 memilih batas yang lebih tegas: hanya berkas dan artefak statis yang diperiksa pada APK malware nyata; karena itu tidak ada UID runtime, waktu pemasangan, izin diberikan, eksekusi, atau jaringan yang diklaim dari kategori S-C.

> ⭐ **`[KOREKSI v3.0]` Bentuk kendali jaringan — 🔒 keputusan.**
>
> Frasa "jaringan dikendalikan" pada v2.9 tidak menetapkan bentuknya. Yang berlaku, dibedakan menurut sampel:
>
> | Sampel | Jaringan | Alasan |
> |---|---|---|
> | **Simulator aman** | Jaringan emulator menuju **endpoint lokal milik peneliti**; tidak menghubungi infrastruktur pihak ketiga | Menghasilkan oracle dinamis G3 tanpa lalu lintas eksternal |
> | **Aplikasi benign/kontrol** | Jaringan diblokir secara default; diaktifkan hanya bila skenario memerlukan endpoint lokal | Mencegah ketergantungan dan lalu lintas pihak ketiga |
> | **APK malware nyata** | VM analisis statis luring | Berkas tidak dipasang, tidak dijalankan, dan tidak berkomunikasi |
>
> Bentuk kendali ini dicatat sebagai konteks pendukung dan wajib ditulis di 3.3.

⛔ **APK malware nyata tidak dipasang atau dijalankan pada emulator maupun perangkat fisik.**

### Perangkat fisik — 🔒 `G-05` *(ditetapkan 2 September 2026)*

**Satu perangkat**, bukan dua:

| Perangkat | Generasi | Peran |
|---|---|---|
| **Samsung Galaxy A10** (rilis Maret 2019, antarmuka One UI) | Plafon **Android 11 / API 30** | Pembanding ketersediaan artefak terhadap emulator |

> ⭐ **`[v3.1]` Perangkat pembanding diganti — keputusan Marco, 3 September 2026.**
>
> `[ARSIP v3.0]` ~~Xiaomi Redmi Note 5 (2018, MIUI), plafon Android 8/9.~~
>
> Galaxy A10 dirilis Maret 2019 dengan Android 9 Pie, menerima One UI 2.0 berbasis Android 10, dan pembaruan besar terakhirnya adalah **Android 11 dengan One UI 3.1** pada 2021. Plafonnya **API 30**.
>
> **Tiga keuntungan dibanding perangkat sebelumnya:**
>
> | # | |
> |---|---|
> | 1 | **Prasyarat `minSdk 28` aman pada versi mana pun** — Android 9, 10, maupun 11. Risiko aplikasi simulasi gagal terpasang, yang melekat pada perangkat sebelumnya, hilang |
> | 2 | Bila perangkat memakai Android 11, jaraknya terhadap Android 16 adalah **lima rilis mayor Android**; pencatatan tetap menggunakan API aktual (API 30 ↔ API 36), bukan menyebutnya selisih lima tingkat API |
> | 3 | Android 11 membawa **izin sekali pakai** dan **penyetelan ulang izin otomatis** bagi aplikasi yang lama tidak dipakai |
>
> ⭐ **Butir 3 berkonsekuensi metodologis dan wajib dinyatakan di 3.3.** Penyetelan ulang izin otomatis berarti fakta `permission_observed_granted` **dapat berubah tanpa tindakan pengguna** seiring waktu. Untuk penelitian yang berpusat pada kapabilitas dan keadaan bukti, ini bukan gangguan melainkan karakteristik lingkungan yang perlu dicatat: keadaan izin yang teramati adalah keadaan **pada saat akuisisi**, bukan keadaan sepanjang rentang waktu insiden.
>
> ⚠️ **Versi Android aktual perangkat belum dipastikan** — dapat berada di Android 9, 10, atau 11 bergantung riwayat pembaruan. **API AVD kedua mengikuti hasil pemeriksaan itu.** Diperiksa lewat Pengaturan → Tentang ponsel → Informasi perangkat lunak, atau `adb shell getprop ro.build.version.release`.

Peran perangkat **tidak berubah**: pembanding ketersediaan artefak, bukan lingkungan pengujian kedua. Garis dasar tetap emulator terisolasi.

> ⛔ **`[KOREKSI v3.0]` Turun dari dua perangkat menjadi satu.** Rancangan v2.7 memakai dua perangkat dari generasi berbeda justru untuk membandingkan ketersediaan artefak **antar versi Android**. Dengan satu perangkat, perbandingan itu **gugur**. Yang tersisa adalah perbandingan emulator ↔ satu perangkat OEM.
>
> **Empat konsekuensi, wajib dinyatakan di 3.3 — jangan ditutupi:**
>
> | # | Konsekuensi |
> |---|---|
> | 1 | Perbandingan antargenerasi Android **tidak dilakukan** |
> | 2 | Perilaku khas OEM **tidak dapat dipisahkan** dari perilaku Android umum. Peringatan v2.7 yang semula bersyarat kini berlaku **mutlak** |
> | 3 | Ketidaktersediaan artefak dilaporkan sebagai *"tidak tersedia pada satu perangkat One UI generasi 2019"* — bukan sebagai sifat Android, bukan sifat OEM secara umum |
> | 4 | Sejalan dengan naskah BAB I Batasan #5: hasil tidak digeneralisasi ke luar lingkungan pengujian. Keputusan ini **mempersempit** lingkungan itu, tidak melanggar batasannya |
>
> ⚠️ **Risiko §9.7 menajam.** Manajemen daya dapat membatasi G1-A10 untuk dimensi eksekusi/persistensi, sedangkan kebijakan penyedia dapat membatasi G2-C1 untuk dimensi data komunikasi sensitif. Ini tetap temuan ketersediaan per lingkungan, bukan kegagalan dan bukan sifat seluruh Android/One UI.
>
> ⚠️ **Prasyarat teknis wajib diperiksa sendiri sebelum 3.3 final.** Jalankan `getprop ro.build.version.release` dan `getprop ro.build.version.sdk`, lalu catat Android/API aktual dan pastikan kompatibel dengan `minSdk 28`. Galaxy A10 yang menjadi baseline berada pada Android 9–11, sehingga residu skenario Android 8.1/API 27 tidak berlaku.
>
> **Bila perangkat kedua kelak tersedia,** `G-05` dibuka kembali secara eksplisit sebagai keputusan baru — bukan ditambahkan diam-diam. Disiplin yang sama dengan `D-5` (`01_BREAKDOWN` §4.1.2).

### Pembagian peran sampel

| Kategori | Dipakai untuk | Perlakuan |
|---|---|---|
| **S-A simulator bukti aman** | Tier-2 dinamis, authoring, holdout, TRUE/FALSE/UNKNOWN, konflik, eksklusi, dan rekonstruksi | dibangun, dipasang, dan dijalankan terkendali |
| **S-B aplikasi benign/kontrol** | anti-klaim-berlebih pada kapabilitas/aktivitas sah | diverifikasi, lalu dapat dipasang/dijalankan terisolasi |
| **S-C APK malware nyata** | keterwakilan pola statis dan pemetaan ke profil identitas/kapabilitas | analisis statis saja; tidak dipasang/dijalankan |

> ⭐ **`[v3.0]` Sumber sampel nyata — 🔒 ditetapkan.**
>
> ⛔ **Istilah "dataset" dicabut.** MalwareBazaar dan VX-Underground **bukan dataset akademik berlabel seragam** dan **bukan perangkat lunak sumber terbuka** — berkas APK berbahaya tidak berlisensi terbuka. Istilah yang dipakai di seluruh naskah: **repositori malware yang dapat diakses publik**, dan penelitian membentuk **himpunan sampel purposif** darinya.
>
> | Peran | Sumber |
> |---|---|
> | Berkas APK dan *hash* | **MalwareBazaar** — sumber utama |
> | Cadangan bila sampel tidak tersedia | **VX-Underground** |
> | Klaim perilaku | Laporan vendor atau publikasi yang membahas sampel/keluarganya |
> | Izin, komponen, SDK | Pemeriksaan statis manifes |
>
> **CICMalDroid dan AndroZoo tidak dijadikan ketergantungan** karena aksesnya memerlukan pengajuan yang hasilnya di luar kendali peneliti. Keduanya boleh diajukan paralel, tetapi **tidak boleh menjadi penghalang jadwal**.
>
> **Model kandidat.** Kumpulkan minimum enam dan target delapan APK malware nyata; pilih tiga akhir yang mewakili komunikasi sensitif, aksesibilitas/*overlay*, serta persistensi/jaringan sejauh kandidat tersedia.
>
> ⛔ **Urutan yang mengikat: kriteria dikunci sebelum APK dipilih.** Kriteria inklusi, eksklusi, dan penggantian ditetapkan lebih dulu; baru kandidat dibandingkan dan tiga APK dipilih berikut SHA-256 serta rujukannya.
>
> ⛔ **Sampel nyata dipakai paling akhir** — setelah pengurai, skema fakta, lima keluarga APKF, dan skenario simulator dibekukan. Sampel tidak dipakai membangun aturan, mengukur ketepatan, atau menjadi keadaan sebenarnya.

## Y.3.5a Protokol APK malware nyata — 🔒 v3.3

**Perlakuan tunggal yang diizinkan: analisis statis berkas APK.** Berkas tidak dipasang, tidak diluncurkan, tidak dimuat pada perangkat fisik/AVD, dan tidak diberi jaringan.

1. Pilih kandidat setelah kriteria dan keluarga APKF dikunci; minimum enam, target delapan, tiga dipilih.
2. Unduh hanya pada VM analisis terisolasi; verifikasi nama berkas dan SHA-256 terhadap sumber.
3. Simpan sampel terenkripsi/terbatas sesuai kebijakan, tanpa sinkronisasi publik dan tanpa memasukkan biner ke Git.
4. Urai manifest, certificate/signature, permission, component, SDK/ABI, resources/config, dan string/endpoint tertanam dengan alat statis.
5. Catat alat/versi, hash, waktu akses, sumber, laporan perilaku pendamping, hasil, galat, dan alasan pilih/tolak.
6. Peta hasil hanya ke profil identitas/kapabilitas atau petunjuk statis; jangan membentuk fakta eksekusi/jaringan.
7. Bekukan matriks kandidat sebelum hasil BAB IV diringkas.

Artefak yang sah: package/versi, SHA-256, certificate, permission/komponen deklaratif, `minSdk`/`targetSdk`/ABI, strings, URL/domain/IP tertanam, dan konfigurasi. `minSdk`, `targetSdk`, serta ABI adalah metadata kompatibilitas, bukan indikator fraud.

Larangan klaim: izin diberikan, layanan aktif, package dieksekusi, komunikasi terjadi, endpoint dihubungi, payload dikirim, eksfiltrasi, atau dampak penipuan. Kecocokan statis hanya menunjukkan bahwa suatu pola deklaratif terdapat pada berkas.

APK malware nyata boleh diproses oleh pengurai dan profil **statis** APKF untuk memeriksa keterwakilan desain, tetapi tidak masuk penilaian kesesuaian runtime karena keadaan sebenarnya tidak ditetapkan peneliti. Hasilnya dilaporkan sebagai pemeriksaan relevansi statis, bukan pengujian deteksi.

## Y.3.5b Protokol simulator bukti aman — 🔒 v3.3

Pengendali host menjalankan siklus berikut pada AVD bersih:

```text
reset → install varian → seed data sintetis → lakukan aksi transparan
→ catat oracle/waktu → akuisisi allowlist → hash/simpan
→ verifikasi artefak/fakta → evaluasi APKF → bandingkan dengan ground truth
```

Kasus `FALSE` dibuat melalui keadaan yang teramati negatif, bukan penghapusan berkas. Kasus `UNKNOWN` dibuat dengan ketidaktersediaan terkontrol pada lapisan akuisisi/artefak. Kasus konflik menyediakan dua sumber sah yang tidak sejalan. Fixture eksklusioner menggunakan fakta sintetis yang secara eksplisit menahan interpretasi tertentu; bila fixture tidak tersedia, ia tidak dianggap benar.

Pengendali menolak menjalankan skenario bila hash APK, versi aturan/KB/kode, konfigurasi, atau `ground_truth.json` tidak sesuai manifest eksperimen. Seluruh log, bukti mentah, dan oracle diberi `scenario_id` yang sama.

---

### Y.3.6 ⭐ Pemetaan `availability_status` → `evidence_state` → keadaan kondisi — 🔒 *(baru v3.0)*

> **Mengapa ini wajib ada.** Tanpa pemetaan ini, BAB III 3.5 tidak dapat menerangkan **dari mana `UNKNOWN` berasal**. Penanganan bukti yang tidak teramati adalah inti kebaruan penelitian, dipakai RQ1 dan RQ3, dan kontraknya sudah **terbit** di naskah BAB II 2.1.13. Sampai v2.9 rantainya putus: `availability_status` didefinisikan di `01_BREAKDOWN` §8, `evidence_state` di §Y.3.4, keadaan kondisi di §Z — dan tidak ada satu pun yang menghubungkan ketiganya.

**Rantai tiga lapis:**

```text
availability_status   (hasil akuisisi — melekat pada Evidence)
        ↓
evidence_state        (hasil penormalisasi — melekat pada NormalizedEvent)
        ↓
keadaan kondisi       (dibaca mesin aturan — TRUE / FALSE / UNKNOWN)
```

| `availability_status` | Arti | `evidence_state` | Keadaan kondisi |
|---|---|---|---|
| `acquired` | Operasi berhasil dan keluarannya terurai | `observed_true` **atau** `observed_false` menurut isi fakta | **TRUE** atau **FALSE** |
| `unavailable` | Operasi berjalan, sumber tidak memuat data yang dicari | `unknown_unavailable` | **UNKNOWN** |
| `denied` | Operasi ditolak karena izin atau kebijakan perangkat | `unknown_unavailable` | **UNKNOWN** |
| `unsupported` | Operasi tidak tersedia pada versi Android atau antarmuka OEM tersebut | `unknown_unavailable` | **UNKNOWN** |
| `failed` | Operasi gagal secara teknis — galat, waktu habis, keluaran rusak | `unknown_unavailable` | **UNKNOWN** |

**Ketentuan yang mengikat:**

1. ⛔ **Hanya `acquired` yang dapat menghasilkan FALSE.** Empat status lain **tidak pernah** menjadi FALSE. Ini penerapan langsung `00_SESSION_STARTER` §5: *missing evidence = UNKNOWN, bukan otomatis FALSE*.
2. **Pembedaan antar keempat status tidak hilang**, hanya tidak masuk logika aturan. Alasannya disimpan pada `availability_reason` (§Y.1) dan **wajib ditampilkan** pada panel keterlacakan serta laporan. Pemeriksa perlu tahu bedanya *ditolak izin* dan *tidak didukung versi*; mesin aturan tidak.
3. `acquired` **tidak otomatis** TRUE. Akuisisi berhasil yang menunjukkan izin **tidak** diberikan menghasilkan `observed_false` → FALSE. Keberhasilan akuisisi dan nilai fakta adalah dua hal berbeda.
4. Pemetaan ditetapkan **penormalisasi secara deterministik**, bukan penulis aturan — ketentuan yang sama dengan `epistemic_class` (§Y.3.2 butir 4).
5. **Untuk pelaporan per lingkungan** (`01_BREAKDOWN` §9.7), status disimpan **apa adanya**, tidak diciutkan menjadi UNKNOWN. Penciutan hanya terjadi saat fakta dibaca mesin aturan.

**Padanan Indonesia — 🔒 menutup kebutuhan `01_BREAKDOWN` §4.7.3:**

| Status | Padanan naskah |
|---|---|
| `acquired` | **diperoleh** |
| `unavailable` | **tidak tersedia** |
| `denied` | **ditolak** |
| `unsupported` | **tidak didukung** |
| `failed` | **gagal** |

⚠️ **`B3-09` berlaku di sini.** Kelima padanan menerangkan **status ketersediaan bukti**; ia bukan keadaan kondisi (terpenuhi · tidak terpenuhi · tidak diketahui) dan bukan keadaan aturan (terpenuhi · tidak terpenuhi · bukti tidak memadai). Ketiganya tidak boleh dicampur dalam satu kalimat naskah.

---

# Z. KONTRAK IMPLEMENTASI MESIN RULE (RULE ENGINE)

Status kondisi:

```text
TRUE
FALSE
UNKNOWN
```

Hasil rule:

```text
matched
not_matched
insufficient_evidence
```

Rule:

```yaml
family_id: APKF-K01
profile_id: APKF-K01-P01
reference_ids:
  - KB-SRC-...
claim_level: capability
unknown_handling:
  required_unknown: insufficient_evidence
  optional_unknown: annotate
  exclusionary_unknown: do_not_exclude
```

Lima `family_id` aktif: `APKF-K01` komunikasi sensitif, `APKF-K02` akses khusus, `APKF-K03` persistensi/trigger, `APKF-K04` eksekusi package, dan `APKF-K05` jaringan UID/package. Satu keluarga dapat memuat beberapa profil bukti; profil bukan wildcard.

## Z.0 Baseline implementasi 16 profil — 🔒 Generate 1.5

YAML lengkap kelima keluarga berada di `01_BREAKDOWN` §14.2 dan merupakan sumber kebenaran desain. Implementasi membuat satu berkas `family.yaml` per keluarga:

| Berkas | Profil | Lingkup |
|---|---:|---|
| `APKF-K01/family.yaml` | 3 | izin komunikasi sensitif runtime dan deklarasi statis |
| `APKF-K02/family.yaml` | 4 | aksesibilitas, overlay, listener notifikasi, dan deklarasi statis |
| `APKF-K03/family.yaml` | 3 | deklarasi pemicu terpasang/statis dan eksekusi terpicu |
| `APKF-K04/family.yaml` | 3 | riwayat penggunaan, activity resumed, dan process running |
| `APKF-K05/family.yaml` | 3 | netstats UID serta dua profil jaringan khusus validasi |

Setiap keluarga/profil wajib lolos validasi skema berikut sebelum aktif:

- `schema_version`, `family_id`, `version`, `status`, `incident_scope`, `reference_ids`, `aggregation`, `unknown_handling`, dan `conflict_handling` tersedia;
- `profile_id` unik global dan diawali `family_id`;
- `applicability.evidence_modes`, `applicability.run_purposes`, `claim_level`, `subject_binding`, `time_binding`, empat daftar peran kondisi, dan `output` tersedia;
- setiap kondisi memiliki `condition_id`, `fact`, `source_group`, `expects_epistemic_class`, `operator`, serta parameter operator yang diperlukan;
- `fact` terdaftar di §Y.3.1a dan kelasnya identik dengan `expects_epistemic_class`;
- setiap `reference_id` dapat diresolusikan ke `KB_Source` aktif;
- setiap profil mewarisi `unknown_handling` dan `conflict_handling` keluarga; override per profil dilarang pada baseline agar semantik keluaran tidak berbeda diam-diam;
- profil `validation_only` ditolak bila `run_purpose=production` atau `evidence_mode=apk_static`.

### Z.0.1 Selector dan operator

Operator yang didukung pada baseline: `exists`, `equals`, `in`, `greater_than`, `delta_greater_than`, dan `overlaps_window`. Evaluator selalu menerapkan urutan:

```text
pilih evidence_mode + run_purpose
→ saring profil pada kedua sumbu applicability
→ ikat subject package/UID/scenario
→ ikat current/observation/case/bucket window
→ pilih fakta menurut event_type + filter nilai
→ cek availability dan parse coverage
→ hasilkan TRUE/FALSE/UNKNOWN
```

Tidak ditemukannya fakta hanya menjadi `FALSE` bila sumber relevan `acquired`, penguraian berhasil, dan cakupan selector lengkap. Selain itu hasilnya `UNKNOWN`. Konflik antarfakta yang sama-sama valid juga menghasilkan `UNKNOWN/conflicting_evidence`.

Evaluator memperlakukan `predicate_value` sebagai nilai kebenaran observasi. Untuk `exists`/`equals`/`in`, satu fakta positif yang cocok menghasilkan `TRUE`; seluruh sasaran yang secara eksplisit negatif pada cakupan lengkap menghasilkan `FALSE`; kombinasi yang belum tertutup menghasilkan `UNKNOWN`. Untuk pembanding numerik, nilai sah yang tidak melewati batas menghasilkan `FALSE`. `overlaps_window` hanya boleh `FALSE` bila keseluruhan jendela pencarian telah dicakup; peristiwa di luar jendela tidak membuktikan ketiadaan peristiwa di dalamnya.

### Z.0.2 Applicability dan agregasi

`evidence_mode` bernilai `installed_runtime` atau `apk_static`. `run_purpose` bernilai `authoring`, `holdout`, `benign_control`, atau `production`. Profil hanya dievaluasi bila kedua nilai tersebut terdapat pada `applicability`; profil yang tidak berlaku dicatat dengan `evaluation_status=skipped_not_applicable` dan `outcome=NULL`, lalu dikeluarkan dari agregasi. Bila tidak ada profil yang berlaku, keluarga menghasilkan `insufficient_evidence/no_applicable_profile`.

Agregasi hanya memakai profil dengan `evaluation_status=evaluated`. Nilai keluaran tetap tiga keadaan; `skipped_not_applicable` adalah status proses, bukan keadaan aturan keempat.

Siklus status YAML: `design_baseline` → `authoring_candidate` → `frozen_for_holdout`. Loader pengembangan boleh memuat dua status pertama; eksekusi *holdout* hanya menerima `frozen_for_holdout` beserta hash yang cocok dengan `freeze_manifest.json`. Penggunaan produksi prototipe juga menolak `design_baseline`.

### Z.0.3 Fixture eksklusioner

Fixture adapter boleh membuat `synthetic_exclusion_marker_observed` hanya ketika `run_purpose` bernilai `authoring` atau `holdout`. Harness mengkloning profil sasaran dan menambahkan kondisi eksklusioner sementara dengan `validation_only=true`; YAML produksi tidak diubah. Ketika marker `TRUE`, `interpretation_status=constrained` dan temuan diblokir dari rekonstruksi pada tingkat klaim yang ditentukan, tetapi fakta wajib yang benar tidak dipalsukan menjadi `FALSE`. Marker ditolak ketika `run_purpose=production` dan tidak dipakai untuk melabeli aplikasi benign dunia nyata.

Agregasi:

```text
required per profil → outcome profil
profil matched ada → outcome keluarga matched
semua profil not_matched → outcome keluarga not_matched
selain itu, bila ada insufficient_evidence → outcome keluarga insufficient_evidence
```

`any_of` hanya menerima event type yang setara secara semantik dan `claim_level` sama. Kondisi komplementer, kontekstual, dan eksklusioner disimpan sebagai peran berbeda. Fakta valid yang bertentangan menghasilkan `UNKNOWN` dengan `reason=conflicting_evidence`.

Pisahkan jalur semua keluaran:

```text
RuleProfileEvaluation               ← selalu dibuat per profil
├── matched → CorrelationFinding    ← maksimum satu per profil matched
├── not_matched/insufficient/skipped → tanpa temuan
└── RuleFamilyEvaluation            ← agregasi selalu dibuat per keluarga
                     └→ temuan dari ≥2 keluarga berbeda
                         → ReconstructionFinding → ReconstructionRun → InvestigationHypothesis
```

Jangan menciutkan evaluasi, temuan, dan hipotesis menjadi “malware detected”.

---

## Z.1 ⭐ Kewajiban pencatatan mesin aturan — 🔒 *(baru v3.0)*

Mesin aturan **wajib mencatat setiap kondisi yang dievaluasi**, bukan hanya kondisi yang terpenuhi, dan bukan hanya untuk aturan yang menghasilkan temuan. Tanpa ini, uji keterlacakan dan uji konsistensi BAB III 3.6 tidak dapat memeriksa skenario B dan D2.

Urutan yang mengikat: buat evaluasi profil → tulis setiap `RuleConditionResult` → hubungkan fakta lewat `RuleConditionFact` → agregasikan profil ke keluarga → buat maksimum satu `CorrelationFinding` untuk setiap profil `matched` → kelompokkan temuan menurut keluarga berbeda, package/UID, dan waktu → susun hipotesis tanpa melampaui `claim_level`. Rinciannya di §AA.1.

`ReconstructionRun` hanya dibuat bila ada sedikitnya dua temuan dari keluarga berbeda dengan subject key dan jendela waktu kompatibel. Rekonstruksi urutan kejadian juga memerlukan sedikitnya satu temuan `observed_activity`; selain itu sistem berhenti pada temuan tingkat rendah.

---

# AA. MODEL BASIS DATA (DATABASE)

Operasional:

```text
User
Agent
Case
Device
CaseDevice
AcquisitionSession
AcquisitionOperation
Evidence
Artifact
NormalizedEvent
CorrelationRun
RuleFamilyEvaluation
RuleProfileEvaluation
RuleConditionResult
RuleConditionFact
CorrelationFinding
ReconstructionRun
ReconstructionFinding
InvestigationHypothesis
Report
AuditLog
```

Knowledge/rule:

```text
KB_Source
KB_ArtifactDefinition
KB_Behavior
KB_BehaviorCondition
KB_Technique
KB_Tactic
KB_BehaviorTechniqueMap
RuleMetadata
RuleReference
RuleElementReference
```

Pilihan v3.3 dikunci pada tabel terpisah: `RuleFamilyEvaluation`, `RuleProfileEvaluation`, `ReconstructionRun`, dan `ReconstructionFinding`. `RuleEvaluation` tunggal pada v3.2 disupersesi agar keluaran profil dan agregasi keluarga tidak bercampur.

---

## AA.1 ⭐ Jalur pencatatan evaluasi aturan — 🔒 *(baru v3.0)*

> **Masalah yang ditutup.** Sampai v2.9, hasil kondisi melekat pada `CorrelationFinding`, dan `CorrelationFinding` hanya lahir ketika aturan terpenuhi. Akibatnya skenario **B** (`not_matched`) dan **D2** (`insufficient_evidence`) **tidak meninggalkan rekaman apa pun** yang dapat diaudit — padahal justru D2 tempat kebaruan penelitian ini diuji. Uji keterlacakan dan uji konsistensi BAB III 3.6 mustahil dijalankan atas keduanya.
>
> Selain itu `FindingEvidence` **dicabut sebagai jalur langsung**. Mempertahankannya berdampingan dengan pencatatan kondisi menghasilkan **dua jalur keterlacakan yang dapat berselisih**, dan sistem yang punya dua jawaban untuk satu pertanyaan lebih buruk daripada yang tidak punya jawaban.

```text
CorrelationRun
    ↓
RuleProfileEvaluation       ← selalu dibuat per profil
    ↓
RuleConditionResult         ← satu baris per kondisi yang dievaluasi
    ↓
RuleConditionFact           ← penghubung M:N; kosong bila UNKNOWN
    ↓
NormalizedEvent → Artifact → Evidence

RuleFamilyEvaluation        ← agregasi seluruh profil keluarga
    ↓ hanya bila terpenuhi
CorrelationFinding
    ↓
ReconstructionFinding       ← penghubung M:N temuan–rekonstruksi
    ↓
ReconstructionRun           ← mengikat package/UID dan jendela waktu
    ↓
InvestigationHypothesis
```

**Ketentuan yang mengikat:**

| # | Ketentuan |
|---|---|
| 1 | Setiap profil menghasilkan satu `RuleProfileEvaluation`, dan setiap keluarga menghasilkan satu `RuleFamilyEvaluation`, apa pun keluarannya |
| 2 | Setiap kondisi menghasilkan `RuleConditionResult` berisi peran (wajib, opsional, kontekstual, eksklusioner), keadaan, dan alasan bila UNKNOWN/konflik |
| 3 | Kondisi **TRUE dan FALSE** wajib memiliki sekurang-kurangnya satu `RuleConditionFact`. FALSE adalah pengamatan negatif yang sah dan **harus punya fakta penopang** — inilah yang membedakannya dari UNKNOWN di tingkat data |
| 4 | Kondisi **UNKNOWN** memiliki nol `RuleConditionFact`, tetapi **wajib** membawa alasan. ⛔ Dilarang membuat fakta semu hanya agar barisnya terisi |
| 5 | `CorrelationFinding` lahir maksimum satu dari setiap evaluasi profil `matched` dan menunjuk evaluasi profil serta keluarganya. Hipotesis disusun dari temuan kompatibel milik sedikitnya dua keluarga berbeda melalui `ReconstructionRun`, bukan langsung dari satu kondisi wajib |
| 6 | `not_matched` dan `insufficient_evidence` **tidak** menghasilkan temuan maupun hipotesis, tetapi evaluasinya **tetap tersimpan lengkap** |
| 7 | **Nama entitas penghubung adalah `RuleConditionFact`, bukan `RuleConditionEvidence`.** Ia menunjuk `NormalizedEvent` (fakta), sementara core memiliki entitas terpisah bernama `Evidence` (bukti mentah). Nama yang memakai kata *Evidence* akan menyesatkan pembaca ERD ke jalur yang salah |
| 8 | Setiap `reference_id` menghasilkan relasi ke `KB_Source`; `RuleElementReference` menambahkan `rule_element_key`, `reference_role`, `extracted_claim`, `version_scope`, dan `verification_status` |
| 9 | `claim_level` tersimpan pada profil dan temuan; penyusun hipotesis menolak kalimat yang memerlukan tingkat klaim lebih tinggi daripada semua temuan penopang |

Jumlah entitas tidak dikunci sebagai klaim naskah. ERD BAB III menampilkan entitas inti dan kardinalitas; kamus data lengkap berada di repositori penelitian.

**Keterlacakan dua arah berjalan di jalur ini:**

| Arah | Jalur |
|---|---|
| Evaluasi → bukti | `RuleProfileEvaluation` → `RuleConditionResult` → `RuleConditionFact` → `NormalizedEvent` → `Artifact` → `Evidence` |
| Temuan → evaluasi | `CorrelationFinding` → `RuleProfileEvaluation` → `RuleFamilyEvaluation` |
| Rekonstruksi | `InvestigationHypothesis` → `ReconstructionRun` → temuan → evaluasi/fakta |
| Aturan → rujukan | evaluasi → `RuleMetadata`/elemen → `RuleElementReference` → `KB_Source` |

## AA.2 Atribut inti tambahan v3.3

| Entitas | Atribut wajib minimum |
|---|---|
| `RuleMetadata` | `family_id`, `profile_id`, `version`, `applicability`, `claim_level`, `incident_scope`, `status`, `content_hash` |
| `RuleProfileEvaluation` | `correlation_run_id`, `rule_id`, `profile_id`, `evidence_mode`, `run_purpose`, `evaluation_status`, `outcome` nullable, `interpretation_status`, `reason`, `evaluated_at` |
| `RuleFamilyEvaluation` | `correlation_run_id`, `family_id`, `evidence_mode`, `run_purpose`, `outcome`, `matched_profile_ids`, `interpretation_status`, `reason` |
| `RuleConditionResult` | `profile_evaluation_id`, `condition_key`, `role`, `operator`, `selector_json`, `state`, `reason`, `conflict_reason` |
| `RuleElementReference` | `rule_id`, `rule_element_key`, `source_id`, `reference_role`, `extracted_claim`, `version_scope`, `verification_status` |
| `CorrelationFinding` | `family_evaluation_id`, `profile_evaluation_id`, `claim_level`, `interpretation_status`, `blocked_from_reconstruction`, `subject_package`, `subject_uid`, `window_start`, `window_end`, `summary` |
| `ReconstructionRun` | `correlation_run_id`, `subject_package`, `subject_uid`, `window_start`, `window_end`, `status` |
| `ReconstructionFinding` | `reconstruction_run_id`, `finding_id`, `sequence_order`, `relation_type` |
| `InvestigationHypothesis` | `reconstruction_run_id`, `statement`, `support_scope`, `missing_evidence`, `created_at`; imutabel per run |

Kardinalitas inti: satu keluarga memiliki satu atau lebih profil; satu evaluasi keluarga memiliki satu atau lebih evaluasi profil; satu evaluasi profil berstatus `evaluated` memiliki satu atau lebih hasil kondisi, sedangkan `skipped_not_applicable` tidak memilikinya; satu hasil kondisi dapat ditopang nol atau lebih fakta (nol hanya untuk `UNKNOWN`); satu evaluasi profil `matched` menghasilkan paling banyak satu temuan; satu rekonstruksi memakai sedikitnya dua temuan dari keluarga berbeda; satu temuan dapat dipakai pada nol atau lebih rekonstruksi.

---

# AB. API DAN WEBSOCKET

REST:

```text
POST   /api/auth/login
GET    /api/health

GET    /api/cases
POST   /api/cases
GET    /api/cases/{case_id}

GET    /api/agents
GET    /api/devices

POST   /api/acquisitions
GET    /api/acquisitions/{session_id}

POST   /api/evidence/upload
GET    /api/evidence/{evidence_id}

GET    /api/cases/{case_id}/artifacts
GET    /api/cases/{case_id}/events

POST   /api/cases/{case_id}/analyze
GET    /api/cases/{case_id}/evaluations
GET    /api/cases/{case_id}/findings

GET    /api/cases/{case_id}/report
```

`/evaluations` mengembalikan evaluasi keluarga, seluruh profil dan kondisi, termasuk tidak terpenuhi, bukti tidak memadai, profil tidak berlaku, dan konflik. `/findings` hanya mengembalikan temuan dari profil `matched`, masing-masing dengan identitas keluarga. Tambahkan `GET /api/cases/{case_id}/reconstructions` untuk hipotesis dan urutan temuan.

WebSocket:

```text
/ws/agent
/ws/dashboard
```

WebSocket untuk:
- heartbeat/status;
- job notification;
- progress;
- completion/error.

Evidence bytes tetap via HTTP upload.

---

# AC. ANTARMUKA WEB (FRONTEND) MVP

Halaman:

```text
/login
/dashboard
/cases
/cases/:id
/cases/:id/device
/cases/:id/acquisition
/cases/:id/evidence
/cases/:id/events
/cases/:id/evaluations
/cases/:id/findings
/cases/:id/reconstruction
/cases/:id/report
```

Komponen:

```text
AppShell
CaseTable
CaseSummary
AgentStatus
DeviceCard
AcquisitionPanel
AcquisitionProgress
EvidenceTable
ArtifactTable
EventTimeline
EvaluationTable
FamilyProfilePanel
ConditionResultTable
FindingCard
EvidenceTracePanel
MissingEvidenceBadge
ConflictEvidenceBadge
ClaimLevelBadge
RuleReferencePanel
ReferenceRolePanel
ReconstructionTimeline
ReportPreview
```

Wireframe BAB III wajib memperlihatkan satu layar hasil dengan tiga tingkat: daftar keluarga/evaluasi, detail profil/kondisi, serta panel keterlacakan. Panel membedakan:

- **basis bukti:** fakta, artefak, bukti mentah, hash, dan status akuisisi;
- **basis aturan:** keluarga, profil, kondisi, peran, keadaan, dan `claim_level`;
- **basis pengetahuan:** sumber, elemen aturan yang ditopang, peran rujukan, klaim yang diekstrak, cakupan versi, dan status verifikasi.

`UNKNOWN` menampilkan alasan; konflik menampilkan semua fakta yang bertentangan; `not_matched` dan `insufficient_evidence` tetap dapat dibuka; rekonstruksi hanya menampilkan urutan yang didukung dan bukti yang belum teramati.

---

# AD. KONTROL KEAMANAN MINIMUM

- investigator authentication;
- password hashing;
- JWT/session token;
- unique agent token;
- `.env` secrets;
- HTTPS/WSS untuk deployment/demo private-LAN bila memungkinkan;
- allowlisted operations;
- upload validation;
- path traversal prevention;
- server-side SHA-256;
- immutable raw evidence;
- audit log;
- restricted CORS;
- database user non-superuser;
- no arbitrary remote ADB shell;
- no malware binaries/raw personal evidence in Git.

---

# AE. TARGET STRUKTUR REPOSITORI LENGKAP

Ini adalah **target MVP**, bukan checklist file hari pertama.

```text
android-forensic-platform/
│
├── agent/
│   ├── src/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── logging_config.py
│   │   ├── models.py
│   │   ├── exceptions.py
│   │   │
│   │   ├── device/
│   │   │   ├── __init__.py
│   │   │   ├── device_detection.py
│   │   │   ├── adb_controller.py
│   │   │   ├── adb_commands.py
│   │   │   └── privilege_detector.py
│   │   │
│   │   ├── acquisition/
│   │   │   ├── __init__.py
│   │   │   ├── acquisition_profiles.py
│   │   │   ├── command_allowlist.py
│   │   │   ├── evidence_writer.py
│   │   │   └── acquisition_runner.py
│   │   │
│   │   ├── integrity/
│   │   │   ├── __init__.py
│   │   │   └── hashing.py
│   │   │
│   │   ├── transport/
│   │   │   ├── __init__.py
│   │   │   ├── api_client.py
│   │   │   ├── uploader.py
│   │   │   ├── ws_client.py
│   │   │   └── heartbeat.py
│   │   │
│   │   ├── security/
│   │   │   ├── __init__.py
│   │   │   └── auth.py
│   │   │
│   │   └── state/
│   │       ├── __init__.py
│   │       ├── state_machine.py
│   │       └── audit_logger.py
│   │
│   ├── tests/
│   │   ├── unit/
│   │   ├── integration/
│   │   └── fixtures/
│   ├── requirements.txt
│   ├── requirements-dev.txt
│   ├── .env.example
│   ├── pyproject.toml
│   └── build.spec
│
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── security.py
│   │   │   ├── logging.py
│   │   │   └── constants.py
│   │   ├── api/
│   │   │   ├── deps.py
│   │   │   └── routes/
│   │   │       ├── auth.py
│   │   │       ├── cases.py
│   │   │       ├── agents.py
│   │   │       ├── devices.py
│   │   │       ├── acquisitions.py
│   │   │       ├── evidence.py
│   │   │       ├── events.py
│   │   │       ├── evaluations.py
│   │   │       ├── findings.py
│   │   │       └── reports.py
│   │   ├── ws/
│   │   │   ├── manager.py
│   │   │   ├── agent_ws.py
│   │   │   └── dashboard_ws.py
│   │   ├── db/
│   │   │   ├── base.py
│   │   │   ├── session.py
│   │   │   └── init_db.py
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── parsing/
│   │   │   ├── base.py
│   │   │   ├── registry.py
│   │   │   ├── package_state/
│   │   │   ├── usage_stats/
│   │   │   ├── settings_state/
│   │   │   ├── sensitive_provider/
│   │   │   ├── network_stats/
│   │   │   └── apk_static/
│   │   ├── normalization/
│   │   │   ├── event_schema.py
│   │   │   ├── normalizer.py
│   │   │   ├── temporal.py
│   │   │   └── subject_resolution.py
│   │   ├── research/
│   │   │   ├── knowledge_base/
│   │   │   │   ├── loader.py
│   │   │   │   ├── validator.py
│   │   │   │   └── data/
│   │   │   │       ├── sources.yaml
│   │   │   │       ├── artifact_definitions.yaml
│   │   │   │       ├── behaviors.yaml
│   │   │   │       └── technique_mappings.yaml
│   │   │   ├── rules/
│   │   │   │   ├── loader.py
│   │   │   │   ├── validator.py
│   │   │   │   └── data/
│   │   │   │       └── apk_fraud/
│   │   │   │           ├── APKF-K01/family.yaml
│   │   │   │           ├── APKF-K02/family.yaml
│   │   │   │           ├── APKF-K03/family.yaml
│   │   │   │           ├── APKF-K04/family.yaml
│   │   │   │           └── APKF-K05/family.yaml
│   │   │   ├── rule_engine.py
│   │   │   ├── correlation_engine.py
│   │   │   ├── hypothesis_builder.py
│   │   │   └── traceability.py
│   │   └── reporting/
│   ├── alembic/
│   │   ├── versions/
│   │   ├── env.py
│   │   └── script.py.mako
│   ├── tests/
│   ├── requirements.txt
│   ├── requirements-dev.txt
│   ├── alembic.ini
│   ├── .env.example
│   └── pyproject.toml
│
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── main.tsx
│   │   ├── App.tsx
│   │   ├── router.tsx
│   │   ├── api/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── hooks/
│   │   ├── types/
│   │   ├── utils/
│   │   └── styles/
│   ├── package.json
│   ├── package-lock.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   ├── eslint.config.js
│   └── .env.example
│
├── android-test-apps/
│   ├── README.md
│   ├── safe-evidence-simulator/
│   ├── scenario-controller/
│   ├── local-endpoint/
│   └── benign-control-catalog/
│
├── experiments/
│   ├── feasibility_tier2/
│   │   ├── protocols/
│   │   ├── logs/
│   │   ├── raw_outputs/
│   │   └── results/
│   ├── controlled_scenarios/
│   ├── authoring_cases/       # minimum 20, termasuk konflik/eksklusioner
│   ├── holdout_cases/         # target 8 bundel tersegel
│   ├── static_sample_candidates/
│   ├── ground_truth/
│   └── results/
│
├── api-collections/
│   └── bruno/
│
├── var/
│   ├── evidence/
│   ├── uploads/
│   └── reports/
│
├── scripts/
│   ├── dev/
│   ├── adb/
│   ├── db/
│   └── experiments/
│
├── docs/
│   ├── architecture.md
│   ├── setup.md
│   ├── acquisition_profiles.md
│   ├── evidence_source_matrix.md
│   ├── normalized_event_schema.md
│   ├── rule_authoring.md
│   ├── test_protocol.md
│   ├── sample_selection.md
│   ├── simulator_safety_contract.md
│   ├── data_dictionary.md
│   ├── diagrams/              # .drawio + exported PNG
│   └── changelog.md
│
├── infra/
│   └── postgres/
│
├── docker-compose.yml
├── .env.example
├── .gitignore
├── .gitattributes
├── README.md
└── LICENSE   # optional; jangan tentukan lisensi publik sebelum kebijakan skripsi/repo diputuskan
```

---

# AF. KERANGKA (SCAFFOLD) MINIMUM HARI PERTAMA

```text
android-forensic-platform/
├── agent/
│   ├── src/main.py
│   ├── src/adb_controller.py
│   ├── requirements.txt
│   └── .env.example
├── backend/
│   ├── app/main.py
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   └── <Vite React-TS scaffold>
├── experiments/
├── docs/
├── docker-compose.yml
├── .gitignore
├── .gitattributes
└── README.md
```

Setelah vertical slice berjalan, baru grow ke target tree.

---

# AG. KONTROL VERSI (VERSION CONTROL) — SETUP LENGKAP

## AG.1 Rekomendasi

Gunakan:

```text
Git lokal
+
GitHub Free private repository sebagai origin
```

Kenapa:
- Git gratis/open source;
- history lokal tetap ada;
- GitHub Free memberi private repo tanpa biaya;
- remote menjadi backup kedua;
- mudah dipakai untuk tag milestone, Issues, dan optional GitHub Actions.

GitLab Free boleh menjadi alternatif, **bukan tambahan wajib**.

## AG.2 Buat repository GitHub

1. Login/buat akun GitHub.
2. Buat repository:
   - nama: `android-forensic-platform`
   - visibility: **Private**
   - jangan auto-generate README jika repository lokal sudah dibuat.
3. Aktifkan 2FA akun.
4. Jangan upload evidence/raw sample ke repository.

## AG.3 Initialisasi repository lokal

Dari folder proyek:

```bash
git init -b main
git config user.name "Nama Lu"
git config user.email "email-lu@example.com"
```

Cek:

```bash
git status
git config --list
```

## AG.4 `.gitignore` minimum

```gitignore
# ===== Secrets =====
.env
.env.*
!.env.example
*.pem
*.key
*.p12
*.jks
*.keystore

# ===== Python =====
**/.venv/
__pycache__/
*.py[cod]
.pytest_cache/
.mypy_cache/
.ruff_cache/
.coverage
htmlcov/

# ===== Node / Frontend =====
frontend/node_modules/
frontend/dist/
frontend/.vite/
npm-debug.log*
yarn-error.log*

# ===== Android / Gradle =====
**/.gradle/
**/build/
**/local.properties
*.apk
*.aab

# ===== Runtime Evidence =====
var/
experiments/**/raw_outputs/
experiments/**/logs/private/
*.pcap
*.pcapng

# ===== Raw / Malware Samples =====
samples/
malware/
evidence/
*.img
*.bin

# ===== Database local =====
*.sqlite
*.sqlite3

# ===== IDE / OS =====
.idea/
.vscode/settings.json
.DS_Store
Thumbs.db

# ===== Python build =====
build/
dist/
*.spec.tmp
```

Catatan:
- `protocols/`, scenario definition, sanitized result JSON/CSV boleh di-commit.
- raw output yang mengandung sensitive data jangan di-commit.
- generated benign APK binary di-ignore; source Kotlin tetap di-commit.

## AG.5 `.gitattributes`

Untuk konsistensi Windows/Linux:

```gitattributes
* text=auto

*.py   text eol=lf
*.md   text eol=lf
*.yml  text eol=lf
*.yaml text eol=lf
*.json text eol=lf
*.ts   text eol=lf
*.tsx  text eol=lf
*.sh   text eol=lf

*.ps1  text eol=crlf
*.bat  text eol=crlf

*.png  binary
*.jpg  binary
*.jpeg binary
*.pdf  binary
*.docx binary
```

## AG.6 Initial commit

```bash
git add .
git status
git commit -m "chore(repo): initialize android forensic platform"
```

## AG.7 Hubungkan ke GitHub remote

HTTPS:

```bash
git remote add origin https://github.com/USERNAME/android-forensic-platform.git
git push -u origin main
```

Atau SSH:

```bash
ssh-keygen -t ed25519 -C "email-lu@example.com"
```

Tambahkan public key ke GitHub, lalu:

```bash
git remote add origin git@github.com:USERNAME/android-forensic-platform.git
git push -u origin main
```

Cek:

```bash
git remote -v
```

## AG.8 Branching strategy — rekomendasi untuk solo researcher

**Jangan pakai GitFlow kompleks.**

Gunakan:

```text
main
feature/<nama>
fix/<nama>
experiment/<nama>
docs/<nama>
```

Contoh:

```text
feature/agent-device-detection
feature/package-acquisition
feature/backend-case-api
feature/parser-package-state
feature/rule-engine
feature/frontend-findings

experiment/tier2-api36
experiment/holdout-v1

fix/netstats-parser
docs/bab3-methodology
```

### Aturan `main`

`main` harus:
- build/run;
- tidak berisi experiment code yang rusak;
- tidak mengandung secrets;
- bisa dipakai untuk demo milestone terbaru.

Alur kerja:

```bash
git switch -c feature/agent-device-detection

# kerja
git add agent/
git commit -m "feat(agent): add adb device polling"

git switch main
git pull
git merge --no-ff feature/agent-device-detection
git push
git branch -d feature/agent-device-detection
```

Untuk proyek solo, branch `dev` **tidak wajib**. Tambahkan hanya jika nanti ada banyak parallel feature yang perlu integration staging.

## AG.9 Commit convention

Gunakan Conventional-Commit-like prefix:

```text
feat:
fix:
refactor:
test:
docs:
chore:
experiment:
```

Contoh:

```text
feat(agent): detect adb device and metadata
feat(acquisition): add package-state acquisition profile
feat(parser): parse granted permission state
feat(normalization): add current-state temporal semantics
feat(research): add APKF-K01 evidence profiles
fix(network): correct uid parsing in netstats
test(correlation): cover required unknown evidence
experiment(tier2): record api36 sms provider result
docs(method): update evidence-selection rationale
chore(deps): freeze backend requirements
```

Satu commit idealnya memiliki satu tujuan logis.

## AG.10 Tag milestone

Milestone pengembangan:

```bash
git tag -a v0.05 -m "Toolchain installed and AVD ADB smoke test"
git push origin v0.05
```

Lalu:
```text
v0.10
v0.20
v0.30
...
v1.00
```

## AG.11 Rule freeze dan evaluation freeze

Lima `family.yaml` pada `01_BREAKDOWN` §14.2 berstatus `design_baseline`: cukup lengkap untuk implementasi, diagram, dan BAB III, tetapi belum diklaim sebagai konfigurasi empiris final. Selama *authoring*, perubahan hanya boleh berada dalam batas `01_BREAKDOWN` §14.3. Perubahan semantik terhadap keluarga, fakta wajib, peran kondisi, agregasi, tingkat klaim, eksklusi, atau gerbang rekonstruksi wajib membuka amandemen core sebelum *holdout*.

Setelah minimum 20 kasus *authoring* selesai, naikkan versi keluarga/profil yang berubah dan buat `freeze_manifest.json` yang menyimpan hash lima YAML, pemetaan normalisasi, registri KB, kode, konfigurasi skenario, APK simulator, dan seluruh bundel *holdout*. Baru setelah itu:

```bash
git tag -a rules-v1-freeze -m "Rule set frozen before holdout evaluation"
git push origin rules-v1-freeze
```

Setiap experiment result harus menyimpan:

```text
git_commit
git_tag
family_id
profile_id
rule_version
parser_version
android_build
platform_tools_version
```

Contoh mengambil SHA:

```bash
git rev-parse HEAD
```

**Jika rule diubah setelah holdout dibuka:**
- jangan overwrite result lama;
- increment rule version;
- buat commit baru;
- kasus yang sudah dilihat tidak lagi dianggap holdout untuk rule baru.

## AG.12 Version control untuk Knowledge Base dan rules

YAML harus di-version-control.

Contoh:

```text
rules/apk_fraud/APKF-K01/family.yaml
knowledge_base/data/sources.yaml
knowledge_base/data/behaviors.yaml
```

Perubahan rule harus punya:
- Git commit;
- `rule_family.version` dan versi profil bila skema implementasi memisahkannya;
- rationale di commit message/changelog;
- reference perubahan.

## AG.13 Version control untuk experiment

Yang **boleh di-commit**:
- protocol;
- scenario definition;
- test script;
- anonymized/sanitized expected result;
- summary CSV/JSON;
- analysis notebook/script jika nanti digunakan.

Yang **jangan di-commit**:
- raw SMS/contact dump asli;
- evidence pribadi;
- malware sample;
- access token;
- database dump berisi evidence;
- large raw ADB output jika sensitif.

## AG.14 Backup repository

Minimum backup:

```text
Laptop local Git repo
+
GitHub private origin
```

Optional offline snapshot:

```bash
git bundle create ../backup-android-forensic-YYYYMMDD.bundle --all
```

Simpan bundle di storage terpisah.

## AG.15 GitHub Actions — optional

Tidak perlu pada hari pertama.

Saat testing sudah stabil, optional workflow:
- Python unit tests;
- frontend lint/build.

GitHub Free memiliki quota Actions, tetapi thesis MVP tidak membutuhkan CI kompleks.

## AG.16 Git LFS

**Jangan gunakan Git LFS sebagai alasan untuk menyimpan raw evidence/malware di GitHub.**

Raw evidence tetap di:
```text
var/evidence/
experiments/.../raw_outputs/
```

Git untuk:
- source code;
- configs;
- rule/KB;
- protocols;
- sanitized results.

---

# AH. SETUP KUALITAS KODE

## AH.1 Python

Direkomendasikan:

```text
Ruff
pytest
mypy (optional)
pre-commit (optional)
```

Example `pyproject.toml`:

```toml
[tool.ruff]
line-length = 100
target-version = "py313"

[tool.pytest.ini_options]
testpaths = ["tests"]
```

## AH.2 Frontend

Use:
- ESLint;
- TypeScript;
- optional Prettier.

`npm run lint` harus bisa dijalankan sebelum milestone freeze.

---

# AI. LINGKUNGAN PENGEMBANGAN: 1 ATAU 2 LAPTOP

Satu laptop sudah cukup.

> ⭐ **`[v3.0]` Spesifikasi yang dipakai — 🔒 ditetapkan.**
>
> **Lenovo IdeaPad Flex 5i · RAM 16 GB · SSD 512 GB · Windows 11.**
>
> Berprosesor Intel, sehingga akselerasi emulator memakai **WHPX/Hyper-V**, bukan HAXM yang sudah tidak didukung. Ini yang memungkinkan dua AVD dijalankan bergantian pada RAM 16 GB, dan **wajib disebut** pada daftar perangkat lunak BAB III 3.3.

Jika kemudian dua laptop:

```text
Laptop A — development
- Git repo
- backend
- frontend
- Docker/PostgreSQL
- docs/literature

Laptop B — controlled test
- Local Agent
- Android Studio/AVD
- physical dummy device
- Tier-2 experiment
```

Repository tetap sama melalui Git; raw evidence tidak perlu disinkronkan lewat GitHub.

---

# AJ. MILESTONE / TAHAP PENGEMBANGAN

## AJ.0 Model pengembangan — 🔒 `D-1` *(diputuskan 1 Sep 2026)*

**Model yang dipakai: *Incremental Development*.**

Sistem dibangun bertahap melalui beberapa *increment* yang saling berkelanjutan; tiap *increment* menghasilkan bagian sistem yang **dapat berfungsi dan diuji** sebelum pengembangan dilanjutkan ke *increment* berikutnya.

**Dasar pemilihan:**

| # | Alasan |
|---|---|
| 1 | **Kebutuhan penelitian tingkat tinggi stabil, tetapi realisasi artefaknya belum seluruhnya diketahui di awal.** `01_BREAKDOWN` §11 menyatakan status artefak tiap kelompok dipertajam melalui Tier-2. Umpan balik formatif dapat mengubah implementasi/profil tanpa mengubah rumusan masalah, lima dimensi, atau struktur G1/G2/G3 |
| 2 | **Arsitektur berlapis dan tiap lapis dapat diuji sendiri** — akuisisi, penguraian, normalisasi, mesin aturan, korelasi, antarmuka |
| 3 | **Artefak adalah keluaran penelitian itu sendiri**, bukan prototipe buangan, sehingga *prototyping* murni tidak sesuai |
| 4 | ***Vertical slice* pertama sudah dirancang** menyentuh seluruh lapis secara tipis (AJ.2) — bentuk baku *increment* pertama |

## AJ.1 ⭐ Urutan *increment* terkunci — pembeda yang wajib dinyatakan

> **Wajib ditulis eksplisit pada BAB III 3.1.**

Pada penerapan *Incremental* yang lazim, urutan *increment* dapat ditukar menurut prioritas karena tiap *increment* berupa modul fitur yang berdiri sendiri. **Pada penelitian ini urutannya tidak dapat ditukar.**

Sebabnya rantai pipeline riset `01_BREAKDOWN` §3: mesin aturan mustahil dibangun sebelum fakta ternormalisasi ada; fakta ternormalisasi mustahil ada sebelum akuisisi dan penguraian berjalan.

**Yang membedakannya dari *Waterfall* tetap jelas: urutan terkunci ≠ satu integrasi besar di akhir.** Setiap *increment* menghasilkan bagian sistem yang berfungsi dan diuji. Tier-2 formatif dapat mempertajam **keanggotaan dan implementasi artefak**, sementara kebutuhan penelitian tingkat tinggi dan struktur kelompok tetap terkunci. *(diperbarui v3.2; lihat `01_BREAKDOWN` §4.1.2 dan §11.2)*

⚠️ **Tanpa pernyataan ini, penguji berhak bertanya mengapa tidak sekalian memakai *Waterfall*.**

## AJ.2 Pemetaan — 5 *increment* atas 12 milestone *(diperbaiki v2.6)*

> ⛔ **KOREKSI v2.6.** Pemetaan v2.4.1–v2.5 **membatalkan definisi modelnya sendiri** dan diganti. Dua cacat:
>
> 1. **Pengujian ditempatkan sebagai *increment* kelima**, seolah pengujian baru dimulai di akhir. Definisi *Incremental* justru menuntut **tiap *increment* menghasilkan bagian yang berfungsi dan diuji**. Susunan lama tidak berbeda dari *Waterfall* yang dipecah.
> 2. ***Vertical slice* dikutip sebagai alasan memilih model, tetapi *increment* pertama hanya akuisisi** — bukan irisan tegak. Irisan tegak §AF membentang dari AVD sampai tampilan, yakni melintasi *increment* 1 **dan** 2 pada susunan lama. Pembenaran dan pemetaan tidak saling cocok.
>
> Pilihan modelnya benar; representasinya yang keliru.

**Ketentuan yang berlaku untuk seluruh *increment*:**

- Tiap *increment* menghasilkan **perangkat lunak yang dapat dijalankan dan diverifikasi**, bukan lapisan setengah jadi.
- **Pengujian berlangsung pada setiap *increment***, bukan ditunda ke akhir.
- *Increment* kelima adalah **integrasi dan evaluasi penelitian** — bukan saat pengujian pertama kali dilakukan.

| *Increment* | Isi | Milestone | Yang dapat dijalankan dan diverifikasi di akhir *increment* |
|---|---|---|---|
| **1 — Irisan tegak minimum** | Rantai tipis menyeluruh: deteksi perangkat → satu operasi ADB ber-*allowlist* → bukti mentah + SHA-256 → unggah → pengurai → satu fakta ternormalisasi → tampil di antarmuka | `v0.05`–`v0.40` | Satu fakta muncul di antarmuka lengkap dengan asal-usul sampai bukti mentahnya. **Seluruh lapisan tersentuh** |
| **2 — Kelengkapan satu kelompok sumber** | Perluasan ke seluruh artefak satu kelompok, `epistemic_class`, status ketersediaan, validasi kelayakan Tier-2 | `v0.45` | Seluruh artefak kelompok itu ternormalisasi; artefak yang gagal tercatat statusnya, bukan hilang |
| **3 — Penalaran** | Basis pengetahuan, lima keluarga/profil APKF, validasi kelas epistemik/claim/reference, dan mesin tiga keadaan | `v0.50`–`v0.60` | Profil dan keluarga menghasilkan tiga keadaan, konflik tercatat, dan setiap elemen penting tertelusur ke rujukan |
| **4 — Lintas sumber dan rekonstruksi** | Dua kelompok sisanya, korelasi lintas kelompok, temuan, `ReconstructionRun`, hipotesis, keterlacakan penuh | `v0.70` | Temuan dan rekonstruksi tertelusur ke bukti, aturan, dan rujukan tanpa menaikkan tingkat klaim |
| **5 — Integrasi dan evaluasi** | simulator aman, 20 kasus authoring, freeze, 8 holdout, aplikasi benign/kontrol, pemeriksaan malware statis, baseline manual | `v0.80`–`v0.90` | Hasil kesesuaian per kasus, konsistensi, UNKNOWN/konflik, anti-klaim-berlebih, dan perbandingan deskriptif |

`v1.00` — prototipe terpadu, laporan, dan dokumentasi — merupakan konsolidasi, bukan *increment* tersendiri.

### Pemetaan ke enam tahap penelitian/proyek a–f — 🔒 `K-04` *(ditetapkan v2.9)*

> Pemetaan ini menjadi sumber langsung BAB III 3.2. Ia **tidak** mengubah jumlah *increment*. Enam tahap adalah tahapan penelitian/proyek; lima *increment* adalah unit pengembangan perangkat lunak yang melintasi **tahap d dan e**.

| Tahap | Isi | Hubungan dengan rancangan |
|---|---|---|
| **a** | Studi pendahuluan dan analisis kebutuhan | Framing masalah, kebutuhan institusi, RQ, batasan, dan kajian awal |
| **b** | Penetapan kelompok sumber bukti dan penilaian kelayakan Tier-1 | `D-5`, G1/G2/G3, kriteria seleksi, matriks Tier-1 |
| **c** | Perancangan sistem | Arsitektur §T–§AC, model data, keamanan, rancangan aturan dan antarmuka |
| **d** | Pengembangan bertahap — *increment* 1 sampai 4 | Empat *increment* pertama pada tabel §AJ.2; tiap *increment* menghasilkan bagian yang dapat dijalankan dan diuji |
| **e** | Integrasi, pengujian skenario, dan pembekuan — *increment* 5 | simulator aman, sanity ADB §AL, authoring, pembekuan, holdout, aplikasi benign/kontrol, malware statis, dan baseline manual |
| **f** | Evaluasi dan pelaporan | kesesuaian per kasus, keterlacakan, UNKNOWN/konflik, konsistensi, batas klaim, pemeriksaan relevansi statis, dan laporan |

> ⭐ **Hubungan urutan.** Tahap a–f berurutan sebagai alur penelitian. Urutan lima *increment* terkunci oleh dependensi pipeline `01_BREAKDOWN` §3, dan urutan itu tetap berlaku melintasi tahap d dan e.

> ⛔ **`[KOREKSI v3.0]` Tumpang tindih tahap d, e, dan f.**
>
> Pemetaan v2.9 menempatkan **seluruh lima *increment*** pada tahap d, padahal *increment* 5 memuat skenario A/B/C/D1/D2, pembekuan aturan, *holdout*, dan baseline analisis manual — yang **juga** menjadi isi tahap e dan f. Akibatnya pembaca BAB III 3.2 tidak dapat menentukan pengujian skenario terjadi di tahap d atau tahap e, padahal keduanya dinyatakan berurutan.
>
> **Yang diperbaiki:** tahap d dibatasi pada *increment* 1–4; *increment* 5 dinaikkan menjadi tahap e. **Tabel lima *increment* di atas tidak disentuh** — jumlah, isi, dan urutannya tetap, sehingga `D-1` tidak dibuka kembali. Yang berubah hanya pemetaannya ke tahapan penelitian.

> ⭐ **Tier-2 muncul dua kali, dengan fungsi berbeda — wajib dinyatakan di 3.2 dan 3.4.**
>
> | Kemunculan | Letak | Fungsi |
> |---|---|---|
> | **Formatif** | Di dalam *increment* 2 dan 4, saat tiap kelompok sumber diimplementasikan | Memastikan artefak kelompok itu benar-benar dapat diperoleh; artefak yang gagal dicatat statusnya, bukan hilang |
> | **Konfirmatif** | Tahap e | Pencatatan ketersediaan artefak lintas lingkungan sebagai bahan pelaporan (`01_BREAKDOWN` §9.7) |
>
> Tanpa pembedaan ini, tumpang tindihnya hanya berpindah tempat, tidak hilang.

⚠️ ***Ablation* tidak dicantumkan — `D-8` berstatus `DEFER`.** Cakupan kelompok ditunjukkan pada tabel rancangan pengujian inti, bukan pengujian konfigurasi tambahan.

✅ **Sitasi model pengembangan — `R-01` DITUTUP v3.1.** `[ARSIP v2.8]` ~~Zein dkk. (2023) wajib dibaca sendiri sebelum dipakai di 3.1~~ — dibuang pada v2.7. Sumber yang berlaku: **Cockburn (2008)** untuk definisi dan **Larman & Basili (2003)** untuk legitimasi historis, keduanya ●●●; **SWEBOK v4.0 (2024)** menjadi penopang kemutakhiran. **SEBoK dicabut.** Pilihan model `D-1` tidak dibuka kembali.

## AJ.3 Daftar milestone

```text
v0.05  Toolchain installed + repo + AVD/ADB smoke test
v0.10  Backend health + PostgreSQL migration + React shell
v0.20  Agent device detection + heartbeat
v0.30  AcquisitionSession + 1 allowlisted operation + hash/upload
v0.40  Parser + Artifact + NormalizedEvent source group #1
v0.45  Tier-2 selected-source acquisition validation
v0.50  Knowledge Base loader + YAML validation
v0.60  Rule engine + TRUE/FALSE/UNKNOWN
v0.70  Multi-source correlation + hypothesis + traceability UI
v0.80  Safe simulator + authoring/benign/UNKNOWN/conflict/exclusionary cases
v0.90  Freeze + 8 holdout bundles + static candidates + manual baseline + results
v1.00  Integrated thesis prototype + report + documentation
```

Vertical slice pertama:

```text
1 AVD
→ adb detected
→ 1 acquisition operation
→ raw evidence
→ SHA-256
→ upload
→ parse
→ normalize
→ display
```

---

# AK. UJI AWAL (SMOKE TEST) SETELAH SETUP

```text
[ ] git --version
[ ] git remote -v
[ ] repository private remote aktif
[ ] python --version = 3.13.x
[ ] backend venv aktif
[ ] agent venv aktif
[ ] node --version = 24.x LTS
[ ] npm works
[ ] Android Studio stable opens
[ ] API 36 AVD boots
[ ] adb version works
[ ] adb devices -l menampilkan AVD
[ ] Docker works jika dipakai
[ ] PostgreSQL container/service running
[ ] FastAPI /api/health running
[ ] Swagger /docs terbuka
[ ] React/Vite dev server running
[ ] backend connect PostgreSQL
[ ] Alembic migration succeeds
[ ] first Git tag v0.05 dibuat setelah smoke test sukses
```

---

# AL. PRIORITAS UJI SANITY ADB TIER-2

Manual sebelum otomatisasi agent:

```text
1. device/build metadata
2. package inventory + UID
3. package detail
4. install/update metadata
5. requested/granted permissions
6. Accessibility current state
7. UsageStats/UsageEvents
8. SMS provider
9. Contacts provider
10. UID network stats
11. APK path/pull
```

Catat:
- command;
- Git commit;
- ADB version;
- Android/API/build;
- privilege;
- expected;
- actual;
- raw output location;
- temporal semantics;
- availability status.

---

# AM. HAL YANG TETAP VS BOLEH BERUBAH

## Arsitektur yang tetap

- Python Local Agent
- Python FastAPI backend
- React/TypeScript frontend
- PostgreSQL
- official ADB
- YAML rules/KB
- filesystem raw evidence MVP
- WebSocket status/control
- REST upload/API
- backend research reasoning
- authorized non-root baseline

## Versi yang fleksibel

Patch/minor boleh berubah sebelum freeze jika:
- stable;
- compatible;
- dicatat;
- dependency di-lock ulang;
- smoke test diulang.

## Keputusan teknis yang masih terbuka

1. keanggotaan artefak final berdasarkan hasil Tier-2;
2. perintah ADB final per versi Android untuk tiap operasi ber-*allowlist*;
3. versi Android aktual Galaxy A10 dan API AVD kedua;
4. identitas serta SHA-256 tiga APK malware nyata dari sedikitnya enam kandidat;
5. package, versi, hash, dan katalog skenario simulator/benign-control;
6. penyesuaian *as-built* profil setelah *authoring* dalam batas kontrak §Z.0 dan `01_BREAKDOWN` §14.3; katalog 16 profil serta YAML awal sudah dikunci;
7. perangkat lunak virtualisasi desktop;
8. implementasi endpoint lokal, pengendali host, dan manifest eksperimen;
9. hasil Tier-2, skenario, manual baseline, dan evaluasi;
10. final deployment serta Python runtime vs executable terpaket untuk agen.

**Sudah tertutup:** tiga kelompok utama (`D-5`), lima dimensi, lima keluarga APKF, tiga kategori sampel, APK-statis sebagai pengaya G1, kontrak simulator aman, desain manual baseline, strategi tanpa lampiran, paket sepuluh diagram, dan status `R-01`–`R-05`. Ekstensi perangkat *pre-rooted* berada di luar baseline MVP.

---

# AN. BATASAN — HAL YANG BUKAN TUJUAN MVP

Jangan memperluas MVP menjadi:
- enterprise DFIR suite;
- malware sandbox lengkap;
- reverse engineering suite;
- mobile EDR;
- root/exploit framework;
- physical extraction tool;
- generic Android malware detector.

Target tetap:

```text
Authorized Acquisition
→ Raw Evidence
→ Artifact
→ Normalized Event
→ Rule-Based Correlation
→ Explainable Finding/Hypothesis
```

---

# AO. SPESIFIKASI DIAGRAM BAB III DRAFT v3 — 🔒 v3.3

Semua diagram dibuat dalam `.drawio` dan diekspor menjadi PNG resolusi tinggi untuk DOCX. Sumber editable disimpan di `docs/diagrams/`. Diagram harus terbaca pada A4, menggunakan konektor ortogonal, tidak mempunyai garis yang menembus node, memakai palet konsisten yang tetap terbaca abu-abu, serta dilengkapi judul, legenda, caption, dan paragraf penjelas.

BAB III tidak memakai lampiran formal. YAML lengkap, kamus data, katalog kasus, metadata sampel, log/hasil, dan sumber diagram disimpan sebagai artefak repositori penelitian berversi; badan bab hanya memuat representasi inti.

| ID | Bentuk | Orientasi | Struktur minimum |
|---|---|---|---|
| `DGM-01` | proses dua-lapis | potret | tahap a–f dan lima increment; bedakan penelitian dari pengembangan |
| `DGM-02` | derivasi kebutuhan | lanskap | lima dimensi → G1–G3 → Tier-1/Tier-2 → KF/KNF |
| `DGM-03` | arsitektur terpadu | lanskap penuh | Pemeriksa; web; backend operational/research; agen/ADB/perangkat; jalur statis; penyimpanan; simulator; protokol |
| `DGM-04` | UML use case | lanskap | satu aktor Pemeriksa, batas sistem, autentikasi/kasus/perangkat/akuisisi/analisis/keterlacakan/laporan |
| `DGM-05` | flowchart | lanskap | validasi sesi → operasi allowlist → status → hash/simpan → parse → fakta/UNKNOWN → normalisasi |
| `DGM-06` | flowchart bercabang | lanskap | `evidence_mode` + `run_purpose` → saring 16 profil → validasi rule/ref → kondisi → konflik/3-state → profil → keluarga → temuan → rekonstruksi berbatas klaim |
| `DGM-07` | Crow’s Foot ERD | lanskap penuh | empat zona; entitas tabel; PK/FK/atribut kritis; kardinalitas opsional/wajib/M:N jelas |
| `DGM-08` | data lineage | lanskap | evaluasi→kondisi→fakta→artefak→bukti dan evaluasi→elemen aturan→rujukan; matched→temuan→rekonstruksi |
| `DGM-09` | wireframe | lanskap | daftar evaluasi, detail profil/kondisi, tiga basis, UNKNOWN/konflik, claim level, rekonstruksi, laporan |
| `DGM-10` | governance flow | lanskap | S-A/S-B/S-C, kandidat, authoring, freeze, holdout, baseline manual, otomatis, pelaporan |

`DGM-03` menggabungkan arsitektur konteks/deployment dan komponen internal, tetapi memakai zona sehingga aktor, proses, data store, dan lingkungan uji tidak tercampur. `DGM-07` wajib digambar ulang; diagram ERD v2 tidak dijadikan basis. Proses bisnis tidak dimasukkan ke ERD—ditanggung `DGM-05`, `DGM-06`, dan `DGM-08`. Diagram sekuens lama dicabut.

---

# AP. REFERENSI RESMI UNTUK SETUP / UNDUHAN

Gunakan halaman resmi saat mengunduh:

```text
Git:
https://git-scm.com/

GitHub pricing:
https://github.com/pricing

VS Code:
https://code.visualstudio.com/

Python:
https://www.python.org/downloads/

Node.js:
https://nodejs.org/en/download

PostgreSQL:
https://www.postgresql.org/download/

Android Studio:
https://developer.android.com/studio

Android Studio releases:
https://developer.android.com/studio/releases

Platform-Tools:
https://developer.android.com/tools/releases/platform-tools

Android 16 SDK:
https://developer.android.com/about/versions/16/setup-sdk

AGP:
https://developer.android.com/build/releases/

Docker:
https://docs.docker.com/get-docker/

DBeaver Community:
https://dbeaver.com/edition/community/

pgAdmin:
https://www.pgadmin.org/download/

Bruno:
https://www.usebruno.com/

Postman:
https://www.postman.com/pricing/

Genymotion:
https://www.genymotion.com/product-desktop/

FastAPI:
https://fastapi.tiangolo.com/

React:
https://react.dev/

Vite:
https://vite.dev/
```
