---
name: sync
description: Push branch aktif (dan tag baru) ke origin (GitHub) lalu ke gitlab (GitLab CI/CD), lalu verifikasi kedua remote menunjuk commit yang sama.
argument-hint: "[nama-branch] (opsional, default branch aktif)"
disable-model-invocation: true
---

# /sync — sinkronisasi GitHub (origin) → GitLab (gitlab)

Ikuti `.claude/rules/git-workflow.md`. Branch sasaran: `$ARGUMENTS` bila diisi, selain itu branch aktif.

1. **Pra-cek**
   - `git status --short` → bila ada perubahan belum di-commit, **berhenti** dan tanyakan user
     (jangan commit otomatis).
   - `git remote -v` → pastikan `origin` (GitHub) dan `gitlab` ada. Bila `gitlab` tidak ada
     (mis. sesi cloud), push ke `origin` saja, lalu catat di `docs/progress.md` bagian
     "Sinkronisasi remote" bahwa `gitlab` perlu disinkronkan dari mesin lokal.
2. **Cek divergensi**
   - `git fetch origin` dan `git fetch gitlab`.
   - Bila `origin/<branch>` atau `gitlab/<branch>` punya commit yang tidak ada di lokal
     (`git log HEAD..origin/<branch>`), **berhenti**: laporkan dan tanyakan user. Jangan force-push.
3. **Push berurutan**
   - `git push -u origin <branch>`; bila gagal → berhenti, laporkan, jangan lanjut ke gitlab.
   - `git push gitlab <branch>`.
   - Tag: `git tag --points-at HEAD` / tag lokal yang belum ada di remote → push per tag
     `git push origin <tag>` lalu `git push gitlab <tag>`. ⛔ Jangan `--tags` membabi buta, jangan hapus tag.
4. **Verifikasi**
   - `git rev-parse <branch> origin/<branch> gitlab/<branch>` → ketiganya harus sama.
   - Laporkan ringkas: branch, SHA, tag yang di-push, status tiap remote. Ingatkan bahwa pipeline GitLab
     akan berjalan dan hasilnya dicek di GitLab.

⛔ Tanpa `--force`, `--force-with-lease`, atau `--no-verify`.
