# Baseline lingkungan pengembangan

Dicatat dari `/card v0.05.2`. Rujukan versi: `docs/dev/REF.md` §VER. Beda mayor/minor ditandai
`[MENYIMPANG]`; beda patch/minor kecil (lebih tinggi dari target) dibiarkan dan ditandai `[lebih tinggi]`.

## Laptop

| Alat | Versi terpasang | Target REF §VER | Catatan |
|---|---|---|---|
| Git | 2.55.0.windows.5 | — | ok |
| Python | 3.13.7 (`py -3.13`) | 3.13.x | ok |
| Node.js | v24.19.0 | 24 LTS | ok |
| npm | 11.17.0 | 11 | ok |
| Docker | 28.1.1 (build 4eba377) | terpasang & jalan | ok — engine WSL2 diverifikasi jalan 2026-09-30 |
| Docker Compose | v2.35.1-desktop.1 | terpasang | ok |
| VS Code | 1.138.0 | — | ok |
| Android Studio | 2026.1.4 (build `AI-261.26222.65.2614.16379836`) | Quail 3 2026.1.3 | `[lebih tinggi]` dibiarkan |
| Android SDK Platform-Tools | 37.0.1 | 37.0.0 | `[lebih tinggi]` dibiarkan |
| Android SDK Build-Tools | 36.0.0 | 36.0.0 | ok |
| Android SDK Platform | 36 | Platform 36 | ok |
| Android SDK Command-line Tools | 23.0 | (latest) | ok |
| Android Emulator | 37.1.11 | — | ok |
| DBeaver | 26.2.0 | DBeaver **atau** pgAdmin, satu saja | ok (DBeaver dipilih) |
| Bruno | 4.1.0 | — | ok |

Riwayat penyesuaian sesi ini: Node.js diupgrade dari v22.19.0 ke v24.19.0 LTS (winget,
`OpenJS.NodeJS.LTS`) supaya sesuai target. WSL2/Virtual Machine Platform diaktifkan (USER, admin +
reboot) supaya Docker Desktop bisa naik.

Tanggal pencatatan: 2026-09-30.

## AVD #1

Belum dibuat — dikerjakan di `v0.05.4`. AVD `Pixel_10` (API 36.1, Google Play) yang ada di mesin ini
bukan `avd1-api36` yang diminta kartu (Pixel 6, Google APIs, tanpa akun) dan tidak dipakai.

## Galaxy A10

Belum dicatat — dikerjakan di `v0.05.5`.
