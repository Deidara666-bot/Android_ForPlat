---
name: new-branch
description: Mulai pekerjaan baru di branch sesuai konvensi (feature/fix/experiment/docs) dari main terbaru, dan cocokkan dengan increment aktif di docs/progress.md.
argument-hint: "<tipe>/<topik>  contoh: feature/agent-device-detection"
disable-model-invocation: true
---

# /new-branch — buka branch kerja baru

Argumen: `$ARGUMENTS` (format `<tipe>/<topik-kebab-case>`, tipe ∈ `feature`, `fix`, `experiment`, `docs`).

1. Validasi nama: tipe sah, topik huruf kecil + tanda hubung, bahasa Inggris. Bila tidak sah atau kosong,
   usulkan nama yang sesuai lalu tanyakan user.
2. `git status --short` → bila ada perubahan belum di-commit, berhenti dan tanyakan user.
3. `git switch main` → `git pull origin main`.
4. `git switch -c $ARGUMENTS`.
5. Baca `docs/progress.md`: sebutkan *increment*/milestone aktif dan apakah pekerjaan ini sesuai urutan
   *increment*. Bila pekerjaan melompati urutan (mis. mesin aturan sebelum ada fakta ternormalisasi),
   peringatkan user sebelum mulai.
6. Tampilkan rules yang relevan untuk folder yang akan disentuh (`.claude/rules/*.md`) dan rencana singkat
   (file yang akan dibuat/diubah + test yang akan ditulis). Jangan mulai coding sebelum user setuju bila
   rencananya menyentuh lebih dari satu lapisan.
