---
name: finish-branch
description: Selesaikan branch kerja - jalankan pemeriksaan, merge --no-ff ke main, push ke origin lalu gitlab, dan rapikan branch.
argument-hint: "[nama-branch] (opsional, default branch aktif)"
disable-model-invocation: true
---

# /finish-branch — merge ke main dan sinkronkan

Branch: `$ARGUMENTS` bila diisi, selain itu branch aktif (tidak boleh `main`).

1. `git status --short` harus bersih. Bila tidak, berhenti dan tanyakan user.
2. **Pemeriksaan** (CLAUDE.md §7) untuk setiap folder yang berubah di branch ini
   (`git diff --stat main...<branch>`): ruff + pytest untuk `agent/`/`backend/`, `npm run lint` +
   `npm run build` untuk `frontend/`, gradle untuk `android-test-apps/`. Bila ada yang gagal → berhenti,
   laporkan output-nya. Bila tidak bisa dijalankan (tool/env belum ada), katakan terus terang dan minta
   keputusan user.
3. Jalankan subagent `claim-auditor` dan (bila `agent/`, `backend/app/api`, penyimpanan bukti, atau
   `.env*` tersentuh) `forensic-integrity-reviewer` atas `git diff main...<branch>`. Temuan blocking harus
   diperbaiki dulu.
4. `git switch main` → `git pull origin main` → `git merge --no-ff <branch>`.
   Konflik merge → selesaikan dengan hati-hati; bila kedua sisi mengubah logika yang sama, tanyakan user.
5. Jalankan skill `/sync` untuk `main`.
6. Hapus branch lokal `git branch -d <branch>`; hapus di remote (`git push origin --delete <branch>` lalu
   `git push gitlab --delete <branch>`) **hanya bila user setuju**.
7. Perbarui `docs/progress.md` (pekerjaan selesai, langkah berikutnya) dan commit sebagai
   `docs(progress): ...` bila ada perubahan, lalu `/sync` lagi.
