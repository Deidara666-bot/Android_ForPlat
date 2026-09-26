# Android_ForPlat

Platform investigasi forensik Android berbasis web dengan *Rule-Based Evidence Correlation*
(APKF — Aturan Pola Korelasi Forensik) untuk mendukung analisis digital forensik kasus aplikasi APK
penipuan. Proyek skripsi; bukan pendeteksi malware.

- Rancangan kanonik (FROZEN): `context/`
- Aturan pengembangan untuk Claude Code: `CLAUDE.md` + `.claude/`
- Status & langkah berikutnya: `docs/progress.md`
- Rencana per versi (kartu kerja): `docs/dev/` — mulai dari `docs/dev/README.md`

## Mirror GitHub → GitLab (sekali setup)

1. GitLab: *Edit profile → Access tokens* → token baru, scope `write_repository` (akun Maintainer project).
2. GitHub repo: *Settings → Secrets and variables → Actions* → secret `GITLAB_REPO`
   (`gitlab.com/<namespace>/<project>.git`) dan `GITLAB_TOKEN`.
3. GitHub → tab *Actions* → `mirror-gitlab` → *Run workflow* (sekali). Setelah itu otomatis tiap push.
4. Bila gagal karena `main` di GitLab punya commit yang tidak ada di GitHub: GitLab *Settings → Repository →
   Protected branches* → izinkan force push di `main` sekali, jalankan ulang, lalu kembalikan.

## Alur repositori

```
Claude Code → C:\mrtz\FORENSIC PLATF\Android_ForPlat (Git lokal)
                 └─ origin → GitHub (sumber utama) ──Action mirror-gitlab──→ GitLab (CI/CD: .gitlab-ci.yml)
Sesi cloud claude.ai → origin/claude/* ──/integrate──→ main
```

Semua perintah git dijalankan Claude Code (lihat `CLAUDE.md` §5). User cukup review, testing, dan
hal di luar terminal. Jangan mengedit langsung lewat web GitHub/GitLab.

## Perintah Claude Code proyek

| Perintah | Fungsi |
|---|---|
| `/card [v0.XX.N]` | kerjakan satu kartu rencana dari `docs/dev/` |
| `/plan-milestone v0.XX` | susun kartu milestone berikutnya (model besar, user review) |
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
