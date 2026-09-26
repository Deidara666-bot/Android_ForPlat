---
name: milestone
description: Buat tag milestone (v0.05 ... v1.00) atau tag freeze aturan (rules-vN-freeze) di main setelah kriteria terpenuhi, lalu push tag ke GitHub dan GitLab.
argument-hint: "<tag>  contoh: v0.05 | v0.30 | rules-v1-freeze"
disable-model-invocation: true
---

# /milestone — tag milestone / freeze

Tag: `$ARGUMENTS`. Daftar milestone dan artinya: `02_ARSITEKTUR` §AJ.3 (cek ringkasannya di
`docs/progress.md`).

1. Pastikan berada di `main`, working tree bersih, dan `main` sama dengan `origin/main`.
2. Pastikan tag belum ada (`git tag -l $ARGUMENTS`, juga di remote). Tag yang sudah ada ⛔ tidak ditimpa.
3. **Cek kriteria milestone** — tampilkan checklist lalu verifikasi satu per satu:
   - `v0.05`: checklist smoke test `02_ARSITEKTUR` §AK (git, python 3.13, venv, node 24, AVD API 36
     boot, `adb devices -l`, PostgreSQL, `/api/health`, `/docs`, Vite, Alembic).
   - milestone lain: kriteria "yang dapat dijalankan dan diverifikasi" di §AJ.2 untuk *increment* terkait.
   - `rules-v<N>-freeze`: ≥20 kasus authoring lulus, semua YAML berstatus `frozen_for_holdout`,
     `reference_ids` terverifikasi, `freeze_manifest.json` ada dan hash-nya cocok, kriteria + vektor
     holdout sudah disegel (`01_BREAKDOWN` §16, `02_ARSITEKTUR` §AG.11).
   Hal yang tidak bisa diverifikasi Claude (mis. AVD di laptop) → minta konfirmasi eksplisit user.
   Bila ada kriteria belum terpenuhi → berhenti, jangan buat tag.
4. Tambahkan entri di `docs/changelog.md` (buat bila belum ada) dan perbarui `docs/progress.md`
   (milestone tercapai, milestone berikutnya). Commit `docs(progress): reach $ARGUMENTS`.
5. `git tag -a $ARGUMENTS -m "<deskripsi milestone>"`.
6. Push commit + tag lewat urutan `/sync`: `origin` dulu, lalu `gitlab`. Verifikasi tag ada di kedua remote.
