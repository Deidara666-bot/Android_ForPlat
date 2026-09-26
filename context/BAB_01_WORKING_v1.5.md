# BAB_01_WORKING — PENELITIAN FORENSIK ANDROID

**Versi:** 1.5 — **CLEAN HANDOFF · LOCKED**
**Tanggal:** 29 Agustus 2026
**Menggantikan:** seluruh versi sebelumnya (v0.2–v1.4)
**Status:** Dokumen ini **dikunci**. BAB I selesai. Perubahan hanya dilakukan bila BAB II menemukan bukti yang memaksa — lihat §11.
**Fungsi:** Dokumen state tunggal untuk BAB I. Memuat claim map, status verifikasi, sumber, keputusan terkunci, dan pekerjaan tersisa.
**Aturan:** Untuk status teknis/scope, tetap tunduk pada Canonical v2.3.

---

## ⚠️ ATURAN BACA — WAJIB DIBACA LEBIH DULU

Dokumen ini pernah membawa status yang saling bertentangan antar-bagian. Sejak v1.2 berlaku empat aturan berikut.

1. **§14 Master Claim Registry adalah satu-satunya tabel status yang berlaku.** Bila §8 atau bagian per-claim di §1–§6 menyebut status berbeda, §14 yang menang.
2. **§15 adalah satu-satunya daftar tingkat verifikasi sumber yang berlaku.** §16 memuat metadata dan tautan, bukan status.
3. **Bagian berlabel `[ARSIP]` tidak menyatakan keadaan sekarang.** Isinya riwayat keputusan, disimpan agar alasan keputusan dapat ditelusuri.
4. **Riwayat versi di §20 bukan status.** Jangan membaca "Perubahan dari v0.x" sebagai keadaan sekarang.

### Ringkasan status — 29 Agustus 2026

| Butir | Keadaan |
|---|---|
| Draft BAB I | ✅ **LENGKAP** (`BAB_01_DRAFT_FINAL_2`), berformat institusi, **13 paragraf, tanpa gambar** |
| Claim aktif | 23 · seluruhnya `VERIFIED`, `FIXED`, atau `BOUNDED` |
| Sumber aktif | **26** · ●●● 21 · ●●○ 4 · peraturan 1 |
| Sumber ●○○ | **0** |
| Sumber REJECTED | 1 (Sikos 2021) |
| Pembanding metodologis | 7 (Tabel 1) + 4 berdampingan (Tabel 2) |
| Bloker berikutnya | Tabel Penelitian Terdahulu BAB II · keputusan clustering Execution state BAB III |

### Perubahan v1.0 → v1.2

| # | Perubahan | Asal |
|---|---|---|
| 1 | Status historis dibersihkan di tempatnya; `CANDIDATE` basi dihapus dari A0, A-delivery, B1, C3a, D1, E1, P2–P8 | audit v1.1 |
| 2 | Aturan baca ditambahkan; §14 dan §15 ditetapkan sebagai tabel status tunggal | audit v1.1 |
| 3 | Aturan verifikasi dipecah menurut **jenis sumber** (ilmiah / institusi / vendor) — §0 | gambar BAB I |
| 4 | Status **`BOUNDED`** ditambahkan, diterapkan ke D2 dan E1 | concern E |
| 5 | Definisi **"sumber aktif"** ditetapkan; rekap dihitung ulang jadi 26 / 21 / 4 | concern B |
| 6 | Claim **A0b** baru (skala produksi APK berbahaya) + sumber Kaspersky | Opsi A |
| 7 | Tiga dokumen OJK dipisah dengan nomor resmi; **R-A0-01b naik ●●●** | concern A |
| 8 | Batas A0 diubah: "maks 2 angka, 1 paragraf" → "1 paragraf; angka boleh lewat gambar" | Opsi A |
| 9 | Wording E1 dikunci: **"fakta forensik yang dinormalisasi dari artefak sistem Android"** | adjudikasi 22 concern |
| 10 | C4 **diturunkan** jadi klaim keragaman konfigurasi | adjudikasi 22 concern |
| 11 | Posisi intelijen: kata "pembuktian" **dihapus** | adjudikasi 22 concern |
| 12 | §17 Keputusan terkunci · §18 Checkpoint bersyarat · §19 Gambar · §14c Riwayat perubahan argumen — **baru** | sesi 29 Agu |
| 13 | Aturan **"N adalah keluaran tinjauan, bukan kuota"** | concern C |
| 14 | Wording cakupan ¶14 diperlebar agar cocok dengan venue sebenarnya | concern D |
| 15 | §8, §9, §10, §11 diperbarui; riwayat lama dilabeli `[ARSIP]` | — |

### Perubahan v1.2 → v1.3 — sinkronisasi sisa state lama

v1.2 memperbaiki status per-claim tetapi **melewatkan enam titik** yang masih membawa state lama. Karena §14 dideklarasikan sebagai tabel yang menang, kontradiksi di dalamnya paling berbahaya.

| # | Titik | Sebelum | Sesudah |
|---|---|---|---|
| 1 | **§14 registry — D2** | `FINAL`, Tabel 1 N=6 + Tabel 2 N=5 | 🔶 `BOUNDED`, **N=7 + N=4** |
| 2 | **§14 registry — C4** | "Satu perilaku, beberapa mekanisme" | Keragaman konfigurasi teknis *(sesuai penurunan v1.2)* |
| 3 | **§6 — E1 duplikat** | `OPEN`, "menunggu D2" | Dilabeli `[ARSIP]`; E1 aktif ada di §6 bagian pertama |
| 4 | **§12 — RQ1 & RQ3** | RQ3 "Bagaimana kinerja … dinilai" | RQ3 **"Sejauh mana …"**; RQ1 diberi gloss *(provenance)* — sesuai naskah final |
| 5 | **§9 — panduan intelijen** | "mendukung kapabilitas penyelidikan **dan pembuktian**" | "penyelidikan **dan analisis informasi**" *(keputusan terkunci 4)* |
| 6 | **§12 — Batasan Masalah** | 5 butir tanpa label; butir 2 memakai "user-secret-based"; tanpa metode pembanding | **5 butir berlabel** sesuai naskah final; wording akuisisi kembali ke canonical; metode pembanding masuk |
| 7 | **§13 — status kesiapan** | "Tabel 1 N=6 + Tabel 2 N=5" | N=7 + N=4 |

### Perubahan v1.4 → v1.5 — clean handoff

Hanya kebersihan dokumen. **Tidak ada perubahan riset, naskah, claim, sumber, maupun keputusan.**

| # | Perbaikan | Sebelum | Sesudah |
|---|---|---|---|
| 1 | Jumlah claim di changelog v1.4 | "Ke-24 claim aktif" | **23 claim aktif; 22 punya alamat paragraf** (B1 `VERIFIED` tetapi tidak `USED`) |
| 2 | §13 — jumlah claim terverifikasi | "14 claim VERIFIED full-text" | **20 `VERIFIED` + 2 `BOUNDED` + 1 `FIXED`** |
| 3 | §13 — peta paragraf | "Peta 17 paragraf + alokasi porsi" | **Peta 13 paragraf** |
| 4 | §13 — judul & simpulan | "KESIMPULAN v0.7 — Paragraf 1–16 dapat ditulis" | **Simpulan v1.5 — seluruh 13 paragraf sudah ditulis** |
| 5 | §13 — landasan bukti | "14 claim, 12 sumber full-text, 6 pembanding" | **23 claim, 21 sumber ●●●, 7 pembanding** |
| 6 | §9 — alokasi porsi | blok 17 paragraf, pembanding 7 hal/17 paragraf | **dilabeli `[ARSIP]`**; digantikan peta 13 paragraf |
| 7 | **§20 — penomoran log versi** | konten pra-v1.0 tergeser **satu versi ke bawah** | **diperbaiki**; v0.9 ditambahkan |

⚠️ **Perbaikan nomor 7 adalah kesalahan gua yang paling substantif di sini.** Pada v1.2 log lama dari v1.0 disalin dengan pembacaan yang keliru: baris *"Perubahan dari v0.8"* di dokumen v1.0 berarti *"apa yang dikerjakan v0.9"*, bukan *"apa yang dikerjakan v0.8"*. Akibatnya seluruh entri pra-v1.0 tercatat satu nomor terlalu rendah, dan **v0.9 hilang sama sekali**. Sudah dikoreksi di §20.

---

### Perubahan v1.3 → v1.4 — pemangkasan panjang Latar Belakang

**Pemicu:** komparasi terhadap enam Latar Belakang senior seangkatan menunjukkan draft ini adalah pencilan.

| Senior | Halaman Latar Belakang | Gambar |
|---|---|---|
| Matthew — API scraping Telegram | ~7,5 | 4 |
| Ferlando — spyware pemantauan layar | ~7 | — |
| Rafly — AES-256 self-destruct | 5 | — |
| Nico — post-quantum cryptography | 4 | — |
| Irham — HID ekstraksi data | 3 | 1 |
| Imam — secure file deletion | ~2,5 | — |

Median ≈ 4,5 halaman; terpanjang 7,5. Draft v1.3 berada di **~12 halaman** Latar Belakang saja — 60 persen lebih panjang dari yang terpanjang.

| # | Perubahan | Efek |
|---|---|---|
| 1 | **Dua gambar dihapus.** Empat dari enam senior tidak memakai gambar sama sekali | −1,4 halaman |
| 2 | **17 → 13 paragraf.** Empat penggabungan: ¶2+3, ¶4+5, ¶12+13, ¶14+15 | struktur |
| 3 | **~2.350 → 1.893 kata** — pemangkasan pengulangan, bukan claim | −19% |
| 4 | **Sutter (R-C3-01) dibuang dari naskah** — tumpang tindih fungsi dengan Ehsan dan satu-satunya ●●○ yang masih dipakai | higiene sumber |
| 5 | **Bernardo (R-T2-04) dibuang dari naskah** — kalimat tata kelola bersifat dekoratif | −30 kata |
| 6 | Batas A0 kembali ke **"maks 2 angka, 1 paragraf"** karena gambar hilang | aturan |
| 7 | §19 Gambar dilabeli `[ARSIP]` | — |
| 8 | §22 Prinsip pemangkasan ditambahkan | baru |

**Hasil: Latar Belakang ~12 → ~8,5 halaman; BAB I utuh 17 → 14 halaman.**

⚠️ **Nol claim dibuang.** Seluruh **23 claim aktif** tetap berstatus `VERIFIED`, `BOUNDED`, atau `FIXED`; **22 di antaranya punya alamat paragraf** di §9. Satu-satunya yang tidak disitir langsung adalah **B1**, yang berstatus `VERIFIED` tetapi tidak `USED` — fungsinya ditanggung C1 dan C2 di naskah.

⚠️ **Konsekuensi hilangnya gambar:** tujuh angka yang hanya hidup di grafik ikut hilang — 74.243 dan 432.637 (Gambar 1.1) serta 1.661.743, 1.315.405, 1.133.329, 196.476, dan 153.682 (Gambar 1.2). Yang hilang **detail statistik, bukan premis argumentatif**; angka penopang klaim tetap ada di prosa. Ketiga sumber OJK dan sumber Kaspersky **tetap `VERIFIED` ●●●** dan tetap di §15/§16 — dua di antaranya kini menjadi rujukan cadangan, bukan sumber yang disitir.

⚠️ **Pagar anti-drift pindah ke prosa.** Gambar 1.2 versi dua garis dulu menjadi pagar visual agar *trojan* perbankan terbaca sebagai irisan, bukan keseluruhan. Tanpa gambar, pagar itu ditanggung kalimat di ¶1: *"…dan trojan perbankan hanyalah satu kategori di dalam kelompok yang lebih luas."* **Kalimat itu tidak boleh dihapus.**

**Naskah BAB I berubah pada v1.4.** Berkas berlaku: `BAB_01_DRAFT_FINAL_2.docx` / `.md`.

---

⚠️ **Yang TIDAK diubah:** frasa **"nilai pembuktian bukti"** (*evidentiary value*) di C5, RQ2, dan §14b tetap berlaku dan benar. Yang dihapus hanya **"pembuktian" sebagai fungsi intelijen** — dua hal berbeda yang kebetulan memakai kata yang sama.

**Naskah BAB I tidak berubah pada v1.3.** Seluruh perbaikan ini hanya menyinkronkan map dengan naskah yang sudah benar.

**Tidak ada isi v1.0 yang dibuang.** Matriks D2, bedah P9/P10/P2, paragraf scoping, kutipan presisi, Tabel 1 & 2, jebakan terminologi, dan alokasi halaman tetap utuh.
---

## 0. Skema ID dan Aturan Status

**Skema ID resmi: A–E.** Tidak ada skema lain. Skema lama (C01–C12, A1–A8) dihentikan dan diserap ke sini.

| Status | Arti |
|---|---|
| `NEED SOURCE` | Belum ada kandidat sumber |
| `CANDIDATE` | Sumber ditemukan, metadata dicek, **full-text belum dibaca**. *(Sejak v1.2 tidak ada lagi claim aktif berstatus ini.)* |
| `BOUNDED` | **Baru v1.2.** Klaim yang benar terhadap himpunan literatur yang ditinjau, bukan terhadap seluruh literatur. Tidak dapat naik jadi `VERIFIED` dengan menambah sumber — yang melebar hanya cakupannya. Diterapkan ke **D2** dan **E1** |
| `VERIFIED` | Full-text sudah dibaca sendiri + chain-of-attribution sudah dicek |
| `USED` | Sudah masuk draft |
| `REJECTED` | Tidak mendukung / tidak valid / tidak dapat diakses |

**Aturan wajib sebelum naik ke VERIFIED:**
1. Full-text dibaca sendiri, bukan dari abstrak/cuplikan pencarian.
2. **Cek atribusi:** apakah klaim ini temuan asli paper tersebut, atau paper ini cuma mengutip sumber lain? Kalau relay → sumber primer wajib dibaca dulu.

Aturan 2 ditambahkan setelah insiden Moreb→Sikos (lihat §6).

---

### Aturan naik ke ●●● berbeda menurut jenis sumber *(baru v1.2)*

**Jenis 1 — Artikel ilmiah.** Dua syarat, keduanya wajib:
1. Full-text dibaca sendiri, bukan dari abstrak atau cuplikan pencarian.
2. **Cek rantai atribusi:** apakah klaim ini temuan asli paper tersebut, atau paper ini hanya mengutip sumber lain? Bila relay, sumber primer wajib dibaca dulu. *(Aturan 2 lahir dari insiden Moreb→Sikos, §7.)*

**Jenis 2 — Dokumen institusi (siaran pers, laporan lembaga).** Dokumen dibaca langsung pada kanal penerbitnya **dan** nomor dokumen resminya dicatat. Cek rantai atribusi tidak berlaku, karena lembaga penerbit adalah sumber primer angka tersebut.

**Jenis 3 — Laporan vendor keamanan.** Sama dengan Jenis 2, ditambah satu syarat wajib: **batas metodologisnya dinyatakan di naskah.** Angka telemetri vendor bukan angka populasi.

### Definisi "sumber aktif" *(baru v1.2)*

Sumber **aktif** = dokumen yang **disitir di naskah BAB I** *atau* **disimpan sebagai pembanding untuk BAB II**.
Tidak dihitung aktif: sumber cadangan yang belum masuk naskah, dan sumber `REJECTED`.
Definisi ini dipakai untuk seluruh rekap angka di dokumen ini.

---

## 1. LAPISAN A — INCIDENT CONTEXT

Menjawab: *kenapa kita bicara APK penipuan Android?*

### ⚠️ Keputusan framing (v0.2) — statistik phishing DITURUNKAN

**Framing lama** menumpuk statistik phishing nasional (BSSN 26,7 juta aktivitas phishing; OJK Rp9,1 triliun) sebagai pembuka. **Itu ditolak** karena tiga alasan:

1. **Kategori tidak sejajar.** Statistik phishing mengukur **anomali trafik jaringan** (deteksi level domain/URL). Insiden penelitian ini adalah **aplikasi terpasang di perangkat**. Mekanisme, artefak, dan cara investigasinya berbeda.
2. **Membuktikan hal yang salah.** Statistik membuktikan *masalahnya besar*. Penelitian ini tentang *sulitnya investigasi*. Rp9,1 triliun tidak menghasilkan satu pun premis yang dibutuhkan Lapisan C.
3. **Pola generik.** Menumpuk lima statistik di depan mengembalikan narasi ke pola "perkembangan teknologi semakin pesat, berdasarkan data X juta…" yang sejak awal dihindari.

**Prinsip pengganti:** *statistik menetapkan relevansi, deskripsi teknis menetapkan spesifisitas.* Satu paragraf angka cukup memenuhi ekspektasi format; sisanya dipakai membangun masalah.

**Phishing/social engineering turun posisi** dari framing utama menjadi **A-delivery** (supporting/opsional).

---

### A0 — Penipuan transaksi keuangan memiliki skala terukur

**Claim kerja:** Penipuan transaksi keuangan/digital merupakan persoalan aktual dengan volume laporan yang terukur, sehingga memberikan konteks praktis bagi penelitian terhadap insiden fraud yang melibatkan aplikasi Android.

**Status: ✅ `VERIFIED` `USED` (¶1)** — dinaikkan v1.2 setelah tiga siaran pers OJK dibaca langsung pada kanal penerbitnya (aturan Jenis 2).

**Sumber utama — OJK/IASC (sumber primer resmi):** sejak beroperasi 22 November 2024 sampai 30 Juli 2026, IASC menerima **636.014 laporan** penipuan transaksi keuangan, dengan 1.176.571 rekening dilaporkan dan terverifikasi serta 604.923 rekening diblokir.
🔗 https://ojk.go.id/id/berita-dan-kegiatan/siaran-pers/Pages/RDKB-Juli-2026.aspx

**Kenapa OJK, bukan statistik phishing:** unitnya **laporan penipuan finansial** — lebih dekat ke domain penelitian daripada anomali trafik jaringan. Statistik phishing mengukur deteksi level domain/URL; penelitian ini tentang aplikasi terpasang di perangkat.

**Opsional (konteks global):** Kaspersky (2024) — lonjakan 196% serangan Trojan banker pada smartphone, lebih dari 1,24 juta serangan pada perangkat Android. 🔗 https://www.bitsight.com/blog/toxicpanda-android-banking-malware-2025-study

**⚠️ BSSN TIDAK DIPERLUKAN di A0** (perubahan v0.5). Sebelumnya BSSN diposisikan sebagai sumber utama Lapisan A; kini turun jadi opsional di A1 saja. Konfirmasi BSSN bukan lagi bloker.

**⚠️ ATURAN KETAT:** maksimal **dua angka**, **satu paragraf**. A0 tidak menopang RQ manapun (lihat uji paragraf yatim, §12) — fungsinya relevansi, bukan premis. Jika melebar, dia jadi beban tanpa fungsi argumentatif.

**Batas penalaran — yang TIDAK boleh disimpulkan:**
- ❌ 636.014 laporan itu adalah APK fraud
- ❌ angka tersebut membuktikan rekonstruksi APK sulit
- ❌ jumlah laporan membuktikan rule-based correlation dibutuhkan

**Kalimat jembatan yang aman:** *"Dalam lingkungan penipuan transaksi keuangan berskala nasional tersebut, penggunaan berkas APK yang dipasang pada perangkat korban merupakan salah satu modus yang telah didokumentasikan secara teknis."*

**Beban: SUPPORTING CONTEXT.**

---

### A1 — APK sebagai komponen teknis aktif pada perangkat

**Claim kerja:** Aplikasi Android berbahaya yang digunakan dalam konteks fraud dapat menjadi komponen teknis aktif pada perangkat setelah installation/activation, dengan capability yang dapat mencakup akses terhadap fungsi atau data sensitif, interaksi dengan aplikasi/perangkat, serta komunikasi dengan infrastruktur eksternal.

**Status: `VERIFIED`** ✅ **(tiga sumber, semuanya full-text dibaca)**

> **⚠️ URUTAN PENYEBUTAN WAJIB DIJAGA.** Umam disebut **pertama**. Hook dan Anubis keduanya banking trojan; jika mereka mendominasi, incident family bergeser menjadi "Banking Trojan" — hal yang `PROJECT_BRIEF` §4 larang eksplisit. Umam adalah jangkar incident family.

#### 1️⃣ Umam dkk. (2025) — JANGKAR INCIDENT FAMILY

*Analisis Aplikasi Malware pada Android Menggunakan Reverse Engineering dan Framework D4I.* Jurnal Ilmu Komputer dan Desain Komunikasi Visual, 10(2), 198–214. UIN Sunan Ampel Surabaya. ISSN 2541-4585. CC BY 4.0.

**Kenapa pertama:** Undangan.apk — APK fraud Indonesia murni, **bukan** banking trojan. Persis incident family penelitian ini.

**Bukti teknis (full-text):**
- Package: `com.google.androidsmsotpteski`, tidak ditemukan di Google Play Store
- Permission manifest: `RECEIVE_SMS`, `READ_SMS`, `SEND_SMS`, `INTERNET`
- Receiver: `abyssalarmy.smseye2.tools.SmsEyeSmsListener` untuk pemantauan SMS
- Komunikasi eksternal: Telegram Bot API, dengan URL dan token yang terekstrak
- `this.device` = gabungan `Build.FINGERPRINT` + `Build.TIME` + fragment encode set

#### 2️⃣ Riadi, Sunardi & Aprilliansyah (2023) — KEDALAMAN KAPABILITAS

*Analysis of Anubis Trojan Attack on Android Banking Application Using Mobile Security Labware.* IJSSE, 13(1), 31–38. DOI 10.18280/ijsse.130104. CC BY 4.0. Universitas Ahmad Dahlan, Yogyakarta. CiteScore 2.8, Scopus.
🔗 PDF gratis: https://www.iieta.org/download/file/fid/92945

**Bukti teknis (full-text):** sampel FakeWhatsapp.apk; permission manifest mencakup receive SMS, read SMS, system alert window, record audio, read contacts, package usage stats; Accessibility service **dipaksa aktif** dan diaktifkan ulang bila pengguna mencoba mematikannya; IOC lengkap (MD5/SHA1/SHA256); domain C2 `pepito.club`.

#### 3️⃣ Schmutz, Rapp & Fehrensen (2024) — SKALA & VARIASI

*Forensic analysis of hook Android malware.* FSI:DI 49, 301769. Bern University of Applied Science. **CC BY 4.0**. DOI 10.1016/j.fsidi.2024.301769.

**Bukti teknis (full-text):** 64 sampel Hook dianalisis dengan metode statis dan dinamis; model malware-as-a-service; permission paling kritis adalah `BIND_ACCESSIBILITY_SERVICE` dan `BIND_DEVICE_ADMIN` (keduanya ditandai *critical!* dan hadir di 64/64 sampel).

**Opsional:** BSSN (2023), imbauan keamanan modus APK undangan pernikahan — penguat konteks kelembagaan, bukan tumpuan.

**Beban: CORE INCIDENT CLAIM.**

---

### A2 — Insiden menghasilkan situasi investigatif tertentu

**Claim kerja:** Dalam pemeriksaan insiden yang melibatkan aplikasi Android berbahaya, investigator menghadapi artefak teknis yang merepresentasikan identitas/konfigurasi aplikasi, state kapabilitas, data lokal aplikasi, informasi terkait eksekusi, serta komunikasi eksternal. Karena aktivitas yang diteliti telah berlalu, analisis forensik menggunakan artefak tersebut untuk merekonstruksi perilaku.

**Status: `VERIFIED`** ✅ — **paragraf terkuat di seluruh Lapisan A; ketiga sumbernya forensik**

> **Catatan struktur:** klaim ini menggabungkan kapabilitas majemuk + representasi artefak menjadi satu. Digabung karena Lapisan A hanya perlu membawa pembaca dari konteks fraud ke problem investigatif; versi terpisah tumpang tindih dengan B1 dan C2.

#### Sub-bukti 1 — Kapabilitas majemuk dan **bervariasi**

**⭐ Hook Tabel 2** mendaftar permission dengan kolom jumlah sampel dari 64. Angkanya **tidak seragam**:

| Permission | # sampel |
|---|---|
| BIND_ACCESSIBILITY_SERVICE, BIND_DEVICE_ADMIN, READ_SMS, RECEIVE_SMS, SEND_SMS, dll. | **64** |
| ACCESS_BACKGROUND_LOCATION | **58** |
| ACCESS_CONTENT_PROVIDERS_EXTERNALLY | **32** |
| GET_ACCOUNTS | **6** |
| ACCESS_LOCATION_EXTRA_COMMANDS | **3** |
| BATTERY_STATS | **1** |

→ **Variasi ini terjadi di dalam satu malware family yang sama.** Bukan antar-keluarga, bukan antar-kasus. Ini menjadikan variasi mekanisme sebagai **pola terukur**, bukan anekdot.

#### Sub-bukti 2 — Kapabilitas terepresentasi sebagai **state residual**

**⭐ Hook Tabel 7** memetakan data yang disimpan lewat SharedPreferences API. Pola deskripsinya:

| Preference | Deskripsi |
|---|---|
| `autoClickAdmin` | Set to 1 **after** `startadmin` has been executed |
| `autoClickSms` | Set to 1 **after** `hiddenSMS` has been applied |
| `whatsappsend` | Set to 1 **after** `openwhatsapp` has been executed |
| `authenticator2` | Set to 1 **after** `startauthenticator2` has been executed |
| `lastDownloadInjects` | Time of the last download of webinjects in Unix time |

→ **Ini C3b dalam bentuk Android konkret.** Flag bernilai 1 adalah state residual yang menandakan perintah pernah dieksekusi. Flag = artefak (dasar inferensi E′); eksekusi = peristiwa (E).

**Anubis** memberi bukti sejenis: data yang diperoleh disimpan di database SQLite pada `data/data/<package>/app_webview/Cookies` dan `/WebData`, lalu dikirim ke server C2.

**⭐⭐ Dan perhatikan lokasinya:** SharedPreferences = `/data/data/<package>/shared_prefs/`; SQLite Anubis = `/data/data/<package>/app_webview/`. Keduanya **penyimpanan privat aplikasi — tidak terjangkau ADB non-root.**

→ Dua paper ini secara tidak sengaja mendemonstrasikan **C1 pada incident family penelitian ini sendiri**: artefaknya ada, berisi informasi investigatif, dan tidak dapat diakuisisi pada baseline. Jauh lebih konkret daripada pernyataan umum.

#### Sub-bukti 3 — Dan harus direkonstruksi setelah kejadian

**Breitinger dkk. (2025)** — event reconstruction sebagai proses menginfer aktivitas masa lalu melalui analisis artefak digital; pembedaan E vs E′.

---

**⚠️ Batasan yang harus diakui:** analisis dinamis Hook memakai Android Virtual Device berbasis QEMU dengan C2 tersimulasi; Anubis memakai Genymotion Android 10. **Keduanya emulator, bukan perangkat sitaan.** Akui eksplisit bila dikutip untuk klaim tentang situasi pemeriksaan nyata.

**Kenapa A2 penting:** klaim ini mengubah narasi dari *"ada aplikasi jahat"* menjadi *"ada situasi pemeriksaan"*. Setelah A2, pembaca sudah berada di dalam masalah forensik, sehingga B2 terasa sebagai kelanjutan alami.

**Beban: CORE — jembatan.**
### A-delivery — Phishing/social engineering sebagai salah satu mekanisme distribusi

**Claim kerja:** Phishing dan social engineering merupakan salah satu mekanisme yang dapat digunakan untuk mendistribusikan APK fraud kepada korban.

**Status: ✅ `VERIFIED` `USED` (¶2) — SUPPORTING SAJA**

Sumber tersedia melimpah (BSSN, Cleafy, Bitsight, statistik phishing nasional). Tapi **posisinya satu kalimat**, bukan paragraf, dan **bukan pembuka**.

**Alasan diturunkan:** mekanisme distribusi berada **di luar scope akuisisi** penelitian ini. Investigasi dimulai dari perangkat yang sudah terpasang APK — bagaimana APK sampai ke sana adalah konteks, bukan objek penelitian.

---

### Ringkasan alur Lapisan A

```
A0  Skala terukur penipuan finansial      ← 1 paragraf, maks 2 angka
    (OJK/IASC 636.014 laporan)               tidak menopang RQ manapun
      ↓
A1  APK sebagai komponen teknis aktif     ← Umam DULU, lalu Anubis, Hook
    (Umam ✅ / Anubis ✅ / Hook ✅)
      ↓
A2  Situasi investigatif yang muncul      ← JEMBATAN ke forensik
    kapabilitas bervariasi (Hook Tbl 2)
    + state residual (Hook Tbl 7, Anubis)
    + harus direkonstruksi (Breitinger)
      ↓
    [lanjut ke B2: akuisisi sudah mapan]

A-delivery: phishing = satu kalimat, disisipkan di A1
BSSN: opsional, penguat konteks di A1 — BUKAN bloker
```

**Tiga klaim, tiga paragraf.** Satu paragraf statistik, dua paragraf teknis.

**Skor Lapisan A v1.2: A0, A0b, A1, A2, A-delivery — seluruhnya `VERIFIED` dan `USED`.**

> `[ARSIP]` Skor v0.5: A1 dan A2 VERIFIED (tiga sumber full-text), A0 CANDIDATE.
## 2. LAPISAN B — FORENSIC POSITIONING

Menjawab: *kenapa ini persoalan forensik, bukan deteksi malware?*

### B1 — Android menyediakan multiple forensic artifacts

**Status: ✅ `VERIFIED`** — dinaikkan v1.2. Casey dkk. (2022) tetap ●●○, tetapi hanya menopang klaim tentang **fokus** paper (definisi *atomic* vs *dependent artifact*), bukan tentang temuannya; klaim substantifnya ditopang Moreb (2024) ●●●.

**Sumber baru:** Casey, E., Nguyen, L., Mates, J., & Lalliss, S. (2022). *Crowdsourcing forensics: Creating a curated catalog of digital forensic artifacts.* Journal of Forensic Sciences, 67(5), 1846–1857. DOI 10.1111/1556-4029.15053.
🔗 Gratis: https://pmc.ncbi.nlm.nih.gov/articles/PMC9543441

**Kenapa berguna:** Paper ini mendefinisikan **atomic artifact** vs **dependent artifact** — definisi yang dipakai Breitinger dkk. (2025) sebagai rujukan resmi. Highlight-nya juga menyatakan bahwa volume, variasi, distribusi, dan kompleksitas bukti digital menyulitkan praktisi menemukan dan memahami informasi yang paling berguna secara forensik.

**Nilai tambahan:** memberi kosakata formal untuk membedakan artefak tunggal dari artefak yang butuh artefak lain untuk dimaknai — langsung relevan dengan desain parser/normalizer.

**Pendukung:** Moreb (2024) untuk daftar jenis evidence.

---

### B4 — Analisis manual tidak praktis pada skala evidence forensik

**Claim kerja:** Volume dan kompleksitas evidence hasil pemeriksaan forensik membuat analisis manual tidak praktis, sehingga otomasi diperlukan untuk menginferensi event pada skala nyata.

**Status: `VERIFIED`** ✅

**Sumber:** Breitinger dkk. (2025), Bagian 9.4.
🔗 Gratis: https://arxiv.org/html/2504.18131v1

**Bukti spesifik:**
- **Research Gap 5:** tantangan melakukan timeline analysis yang efisien dan efektif masih belum terselesaikan; menangani volume timestamp yang diekstraksi secara efektif masih dibutuhkan.
- **Research Gap 6:** otomasi kemungkinan **satu-satunya cara praktis** untuk menangani tantangan menginferensi event dalam skala besar.
- Bagian 6.4.1: volume entri timeline membuat analisis memakan waktu dan membebani examiner.

**⚠️ KENAPA CLAIM INI WAJIB ADA:** Ini skripsi **pengembangan**. Tanpa B4, seluruh BAB I membuktikan "ada masalah analisis" tapi **tidak membuktikan bahwa jawabannya adalah perangkat lunak**. Rule-based correlation bisa dijalankan manual sebagai checklist/SOP. Pertanyaan penguji *"kenapa harus aplikasi, kenapa nggak cukup prosedur?"* dijawab di sini.

**Beban: LOAD-BEARING.**

---

### B5 — Reprodusibilitas menuntut metode yang deterministic

**Claim kerja:** Hasil forensik harus dapat direproduksi untuk diterima secara metodologis dan hukum; metode yang non-deterministik bertentangan dengan syarat tersebut.

**Status: `VERIFIED`** ✅ (dua sumber independen, dulu S3)

**Sumber 1:** Breitinger dkk. (2025), Bagian 6.3.2 — LLM bermasalah karena sifat non-deterministiknya serta data dan proses pelatihan yang sering tidak transparan; tools AI juga memunculkan persoalan explainability.
🔗 https://arxiv.org/html/2504.18131v1

**Sumber 2:** *Large language models in digital forensics: capabilities, challenges and future directions.* FSI:DI — sifat probabilistik output LLM membuat input identik dapat menghasilkan output berbeda, yang bertentangan secara fundamental dengan syarat reprodusibilitas untuk penerimaan metode forensik dan admisibilitas hukum bukti digital.

**⚠️ KENAPA WAJIB ADA:** Kata "deterministic" muncul di rumusan masalah dan desain. Tanpa B5, istilah itu muncul di BAB I tanpa argumen pendukung. Ini juga jawaban untuk *"kenapa tidak pakai AI/ML saja?"*

**Beban: LOAD-BEARING.**

---

### B6 — Pemisahan fakta dari hipotesis menuntut traceability eksplisit

**Claim kerja:** Hasil analisis forensik perlu membedakan secara eksplisit antara data yang diekstraksi sebagai fakta dan event hasil inferensi sebagai hipotesis kerja; pembedaan ini menuntut keterlacakan dari temuan kembali ke sumbernya.

**Status: `VERIFIED`** ✅ (dulu S2)

**Sumber:** Breitinger dkk. (2025), Bagian 9.4 dan 6.3.2.
🔗 https://arxiv.org/html/2504.18131v1

**Bukti spesifik:**
- **Research Gap 7:** dibutuhkan delineasi yang jelas antara nilai timestamp yang diekstraksi **sebagai fakta**, dan inferred event **sebagai hipotesis kerja**, baik dalam riset maupun dalam tooling forensik.
- Bagian 6.3.2: tools sering **mencampur fakta dengan interpretasi** di antarmukanya — contohnya, adanya data pencarian Google mudah disalahartikan sebagai fakta bahwa pencarian itu benar-benar terjadi.
- Bagian 9.4: saat entri diringkas menjadi high-level event, kemampuan kembali ke tampilan entri level rendah penting untuk melihat konteks dan **menunjukkan provenance** dari event yang direkonstruksi.

**⚠️ KENAPA WAJIB ADA:** Menopang hierarki Artifact → Event → Behavior → Technique → Tactic → Hypothesis, dual traceability, dan penggantian istilah "confidence" menjadi Rule Match Score / Evidence Support Score.

**Beban: LOAD-BEARING.**

### B2 — Analisis/rekonstruksi adalah tahap penting setelah akuisisi

**Claim kerja:** Investigasi forensik mobile tidak berhenti pada acquisition/extraction; data yang diperoleh masih memerlukan examination, interpretation, validation, dan analysis/reconstruction.

**Status: `VERIFIED`** ✅

**Sumber:** Moreb, M., Salah, S., & Amro, B. (2024). *A Novel Framework for Mobile Forensics Investigation Process.* International Journal of Computing and Digital Systems, 16(1), 125–135. DOI: 10.12785/ijcds/160110.

**Bukti spesifik (full-text dibaca):**
- Framework MFIPF memisahkan 4 fase: Data Preparation → Information Analysis → Case Construction → Case Closing
- Fase Information Analysis punya sub-langkah: Selection of Forensic Tools → Information Examination → Evidence Validation → **Evidence Correlation** (hlm. 129–130)

**Fungsi di BAB I:** Blok "akui bahwa jalur forensik sudah mapan" — dipakai sebelum masuk ke masalah.

### B3 — Integritas, provenance, reproducibility penting

**Status: `VERIFIED` (sebagian)** ✅

**Sumber:** Moreb dkk. (2024), hlm. 130 — bagian Evidence Validation dan Results Analysis: pembahasan validation, standar NIST, hash comparison dengan dua tool berbeda, dan keharusan hasil bersifat repeatable. Tabel I juga membandingkan kapabilitas "Hash-Comparison" antar tool.

---

## 3. LAPISAN C — TECHNICAL FORENSIC PROBLEM

Tulang punggung BAB I. Alokasi paragraf terbesar di sini.

### C1 — Ketersediaan/observability evidence tidak seragam

**Claim kerja:** Ketersediaan digital evidence pada Android tidak seragam; mekanisme keamanan perangkat, tingkat privilege, serta metode dan tool akuisisi memengaruhi jenis dan jumlah data yang berhasil diperoleh.

**Status: `VERIFIED`** ✅ **(full-text kedua sumber dibaca, v0.3-rev)**

> **⚠️ KOREKSI v0.3-rev:** versi sebelumnya menandai Fukami sebagai "konflik scope" karena mengusulkan exploit-based acquisition. **Penilaian itu keliru** — didasarkan pada highlights publisher, bukan isi paper. Setelah full-text dibaca, Fukami justru mendukung baseline non-root secara langsung. Ini contoh kedua (setelah BlockFECS) bahwa metadata dan ringkasan tidak cukup.

---

#### Sumber 1 — Fukami, A., Stoykova, R., & Geradts, Z. (2021)

*A new model for forensic data extraction from encrypted mobile devices.* FSI:DI 38, 301169. Open access CC BY. Netherlands Forensic Institute / Univ. of Groningen / Univ. of Amsterdam / NTNU. Proyek EU EXFILES (Horizon 2020, No. 883156).
🔗 https://doi.org/10.1016/j.fsidi.2021.301169

**⭐ Bukti utama — Bagian 3.2 (File system extraction):** untuk melakukan file system extraction yang efektif, **rooting perangkat dibutuhkan**; tanpa rooting, examiner **hanya dapat mengakuisisi data parsial** dan pemulihan data mungkin terbatas.

→ Ini C1 untuk baseline non-root, dari jurnal forensik, dalam scope yang persis sama. Tidak ada sumber yang lebih tepat.

**⭐ Bukti kedua — Bagian 3.1 (Manual/logical extraction):** pada perangkat mobile modern, **aplikasi dapat memilih untuk tidak menjadi bagian dari operasi backup** yang didukung OS. Jika data dari aplikasi yang opt-out dibutuhkan, menurunkan versi aplikasi mungkin membukanya — tetapi karena itu memodifikasi perangkat target secara langsung, mereka menyatakan itu harus dianggap **opsi terakhir**.

→ Lebih spesifik dari sekadar "data mungkin tidak tersedia": *aplikasi tertentu dapat secara sengaja tidak terakuisisi lewat kanal logical*. Untuk penelitian tentang APK, ini sangat relevan.

**Bukti ketiga — Bagian 2.3:** bertentangan dengan keyakinan tradisional, naik lebih tinggi dalam model lima level NIST **tidak selalu lebih efektif** untuk pemulihan data forensik pada smartphone modern; tanpa teknik dekripsi, mengakuisisi data fisik tidak menghasilkan data bermakna.

#### ⭐ Gambar 1 Fukami — pakai untuk memposisikan batas akuisisi

Flowchart mereka bercabang pada *"User authentication credentials known?"*:

```
                 User authentication credentials known?
                    │                          │
                   YES                         NO
                    │                          │
     ┌──────────────────────────┐   ┌───────────────────────────┐
     │ Manual control &         │   │ Bypassing/disabling lock  │
     │ logical data extraction  │   │ Special download mode     │
     │ File system acquisition  │   │ Custom bootloader         │
     │ Cloud based extraction   │   │ Other vulnerabilities     │
     │                          │   │                           │
     │ "User secret based       │   │ "Vulnerability            │
     │  extraction"             │   │  exploitation based"      │
     └──────────────────────────┘   └───────────────────────────┘
              ▲
       BASELINE PENELITIAN INI
```

**Baseline authorized non-root ADB berada di cabang YES.** Seluruh pembahasan exploit ada di cabang NO.

→ Penelitian ini **tidak berada di luar model Fukami — berada pada satu cabang spesifik di dalamnya.** Ini menguntungkan: model Fukami dapat dipakai untuk **memposisikan batas akuisisi secara presisi**, bukan sekadar menyatakannya.

**Kalimat yang dapat dipakai:** *"Mengikuti model akuisisi Fukami dkk. (2021), penelitian ini berada pada jalur user-secret-based acquisition, sehingga jalur vulnerability-exploitation-based berada di luar cakupan penelitian."*

**⚠️ ATURAN SITASI:** kutip **Bagian 2.3, 3.1, 3.2, dan Gambar 1**. **Jangan** kutip Bagian 6 (model yang diusulkan) sebagai penopang klaim — itu kontribusi mereka, bukan bagian yang dipakai.

---

#### Sumber 2 — Salimi, N. F., Abd Warif, N. B., & Ismail, N.-S. N. (2022)

*Comparative Analysis of Logical Acquisition Using Wondershare Dr. Fone, MOBILedit Forensic, and FonePaw on Android Phones.* Malaysian Journal of Computing, 7(2), 1162–1177. eISSN 2600-8238. DOI 10.24191/mjoc.v7i2.16968. Open access CC BY-SA.
🔗 PDF gratis: `ir.uitm.edu.my/id/eprint/69248/1/69248.pdf`

**✅ Urutan penulis TUNTAS:** halaman judul PDF menulis **Nuraimi Farhana Salimi¹, Nor Bakiah Abd Warif²\*, Nor-Syahidatul N Ismail³**. Salimi memang penulis pertama. Running header halaman dalam menulis "Abd Warif et. al." — **inkonsistensi typesetting jurnal, bukan urutan resmi.** Ikuti halaman judul.

**✅ Angka 56% TERKONFIRMASI:** MOBILedit Forensic pada Samsung S7 Edge memperoleh 2.278 dari 4.091 data handset (56%). Peringatan sebelumnya tidak perlu.

**⭐ Angka yang lebih kuat — kegagalan per jenis data (jangan pakai rata-rata):**

| Tool | Perangkat | Jenis data | Handset | Terakuisisi |
|---|---|---|---|---|
| Dr. Fone | Oppo F9 | Pesan | 161 | **0** |
| Dr. Fone | Samsung S7 Edge | Pesan | 31 | **0** |
| Dr. Fone | keduanya | Dokumen | 127 / 55 | **0** |
| MOBILedit | Samsung S7 Edge | Video | 184 | **1** |
| MOBILedit | Samsung S7 Edge | Foto | 3.030 | 1.400 |
| MOBILedit | Oppo F9 | Foto | 301 | 104 |

→ Kegagalan bergantung pada **kombinasi tool × jenis data × perangkat**, bukan sekadar "tool A lebih baik dari tool B". Jauh lebih tajam daripada mengutip rata-rata 97% vs 74%.

**⭐ Relevansi ke baseline ADB:** ketiga tool mensyaratkan **USB debugging diaktifkan** pada perangkat (Bagian 3.3) — prasyarat yang sama persis dengan ADB. Papernya lebih dekat ke baseline penelitian ini daripada yang sempat dinilai sebelumnya.

**Perangkat uji:** Oppo F9 (Android 10) dan Samsung S7 Edge (Android 8).

**Catatan mutu:** jurnal kampus regional (UiTM Press), bukan venue top-tier. Posisinya sebagai **bukti empiris pendukung**; beban konseptual C1 ditanggung Fukami.

---

#### Rumusan C1 final

> Ketersediaan digital evidence pada perangkat Android tidak bersifat seragam. Pada tingkat privilege non-root, akuisisi hanya menghasilkan data parsial (Fukami dkk., 2021), aplikasi tertentu dapat tidak menyertakan datanya dalam operasi backup sistem (Fukami dkk., 2021), dan cakupan akuisisi aktual berbeda menurut kombinasi tool, jenis data, dan perangkat (Salimi dkk., 2022).
#### C2a — Evidence berasal dari berbagai source/type

**Status: `VERIFIED`** ✅

**Sumber:** Moreb dkk. (2024), hlm. 129–130. Paper menyebut event dapat ditemukan di lokasi berbeda (SMS, call log, gambar tersimpan, email), dan sebagian event kompleks memerlukan tool berbeda serta pengumpulan informasi untuk merekonstruksinya.

#### C2b — Evidence berbeda perlu dimaknai sesuai konteks/semantics-nya

**Status: `VERIFIED`** ✅ **(full-text dibaca, v0.2-rev)**

Sumber yang sebelumnya dipasang di sini (Xi dkk. 2025 / JoSemA) dipindahkan ke Lapisan D.

**Sumber:** Spichiger, H., & Adelstein, F. (2025). *Preserving meaning of evidence from evolving systems.* Forensic Science International: Digital Investigation, 52, 301867. DFRWS EU 2025. Open access CC BY-NC-ND.
🔗 https://doi.org/10.1016/j.fsidi.2025.301867

**Definisi kunci (Bagian 1):** *Reference Data adalah data yang digunakan sebagai standar untuk mengklasifikasi atau menginterpretasi trace data yang diperoleh dari perangkat digital.*

**Bukti spesifik (Bagian 4.1) — ini C2b secara harfiah:** Signifikansi data tidak dapat begitu saja diturunkan dari data evidentiary itu sendiri. Pada aplikasi yang tidak dikenal, nilai field dan flag perlu dipahami melalui pengujian.

**Contoh mereka yang langsung relevan:** sebuah aplikasi tak dikenal memiliki kolom database bernama "read" berisi flag biner. Itu sendiri **tidak** memberi tahu apakah field tersebut benar-benar menunjukkan status baca pesan, apa yang menyebabkan nilainya berubah, dan state mana berkorespondensi dengan status mana.

Mereka juga menyatakan: tanpa reference data, nilai sebuah trace tidak dapat dinilai, dan upaya menilainya **sama saja dengan menebak** (Bagian 4.1).

**⭐ Bonus untuk Knowledge Base — definisi Preservation yang diperluas (Bagian 4.2):**
> Preservation: melindungi trace dari alterasi, mengumpulkan trace dengan cara yang mengubah sesedikit mungkin, dan aktivitas manajemen evidence. **Ini termasuk pengumpulan informasi suplemen yang relevan tentang trace seperti metadata, reference data, dan konteks.**

→ KB penelitian ini bukan fitur tambahan. Menurut definisi yang diusulkan di DFRWS EU 2025, **reference data adalah bagian dari preservation**. Ini menaikkan bobot akademik KB secara signifikan.

---

### ⚠️⚠️ JEBAKAN TERMINOLOGI — WAJIB DIBACA SEBELUM MENULIS

**Spichiger & Adelstein (2025) Bagian 3.4 berjudul "The illusion of determinism and sources of uncertainty."**

Isinya: pola pikir bahwa komputer bersifat deterministik dan biner sehingga harus dapat menghasilkan jawaban ground-truth ya/tidak yang sederhana **dapat menyesatkan** investigator forensik; mengingat kompleksitas seluruh lapisan dan informasi yang tidak lengkap, jawaban ya/tidak absolut umumnya tidak feasible. Beroperasi di bawah ilusi determinisme mendorong investigator ke dunia hitam-putih dan membuka celah bias kognitif (mereka mengutip Sunde & Dror, 2019).

**Judul penelitian ini memuat kata "deterministic."** Penguji yang membaca sumber ini dapat menyerang: *"Sumber Anda sendiri memperingatkan terhadap determinisme."*

**Resolusi — dua jenis determinisme yang berbeda:**

| | Yang ditolak Spichiger | Yang dimaksud penelitian ini |
|---|---|---|
| Jenis | **Epistemik** — memaksa kesimpulan biner ya/tidak | **Prosedural** — input sama menghasilkan output sama |
| Target | Sikap/mindset investigator | Sifat mekanisme korelasi |
| Konsekuensi | Bias kognitif, hipotesis alternatif dibuang | Reprodusibilitas, auditabilitas |

**Dan lebih jauh: desain penelitian ini justru menjalankan resep Spichiger.**
- Spichiger menolak dunia hitam-putih → three-state (TRUE/FALSE/**UNKNOWN**) menghindarinya
- Spichiger mendorong evaluasi hipotesis yang bersaing untuk mengurangi ketidakpastian (Bagian 3.4) → output sistem adalah *investigation hypothesis*, bukan verdict
- Spichiger menuntut reference data agar makna dapat dinilai → dual traceability rule → referensi

**AKSI WAJIB:** tulis pembedaan ini **secara eksplisit** di BAB I atau BAB III. Jangan biarkan jadi tabrakan istilah yang tidak dijelaskan. Satu paragraf sudah cukup, dan paragraf itu justru memperkuat posisi.

**Catatan untuk Lapisan D:** Bagian 5.2 paper ini mengusulkan basis data publik artefak dan aplikasi yang dapat dikueri — mereka menyebutnya *"VirusTotal + Archive.org untuk Artefak Forensik."* Ini **usulan riset masa depan, bukan sistem yang dibangun**, sehingga bukan kompetitor. Justru sebaliknya: ini kebutuhan yang diidentifikasi di venue forensik teratas, dan KB penelitian ini menjawab sebagian dari kebutuhan itu untuk satu domain spesifik.

---

### C3 — State/artefak tunggal ≠ behavior

Dipecah dua. **Ini pemecahan penting** — keduanya klaim berbeda dengan sumber berbeda.

#### C3a — Informasi statis/deklaratif ≠ perilaku runtime

**Status: ✅ `VERIFIED` `USED` (¶8)** — dinaikkan v1.2. Restrukturisasi v0.3-rev tetap berlaku: sumber forensik jadi tulang, sumber keamanan jadi ilustrasi.

> **⭐ Penguatan v1.2 — kaki "keluaran tingkat perilaku".** Diferensiator nomor 2 (keluaran pada tingkat perilaku, bukan relasi antar-butir bukti) semula hanya ditopang satu kalimat di ujung ¶8. Pada draft final kalimat itu ditarik jadi eksplisit: *"keluaran yang berguna bagi penyidik bukan penilaian atas status sebuah berkas, melainkan pernyataan mengenai perilaku yang didukung bukti pada perangkat tersebut, beserta batas dukungannya."* **Jangan dipangkas** — kalimat itu yang menyambungkan ¶8 ke ¶15–16.

> **Perubahan struktur.** Versi sebelumnya menopang C3a **100% pada literatur keamanan** (Sutter, Ehsan) dan mengandalkan pagar framing sebagai satu-satunya pertahanan. Itu plester, bukan perbaikan — penguji tetap dapat membuka daftar pustaka. Sekarang Spichiger menyediakan jangkar forensik untuk klaim yang sama, sehingga peran sumber dapat ditata ulang.

**Susunan yang dipakai:**

```
TULANG PARAGRAF  → Spichiger & Adelstein (2025) — FORENSIK
                   nilai sebuah field tidak memberi tahu maknanya
                   tanpa reference data

ILUSTRASI ANDROID → Sutter (2024), Ehsan (2022) — KEAMANAN
                    permission = capability terdeklarasi,
                    bukan perilaku runtime yang teramati

PAGAR FRAMING    → tetap dipakai, sebagai lapisan kedua
```

**Jangkar forensik — Spichiger & Adelstein (2025), Bagian 4.1:** contoh kolom database bernama "read" berisi flag biner. Itu sendiri tidak memberi tahu apakah field tersebut benar-benar menunjukkan status baca pesan, apa yang menyebabkan nilainya berubah, dan state mana berkorespondensi dengan status mana.
🔗 https://doi.org/10.1016/j.fsidi.2025.301867

**Ilustrasi Android:**
- Sutter, T. dkk. (2024). *Dynamic Security Analysis on Android: A Systematic Literature Review.* IEEE Access, 12, 57261–57287. Open access CC BY. 🔗 DOI 10.1109/ACCESS.2024.3390612
- Ehsan, A., Catal, C., & Mishra, A. (2022). *Detecting Malware by Analyzing App Permissions on Android Platform: A SLR.* Sensors, 22(20), 7928. Open access. 🔗 DOI 10.3390/s22207928
  **⚠️ Belum dibaca siapa pun.** Baca sebelum masuk draft.

**Catatan soal keabsahan framing:** menerjemahkan literatur keamanan ke pertanyaan forensik adalah langkah ilmiah yang sah, bukan akal-akalan. Literatur security bertanya *"bagaimana malware melakukan X"*; forensik bertanya *"apa yang dapat disimpulkan dari jejak X"*. Menjembatani keduanya adalah kerja intelektual yang riil. Keberatan sebelumnya bukan pada keabsahannya, melainkan pada **proporsi** — dan proporsi itu sudah diperbaiki dengan menempatkan Spichiger sebagai tulang.

**Pagar framing (tetap berlaku):**
- ❌ "malware menyalahgunakan accessibility untuk mencuri OTP"
- ✅ "karena permission menunjukkan kapabilitas terdeklarasi dan bukan perilaku yang teramati, pemeriksaan terhadap state permission saja tidak memadai untuk menyimpulkan terjadinya akses"

**Batasan wording:** jangan tulis "permission tidak berguna" — tidak didukung. Yang didukung: permission menunjukkan capability/konfigurasi, bukan verdict perilaku.

---

#### C3b — State yang teramati ≠ peristiwa yang pernah terjadi

**Status: `VERIFIED`** ✅ **← claim load-bearing utama**

**Sumber:** Breitinger, F., Studiawan, H., & Hargreaves, C. (2025). *SoK: Timeline based event reconstruction for digital forensics.* FSI:DI 53, 301932. DFRWS USA 2025.
🔗 https://arxiv.org/html/2504.18131v1

**Bukti (Bagian 4.3, Q4):** paper membedakan secara formal antara **event E** yang benar-benar terjadi di realitas dengan **inferred event E′** yang diturunkan dari analisis timeline entries. E′ didefinisikan sebagai skenario rekonstruksi yang *mungkin* terjadi dalam rentang waktu tertentu, dan definisi ini secara eksplisit mengakui ketidakpastian dalam merekonstruksi peristiwa masa lalu.

**Kenapa ini menangkap masalah yang sebenarnya:** baseline non-root ADB membaca **residual state** — bukan static analysis (kode APK) dan bukan dynamic analysis (observasi runtime). C3a tidak menangkap ini; C3b menangkapnya.

#### Jangkar Android untuk C3b — Kaart & Laraghy DICORET

> **Keputusan v0.3-rev.** Kaart & Laraghy (2014), *Android forensics: Interpretation of timestamps*, Digital Investigation 11, 234–248 — **dicoret**. Alasan: (i) terbit 2014, di luar batas 5 tahun; (ii) tidak tersedia gratis; (iii) C3b sudah VERIFIED tanpanya.

**Pengganti — Shang, D., Sakzad, A., & Hall, S. W. (2025).** *Thumb: A forensic automation framework leveraging MLLMs and OCR on Android device.* FSI:DI, September 2025.
🔗 https://www.sciencedirect.com/science/article/pii/S2666281725000885

**Kalimat pembuka abstraknya adalah C3b versi Android:** forensik perangkat Android sulit karena thumbnail dihasilkan secara otomatis oleh aplikasi dan sistem operasi, sehingga **menyulitkan atribusi ke aksi pengguna tertentu**.

→ Artefak ada, tetapi atribusinya ke perbuatan tidak langsung. Android, forensik, 2025. Status ✅ `VERIFIED` ●●● — full-text sudah dibaca (v1.0). ⚠️ Metadata benar: FSI:DI **54, 301949**.

**⭐ Opsi ketiga, dan mungkin yang terkuat:** jangkar Android untuk C3b **tidak harus datang dari literatur**. Tier-2 empirical feasibility testing sudah ada di rencana penelitian. Jika dapat ditunjukkan sendiri lewat percobaan bahwa `dumpsys` memberikan state saat ini tanpa riwayat kapan permission diberikan, itu menjadi **bukti primer penelitian ini sendiri**.

Sesuai kerangka tiga jenis premis (§9): premis penalaran tidak wajib bersitasi. C3b-Android dapat menjadi **temuan**, bukan **pinjaman** — dan untuk skripsi pengembangan, itu lebih bernilai.
### C4 — Keragaman konfigurasi teknis di dalam satu keluarga insiden

> ### ⚠️⚠️ PENURUNAN KLAIM — v1.2
>
> **Judul lama:** *"Satu perilaku dapat ditempuh melalui beberapa mekanisme."*
>
> **Masalah:** variasi deklarasi izin antar-sampel **bukan bukti langsung** bahwa satu perilaku memiliki beberapa jalur teknis. Itu inferensi yang melampaui data. Claim map ChatGPT secara independen menandai klaim ini `OPTIONAL / HOLD` dengan catatan "belum cukup direct evidence" — dan penilaian itu benar.
>
> **Klaim yang berlaku sekarang:** *terdapat keragaman konfigurasi teknis di dalam satu keluarga insiden yang sama, sebagaimana terlihat pada variasi deklarasi izin antar-sampel.* Konsekuensi praktisnya tetap sama — pemeriksaan yang hanya menyasar satu jenis artefak tidak menjamin tercakupnya keragaman konfigurasi yang mungkin ditemui pada kasus lain.
>
> **Beban:** turun dari load-bearing jadi **supporting**.
> ⛔ **Dilarang** menulis "satu perilaku, banyak jalur" di naskah mana pun.

> `[ARSIP]` — Susunan tiga lapis di bawah ini disusun pada v0.4 untuk menopang klaim versi lama. Isinya tetap sahih sebagai bukti keragaman konfigurasi, tetapi **tidak lagi** menopang klaim multi-jalur.

#### [ARSIP] Susunan asli C4

**Claim kerja:** Perilaku serupa pada Android dapat ditempuh melalui lebih dari satu mekanisme teknis, sehingga observasi terhadap satu jenis artefak tidak menjamin terdeteksinya perilaku yang sama bila ditempuh melalui mekanisme lain.

**Status: `VERIFIED`** ✅ **(v0.5 — sumber keamanan diganti sumber forensik)**

> **⚠️ RUMUSAN KLAIM TIDAK BERUBAH.** Yang berubah hanya sumbernya. Posisi C4 di alur argumen tetap sama: Blok II bersama C2a/C2b, menopang RQ1. Peta paragraf tidak bergeser.

| | Sebelum (v0.4) | Sesudah (v0.5) |
|---|---|---|
| Sumber | Bitsight, Cleafy, Cyble | Hook Tabel 2, Umam, Anubis |
| Domain | keamanan (laporan vendor) | **forensik (jurnal peer-reviewed)** |
| Pagar framing | wajib terus-menerus | tidak diperlukan |
| Jenis bukti | daftar kapabilitas | **variasi terukur pada 64 sampel** |

---

#### ⚠️ RISIKO: penyempitan ke kasus spesifik

Laporan vendor memberi klaim **umum** ("kapabilitas dapat mencakup…"). Umam dan Anubis memberi **kasus tunggal**. Menulis *"Undangan.apk memakai RECEIVE_SMS sementara Anubis memakai Accessibility"* menyempitkan klaim universal menjadi perbandingan dua sampel — dan penguji berhak bertanya *"dua contoh membuktikan apa?"*

**Mitigasi: susunan tiga lapis. Hook menanggung generalitas, dua kasus jadi ilustrasi.**

```
LAPIS 1 — UMUM & TERUKUR
  Hook Tabel 2: 64 sampel satu keluarga,
  deklarasi permission bervariasi (64/58/32/6/3/1)
  → variasi mekanisme adalah POLA, bukan anekdot
        ↓
LAPIS 2 — ILUSTRASI KONKRET
  Umam:   RECEIVE_SMS + BroadcastReceiver → Telegram Bot API
  Anubis: Accessibility dipaksa aktif → SQLite app_webview → C2
  → tujuan sama (memperoleh OTP), jejak artefak berbeda
        ↓
LAPIS 3 — KONSEKUENSI FORENSIK
  pemeriksaan satu jenis artefak tidak menjamin cakupan
  terhadap perilaku yang sama
```

**⚠️ ATURAN MENULIS:** jangan buka paragraf dengan nama sampel. Mulai dari **polanya** (Hook Tabel 2), baru sebut contoh. Paragraf yang dibuka dengan "Undangan.apk…" sudah terlanjur sempit sebelum kalimat kedua.

**Sumber lama (Bitsight/Cleafy/Cyble):** boleh disimpan sebagai cadangan, tapi **tidak diperlukan lagi**. Menghapusnya menghilangkan satu titik risiko framing drift.

**Sumber pendukung tambahan:** systematic review *Mobile forensics for Android devices* (DiVA, 30 studi 2015–2025) — tidak ada satu tool pun yang memberi cakupan lengkap di seluruh skenario.

**Beban: SUPPORTING** — tetapi kini sanggup naik bila diperlukan.
### C5 — Correlation/reconstruction relevan dalam analisis forensik

**Status: `VERIFIED`** ✅

**Sumber utama:** Breitinger dkk. (2025) — sama seperti C3b.

**Bukti spesifik (full-text dibaca):**
- Bagian 4.1: inti event reconstruction adalah *temporal sequencing and correlation*
- Bagian 6.4.1: correlation antar timeline entry disebut **sulit**, terutama bila data berasal dari source/format berbeda; membutuhkan pengalaman dan ketelitian
- Bagian 6.3.1: tantangan heterogenitas source, normalisasi, kombinasi source

**Sumber pendukung:** Moreb dkk. (2024) — Evidence Correlation sebagai sub-tahap resmi Information Analysis.

**⚠️ Batasan penting:** Breitinger memposisikan correlation sebagai **tantangan terbuka**, bukan masalah yang sudah selesai. Ini menguntungkan (mendukung gap), tapi jangan diklaim sebagai "correlation sudah terbukti efektif".

---

## 4. LAPISAN S — PENDUKUNG DESAIN

**Catatan v0.2:** S2 dan S3 sudah **dipromosikan** menjadi B6 dan B5, karena keduanya menopang properti yang ada di judul penelitian dan karenanya harus jadi claim resmi, bukan lampiran. Tersisa satu di lapisan ini.

### S1 — Justifikasi three-state / UNKNOWN

**Claim kerja:** Ketiadaan data pada pemeriksaan forensik bersifat ambigu — dapat disebabkan konfigurasi, tampering, atau berlalunya waktu — sehingga tidak dapat langsung dimaknai sebagai bukti bahwa suatu peristiwa tidak terjadi.

**Status: `VERIFIED`** ✅

**Sumber:** Breitinger dkk. (2025), **Research Gap 3** (Bagian 9.2).
🔗 https://arxiv.org/html/2504.18131v1

**Bukti spesifik:** Masih sedikit penelitian tentang persistensi artefak, dan tentang bagaimana menentukan apakah ketiadaan data disebabkan oleh konfigurasi, tampering, atau sekadar berlalunya waktu. Paper menyatakan penelitian di area ini dapat mengurangi ketidakpastian dalam model dan proses.

**Bukti pendukung dari paper yang sama, Bagian 9:** disebutkan sebagai *general research gap* bahwa ketidakpastian berpotensi masuk ke seluruh tahapan model (Research Gap 1), dan penanganannya di tiap tahap masih dibutuhkan.

→ Prinsip `unavailable ≠ FALSE` bukan sekadar pilihan desain, tapi menjawab celah yang diakui komunitas forensik.

**Beban: LOAD-BEARING** (menopang seluruh desain three-state).

---

## 5. LAPISAN D — STATE OF THE ART

### D1 — Penelitian terkini sudah punya berbagai pendekatan

**Status: ✅ `VERIFIED` `USED` (¶14)** — dinaikkan v1.2; perbandingan sistematis selesai (Tabel 1 N=7, Tabel 2 N=4).

| ID | Sistem/Paper | Ruang | Status |
|---|---|---|---|
| P1 | Moreb dkk. (2024) — MFIPF | Framework proses mobile forensik | ✅ `VERIFIED` |
| P2 | Xi dkk. (2025) — **JoSemA**. FSI:DI 52, 301846 | Analisis semantik isi komunikasi mobile | ✅ `VERIFIED` ●●● — bukan kompetitor |
| P3 | Hargreaves, van Beek & Casey (2025) — **SOLVE-IT**. FSI:DI 52, 301864 | KB forensik terinspirasi MITRE ATT&CK | ●●○ — Tabel 2 |
| P4 | Boztas dkk. (2025) — **Argus/Aardwolf**. FSI:DI 53, 301938 | Identifikasi lokasi artefak via analisis dinamis | ●●○ — Tabel 2 |
| P5 | Hakim & Saputri (2025) — DEO Model. JUTIF 6(4) | Evidence reduction Android | ✅ `VERIFIED` ●●● — **Tabel 1** |
| P6 | Bernardo dkk. (2024) — Toolbox. Emerging Science Journal | Framework/tool governance | ✅ `VERIFIED` ●●● — Tabel 2 |
| P7 | Breitinger dkk. (2025) — SoK TER | Fondasi rekonstruksi | ✅ `VERIFIED` |
| P8 | Shang, Sakzad & Hall (2025) — **Thumb**. FSI:DI, Sep 2025 | Otomasi forensik Android (atribusi thumbnail→aksi) | ✅ `VERIFIED` ●●● — Tabel 2 |
| P9 | Igonor, Amin & Garg (2026) — **BlockFECS**. Forensic Sciences 6(3), 59 | Korelasi evidence berbasis metadata + blockchain | ✅ **`VERIFIED`** |
| P10 | Dimitriadis, Ivezic, Kulvatunyou & Mavridis (2020) — **D4I**. Array 5, 100015 | Kerangka korelasi artefak → fase Cyber Kill Chain | ✅ **`VERIFIED`** |

---

### ⭐ P9 — BlockFECS (Igonor, Amin & Garg, 2026) — PEMBANDING TERPENTING

**Metadata:** Forensic Sciences, 6(3), 59. MDPI, open access CC BY. DOI 10.3390/forensicsci6030059. Diterima 11 Mei 2026, terbit 6 Juli 2026. Penulis: University of Tasmania & RMIT.
🔗 https://doi.org/10.3390/forensicsci6030059
🔗 Dataset: https://github.com/igsamoshoke/BLOCKFECS-POC-DATASET

#### Yang menabrak klaim novelty

Paper ini secara eksplisit menyebut pendekatannya *"transparent rule-based correlation algorithm"* dengan tiga sifat: (i) tiap field metadata dibandingkan secara **deterministik**, (ii) menghasilkan skor kemiripan berbobot, (iii) label kategoris dapat dipersistensi kembali ke blockchain untuk **auditabilitas**. Mereka juga menyebutnya *machine-executable and reproducible*.

**Konsekuensi:** kombinasi **deterministic + rule-based + provenance + auditability + explainability BUKAN novelty.** Jangan pernah dipakai sendirian sebagai klaim kebaruan.

#### ⭐ Yang justru MENGUATKAN gap (temuan terpenting)

**Tabel 5 paper, hlm. 15 — hasil pada 4.186 pasangan evidence:**

| Kategori | Correct | Incorrect | Missed | Precision | Recall | F1 |
|---|---|---|---|---|---|---|
| Related | 3 | 0 | 0 | 1.00 | 1.00 | 1.00 |
| **Supplementary** | 196 | 21 | **952** | 0.90 | **0.17** | **0.29** |
| Duplicate | 55 | 0 | 0 | 1.00 | 1.00 | 1.00 |
| Unrelated | 2959 | 952 | 21 | 0.76 | 0.99 | 0.86 |

**952 hubungan terlewat. Recall 0.17.**

Penyebab yang mereka sebut sendiri (hlm. 15–16): skema pembobotan berbasis aturan mereka andal untuk hubungan yang jelas, **tetapi kurang efektif ketika evidence mengandung metadata parsial, bernoise, atau hilang**. Mereka juga menyatakan metadata yang hilang atau bernoise menurunkan recall, khususnya untuk kategori Supplementary (Bagian 4.3).

**KENAPA INI PENTING:** BlockFECS adalah korelasi deterministik **tanpa semantik missing-evidence eksplisit**. Ketika data tidak lengkap, skornya turun diam-diam dan hubungannya hilang — tidak ada mekanisme yang menyatakan "ini tidak diketahui" versus "ini tidak ada".

Dan baseline non-root ADB pada perangkat sitaan **menjamin data tidak lengkap**.

→ Ini **bukti empiris kuantitatif** bahwa pendekatan deterministik tanpa three-state gagal persis pada kondisi yang menjadi baseline penelitian ini. Digabung dengan Research Gap 3 Breitinger (S1), argumen UNKNOWN sekarang punya dua kaki: satu teoretis, satu empiris.

#### Pembeda struktural

| Aspek | BlockFECS | Penelitian ini |
|---|---|---|
| Objek korelasi | Evidence A ↔ Evidence B | Facts → behavior finding → hypothesis |
| Yang dibandingkan | Metadata kontainer (timestamp, geolokasi, device ID, user ID, hash) | Semantik artefak sistem (state permission, package, aktivitas jaringan) |
| Output | Label: Related/Supplementary/Duplicate/Unrelated | Temuan perilaku + hipotesis investigasi |
| Missing data | Skor turun, hubungan hilang | UNKNOWN eksplisit, `insufficient_evidence` |
| Domain | IoT/smart city, kecelakaan kendaraan | Android, APK penipuan |

BlockFECS menjawab *"dua bukti ini berhubungan atau tidak?"* — penelitian ini menjawab *"kombinasi fakta ini mendukung perilaku apa?"* Beda level abstraksi.

#### Dua kelemahan metodologis yang dapat dicatat

1. **Ground truth sebagian dari LLM.** Mereka memakai ChatGPT-4.1 untuk membantu melabeli hubungan antar-pasangan evidence (Bagian 3.1.2). Mereka jujur menyebutnya sebagai mekanisme pengecekan konsistensi tambahan, bukan pengganti validasi forensik. Tetap: sistem yang mengklaim reprodusibilitas divalidasi sebagian oleh alat non-deterministik.
2. **Bobot diakui tidak universal.** Mereka menyatakan bobot yang dipakai adalah nilai spesifik skenario untuk konteks kecelakaan smart city, bukan bobot forensik universal, dan konteks investigasi lain mungkin memerlukan distribusi bobot berbeda (Bagian 2.3.1).

→ Poin 2 **menguntungkan:** jika bobot harus disesuaikan per domain, maka spesialisasi domain (APK fraud) bukan keterbatasan melainkan **keharusan metodologis**.

**Catatan proses:** paper ini sempat tidak ditemukan dalam dua kali pencarian dan sempat ditandai "keberadaan belum terkonfirmasi". PDF disediakan peneliti dan verifikasi penuh dilakukan. Pelajaran: ketidakhadiran dalam hasil pencarian bukan bukti ketiadaan.

**Link akses gratis:**
- P1 Moreb: PDF sudah dimiliki (IJCDS160110)
- P2 JoSemA: https://www.sciencedirect.com/science/article/pii/S2666281724001884
- P7 Breitinger: https://arxiv.org/html/2504.18131v1
- Casey artifact catalog: https://pmc.ncbi.nlm.nih.gov/articles/PMC9543441

**⚠️ Dua yang paling perlu diperhatikan:**

**P3 SOLVE-IT** — knowledge base forensik yang secara eksplisit terinspirasi MITRE ATT&CK. Ini tetangga sangat dekat dengan desain KB penelitian ini.
- **Pembeda:** SOLVE-IT mengindeks *teknik investigasi* beserta weakness/mitigation-nya. Penelitian ini mengindeks *perilaku pelaku* pada perangkat. Objek berbeda.
- **Nilai positif:** memvalidasi bahwa adopsi struktur ala MITRE ATT&CK ke forensik adalah arah yang sah dan peer-reviewed.
- Dikutip juga oleh Breitinger dkk. (2025) sebagai tempat menampung knowledge base of weaknesses.

**P2 JoSemA** — memposisikan diri sebagai solusi standalone yang **melengkapi, bukan menggantikan** tools forensik yang ada (Magnet Axiom, XAMN, Cellebrite PATHFINDER, Oxygen, Belkasoft), dan membandingkan diri dengan Moreb (2024) pada aspek data preparation, information analysis, case construction, case closure.
- **Pembeda:** JoSemA menganalisis isi komunikasi manusia (teks/voice/gambar/video lintas messenger) dengan NLP/topic modeling untuk kasus kejahatan terorganisir. Penelitian ini menganalisis artefak sistem dengan rule deterministik untuk perilaku aplikasi.
- **Yang perlu dicontek:** kalimat positioning "melengkapi, bukan menggantikan". Itu postur yang tepat untuk BAB I.

### D2 — Comparative matrix

**Status: `SELESAI v0.1`** — matriks dibangun, tetapi lima dari sembilan kolom masih perlu verifikasi full-text.

#### Tingkat kepercayaan per sumber

Setiap sel di matriks hanya sekuat verifikasi sumbernya. Tanda berikut wajib dibaca bersama matriks:

| Kode | Sumber | Verifikasi |
|---|---|---|
| ●●● | Moreb (2024), Breitinger (2025), Igonor/BlockFECS (2026), Spichiger (2025) | Full-text dibaca sendiri |
| ●●○ | Xi/JoSemA (2025), SOLVE-IT (2025), Argus (2025) | Abstrak + cuplikan publisher |
| ●○○ | *(kosong — tidak ada lagi sumber pada tingkat ini per v1.0)* | — |

**Sumber ●●● bertambah v0.4:** Fukami (2021), Salimi (2022).
**Sumber ●●● bertambah v1.0:** Ehsan (2022), Hakim & Saputri (2025), Bernardo (2024), Shang/Thumb (2025), Sudjayanti & Hamdani (2024), Muthohirin (2024). **Seluruh baris Tabel 1 kini ●●●.**

**Aturan pakai:** hanya baris ●●● yang boleh dinyatakan sebagai fakta di BAB II. Baris ●●○ ditulis dengan hedging ("berdasarkan deskripsi yang dipublikasikan"). Baris ●○○ **tidak boleh masuk BAB II** sebelum dibaca.

#### Matriks

Notasi: **✓** = kemampuan eksplisit; **~** = disinggung/parsial; **—** = tidak ditemukan sebagai fokus pada bagian yang diperiksa; **✗** = eksplisit di luar scope.

`—` **bukan** klaim bahwa fitur itu mustahil ada. Artinya: bukan fokus atau kemampuan eksplisit yang dapat diverifikasi dari bagian paper yang diperiksa.

| Aspek | Moreb 2024 ●●● | Breitinger 2025 ●●● | BlockFECS 2026 ●●● | Spichiger 2025 ●●● | JoSemA 2025 ●●○ | SOLVE-IT 2025 ●●○ | Argus 2025 ●●○ | Hakim 2025 ●○○ | Bernardo 2024 ●○○ | Thumb 2025 ●○○ | **Penelitian ini** |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **Domain** | Mobile | DF umum | IoT/smart city | DF umum | Mobile | DF umum | Mobile | Android | Mobile | Android | **Android** |
| **Incident-specific** | ✗ | ✗ | ✗ | ✗ | ~ kejahatan terorganisir | ✗ | ✗ | ~ skenario | ✗ | ~ thumbnail | **✓ APK fraud** |
| **Post-acquisition** | ✓ | ✓ | ✓ | ~ preservation | ✓ | ~ | ✓ | ✓ | ~ | ✓ | **✓** |
| **Multi-source heterogen** | ✓ | ✓ | ✓ | ✓ | ✓ | — | ~ | ✓ | ✓ | — | **✓** |
| **Normalisasi eksplisit** | ~ konseptual | ~ tantangan | ✓ metadata terstruktur | — | ✓ semantic unification | — | ✓ katalog artefak | ~ 5W | ~ governance | — | **✓** |
| **Mekanisme korelasi** | ~ sub-tahap | ✓ rekonstruksi | ✓ metadata-weighted | — | ✓ semantik | — | — | — | — | ~ atribusi | **✓ rule-based** |
| **Rule-based** | ~ disebut | ~ dibahas | **✓ diimplementasi** | — | ✗ NLP/ML | — | — | ~ filter | — | ✗ MLLM | **✓** |
| **Deterministic** | — | — | **✓** | ⚠️ menolak epistemik | ✗ | — | ✓ | ~ | — | ✗ | **✓ prosedural** |
| **Provenance/integritas** | ✓ hash | ~ concern | **✓ blockchain** | ✓ preservation | — | ~ | ✓ | ~ | ✓ | — | **✓ SHA-256** |
| **Reference traceability** (rule → literatur) | — | ~ Gap 7 | ~ bobot transparan | **✓ inti argumen** | ~ knowledge-guided | ✓ weakness/mitigation | ✓ Aardwolf | — | — | — | **✓** |
| **Missing-evidence state eksplisit** | — | ~ Gap 3 (diakui *gap*) | ✗ **recall 0.17** | ~ uncertainty | — | — | — | — | — | — | **✓ 3-state** |
| **Output behavior-level** | — | ~ inferred event E′ | ✗ relasi evidence | — | ~ course of events | — | ✗ lokasi artefak | ✗ objek relevan | ✗ panduan tool | ~ atribusi aksi | **✓ finding + hipotesis** |
| **Evaluasi empiris** | ~ contoh | SoK | ✓ PoC | posisi | ✓ | ~ | ✓ | ✓ | ✓ | ✓ | rencana BAB IV |

### ⭐ P10 — D4I (Dimitriadis dkk., 2020) — PEMBANDING METODOLOGIS

**Metadata:** *D4I – Digital forensics framework for reviewing and investigating cyber attacks.* Array, 5, 100015. University of Macedonia (Yunani) + NIST (USA). CC BY-NC-ND. DOI 10.1016/j.array.2019.100015.
🔗 https://doi.org/10.1016/j.array.2019.100015

**Kenapa wajib masuk:** kerangka ini dipakai oleh Umam dkk. (2025) pada Undangan.apk — **incident family penelitian ini persis**. Mengabaikannya berarti meninggalkan celah yang mudah ditemukan penguji.

#### Tiga temuan yang menentukan

**1. Domainnya Windows — dinyatakan sendiri.** Paper mengelaborasi artefak Windows karena Windows adalah OS yang paling banyak digunakan saat ini, **"except Android in Mobile devices"**. Taksonomi artefaknya diambil dari poster SANS *Windows Forensic Analysis* (8 kategori: File download, Program Execution, File/Folder Opening, Deleted File, Network Activity, External Device/USB usage, Account Usage, Browser Usage). Contoh aplikasinya spear phishing pada Windows.

→ Perluasan ke OS lain disebut mungkin (contoh Linux `/etc/init.d`), tetapi **tidak dilakukan untuk Android**.

**2. Korelasinya kemiripan atribut, bukan penalaran perilaku.** Langkah 3 (Correlate): mencari korelasi antar-artefak dari fase CKC yang sama, sebelumnya, atau berikutnya; artefak **dikorelasikan berdasarkan atributnya (misalnya timestamp, nama) atau isinya**.

→ Objek yang sama dengan BlockFECS: **evidence ↔ evidence**. Bukan facts → behavior finding. Enam langkahnya (Choose → Identify → Correlate → Construct CoA → Repeat → Analyze CoA) adalah **prosedur manual**, bukan sistem.

**3. ⭐⭐ Notasi CoA — kaki ketiga untuk S1**

Keluaran mereka berbentuk:

```
CoA: [–], [–], [–], [–], [Run Registry key, ADS], [–], [–]
      R    W    D    E    I                        C2   A
```

Tanda `[–]` menandai fase di mana tidak ada artefak ditemukan. **Ada notasi untuk ketiadaan, tetapi tidak ada semantik untuk ketiadaan itu.** Tanda hubung tidak membedakan:
- tidak teramati karena batas akuisisi,
- tidak teramati karena artefak sudah kedaluwarsa/terhapus,
- memang tidak terjadi.

→ **Ini menjelaskan Umam.** Baris Reconnaissance di Tabel 6 dan 7 Umam diisi tanda hubung tanpa penjelasan — itu **diwarisi dari D4I**. Kelemahannya struktural, ada di kerangkanya, bukan pada penerapannya.

**Konsekuensi untuk S1:** argumen three-state kini punya **tiga kaki**:

| Kaki | Sumber | Jenis |
|---|---|---|
| Teoretis | Breitinger (2025) Research Gap 3 | celah diakui komunitas |
| Empiris | BlockFECS (2026) recall 0.17, 952 terlewat | konsekuensi terukur |
| **Struktural** | **D4I (2020) notasi `[–]`** | **kerangka mapan tidak menyediakannya** |

---

### ⭐ P2 — JoSemA (Xi dkk., 2025) — DIVERIFIKASI, BUKAN KOMPETITOR

**Metadata:** *Towards a joint semantic analysis in mobile forensics environments.* FSI:DI 52, 301846. Hochschule Mittweida + Hochschule Darmstadt + Fraunhofer FKIE (Jerman). CC BY. Proyek EU Horizon 2020 **FORMOBILE** (grant 832800).

**Objek: isi komunikasi manusia.** Pesan singkat, percakapan, kontak, kanal messenger. Bukan artefak sistem.

**Pipeline (Gambar 4):** Data Preparation (dump extraction, data decomposition) → Data Preprocess (channel decomposition, conversation detection, semantic annotation) → Hypothese-driven Data Analytics (network analytics, **topic modeling**, concept networks, channel linking) → Visual Analytics (correlation detection, relevance visualization) → Report.

**Metode: NLP dan topic modeling — probabilistik**, bukan deterministik.

**Output:** identifikasi bagian komunikasi yang relevan dengan kasus + rekonstruksi rangkaian peristiwa dalam riwayat komunikasi.

**✅ VERDICT: bukan kompetitor.** Objek berbeda (percakapan manusia vs artefak sistem), metode berbeda (probabilistik vs deterministik), output berbeda (konteks komunikasi vs temuan perilaku aplikasi).

**Bonus:** mendukung C2b — makna satu modalitas tidak lengkap tanpa konteks modalitas lain.

**Yang layak dicontek:** postur *"melengkapi, bukan menggantikan"* tools forensik komersial.

---

#### Tiga kolom yang menentukan

Baca matriks secara vertikal pada tiga baris ini:

**1. Missing-evidence state eksplisit** — hanya satu sel yang mendekati (`~` Breitinger), dan itu pun **disebut sebagai research gap, bukan sebagai kemampuan**. BlockFECS justru menunjukkan konsekuensi ketiadaannya secara kuantitatif: recall 0.17 pada kategori Supplementary, 952 hubungan terlewat karena metadata parsial/bernoise.

**2. Output behavior-level** — semua pembanding berhenti sebelum lapisan perilaku. BlockFECS berhenti di relasi antar-evidence, Argus di lokasi artefak, Hakim di objek relevan, Bernardo di panduan tool. Yang paling dekat adalah *inferred event E′* Breitinger, tetapi itu kerangka konseptual, bukan sistem.

**3. Incident-specific** — kosong di seluruh baris. Tidak ada pembanding yang dirancang untuk satu incident family tertentu.

**Kombinasi ketiganya tidak ditemukan pada satu pun pembanding.**

#### Yang justru padat terisi — jangan diklaim sebagai kebaruan

Baris **multi-source**, **provenance**, **rule-based**, dan **deterministic** hampir semuanya terisi. Ini bukti bahwa keempatnya sudah menjadi praktik mapan. Setiap klaim kebaruan yang bertumpu pada salah satu — atau bahkan kombinasi keempatnya, karena BlockFECS memiliki semuanya sekaligus — **akan gugur**.

#### ⭐ PARAGRAF SCOPING D2 — WAJIB DITULIS SEBELUM E1

Rumusan gap memakai frasa *"belum ditemukan pada literatur yang ditinjau"*. Frasa itu **hanya sah bila cakupan tinjauan dinyatakan**. Tanpa paragraf ini, penguji berhak bertanya "ditinjau seberapa luas?" dan lu tidak punya jawaban.

**Draft untuk BAB II (sesuaikan angka bila daftar berubah):**

> Tinjauan terhadap pendekatan terdahulu dilakukan secara terbatas dan terarah, bukan sebagai tinjauan sistematis. Cakupan tinjauan ditetapkan sebagai berikut. **Rentang waktu** 2020–2026, dengan pengecualian pada rujukan metodologis yang masih menjadi dasar pendekatan mutakhir. **Sumber** meliputi Forensic Science International: Digital Investigation dan prosiding DFRWS sebagai venue utama forensik digital, ditambah jurnal nasional terindeks untuk konteks insiden lokal. **Kriteria pemilihan**: (i) beroperasi pada tahap pasca-akuisisi, (ii) melibatkan korelasi, rekonstruksi, atau penstrukturan hubungan antar-bukti, dan (iii) menghasilkan keluaran analitis, bukan semata prosedur akuisisi atau panduan pemilihan perangkat lunak. Berdasarkan kriteria tersebut, [N] pendekatan diperbandingkan. Pendekatan yang berfokus pada reduksi volume bukti, tata kelola perangkat lunak forensik, atau atribusi artefak tunggal tidak diikutsertakan karena berada di luar kriteria (ii) dan (iii).

**Fungsi kalimat terakhir:** itu yang membenarkan pengecualian Hakim & Saputri (reduksi bukti), Bernardo (tata kelola tool), dan Thumb (atribusi thumbnail) **tanpa perlu membacanya**. Pengecualian berdasarkan kriteria adalah praktik ilmiah yang sah; pengecualian tanpa alasan tidak.

**✅ [N] = 7** (v1.0 — naik dari 6; Hakim & Saputri dipindah dari Tabel 2).

**Kalimat tambahan untuk menjelaskan Tabel 2:**

> Selain keenam pendekatan tersebut, ditinjau pula empat pendekatan berdekatan yang tidak memenuhi kriteria (ii) namun membantu memetakan lanskap penelitian: tata kelola perangkat lunak forensik, atribusi artefak tunggal, basis pengetahuan teknik investigasi, dan identifikasi lokasi artefak. Pendekatan-pendekatan ini disajikan secara deskriptif.

---

#### Pekerjaan tersisa D2

**✅ KEPUTUSAN DIAMBIL (v0.7): dua tabel.**

### TABEL 1 — Pembanding metodologis (N = 7)

Seluruhnya `VERIFIED` full-text. 13 aspek penuh. **Inilah yang menopang E1.**

| # | Pendekatan | Ruang |
|---|---|---|
| 1 | Moreb dkk. (2024) — MFIPF | Framework proses mobile; Evidence Correlation sebagai sub-tahap |
| 2 | Dimitriadis dkk. (2020) — D4I | Korelasi artefak → fase Cyber Kill Chain |
| 3 | Umam dkk. (2025) | D4I diterapkan pada Undangan.apk — **domain identik** |
| 4 | Xi dkk. (2025) — JoSemA | Analisis semantik komunikasi mobile |
| 5 | Igonor dkk. (2026) — BlockFECS | Korelasi deterministik berbasis metadata |
| 6 | Breitinger dkk. (2025) — SoK TER | Fondasi rekonstruksi peristiwa |
| **7** | **Hakim & Saputri (2025) — DEO Model** | **Reduksi & penstrukturan evidence Android pasca-akuisisi** |

**⭐ Penambahan v1.0 — kenapa Hakim & Saputri naik ke Tabel 1:** penulis berafiliasi **Politeknik Siber dan Sandi Negara** dan **Badan Siber dan Sandi Negara**. Untuk skripsi STIN, pembanding dari perguruan tinggi kedinasan bidang siber tidak layak hanya disebut sepintas — penguji kemungkinan besar mengenal venue dan institusinya. Secara kriteria, DEO memang *reduksi* bukan *korelasi relasi*, tetapi ia melakukan **penstrukturan evidence** dengan parameter terdefinisi (5W) pada domain dan tahap yang sama.

*Baris 2 dan 3 bertaut (Umam menerapkan D4I) tetapi tetap dipisah: D4I menunjukkan kerangkanya (Windows, spear phishing), Umam menunjukkan penerapannya pada incident family penelitian ini.*

### TABEL 2 — Pendekatan berdekatan (N = 4)

Deskriptif, 3 kolom (fokus, domain, keluaran). **Cukup dari judul dan abstrak — tidak membuat klaim tentang isi paper.**

| # | Pendekatan | Fokus | Gugur kriteria |
|---|---|---|---|
| 1 | Bernardo dkk. (2024) | Toolbox & tata kelola proses | (ii) bukan korelasi |
| 2 | Shang dkk. (2025) — Thumb | Atribusi thumbnail → aksi | (ii) artefak tunggal · ⭐ tetap dikutip untuk C3b |
| 3 | Hargreaves dkk. (2025) — SOLVE-IT | KB teknik investigasi | (ii) mengindeks teknik, bukan bukti |
| 4 | Boztas dkk. (2025) — Argus | Identifikasi lokasi artefak | (ii) lokasi ≠ korelasi |

### Yang TIDAK masuk tabel manapun

**Spichiger & Adelstein (2025)** — position paper tentang reference data. Tidak mengorelasikan apa pun, sehingga sebagian besar sel akan `—` tanpa makna. Perannya **fondasi konseptual** (menopang C2b dan B6), dikutip di prosa.

### Prinsip pembagian

> Klaim *"pendekatan ini tidak memiliki penanganan missing-evidence"* menuntut full-text.
> Klaim *"pendekatan ini berfokus pada tata kelola tool"* cukup dari abstrak.
> Dua tingkat klaim, dua tingkat bukti.

---

#### Catatan arsip — pertimbangan sebelum keputusan

| Paper | Fokus | Lolos kriteria (ii)+(iii)? | Rekomendasi |
|---|---|---|---|
| Hakim & Saputri (2025) | Reduksi volume bukti | ❌ reduksi ≠ korelasi | **CORET** |
| Bernardo (2024) | Toolbox & tata kelola | ❌ panduan tool | **CORET** |
| Thumb (2025) | Atribusi thumbnail→aksi | ❌ artefak tunggal, sempit | **CORET** |

**Rekomendasi: coret ketiganya.** Alasannya bukan karena tidak penting, melainkan karena **tidak lolos kriteria cakupan** yang sudah dinyatakan di paragraf scoping. Ini keputusan metodologis, bukan penghindaran.

**Hasilnya: 7 pembanding, seluruhnya `VERIFIED` full-text** — Moreb, Breitinger, BlockFECS, Spichiger, JoSemA, D4I, dan Umam. Matriks tanpa satu pun baris ●○○.

**Tujuh pembanding terverifikasi jauh lebih kuat dipertahankan daripada sepuluh dengan tiga yang belum dibaca.**

**Bila memilih mempertahankan:** ketiganya wajib dibaca full-text sebelum masuk BAB II, dan paragraf scoping harus diperlebar kriterianya.

**Sisa pekerjaan lain:** naikkan SOLVE-IT dan Argus dari ●●○ ke ●●● bila memungkinkan. Keduanya risiko sedang — SOLVE-IT mengancam klaim KB (bukan klaim korelasi), Argus berhenti di lokasi artefak.

## 6. LAPISAN E — GAP & POSISI

### E1 — Research gap

**Status: ✅ `BOUNDED` `USED` (¶16)** — tiga baris ●○○ sudah diverifikasi seluruhnya (v1.0).

> **Kenapa `BOUNDED`, bukan `VERIFIED`.** E1 adalah **klaim negatif atas himpunan terbatas**. Sifatnya berbeda dari fakta yang dapat dicek (angka OJK) atau hasil eksperimen yang dilaporkan (recall BlockFECS). Klaim negatif tidak dapat dibuktikan, hanya dapat dibatasi cakupannya. Menandainya `VERIFIED` membuat pembaca — termasuk AI pada sesi berikutnya — memperlakukan gap sebagai perkara yang sudah tuntas. Itu kebalikan dari tujuan dokumen ini.
>
> Ini **bukan kelemahan**. Setiap klaim kebaruan di setiap skripsi punya sifat yang sama. Yang membedakan skripsi kuat dari yang lemah bukan ada-tidaknya batas itu, melainkan apakah batasnya dinyatakan atau disembunyikan. Naskah sudah menyatakannya di ¶16.
>
> **Cara memperkuatnya bukan menghapus batas, melainkan memperlebar himpunan yang ditinjau** — dan itu justru pekerjaan BAB II.

**Wording E1 yang dikunci (v1.2):**

> Belum ditemukan pendekatan pasca-akuisisi yang secara khusus mengoperasionalkan korelasi deterministik atas **fakta forensik yang dinormalisasi dari artefak sistem Android** menjadi **temuan perilaku** untuk satu keluarga insiden tertentu, dengan mempertahankan **keterlacakan ganda** (temuan→bukti pendukung, aturan→rujukan), dan dengan memperlakukan **bukti yang tidak teramati sebagai keadaan epistemik yang dinyatakan eksplisit** alih-alih sebagai ketiadaan.

⚠️ Frasa "artefak sistem Android" tunduk pada **CP-01** (§18).

#### Aturan wording

Gunakan **"belum ditemukan pada literatur yang ditinjau"**, bukan **"belum ada"**. Yang pertama adalah klaim tentang cakupan tinjauan — dapat dipertahankan. Yang kedua adalah klaim tentang dunia — tidak dapat dibuktikan dan gugur oleh satu counter-example.

#### Struktur gap dalam tiga lapis

**Lapis 1 — Akui yang sudah ada (jangan diserang):**

> Penelitian forensik digital mutakhir telah mengembangkan korelasi evidence sebagai sub-tahap resmi dalam proses investigasi mobile (Moreb dkk., 2024), kerangka rekonstruksi peristiwa berbasis timeline beserta terminologi formalnya (Breitinger dkk., 2025), korelasi deterministik berbasis aturan dengan provenance dan auditabilitas (Igonor dkk., 2026), basis pengetahuan terstruktur untuk teknik investigasi (Hargreaves dkk., 2025), identifikasi lokasi artefak melalui analisis dinamis (Boztas dkk., 2025), analisis semantik lintas kanal komunikasi mobile (Xi dkk., 2025), serta penegasan bahwa makna trace bergantung pada reference data (Spichiger & Adelstein, 2025).

**Lapis 2 — Tunjukkan bahwa masing-masing beroperasi pada lapisan berbeda:**

> Namun pendekatan-pendekatan tersebut beroperasi pada objek yang berbeda-beda: teknik investigasi (SOLVE-IT), lokasi penyimpanan artefak (Argus), isi komunikasi manusia (JoSemA), relasi antar-item evidence berdasarkan metadata kontainer (BlockFECS), atau relevansi objek terhadap skenario (Hakim & Saputri). Tidak satu pun beroperasi pada korelasi antar-artefak sistem menuju temuan perilaku aplikasi.

**Lapis 3 — Rumusan gap:**

> Pada literatur yang ditinjau, belum ditemukan pendekatan post-acquisition yang secara khusus mengoperasionalkan korelasi deterministik antar-artefak sistem Android menjadi temuan perilaku untuk suatu incident family tertentu, dengan mempertahankan keterlacakan ganda — dari temuan menuju evidence mentah, dan dari aturan menuju referensi yang mendasarinya — serta menangani evidence yang tidak teramati sebagai state epistemik eksplisit alih-alih sebagai ketiadaan.

#### Kenapa gap ini bermakna, bukan sekadar celah kombinasi

Ini bagian yang **wajib ada**. Gap yang hanya menunjuk kombinasi fitur yang belum pernah digabung akan dianggap kebaruan artifisial. Gap ini bermakna karena tiga alasan yang masing-masing punya dukungan literatur:

1. **Ketiadaan penanganan missing-evidence punya konsekuensi terukur.** BlockFECS: recall 0.17, 952 hubungan terlewat, penyebab diakui sendiri sebagai metadata parsial/bernoise. Baseline non-root ADB pada perangkat sitaan menjamin kondisi tersebut.
2. **Komunitas forensik sudah menandainya sebagai celah.** Breitinger dkk. (2025) Research Gap 3: menentukan apakah ketiadaan data disebabkan konfigurasi, tampering, atau berlalunya waktu masih sedikit diteliti.
3. **Keterlacakan referensi adalah syarat pemaknaan, bukan fitur.** Spichiger & Adelstein (2025): tanpa reference data, nilai sebuah trace tidak dapat dinilai; definisi Preservation yang mereka usulkan memasukkan reference data ke dalamnya.

#### ⚠️ Apa yang akan MEMBATALKAN gap ini

Disiplin yang jarang ditulis tetapi menyelamatkan sidang. Gap ini gugur jika ditemukan sistem yang:

- Mengorelasikan artefak **sistem** Android (bukan isi komunikasi, bukan metadata kontainer) menuju **temuan perilaku**; **dan**
- Memiliki state epistemik eksplisit untuk evidence yang tidak teramati; **dan**
- Menelusuri aturan kembali ke referensi yang mendasarinya.

**Ketiganya harus terpenuhi bersamaan.** Jika hanya satu atau dua, gap tetap berdiri dengan wording dipersempit.

**Kandidat paling berisiko membatalkan:** JoSemA dan Argus, karena keduanya mobile dan keduanya belum dibaca full-text.

---

### E2 — Posisi penelitian

**Status: `FIXED`** — design statement, bukan klaim literatur. Tidak memerlukan sumber.

#### Rumusan posisi

> Penelitian ini mengembangkan platform analisis forensik Android pasca-akuisisi yang mengoperasionalkan korelasi deterministik berorientasi perilaku dan berbasis referensi atas evidence yang telah dinormalisasi, dengan penanganan eksplisit terhadap evidence yang tidak teramati, untuk mendukung penyusunan hipotesis investigasi pada konteks insiden APK penipuan.

#### ⛔ Yang TIDAK boleh diklaim sebagai kebaruan

Setiap butir di bawah ini memiliki pembanding yang telah diverifikasi:

| Klaim terlarang | Dibantah oleh |
|---|---|
| "Menggunakan rule-based correlation" | Moreb 2024 (disebut), BlockFECS 2026 (diimplementasi) |
| "Korelasi deterministik" | BlockFECS 2026 |
| "Menggabungkan heterogeneous evidence" | Moreb, JoSemA, BlockFECS |
| "Menjaga provenance/auditabilitas" | BlockFECS, Bernardo |
| "Otomasi analisis forensik" | Thumb, Argus, Hakim |
| "Berbasis web" | bukan kontribusi ilmiah |
| "Knowledge base ala MITRE ATT&CK" | SOLVE-IT 2025 |

#### ✅ Lima diferensiasi yang bertahan

**1. Objek korelasi: artefak sistem, bukan metadata kontainer atau isi komunikasi**
BlockFECS mengorelasikan timestamp/geolokasi/device-ID/hash — properti *wadah*. JoSemA mengorelasikan makna *isi* komunikasi manusia. Penelitian ini mengorelasikan *state sistem* (package, permission, aktivitas jaringan). Tiga objek berbeda.

**2. Lapisan output: perilaku, bukan relasi antar-evidence**
BlockFECS menjawab *"dua bukti ini berhubungan?"*. Penelitian ini menjawab *"kombinasi fakta ini mendukung perilaku apa?"*. Beda level abstraksi, dan lapisan kedua belum ditempati.

**3. Semantik epistemik eksplisit**
TRUE/FALSE/UNKNOWN dan matched/not_matched/insufficient_evidence. Didukung Breitinger Gap 3 (teoretis) dan BlockFECS recall 0.17 (empiris). **Ini diferensiasi terkuat** karena punya dua jenis dukungan sekaligus.

**4. Disiplin capability versus behavior**
Output aturan dijaga agar tidak melampaui nilai pembuktian evidence: permission granted ≠ akses terjadi; aktivitas jaringan ≠ eksfiltrasi. Didukung C3b (E vs E′) dan Spichiger Bagian 3.4 yang menolak kesimpulan biner paksa.

**5. Keterlacakan ganda**
Temuan → aturan → fakta ternormalisasi → evidence mentah → sesi akuisisi, **dan** aturan → referensi ilmiah. BlockFECS kuat pada jalur pertama; jalur kedua adalah kebutuhan yang dinyatakan Spichiger dan Breitinger Gap 7 tetapi belum dioperasionalkan pada sistem manapun yang ditinjau.

#### Spesialisasi domain: keterbatasan atau keharusan?

Pertanyaan penguji yang mungkin: *"Kenapa hanya APK fraud? Bukankah itu membatasi kontribusi?"*

Jawaban yang didukung literatur: **BlockFECS sendiri menyatakan bobot korelasi yang mereka gunakan adalah nilai spesifik skenario untuk konteks kecelakaan smart city, bukan bobot forensik universal, dan konteks investigasi lain memerlukan distribusi bobot berbeda** (Bagian 2.3.1).

→ Jika parameter korelasi memang harus disesuaikan per domain, maka spesialisasi domain bukan pembatasan yang dipilih peneliti — melainkan **konsekuensi metodologis yang diakui literatur**. Generalisasi lintas domain justru yang perlu dibuktikan, bukan sebaliknya.

#### Postur yang harus diambil

Contek dari JoSemA: **melengkapi, bukan menggantikan.** Sistem ini bukan pengganti tool forensik komersial dan bukan mesin verdict malware otomatis; ia menempati satu tahap spesifik (analisis pasca-akuisisi) pada satu incident family, dengan menghasilkan hipotesis yang dapat ditelusuri untuk dievaluasi investigator.

---

### [ARSIP] E1 — Rumusan kandidat v0.1

> ⚠️ **`[ARSIP]` — BUKAN STATUS SEKARANG.** E1 yang berlaku ada di bagian pertama §6, berstatus 🔶 `BOUNDED` `USED` (¶16), dengan wording yang dikunci pada keputusan terkunci 7 (§17). Bagian di bawah ini disimpan hanya untuk menunjukkan bagaimana rumusan itu dipersempit.

**Status historis: `OPEN`** — saat itu menunggu D2, yang kini sudah selesai.

**Rumusan kandidat (v0.1), sudah dipersempit setelah temuan SOLVE-IT & Argus:**

> Knowledge base terstruktur untuk forensik digital sudah ada (SOLVE-IT), identifikasi lokasi artefak sudah ditangani (Argus/Aardwolf), dan analisis semantik lintas kanal komunikasi mobile sudah dikembangkan (JoSemA). Namun ketiganya beroperasi pada *teknik investigasi*, *lokasi artefak*, dan *isi komunikasi* — belum pada korelasi deterministik antar-artefak sistem menjadi behavior finding untuk suatu incident family tertentu, dengan traceability dan penanganan eksplisit terhadap evidence yang tidak teramati.

**Gunakan frasa "belum ditemukan pada literatur yang ditinjau", BUKAN "belum ada".**

### E2 — Posisi penelitian

**Status: `FIXED`** — design statement, bukan klaim literatur.

**Yang TIDAK boleh dipakai sebagai novelty** (terlalu mudah dibantah):
- ❌ "menggunakan rule-based correlation" — Moreb 2024 sudah menyebutnya
- ❌ "menggabungkan heterogeneous evidence"
- ❌ "menjaga provenance"
- ❌ "berbasis web"

**Yang masih bertahan sebagai diferensiasi:**
1. Spesialisasi domain APK fraud Android
2. Korelasi berorientasi **behavior**, bukan kemiripan evidence-ke-evidence
3. Semantik epistemik eksplisit (TRUE/FALSE/UNKNOWN; matched/not_matched/insufficient_evidence) — didukung S1
4. Disiplin capability vs behavior — didukung C3b, S2
5. Dual traceability: finding → rule → fact → raw evidence → sesi akuisisi, **dan** rule → referensi ilmiah

---

## 7. CATATAN VERIFIKASI KRITIS

### Insiden Moreb → Sikos (rantai atribusi putus)

Moreb dkk. (2024, hlm. 130) menulis bahwa event correlation dapat dilakukan dengan teknik "rule-based, semantic models, tree/graph-based, timestamp-based, finite state machines, live event construction" dan menyitir **[49] = Sikos, L.F. (2021), AI in Digital Forensics, WIREs Forensic Science, 3(3), e1394**.

**Setelah Sikos (2021) dibaca full-text: daftar enam teknik itu TIDAK ADA di paper Sikos.**

Yang ada di Sikos hanyalah penyebutan "rule-based" dalam konteks berbeda, dan semuanya mengutip paper lain:
- Hlm. 4 — EFIOSN, mengutip **Arshad, Jantan, Hoon & Abiodun (2020)**: relasi entitas dapat dikarakterisasi lewat korelasi interaction-based, temporal, subject-object, dan rule-based (konteks: social network forensics)
- Hlm. 4 & 6 — mengutip **Amato dkk. (2016/2019)**: SWRL rules untuk korelasi data (konteks: OWL/RDF ontology reasoning)
- Hlm. 8 — satu-satunya kalimat murni Sikos: mekanisme agregasi data seperti rule-based systems dan machine learning

**Konsekuensi:**
1. ❌ Jangan sitir Sikos (2021) untuk klaim taksonomi teknik correlation
2. Sumber primer sebenarnya: **Arshad dkk. (2020)** dan **Amato dkk. (2016/2019)** — status `NEED SOURCE`
3. Konteks literatur "rule-based" yang ada adalah **SWRL/OWL ontology reasoning** (Semantic Web), berbeda genus dari deterministic rule engine dengan three-state semantics → ini justru menguntungkan diferensiasi

**Petunjuk tambahan:** Daftar pustaka Breitinger dkk. (2025) memuat **Gladyshev & Patel (2004)** (FSM approach to digital event reconstruction) dan **Amato dkk. (2017)** (semantic evidence correlation). Daftar enam teknik itu kemungkinan ramuan dari beberapa paper berbeda, bukan taksonomi utuh dari satu sumber.

---

## 8. REKAP STATUS

> ⚠️ **Tabel status yang berlaku ada di §14.** Bagian ini adalah ringkasan; bila berbeda, §14 yang menang.

| ID | Claim | Beban | Status v1.2 |
|---|---|---|---|
| A0 | Skala penipuan finansial (OJK/IASC) | Supporting | ✅ `VERIFIED` `USED` |
| **A0b** | **Skala produksi APK berbahaya (Kaspersky)** | **Supporting** | ✅ `VERIFIED` `USED` — *baru v1.2* |
| A1 | APK sebagai komponen teknis aktif | Core | ✅ `VERIFIED` `USED` |
| A2 | Situasi investigatif (jembatan) | **Core (jembatan)** | ✅ `VERIFIED` `USED` |
| A-del | Distribusi sebagai salah satu mekanisme | Supporting | ✅ `VERIFIED` `USED` |
| B1 | Android punya multiple artifacts | Core | ✅ `VERIFIED` |
| B2 | Analisis ≠ akhir di akuisisi | Core | ✅ `VERIFIED` `USED` |
| B3 | Integritas/reproducibility | Supporting | ✅ `VERIFIED` `USED` |
| **B4** | **Manual tidak praktis → perlu otomasi** | **Load-bearing** | ✅ `VERIFIED` `USED` |
| **B5** | **Reprodusibilitas → perlu deterministik prosedural** | **Load-bearing** | ✅ `VERIFIED` `USED` |
| **B6** | **Fakta vs hipotesis → perlu keterlacakan ganda** | **Load-bearing** | ✅ `VERIFIED` `USED` |
| C1 | Ketersediaan tidak seragam | Load-bearing | ✅ `VERIFIED` `USED` |
| C2a | Multi-sumber | Load-bearing | ✅ `VERIFIED` `USED` |
| C2b | Makna bergantung konteks | Load-bearing | ✅ `VERIFIED` `USED` |
| C3a | Statis ≠ runtime → **keluaran tingkat perilaku** | Supporting | ✅ `VERIFIED` `USED` — Sutter dibuang v1.4 |
| C3b | Keadaan ≠ peristiwa historis | **Load-bearing utama** | ✅ `VERIFIED` `USED` |
| C4 | **Keragaman konfigurasi** *(diturunkan v1.2)* | Supporting | ✅ `VERIFIED` `USED` |
| C5 | Korelasi relevan | Load-bearing | ✅ `VERIFIED` `USED` |
| S1 | Justifikasi tiga keadaan | Load-bearing | ✅ `VERIFIED` `USED` |
| D1 | SOTA sudah ada | Core | ✅ `VERIFIED` `USED` |
| D2 | Matriks pembanding | Gap-builder | 🔶 `BOUNDED` `USED` |
| E1 | Research gap | Gap | 🔶 `BOUNDED` `USED` |
| E2 | Posisi penelitian | Design | `FIXED` `USED` |

**Skor v1.2: 23 claim aktif — 20 `VERIFIED`, 2 `BOUNDED`, 1 `FIXED`. Nol `CANDIDATE`, nol `NEED SOURCE`.**

### Rekap sumber — dihitung ulang v1.2

Perhitungan v1.1 salah dan sudah dikoreksi. Definisi "aktif" ada di §0.

| Kategori | Jumlah |
|---|---|
| Disitir di naskah BAB I | **23** — 4 institusi/vendor + 18 ilmiah + 1 peraturan |
| Belum disitir, disimpan untuk Tabel 2 BAB II | **3** — Casey, SOLVE-IT, Argus |
| **Total aktif** | **26** |
| ●●● | **21** |
| ●●○ | **4** — Sutter, Casey, SOLVE-IT, Argus |
| Peraturan (tanpa tingkat) | 1 — UU 17/2011 |
| Cadangan, belum masuk naskah | 2 |
| `REJECTED` | 1 — Sikos (2021) |

21 + 4 + 1 = 26 ✅

**Keempat sumber ●●○ hanya menopang klaim tentang fokus atau posisi paper, tidak tentang temuannya** — sesuai aturan §0.

> `[ARSIP]` Rekap v1.0: "15 VERIFIED claim, 18 sumber full-text, 0 sumber ●○○". Angka 18 itu benar untuk v1.0 tetapi tidak lagi berlaku setelah empat dokumen institusi/vendor masuk.

---

## 9. STRUKTUR PARAGRAF LATAR BELAKANG

### Prinsip pengelompokan

**Jangan buat satu paragraf per claim.** Lapisan C punya 6 sub-claim; kalau masing-masing dapat satu paragraf, hasilnya 6 paragraf berturut-turut yang isinya "ada masalah" — melelahkan dan terasa mengulang.

Kelompokkan berdasarkan **jenis masalah**, bukan per ID:

| Blok | Claim | Pesan tunggal |
|---|---|---|
| Blok I | C1 | Evidence tidak lengkap |
| Blok II | C2a + C2b + C4 | Evidence tersebar dan maknanya bergantung konteks |
| Blok III | C3a + C3b | Evidence tidak bicara langsung tentang perbuatan |

### Peta paragraf (13 unit argumentatif — final v1.4)

| ¶ | Isi | Claim | Kata | Gabungan dari |
|---|---|---|---|---|
| 1 | Konteks: skala penipuan + skala produksi APK berbahaya | A0, A0b | ~150 | ¶1 |
| 2 | APK sebagai komponen aktif + situasi investigatif | A1, A-del, A2 | ~185 | **¶2+3** |
| 3 | Akuisisi tersedia → pivot ke tahap analisis | B-pos, B2, B3, C5 | ~135 | **¶4+5** |
| 4 | **Sifat 1: ketersediaan tidak seragam** | C1 | ~118 | ¶6 |
| 5 | **Sifat 2: sumber beragam, makna kontekstual** | C2a, C2b, C4 | ~135 | ¶7 |
| 6 | Sifat 3: keadaan ≠ peristiwa → keluaran tingkat perilaku | C3a, C3b | ~175 | ¶8 |
| 7 | Sifat 4: ketiadaan data ambigu | S1 | ~136 | ¶9 |
| 8 | Relevansi fungsi intelijen negara | UU 17/2011 | ~115 | ¶10 |
| 9 | Manual tidak praktis → butuh sarana | B4 | ~93 | ¶11 |
| 10 | Dua karakteristik: determinisme prosedural + keterlacakan ganda | B5, B6 | ~195 | **¶12+13** |
| 11 | Cakupan tinjauan → SOTA → perbedaan objek | D1, D2 | ~220 | **¶14+15** |
| 12 | Rumusan gap | E1 | ~81 | ¶16 |
| 13 | Posisi penelitian + komponen platform | E2 | ~113 | ¶17 |

**Total ~1.893 kata · ~8,5 halaman Latar Belakang · BAB I utuh 14 halaman.**

### Kenapa persis empat penggabungan ini

**¶14+15 → ¶11 adalah penghematan terbesar.** Versi lama menyebut lima pendekatan dua kali: sekali sebagai "sudah ada", sekali sebagai "objeknya berbeda". Versi baru menyebut sekali, langsung dengan objeknya. Lebih pendek **sekaligus lebih tajam**, karena pembeda menempel pada namanya alih-alih menunggu satu paragraf.

**¶2+3 → ¶2** membuang Schmutz dan Riadi yang tampil dua kali dengan angka berbeda.

**¶4+5 → ¶3** menyatukan satu gerakan argumentatif yang memang tunggal: akui lalu berbelok.

**¶12+13 → ¶10** menyatukan dua karakteristik yang memang sepasang, dengan penanda "karakteristik pertama/kedua" agar tetap bisa dirujuk.

### ⛔ Yang ditolak digabung — dan alasannya

| Ditolak | Alasan |
|---|---|
| **C1 + C2** *(¶4+5)* | Dua jenis masalah berbeda: bukti tidak tersedia (akuisisi) vs bukti tersedia tetapi tidak langsung bermakna (interpretasi). Keduanya menopang RQ1 lewat jalur berbeda — C1 → status keteramatan, C2 → normalisasi dan asal-usul. Penggabungan juga merusak paralelisme "empat sifat" yang membuat blok ini mudah dipindai dan mudah dirujuk saat sidang |
| **B4 + syarat** *(¶9+10)* | Menaruh tiga claim load-bearing dalam satu blok. Bila penguji bertanya "di mana kamu membenarkan determinisme?", jawaban "di dalam paragraf 9" itu lemah |
| **Intelijen** | Ekspektasi institusional; kelima senior punya paragraf UU 17/2011 tersendiri |
| **Gap** | Kalimat terpenting di seluruh bab, sekaligus pembawa pernyataan cakupan tinjauan sebagai batas epistemik |

### [ARSIP] Peta paragraf 17 unit (v1.2–v1.3)

Versi 17 paragraf memisahkan A1/A2, B-pos/pivot, B5/B6, dan D1/D2 masing-masing jadi paragraf sendiri, serta memuat Gambar 1.1 dan 1.2 pada ¶1. Digantikan v1.4.

### ⚠️ Dua titik yang wajib dijaga saat revisi lanjutan *(baru v1.2)*

**1. ¶12–13 berisiko dibaca melingkar.** Urutannya: masalah (¶6–9) → syarat determinisme (¶12) → syarat keterlacakan (¶13) → SOTA (¶14) → gap (¶16). Penguji dapat menuduh: *"syarat disusun agar cocok dengan solusi, lalu ditemukan tidak ada yang memenuhi."*

Pertahanannya: kedua paragraf bersandar penuh pada literatur dan berbentuk **normatif** — *"mekanisme perlu bersifat"* — bukan preferensi penulis — *"penelitian ini memilih"*. **Jaga bentuk kalimat itu.** Pada v1.2 frasa "determinisme **yang dimaksud**" sudah diganti jadi pembedaan umum, karena "yang dimaksud" diam-diam menunjuk ke penelitian ini di paragraf yang seharusnya masih murni literatur.

**2. Diferensiator "keluaran tingkat perilaku" adalah kaki paling tipis.** Sudah diperkuat di ¶8. Jangan dipangkas. Lihat catatan di C3a.

### [ARSIP] Peta paragraf v0.8

Versi v0.8 menggabungkan ¶14–15 sebagai satu baris dan belum memuat gambar, cakupan tinjauan, maupun penguatan ¶8.

### Alokasi porsi (7 halaman)

| Blok | Porsi | Alasan |
|---|---|---|
| 1–3 konteks insiden | ~15% | pendek — konteks, bukan premis |
| 4–5 pengakuan + pivot | ~12% | sedang |
| **6–9 masalah inti** | **~30%** | **terbesar — di sinilah kontribusi duduk** |
| 10 fungsi intelijen | ~8% | sedang |
| 11–13 kenapa sistem | ~18% | sedang |
| 14–16 SOTA + gap | ~12% | sedang |
| 17 posisi | ~5% | pendek |

**⚠️ Paragraf tidak boleh sama panjang.** Paragraf seragam akan terasa datar. Blok sifat bukti harus terasa paling padat.

> `[ARSIP]` **Alokasi di atas disusun untuk struktur 17 paragraf dan tidak lagi berlaku.** Alokasi yang berlaku ada pada peta 13 paragraf di awal §9, lengkap dengan jumlah kata per paragraf hasil pengukuran. Pembanding angkatan yang berlaku ada di tabel komparasi enam senior pada bagian perubahan v1.4 — median 4,5 halaman, terpanjang 7,5, penelitian ini ~8,5.

### ⭐ Paragraf 10 — Relevansi fungsi intelijen negara (BARU v0.8)

**Kenapa ditambahkan:** kedua contoh skripsi senior STIN memuat paragraf yang mengaitkan penelitian ke **UU No. 17 Tahun 2011 tentang Intelijen Negara**. Ini ekspektasi institusional, dan peta paragraf sebelumnya tidak memilikinya.

**Posisi:** setelah masalah tegak (par. 5–9), sebelum syarat teknis (par. 11–13). Mengikuti pola senior: **masalah → mandat institusional → respons teknis.**

**⚠️ FRAMING WAJIB — jangan disamakan dengan senior.** Kedua senior punya jalur mulus ke *deteksi dini/early warning*. Penelitian ini **tidak**:

| ❌ Jangan | ✅ Pakai |
|---|---|
| "sistem melakukan deteksi dini ancaman" | "mendukung fungsi penyelidikan dan analisis informasi" |
| "mendukung fungsi pembuktian" | "dukungan teknis, bukan pengganti proses maupun kewenangan formal intelijen negara" |
| "peringatan dini serangan siber" | "analisis pasca-insiden yang dapat dipertanggungjawabkan" |
| real-time monitoring | pemeriksaan pasca-akuisisi |

Mengklaim deteksi dini bertabrakan dengan posisi penelitian sendiri (bukan mesin verdict, bukan monitoring real-time). Jalurnya lewat **fungsi penyelidikan dan analisis informasi**, bukan fungsi peringatan dini.

> ### ⛔ KOREKSI v1.3 — kata "pembuktian" dihapus dari posisi intelijen
>
> Versi sebelumnya menyarankan frasa *"mendukung kapabilitas penyelidikan dan pembuktian"*. **Itu salah.** UU No. 17 Tahun 2011 menetapkan fungsi intelijen negara sebagai **penyelidikan, pengamanan, dan penggalangan** — *pembuktian* bukan fungsi intelijen, melainkan ranah hukum acara pidana yang dimiliki penyidik dan pengadilan. Menggabungkan keduanya mencampur penyelidikan intelijen dengan penyelidikan KUHAP, dan itu titik serang yang mudah di sidang.
>
> Pada UU tersebut, penyelidikan dipahami sebagai upaya **mencari, menemukan, mengumpulkan, dan mengolah informasi** — sehingga pasangan yang tepat adalah **analisis informasi**, bukan pembuktian.
>
> ⚠️ **Jangan bingungkan dengan "nilai pembuktian bukti"** (*evidentiary value*) di C5, RQ2, dan §14b. Frasa itu berbeda artinya, tetap berlaku, dan **tidak boleh** ikut dihapus.

### ⚠️ Catatan alokasi: Lapisan D milik BAB II

Format kampus (PROJECT_BRIEF §9) menempatkan Tinjauan Penelitian Terdahulu di **BAB II**, bukan BAB I.

Comparative matrix D2 (9 paper × 12 kolom) adalah **material BAB II**. Di BAB I cukup 2–3 kalimat: *"penelitian terkini telah mengembangkan X, Y, Z."*

**Konsekuensi praktis:** D2 belum selesai **bukan penghalang** untuk mulai menulis BAB I. Yang dibutuhkan dari D2 di BAB I hanya cukup untuk tidak overclaim di E1.

### ⚠️ Catatan konsentrasi risiko

Paragraf 3, 6, 7, 8, 9, 10 semuanya bertumpu pada **Breitinger dkk. (2025)**. Enam dari tujuh paragraf siap-tulis berasal dari satu paper.

Mitigasi: paper itu sudah `VERIFIED` full-text dan terbit di venue forensik teratas. Tapi idealnya dipasangkan dengan minimal satu sumber Android-spesifik (lihat pekerjaan tersisa no. 4).

---

## 10. PEKERJAAN TERSISA (urut prioritas) — v1.2

| # | Pekerjaan | Prioritas | Konsekuensi bila diabaikan |
|---|---|---|---|
| 1 | **Tabel Penelitian Terdahulu BAB II** — lihat §21 untuk pembagian tiga lapisan dan sumber barisnya | **Tinggi** | Bloker utama BAB II |
| 2 | Validasi empiris kelayakan artefak via ADB pada perangkat uji | **Tinggi** | Kelompok sumber final tidak dapat ditetapkan |
| 3 | Putuskan clustering Execution state (kanal vs epistemik) | **Tinggi** | Skema Knowledge Base terblokir |
| 4 | Evaluasi **CP-01** (§18) setelah kelompok sumber final ditetapkan | Sedang | Wording E1 berpotensi tidak presisi |
| 5 | ~~Naikkan Sutter ke ●●●~~ **GUGUR v1.4** — Sutter dibuang dari naskah, sehingga tidak ada lagi sumber ●●○ yang disitir. Naikkan hanya bila dipakai di Tabel 2 BAB II | Rendah | — |
| 6 | Naikkan SOLVE-IT & Argus ke ●●● | Rendah | Baris Tabel 2 harus tetap ditulis dengan hedging |

### [ARSIP] Pekerjaan tersisa v1.0

Seluruh butir v1.0 sudah selesai: verifikasi Spichiger, tiga isu C1, matriks D2, jangkar Android untuk C3b, penurunan BSSN, penanganan C3a, finalisasi wording E1, dan penyusunan Rumusan Masalah.

---

## 11. ATURAN PEMBARUAN

- Naikkan versi setiap perubahan substantif; catat perubahannya di §20
- Status naik ke `VERIFIED` hanya setelah syarat pada §0 dipenuhi **sesuai jenis sumbernya**
- Klaim negatif atas himpunan literatur ditandai `BOUNDED`, bukan `VERIFIED`
- **Angka N pembanding adalah keluaran tinjauan, bukan kuota.** Bila BAB II menemukan pendekatan yang memenuhi kriteria inklusi, masukkan, lalu perbarui angka di ¶14 dan di sini. Mempertahankan angka demi konsistensi dokumen padahal bukti berubah adalah kebalikan dari metode ilmiah
- Perubahan aturan dicatat bertanggal, tidak dilanggar diam-diam
- Bagian yang tidak lagi berlaku **dilabeli `[ARSIP]`, tidak dihapus**
- Dokumen ini dibawa ke setiap sesi BAB I bersama tiga dokumen Canonical v2.3

---

## 12. RUMUSAN MASALAH (RQ)

**Status: `FINAL` (v0.8)** — dikunci sebagai dasar penulisan. Perubahan hanya bila pembimbing meminta.

> **Aturan:** RQ ini diperlakukan sebagai FIXED untuk keperluan penulisan draft. Jika pembimbing kelak meminta bentuk lain, yang berubah hanya paragraf 13–16 (SOTA → gap → posisi); paragraf 1–12 tidak terpengaruh karena menopang premis, bukan rumusan.

Diturunkan mundur dari rumusan kerja `01_BREAKDOWN` §1.2, dipecah menjadi tiga RQ operasional yang masing-masing memetakan ke satu lapisan sistem.

### RQ1 — Representasi

> Bagaimana artefak forensik Android yang diperoleh melalui akuisisi non-*root* dapat dinormalisasi menjadi representasi fakta yang konsisten, dengan mempertahankan asal-usul (*provenance*) dan status keteramatannya?

*(Wording final v1.3 — sesuai naskah. Gloss Inggris pada kemunculan pertama, sesuai §13 istilah kunci.)*

**Ditopang:** C1, C2a, C2b, C4, S1
**Dijawab dengan:** skema fakta ternormalisasi + parser/normalizer

### RQ2 — Korelasi

> Bagaimana mekanisme korelasi deterministik berbasis aturan dirumuskan untuk menghasilkan temuan perilaku pada insiden APK penipuan tanpa melampaui nilai pembuktian evidence, sehingga setiap temuan dapat ditelusuri hingga evidence pendukungnya dan setiap aturan dapat ditelusuri hingga referensi yang mendasarinya?

**Ditopang:** C3a, C3b, C5, B5, B6, S1
**Dijawab dengan:** skema aturan + knowledge base + rule engine

**⚠️ Dua catatan wording yang jangan diubah:**

1. **"tanpa melampaui nilai pembuktian evidence"** — ini yang membedakan sistem dari mesin verdict. Jangan dihapus saat meringkas.
2. **Dua arah keterlacakan dipisah secara gramatikal**, bukan digabung jadi daftar empat item:

```
setiap TEMUAN  → ditelusuri → EVIDENCE PENDUKUNG   (finding → rule → fact → raw evidence)
setiap ATURAN  → ditelusuri → REFERENSI            (rule → reference)
```

Menulisnya sebagai daftar ("temuan, aturan, evidence, referensi") membuat pembaca menyangka itu satu rantai panjang. Padahal dua arah berbeda dengan subjek berbeda.

### RQ3 — Evaluasi

> Sejauh mana platform yang dikembangkan menunjukkan ketepatan, keterlacakan, konsistensi, dan kemampuan menangani bukti yang tidak teramati pada skenario insiden APK penipuan yang dirancang secara terkendali?

*(Wording final v1.3 — keputusan terkunci 3 (§17). Bentuk lama "Bagaimana kinerja … dinilai" dapat dijawab hanya dengan menyebut metode pengukuran, sehingga terbaca sebagai pertanyaan metodologi. "Sejauh mana" menuntut hasil empiris — dan itu yang dijawab BAB IV.)*

**Ditopang:** rencana evaluasi BAB IV
**Dijawab dengan:** pengujian pada skenario terkendali

**⚠️ Empat dimensi wajib disebut eksplisit.** Terutama **penanganan evidence yang tidak teramati** — itu diferensiasi terkuat penelitian ini (tiga kaki bukti: Breitinger Gap 3, recall 0.17 BlockFECS, notasi `[–]` D4I). Jika RQ3 tidak mengevaluasinya, penelitian tidak pernah menguji hal yang membuatnya baru.

**Dimensi consistency** membuktikan klaim determinisme (input sama → output sama). Tanpa itu, kata "deterministik" di judul tidak pernah diuji.

**⚠️ Frasa "dirancang secara terkendali" menerangkan METODE PENGUJIAN, bukan membatasi sistem.** Menulis "pada skenario terkontrol" saja terbaca seolah sistem hanya berlaku di lingkungan yang sudah disiapkan.

**⛔ ROOT VS NON-ROOT COMPARISON — DICORET (v0.8)**

Rencana evaluasi lama memuat butir "coverage root vs non-root". **Butir ini dibuang.** Membandingkan cakupan root vs non-root mensyaratkan akuisisi pada perangkat yang di-root — bertentangan langsung dengan `PROJECT_BRIEF` §5 dan membuka scope yang sengaja ditutup.

**Tiga hal yang mirip dan jangan tertukar:**

| Hal | Status | Alasan |
|---|---|---|
| Membandingkan cakupan root vs non-root | ❌ **BUANG** | butuh rooting; kontradiksi boundary |
| Menyatakan non-root menghasilkan data parsial | ✅ **TETAP** | itu C1, ditopang Fukami Bagian 3.2 — klaim literatur |
| Menguji artefak mana yang dapat diperoleh pada baseline | ✅ **TETAP** | Tier-2 feasibility; satu kondisi, tanpa pembanding |

---

## TUJUAN (cermin RQ)

Mengikuti konvensi skripsi STIN: apa yang ditanyakan di Rumusan Masalah dijawab satu-per-satu di Tujuan.

1. **Merancang dan menerapkan** skema normalisasi artefak forensik Android yang mempertahankan provenance dan status keteramatan. *(← RQ1)*
2. **Merumuskan dan menerapkan** mekanisme korelasi deterministik berbasis aturan yang menghasilkan temuan perilaku dengan **keterlacakan ganda**: dari temuan menuju evidence pendukung, dan dari aturan menuju referensi yang mendasarinya. *(← RQ2)*
3. **Menguji** kinerja platform dari sisi correctness, traceability, consistency, dan penanganan evidence yang tidak teramati. *(← RQ3)*

---

## BATASAN MASALAH

Kriteria seleksi: hanya butir yang **membatasi apa yang dapat diklaim dari hasil penelitian**, bukan yang membatasi cara kerja.

**Versi final v1.3 — 5 butir berlabel, sesuai naskah BAB I.**

1. **Batas akuisisi.** Akuisisi logis non-*root* melalui *Android Debug Bridge* yang terotorisasi pada lingkungan investigasi terkendali. Tidak ada *rooting*, ekstraksi fisik, *chip-off*, *JTAG*, pelewatan kunci layar, maupun pemanfaatan celah keamanan. Mengikuti model Fukami dkk. (2021), penelitian berada pada jalur yang bertumpu pada **mekanisme otorisasi sah perangkat**, bukan jalur berbasis eksploitasi. Konsekuensinya cakupan bukti parsial, dan penelitian **tidak membandingkan cakupan itu terhadap tingkat hak akses lain**.
2. **Cakupan insiden.** Keluarga insiden APK penipuan Android — bukan seluruh kategori perangkat lunak berbahaya, dan **tidak dikunci** pada satu keluarga *malware*, satu mekanisme distribusi, maupun satu rantai serangan. Penipuan sepenuhnya lewat fitur aplikasi sah tanpa pemasangan APK terpisah di luar cakupan.
3. **Sumber dan bukti.** Maksimal **tiga kelompok sumber** primer. Hanya artefak yang dapat diperoleh secara layak dan berulang.
4. **Mekanisme dan keluaran.** Korelasi deterministik berbasis aturan; bukti tak teramati **tidak** otomatis bernilai salah. Keluaran dibatasi pada bukti ternormalisasi, temuan perilaku, hipotesis investigasi, aturan terpenuhi, bukti pendukung, asal-usul, rujukan, dan keterangan bukti tak teramati. **Bukan mesin penilai otomatis**, tidak menghasilkan kesimpulan hukum.
5. **Pengujian dan validitas.** Skenario terkendali pada perangkat uji dan/atau emulator Android. **Satu metode pembanding: analisis manual** terhadap bukti yang sama (Canonical §18.4). Hasil **tidak digeneralisasi** ke model perangkat, versi, vendor, keluarga *malware*, konfigurasi keamanan, atau kondisi akuisisi di luar lingkungan pengujian.

**⚠️ Butir 4 paling penting.** Tanpa itu, penguji berhak menilai sistem sebagai detektor malware yang akurasinya kurang.

**✅ Ketiga constraint institusi hadir:** satu jenis insiden → butir 2 · maksimal tiga sumber → butir 3 · satu metode pembanding → butir 5.

> `[ARSIP]` **Versi lama (5 butir tanpa label).** Butir 2 lama berbunyi *"penelitian berada pada jalur user-secret-based acquisition"*. Diganti pada v1.3 karena menyimpang dari wording Canonical dan mengundang pertanyaan "kredensial apa — PIN, sandi perangkat, akun Google, atau otorisasi host ADB?". Model Fukami tetap dipakai untuk **memposisikan jalur**, tidak untuk mendefinisikan sistem. Versi lama juga belum memuat batas validitas eksternal, daftar keluaran, maupun metode pembanding.

**TIDAK masuk Batasan Masalah** (masuk BAB III sebagai alat dan bahan): pilihan stack (Python, FastAPI, PostgreSQL, React), lingkungan pengembangan (laptop pribadi + emulator).

---

### Uji paragraf yatim

Setiap paragraf harus menopang minimal satu RQ.

| Paragraf | Menopang RQ |
|---|---|
| 1 — skala fraud (A0) | **tidak ada** ⚠️ |
| 2 — APK komponen teknis (A1) | RQ2 (spesifisitas domain) |
| 3 — situasi investigatif (A2) | RQ1 |
| 4 — akuisisi sudah mapan (B2) | RQ1 (titik mulai) |
| 5 — beban ke interpretasi (C5) | RQ2 |
| 6 — evidence tidak lengkap (C1) | RQ1 |
| 7 — heterogen (C2, C4) | RQ1 |
| 8 — state ≠ perbuatan (C3) | RQ2 |
| 9 — ketiadaan data ambigu (S1) | RQ1 + RQ2 |
| 10 — skala → otomasi (B4) | RQ3 |
| 11 — deterministik (B5) | RQ2 |
| 12 — keterlacakan (B6) | RQ3 |
| 13–16 — SOTA, gap, posisi | semua |

**Paragraf 1 satu-satunya yang tidak menopang RQ manapun.** Itu bukan cacat — dia konteks relevansi, bukan premis. Konsekuensinya: **maksimal satu paragraf pendek, dua angka** (lihat aturan A0).

### Alternatif bila pembimbing meminta lebih sedikit

Dua RQ juga sah untuk skripsi pengembangan: **RQ desain** (gabungan RQ1–RQ3) + **RQ evaluasi**. Tiga RQ di atas lebih disarankan karena masing-masing memetakan ke satu lapisan sistem, sehingga BAB III dan BAB IV lebih mudah disusun.

---

## 13. STATUS KESIAPAN DRAFT

| Prasyarat | Status |
|---|---|
| Claim map A–E lengkap | ✅ |
| 23 claim aktif: 20 `VERIFIED` + 2 `BOUNDED` + 1 `FIXED` | ✅ |
| Struktur paragraf ditetapkan | ✅ **13 paragraf** |
| **Rumusan Masalah RQ1–RQ3** | ✅ `FINAL` |
| Tujuan 1–3 (cermin RQ) | ✅ `FINAL` |
| Batasan Masalah (5 butir) | ✅ `FINAL` |
| Peta 13 paragraf (§9) | ✅ `FINAL` v1.4 |
| Paragraf UU Intelijen (par. 10) | ✅ posisi & framing ditetapkan |
| Comparative matrix D2 | 🔶 **`BOUNDED`** — Tabel 1 (**N=7**, semua ●●●) + Tabel 2 (**N=4**, deskriptif) |
| Paragraf scoping D2 | ✅ draft ditulis (§5) |
| Rumusan gap E1 | ✅ **DIKUNCI** 🔶 `BOUNDED` — wording final pada keputusan terkunci 7 (§17); cakupan tinjauan dinyatakan di ¶12 |
| Posisi penelitian E2 | ✅ FIXED |
| Konfirmasi BSSN (A1) | — tidak lagi bloker |
| Ehsan (2022) dibaca | ✅ selesai — C3a naik VERIFIED |
| Seluruh sumber ●○○ | ✅ **nihil** |

## ✅ SIMPULAN v1.5 — BAB I SELESAI

**Seluruh prasyarat terpenuhi. Ketiga belas paragraf sudah ditulis; naskah final ada pada `BAB_01_DRAFT_FINAL_2.docx` / `.md`.**

| Yang sempat jadi bloker | Status |
|---|---|
| Rumusan Masalah kosong | ✅ RQ1–RQ3 WORKING-FIXED |
| D4I & JoSemA belum dibaca | ✅ keduanya VERIFIED, bukan kompetitor |
| Paragraf scoping D2 | ✅ ditulis, **N=7**; wording cakupan diperlebar v1.2 (§21) |
| Tiga baris ●○○ | ✅ dipindah ke Tabel 2 (deskriptif) |
| Konfirmasi BSSN | ✅ tidak lagi relevan (turun jadi opsional) |

**Landasan bukti v1.5:** 23 claim aktif · 21 sumber ●●● · 0 sumber ●●○ yang disitir di naskah · 7 pembanding metodologis terverifikasi penuh · 3 kaki untuk argumen tiga keadaan (teoretis, empiris, struktural).

**Tidak ada lagi item yang menghalangi BAB I.** Bloker berikutnya seluruhnya berada di BAB II dan BAB III — lihat §10.

### Istilah kunci yang dipakai konsisten sampai BAB V

| Istilah | Definisi singkat | Muncul pertama di |
|---|---|---|
| **Keterlacakan ganda** *(dual traceability)* | temuan → evidence pendukung, **dan** aturan → referensi | Tujuan 2 |
| **Evidence tidak teramati** | status epistemik terpisah dari "tidak terjadi" | par. 9, RQ3 |
| **Temuan perilaku** *(behavior finding)* | keluaran korelasi, bukan verdict | RQ2 |
| **Hipotesis investigasi** | keluaran akhir untuk dievaluasi investigator | Batasan Masalah 5 |

Istilah Indonesia dipakai sebagai bentuk utama, padanan Inggris dicantumkan dalam kurung pada kemunculan pertama, lalu bentuk Indonesia konsisten seterusnya.


---

## 14. MASTER CLAIM REGISTRY A–E (KONSOLIDASI)

Tabel ini menelusuri **perjalanan setiap claim**: dari argumen awal yang ingin dibuktikan, melalui evidence hunting, sampai rumusan final beserta batasnya.

**Legenda status:**
`VERIFIED` = syarat §0 dipenuhi sesuai jenis sumber · `BOUNDED` = benar terhadap himpunan literatur yang ditinjau, bukan seluruh literatur · `FIXED` = pernyataan desain, tidak butuh sumber · `USED` = sudah masuk draft BAB I

> **⚠️ Ini tabel status yang berlaku.** Bila §1–§6 atau §8 menyebut status berbeda, tabel ini yang menang.

---

### LAPISAN A — INCIDENT CONTEXT

| ID | Argumen awal | Fungsi di BAB I | Claim final setelah hunting | Status | Sumber utama | Batas klaim | RQ |
|---|---|---|---|---|---|---|---|
| **A0** | Perlu bukti bahwa fraud yang jadi konteks penelitian memang nyata | Memberi urgensi praktis, **bukan** membuktikan masalah teknis | Penipuan transaksi keuangan merupakan persoalan aktual dengan volume laporan terukur, sehingga memberi konteks praktis bagi penelitian terhadap insiden fraud yang melibatkan aplikasi Android | ✅ `VERIFIED` `USED` | R-A0-01a/b/c ●●● | ⛔ Angka IASC **bukan** jumlah APK fraud; tidak membuktikan rekonstruksi sulit; tidak membuktikan korelasi dibutuhkan. **Maks 2 angka, 1 paragraf** *(dikembalikan pada v1.4 setelah gambar dihapus — lihat §17 keputusan 13)* | — |
| **A0b** | Perlu menunjukkan produksi APK berbahaya memang masif | Menjawab "kenapa APK, bukan kategori lain" dengan angka | Produksi berkas APK berbahaya berlangsung dalam volume besar, dengan pergeseran komposisi ke kategori yang menyasar kredensial keuangan | ✅ `VERIFIED` `USED` | R-A0-02 ●●● | ⛔ Telemetri satu vendor, bukan populasi — batas ini **wajib dinyatakan di prosa ¶1** (sejak v1.4 tidak ada lagi keterangan gambar yang menanggungnya). ⛔ Angka 255.090 spesifik *trojan* perbankan; **dilarang** disebut "jumlah APK penipuan". ⚠️ Kalimat pagar *"trojan perbankan hanyalah satu kategori di dalam kelompok yang lebih luas"* **tidak boleh dihapus** | — |
| **A1** | APK fraud bukan sekadar file yang dikirim; jadi komponen aktif di perangkat | Menghubungkan *fraud* → *aplikasi Android* sebagai objek teknis insiden | Aplikasi Android berbahaya dalam konteks fraud dapat menjadi komponen teknis aktif setelah installation/activation, dengan capability mencakup akses fungsi/data sensitif, interaksi aplikasi/perangkat, dan komunikasi eksternal | ✅ `VERIFIED` | Umam (2025) ●●●; Riadi/Anubis (2023) ●●●; Schmutz/Hook (2024) ●●● | ⛔ **Jangan bergeser jadi "APK fraud = banking trojan"**. Umam disebut PERTAMA sebagai jangkar incident family | RQ2 |
| **A2** | Multiple capability perlu dibawa ke problem investigasi, bukan sekadar didaftar | Menempatkan pembaca **di dalam situasi investigatif** sebelum Lapisan C | Investigator menghadapi artefak teknis yang merepresentasikan identitas/konfigurasi, state kapabilitas, data lokal, informasi eksekusi, dan komunikasi eksternal; karena aktivitas telah berlalu, analisis menggunakan artefak untuk merekonstruksi perilaku | ✅ `VERIFIED` | Hook Tabel 2 & 7 ●●●; Anubis ●●●; Breitinger (2025) ●●● | ⛔ Tidak berarti seluruh artefak selalu tersedia; tidak berarti satu artefak membuktikan behavior. **Akui: Hook & Anubis pakai emulator** | RQ1 |
| **A-del** | Awalnya phishing/social engineering hampir jadi pusat framing | Sekarang hanya contoh bagaimana APK sampai ke korban | Phishing/social engineering adalah salah satu *possible delivery mechanism*, bukan core post-acquisition problem | `OPSIONAL` | Sudjayanti & Hamdani (2024); Muthohirin (2024) | ⛔ **Satu kalimat, bukan paragraf.** Tidak dipakai sebagai backbone | — |

### LAPISAN B — FORENSIC POSITIONING

| ID | Argumen awal | Fungsi di BAB I | Claim final | Status | Sumber utama | Batas klaim | RQ |
|---|---|---|---|---|---|---|---|
| **B1** | Android menghasilkan lebih dari satu artefak/sumber data | Menunjukkan kenapa insiden APK jadi problem analisis forensik mobile | Pemeriksaan Android menghasilkan berbagai artefak yang dipakai merekonstruksi aktivitas aplikasi/pengguna | ✅ `VERIFIED` | Casey dkk. (2022) ●●○ *(hanya untuk fokus paper)*; Moreb (2024) ●●● *(klaim substantif)* | ⛔ G1/G2/G3 tetap **taksonomi operasional penelitian**, bukan taksonomi universal literatur | RQ1 |
| **B2** | Akuisisi bukan akhir proses forensik | ⭐ **Blok pengakuan** — dipasang di par. 4, sebelum masuk masalah | Investigasi forensik mobile tidak berhenti pada acquisition; data masih memerlukan examination, interpretation, validation, dan analysis/reconstruction | ✅ `VERIFIED` | Moreb (2024) hlm. 129–130 ●●● | Framework/process level; **bukan** rule engine APK-specific yang terimplementasi | RQ1 |
| **B3** | Hasil forensik harus terjaga integritas & reproducibility | Fondasi provenance & SHA-256 | Hasil pemeriksaan perlu dipertahankan integritas dan keterlacakannya agar dapat diverifikasi atau direproduksi | ✅ `VERIFIED` | Moreb (2024) hlm. 130 ●●● | Peran Bernardo (2024) untuk claim ini **sudah digantikan** Moreb yang terverifikasi | RQ3 |
| **B4** | *(tidak ada di versi awal)* | ⭐ **Menjawab "kenapa harus sistem?"** | Volume dan kompleksitas evidence membuat analisis manual tidak praktis; otomasi diperlukan untuk menginferensi event pada skala nyata | ✅ `VERIFIED` | Breitinger (2025) Gap 5 & 6 ●●●; **Hakim & Saputri (2025) ●●●** | Tanpa B4, BAB I membuktikan ada masalah tapi **tidak** membuktikan jawabannya perangkat lunak. ⭐ Konsentrasi Breitinger berkurang — kini ada penguat independen | RQ3 |
| **B5** | *(tidak ada di versi awal)* | ⭐ **Menjawab "kenapa deterministik, bukan AI?"** | Reprodusibilitas menuntut metode deterministik; metode probabilistik bertentangan dengan syarat penerimaan metode forensik | ✅ `VERIFIED` | Breitinger (2025) §6.3.2 ●●●; paper LLM in DF (FSI:DI) ●●○ | ⚠️ **Determinisme prosedural**, bukan epistemik — lihat jebakan terminologi Spichiger §3 | RQ2 |
| **B6** | *(tidak ada di versi awal)* | ⭐ **Menjawab "kenapa traceability?"** | Pemisahan fakta dari hipotesis menuntut keterlacakan eksplisit dari temuan kembali ke sumbernya | ✅ `VERIFIED` | Breitinger (2025) Research Gap 7 ●●● | Menopang **keterlacakan ganda**; juga dasar mengganti "confidence" → Rule Match Score | RQ2 |

### LAPISAN C — TECHNICAL FORENSIC PROBLEM

| ID | Argumen awal | Fungsi di BAB I | Claim final | Status | Sumber utama | Batas klaim | RQ |
|---|---|---|---|---|---|---|---|
| **C1** | Evidence tidak selalu tersedia lengkap | Blok I masalah inti | Ketersediaan evidence Android tidak seragam; pada privilege non-root akuisisi hanya menghasilkan data parsial, aplikasi dapat opt-out dari backup, dan cakupan berbeda menurut tool/jenis data/perangkat | ✅ `VERIFIED` | Fukami (2021) §2.3, 3.1, 3.2, Gbr. 1 ●●●; Salimi (2022) ●●● | ⚠️ **Kutip §2.3/3.1/3.2 saja, JANGAN §6** (model exploit-based = kontribusi mereka, bukan bagian yang dipakai) | RQ1 |
| **C2a** | Evidence berasal dari banyak sumber | Blok II | Evidence forensik mobile berasal dari berbagai lokasi dan jenis; event kompleks memerlukan beberapa tool dan pengumpulan lintas sumber | ✅ `VERIFIED` | Moreb (2024) hlm. 129–130 ●●● | — | RQ1 |
| **C2b** | Evidence beda perlu dimaknai sesuai konteks | Blok II | Signifikansi data tidak dapat diturunkan dari data evidentiary itu sendiri; makna bergantung pada reference data | ✅ `VERIFIED` | Spichiger & Adelstein (2025) §4.1 ●●● | ⚠️ Paper yang sama memuat **"illusion of determinism"** (§3.4) — wajib dijelaskan proaktif | RQ1 |
| **C3a** | Permission ≠ perilaku runtime | Blok III (ilustrasi) | Informasi statis/deklaratif menunjukkan capability/konfigurasi, bukan perilaku runtime yang teramati | ✅ `VERIFIED` | **Tulang:** Spichiger (2025) ●●● · **Ilustrasi:** Sutter (2024) ●●○, **Ehsan (2022) ●●●** | ⛔ Jangan tulis "permission tidak berguna". ⚠️ **RISIKO AKURASI** — lihat §14b | RQ2 |
| **C3b** | State teramati ≠ peristiwa terjadi | ⭐ Blok III (tulang) — **load-bearing utama** | Perlu dibedakan event E yang benar-benar terjadi dari inferred event E′ yang diturunkan dari analisis artefak; E′ mengakui ketidakpastian | ✅ `VERIFIED` | Breitinger (2025) §4.3 Q4 ●●●; **Shang/Thumb (2025) ●●● (penguat Android)**; Hook Tbl 7 ●●● | ⭐ **Jangkar Android sudah ada** — Thumb: artefak dapat terbentuk tanpa aksi pengguna eksplisit, menyulitkan atribusi jejak ke perilaku yang disengaja | RQ2 |
| **C4** | Satu perilaku, beberapa mekanisme *(diturunkan v1.2)* | Blok II — **supporting**, bukan load-bearing | Terdapat keragaman konfigurasi teknis di dalam satu keluarga insiden yang sama, sebagaimana terlihat pada variasi deklarasi izin antar-sampel; pemeriksaan yang hanya menyasar satu jenis artefak tidak menjamin tercakupnya keragaman konfigurasi yang mungkin ditemui | ✅ `VERIFIED` `USED` | Hook Tabel 2 ●●● *(Umam & Anubis kini ilustrasi, bukan lapis penopang)* | ⛔ **Dilarang** menulis "satu perilaku, banyak jalur" — variasi izin bukan bukti langsung multi-jalur. ⚠️ Jangan buka paragraf dengan nama sampel | RQ1 |
| **C5** | Correlation relevan dalam analisis forensik | ⭐ **PIVOT** — par. 5 | Correlation dan event reconstruction menghubungkan informasi lintas sumber untuk membangun hubungan, urutan, dan konteks | ✅ `VERIFIED` | Breitinger (2025) §4.1, 6.4.1 ●●●; Moreb (2024) ●●● | ⛔ Breitinger memposisikan correlation sebagai **tantangan terbuka**, bukan masalah selesai | RQ2 |
| **S1** | Ketiadaan data itu ambigu | Justifikasi three-state | Ketiadaan data dapat disebabkan konfigurasi, tampering, atau berlalunya waktu — tidak dapat langsung dimaknai sebagai bukti peristiwa tidak terjadi | ✅ `VERIFIED` | **3 kaki:** Breitinger Gap 3 ●●● · BlockFECS recall 0.17 ●●● · D4I notasi `[–]` ●●● | ⭐ **Diferensiasi terkuat** — satu-satunya claim dengan tiga jenis bukti berbeda | RQ1+RQ2 |

### LAPISAN D–E — STATE OF THE ART, GAP, POSISI

| ID | Argumen awal | Fungsi di BAB I | Claim final | Status | Sumber utama | Batas klaim | RQ |
|---|---|---|---|---|---|---|---|
| **D1** | Penelitian terkini sudah punya berbagai pendekatan | Mencegah novelty palsu | Penelitian terkini telah mengembangkan korelasi evidence, rekonstruksi timeline, korelasi deterministik dengan provenance, KB terstruktur, identifikasi lokasi artefak, dan analisis semantik komunikasi | ✅ `VERIFIED` `USED` | **7** pembanding Tabel 1 | ⛔ **Sengaja dibuat positif.** Mengakui existing dulu = menutup serangan "kan sudah ada Cellebrite" | — |
| **D2** | Pendekatan existing berbeda-beda | Membangun gap | Pendekatan existing beroperasi pada objek berbeda: teknik investigasi, lokasi artefak, isi komunikasi, relasi metadata, relevansi objek | 🔶 `BOUNDED` `USED` | **Tabel 1 (N=7)** + **Tabel 2 (N=4)** | Tabel 2 deskriptif — **tidak** membuat klaim tentang isi paper yang belum dibaca. ⚠️ `BOUNDED`: sintesis komparatif atas himpunan yang ditinjau, bukan atas seluruh literatur. **N adalah keluaran tinjauan, bukan kuota** (§11) | — |
| **E1** | Ada gap spesifik | Research gap | Pada literatur yang ditinjau, belum ditemukan pendekatan post-acquisition yang mengoperasionalkan korelasi deterministik atas **fakta forensik yang dinormalisasi dari artefak sistem Android** menjadi temuan perilaku untuk satu incident family, dengan keterlacakan ganda dan penanganan evidence tak teramati sebagai state epistemik eksplisit | 🔶 `BOUNDED` `USED` | Dari D2 | ⛔ **"belum ditemukan pada literatur yang ditinjau"**, BUKAN "belum ada". Wajib disertai pernyataan cakupan **di paragraf yang sama**. ⚠️ Frasa "artefak sistem Android" tunduk pada CP-01 (§18) | — |
| **E2** | Posisi penelitian | Penutup | Platform analisis forensik Android pasca-akuisisi yang mengoperasionalkan korelasi deterministik berorientasi perilaku dan berbasis referensi, dengan penanganan eksplisit evidence tak teramati | ✅ `FIXED` | Design statement | ⛔ 7 klaim terlarang — lihat §6 E2 | — |

---

## 14b. PENANGANAN RISIKO — "AKURASI KLASIFIKASI ≠ NILAI PEMBUKTIAN"

**Risiko yang teridentifikasi v1.0.** Ehsan dkk. (2022) Tabel 3 melaporkan akurasi deteksi malware berbasis permission **75–99,8%**. Penguji yang membuka paper ini dapat berargumen: *"Paper yang Anda kutip justru menunjukkan permission bekerja dengan sangat baik."*

### Resolusi inti — angka itu justru mendukung, bukan melemahkan

Akurasi tinggi dan kesimpulan Ehsan **tidak bertentangan**, karena menjawab pertanyaan berbeda:

| | Pertanyaan | Jawaban |
|---|---|---|
| **Deteksi/klasifikasi** | Apakah aplikasi ini tergolong berbahaya? | akurasi 75–99,8% |
| **Pemeriksaan forensik** | Perbuatan apa yang terjadi pada perangkat ini? | belum dijawab |

→ Justru **memperkuat gap**: literatur sudah sangat baik menjawab *"ini malware atau bukan"*, dan belum menjawab *"apa yang dilakukannya"*.

### Tiga alasan teknis (bila ditanya lebih dalam)

1. **Ground truth-nya label, bukan perbuatan.** Akurasi 99,8% berarti model setuju dengan label dataset, bukan bahwa model benar menentukan apa yang dilakukan aplikasi.
2. **Level inferensi berbeda.** Akurasi adalah properti populasi. Forensik menuntut pernyataan tentang satu perangkat, satu aplikasi, satu peristiwa.
3. **Papernya sendiri membatasi klaimnya.** Ehsan menyatakan malware dapat meminta permission normal untuk menyamar, dan aplikasi bersih dapat salah diklasifikasi karena meminta permission sensitif.

### ⚠️ Disiplin sitasi Ehsan

| ✅ Kutip | ⛔ Jangan kutip |
|---|---|
| Kesimpulan hlm. 16 — analisis statis tidak mampu mengamati perilaku aplikasi | Tabel 3 (akurasi 75–99,8%) |
| Temuan false positive/negative | Gambar 7 (grafik akurasi) |

Mengutip kesimpulan penulis, bukan memotong data yang menguntungkan.

### Paragraf preemptif — sisipkan di paragraf 8 (Blok III), setelah C3b

> Perlu dibedakan antara akurasi klasifikasi dan nilai pembuktian. Penelitian deteksi berbasis permission melaporkan akurasi klasifikasi yang tinggi, namun tinjauan sistematis pada bidang tersebut menyimpulkan bahwa analisis statis tidak mampu mengamati perilaku aplikasi (Ehsan dkk., 2022). Dalam konteks pemeriksaan forensik, pertanyaannya bukan seberapa akurat suatu aplikasi diklasifikasikan sebagai berbahaya, melainkan perbuatan apa yang didukung oleh evidence yang tersedia pada perangkat yang diperiksa.

**Fungsi ganda:** menutup serangan sebelum muncul, **dan** menegaskan pembedaan *akurasi vs nilai pembuktian* yang menopang seluruh posisi "bukan mesin verdict".

### Jawaban lisan untuk sidang

> "Betul, dan itu justru relevan. Paper tersebut menunjukkan klasifikasi malware berbasis permission sudah matang. Yang belum dijawab adalah pertanyaan forensiknya — apa yang terjadi pada perangkat ini. Paper yang sama menyimpulkan analisis statis tidak mampu mengamati perilaku aplikasi. Penelitian saya berada di pertanyaan kedua, bukan yang pertama."

Pola: **akui dulu, baru pisahkan pertanyaannya.**

---

## 15. REFERENCE EVIDENCE MAP — APA YANG BENAR-BENAR DIDUKUNG TIAP SUMBER

**Tingkat verifikasi:** ●●● full-text dibaca sendiri · ●●○ abstrak + cuplikan publisher · ●○○ belum dibuka siapa pun

| Ref | Sumber | Tingkat | Apa yang BENAR-BENAR didukung | Dipakai untuk | Kenapa dipilih | ⚠️ Limitasi |
|---|---|---|---|---|---|---|
| **R-A0-01a** | OJK — Satgas PASTI, *Waspada Penipuan Website Mengatasnamakan IASC*, **SP 3/STPASTI/III/2025**, 28 Mar 2025 | ●●● | 74.243 **laporan** s.d. 23 Mar 2025; 78.041 rekening dilaporkan; 33.857 diblokir | A0, **Gambar 1.1 titik 1** | Regulator primer | Bukan APK-specific |
| **R-A0-01b** | OJK, *IASC Berhasil Kembalikan Rp161 Miliar Dana Masyarakat Korban Scam*, **SP 15/GKPB/OJK/I/2026**, 21 Jan 2026 | ●●● | 432.637 **aduan** s.d. 14 Jan 2026; 721.101 rekening dilaporkan; 397.028 diblokir; kerugian Rp9,1 T | A0, **Gambar 1.1 titik 2** | Regulator primer | Bukan APK-specific · lihat catatan kesetaraan unit di bawah |
| **R-A0-01c** | OJK, *Siaran Pers RDK Juli 2026*, **SP 147/DKPU/OJK/VIII/2026**, 4 Agu 2026 | ●●● | 636.014 **laporan** s.d. 30 Jul 2026; 1.176.571 rekening dilaporkan & terverifikasi; 604.923 diblokir | A0 (¶1), **Gambar 1.1 titik 3** | Regulator primer; angka terbaru | Bukan APK-specific |
| **R-A0-02** | Kaspersky Securelist, *Mobile malware evolution in 2025*, 4 Mar 2026 (Anton Kivva) | ●●● | Paket instalasi berbahaya: 1.661.743 (2022) · 1.315.405 (2023) · 1.133.329 (2024) · 815.735 (2025). Trojan perbankan: 196.476 · 153.682 · 68.730 · 255.090 | **A0b** (¶1), **Gambar 1.2** | Satu-satunya data publik tentang volume produksi APK berbahaya | ⚠️ **Telemetri KSN, bukan populasi — batas ini wajib dinyatakan di naskah** (aturan Jenis 3 §0). Angka 255.090 spesifik *trojan* perbankan |

> #### ⚠️ Catatan kesetaraan unit — R-A0-01b *(dituntaskan v1.2)*
>
> Ketiga dokumen OJK memakai kata berbeda: SP 3 dan SP 147 menulis **"laporan"**, SP 15 menulis **"aduan"**. Sempat ditandai sebagai risiko unit tidak sebanding.
>
> **Terselesaikan lewat kesejajaran struktur.** Ketiga dokumen melaporkan **tiga metrik yang sama dalam urutan yang sama**:
>
> | Dokumen | Laporan/aduan | Rekening dilaporkan | Rekening diblokir |
> |---|---|---|---|
> | SP 3 (23 Mar 2025) | 74.243 | 78.041 | 33.857 |
> | SP 15 (14 Jan 2026) | 432.637 | 721.101 | 397.028 |
> | SP 147 (30 Jul 2026) | 636.014 | 1.176.571 | 604.923 |
>
> Ketiga kolom monoton naik. Bila "aduan" adalah unit berbeda dari "laporan", mustahil ketiganya membentuk deret konsisten pada ketiga kolom sekaligus. **Simpulan: OJK memakai dua kata untuk metrik yang sama.** R-A0-01b naik ●●○ → ●●●.
>
> **Batas kejujuran:** kesetaraan ini disimpulkan dari kesejajaran struktur, **bukan** dari pernyataan OJK bahwa kedua kata itu identik. Inferensi kuat, bukan kepastian. Bila digugat, penalaran di atas adalah jawabannya.
| **R-A1-01** | Schmutz dkk., *Forensic analysis of Hook Android malware*, FSI:DI 49, 301769 (2024) | ●●● | 64 sampel; permission kritis dengan **jumlah sampel bervariasi** (Tbl 2); **SharedPreferences flag = state residual pasca-eksekusi** (Tbl 7); model MaaS | A1, A2, **C4 lapis 1**, C3b Android | Venue forensik teratas, Android, kedalaman teknis, OA | Banking trojan — **jangan** ubah incident family; analisis dinamis pakai AVD/emulator |
| **R-A1-02** | Riadi, Sunardi & Aprilliansyah, *Analysis of Anubis Trojan Attack*, IJSSE 13(1) (2023) | ●●● | Permission manifest; Accessibility **dipaksa aktif**; IOC MD5/SHA1/SHA256; **SQLite di `data/data/<pkg>/app_webview/`**; C2 `pepito.club` | A1, A2, C4 lapis 2, **C1 (artefak privat)** | Penulis Indonesia, OA, kasus teknis independen | Emulator Genymotion Android 10; banking-malware scope; 2023 |
| **R-A1-03** | Umam, Abdillah, Izzudin & Nooriansyah, *Analisis Malware Android + D4I* (2025) | ●●● | Undangan.apk: package `com.google.androidsmsotpteski`; `RECEIVE_SMS`/`READ_SMS`/`SEND_SMS`/`INTERNET`; receiver `SmsEyeSmsListener`; Telegram Bot API | **A1 (jangkar)**, A2, C4 lapis 2, **motivasi C3b**, D2 | **Domain identik** — APK fraud Indonesia non-banking-trojan | ⭐ Tabel 7 naik dari permission → "peretasan m-banking **terjadi**" tanpa bukti perangkat. **Pakai sebagai gejala metodologis, jangan serang penulisnya** |
| **R-B/C-01** | Moreb, Salah & Amro, *A Novel Framework for Mobile Forensics Investigation Process*, IJCDS 16(1) (2024) | ●●● | MFIPF 4 fase; **Evidence Correlation sebagai sub-tahap Information Analysis**; event di lokasi berbeda; hash comparison, repeatability | B1, **B2**, **B3**, **C2a**, C5, D1, D2 | Sumber mobile-forensic langsung yang menempatkan correlation dalam analysis stage | ⚠️ **Daftar 6 teknik correlation-nya salah atribusi ke Sikos** — lihat §7 |
| **R-B/C-02** | Spichiger & Adelstein, *Preserving meaning of evidence from evolving systems*, FSI:DI 52, 301867 (2025) | ●●● | Definisi **Reference Data**; signifikansi data tidak dapat diturunkan dari data evidentiary sendiri (contoh kolom "read"); definisi Preservation diperluas mencakup reference data | **C2b**, **C3a (tulang)**, justifikasi KB | Forensik murni; menutup risiko framing drift C3a | ⚠️ **§3.4 "The illusion of determinism"** — wajib dijelaskan proaktif |
| **R-C1-01** | Fukami, Stoykova & Geradts, *A new model for forensic data extraction from encrypted mobile devices*, FSI:DI 38, 301169 (2021) | ●●● | **§3.2: tanpa rooting hanya data parsial**; §3.1: aplikasi dapat opt-out backup; §2.3: naik level NIST tidak selalu efektif; **Gbr. 1 cabang user-secret-based** | **C1**, Batasan Masalah 1–2 | Mobile-forensic langsung; Gbr. 1 memposisikan boundary secara presisi | ⚠️ **Kutip §2.3/3.1/3.2 + Gbr. 1 SAJA.** §6 (model exploit) di luar scope |
| **R-C1-02** | Salimi, Abd Warif & Ismail, *Comparative Analysis of Logical Acquisition*, MJoC 7(2) (2022) | ●●● | Dr.Fone: **0 pesan** dari 161 & 31; **0 dokumen**; MOBILedit: **1 dari 184 video**; rata-rata 97% vs 74% | **C1 (empiris)** | Bukti empiris Android; ketiga tool syaratkan **USB debugging** = prasyarat sama dengan ADB | Tool komersial, bukan ADB langsung; jurnal kampus regional |
| **R-REC-01** | Breitinger, Studiawan & Hargreaves, *SoK: Timeline based event reconstruction*, FSI:DI 53, 301932 (2025) | ●●● | **E vs E′** (§4.3 Q4); **Gap 3** ketiadaan data ambigu; **Gap 5–6** otomasi satu-satunya cara praktis; **Gap 7** fakta vs hipotesis; LLM non-deterministik (§6.3.2) | **C3b, C5, B4, B5, B6, S1** | Fondasi disipliner terkuat; DFRWS 2025 | ⚠️ **Konsentrasi risiko** — 6 claim bertumpu di sini. General DF, bukan Android |
| **R-D-01** | Igonor, Amin & Garg, *BlockFECS*, Forensic Sciences 6(3), 59 (2026) | ●●● | Korelasi deterministik + rule-based + provenance + auditability **terimplementasi**; **recall Supplementary 0.17, 952 hubungan terlewat** karena metadata parsial/noisy; bobot diakui spesifik skenario | **S1 (kaki empiris)**, D2, batas novelty | Pembanding paling berbahaya untuk novelty — **wajib** | Ground truth sebagian dari ChatGPT-4.1; IoT/smart city, bukan Android |
| **R-D-02** | Dimitriadis, Ivezic, Kulvatunyou & Mavridis, *D4I*, Array 5, 100015 (2020) | ●●● | Korelasi artefak → fase CKC **berdasarkan atribut (timestamp, nama) atau isi**; 6 langkah manual; **notasi CoA `[–]` tanpa semantik ketiadaan** | **S1 (kaki struktural)**, D2 | Dipakai Umam pada incident family identik — mengabaikannya = celah | Windows-focused ("except Android in Mobile devices"); contoh spear phishing; 2020 |
| **R-D-03** | Xi, Siegel, Labudde & Spranger, *Towards a joint semantic analysis*, FSI:DI 52, 301846 (2025) | ●●● | Analisis semantik **isi komunikasi manusia**; topic modeling/NLP; rekonstruksi course of events lintas kanal | D2, C2b pendukung | Mobile + rekonstruksi + benchmark ke Moreb — perlu dipastikan bukan kompetitor | ✅ **Terbukti bukan kompetitor**: objek percakapan, metode probabilistik |
| **R-C3-01** | Sutter dkk., *Dynamic Security Analysis on Android: SLR*, IEEE Access 12 (2024) | ●●○ | Static ≠ observasi runtime; runtime loading membatasi penentuan behavior secara statis | ⛔ **DIBUANG DARI NASKAH v1.4** — tersedia untuk Tabel 2 BAB II | Android-spesifik untuk kontras statis/dinamis | Android **security**, bukan forensik. Tumpang tindih fungsi dengan Ehsan (●●●); membuangnya menghilangkan ketergantungan ●●○ terakhir di naskah, sekaligus memangkas kata |
| **R-C3-02** | Ehsan, Catal & Mishra, *Detecting Malware by Analyzing App Permissions: SLR*, Sensors 22(20), 7928 (2022) | ●●● | **Kesimpulan hlm. 16:** analisis statis efisien tetapi **tidak menjamin deteksi komprehensif karena tidak mampu mengamati perilaku aplikasi**; malware dapat meminta permission normal untuk menyamar, aplikasi bersih dapat salah diklasifikasi | C3a (ilustrasi) | Dukungan spesifik permission dari SLR | ⚠️ **Tabel 3 melaporkan akurasi 75–99,8%** — risiko disalahpahami. Kutip Kesimpulan, JANGAN Tabel 3. Lihat §14b |
| **R-B1-01** | Casey, Nguyen, Mates & Lalliss, *Crowdsourcing forensics*, J Forensic Sci 67(5) (2022) | ●●○ | Definisi **atomic artifact** vs **dependent artifact**; volume/variasi/kompleksitas menyulitkan praktisi | B1, C2b pendukung | Definisi yang dirujuk Breitinger | Katalog artefak, bukan korelasi |
| **R-T2-01** | Hargreaves, van Beek & Casey, *SOLVE-IT*, FSI:DI 52, 301864 (2025) | ●●○ | KB forensik **terinspirasi MITRE ATT&CK**; indeks weakness & mitigation teknik investigasi | Tabel 2; validasi desain KB | Tetangga terdekat desain KB | Mengindeks **teknik investigasi**, bukan perilaku pelaku |
| **R-T2-02** | Boztas, De Jong & Hadjigeorghiou, *Argus/Aardwolf*, FSI:DI 53, 301938 (2025) | ●●○ | Analisis dinamis file system; database referensi lokasi artefak | Tabel 2 | Bukti bahwa lokasi artefak masih masalah terbuka 2025 | Berhenti di **lokasi** artefak, bukan makna |
| **R-T1-07** | Hakim & Saputri, *Efficient Evidence Reduction Technique for Mobile Forensics based on DEO Model*, JUTIF 6(4), 2707–2722 (2025) | ●●● | Akuisisi internal storage menghasilkan **dataset besar dan kompleks yang menghambat analisis tepat waktu**; DEO Model berbasis Python; filtering terstruktur parameter 5W; FPR 0,00072 | **B4 (penguat)**, **Tabel 1** | ⭐ **Poltek SSN + BSSN** — institusi kedinasan siber; Android, pasca-akuisisi, Indonesia | Fokus reduksi/relevansi, bukan korelasi relasi antar-bukti |
| **R-T2-04** | Bernardo, Mamede, Barroso & dos Santos, *Mobile Device Forensics Framework: A Toolbox*, Emerging Science Journal 8(3), 972 (2024) | ●●● | Toolbox forensik mobile via **Design Science Research**; mengatasi kurangnya guidance, dokumentasi, dan kemampuan mengikuti perubahan cepat industri mobile | ⛔ **DIBUANG DARI NASKAH v1.4** — tetap dipakai di Tabel 2 BAB II | INESC TEC + NOVA IMS Portugal; ada sejak claim map awal | Tata kelola & panduan proses — **bukan** implementasi korelasi. Peran B3-nya sudah digantikan Moreb, sehingga kalimatnya di ¶4 lama bersifat dekoratif |
| **R-T2-05** | Shang, Sakzad & Hall, *Thumb*, **FSI:DI 54, 301949** (2025) | ●●● | Thumbnail dihasilkan otomatis oleh aplikasi dan OS, **menyulitkan atribusi ke aksi pengguna spesifik**; artefak dapat terbentuk **tanpa aksi pengguna eksplisit**; MLLM + OCR + eksperimen pada perangkat fisik | Tabel 2; **C3b (penguat Android)** | ⭐ **Jangkar Android untuk C3b** — Monash University, FSI:DI, 2025 | ⚠️ **KOREKSI: volume 54/301949, bukan 53/301938.** MLLM/OCR = probabilistik |
| **R-SIKOS** | Sikos, *AI in digital forensics*, WIREs Forensic Science 3(3) (2021) | ●●● | Ontology engineering; rule-based disebut **hanya mengutip Arshad (2020) & Amato (2016/2019)** | ⛔ **REJECTED** | — | ⛔ **Daftar 6 teknik yang Moreb atribusikan ke paper ini TIDAK ADA di dalamnya.** Jangan sitir untuk klaim taksonomi |

---

## 16. DAFTAR REFERENSI — DENGAN LINK AKSES

Disusun menurut urutan tingkat verifikasi. Semua link dipilih karena dapat diakses daring.

### ✅ TERVERIFIKASI FULL-TEXT (●●●) — 12 sumber

**R01 — Moreb, Salah & Amro (2024)**
Moreb, M., Salah, S., & Amro, B. (2024). *A Novel Framework for Mobile Forensics Investigation Process.* International Journal of Computing and Digital Systems, 16(1), 125–135.
DOI: https://doi.org/10.12785/ijcds/160110
Dipakai: B1, B2, B3, C2a, C5, D1, D2 · ⚠️ Chain-of-attribution bermasalah pada daftar teknik correlation

**R02 — Breitinger, Studiawan & Hargreaves (2025)**
Breitinger, F., Studiawan, H., & Hargreaves, C. (2025). *SoK: Timeline based event reconstruction for digital forensics: Terminology, methodology, and current challenges.* Forensic Science International: Digital Investigation, 53, 301932. DFRWS USA 2025.
arXiv (akses penuh): https://arxiv.org/html/2504.18131v1
DFRWS PDF: https://dfrws.org/wp-content/uploads/2025/05/SoK-Timeline-based-event-reconstruction-for-digital-forensics-Terminology-methodology-and-current-challenges.pdf
Dipakai: C3b, C5, B4, B5, B6, S1

**R03 — Spichiger & Adelstein (2025)**
Spichiger, H., & Adelstein, F. (2025). *Preserving meaning of evidence from evolving systems.* Forensic Science International: Digital Investigation, 52, 301867. DFRWS EU 2025. CC BY-NC-ND.
DOI: https://doi.org/10.1016/j.fsidi.2025.301867
Dipakai: C2b, C3a, justifikasi KB

**R04 — Igonor, Amin & Garg (2026)**
Igonor, O. S., Amin, M. B., & Garg, S. (2026). *BlockFECS: A Blockchain-Based Proof-of-Concept System for Metadata-Driven Evidence Correlation in Digital Forensics.* Forensic Sciences, 6(3), 59. MDPI, CC BY.
DOI: https://doi.org/10.3390/forensicsci6030059
Dataset: https://github.com/igsamoshoke/BLOCKFECS-POC-DATASET
Dipakai: S1 (kaki empiris), D2, batas novelty

**R05 — Dimitriadis, Ivezic, Kulvatunyou & Mavridis (2020)**
Dimitriadis, A., Ivezic, N., Kulvatunyou, B., & Mavridis, I. (2020). *D4I – Digital forensics framework for reviewing and investigating cyber attacks.* Array, 5, 100015. CC BY-NC-ND.
DOI: https://doi.org/10.1016/j.array.2019.100015
Dipakai: S1 (kaki struktural), D2

**R06 — Xi, Siegel, Labudde & Spranger (2025)**
Xi, J., Siegel, M., Labudde, D., & Spranger, M. (2025). *Towards a joint semantic analysis in mobile forensics environments.* Forensic Science International: Digital Investigation, 52, 301846. CC BY.
DOI: https://doi.org/10.1016/j.fsidi.2024.301846
Publisher: https://www.sciencedirect.com/science/article/pii/S2666281724001884
Dipakai: D2, C2b pendukung

**R07 — Fukami, Stoykova & Geradts (2021)**
Fukami, A., Stoykova, R., & Geradts, Z. (2021). *A new model for forensic data extraction from encrypted mobile devices.* Forensic Science International: Digital Investigation, 38, 301169. CC BY.
DOI: https://doi.org/10.1016/j.fsidi.2021.301169
Dipakai: C1, Batasan Masalah · ⚠️ Kutip §2.3, 3.1, 3.2, Gbr. 1 saja

**R08 — Salimi, Abd Warif & Ismail (2022)**
Salimi, N. F., Abd Warif, N. B., & Ismail, N.-S. N. (2022). *Comparative Analysis of Logical Acquisition Using Wondershare Dr. Fone, MOBILedit Forensic, and FonePaw on Android Phones.* Malaysian Journal of Computing, 7(2), 1162–1177. CC BY-SA.
DOI: https://doi.org/10.24191/mjoc.v7i2.16968
PDF: https://ir.uitm.edu.my/id/eprint/69248/1/69248.pdf
Dipakai: C1 (empiris) · Urutan penulis ikut halaman judul, bukan running header

**R09 — Schmutz, Rapp & Fehrensen (2024)**
Schmutz, D., Rapp, R., & Fehrensen, B. (2024). *Forensic analysis of hook Android malware.* Forensic Science International: Digital Investigation, 49, 301769. CC BY.
DOI: https://doi.org/10.1016/j.fsidi.2024.301769
Publisher: https://www.sciencedirect.com/science/article/pii/S266628172400088X
Repositori: https://arbor.bfh.ch/entities/publication/ed5df520-777c-4fd2-98b8-aa78b776ad47
Dipakai: A1, A2, C4 lapis 1, C3b Android

**R10 — Riadi, Sunardi & Aprilliansyah (2023)**
Riadi, I., Sunardi, & Aprilliansyah, D. (2023). *Analysis of Anubis Trojan Attack on Android Banking Application Using Mobile Security Labware.* International Journal of Safety and Security Engineering, 13(1), 31–38. CC BY.
DOI: https://doi.org/10.18280/ijsse.130104
Artikel: https://www.iieta.org/journals/ijsse/paper/10.18280/ijsse.130104
PDF: https://www.iieta.org/download/file/fid/92945
Dipakai: A1, A2, C4 lapis 2, C1

**R11 — Umam, Abdillah, Izzudin & Nooriansyah (2025)**
Umam, M. K., Abdillah, A. K., Izzudin, A., & Nooriansyah, S. (2025). *Analisis Aplikasi Malware pada Android Menggunakan Reverse Engineering dan Framework D4I.* Jurnal Ilmu Komputer dan Desain Komunikasi Visual, 10(2), 198–214. UIN Sunan Ampel Surabaya. CC BY 4.0.
Dipakai: A1 (jangkar), A2, C4, motivasi C3b, D2

**R12 — Sikos (2021)** ⛔ **REJECTED**
Sikos, L. F. (2021). *AI in digital forensics: Ontology engineering for cybercrime investigations.* WIREs Forensic Science, 3(3), e1394.
DOI: https://doi.org/10.1002/wfs2.1394
⛔ **Jangan sitir untuk klaim taksonomi teknik correlation** — daftar 6 teknik yang diatribusikan Moreb tidak ada di paper ini. Dicatat sebagai temuan chain-of-attribution.

### 🟡 METADATA TERVERIFIKASI (●●○) — 5 sumber

**R13 — Sutter dkk. (2024)** · *Dynamic Security Analysis on Android: A Systematic Literature Review.* IEEE Access, 12, 57261–57287. CC BY.
DOI: https://doi.org/10.1109/ACCESS.2024.3390612 · Dipakai: C3a (ilustrasi)

**R14 — Casey, Nguyen, Mates & Lalliss (2022)** · *Crowdsourcing forensics: Creating a curated catalog of digital forensic artifacts.* Journal of Forensic Sciences, 67(5), 1846–1857.
DOI: https://doi.org/10.1111/1556-4029.15053 · PMC: https://pmc.ncbi.nlm.nih.gov/articles/PMC9543441 · Dipakai: B1, C2b

**R15 — Hargreaves, van Beek & Casey (2025)** · *SOLVE-IT.* FSI:DI, 52, 301864 · Dipakai: Tabel 2

**R16 — Boztas, De Jong & Hadjigeorghiou (2025)** · *Argus.* FSI:DI, 53, 301938 · Dipakai: Tabel 2

**R17 — OJK / Indonesia Anti-Scam Centre (2026)** · Laporan RDKB Juli 2026
https://ojk.go.id/id/berita-dan-kegiatan/siaran-pers/Pages/RDKB-Juli-2026.aspx
Siaran pers Januari 2026: https://ojk.go.id/id/berita-dan-kegiatan/siaran-pers/Pages/IASC-Berhasil-Kembalikan-Rp161-Miliar-Dana-Masyarakat-Korban-Scam.aspx
Dipakai: A0

### ✅ TERVERIFIKASI FULL-TEXT (●●●) — TAMBAHAN v1.0 — 6 sumber

**R18 — Ehsan, Catal & Mishra (2022)**
Ehsan, A., Catal, C., & Mishra, A. (2022). *Detecting Malware by Analyzing App Permissions on Android Platform: A Systematic Literature Review.* Sensors, 22(20), 7928. Qatar University + Molde University College, Norwegia. CC BY.
DOI: https://doi.org/10.3390/s22207928
Dipakai: **C3a (ilustrasi)** · ⚠️ Kutip **Kesimpulan hlm. 16**, jangan Tabel 3 — lihat §14b

**R19 — Hakim & Saputri (2025)** ⭐ *naik ke Tabel 1*
Hakim, A. R., & Saputri, L. (2025). *Efficient Evidence Reduction Technique for Mobile Forensics based on Digital Evidence Object (DEO) Model.* Jurnal Teknik Informatika (JUTIF), 6(4), 2707–2722. **Politeknik Siber dan Sandi Negara** + **Badan Siber dan Sandi Negara**. CC BY-NC.
DOI: https://doi.org/10.52436/1.jutif.2025.6.4.4999
Jurnal: https://jutif.if.unsoed.ac.id
Dipakai: **B4 (penguat)**, **Tabel 1 pembanding**

**R20 — Bernardo, Mamede, Barroso & dos Santos (2024)**
Bernardo, B. M. V., Mamede, H. S., Barroso, J. M. P., & dos Santos, V. M. P. D. (2024). *Mobile Device Forensics Framework: A Toolbox to Support and Enhance This Process.* Emerging Science Journal, 8(3), 972. INESC TEC + Universidade Aberta + NOVA IMS, Portugal. CC BY.
DOI: https://doi.org/10.28991/ESJ-2024-08-03-011
Dipakai: Tabel 2

**R21 — Shang, Sakzad & Hall (2025)** ⚠️ *metadata dikoreksi*
Shang, D., Sakzad, A., & Hall, S. W. (2025). *Thumb: A forensic automation framework leveraging MLLMs and OCR on Android device.* Forensic Science International: Digital Investigation, **54, 301949**. Monash University, Australia. CC BY.
DOI: https://doi.org/10.1016/j.fsidi.2025.301949
Publisher: https://www.sciencedirect.com/science/article/pii/S2666281725000885
Dipakai: Tabel 2; **C3b (penguat Android)** · ⚠️ **Volume 54/301949 — bukan 53/301938 seperti tercatat di v0.9**

**R22 — Sudjayanti & Hamdani (2024)**
Sudjayanti, S. A., & Hamdani, D. (2024). *Digital Forensic Analysis of APK Files in Phishing Scams on WhatsApp Using the NIST Method.* Brilliance: Research of Artificial Intelligence, 4(1), 100. Widyatama University. E-ISSN 2807-9035. CC BY-NC.
DOI: https://doi.org/10.47709/brilliance.v4i1.3800
Dipakai: A-delivery · Metode NIST; APKTool + Vscode APKLab; temuan SMS/OTP → Telegram

**R23 — Muthohirin, Nasuhah & Akbi (2024)** ⚠️ *urutan penulis dikoreksi*
Muthohirin, B. F., Nasuhah, A. Z., & Akbi, D. R. (2024). *Penerapan Tools JADX pada Serangan Malware Berbasis Android Menggunakan Metode NIST: Studi Kasus Undangan.APK.* Syntax: Journal of Software Engineering, Computer Science and Information Technology, 5(2), 528. Universitas Muhammadiyah Malang. p-ISSN 2776-7027, e-ISSN 2723-0538.
DOI: https://doi.org/10.46576/syntax.v5i2.5489
Dipakai: A-delivery · Metode NIST; MOBILedit + VirusTotal + JADX GUI

---

### ✅ DOKUMEN INSTITUSI & VENDOR (●●●) — TAMBAHAN v1.2 — 4 dokumen

**Otoritas Jasa Keuangan. (2025).** *Siaran Pers: Waspada Penipuan Website Mengatasnamakan Indonesia Anti-Scam Centre (IASC)* (SP 3/STPASTI/III/2025). Jakarta: Satuan Tugas Pemberantasan Aktivitas Keuangan Ilegal.
🔗 https://ojk.go.id/id/berita-dan-kegiatan/info-terkini/Pages/Waspada-Penipuan-Website-Mengatasnamakan-Indonesia-Anti-Scam-Centre-IASC.aspx
→ 74.243 laporan s.d. 23 Maret 2025. **Sitasi naskah:** (Otoritas Jasa Keuangan, 2025)

**Otoritas Jasa Keuangan. (2026a).** *Siaran Pers: Indonesia Anti-Scam Centre Berhasil Kembalikan Rp161 Miliar Dana Masyarakat Korban Scam* (SP 15/GKPB/OJK/I/2026). Jakarta: Otoritas Jasa Keuangan.
🔗 https://ojk.go.id/id/berita-dan-kegiatan/siaran-pers/Pages/IASC-Berhasil-Kembalikan-Rp161-Miliar-Dana-Masyarakat-Korban-Scam.aspx
→ 432.637 aduan s.d. 14 Januari 2026. **Sitasi naskah:** (Otoritas Jasa Keuangan, 2026a)

**Otoritas Jasa Keuangan. (2026b).** *Siaran Pers: Stabilitas Sektor Jasa Keuangan Terjaga Mendukung Pengembangan dan Penguatan Sektor Keuangan* (SP 147/DKPU/OJK/VIII/2026). Jakarta: Otoritas Jasa Keuangan.
🔗 https://www.ojk.go.id/id/berita-dan-kegiatan/siaran-pers/Pages/RDKB-Juli-2026.aspx
→ 636.014 laporan; 1.176.571 rekening dilaporkan dan terverifikasi s.d. 30 Juli 2026. **Sitasi naskah:** (Otoritas Jasa Keuangan, 2026b)

**Kaspersky. (2026).** *Mobile malware evolution in 2025* (A. Kivva). Securelist.
🔗 https://securelist.com/mobile-threat-report-2025/119076/
→ 815.735 paket instalasi berbahaya unik pada 2025, di antaranya 255.090 trojan perbankan. **Sitasi naskah:** (Kaspersky, 2026)

⚠️ **Nomor dokumen wajib dicantumkan** untuk ketiga siaran pers OJK. Siaran pers OJK terbit berkala dengan judul serupa; tanpa nomor, rujukan menjadi ambigu.
⚠️ **Securelist berhak cipta penuh** — gambar mereka tidak boleh disalin. Gambar 1.2 dibuat sendiri dari angkanya, ditandai "diolah peneliti".

---

### 🎉 TIDAK ADA LAGI SUMBER ●○○

**Seluruh 23 sumber utama telah diverifikasi minimal pada level metadata; 18 di antaranya dibaca full-text.**

### 📋 SUMBER PENDUKUNG LAIN

- **Android anti-forensics: A systematic review** (FSI:DI, 2026) — https://www.sciencedirect.com/science/article/pii/S2666281726001162 · A2, C1
- **Oh dkk. (2026)** — *Forensic analysis and evaluation of file-wiping applications in Android OS.* Journal of Forensic Sciences · https://onlinelibrary.wiley.com/doi/10.1111/1556-4029.70174 · A2
- **UU No. 17 Tahun 2011** tentang Intelijen Negara · Paragraf 10
- **BSSN (2023)** — Imbauan modus APK undangan pernikahan · A1 opsional

---

### ⚠️ CATATAN VERIFIKASI

**✅ Tidak ada lagi sumber yang belum dibaca.** Enam sumber terakhir (R18–R23) diverifikasi full-text pada v1.0.

**Tiga koreksi metadata dari verifikasi v1.0:**
1. **Thumb** — FSI:DI **54, 301949** (sebelumnya tercatat 53/301938). DOI 10.1016/j.fsidi.2025.301949.
2. **Muthohirin** — urutan penulis: Muthohirin, B. F., Nasuhah, A. Z., & Akbi, D. R.
3. **Hakim & Saputri** — afiliasi Poltek SSN + BSSN; DOI terkonfirmasi ke publisher.

**Pelajaran dari dua insiden:**
1. **Moreb→Sikos** — metadata cocok, tapi klaim tidak ada di sumber yang disitir. Chain-of-attribution wajib dicek.
2. **Fukami** — sempat ditandai "konflik scope" berdasarkan highlights publisher; setelah full-text dibaca, ternyata justru mendukung baseline. **Ringkasan bukan pengganti isi.**


---

## 14c. RIWAYAT PERUBAHAN ARGUMEN PER CLAIM *(baru v1.2)*

Diserap dari struktur claim map ChatGPT. Fungsinya menjawab pertanyaan pembimbing *"kenapa kamu sampai di rumusan ini?"* — sesuatu yang tidak dapat dijawab oleh tabel status, karena tabel status hanya menunjukkan posisi akhir.

| Claim | Argumen awal | Apa yang berubah setelah membaca sumber | Claim final |
|---|---|---|---|
| **A0** | Statistik phishing hampir jadi pusat framing | Statistik phishing diturunkan jadi A-delivery; diganti data regulator yang unitnya jelas dan dapat dilacak ke nomor dokumen | Skala penipuan finansial sebagai konteks, bukan sebagai bukti masalah teknis |
| **A0b** | *(tidak ada — claim baru)* | Ditemukan data vendor: produksi total justru **menurun**, tetapi kategori penyasar kredensial finansial melonjak. Ceritanya jadi **pergeseran komposisi**, bukan sekadar kenaikan volume | Produksi APK berbahaya masif dengan komposisi bergeser |
| **A1** | APK adalah berkas yang dikirim ke korban | Tiga kasus teknis independen menunjukkan APK jadi **komponen aktif** setelah pemasangan | APK sebagai komponen teknis aktif |
| **B4** | Belum terpikir | Muncul pertanyaan *"kenapa perangkat lunak, bukan SOP?"*. Ditemukan dua kaki: volume evidence + pernyataan bahwa otomasi kemungkinan satu-satunya cara praktis | Manual tidak praktis pada skala nyata |
| **B5** | "Deterministik" dipakai sebagai kata kunci metode | Ditemukan peringatan *illusion of determinism*. Framing anti-LLM dibuang karena penelitian ini tidak membandingkan rule engine dengan LLM | Determinisme **prosedural**, dibedakan tegas dari epistemik |
| **B6** | Keterlacakan bagus untuk audit | Dikaitkan ke pemisahan fakta vs hipotesis, sehingga menjadi **syarat epistemik**, bukan fitur antarmuka | Keterlacakan dua arah |
| **C3a** | Statis ≠ runtime | Sumber forensik dijadikan tulang, sumber keamanan jadi ilustrasi. **v1.2:** konsekuensinya ditarik eksplisit — keluaran harus pada tingkat perilaku | Kapabilitas ≠ perilaku → keluaran tingkat perilaku |
| **C4** | Satu perilaku dapat ditempuh beberapa jalur teknis | **Diturunkan v1.2** — variasi izin bukan bukti langsung multi-jalur | Keragaman konfigurasi dalam satu keluarga insiden |
| **S1** | "Akuisisi tidak lengkap, jadi pakai UNKNOWN" | Dibangun tiga kaki independen: teoretis, empiris, struktural | Ketiadaan sebagai keadaan epistemik eksplisit |
| **D1** | Godaan menyatakan "belum ada korelasi otomatis" | **Sengaja dibuat positif** untuk menutup serangan "kan sudah ada Cellebrite" | Pendekatan-pendekatan itu sudah ada |
| **E1** | "Belum ada rule-based correlation Android" | Dipersempit jadi kombinasi lima karakteristik + pernyataan cakupan tinjauan. **v1.2:** wording objek disintesiskan agar akurat secara canonical sekaligus mempertahankan diferensiator | Lihat §6 |

---

## 17. KEPUTUSAN TERKUNCI *(baru v1.2)*

Jangan dibuka ulang tanpa alasan baru.

| # | Keputusan | Tanggal |
|---|---|---|
| 1 | Baseline draft BAB I = versi Claude, bukan ChatGPT | 29 Agu 2026 |
| 2 | Batasan Masalah = **5 butir berlabel**, bukan 9 | 29 Agu 2026 |
| 3 | RQ3 memakai bentuk **"Sejauh mana…"**, bukan "Bagaimana … dinilai" | 29 Agu 2026 |
| 4 | Posisi intelijen = **penyelidikan dan analisis informasi**. Kata **"pembuktian" DIHAPUS** — bukan fungsi intelijen menurut UU 17/2011, melainkan ranah KUHAP | 29 Agu 2026 |
| 5 | Wording akuisisi kembali ke Canonical; Fukami **hanya memposisikan jalur**, tidak mendefinisikan sistem | 29 Agu 2026 |
| 6 | Metode pembanding = **analisis manual** (Canonical §18.4), masuk Batasan butir 5 | 29 Agu 2026 |
| 7 | Wording gap = **"fakta forensik yang dinormalisasi dari artefak sistem Android"** — sintesis; mempertahankan diferensiator objek sekaligus akurat terhadap model canonical `raw evidence → fact → normalized event → correlation` | 29 Agu 2026 |
| 8 | **Opsi A** — dua gambar bersandar pada ¶1; Lapisan A tetap satu unit argumentatif. Batas A0 diubah dari "maks 2 angka" jadi "1 paragraf; angka boleh lewat gambar" | 29 Agu 2026 |
| 9 | Gambar 1.1 memakai **tiga titik**; dua titik tengah (Apr & Jun 2026) dibuang karena hanya tersedia lewat berita | 29 Agu 2026 |
| 10 | Gambar 1.2 memakai **dua garis** (total vs trojan perbankan) agar kategori terbaca sebagai **irisan**, bukan keseluruhan — pagar terhadap drift keluarga insiden | 29 Agu 2026 |
| 11 | Framing anti-nondeterminisme dilunakkan; **LLM tidak dijadikan lawan** | 29 Agu 2026 |
| 12 | C4 diturunkan jadi klaim keragaman konfigurasi | 29 Agu 2026 |
| 13 | **Dua gambar dihapus** dari BAB I; batas A0 kembali ke "maks 2 angka, 1 paragraf". Pagar anti-drift trojan perbankan pindah ke prosa ¶1 | 29 Agu 2026 |
| 14 | **Latar Belakang 17 → 13 paragraf.** C1 dan C2 **tetap terpisah** — dua jenis masalah berbeda (bukti tidak tersedia vs bukti tersedia tetapi tidak langsung bermakna), keduanya menopang RQ1 lewat jalur berbeda, dan pemisahannya menjaga paralelisme "empat sifat" | 29 Agu 2026 |
| 15 | **Sutter (R-C3-01) dibuang dari naskah.** Tumpang tindih fungsi dengan Ehsan (●●●) dan satu-satunya ●●○ yang masih disitir. Akibatnya **nol sumber ●●○ di naskah**. Sutter tetap tersedia untuk BAB II | 29 Agu 2026 |
| 16 | **Bernardo (R-T2-04) dibuang dari naskah** — kalimat tata kelola perangkat bersifat dekoratif. Tetap dipakai di Tabel 2 BAB II | 29 Agu 2026 |

---

## 18. CHECKPOINT BERSYARAT *(baru v1.2)*

Berbeda dari pekerjaan tersisa: butir di sini **hanya dievaluasi bila kondisinya terpenuhi**.

### CP-01 — Wording objek korelasi pada E1

**Kondisi pemicu:** kelompok sumber bukti primer final (BAB III) memasukkan **bukti turunan APK** — hasil penguraian berkas APK itu sendiri: manifest, izin terdeklarasi — sebagai sumber primer yang dikorelasikan.

**Bila terpicu:** ubah E1 dan ¶16 menjadi *"artefak **sistem dan paket aplikasi** Android"*. Satu kata ditambahkan; diferensiator objek tetap utuh.

**Bila tidak terpicu:** tidak ada perubahan. Bukti turunan APK sebagai pengaya tidak memicu CP-01.

**⛔ Yang TIDAK boleh dilakukan:** mengganti frasa jadi *"artefak dan sumber bukti terpilih"*. Frasa itu **tidak membedakan apa pun** — setiap pendekatan korelasi memakai sumber bukti terpilih. Menggantinya membuat ¶15 melakukan pembedaan objek yang tidak dipanen ¶16, sehingga diferensiator nomor 1 hilang.

**Alasan pilihan ini:** menukar presisi hari ini demi menghindari suntingan satu kata di masa depan adalah perdagangan yang rugi.

---

## 19. [ARSIP] GAMBAR PADA BAB I

> ⚠️ **`[ARSIP]` — TIDAK BERLAKU SEJAK v1.4.** Kedua gambar **dihapus** dari naskah pada v1.4 setelah komparasi dengan enam Latar Belakang senior menunjukkan empat di antaranya tidak memakai gambar sama sekali, dan penghapusannya menghemat ~1,4 halaman. Berkas `gambar_1_1.png` dan `gambar_1_2.png` tetap disimpan dan dapat dipakai ulang untuk slide sidang atau BAB II.
>
> Isi di bawah ini disimpan agar keputusan desainnya dapat ditelusuri bila gambar suatu saat dipakai kembali.

### [ARSIP] Rancangan gambar v1.2

| | **Gambar 1.1** | **Gambar 1.2** |
|---|---|---|
| Judul | Pertumbuhan Jumlah Laporan Penipuan Transaksi Keuangan yang Diterima IASC | Jumlah Paket Instalasi Aplikasi Android Berbahaya yang Terdeteksi, 2022–2025 |
| Letak | ¶1 | ¶1 |
| Menopang | A0 | **A0b** |
| Sumber | Otoritas Jasa Keuangan (2025, 2026a, 2026b), diolah peneliti | Kaspersky Securelist (2026), diolah peneliti |
| Data | 74.243 · 432.637 · 636.014 | dua deret 2022–2025 (lihat R-A0-02) |
| Berkas | `gambar_1_1.png` | `gambar_1_2.png` |

### Aturan yang mengikat

1. **Keterangan batas metodologis pada Gambar 1.2 tidak boleh dihapus.** Itu syarat aturan Jenis 3 (§0).
2. **"Diolah peneliti" hanya sah bila lembaga penerbitnya disebut lebih dulu.** Menulis `Sumber: nama-portal-berita` melanggar disiplin rantai atribusi dokumen ini.
3. **Gambar vendor/penerbit tidak boleh disalin.** Kedua gambar dibuat sendiri dari angkanya.
4. **D4I berlisensi CC BY-NC-ND** — turunan tidak diizinkan. Notasi CoA `[–]` dijelaskan dengan teks, jangan digambar ulang.
5. **Gambar 1.2 wajib dua garis.** Versi satu garis (trojan perbankan saja) membuat pembaca menyamakan keluarga insiden penelitian ini dengan banking trojan.

### Kandidat yang ditolak masuk BAB I

| Kandidat | Alasan penolakan |
|---|---|
| Diagram tiga keadaan TRUE/FALSE/UNKNOWN | Menjelaskan mekanisme solusi **sebelum** gap dibuktikan — persis inversi argumen yang ditemukan pada draft ChatGPT ¶9. Milik BAB III |
| Grafik anomali trafik BSSN | Mengukur trafik jaringan, bukan aplikasi Android; menarik framing kembali ke keamanan siber umum |
| Variasi izin 64 sampel Hook | Baik, tetapi **dipindah ke BAB II** agar BAB I tidak jadi enam gambar |
| Cakupan akuisisi (Salimi) | Sama — dipindah ke BAB II |
| Posisi penelitian dalam tahapan MFIPF | Berguna untuk sidang, **dipindah ke BAB II** karena butuh ruang penjelasan |

---

## 20. RIWAYAT VERSI

> `[ARSIP]` **Bagian ini bukan status.** Jangan membaca "Perubahan dari v0.x" sebagai keadaan sekarang. Status yang berlaku ada di §14 dan §15.

**v1.5 (29 Agu 2026) — CLEAN HANDOFF · LOCKED.** Kebersihan dokumen saja. Kontradiksi jumlah claim diperbaiki (24 → 23); §13 disinkronkan dengan state v1.4; alokasi porsi 17 paragraf dilabeli `[ARSIP]`; **penomoran log versi pra-v1.0 dikoreksi dan v0.9 ditambahkan**. Tidak ada perubahan riset, naskah, claim, sumber, maupun keputusan.

**v1.4 (29 Agu 2026)** — Pemangkasan panjang Latar Belakang setelah komparasi dengan enam Latar Belakang senior. Dua gambar dihapus; 17 → 13 paragraf; ~2.350 → 1.893 kata; Sutter dan Bernardo dibuang dari naskah; batas A0 kembali ke "maks 2 angka, 1 paragraf"; §19 dilabeli `[ARSIP]`; §22 Prinsip pemangkasan ditambahkan. Latar Belakang ~12 → ~8,5 halaman. **Nol claim dibuang.**

**v1.3 (29 Agu 2026)** — Sinkronisasi enam sisa state lama yang terlewat pada v1.2: D2 dan C4 di §14 registry, E1 duplikat berstatus `OPEN`, RQ1 dan RQ3 di §12, panduan intelijen, dan Batasan Masalah lama. Naskah tidak berubah.

**v1.2 (29 Agu 2026)** — Konsolidasi tanpa pemotongan. Status historis dibersihkan di tempatnya; aturan baca ditambahkan; aturan verifikasi dipecah per jenis sumber; status `BOUNDED` diperkenalkan; rekap sumber dihitung ulang; claim A0b + sumber Kaspersky + tiga dokumen OJK masuk; R-A0-01b naik ●●●; C4 diturunkan; wording E1 dikunci; §14c, §17, §18, §19, §21 ditambahkan.

**v1.1 (29 Agu 2026) — DICABUT.** Ditulis ulang dari nol dan memotong 79 persen isi v1.0, termasuk matriks D2, komposisi Tabel 1 & 2, paragraf scoping, dan kutipan presisi tiap paper. Memperbaiki masalah konsistensi status sambil membuang bahan kerja yang dibutuhkan BAB II. Digantikan v1.2.

**v1.0 (27 Agu 2026)** — Milestone: tidak ada lagi sumber ●○○. Enam sumber terakhir diverifikasi full-text. Hakim & Saputri naik ke Tabel 1 (N=7) karena afiliasi Poltek SSN/BSSN dan menopang B4. Koreksi metadata Thumb: FSI:DI 54, 301949. Ehsan naik ●●● sehingga C3a punya dua ilustrasi terverifikasi; Thumb jadi penguat Android untuk C3b. Koreksi urutan penulis Muthohirin. Ditambahkan penanganan risiko "akurasi klasifikasi ≠ nilai pembuktian".

**v0.9** — Ditambahkan §14 Master Claim Registry (22 claim: argumen awal → fungsi → claim final → status → sumber → batas klaim → RQ yang ditopang), §15 Reference Evidence Map (tingkat verifikasi per sumber + apa yang benar-benar didukung + limitasi), dan §16 Daftar Referensi lengkap dengan link akses.

**v0.8** — RQ1–RQ3 direvisi final: RQ3 menyebut empat dimensi evaluasi eksplisit termasuk penanganan bukti tak teramati; RQ2 memisahkan dua arah keterlacakan secara gramatikal. Tujuan 1–3 disusun sebagai cermin RQ. Paragraf UU Intelijen ditambahkan di posisi 10; total paragraf menjadi 17 dengan alokasi timpang. Batasan Masalah disusun. **Perbandingan root vs non-root DICORET** dari rencana evaluasi.

**v0.7** — Keputusan diambil: D2 dipecah jadi dua tabel. Tabel 1 = 6 pembanding metodologis (semua VERIFIED, 13 aspek); Tabel 2 = 5 pendekatan berdampingan (deskriptif, 3 kolom). Spichiger dikeluarkan dari kedua tabel karena berperan sebagai fondasi konseptual, bukan pembanding. SOLVE-IT & Argus dipindah ke Tabel 2 karena gugur kriteria (ii), konsisten dengan Bernardo/Hakim/Thumb. N=6.

**v0.6** — D4I (Dimitriadis, 2020) dan JoSemA (Xi, 2025) diverifikasi full-text; keduanya **bukan** kompetitor, dan D4I justru memberi kaki ketiga untuk S1 lewat notasi CoA `[–]` tanpa semantik ketiadaan. RQ1–RQ3 dikunci sebagai WORKING-FIXED. Paragraf scoping D2 ditulis. Hakim/Bernardo/Thumb direkomendasikan dicoret dengan justifikasi kriteria — rekomendasi yang kemudian gugur pada v1.0.

**v0.5** — Lapisan A direvisi total: A1 & A2 naik ke VERIFIED lewat tiga sumber forensik full-text (Umam 2025, Riadi/Anubis 2023, Schmutz/Hook 2024). BSSN diturunkan jadi opsional dan tidak lagi menjadi bloker. C4 diganti sumber dari laporan vendor ke jurnal forensik dengan susunan tiga lapis anti-penyempitan. Rumusan Masalah RQ1–RQ3 disusun (§12).

**v0.4** — C1 naik ke VERIFIED; konflik scope Fukami **terbantah** setelah full-text dibaca — Bagian 3.2 justru mendukung baseline non-root secara langsung. Metadata Salimi dituntaskan. C3a direstrukturisasi: Spichiger jadi tulang, sumber keamanan jadi ilustrasi. Kaart & Laraghy dicoret, diganti Thumb (2025); metadata Thumb dilengkapi.

**v0.3** — D2 comparative matrix disusun (9 pembanding × 13 aspek, dengan penanda tingkat verifikasi per sumber). Lapisan E ditulis lengkap: E1 rumusan gap tiga lapis + kondisi pembatalan, E2 posisi penelitian + lima diferensiasi yang bertahan. C2b naik ke VERIFIED lewat Spichiger full-text. Jebakan terminologi determinisme didokumentasikan.

**v0.2 dan v0.1** — Tidak terdokumentasi. Dokumen v1.0 tidak memuat catatan perubahan untuk kedua versi tersebut.

> ⚠️ **Catatan penomoran.** Pada dokumen v1.0, baris berlabel *"Perubahan dari v0.X"* berarti *"apa yang dikerjakan versi v0.X+1"*. Saat log itu disalin ke §20 pada v1.2, pembacaannya keliru sehingga seluruh entri pra-v1.0 tercatat satu nomor terlalu rendah dan **v0.9 hilang**. Penomoran di atas sudah dikoreksi pada v1.5 dan merupakan yang berlaku.

---

## 21. PANDUAN TABEL PENELITIAN TERDAHULU BAB II *(baru v1.2)*

Ditulis untuk mencegah salah paham: **angka tujuh di ¶14 tidak membatasi jumlah pustaka BAB II.**

### Tiga lapisan yang berbeda fungsi

| Lapisan | Isi | Jumlah | Fungsi |
|---|---|---|---|
| **Tabel Penelitian Terdahulu** | Lanskap penelitian bidang ini | 10–15+ | Menunjukkan penguasaan literatur |
| **Tabel 1 — Pembanding metodologis** | Yang memenuhi kriteria inklusi ¶14 | **7** | Memikul beban klaim gap |
| **Tabel 2 — Pendekatan berdampingan** | Relevan tetapi tidak memenuhi kriteria | 4 | Menunjukkan kesadaran atas pendekatan lain |

Tujuh adalah jumlah pendekatan yang **memikul beban klaim gap**, bukan jumlah pustaka yang ditinjau.

### Sumber baris tambahan — semuanya sudah dibaca

Dari 26 sumber aktif, yang **belum** masuk Tabel 1: Casey (katalog artefak) · SOLVE-IT (basis pengetahuan forensik) · Argus (basis data lokasi artefak) · Bernardo (toolbox forensik mobile) · Shang/Thumb (artefak tanpa aksi pengguna) · Fukami (model akuisisi) · Salimi (evaluasi cakupan) · Riadi (analisis Anubis) · Schmutz (analisis Hook) · Sudjayanti (studi kasus APK Indonesia) · Muthohirin (studi kasus APK Indonesia) · Sutter (analisis dinamis Android) · Ehsan (deteksi berbasis izin).

**Dua belas** — ditambah tujuh pembanding, tersedia **19 baris** yang seluruhnya sudah dibaca dan diverifikasi.

### Dua kewajiban

**1. Tabel Penelitian Terdahulu wajib punya kolom penanda pembanding metodologis.** Tanpa itu, penguji akan bertanya *"kenapa dibandingkan dengan tujuh ini, bukan dengan yang lain?"* Jawabannya kriteria inklusi — dan kriteria itu harus terlihat di tabelnya.

**2. N bukan kuota.** Bila BAB II menemukan pendekatan kedelapan yang memenuhi kriteria dan dekat dengan sistem ini, **masukkan**, lalu ubah satu kata di ¶14. BAB II adalah kesempatan terakhir untuk mencoba mematahkan gap sendiri — mempertahankan angka demi konsistensi dokumen membuang kesempatan itu.

### Wording cakupan tinjauan — diperbarui v1.2

Wording lama *"venue utama forensik digital serta jurnal nasional terindeks"* tidak cocok dengan himpunan sebenarnya, yang mencakup FSI:DI, Array, IJCDS, Forensic Sciences, IEEE Access, Sensors, J Forensic Sci, ESJ, MJoC, IJSSE, dan JUTIF.

**Wording yang berlaku:** *"publikasi ilmiah pada venue forensik digital dan jurnal terkait, termasuk jurnal nasional untuk konteks insiden lokal."*

Ini penting karena paragraf tersebut berfungsi sebagai **batas epistemik** klaim gap. Deskripsi cakupan harus cocok dengan cara paper benar-benar dipilih.


---

## 22. PRINSIP PEMANGKASAN *(baru v1.4)*

Dipakai saat memangkas v1.3 → v1.4, dan berlaku untuk pemangkasan berikutnya di bab mana pun.

### Empat syarat yang wajib bertahan di tiap paragraf

| Syarat | Artinya |
|---|---|
| **Proposisi inti** | apa sebenarnya yang mau dibuktikan paragraf ini |
| **Sumber terkuat** | minimal satu jangkar kredibel tetap ada |
| **Batas klaim** | pagar overclaim tidak ikut terpotong |
| **Fungsi transisi** | paragraf berikutnya tetap terasa menyusul secara logis |

Bila keempatnya bertahan, paragraf 220 kata boleh menjadi 120 kata tanpa kehilangan bobot akademik. Sebaliknya, mempertahankan tiga contoh, empat angka, dan empat sitasi **tidak** otomatis membuat paragraf lebih kuat.

⚠️ Dua syarat terakhir yang paling sering terlewat. Contoh nyata: saat ¶10 lama (intelijen) dipangkas ~30 persen, pagar non-substitusi kewenangan intelijen nyaris ikut terbuang — padahal itu butir terpenting di paragraf tersebut.

### Yang dipangkas dan yang tidak

| Aman dibuang | Tidak boleh dibuang |
|---|---|
| Sumber pendukung yang tumpang tindih fungsi (Sutter) | Claim, sekecil apa pun bebannya |
| Bukti yang muncul dua kali di paragraf berbeda | Jangkar sumber terkuat tiap claim |
| Statistik ketiga dan keempat dari satu sumber | Pagar overclaim / batas klaim |
| Kalimat dekoratif tanpa beban argumen (Bernardo) | Tiga kaki argumen S1 |
| Deskripsi ganda pendekatan yang sama (¶14 vs ¶15) | Pernyataan cakupan tinjauan pada ¶12 |
| Pertanyaan retoris berpanjang-panjang | Pembedaan determinisme prosedural vs epistemik |

### Dua catatan metodologis

**Menggabung paragraf hampir tidak memendekkan halaman.** Pada spasi ganda, 17 → 13 paragraf hanya menghemat ~0,3 halaman. Panjang datang dari **jumlah kata**, bukan jumlah paragraf. Penggabungan berguna untuk kerapian argumen; pemendekan datang dari membuang pengulangan.

**Angka target adalah kawat pemicu, bukan hukum.** Bila jumlah kata Latar Belakang turun di bawah ~1.500, berhenti dan periksa keempat syarat di atas satu per satu — bukan berasumsi masih aman, dan bukan pula menolak memotong. Bila sebuah claim dapat dinyatakan dengan 60 kata alih-alih 110, potong.

### Kalibrasi terhadap angkatan

Median Latar Belakang senior ≈ 4,5 halaman; terpanjang 7,5 (lihat tabel di bagian perubahan v1.4). Draft ini pada ~8,5 halaman berada **sedikit di atas yang terpanjang**, dan itu posisi yang dapat dibela: bab ini memuat tinjauan pembanding dan rumusan gap terbatas yang tidak dimiliki draft lain. Yang tidak dapat dibela adalah posisi lama di ~12 halaman.
