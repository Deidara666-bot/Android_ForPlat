---
paths:
  - "android-test-apps/**"
---

# Aturan simulator bukti aman (`android-test-apps/`)

Dasar: `02_ARSITEKTUR` §N, §O, §Y.3.5b; `01_BREAKDOWN` §11.3. Simulator adalah **penghasil keadaan
forensik yang diketahui**, bukan malware, dan bukan *increment* keenam.

## Komponen

`safe-evidence-simulator/` (aplikasi Kotlin), `scenario-controller/` (pengendali host: reset → install
varian → seed data sintetis → aksi transparan → catat oracle/waktu → akuisisi allowlist → hash → verifikasi
→ evaluasi → bandingkan ground truth), `local-endpoint/` (penerima lalu lintas lokal/loopback saja),
`benign-control-catalog/` (metadata aplikasi S-B, bukan binernya).

## Build baseline

Kotlin plugin 2.3.21 · AGP 9.3.0 · Gradle 9.5.0 · JDK 17 · compileSdk/targetSdk 36 · minSdk 28.
Versi eksak tanpa `+`. Varian: `authoring`, `holdout`, `benignControl` (`run_purpose` = `benign_control`);
`holdout` memakai package/signature/config berbeda.

## Boleh

Identitas package/UID/versi; permintaan izin transparan dengan persetujuan pengguna; layanan
aksesibilitas **no-op** yang diaktifkan manual; overlay berlabel jelas **SIMULASI UJI**; receiver
`BOOT_COMPLETED` yang hanya menghasilkan notifikasi/log terlihat; aktivitas penggunaan dipicu pengendali;
HTTP ke endpoint lokal dengan payload sintetis; SMS/kontak sintetis ditanam oleh pengendali lewat
mekanisme lab yang sah.

## ⛔ Larangan keras

Pencurian kredensial; membaca/mengirim data pribadi nyata; impersonasi merek/bank/lembaga; komunikasi
ke host selain endpoint lokal; stealth (ikon tersembunyi, notifikasi disembunyikan); obfuscation/packing/
evasion/deteksi emulator; exploit; auto-grant izin; penyalahgunaan aksesibilitas (membaca layar, input
injection); overlay yang menipu; persistensi tersembunyi; modul aktif yang tidak dinyatakan konfigurasi.
Setiap modul dinyalakan eksplisit lewat konfigurasi build/pengendali.

## Skenario & oracle

- Setiap skenario punya `ground_truth.json` sesuai kontrak §N.6 (`scenario_id`, `sample_category`,
  `variant`, `apk`{package, version, sha256}, `environment`, `initial_state`, `actions`,
  `expected_artifacts`, `expected_facts`, `expected_apkf`, `claim_limits`, `intentional_unavailability`,
  `expected_conflicts`) dan disimpan di `experiments/ground_truth/`.
- Skenario harus diturunkan dari perilaku APK penipuan yang **terdokumentasi** dan menyebut rujukannya.
- FALSE dibuat lewat keadaan negatif teramati, bukan menghapus berkas; UNKNOWN lewat ketidaktersediaan
  terkontrol; konflik lewat dua sumber sah yang tidak sejalan.
- Pengendali menolak jalan bila hash APK, versi aturan/KB/kode, konfigurasi, atau ground truth tidak cocok
  dengan manifest eksperimen. Semua log/bukti/oracle memakai `scenario_id` yang sama.
- APK hasil build di-ignore Git; source Kotlin dan konfigurasi di-commit. Hash APK beku dicatat di manifest.
