# MAP — peta v0.45 → v1.00 (draf untuk review user)

Tingkat **peta**. Kartu draf tiap milestone sudah ada (`v0.45.md` … `v1.00.md`) dan **wajib disegarkan** lewat
`/plan-milestone v0.XX` (mode *refresh*, model besar) setelah tag milestone sebelumnya, karena kartu harus menyebut
nama berkas/fungsi/tabel yang benar-benar ada dan hasil Tier-2 mengubah keanggotaan artefak. Peta ini mengunci: urutan, isi, titik kontrak, pemetaan
operasi, keputusan `[plan]`, jadwal, dan daftar yang boleh dipangkas. Sumber: `01_BREAKDOWN` §8–§18,
`02_ARSITEKTUR` §N, §V, §Y.3.5–§Z.1, §AA.1, §AC, §AJ.

## Jadwal target — 8 minggu (±30 Sep → ±30 Nov 2026)

| Minggu | Milestone | Kartu | Beban user (di luar review) |
|---|---|---|---|
| 1 | v0.05 · v0.10 | 10 | AVD #1, password pemeriksa |
| 2 | v0.20 · awal v0.30 | ±11 | AVD hidup saat uji |
| 3 | v0.30 · v0.40 | ±13 | cek layar irisan tegak |
| 4 | **v0.45** Tier-2 G1 formatif | 9 | snapshot `clean` AVD #1 |
| 5 | **v0.50** · **v0.60** | 14 | review YAML & hasil 7 kelas skenario |
| 6 | **v0.70** G2/G3 + rekonstruksi | 9 | AVD #1 hidup saat Tier-2 formatif G2/G3 |
| 7 | **v0.80** simulator + 20 authoring | 10 | Gemini di Android Studio, pilih aplikasi S-B |
| 8 | **v0.90** freeze + holdout + S-C + baseline manual + Tier-2 konfirmatif | 10 | **baseline manual** (kerja peneliti), VM S-C, **Galaxy A10 + AVD #2** |
| sisa | **v1.00** laporan, dokumen, paket agen | 6 | review akhir |

Total 92 kartu (34 + 58 draf) ≈ 2 kartu/hari kerja. **Ketat.** Bila tertinggal >3 hari, pakai daftar pangkas di bawah
sebelum menggeser v0.90 (hasil v0.90 = bahan BAB IV).

## Keputusan yang dipakai peta ini

| # | Keputusan | Sumber |
|---|---|---|
| K1 | Tier-2 dijalankan **lewat agen** (profil akuisisi `tier2_*`, 3 ulangan, reset tiap ulangan, dicatat per lingkungan) — agen yang sama dengan yang dipasang di laptop pemeriksa | user 2026-09-29 |
| K2 | Analisis statis S-C memakai alat **Android SDK** yang sudah terpasang: `aapt2 dump badging/xmltree/permissions` + `apksigner verify --print-certs` + ekstraksi string/URL dengan Python stdlib (`zipfile`, `re`). Tanpa dependency baru, tanpa eksekusi APK. Dijalankan **di VM terisolasi**; yang masuk platform hanya **bundel teks hasil ekstraksi + SHA-256 APK** (biner tidak pernah keluar VM). Ekstraktor yang sama dipakai untuk `pull_subject_apk` pada APK simulator/benign | `[plan]` — dipilih sesuai §Y.3.5a (statis saja, tanpa lisensi/dependency) |
| K3 | Data G2 sintetis di emulator lewat mekanisme lab bawaan: `adb emu sms send <nomor> <teks>` (SMS masuk), `adb shell content insert` untuk kontak/call log. Satu skrip `scripts/adb/seed_synthetic.sh` + berkas data sintetis. A10: tidak di-seed; statusnya dicatat apa adanya (temuan per lingkungan) | user 2026-09-29 |
| K4 | Simulator Kotlin **berlapis**: Sonnet menulis Gradle, kontrak modul, test, dan **blok `PROMPT-GEMINI`** di kartu; user menempel prompt ke Gemini di Android Studio; Sonnet memverifikasi lewat `./gradlew` + `adb`. Kartu v0.80 membawa format ini | user 2026-09-29 |
| K5 | Distribusi agen: paket **PyInstaller** (`agent.exe`) di v1.00 (menutup data OPEN "distribusi agen"); VPS setelah v1.00 | user + §I.3 |
| K6 | Tier-2 **formatif** (v0.45.9, v0.70.3) hanya di AVD #1; Galaxy A10 dan AVD #2 hanya dipakai Tier-2 **konfirmatif** (v0.90.7–.8), sesuai pembedaan §AJ.2. Pengembangan v0.05–v0.80 tidak bergantung pada perangkat fisik. Parser ketat: struktur tak dikenali → `failed`, bukan diurai sebagian | user 2026-09-30 |

## Pemetaan 6 operasi yang tersisa (jawaban: masuk versi berapa)

Tidak perlu menunggu hasil apa pun untuk **merencanakannya**; perintah final tiap operasi ditutup oleh Tier-2
di milestone yang sama (data OPEN "perintah ADB final"). Satu operasi boleh menjalankan beberapa perintah
berurutan → beberapa berkas bukti (`sequence`) `[plan]`.

| ID operasi | Milestone | Perintah kandidat (difinalkan Tier-2) | Kelompok | Memasok profil |
|---|---|---|---|---|
| `collect_package_detail` | v0.45 | `dumpsys package <pkg>` | G1 | identitas, izin requested/granted, receiver/service, waktu instal, installer, signing → K01-P01/P02, K03-P01 |
| `collect_accessibility_state` | v0.45 | `settings get secure enabled_accessibility_services` · `settings get secure enabled_notification_listeners` · `appops get <pkg> SYSTEM_ALERT_WINDOW` | G1 | K02-P01/P02/P03 |
| `collect_usage_state` | v0.45 | `dumpsys usagestats` · `dumpsys activity activities` · `ps -A -o PID,UID,NAME` | G1 | K04-P01/P02/P03, K03-P03 |
| `pull_subject_apk` | v0.45 | `pm path <pkg>` → `adb pull <path dari keluaran agen sendiri>` → ekstraktor K2 | G1 statis | K01-P03, K02-P04, K03-P02 |
| `collect_sensitive_provider_data` | v0.70 | `content query --uri content://sms` · `content://contacts/phones` · `content://call_log/calls` | G2 | konteks K01, rekonstruksi |
| `collect_network_stats` | v0.70 | `dumpsys netstats detail` | G3 | K05-P01 |

`<pkg>` = parameter `package_name` (regex REF §OPS). Path APK **tidak** pernah datang dari backend.

## Milestone

### v0.45 — Kelengkapan G1 + Tier-2 formatif (Increment 2) · ±8 kartu · 2 kontrak
Hasil: seluruh artefak inti G1 terakuisisi/terurai/ternormalisasi; 5 status ketersediaan berujung benar;
fakta negatif eksplisit; status Tier-2 G1 formatif di AVD #1 (K6).
1. `collect_package_detail` + parser + normalisasi (izin, komponen, receiver+intent, waktu instal, installer, signing).
2. `collect_accessibility_state` + parser (layanan aksesibilitas, listener notifikasi, overlay).
3. `collect_usage_state` + parser (UsageEvents → `historical_event`; activity/ps → `current_state`).
4. `pull_subject_apk` + ekstraktor statis K2 + parser `apk_static` (uji pada APK sistem bawaan AVD).
5. **Kontrak §8/§Y.3.6** — rantai `availability_status → evidence_state → UNKNOWN`, layanan *cakupan sumber*
   (sumber diperoleh? terurai? cakupan selector lengkap?) sebagai bahan evaluator v0.60.
6. **Kontrak §Y.3.2 butir 6** — fakta negatif `predicate_value=false` hanya untuk predikat tertutup bercakupan lengkap.
7. Runner Tier-2 lewat agen (K1): profil `tier2_g1`, reset (AVD: snapshot `clean`; A10: reboot), label lingkungan,
   ekspor `experiments/feasibility_tier2/results/tier2_g1_<env>.csv`. Generik untuk 3 label, dijalankan di AVD #1 saja.
8. Jalankan Tier-2 G1 formatif di AVD #1 → `docs/tier2_g1.md`, isi data OPEN → tag.

### v0.50 — Basis pengetahuan + pemuat YAML (Increment 3) · ±5 kartu · 1 kontrak
1. `KB_Source` + `knowledge_base/data/sources.yaml` (11 entri §12.1) + loader/validator.
2. Lima `family.yaml` **disalin apa adanya** dari `01_BREAKDOWN` §14.2 + model `RuleMetadata`, `RuleReference`, `RuleElementReference`.
3. **Kontrak §Z.0/§Y.3.3/§Y.3.3a** — validasi saat muat: field wajib, `profile_id` unik, `fact` ∈ katalog & kelas =
   `expects_epistemic_class`, `reference_ids` resolve, `any_of` setara, larangan override, `validation_only`.
4. Siklus status + `content_hash` (dev: `design_baseline`/`authoring_candidate`; holdout: hanya `frozen_for_holdout` + manifest).
5. Test "YAML rusak → gagal dimuat" untuk tiap aturan + rute baca aturan/KB → tag.

### v0.60 — Mesin aturan 3-keadaan (Increment 3) · ±8 kartu · 5 kontrak
1. Model `CorrelationRun`, `RuleFamilyEvaluation`, `RuleProfileEvaluation`, `RuleConditionResult`, `RuleConditionFact` (§AA.1–AA.2).
2. **Kontrak** selector + 6 operator → TRUE/FALSE/UNKNOWN (pakai layanan cakupan v0.45).
3. **Kontrak** keluaran profil, dua sumbu aplikabilitas, `skipped_not_applicable`, agregasi keluarga.
4. **Kontrak** konflik → `UNKNOWN/conflicting_evidence`; efek eksklusioner; *fixture adapter* `validation_only`.
5. **Kontrak** kewajiban pencatatan (tiap kondisi; fakta untuk TRUE/FALSE; nol fakta + alasan untuk UNKNOWN).
6. **Kontrak** `CorrelationFinding` (maks 1 per profil matched) + `claim_level`.
7. `POST /api/cases/{id}/analyze`, `GET /evaluations`, `GET /findings` + UI `EvaluationTable`, `ConditionResultTable`.
8. Matriks uji sintetis A/B/C/D1/D2/E/F + determinisme 3× → tag.

### v0.70 — G2 + G3, rekonstruksi, keterlacakan penuh (Increment 4) · ±8 kartu · 2 kontrak
1. `collect_sensitive_provider_data` + skrip seed K3 + parser (fakta `data_present`, data sintetis saja).
2. `collect_network_stats` + parser (bucket UID → `uid_network_activity_observed`, `aggregated_window`, delta).
3. Tier-2 G2/G3 formatif lewat runner di AVD #1 → `docs/tier2_g2g3.md`.
4. **Kontrak** `ReconstructionRun`/`ReconstructionFinding` + gerbang (≥2 keluarga, subjek & jendela kompatibel, ≥1 `observed_activity`).
5. **Kontrak** `InvestigationHypothesis` dibatasi `claim_level` + `missing_evidence`, imutabel per run.
6. `TraceabilityService` dua arah + `GET /reconstructions`.
7. UI: `FamilyProfilePanel`, `EvidenceTracePanel` (tiga basis), badge UNKNOWN/konflik/claim, `ReconstructionTimeline`.
8. Sapuan `claim-auditor` + `forensic-integrity-reviewer` → tag.

### v0.80 — Simulator aman + 20 kasus authoring (Increment 5a) · ±9 kartu · 1 kontrak
1. Skema `ground_truth.json` (§N.6) + validator + konvensi `scenario_id`.
2. Proyek Gradle (Kotlin 2.3.21, AGP 9.3.0, flavor `authoring`/`holdout`/`benignControl`) — Sonnet + `PROMPT-GEMINI`.
3. Modul identitas/izin/akses khusus: aksesibilitas no-op, overlay **SIMULASI UJI**, listener notifikasi — `PROMPT-GEMINI`.
4. Pemicu terlihat (`BOOT_COMPLETED` → notifikasi) + aktivitas pemakaian + `local-endpoint` (Python stdlib `http.server`).
5. Pengendali skenario host (reset → install → seed → aksi → oracle → akuisisi → verifikasi), tolak bila hash/manifest tidak cocok.
6. **Kontrak** *fixture adapter* eksklusioner + injeksi konflik (hanya `authoring`/`holdout`).
7. 20 kasus authoring (4/keluarga, ≥2 konflik, ≥2 eksklusioner, D1 tiap peran opsional).
8. Pilih & jalankan S-B benign/kontrol (USER memilih; Claude mencatat hash/signature).
9. Laporan authoring + penyesuaian YAML dalam batas §14.3 lewat `/rule-change` → `authoring_candidate` → tag.

### v0.90 — Freeze, holdout, S-C, baseline manual, Tier-2 konfirmatif, hasil (Increment 5b) · ±10 kartu · 2 kontrak
1. USER menyegel kriteria + vektor keluaran 8 bundel holdout (hash di-commit, isi tetap di `experiments/holdout_cases/`, Claude tidak membaca).
2. **Kontrak** `freeze_manifest.json` + YAML `frozen_for_holdout` + tag `rules-v1-freeze`.
3. Bangun & akuisisi 8 bundel holdout (varian `holdout` simulator).
4. USER: baseline manual atas bundel yang sama, **disegel sebelum** analisis otomatis dilihat.
5. **Kontrak** analisis otomatis holdout + uji konsistensi 3× (pembanding semantik, bukan ID/timestamp).
6. S-C di VM: matriks ≥6 kandidat → 3 akhir; bundel ekstraksi K2 diimpor; laporan relevansi statis.
7. USER: Galaxy A10 dibaca versinya → AVD #2 dibuat dengan API yang sama (A10 tidak ada → berhenti, amandemen `G-05` oleh user).
8. Tier-2 konfirmatif G1+G2+G3 di AVD #1, AVD #2, A10 (runner v0.45.8; ⛔ ubah parser/aturan setelah freeze) → `docs/tier2_confirm.md`.
9. Rekap hasil per kasus & per kelas (tanpa skor agregat) → `docs/results/` untuk BAB IV.
10. Tag.

### v1.00 — Prototipe terpadu (konsolidasi) · ±6 kartu
1. `ReportService` + `GET /api/cases/{id}/report` (HTML siap cetak: tiga basis, bukti tidak teramati, batas klaim).
2. Lengkapi halaman §AC yang tersisa + halaman laporan.
3. Dokumen `docs/` §AE (architecture, setup, data_dictionary, rule_authoring, test_protocol, sample_selection, simulator_safety_contract, changelog).
4. Regresi penuh + `claim-auditor` + `forensic-integrity-reviewer` + `/security-review`.
5. Paket agen PyInstaller (K5) + panduan pasang di laptop pemeriksa.
6. Tag `v1.00` → rencana VPS lewat `/plan-milestone`.

## Boleh dipangkas bila jadwal tertinggal (tanpa amandemen core)

1. Artefak `OPTIONAL` (G1-B4…B6, G2-C2/C4/C6, G3-D3/D7): tidak diuji Tier-2 (§11.1 butir 2 mengizinkan).
2. Koleksi Bruno, polesan UI di luar wireframe DGM-09, ekspor PDF laporan (HTML cetak cukup).
3. Paket PyInstaller → pindah ke jalur VPS setelah v1.00 (agen tetap jalan sebagai `python -m`).
4. `K05-P03` (flow lab): bila capture lab tidak tersedia, profil tetap dievaluasi dan dilaporkan
   `insufficient_evidence` apa adanya — bukan dihapus.

⛔ **Tidak boleh dipangkas:** 5 keluarga/16 profil, kelas skenario A–F, 20 authoring + 8 holdout, freeze sebelum
holdout, baseline manual tersegel, uji konsistensi, keterlacakan dua arah, 3 kategori sampel.

## Data OPEN → ditutup di mana

| Data OPEN | Ditutup |
|---|---|
| Versi Android A10 → API AVD #2 | v0.90.7 |
| Perintah ADB final tiap operasi | v0.45 (G1), v0.70 (G2/G3) untuk API 36; varian API lain teramati di v0.90.8 |
| Status Tier-2 per lingkungan | v0.45, v0.70 (formatif, AVD #1); v0.90.8 (konfirmatif, 3 lingkungan) |
| Mekanisme `denied`/`unsupported` terkendali | v0.45/v0.70 bila teramati di AVD #1; v0.90.8 (mis. operasi pada API lain, izin shell ditolak di A10). Kode sudah diuji fixture v0.30 |
| Package/varian/hash simulator, `ground_truth.json`, endpoint lokal, pengendali | v0.80 |
| Aplikasi S-B | v0.80 |
| Kandidat & 3 APK S-C + SHA-256 | v0.90 |
| Katalog & hash 8 holdout | v0.90 |
| Distribusi agen | v1.00 (K5); deployment VPS setelah v1.00 |
