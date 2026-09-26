---
name: card
description: Kerjakan satu kartu rencana pengembangan dari docs/dev (mis. v0.10.3) - baca kartu dan seksi REF yang dirujuk saja, kerjakan, jalankan Cek dan Uji gagal, commit, catat di progress. Tanpa argumen = kartu berikutnya.
argument-hint: "[v0.XX.N]"
---

# /card — eksekusi satu kartu

Kartu: `$ARGUMENTS`. Kosong → kartu berikutnya setelah "Kartu terakhir" di `docs/progress.md`.
Aturan lengkap: `docs/dev/README.md` bagian "Aturan eksekusi". Hemat token: baca **hanya** yang disebut di bawah.

1. **Muat**
   - Cari kartu: `grep -n "^## v0.XX.N " docs/dev/v0.XX.md`, lalu baca dari baris itu sampai `---` berikutnya.
   - Baca paragraf pembuka berkas milestone itu (sampai `---` pertama) sekali per milestone.
   - Baca hanya seksi `REF §...` yang disebut kartu (`grep -n "^## §X" docs/dev/REF.md`). Seksi `Ref:` di kartu
     (nomor §core) **tidak** perlu dibuka.
2. **Prasyarat**
   - `Butuh:` terpenuhi → cari commit `[<kartu sebelumnya>]` di `git log --oneline` (kartu pertama milestone:
     tag milestone sebelumnya ada). Tidak terpenuhi → berhenti, sebutkan yang kurang.
   - `Env:` — cek yang bisa dicek (`docker compose ps`, `adb devices -l`, `curl -s localhost:8000/api/health`).
     Sesi cloud dan kartu butuh AVD/Docker → berhenti: "kartu ini butuh sesi lokal".
   - `USER:` yang harus terjadi **sebelum** kerja → minta user melakukannya, tunggu konfirmasi.
   - Branch: harus `feature/v0.XX` (kartu pertama milestone membuatnya dari `main`).
3. **Kerjakan** langkah `Kerjakan` berurutan. Patuhi `Jangan`. Berkas di luar `File` hanya bila wajib
   (mis. `__init__.py`) — sebutkan di laporan. Server dev dijalankan di background dan dimatikan setelah selesai.
4. **Cek** — jalankan tiap perintah `Cek`, bandingkan dengan hasil yang diharapkan. Gagal → perbaiki
   (maks 3 percobaan per masalah). ⛔ Tidak melonggarkan test/validator/constraint/`Uji gagal`.
5. **Uji gagal** — jalankan; ia **harus** gagal dengan cara yang disebut. Jika malah lulus → itu temuan
   serius: perbaiki kodenya, bukan ujinya. Bersihkan berkas probe setelahnya.
6. **Commit** dengan pesan `Commit:` (tambahkan body singkat bila perlu). Pre-commit hook gagal → perbaiki,
   ⛔ jangan `--no-verify`.
7. **Catat** di `docs/progress.md`: "Kartu terakhir: v0.XX.N (YYYY-MM-DD)", kartu berikutnya, dan temuan
   (data OPEN terisi, asumsi yang meleset). Commit `docs(progress): v0.XX.N done` — boleh digabung ke commit kartu.
8. **Lapor** (ringkas, ≤ 15 baris): berkas berubah · hasil Cek · hasil Uji gagal · commit · langkah USER berikutnya.
   Kartu terakhir milestone: jalankan `/finish-branch`, lalu minta persetujuan user untuk `/milestone v0.XX`.

⛔ Jangan mengubah `docs/dev/**`. Kartu salah, ambigu, atau bertentangan dengan `CLAUDE.md`/REF/core → berhenti
dan jelaskan konfliknya; user yang memutuskan perbaikan kartu.
