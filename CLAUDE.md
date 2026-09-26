# CLAUDE.md — Android_ForPlat

Platform investigasi forensik Android berbasis web dengan *Rule-Based Evidence Correlation*
(APKF — Aturan Pola Korelasi Forensik). Proyek skripsi, dikerjakan solo, dikembangkan dengan
model **Incremental** (5 *increment*, urutan terkunci).

Status kerja terkini (milestone aktif, langkah berikutnya, data yang masih terbuka) ada di file
di bawah ini. File itu **boleh dan wajib** diperbarui; file aturan ini tidak.

@docs/progress.md

---

## 1. Sumber kebenaran & urutan otoritas

Dokumen kanonik ada di `context/` dan berstatus **FROZEN**. Pakai berkas dengan versi tertinggi:

| Berkas | Isi yang dirujuk saat coding |
|---|---|
| `context/02_ARSITEKTUR_*` | stack & versi (§C, §E), agen (§U), operasi akuisisi (§V), integritas (§W), modul backend (§X), model data (§Y), kontrak mesin aturan (§Z), basis data (§AA), API (§AB), UI (§AC), keamanan (§AD), struktur repo (§AE), scaffold (§AF), git (§AG), milestone (§AJ) |
| `context/01_BREAKDOWN_*` | pipeline (§3), label epistemik (§4.4a), istilah Indonesia (§4.7), status ketersediaan (§8), matriks Tier-1 (§9), protokol Tier-2 (§11.1), KF/KNF (§11.2), KB (§12), semantik 3-keadaan (§13), **YAML 5 keluarga APKF (§14.2)**, batas perubahan (§14.3), validasi (§15–§18) |
| `context/00_SESSION_STARTER_*` | ringkasan keputusan, prinsip epistemik (§5), instruksi AI (§13) |
| `context/BAB_0*_WORKING_*` | kendali naskah skripsi — bukan spesifikasi kode |

Jika ada konflik: **(1)** keputusan langsung user di sesi berjalan → **(2)** judul → **(3)** naskah
BAB I/II `DRAFT FINAL` → **(4)** `01_BREAKDOWN` → **(5)** `02_ARSITEKTUR` → **(6)** `00_SESSION_STARTER`
→ **(7)** dokumen `WORKING` → **(8)** asumsi AI (paling rendah).

- ⛔ Jangan pernah mengedit isi `context/`. Kalau kode butuh sesuatu yang bertentangan dengan core,
  **berhenti dan tanya user** — perubahan core adalah amandemen versi baru, bukan tambalan diam-diam.
- Jangan membaca dokumen `context/` utuh setiap sesi (ratusan KB). Buka **seksi yang relevan** saja
  memakai nomor seksi di tabel di atas.
- Jangan mengisi data yang masih OPEN (versi Android Galaxy A10, hash sampel, nama package simulator,
  hasil Tier-2, dsb.) dengan tebakan. Tulis `TODO(open-data): ...` dan catat di `docs/progress.md`.

## 2. Arsitektur yang tidak boleh digeser

```
Pemeriksa → React Web → FastAPI (REST + WebSocket) → PostgreSQL + filesystem bukti mentah
                              ↕ WebSocket/HTTP
                        Agen lokal (Python) → ADB resmi → AVD / perangkat dummy
```

- **Agen = lapisan eksekusi/akuisisi. Backend = lapisan analisis/riset.** Agen tidak melakukan
  penalaran malware, parsing semantik, atau evaluasi aturan.
- Pipeline tetap: `Raw Evidence → Parser → Artifact → Normalizer → NormalizedEvent → APKF evaluation
  → CorrelationFinding → Reconstruction → InvestigationHypothesis → Dashboard/Report`.
- Stack terkunci: Python 3.13 (agen + backend), FastAPI, SQLAlchemy 2, Alembic, PostgreSQL 18,
  React 19 + TypeScript + Vite, YAML untuk aturan/KB, Kotlin untuk simulator aman.
- ⛔ Jangan menambah Kafka, Redis, Celery, RabbitMQ, Neo4j, Elasticsearch, Kubernetes, MinIO, ML
  framework, atau design system berat. Dependency baru apa pun → tanya user dulu.
- ⛔ Tidak ada skor, bobot, ambang, peringkat, atau probabilitas (`D-6`). Keluaran aturan hanya
  `matched` · `not_matched` · `insufficient_evidence`.

## 3. Invarian forensik & epistemik (WAJIB, ditegakkan di kode dan test)

1. Kapabilitas ≠ perbuatan. `permission granted` ≠ akses terjadi; Accessibility aktif ≠ disalahgunakan;
   SMS ada ≠ dibaca aplikasi; aktivitas jaringan ≠ eksfiltrasi; string URL di APK ≠ endpoint dihubungi;
   metadata installer ≠ kanal penipuan.
2. **Bukti hilang = `UNKNOWN`, bukan `FALSE`.** Hanya `availability_status=acquired` + parse sukses +
   cakupan selector lengkap yang boleh menghasilkan `FALSE`, dan `FALSE` wajib ditopang fakta negatif
   eksplisit (`predicate_value: false`).
3. *Current state* tidak boleh diubah menjadi *historical event*. Bila waktu kejadian tidak diketahui:
   `event_time = null`, pakai `observed_at`. Jangan mengarang timestamp.
4. Setiap `NormalizedEvent` punya tepat satu `epistemic_class` (`identity_attribute`, `capability_state`,
   `execution_observed`, `data_present`) yang ditentukan penormalisasi dari `event_type` lewat tabel
   tetap. Enum ini tertutup.
5. Bukti mentah **imutabel**: SHA-256 di agen, re-hash di server, mismatch ditolak, parser hanya membaca.
6. Operasi ADB **allowlist berbasis operation ID**. ⛔ Tidak ada `adb shell <string dari backend/user>`,
   tidak ada `shell=True`, tidak ada rooting/exploit/bypass lockscreen.
7. Keterlacakan dua arah wajib utuh: evaluasi → kondisi → fakta → artefak → bukti mentah → sesi akuisisi,
   dan evaluasi → elemen aturan → rujukan `KB_Source`.
8. Bahasa keluaran dibatasi `claim_level`. ⛔ Jangan pernah menulis "malware detected", "aplikasi
   penipuan terbukti", "eksfiltrasi", atau yang setara di kode, UI, laporan, test, maupun commit.

Rincian per lapisan ada di `.claude/rules/` (dimuat otomatis sesuai folder yang disentuh).

## 4. Keamanan sampel & data

- ⛔ APK malware nyata (kategori S-C) **tidak pernah** dipasang, dijalankan, dimuat ke AVD/perangkat,
  diunggah ke layanan online, atau di-commit. Hanya analisis statis di VM terisolasi.
- ⛔ Simulator aman (S-A) tidak boleh punya perilaku berbahaya: tanpa pencurian data, impersonasi
  merek, stealth, obfuscation, auto-grant, komunikasi pihak ketiga, atau persistensi tersembunyi.
- ⛔ Jangan commit: `.env`, token, keystore, bukti mentah (`var/`, `raw_outputs/`), dump SMS/kontak
  asli, dump database, `*.apk`, `*.pcap`. Data uji selalu sintetis.

## 5. Alur kerja Git — otomatis dari Claude Code

```
Claude Code (lokal: C:\mrtz\FORENSIC PLATF\Android_ForPlat) → Git lokal
      └─ push → origin (GitHub, sumber utama) ──mirror otomatis──→ GitLab (CI/CD)
Sesi cloud claude.ai → branch origin/claude/* ──/integrate di lokal──→ main
```

- **User tidak menjalankan perintah git.** Claude yang menjalankan semuanya; user cukup review, testing,
  dan hal di luar terminal (download/instal aplikasi, login, AVD, perangkat fisik).
- Hook `SessionStart` (`.claude/hooks/session-start.sh`, aktif bila terdaftar di `.claude/settings.json`)
  menyiapkan git config per-clone dan mencetak laporan `[forplat session-start]`. Tanpa hook itu, user
  bisa menjalankan `/setup`. Dari laporan tersebut lakukan **housekeeping** bila aman, lalu laporkan singkat:
  - ada `origin/claude/*` yang belum masuk `main` → `/integrate`;
  - `main` lokal lebih maju dari `origin/main` → `/sync main`;
  - aman = working tree bersih, merge tanpa konflik, pemeriksaan tidak gagal. Selain itu tanya user dulu.
- GitLab: mode **mirror** (default) → cukup push ke `origin`; ⛔ jangan tambah remote/push ke GitLab.
  Mode **push** hanya bila remote `gitlab` ada. Semua push lewat alur `/sync`.
- ⛔ Jangan pernah edit/commit langsung lewat web UI GitHub atau GitLab.
- Branch: `main` + `feature/*`, `fix/*`, `experiment/*`, `docs/*` (sesi cloud: `claude/*`).
  Merge ke `main` pakai `--no-ff --no-edit`. `main` harus selalu bisa jalan dan bebas secret.
- Commit gaya Conventional: `feat|fix|refactor|test|docs|chore|experiment(scope): ringkasan`,
  bahasa Inggris, satu tujuan logis per commit. Commit/push dilakukan saat user meminta, lewat skill,
  atau sebagai housekeeping di atas.
- ⛔ Tanpa `push --force`, `reset --hard`, rebase branch yang sudah di-push, atau hapus tag, kecuali
  user minta eksplisit.
- Skill: `/setup`, `/integrate`, `/sync`, `/new-branch`, `/finish-branch`, `/milestone`, `/rule-change`,
  `/wrap-up`. Detail: `.claude/rules/git-workflow.md`.

## 6. Cara kerja per tugas

1. Cek `docs/progress.md` → tahu *increment*/milestone aktif. Jangan lompat urutan *increment*:
   mesin aturan tidak dibangun sebelum fakta ternormalisasi ada; fakta tidak ada sebelum akuisisi + parser.
2. Bangun **vertical slice** tipis dulu, baru melebar ke target tree `02_ARSITEKTUR` §AE. Jangan
   membuat file kosong hanya karena ada di target tree.
3. Setiap perubahan disertai test di lapisan yang sama. Pengujian terjadi di **setiap** *increment*.
4. Sebelum menyatakan selesai, jalankan pemeriksaan (lihat §7) dan laporkan hasilnya apa adanya —
   termasuk yang gagal atau tidak bisa dijalankan.
5. Di akhir sesi yang mengubah status proyek, perbarui `docs/progress.md` (skill `/wrap-up`).

## 7. Perintah pemeriksaan

Jalankan dari folder masing-masing, di dalam venv/`node_modules` proyek (bukan global):

| Area | Perintah |
|---|---|
| agen / backend | `python -m ruff check .` · `python -m ruff format --check .` · `python -m pytest` · (opsional) `python -m mypy app` / `src` |
| migrasi DB | `alembic upgrade head` pada DB dev, lalu `alembic check` |
| frontend | `npm run lint` · `npm run build` |
| simulator Android | `./gradlew assembleAuthoringDebug` (atau varian terkait) · `./gradlew test` |
| database dev | `docker compose up -d postgres` |

Kalau folder/perintah belum ada karena scaffold belum dibuat, katakan itu — jangan pura-pura lulus.

## 8. Lingkungan

- Mesin utama: Windows 11 (Lenovo IdeaPad Flex 5i, 16 GB), PowerShell + Git Bash. Path proyek
  mengandung spasi → **selalu kutip path**, dan jangan hardcode path absolut di kode/skrip.
- Venv terpisah: `agent/.venv` dan `backend/.venv`. Jangan `pip install` global.
- Sesi Claude Code di cloud (claude.ai/code) tidak punya ADB, AVD, atau Docker: kerjakan kode + test
  unit saja, push ke branch `claude/*` yang ditugaskan di `origin`. Sesi lokal berikutnya membawanya ke
  `main` lewat `/integrate` secara otomatis.

## 9. Bahasa & istilah

- Kode, identifier, nama tabel/field, commit message: **Inggris**, mengikuti nama teknis core
  (`event_type`, `epistemic_class`, `RuleProfileEvaluation`, `RuleConditionFact`, dst. — jangan
  diganti sinonim).
- Dokumentasi di `docs/` dan teks UI untuk Pemeriksa: **Indonesia**, memakai padanan terkunci
  `01_BREAKDOWN` §4.7 (mis. *fakta ternormalisasi*, *terpenuhi / tidak terpenuhi / bukti tidak memadai*,
  *diperoleh / tidak tersedia / ditolak / tidak didukung / gagal*, *kapabilitas*, *pemeriksa*).
- Balas user dalam bahasa yang user pakai.

## 10. Kebijakan perubahan file aturan

File berikut dirancang **tetap** sepanjang pengembangan: `CLAUDE.md`, `.claude/rules/*`,
`.claude/skills/*`, `.claude/agents/*`, `.claude/hooks/*`, `.claude/settings.json`, `.githooks/*`.
Status, progres, dan data yang berubah-ubah **hanya** masuk `docs/progress.md` (dan nanti
`docs/changelog.md`). Aturan ini hanya direvisi bila core `context/` naik versi karena amandemen
resmi, atau user memutuskannya secara eksplisit — jangan mengubahnya atas inisiatif sendiri.
