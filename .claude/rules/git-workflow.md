# Aturan Git & dua remote (GitHub + GitLab)

Dasar: `02_ARSITEKTUR` §AG. Berlaku untuk semua sesi.

## Topologi remote

| Remote | Host | Peran |
|---|---|---|
| `origin` | GitHub | **sumber kebenaran**: history, backup, tag milestone, tag freeze |
| `gitlab` | GitLab | mirror untuk **CI/CD** (`.gitlab-ci.yml`: SAST + secret detection, nanti test/lint) |

- Kedua remote harus menunjuk commit yang sama untuk setiap branch dan tag yang di-push.
- Push selalu **`origin` dulu**, baru `gitlab`. Kalau push ke `origin` gagal, jangan push ke `gitlab`.
- Kalau push ke `gitlab` gagal (jaringan/auth), laporkan ke user; jangan mengubah history untuk
  "memperbaikinya".
- ⛔ Jangan pernah commit lewat web UI GitHub/GitLab, merge request GitLab, atau fitur "edit file"
  online. Bila itu terlanjur terjadi, **tarik ke lokal dulu** (`git pull origin <branch>`), lalu sinkronkan.
- Cek sinkronisasi: `git fetch origin && git fetch gitlab` lalu bandingkan
  `git rev-parse origin/<branch>` vs `git rev-parse gitlab/<branch>`.
- Pipeline CI hanya didefinisikan di `.gitlab-ci.yml`. File ini diedit di repo lokal dan ikut alur
  commit biasa. Jangan menambah `.github/workflows/` kecuali user memutuskan.

## Setup sekali per clone (mesin lokal)

```bash
git remote -v                                   # pastikan origin = GitHub
git remote add gitlab <URL-repo-GitLab>         # bila belum ada
git config core.hooksPath .githooks             # aktifkan pre-commit guard
git config core.autocrlf false                  # line ending diatur .gitattributes
```

## Branch

| Pola | Untuk |
|---|---|
| `main` | selalu bisa build/run, bebas secret, siap demo milestone terakhir |
| `feature/<topik>` | fitur (`feature/agent-device-detection`, `feature/rule-engine`) |
| `fix/<topik>` | perbaikan bug |
| `experiment/<topik>` | Tier-2, skenario, holdout (`experiment/tier2-api36`, `experiment/holdout-v1`) |
| `docs/<topik>` | dokumentasi & diagram |
| `claude/<nama>` | branch yang ditugaskan untuk sesi Claude Code di cloud |

- Tanpa GitFlow, tanpa branch `dev` kecuali user memutuskan.
- Merge ke `main`: `git switch main && git pull origin main && git merge --no-ff <branch>`,
  jalankan pemeriksaan, push ke kedua remote, lalu hapus branch lokal (dan remote bila sudah tidak dipakai).
- Commit/push/merge/tag hanya dilakukan bila user memintanya (langsung atau lewat skill).

## Commit

Format: `type(scope): ringkasan singkat dalam bahasa Inggris, huruf kecil, tanpa titik`.

- `type`: `feat` · `fix` · `refactor` · `test` · `docs` · `chore` · `experiment`
- `scope` yang dipakai: `repo`, `ci`, `deps`, `agent`, `acquisition`, `backend`, `api`, `ws`, `db`,
  `parser`, `normalization`, `research`, `rules`, `kb`, `correlation`, `frontend`, `simulator`,
  `experiments`, `docs`, `diagrams`
- Satu commit = satu tujuan logis. Jangan mencampur refactor dengan perubahan perilaku.
- Perubahan YAML aturan/KB **wajib** punya body berisi alasan + rujukan (lihat `rules-kb-yaml.md`).
- Contoh: `feat(parser): parse granted permission state`,
  `test(correlation): cover required unknown evidence`,
  `experiment(tier2): record api36 sms provider result`.

## Tag

- Milestone: `v0.05`, `v0.10`, `v0.20`, `v0.30`, `v0.40`, `v0.45`, `v0.50`, `v0.60`, `v0.70`, `v0.80`,
  `v0.90`, `v1.00` (arti tiap milestone: `02_ARSITEKTUR` §AJ.3). Annotated tag, dibuat di `main`.
- Freeze aturan sebelum holdout: `rules-v<N>-freeze` (§AG.11), hanya setelah `freeze_manifest.json` ada.
- Tag di-push ke **kedua** remote. ⛔ Tag yang sudah di-push tidak dipindah/dihapus.

## Larangan

- ⛔ `git push --force` / `-f`, `git reset --hard` pada branch yang sudah di-push, rebase branch yang
  sudah di-push, `git filter-branch`, menghapus tag — kecuali user meminta secara eksplisit.
- ⛔ `--no-verify` untuk melewati pre-commit hook.
- ⛔ Git LFS sebagai jalan menyimpan bukti mentah atau sampel.
- ⛔ Commit file: `.env*` (kecuali `.env.example`), kunci/keystore, `var/**`, `**/raw_outputs/**`,
  `*.apk`, `*.aab`, `*.dex`, `*.pcap*`, dump database, sampel malware.

## Backup

Minimum: repo lokal + `origin`. `gitlab` adalah salinan ketiga. Bundle offline opsional:
`git bundle create ../backup-android-forplat-YYYYMMDD.bundle --all`.
