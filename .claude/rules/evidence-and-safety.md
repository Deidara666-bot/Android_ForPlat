# Aturan bukti, sampel, dan keamanan

Dasar: `02_ARSITEKTUR` §W, §Y.3.5–§Y.3.5b, §AD; `01_BREAKDOWN` §11.3, §20. Berlaku di seluruh repo.

## Tiga kategori sampel

| Kategori | Boleh | Tidak boleh |
|---|---|---|
| **S-A** simulator bukti aman (buatan sendiri) | dibangun, dipasang, dijalankan di AVD/perangkat dummy; jaringan hanya ke endpoint lokal | perilaku berbahaya apa pun (lihat `android-simulator.md`) |
| **S-B** aplikasi benign/kontrol | dipasang/dijalankan terisolasi **setelah** hash, signature, package, versi, sumber dicatat; jaringan diblokir default | diberi label "penipuan"; dipakai sebagai bukti malware |
| **S-C** APK malware nyata (MalwareBazaar, cadangan VX-Underground) | analisis **statis** di VM terisolasi; hasil dipetakan ke profil identitas/kapabilitas statis | dipasang, dijalankan, dimuat ke AVD/perangkat, diberi jaringan, diunggah ke layanan online, di-commit, disimpan di folder repo |

- ⛔ Claude tidak mengunduh, menyalin, membuka, atau menjalankan APK malware nyata. Kode untuk
  analisis statis diuji dengan **APK sintetis/simulator**, bukan sampel malware.
- Dari S-C ⛔ tidak boleh lahir fakta `execution_observed`, UID runtime, waktu pemasangan, izin
  diberikan, atau aktivitas jaringan.

## Bukti mentah

- Alur integritas: akuisisi → tulis berkas mentah → SHA-256 di agen → unggah → SHA-256 di server →
  bandingkan → simpan imutabel. Mismatch = tolak + audit log, bukan "perbaiki".
- Bukti mentah tidak pernah ditimpa, dipangkas, diformat ulang, atau didekode di tempat. Parser membaca
  salinan/stream; hasil parse disimpan terpisah (`Artifact`).
- Metadata sesi akuisisi wajib: case/device, agent ID+versi, Android/API/build, versi Platform-Tools,
  operation ID, perintah/API, waktu mulai/selesai, timezone, `availability_status`, alasan, hash, error.
- Lokasi runtime: `var/evidence/`, `var/uploads/`, `var/reports/`, `experiments/**/raw_outputs/` —
  semuanya di-ignore Git.

## Data & secret

- Data SMS/kontak/call log untuk pengujian selalu **sintetis**. ⛔ Jangan pernah memakai data pribadi
  nyata, termasuk dari ponsel pribadi user.
- Secret hanya di `.env` (tidak di-commit). Yang di-commit hanya `.env.example` berisi placeholder.
- ⛔ Jangan membaca, mencetak, atau menyalin isi `.env`, token, atau kunci ke output, log, test, atau commit.
- Password contoh (`local-dev-only`, `change-me`) hanya untuk dev; jangan dipakai untuk demo/final.

## Kontrol keamanan minimum aplikasi (§AD)

Autentikasi pemeriksa + hash password (argon2 via `pwdlib`), JWT, token unik per agen, validasi unggahan
(ukuran, tipe, nama berkas), pencegahan *path traversal*, SHA-256 sisi server, audit log, CORS terbatas
(`CORS_ORIGINS`), user DB non-superuser, HTTPS/WSS untuk demo LAN bila memungkinkan, dan ⛔ tanpa remote
ADB shell arbitrer.
