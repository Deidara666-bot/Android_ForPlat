---
name: plan-milestone
description: Susun berkas rencana milestone baru docs/dev/v0.XX.md (peta singkat + kartu ringkas) dari dokumen core, dalam format yang sama dengan v0.05-v0.40, lalu minta review user. Sebaiknya dijalankan dengan model besar.
argument-hint: "v0.XX  (contoh: v0.45)"
disable-model-invocation: true
---

# /plan-milestone — rencana milestone baru

Milestone: `$ARGUMENTS`. Contoh format: `docs/dev/v0.40.md`. Aturan format: `docs/dev/README.md`.

**Mode refresh** — bila `docs/dev/$ARGUMENTS.md` sudah ada (draf): pertahankan urutan kartu, kelas, kontrak, dan batas;
sesuaikan nama berkas/fungsi/tabel/rute dengan kode aktual (`grep`), perintah & format dengan hasil Tier-2/milestone
sebelumnya, dan seksi REF terkait. Hapus baris `DRAF`. Laporkan diff ringkas; perubahan isi/kontrak → tanya user dulu.

1. **Konteks minimum**
   - `docs/dev/ROADMAP.md` (isi milestone), `docs/dev/REF.md`, berkas milestone sebelumnya (kartu terakhirnya +
     peta), `docs/progress.md` (data OPEN, temuan kartu, hasil Tier-2 bila ada).
   - Dari core, baca **hanya** seksi yang relevan dengan milestone (mis. v0.45: `01_BREAKDOWN` §8, §9, §11.1,
     `02_ARSITEKTUR` §V, §Y.3.2 butir 6, §Y.3.6, §AL, §O; v0.50–v0.60: §12, §13, §14, §Y.3.3, §Z, §AA.1).
   - Periksa kode yang sudah ada untuk nama berkas/fungsi yang akan diperluas (`grep`, jangan membaca semua).
2. **Susun** `docs/dev/v0.XX.md`:
   - Pembuka ≤ 8 baris: increment, jumlah kartu/kontrak, hasil akhir, batas (yang ⛔ dikerjakan di sini), env.
   - Kartu: `Butuh · Env · Kelas`, `USER` (hanya hal di luar terminal), `Kerjakan` (bernomor, konkret: nama
     berkas, fungsi, nilai), `Jangan`, `File`, `Cek` (perintah → hasil), `Uji gagal`, `Commit`, `Ref`.
   - Target 20–45 baris per kartu. Tanpa narasi alasan panjang; alasan cukup satu klausa bila tidak jelas.
   - Kelas **kontrak** untuk kartu yang mewujudkan aturan inti (§V, §W, §Y.x, §Z, §AA.1, epistemik, 3-keadaan).
   - Nilai terkunci baru (enum, kolom, event, operasi, rute) ditambahkan ke `REF.md` di seksi yang sesuai,
     bertanda milestone lahirnya. Keputusan yang bukan dari core ditandai `[plan]`.
   - Data OPEN yang belum ada → tulis kartu yang **mengumpulkannya** (USER/Tier-2), jangan mengarang nilainya.
3. **Periksa sendiri** sebelum menyerahkan: tiap kartu punya Cek & Uji gagal yang bisa dijalankan; tidak ada
   kartu yang melompati urutan increment; tidak ada rujukan ke berkas yang tidak ada; tidak ada klaim
   berlebih (skor, vonis malware, UNKNOWN→FALSE).
4. Perbarui baris milestone di `ROADMAP.md` (jumlah kartu, nama berkas). Commit
   `docs(dev): plan v0.XX milestone cards`. Minta user me-review sebelum `/card` pertama dijalankan.
