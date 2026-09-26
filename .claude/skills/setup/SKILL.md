---
name: setup
description: Cek dan siapkan lingkungan kerja lokal (git config per-clone, mode GitLab, toolchain §E, venv, node_modules, .env dari .env.example, database Docker). Mengerjakan semua yang bisa dilakukan Claude dan memberi daftar singkat hal yang hanya bisa dilakukan user (download/instal aplikasi, boot AVD).
argument-hint: "[gitlab-url] (opsional, untuk verifikasi mirror GitLab)"
---

# /setup — doctor + bootstrap lingkungan

Prinsip: Claude mengerjakan semua langkah yang bisa dijalankan dari terminal. User hanya mengerjakan
yang memang butuh manusia: download/instal aplikasi, persetujuan UAC/installer, login akun, boot AVD
dari Android Studio, sambungkan perangkat fisik, dan review/testing.

## 1. Git (otomatis, idempotent)

- Pastikan `git config --local core.hooksPath .githooks` dan `core.autocrlf false` (hook
  `SessionStart` juga melakukan ini tiap sesi).
- Remote: `origin` harus GitHub `Deidara666-bot/Android_ForPlat`.
- **Mode GitLab**:
  - Tidak ada remote `gitlab` → mode **mirror**: GitLab mengikuti GitHub otomatis (project GitLab
    tersambung ke GitHub). ⛔ Jangan menambah remote `gitlab` dan jangan push ke GitLab di mode ini.
  - Bila `$ARGUMENTS` berisi URL GitLab: simpan `git config --local forplat.gitlabUrl <url>` agar `/sync`
    bisa memverifikasi mirror via `git ls-remote`. Bila `ls-remote` gagal karena auth, simpan tetap dan
    laporkan bahwa verifikasi dilakukan manual di web GitLab.
  - Remote `gitlab` hanya ditambahkan bila user menyatakan GitLab **bukan** mirror.

## 2. Toolchain (cek saja, bandingkan dengan `02_ARSITEKTUR` §E)

Cek dengan perintah versi (tanpa menginstal apa pun): `git --version`, Python 3.13 (`py -3.13 --version`
di Windows / `python3.13 --version`), `node --version` (24.x), `npm --version` (11.x),
`adb version`, `docker --version` + `docker compose version`, JDK 17 (`java -version`).
Tampilkan tabel: komponen · versi terpasang · baseline · status. Untuk yang belum ada, beri tautan unduhan
resmi dari `02_ARSITEKTUR` §AP — itu bagian user.

## 3. Proyek (otomatis bila foldernya sudah ada)

- `agent/` dan `backend/`: buat `.venv` dengan Python 3.13 bila belum ada, `pip install -r requirements.txt`
  (+ `requirements-dev.txt`) di dalam venv.
- `frontend/`: `npm ci` bila ada `package-lock.json`, selain itu `npm install`.
- `.env`: bila `.env` tidak ada tetapi `.env.example` ada → salin (`cp .env.example .env`). ⛔ Jangan membaca
  atau menampilkan isi `.env`; beri tahu user kalau ada nilai yang harus diganti (mis. `JWT_SECRET`).
- Database: bila Docker jalan dan `docker-compose.yml` ada → `docker compose up -d postgres`, lalu
  `alembic upgrade head` di backend.
- Folder yang belum ada karena scaffold belum dibuat → sebutkan saja, jangan membuat scaffold di skill ini.

## 4. Laporan

Ringkas dalam dua daftar:
- **Sudah dikerjakan Claude** (dengan hasil tiap langkah, termasuk yang gagal).
- **Perlu user** (hanya hal yang tidak bisa dilakukan dari terminal), berurutan dan singkat.
Perbarui `docs/progress.md` bila status lingkungan berubah.
