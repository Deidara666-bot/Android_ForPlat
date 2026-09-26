# Aturan Git & dua remote (GitHub + GitLab)

Dasar: `02_ARSITEKTUR` §AG. Berlaku untuk semua sesi.

## Topologi remote

| Remote | Host | Peran |
|---|---|---|
| `origin` | GitHub `Deidara666-bot/Android_ForPlat` | **sumber kebenaran**: history, backup, tag milestone, tag freeze |
| GitLab | project GitLab yang tersambung ke GitHub | **CI/CD** (`.gitlab-ci.yml`: SAST + secret detection, nanti test/lint) |

Mode GitLab dideteksi otomatis (hook `SessionStart` melaporkannya):

- **mirror** (default, tidak ada remote lokal `gitlab`): GitLab menarik dari GitHub sendiri.
  Cukup push ke `origin`. ⛔ Jangan menambah remote `gitlab` atau push ke GitLab — dua jalur tulis ke
  repo mirror bisa membuat mirror berhenti/divergen.
- **push** (remote `gitlab` ada karena user menyatakan GitLab bukan mirror): push `origin` dulu, baru
  `gitlab`, untuk branch dan tag yang sama. Push `origin` gagal → jangan push ke `gitlab`.

Umum:

- ⛔ Jangan commit lewat web UI GitHub/GitLab, merge request GitLab, atau "edit file" online. Bila terlanjur,
  tarik ke lokal dulu (`git merge --no-ff --no-edit origin/<branch>`), baru lanjut.
- Verifikasi mirror opsional: `git config --local forplat.gitlabUrl` berisi URL GitLab → `/sync` membandingkan
  SHA via `git ls-remote`.
- Pipeline CI hanya didefinisikan di `.gitlab-ci.yml`, diedit di repo lokal lewat commit biasa. Jangan
  menambah `.github/workflows/` kecuali user memutuskan.

## Otomasi (user tidak perlu menjalankan perintah git)

- Hook `SessionStart` (`.claude/hooks/session-start.sh`) di setiap sesi: set `core.hooksPath=.githooks` dan
  `core.autocrlf=false` bila belum, `git fetch --prune origin`, lalu melaporkan branch, perubahan belum
  di-commit, ahead/behind terhadap origin, mode GitLab, dan branch `origin/claude/*` yang belum masuk `main`.
- Hasil sesi Claude Code cloud (branch `claude/*`) dibawa ke `main` di mesin lokal lewat `/integrate`.
- Push selalu lewat alur `/sync`. Setup lingkungan/doctor lewat `/setup`.
- Merge selalu `--no-edit` (tidak membuka editor). ⛔ Jangan menyuruh user mengetik perintah git; jalankan
  sendiri, dan hanya minta user melakukan hal yang memang di luar terminal (instal aplikasi, login, review).

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
- Merge ke `main`: `git switch main && git pull origin main && git merge --no-ff --no-edit <branch>`,
  jalankan pemeriksaan, `/sync`, lalu hapus branch lokal (dan remote bila user setuju).
- Commit/push/merge/tag dilakukan bila user memintanya, lewat skill, atau sebagai housekeeping awal sesi
  (CLAUDE.md §5).

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
- Tag di-push lewat `/sync` (GitLab ikut lewat mirror). ⛔ Tag yang sudah di-push tidak dipindah/dihapus.

## Larangan

- ⛔ `git push --force` / `-f`, `git reset --hard` pada branch yang sudah di-push, rebase branch yang
  sudah di-push, `git filter-branch`, menghapus tag — kecuali user meminta secara eksplisit.
- ⛔ `--no-verify` untuk melewati pre-commit hook.
- ⛔ Git LFS sebagai jalan menyimpan bukti mentah atau sampel.
- ⛔ Commit file: `.env*` (kecuali `.env.example`), kunci/keystore, `var/**`, `**/raw_outputs/**`,
  `*.apk`, `*.aab`, `*.dex`, `*.pcap*`, dump database, sampel malware.

## Backup

Minimum: repo lokal + `origin`. GitLab adalah salinan ketiga. Bundle offline opsional:
`git bundle create ../backup-android-forplat-YYYYMMDD.bundle --all`.
