---
name: wrap-up
description: Tutup sesi kerja - ringkas perubahan, perbarui docs/progress.md, catat data OPEN dan status sinkronisasi remote, lalu tawarkan commit dan /sync.
---

# /wrap-up — tutup sesi

1. Kumpulkan apa yang berubah sesi ini: `git status --short`, `git diff --stat`,
   `git log --oneline origin/<branch>..HEAD`.
2. Perbarui `docs/progress.md` (hanya file ini; ⛔ jangan mengubah CLAUDE.md / `.claude/**`):
   - **Posisi saat ini**: increment + milestone aktif, branch aktif.
   - **Selesai sesi ini**: butir singkat dengan nama file/fitur.
   - **Langkah berikutnya**: 1–5 butir konkret, berurutan.
   - **Data OPEN**: tandai yang sudah terisi (dengan sumbernya), tambahkan `TODO(open-data)` baru yang
     muncul dari kode.
   - **Sinkronisasi remote**: apakah branch sudah di-push ke `origin` (GitLab mengikuti via
     mirror); bila sesi cloud, tulis branch `claude/*` yang perlu `/integrate` dari mesin lokal.
   - **Catatan diagram/naskah**: perubahan kode yang berdampak ke DGM-xx atau BAB III.
   - Tulis tanggal dengan format `YYYY-MM-DD`.
3. Laporkan ke user: ringkasan, test yang dijalankan + hasilnya (termasuk yang gagal / tidak bisa
   dijalankan), dan hal yang butuh keputusan user.
4. Tawarkan commit (`docs(progress): ...` atau sesuai isi) dan `/sync`. Jangan commit/push tanpa
   persetujuan user.
