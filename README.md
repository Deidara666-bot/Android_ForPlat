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
                 └─ origin → GitHub (sumber utama) ──mirror──→ GitLab (CI/CD: .gitlab-ci.yml)
Sesi cloud claude.ai → origin/claude/* ──/integrate──→ main
```

Semua perintah git dijalankan Claude Code (lihat `CLAUDE.md` §5). User cukup review, testing, dan
hal di luar terminal. Jangan mengedit langsung lewat web GitHub/GitLab.

## Perintah Claude Code proyek

| Perintah | Fungsi |
|---|---|
| `/setup [gitlab-url]` | doctor + bootstrap lingkungan lokal (git config, toolchain, venv, .env, DB) |
| `/integrate` | bawa branch hasil sesi cloud (`claude/*`) ke `main` lalu push |
| `/new-branch feature/<topik>` | buka branch kerja dari `main` terbaru |
| `/finish-branch` | cek + review + merge `--no-ff` ke `main` + sync dua remote |
| `/sync` | push ke GitHub (GitLab ikut via mirror) dan verifikasi |
| `/milestone v0.xx` | cek kriteria lalu tag milestone / freeze aturan |
| `/rule-change <APKF-K0x> <deskripsi>` | ubah YAML aturan/KB sesuai batas *authoring* |
| `/wrap-up` | perbarui `docs/progress.md` di akhir sesi |

Subagent review: `claim-auditor` (semantik epistemik, anti-klaim-berlebih) dan
`forensic-integrity-reviewer` (integritas bukti, allowlist ADB, keamanan repo).
