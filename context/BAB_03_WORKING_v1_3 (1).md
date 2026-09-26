# BAB_03_WORKING — PENELITIAN FORENSIK ANDROID
## Dokumen kendali BAB III — versi 1.3

**Tanggal:** 5 September 2026  
**Status:** `ACTIVE · FROZEN FOR DRAFT v3`  
**Target naskah:** BAB III Draft v3, 31–35 halaman  
**Prinsip:** naskah ringkas, tanpa lampiran formal, visual yang informatif, dan tanpa perubahan BAB I–II

> **Generate 1.5:** v1.3 diperbarui tanpa mengganti identitas versi untuk menutup spesifikasi implementasi APKF sebelum produksi diagram: 16 profil awal, lima YAML `design_baseline`, kosakata fakta, semantik TRUE/FALSE, dua sumbu aplikabilitas, fixture eksklusioner, dan batas perubahan saat *authoring*.

---

# 0. FUNGSI DAN BATAS DOKUMEN

Dokumen ini mengendalikan penyusunan BAB III Draft v3. Ia bukan naskah skripsi, bukan tempat hasil pengujian, dan bukan tempat menyimpan riwayat diskusi panjang.

Yang diatur:

- fungsi serta batas setiap subbab 3.1–3.6;
- keputusan substansi APKF, G1–G3, sampel, simulator, dan evaluasi;
- anggaran halaman, tabel, serta diagram;
- data yang masih kosong dan tidak boleh diasumsikan;
- urutan produksi Draft v3.

BAB I dan BAB II berstatus `DRAFT FINAL` dan **tidak diubah** pada pekerjaan ini.

---

# 1. URUTAN OTORITAS

Jika terdapat konflik, gunakan urutan berikut:

1. keputusan langsung Marco pada sesi berjalan;
2. judul yang telah diterima institusi;
3. naskah `BAB_01_DRAFT_FINAL_2` dan `BAB_02_DRAFT_FINAL`;
4. `01_BREAKDOWN_PROYEK_FORENSIK_ANDROID_V3_3.md`;
5. `02_ARSITEKTUR_SETUP_FORENSIK_ANDROID_V3_3.md`;
6. `00_SESSION_STARTER_FORENSIK_ANDROID_V3_3.md`;
7. dokumen ini, `BAB_01_WORKING_v1.5.md`, dan `BAB_02_WORKING_v0.8.md`;
8. naskah senior sebagai preseden bentuk, bukan otoritas isi;
9. asumsi AI.

Draft v1/v2 BAB III adalah inventaris bahan. Keduanya tidak mengalahkan core v3.3.

---

# 2. PUTUSAN SUBSTANTIF TERKUNCI

## 2.1 Posisi penelitian

Penelitian berada pada bidang **forensik digital Android pascaakuisisi** dengan kasus aplikasi APK penipuan. Kontribusinya adalah korelasi deterministik atas fakta Android ternormalisasi untuk menghasilkan temuan dan hipotesis investigasi yang tertelusur.

Platform **bukan**:

- pendeteksi atau pengklasifikasi malware;
- mesin vonis bahwa suatu aplikasi adalah penipuan;
- sandbox malware;
- alat pembuktian eksfiltrasi, pencurian kredensial, atau kerugian finansial tanpa bukti yang sesuai.

## 2.2 Lima dimensi investigatif

1. identitas dan keadaan instalasi;
2. kapabilitas sensitif dan akses khusus;
3. eksekusi dan persistensi;
4. keberadaan data komunikasi sensitif dalam konteks perangkat;
5. aktivitas jaringan terkait package/UID.

Kelima dimensi adalah subpertanyaan operasional, bukan kondisi APKF dan bukan kode yang harus muncul dalam setiap paragraf naskah.

## 2.3 Tiga kelompok sumber bukti

| Kelompok | Cakupan aktif v3.3 | Dimensi utama |
|---|---|---|
| **G1 — Keadaan Aplikasi dan Sistem** | identitas/instalasi; kapabilitas/akses khusus; eksekusi/persistensi; pengayaan statis APK | 1–3 |
| **G2 — Data Komunikasi Sensitif** | SMS/MMS; kontak/catatan panggilan; konteks notifikasi bila layak | 4 |
| **G3 — Aktivitas Jaringan** | statistik UID/package; konteks konektivitas; endpoint lokal/capture lab untuk validasi simulator | 5 |

Jumlah kelompok tetap tiga. APK-statis adalah pengayaan G1, bukan G4. *Fallback* tidak dianggap setara dengan artefak inti tanpa pembuktian semantik dan Tier-2.

## 2.4 Lima keluarga APKF

**APKF** berarti **Aturan Pola Korelasi Forensik**.

| Keluarga | Fokus | Tingkat klaim |
|---|---|---|
| `APKF-K01` | kapabilitas komunikasi sensitif | kapabilitas; konteks G2 tetap keberadaan data |
| `APKF-K02` | antarmuka istimewa/akses khusus | kapabilitas |
| `APKF-K03` | persistensi atau eksekusi terpicu peristiwa | kapabilitas atau aktivitas teramati sesuai profil |
| `APKF-K04` | eksekusi package relevan teramati | aktivitas teramati |
| `APKF-K05` | aktivitas jaringan terkait UID/package | aktivitas jaringan teramati |

Satu keluarga dapat memiliki beberapa profil bukti. Fleksibel berarti menyediakan profil yang sah untuk jalur artefak berbeda, **bukan** menggabungkan semua fakta terkait dalam satu wildcard.

Katalog awal aktif berisi **16 profil**:

| Keluarga | Profil awal | Lingkup bukti |
|---|---:|---|
| K01 | 3 | izin komunikasi sensitif aktif; izin kontak/catatan panggilan aktif; deklarasi sensitif APK statis |
| K02 | 4 | aksesibilitas aktif; overlay aktif; listener notifikasi aktif; deklarasi akses khusus APK statis |
| K03 | 3 | deklarasi pemicu package terpasang; deklarasi pemicu APK statis; eksekusi terpicu yang teramati |
| K04 | 3 | riwayat penggunaan; activity resumed; proses berjalan |
| K05 | 3 | statistik jaringan UID; request endpoint lokal; koeksistensi flow lab teratribusi |

Rincian setiap profil—fakta wajib, konteks, operator, rujukan, batas klaim, dan keluaran—dikunci pada `01_BREAKDOWN` §14.1.3. Lima YAML lengkap berstatus `design_baseline` berada di §14.2 dan kontrak implementasinya berada di `02_ARSITEKTUR` §Z.0. Tabel portofolio di BAB III merangkum rancangan ini; YAML tidak perlu disalin ke naskah.

Kontrak:

- `any_of` hanya untuk bukti yang setara secara semantik;
- peran kondisi: wajib, opsional, kontekstual, atau eksklusioner;
- setiap profil memiliki `claim_level`;
- konflik bukti menghasilkan `UNKNOWN/conflicting_evidence`;
- setiap evaluasi profil dan keluarga dicatat;
- setiap profil `matched` dapat menghasilkan satu temuan yang menunjuk profil dan keluarganya; beberapa profil dari keluarga sama tidak dihitung sebagai beberapa keluarga saat rekonstruksi;
- hipotesis memerlukan sedikitnya dua temuan dari keluarga berbeda yang kompatibel menurut package/UID, waktu, dan konteks;
- rekonstruksi urutan kejadian memerlukan sedikitnya satu temuan berkelas aktivitas teramati; jika tidak, sistem berhenti pada temuan tingkat rendah;
- kondisi wajib hanya gerbang profil tingkat rendah, bukan rekonstruksi lengkap.

Aplikabilitas tidak memakai satu label campuran. Setiap profil mencantumkan `evidence_mode` (`installed_runtime`/`apk_static`) dan `run_purpose` (`authoring`/`holdout`/`benign_control`/`production`). Profil yang tidak berlaku dicatat `skipped_not_applicable` dengan `outcome: null` dan dikeluarkan dari agregasi.

Kondisi `FALSE` wajib ditopang fakta negatif eksplisit (`predicate_value: false`) dari sumber dengan cakupan lengkap; ketiadaan baris pada sumber yang tidak lengkap adalah `UNKNOWN`. Fixture eksklusioner sintetis hanya menguji mekanisme pada *authoring/holdout*, tidak menjadi label benign dan tidak masuk penggunaan produksi.

Siklus status YAML: `design_baseline` → `authoring_candidate` → `frozen_for_holdout`. Status pertama sudah cukup untuk memfinalisasi rancangan BAB III; status terakhir baru dihasilkan setelah implementasi dan *authoring*, sebelum *holdout*.

## 2.5 Rujukan

Rujukan tidak hanya menempel pada metadata aturan. Kondisi, profil, dan batas interpretasi dapat mempunyai:

- `rule_element_key`;
- `reference_role`: semantik artefak, relevansi perilaku, batas interpretasi, atau pemetaan teknik;
- klaim yang diekstrak;
- cakupan versi;
- status verifikasi.

Antarmuka membedakan basis bukti, basis aturan, dan basis pengetahuan.

---

# 3. SAMPEL DAN SIMULATOR

## 3.1 Tiga kategori sampel

| Kategori | Peran | Perlakuan |
|---|---|---|
| **S-A simulator bukti aman** | sumber *ground truth* untuk pengujian dinamis | dibangun, dipasang, dan dijalankan terkendali |
| **S-B aplikasi benign/kontrol** | menguji anti-klaim-berlebih | diverifikasi; dapat dipasang/dijalankan terisolasi |
| **S-C APK malware nyata** | memeriksa keterwakilan pola statis | analisis statis saja; tidak dipasang/dijalankan |

Sumber S-C: MalwareBazaar sebagai sumber utama dan VX-Underground sebagai cadangan.

## 3.2 Seleksi kandidat malware nyata

- kumpulkan minimum 6, target 8 kandidat;
- pilih 3 sampel akhir setelah pemetaan lima keluarga APKF;
- usahakan portofolio mewakili komunikasi sensitif, aksesibilitas/*overlay*, dan persistensi/jaringan;
- catat SHA-256, sumber, identitas/family yang dikorroborasi, rujukan perilaku, artefak statis, keluarga/profil terkait, `minSdk`, `targetSdk`, ABI, duplikasi, serta alasan pilih/tolak;
- `minSdk`, `targetSdk`, dan ABI adalah kompatibilitas, bukan indikator fraud.

S-C tidak memberi *ground truth* runtime dan tidak dipakai mengukur akurasi deteksi.

## 3.3 Simulator bukti aman

Komponen:

1. aplikasi Android simulator;
2. pengendali skenario pada host;
3. endpoint lokal.

Kemampuan yang boleh ada:

- package/UID/versi dan artefak instalasi;
- permintaan izin transparan;
- aksesibilitas *no-op*;
- *overlay* berlabel uji;
- `BOOT_COMPLETED` yang hanya menghasilkan notifikasi/log terlihat;
- aktivitas penggunaan terkendali;
- lalu lintas ke endpoint lokal;
- SMS/kontak sintetis yang disiapkan pengendali.

Larangan:

- pencurian kredensial atau data nyata;
- impersonasi merek/lembaga;
- stealth, obfuscation, evasion, exploit, atau *auto-grant*;
- penyalahgunaan aksesibilitas dan *overlay* menipu;
- komunikasi pihak ketiga;
- persistensi tersembunyi.

Varian build minimal: `authoring`, `holdout`, dan `benignControl`; nilai teknis `run_purpose` untuk varian terakhir adalah `benign_control`.

Setiap skenario mempunyai `ground_truth.json` yang memuat ID, kategori/varian, package/versi/hash, lingkungan, keadaan awal, aksi/waktu, artefak dan fakta yang diharapkan, vektor APKF, batas klaim, bukti yang sengaja tidak tersedia, serta konflik yang diharapkan.

Urutan development:

1. kontrak skenario dan oracle;
2. scaffold serta varian build;
3. identitas, izin, dan akses khusus;
4. eksekusi/persistensi yang terlihat;
5. data sintetis dan jaringan lokal;
6. pengendali host;
7. katalog authoring, benign, konflik, eksklusioner, dan holdout;
8. validasi oracle dan pembekuan Git/APK/konfigurasi/hash.

Simulator adalah bagian pekerjaan pengujian/integrasi, bukan increment keenam.

---

# 4. RANCANGAN PENGUJIAN DAN EVALUASI

## 4.1 Katalog kasus

- minimum 20 kasus *authoring*: empat per keluarga APKF;
- fixture konflik dan eksklusioner dimasukkan ke katalog tersebut, sekurang-kurangnya dua kasus masing-masing lintas keluarga;
- kasus opsional-hilang ada untuk setiap peran bukti opsional yang benar-benar dipakai;
- target 8 bundel *holdout*, masing-masing membawa vektor keluaran kelima keluarga;
- hasil holdout tidak digunakan untuk tuning.

Kelas cakupan: positif, *near-miss*, benign/kontrol, opsional hilang, wajib `UNKNOWN`, konflik, dan eksklusioner. Kelas bukan produk Kartesius wajib bagi semua profil.

## 4.2 Yang dinilai

1. kesesuaian fakta/kondisi terhadap oracle;
2. kesesuaian keluaran profil dan agregasi keluarga;
3. ketepatan penanganan `UNKNOWN`, konflik, dan eksklusioner;
4. kelengkapan keterlacakan ke bukti dan rujukan;
5. konsistensi semantik atas input dan versi yang sama;
6. ketaatan temuan/hipotesis pada `claim_level`;
7. tidak adanya klaim berlebih pada aplikasi benign dan sampel statis.

Tidak ada precision, recall, F1, skor risiko, atau satu angka agregat lintas kelas. Jika istilah akurasi dipakai, batasnya hanya kesesuaian spesifikasi pada skenario terkendali.

## 4.3 Baseline manual

Analisis manual dan platform menerima paket bukti mentah serta metadata yang sama. Akuisisi berada di luar unit perbandingan. Catatan manual disegel sebelum keluaran otomatis dilihat.

Dimensi deskriptif:

- keluaran yang ditemukan;
- langkah/interaksi;
- keterlacakan;
- penanganan bukti hilang;
- dokumentasi alasan.

Tidak mengukur waktu dan tidak mengklaim keunggulan umum.

---

# 5. BLUEPRINT NASKAH BAB III DRAFT v3

## 5.1 Struktur dan anggaran halaman

| Subbab | Fungsi | Target |
|---|---|---:|
| **3.1 Deskripsi Model/Pola Pengembangan** | alasan memilih Incremental dan karakteristik penerapannya | 1–1,5 |
| **3.2 Tahapan Pengembangan Proyek** | penerapan tahap a–f dan lima increment | 3–4 |
| **3.3 Alat dan Bahan** | perangkat lunak/perangkat, tiga kategori sampel, seleksi kandidat | 3–4 |
| **3.4 Teknik Pengumpulan dan Analisis Kebutuhan** | lima dimensi, G1–G3, Tier-1/Tier-2, KF/KNF | 6–7 |
| **3.5 Desain Sistem** | arsitektur, alur, APKF, data, keterlacakan, antarmuka | 11–12 |
| **3.6 Teknik Pengujian** | skenario, freeze/holdout, konsistensi, baseline, evaluasi | 6–7 |
| **Total** |  | **31–35** |

## 5.2 Isi per subbab

### 3.1 Deskripsi Model/Pola Pengembangan

Maksimum tiga unit ide:

1. definisi dan alasan memilih Incremental;
2. kesesuaian dengan dependensi penelitian;
3. perbedaan dari Waterfall/prototyping secara singkat.

Tidak perlu tujuh sub-subbagian. Alasan pemilihan berada di 3.1; penerapannya berada di 3.2.

### 3.2 Tahapan Pengembangan Proyek

Jelaskan enam tahap a–f secara sentral. Tahap d memuat increment 1–4; tahap e memuat increment 5. Tabel hanya dipakai bila membantu memetakan tahap, increment, keluaran, dan verifikasi secara bersamaan. Jangan mengulang teori Incremental.

### 3.3 Alat dan Bahan

Struktur:

1. perangkat keras dan lingkungan;
2. perangkat lunak utama;
3. bahan/sampel dan protokol seleksi.

Keterbatasan lingkungan ditulis hanya sepanjang memengaruhi pemilihan alat/bahan. Jangan menuliskan identitas sampel final sebelum datanya tersedia.

### 3.4 Teknik Pengumpulan dan Analisis Kebutuhan

Alur:

1. turunkan lima dimensi dari masalah/tujuan;
2. petakan ke G1–G3;
3. nilai artefak melalui Tier-1 dan rancang Tier-2;
4. turunkan kebutuhan fungsional/nonfungsional;
5. nyatakan batas semantik.

Matriks Tier-1 inti wajib masuk dan dibuat padat. Rincian operasi/data tidak diulang jika sudah ditanggung tabel atau repositori.

### 3.5 Desain Sistem

Urutan:

1. arsitektur platform terpadu;
2. use case Pemeriksa;
3. alur akuisisi dan normalisasi;
4. mekanisme APKF dan rekonstruksi;
5. rancangan data serta keterlacakan;
6. rancangan penyajian hasil.

Diagram memikul struktur proses; prosa menjelaskan keputusan, batas, dan cara baca. Diagram sekuens lama tidak dipakai.

### 3.6 Teknik Pengujian

Urutan:

1. objek dan lingkungan uji;
2. katalog kasus dan oracle;
3. authoring, freeze, dan holdout;
4. uji kondisi/APKF/rekonstruksi/keterlacakan;
5. uji konsistensi;
6. baseline manual dan pelaporan.

Jangan memakai tabel matriks besar dengan kolom kode yang tidak dijelaskan. Satu tabel pengujian inti harus dapat dibaca tanpa membuka dokumen core.

---

# 6. INVENTARIS TABEL INTI

Target sekitar tujuh tabel; nomor final ditentukan ketika DOCX dirakit.

| ID kerja | Isi | Lokasi |
|---|---|---|
| `T-01` | alat, perangkat, versi/fungsi | 3.3 |
| `T-02` | lima dimensi → G1–G3 → keluaran | 3.4 |
| `T-03` | Tier-1: artefak inti, penguat, fallback, semantik, status | 3.4 |
| `T-04` | status akuisisi → keadaan fakta → kondisi aturan | 3.4/3.5 |
| `T-05` | lima keluarga APKF, 16 profil awal, mode bukti, fakta wajib, dan batas klaim | 3.5 |
| `T-06` | seleksi kandidat dan tiga sampel akhir | 3.3 atau 3.6 |
| `T-07` | rancangan kasus dan dimensi evaluasi | 3.6 |

Tabel dua kolom yang hanya mengganti daftar dilarang. Tabel dipakai jika beberapa atribut perlu dibandingkan sekaligus.

---

# 7. PAKET SEPULUH DIAGRAM

| ID | Diagram | Lokasi | Kriteria utama |
|---|---|---|---|
| `DGM-01` | tahap penelitian dan lima increment | 3.2 | dua lapis jelas; d/e tidak tumpang tindih |
| `DGM-02` | derivasi kebutuhan | 3.4 | lima dimensi → G1–G3 → Tier-1/Tier-2 → KF/KNF |
| `DGM-03` | arsitektur platform terpadu | 3.5 | konteks/deployment + komponen internal dalam satu lanskap berzona |
| `DGM-04` | use case Pemeriksa | 3.5 | notasi UML, satu aktor, batas sistem jelas |
| `DGM-05` | akuisisi dan normalisasi | 3.5 | flowchart bercabang sampai fakta/UNKNOWN |
| `DGM-06` | evaluasi APKF dan rekonstruksi | 3.5 | dua sumbu aplikabilitas → 16 profil → kondisi/3-state → keluarga → temuan → hipotesis |
| `DGM-07` | ERD logis Crow’s Foot | 3.5 | tabel PK/FK, kardinalitas, empat zona, tanpa Chen/class diagram |
| `DGM-08` | data lineage/keterlacakan | 3.5 | jalur ke bukti dan rujukan; keluaran matched dipisah |
| `DGM-09` | wireframe hasil evaluasi | 3.5 | semua keadaan, konflik, tiga basis, claim level, rekonstruksi |
| `DGM-10` | tata kelola sampel dan pembekuan | 3.6 | S-A/S-B/S-C, kandidat, authoring, freeze, holdout, baseline |

Ketentuan visual:

- sumber editable `.drawio` untuk setiap diagram;
- PNG resolusi tinggi ditanam ke DOCX;
- konektor ortogonal dan tidak menembus node;
- maksimal lima node horizontal dalam satu baris;
- warna konsisten dan tetap terbaca abu-abu;
- ukuran teks terbaca pada A4;
- setiap diagram memiliki legenda, caption, dan paragraf cara baca;
- DGM-03 dan DGM-07 boleh satu halaman lanskap penuh;
- ERD v2 dibuang dan digambar ulang, bukan ditambal.

---

# 8. STRATEGI TANPA LAMPIRAN

Naskah tidak memakai lampiran formal. Isi berikut **tidak** dipindahkan ke akhir skripsi, melainkan menjadi artefak repositori penelitian berversi:

- lima YAML `design_baseline` tersedia lengkap di core (`01_BREAKDOWN` §14.2); salinan implementasi dan versi hasil *authoring* disimpan di repositori penelitian;
- kamus data dan seluruh atribut entitas;
- katalog lengkap 20 authoring dan 8 holdout;
- `ground_truth.json`;
- matriks kandidat sampel lengkap dan metadata hash;
- perintah/prosedur operasi rinci;
- keluaran mentah dan hasil pengujian;
- seluruh sumber `.drawio` dan PNG.

BAB III hanya memuat representasi inti yang diperlukan untuk memahami dan mereplikasi metode pada tingkat desain. Repositori dirujuk sebagai artefak penelitian, bukan “lampiran daring”.

---

# 9. ATURAN BAHASA DAN KODE INTERNAL

- naskah memakai istilah **rumusan masalah**, bukan `RQ`;
- kode `D-`, `K-`, `M-`, `R-`, `B3-`, dan ID kontrol lain tidak masuk prosa final;
- G1–G3 dan APKF-K01–K05 boleh dipakai setelah didefinisikan pada kemunculan pertama;
- istilah teknis Inggris dimiringkan atau diberi padanan Indonesia;
- tidak memakai “malware terdeteksi”, “APK terbukti menipu”, “eksfiltrasi”, atau “akses terjadi” tanpa bukti pada tingkat klaim yang benar;
- permission/deklarasi = kapabilitas, bukan perilaku;
- bukti tidak tersedia = tidak diketahui, bukan tidak terpenuhi;
- narasi langsung ke fungsi metodologis; hapus paragraf yang hanya mengulang tabel/diagram.

---

# 10. DATA PELAKSANAAN YANG MASIH TERBUKA

1. versi Android/API aktual Samsung Galaxy A10 dan API AVD kedua;
2. perangkat lunak virtualisasi desktop yang dipakai;
3. package, versi, dan hash simulator aman;
4. aplikasi benign/kontrol yang lolos verifikasi;
5. minimum enam kandidat dan tiga APK malware akhir beserta SHA-256;
6. status Tier-2 tiap artefak per lingkungan;
7. penyesuaian *as-built* profil setelah *authoring* dalam batas kontrak; katalog 16 profil dan YAML desain awal sudah lengkap;
8. katalog dan hash 8 bundel holdout;
9. hasil pengujian, baseline manual, dan evaluasi.

Data ini tidak boleh diisi dengan asumsi. BAB III dapat menjelaskan kriteria dan prosedurnya; identitas final diisi setelah tersedia.

---

# 11. ALUR PRODUKSI

## Generate 1 — selesai setelah dokumen ini lolos audit

- tiga core v3.3;
- Working v1.3;
- BAB I–II tidak berubah.

## Generate 1.5 — pembaruan aktif sebelum diagram

- kunci registri rujukan desain, kosakata fakta, dan semantik selector/operator;
- kunci 16 profil awal serta lima YAML `design_baseline`;
- pisahkan `evidence_mode` dari `run_purpose` dan tetapkan `skipped_not_applicable`;
- kunci fakta negatif eksplisit, fixture eksklusioner, serta siklus `design_baseline` → `authoring_candidate` → `frozen_for_holdout`;
- audit silang empat dokumen dan pertahankan BAB I–II tanpa perubahan.

## Generate 2 — paket diagram

- buat sepuluh `.drawio`;
- ekspor sepuluh PNG;
- audit isi, notasi, konektor, keterbacaan, dan kesesuaian dengan core.

## Generate 3 — BAB III Draft v3

- tulis ulang naskah berdasarkan blueprint ini;
- tanam PNG;
- sertakan tabel inti;
- target 31–35 halaman;
- render DOCX dan audit seluruh halaman.

## Generate 4 — audit final bila diperlukan

- konsistensi BAB I–III;
- nomor/caption/cross-reference;
- kepadatan, pengulangan, layout, orientasi, dan daftar pustaka;
- revisi hanya pada temuan nyata.

---

# 12. KRITERIA KELUAR GENERATE 1/1.5 — `PASSED`

- [x] seluruh empat dokumen memakai versi yang benar;
- [x] BAB I–II tidak berubah;
- [x] lima dimensi identik pada seluruh core/working;
- [x] G1–G3 identik secara peran;
- [x] lima keluarga APKF dan semantik profil identik;
- [x] katalog berisi tepat 16 `profile_id` unik dan lima blok YAML valid;
- [x] `evidence_mode`, `run_purpose`, `skipped_not_applicable`, dan tiga status YAML konsisten;
- [x] seluruh `event_type` serta `reference_ids` YAML dapat diresolusikan ke katalog/registri aktif;
- [x] TRUE/FALSE memakai fakta eksplisit, sedangkan UNKNOWN tidak memakai fakta semu;
- [x] tiga kategori sampel serta larangan menjalankan malware identik;
- [x] simulator memiliki komponen, larangan, varian, oracle, dan urutan development;
- [x] katalog 20 authoring dan 8 holdout konsisten;
- [x] strategi tanpa lampiran dan target 31–35 halaman konsisten;
- [x] sepuluh diagram memiliki nama, fungsi, isi minimum, dan format sumber;
- [x] tidak ada code fence Markdown yang rusak;
- [x] keputusan v3.2 yang disupersesi tidak tampil sebagai instruksi aktif.

---

# 13. RIWAYAT VERSI RINGKAS

| Versi | Tanggal | Status | Perubahan utama |
|---|---|---|---|
| v1.0 | 3 Sep 2026 | arsip | kendali awal Draft v1 |
| v1.1 | 4 Sep 2026 | arsip | sinkronisasi core v3.2 dan audit Draft v1 |
| v1.2 | 5 Sep 2026 | arsip | blueprint serta revisi total Draft v2 |
| **v1.3** | **5 Sep 2026** | **aktif** | lima dimensi, lima keluarga/16 profil APKF, lima YAML `design_baseline`, tiga kategori sampel, simulator aman, tanpa lampiran, 10 diagram Draft v3; dilengkapi Generate 1.5 |

---

# 14. EVENT LOG

| ID | Tanggal | Peristiwa |
|---|---|---|
| E-01 | 5 Sep 2026 | Keputusan substansi APKF, sampel, dan simulator dikunci |
| E-02 | 5 Sep 2026 | BAB I–II ditetapkan read-only |
| E-03 | 5 Sep 2026 | Target BAB III 31–35 halaman dan tanpa lampiran formal dikunci |
| E-04 | 5 Sep 2026 | Paket sepuluh diagram `.drawio` + PNG dikunci |
| E-05 | 5 Sep 2026 | Generate 1 selesai: core v3.3 dan Working v1.3 terbentuk |
| E-06 | 5 Sep 2026 | Generate 1.5 menutup katalog 16 profil, YAML awal, aplikabilitas dua sumbu, fakta negatif, dan batas pembekuan sebelum diagram |
