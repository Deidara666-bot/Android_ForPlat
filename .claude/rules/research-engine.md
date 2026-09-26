---
paths:
  - "backend/app/parsing/**"
  - "backend/app/normalization/**"
  - "backend/app/research/**"
  - "backend/app/reporting/**"
  - "backend/tests/**"
---

# Aturan lapisan riset: parser → penormalisasi → mesin aturan → rekonstruksi

Ini inti kebaruan penelitian. Kontrak diambil dari `02_ARSITEKTUR` §Y.3–§Z.1, §AA.1–§AA.2 dan
`01_BREAKDOWN` §4.4a, §6, §13, §14. Bila ragu, buka seksi tersebut — jangan menebak semantik.

## Parser (`app/parsing/`)

- Satu parser per sumber mentah (`package_state`, `usage_stats`, `settings_state`,
  `sensitive_provider`, `network_stats`, `apk_static`), terdaftar di `registry.py`, punya
  `parser_name` + `parser_version` yang tersimpan di setiap `Artifact`.
- Parser hanya membaca bukti mentah. Keluaran tidak dikenali → `parse_status` gagal + `parse_note`,
  bukan exception yang menelan data atau tebakan nilai.
- Fixture test parser = keluaran ADB **sintetis/dari AVD uji** yang disimpan di `backend/tests/fixtures/`
  (sudah disanitasi). Perubahan format lintas versi Android ditangani eksplisit per API level.

## Penormalisasi (`app/normalization/`)

- `event_type` hanya dari katalog tertutup `02_ARSITEKTUR` §Y.3.1a. Event baru → tanya user.
- `epistemic_class` diisi **deterministik** dari tabel pemetaan `event_type → epistemic_class` yang tetap;
  tidak pernah dari aturan, pengguna, atau heuristik per kasus. Tepat satu nilai, NOT NULL.
- Fakta yang menopang dua jenis klaim **dipecah** jadi dua fakta, bukan satu fakta berlabel ganda.
- `evidence_state` dari `availability_status` (§Y.3.6):
  `acquired` → `observed_true`/`observed_false` sesuai isi; `unavailable`/`denied`/`unsupported`/`failed`
  → `unknown_unavailable`. ⛔ Empat status non-acquired tidak pernah menjadi FALSE.
  `availability_status` asli tetap disimpan apa adanya untuk pelaporan per lingkungan.
- Fakta negatif eksplisit (`predicate_value: false`) **hanya** dibuat untuk predikat tertutup yang
  cakupan sumbernya lengkap (mis. daftar permission target pada package yang terurai penuh).
  Sumber tak lengkap → tidak ada fakta negatif.
- `temporal_semantics`: `historical_event` · `current_state` · `aggregated_window` · `unknown`.
  Snapshot = `current_state` dengan `observed_at`; ⛔ jangan mengisi `event_time` dari waktu akuisisi.
- Nilai asli (permission, komponen, action, bucket, endpoint) tetap disimpan di `object_value` /
  `context_json`, dan `artifact_id` selalu terisi.
- `synthetic_exclusion_marker_observed` ⛔ tidak pernah dibuat penormalisasi produksi — hanya oleh
  *fixture adapter* pengujian.

## Pemuat & validator aturan/KB (`app/research/rules`, `app/research/knowledge_base`)

Aturan **gagal dimuat** (bukan warning) bila salah satu pemeriksaan §Z.0 gagal:

- field keluarga lengkap: `schema_version`, `family_id`, `version`, `status`, `incident_scope`,
  `reference_ids`, `aggregation`, `unknown_handling`, `conflict_handling`;
- `profile_id` unik global dan berawalan `family_id`;
- tiap profil punya `applicability.evidence_modes`, `applicability.run_purposes`, `claim_level`,
  `subject_binding`, `time_binding`, empat daftar peran (`required`/`optional`/`contextual`/`exclusionary`),
  dan `output`;
- tiap kondisi punya `condition_id`, `fact`, `source_group`, `expects_epistemic_class`, `operator`,
  dan parameter operatornya; `fact` terdaftar di katalog §Y.3.1a dan **kelasnya identik** dengan
  `expects_epistemic_class`;
- `reference_ids` tidak kosong, tanpa duplikat, dan setiap ID resolve ke `KB_Source` aktif;
- profil tidak meng-override `unknown_handling`/`conflict_handling` keluarga;
- profil `validation_only` ditolak untuk `run_purpose=production` atau `evidence_mode=apk_static`;
- `any_of` hanya berisi event type yang setara semantik **dan** `claim_level` sama;
- status YAML: loader dev menerima `design_baseline` + `authoring_candidate`; run `holdout` hanya
  `frozen_for_holdout` dengan hash cocok `freeze_manifest.json`; run `production` menolak `design_baseline`.

Kunci rujukan elemen dikompilasi deterministik: keluarga = `family_id`, kondisi =
`profile_id.condition_id`; `reference_role` dari label baku `KB_Source` kecuali override eksplisit.

## Mesin aturan (`rule_engine.py`)

Urutan evaluasi per profil (§Z.0.1):
`evidence_mode + run_purpose → saring applicability → ikat subject → ikat window → pilih fakta
(event_type + filter) → cek availability & cakupan parse → TRUE/FALSE/UNKNOWN`.

- Operator baseline **hanya**: `exists`, `equals`, `in`, `greater_than`, `delta_greater_than`,
  `overlaps_window`. Semantik FALSE per operator mengikuti §Z.0.1 / `01_BREAKDOWN` §13.2.1.
- `exists`/`equals`/`in` membaca `predicate_value`, bukan sekadar ada-tidaknya baris.
- Semua kondisi satu profil memakai `subject_binding` yang sama; ⛔ tidak menggabungkan lintas UID/package.
- Fakta valid yang bertentangan → kondisi `UNKNOWN` dengan `reason=conflicting_evidence`, semua fakta
  konflik tertelusur. ⛔ Mesin tidak memilih fakta yang "menguntungkan".
- Outcome profil: semua `required` TRUE → `matched`; ada `required` FALSE → `not_matched`;
  selain itu ada `required` UNKNOWN → `insufficient_evidence`. `optional`/`contextual` UNKNOWN → anotasi.
- Eksklusioner TRUE → outcome tetap dari kondisi wajib, `interpretation_status=constrained`, temuan
  diblokir dari rekonstruksi. Eksklusioner UNKNOWN → dicatat, tidak mengecualikan.
- Profil tidak berlaku → `evaluation_status=skipped_not_applicable`, `outcome=NULL`, keluar dari agregasi.
  Bukan keadaan keempat.
- Agregasi keluarga: ada profil `matched` → `matched`; semua `not_matched` → `not_matched`; selain itu
  `insufficient_evidence`; tak ada profil berlaku → `insufficient_evidence/no_applicable_profile`.
- Deterministik: urutan iterasi stabil (sort by ID), tanpa randomness, tanpa waktu sistem dalam logika
  keputusan. Masukan + versi aturan/KB/kode sama → keluaran semantik identik (`KNF-01`).

## Kewajiban pencatatan (§Z.1, §AA.1)

Urutan: buat `RuleProfileEvaluation` → tulis **setiap** `RuleConditionResult` (peran, operator,
`selector_json`, keadaan, alasan, `conflict_reason`) → hubungkan fakta via `RuleConditionFact` →
`RuleFamilyEvaluation` → maksimum satu `CorrelationFinding` per profil `matched`.

- Kondisi TRUE dan FALSE wajib punya ≥1 `RuleConditionFact`. Kondisi UNKNOWN punya **nol** fakta
  dan wajib punya alasan. ⛔ Dilarang membuat fakta semu.
- `not_matched`, `insufficient_evidence`, dan `skipped_not_applicable` tetap tersimpan lengkap, tanpa temuan.

## Rekonstruksi & hipotesis (`correlation_engine.py`, `hypothesis_builder.py`)

- `ReconstructionRun` hanya bila ada ≥2 temuan dari **keluarga berbeda** dengan subject key dan jendela
  waktu kompatibel. Beberapa profil satu keluarga ≠ beberapa keluarga.
- Urutan kejadian hanya bila ada ≥1 temuan `observed_activity`; kalau tidak, berhenti di temuan tingkat rendah.
- Temuan ber-`blocked_from_reconstruction` tidak dipakai menaikkan klaim.
- Kalimat hipotesis yang memerlukan `claim_level` lebih tinggi daripada seluruh temuan penopangnya
  ⛔ ditolak. Hipotesis tidak mengisi tahap yang tidak didukung dan selalu menyebut bukti yang tidak
  teramati (`missing_evidence`).
- Template kalimat berasal dari `output.summary_template` + `limitations` YAML, bukan teks bebas.

## Test wajib untuk lapisan ini

- Tujuh kelas skenario (`01_BREAKDOWN` §15.1): A positif, B near-miss, C benign, D1 opsional hilang,
  D2 wajib UNKNOWN, E konflik, F eksklusioner — masing-masing punya test unit mesin aturan.
- Loader: setiap aturan pemuatan di atas punya test "YAML rusak → gagal dimuat" (terutama
  `expects_epistemic_class` salah dan `reference_id` tak resolve).
- Keterlacakan: tiap kondisi TRUE/FALSE punya fakta; UNKNOWN nol fakta + alasan.
- Konsistensi: evaluasi yang sama dijalankan 3× menghasilkan hasil semantik identik (abaikan ID/timestamp).
- Anti-klaim-berlebih: tidak ada string output yang memuat "malware", "fraud detected", "exfiltrat",
  "terbukti menipu" di luar teks batasan (`limitations`).
