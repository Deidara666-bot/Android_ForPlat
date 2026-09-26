---
name: rule-change
description: Protokol aman untuk mengubah YAML keluarga APKF atau entri basis pengetahuan - cek apakah perubahan diizinkan saat authoring, naikkan versi, jalankan validator dan test, lalu commit dengan alasan dan rujukan.
argument-hint: "<APKF-K0x[-P0y] atau KB-...> <deskripsi perubahan>"
disable-model-invocation: true
---

# /rule-change — ubah aturan APKF / KB dengan disiplin

Permintaan: `$ARGUMENTS`. Aturan lengkap: `.claude/rules/rules-kb-yaml.md`, `01_BREAKDOWN` §14.3, §16.

1. **Cek status** YAML target. Bila `frozen_for_holdout` dan holdout sudah dibuka → ⛔ berhenti.
   Jelaskan ke user bahwa perubahan hanya sah sebagai versi baru dan kasus holdout kehilangan statusnya.
2. **Klasifikasikan perubahan**:
   - *Diizinkan tanpa amandemen core*: jalur parser/operasi setelah Tier-2; nama field `context_json`
     tanpa ubah makna; batas waktu `case_configured`; profil ekuivalen untuk sumber yang lolos Tier-2;
     koreksi teknis yang tidak menaikkan `claim_level`.
   - *Butuh amandemen core*: keluarga, arti profil, fakta wajib, kelas epistemik, peran kondisi,
     agregasi, batas klaim, efek eksklusioner, gerbang rekonstruksi → ⛔ berhenti, jelaskan dampaknya,
     dan minta keputusan user. Jangan mengubah YAML.
3. Tampilkan diff yang diusulkan + dampak ke test/skenario/diagram sebelum menulis.
4. Terapkan: naikkan `version` keluarga (dan profil bila dipisah), jaga `reference_ids` tetap resolve
   ke `sources.yaml`.
5. Jalankan loader/validator aturan + seluruh test lapisan riset (`python -m pytest` di `backend/`).
   Semua harus lulus; laporkan hasil apa adanya.
6. Commit dengan format body di `rules-kb-yaml.md` (Family/profile, versi lama → baru, Change class,
   Rationale, References). Tambahkan entri ringkas di `docs/changelog.md`.
7. Bila perubahan menyentuh isi diagram `DGM-06`/`DGM-07`/`DGM-08`, tambahkan catatan di
   `docs/progress.md`.
