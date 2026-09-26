---
name: integrate
description: Gabungkan branch hasil sesi Claude Code cloud (origin/claude/*) ke main di mesin lokal, lalu push ke GitHub. Pakai saat session-start melaporkan cloud branch yang belum masuk main.
argument-hint: "[origin/claude/<nama>] (opsional, default semua yang belum di-merge)"
---

# /integrate — bawa hasil sesi cloud ke main

Menggantikan langkah manual `git fetch` + `git switch main` + `git merge --no-ff origin/claude/...`.
Aturan: `.claude/rules/git-workflow.md`.

1. **Pra-cek**
   - Harus di mesin lokal (bukan sesi cloud). Di sesi cloud → berhenti dan jelaskan.
   - `git status --porcelain` harus kosong. Bila ada perubahan: tampilkan daftarnya dan tanyakan user
     (commit dulu, stash, atau batal). ⛔ Jangan stash/buang otomatis.
   - `git fetch --prune origin`.
2. **Tentukan branch**: `$ARGUMENTS` bila diisi; selain itu semua `origin/claude/*` yang **bukan** ancestor
   `main` (`git merge-base --is-ancestor <ref> main` gagal). Tampilkan per branch: jumlah commit dan
   `git log --oneline main..<ref>`.
3. **Siapkan main**: `git switch main`, lalu `git merge --ff-only origin/main` bila origin/main lebih maju.
   Bila main lokal dan origin/main bercabang (keduanya punya commit unik) → `git merge --no-ff --no-edit
   origin/main` dulu.
4. **Merge** tiap branch: `git merge --no-ff --no-edit <ref>` (pesan default dipakai — tidak membuka editor).
   - Konflik → `git merge --abort`, laporkan berkas yang konflik, dan tanyakan user cara penyelesaiannya
     (kecuali konflik sepele di `docs/progress.md`: gabungkan kedua isi, lalu lanjut).
5. **Pemeriksaan**: jalankan pemeriksaan CLAUDE.md §7 untuk folder yang berubah (bila tool tersedia).
   Gagal → jangan push; laporkan.
6. **Push**: jalankan alur `/sync` untuk `main`.
7. **Rapikan**: tawarkan penghapusan branch remote yang sudah masuk main
   (`git push origin --delete claude/<nama>`); lakukan hanya bila user setuju.
8. Perbarui `docs/progress.md` (bagian "Sinkronisasi remote") dan laporkan ringkas.
