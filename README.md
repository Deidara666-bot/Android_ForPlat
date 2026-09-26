# Android_ForPlat

Platform investigasi forensik Android berbasis web dengan *Rule-Based Evidence Correlation*
(APKF — Aturan Pola Korelasi Forensik) untuk mendukung analisis digital forensik kasus aplikasi APK
penipuan. Proyek skripsi; bukan pendeteksi malware.

- Rancangan kanonik (FROZEN): `context/`
- Aturan pengembangan untuk Claude Code: `CLAUDE.md` + `.claude/`
- Status & langkah berikutnya: `docs/progress.md`

## Alur repositori

```
Claude Code → C:\mrtz\FORENSIC PLATF\Android_ForPlat (Git lokal)
                 ├─ origin  → GitHub  (sumber utama)
                 └─ gitlab  → GitLab  (CI/CD: .gitlab-ci.yml)
```

Semua perubahan dibuat di repo lokal, lalu di-push ke `origin` dulu, kemudian `gitlab`.
Jangan mengedit langsung lewat web GitHub/GitLab.

## Setup sekali per clone

```bash
git remote add gitlab <URL-repo-GitLab>      # origin (GitHub) sudah ada dari clone
git config core.hooksPath .githooks          # aktifkan pre-commit guard (bukti/sampel/secret)
git config core.autocrlf false               # line ending diatur .gitattributes
```

## Perintah Claude Code proyek

| Perintah | Fungsi |
|---|---|
| `/new-branch feature/<topik>` | buka branch kerja dari `main` terbaru |
| `/finish-branch` | cek + review + merge `--no-ff` ke `main` + sync dua remote |
| `/sync` | push ke GitHub lalu GitLab dan verifikasi keduanya sama |
| `/milestone v0.xx` | cek kriteria lalu tag milestone / freeze aturan |
| `/rule-change <APKF-K0x> <deskripsi>` | ubah YAML aturan/KB sesuai batas *authoring* |
| `/wrap-up` | perbarui `docs/progress.md` di akhir sesi |

Subagent review: `claim-auditor` (semantik epistemik, anti-klaim-berlebih) dan
`forensic-integrity-reviewer` (integritas bukti, allowlist ADB, keamanan repo).
