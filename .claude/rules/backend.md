---
paths:
  - "backend/**"
---

# Aturan backend (`backend/`)

Dasar: `02_ARSITEKTUR` §K, §S.1, §T, §W, §X, §Y, §AA, §AB, §AD, §AE (pohon `backend/`).

## Struktur & lapisan

- Ikuti pohon §AE: `app/core`, `app/api/routes`, `app/ws`, `app/db`, `app/models`, `app/schemas`,
  `app/services`, `app/parsing`, `app/normalization`, `app/research`, `app/reporting`.
- Route tipis → service → model. Tidak ada query SQL atau logika bisnis di route.
- Service **engineering** (Auth, Agent, Case, Device, Acquisition, EvidenceStorage, Integrity, Audit,
  WebSocketConnectionManager, Report) dipisah dari service **riset** (ParserRegistry, Artifact,
  Normalization, KnowledgeBaseLoader/Validator, RuleLoader/Validator, RuleEngine, CorrelationEngine,
  HypothesisBuilder, Traceability). Aturan riset rinci: `research-engine.md`.

## Data & migrasi

- SQLAlchemy 2 gaya typed (`Mapped[...]`, `mapped_column`). Pydantic v2 untuk schema API.
- Nama entitas mengikuti core persis: `Evidence`, `Artifact`, `NormalizedEvent`, `CorrelationRun`,
  `RuleFamilyEvaluation`, `RuleProfileEvaluation`, `RuleConditionResult`, `RuleConditionFact`,
  `CorrelationFinding`, `ReconstructionRun`, `ReconstructionFinding`, `InvestigationHypothesis`,
  `KB_Source`, `RuleMetadata`, `RuleReference`, `RuleElementReference`, dst. (§AA, §AA.2).
  ⛔ Jangan menghidupkan kembali `FindingEvidence` atau `RuleEvaluation` tunggal (sudah dicabut).
- Enum tertutup (`epistemic_class`, `availability_status`, `evidence_state`, `temporal_semantics`,
  keadaan kondisi, `outcome`, `evaluation_status`, `claim_level`, `reference_role`, `evidence_mode`,
  `run_purpose`, status YAML) didefinisikan **sekali** di `app/core/constants.py` dan dipakai ulang
  oleh model, schema, loader, dan test. ⛔ Jangan menambah nilai enum tanpa keputusan user.
- Kolom wajib dari §Y dan §AA.2 tidak boleh dijadikan nullable demi kemudahan
  (`epistemic_class` NOT NULL; `outcome` memang nullable untuk `skipped_not_applicable`).
- Setiap perubahan skema lewat **migrasi Alembic baru**. ⛔ Jangan mengedit migrasi yang sudah
  ter-commit; buat migrasi lanjutan.
- Waktu disimpan `timestamptz` (UTC) + timezone perangkat dicatat terpisah. `event_time` boleh NULL.
- `InvestigationHypothesis` imutabel per `CorrelationRun` — tidak ada endpoint update/edit.

## API & WebSocket (§AB)

- REST di bawah `/api/...` sesuai daftar §AB (health, auth, cases, agents, devices, acquisitions,
  evidence upload, artifacts, events, analyze, evaluations, findings, reconstructions, report).
- `/evaluations` mengembalikan **semua** evaluasi (termasuk `not_matched`, `insufficient_evidence`,
  `skipped_not_applicable`, konflik). `/findings` hanya temuan dari profil `matched`.
- WebSocket `/ws/agent` dan `/ws/dashboard` hanya untuk heartbeat, notifikasi job, progress,
  completion/error. Bytes bukti lewat HTTP upload.
- Backend ⛔ tidak pernah mengirim string perintah shell ke agen — hanya operation ID + parameter.

## Unggahan & penyimpanan bukti

- Validasi ukuran, tipe, dan nama berkas; nama berkas di disk dibuat server (ID/hash), bukan dari klien.
- Resolusi path selalu dicek tetap di bawah `EVIDENCE_ROOT` (cegah path traversal).
- Re-hash SHA-256 server, bandingkan dengan `sha256_agent`, tolak bila beda, catat `AuditLog`.
- Berkas yang sudah disimpan dibuat read-only; tidak ada endpoint yang menimpa/menghapus bukti mentah.

## Konfigurasi

`pydantic-settings` dari `.env`: `APP_ENV`, `DATABASE_URL`, `EVIDENCE_ROOT`, `JWT_SECRET`, `CORS_ORIGINS`.
Default aman; tidak ada secret hardcoded.

## Test

- `pytest` + `httpx`/`TestClient`; test DB terpisah dari DB dev.
- Setiap route punya test sukses + gagal (auth, validasi). Upload punya test mismatch hash dan
  path traversal.
