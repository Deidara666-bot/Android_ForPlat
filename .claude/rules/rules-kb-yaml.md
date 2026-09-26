---
paths:
  - "backend/app/research/rules/data/**"
  - "backend/app/research/knowledge_base/data/**"
  - "**/freeze_manifest.json"
---

# Aturan YAML APKF & basis pengetahuan

Dasar: `01_BREAKDOWN` §12, §14.0–§14.3, §16; `02_ARSITEKTUR` §Z.0, §AG.11–§AG.12.

## Sumber kebenaran

- Lima berkas `APKF-K01/family.yaml` … `APKF-K05/family.yaml` di
  `backend/app/research/rules/data/apk_fraud/` adalah **implementasi** YAML `design_baseline` pada
  `01_BREAKDOWN` §14.2 (16 profil: K01=3, K02=4, K03=3, K04=3, K05=3).
- Saat pertama dibuat, salin isi §14.2 **apa adanya** (struktur, ID, fakta, operator, nilai, rujukan,
  `limitations`). Jangan "merapikan", menambah profil, atau mengganti nama field.
- `reference_ids` harus cocok dengan registri `01_BREAKDOWN` §12.1 (`KB-AND-*`, `KB-MITRE-*`), dan
  entri tersebut ada di `knowledge_base/data/sources.yaml` dengan: judul, penerbit, URL, tanggal akses,
  `extracted_claim`, cakupan versi Android, `reference_role`, catatan mutu, `verification_status`.
- YAML aturan hanya berisi ID rujukan; detail bibliografis hanya di `KB_Source`. ⛔ Jangan menaruh
  sitasi teks bebas di YAML aturan.

## Batas perubahan selama *authoring* (§14.3)

Boleh tanpa amandemen core (tetap wajib commit + alasan):

- jalur parser/operasi akuisisi setelah hasil Tier-2;
- nama field di `context_json` yang tidak mengubah makna fakta;
- batas waktu yang memang `case_configured`;
- profil ekuivalen baru untuk sumber artefak yang lolos Tier-2;
- koreksi teknis yang **tidak menaikkan** `claim_level`.

⛔ **Wajib berhenti dan tanya user** (butuh amandemen core sebelum holdout) bila perubahan menyentuh:
keluarga, arti profil, fakta wajib, kelas epistemik, peran kondisi, agregasi, batas klaim, efek
eksklusioner, atau gerbang rekonstruksi.

## Siklus status & pembekuan

`design_baseline` → `authoring_candidate` → `frozen_for_holdout` (tidak pernah mundur untuk putaran uji yang sama).

1. Selama authoring: naikkan `version` keluarga setiap perubahan semantik yang diizinkan.
2. Setelah ≥20 kasus authoring lulus: verifikasi semua `reference_ids`, set status `frozen_for_holdout`,
   buat `freeze_manifest.json` berisi hash lima YAML, tabel pemetaan normalisasi, registri KB, commit
   kode, konfigurasi skenario, APK simulator, dan bundel holdout.
3. Commit, lalu tag `rules-v<N>-freeze` (lewat skill `/milestone`), push ke kedua remote.
4. ⛔ Setelah holdout dibuka, YAML beku tidak disentuh. Ketidaksesuaian holdout adalah **hasil (BAB IV)**,
   bukan alasan tuning. Perubahan hanya sebagai versi baru, dan kasus holdout kehilangan statusnya untuk
   versi itu.

## Commit perubahan aturan/KB

```
feat(rules): <ringkasan>

Family/profile: APKF-K0x / APKF-K0x-P0y (version a -> b)
Change class: <salah satu butir "boleh" §14.3>
Rationale: <alasan, mis. hasil Tier-2 api36 tanggal ...>
References: <KB-... atau berkas eksperimen>
```

## Larangan isi

- ⛔ Skor, bobot, ambang risiko, `scoring:`.
- ⛔ `INTERNET` permission sebagai kondisi wajib yang dianggap mencurigakan.
- ⛔ Allowlist nama package sebagai satu-satunya pengecualian benign.
- ⛔ `any_of` yang mencampur fakta tidak setara semantik atau `claim_level` berbeda.
- ⛔ Fixture `synthetic_exclusion_marker_observed` di YAML produksi — hanya disuntik harness uji.
