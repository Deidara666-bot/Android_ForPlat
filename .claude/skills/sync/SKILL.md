---
name: sync
description: Push branch aktif (dan tag baru) ke GitHub (origin) dan pastikan GitLab ikut ter-update - lewat mirror otomatis (default) atau push ke remote gitlab bila remote itu ada. Verifikasi hasilnya.
argument-hint: "[nama-branch] (opsional, default branch aktif)"
---

# /sync — GitHub (origin) → GitLab

Ikuti `.claude/rules/git-workflow.md`. Branch sasaran: `$ARGUMENTS` bila diisi, selain itu branch aktif.

1. **Pra-cek**
   - `git status --porcelain` → bila ada perubahan belum di-commit, tampilkan dan tanyakan user
     (jangan commit otomatis kecuali user memang meminta commit di permintaan yang sama).
   - `git fetch --prune origin`.
   - Bila `origin/<branch>` punya commit yang tidak ada di lokal (`git log --oneline HEAD..origin/<branch>`):
     gabungkan dulu dengan `git merge --no-ff --no-edit origin/<branch>` (konflik → abort, tanya user).
     ⛔ Jangan force-push.
2. **Push ke GitHub**: `git push -u origin <branch>`. Gagal → berhenti dan laporkan output-nya.
   Tag baru di HEAD yang belum ada di origin: `git push origin <tag>` per tag (⛔ bukan `--tags`).
3. **GitLab** — tentukan mode:
   - **mirror** (tidak ada remote `gitlab`, default proyek ini): GitLab menarik dari GitHub otomatis.
     ⛔ Jangan push ke GitLab. Bila `git config --get forplat.gitlabUrl` terisi, verifikasi:
     `git ls-remote <url> refs/heads/<branch>` — SHA sama → OK; beda → sebutkan bahwa mirror belum
     menyusul (biasanya beberapa menit) dan tidak perlu tindakan; gagal auth → sebutkan cek di web GitLab.
   - **push** (remote `gitlab` ada): `git push gitlab <branch>` (+ tag yang sama). Gagal → laporkan,
     jangan ubah history.
4. **Verifikasi & laporan**: `git rev-parse <branch> origin/<branch>` harus sama. Laporkan singkat:
   branch, SHA pendek, tag yang di-push, mode GitLab + hasil verifikasinya, dan bahwa pipeline GitLab CI
   akan berjalan dari commit ini.

⛔ Tanpa `--force`, `--force-with-lease`, `+refspec`, atau `--no-verify`.
