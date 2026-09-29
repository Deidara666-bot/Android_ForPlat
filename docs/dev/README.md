# docs/dev — rencana pengembangan per versi

## Isi

| Berkas | Fungsi |
|---|---|
| `ROADMAP.md` | peta milestone `v0.05`–`v1.00`, increment, dan jalur VPS |
| `MAP.md` | peta v0.45–v1.00: isi, kontrak, pemetaan operasi, keputusan, jadwal 8 minggu, daftar pangkas |
| `REF.md` | **semua nilai terkunci** (versi, enum, kolom, rute, perintah). Kartu merujuk `REF §X` |
| `v0.XX.md` | satu berkas per milestone: peta singkat + kartu `v0.XX.N` |

## Cara pakai

- **User:** di Claude Code ketik `/card v0.10.3` (atau `/card` untuk kartu berikutnya). Kerjakan hanya
  langkah bertanda **USER**, lalu review hasil yang dilaporkan.
- **Claude:** skill `/card` mengeksekusi satu kartu: baca kartu + seksi REF yang dirujuk → kerjakan →
  `Cek` → `Uji gagal` → commit → catat di `docs/progress.md`.
- Milestone berikutnya (`v0.45`+) dibuat dengan `/plan-milestone v0.45` — sebaiknya pakai model besar,
  lalu user review sebelum kartu dijalankan.

## Format kartu

```text
## v0.XX.N — judul
Butuh: kartu sebelumnya · Env: apa yang harus hidup · Kelas: pipa|kontrak
USER: langkah manual (hanya bila ada)
Kerjakan: langkah bernomor
Jangan: batas keras kartu ini
File: berkas yang dibuat/diubah
Cek: perintah → hasil yang diharapkan
Uji gagal: perintah → harus gagal dengan cara yang disebut
Commit: pesan
Ref: seksi core untuk dibaca user (Claude tidak perlu membukanya)
```

- **Kontrak** = kartu yang mewujudkan aturan inti penelitian; `Cek` dan `Uji gagal` tidak boleh dilonggarkan.
- **Pipa** = kartu plumbing; cukup lulus `Cek`.

## Aturan eksekusi (mengikat)

1. ⛔ Claude tidak mengubah `docs/dev/**` saat mengerjakan kartu. Kartu salah/ambigu → berhenti, laporkan.
2. ⛔ Tidak membuat berkas di luar `File` kecuali wajib (mis. `__init__.py`); sebutkan di laporan.
3. ⛔ Tidak melonggarkan test, validator, constraint, atau `Uji gagal` supaya lulus.
4. Maksimal 3 percobaan perbaikan per kegagalan; lebih dari itu → berhenti, laporkan keluaran terakhir.
5. Laporan akhir kartu ringkas: berkas berubah, hasil `Cek`, hasil `Uji gagal`, commit, catatan.
6. Kartu yang butuh AVD/Docker tidak bisa dijalankan di sesi cloud — tandai "butuh lokal" dan berhenti.

## Perbedaan dari plan lama (Cowork, 16–26 Sep 2026)

Plan lama disinkronkan ke repo nyata dan dipadatkan (±70% lebih pendek). Perubahan isi:

| # | Perubahan | Alasan |
|---|---|---|
| 1 | Repo/pagar `v0.05.2` lama dihapus; diganti setup repo yang sudah ada | repo `Android_ForPlat`, `CLAUDE.md`, rules, hook sudah berdiri |
| 2 | Rujukan `kerja.md`, `kontrak/*.md`, `PETA-BESAR`, `gate.sh`, `S-xx` diganti `REF.md`, `.claude/rules/`, `scripts/dev/check.sh` | berkas lama tidak pernah ada di repo; Claude tidak bisa membacanya |
| 3 | Gerbang mutu dijalankan per kartu (`check.sh`), bukan hook tiap edit | hemat token & waktu; hasil sama di titik commit |
| 4 | Tabel jamak (`users`, `cases`, …) | `user` dan `case` kata tercadang SQL |
| 5 | User aplikasi DB non-superuser via `infra/postgres/init` | `POSTGRES_USER` image resmi selalu superuser; §AD melarang |
| 6 | Password `DATABASE_URL` = password compose | contoh §S.1 (`password`) tidak cocok §R (`local-dev-only`) → koneksi gagal |
| 7 | `POST /api/agents/register` wajib JWT; token ditulis ke `agent/.env` oleh skrip | rute pendaftaran terbuka = siapa pun bisa dapat token agen |
| 8 | Unggah bukti pakai token agen saja | agen tidak punya JWT pemeriksa |
| 9 | WS + heartbeat sebelum deteksi perangkat; laporan perangkat lewat WS | laporan perangkat butuh kanal yang sudah ada |
| 10 | Nilai enum/keadaan di kode berbahasa Inggris | aturan repo: identifier Inggris, label UI Indonesia |
| 11 | Semua enum tertutup ditulis sekali di `v0.10.1` | satu sumber, kartu berikutnya tinggal pakai |
| 12 | Uji negatif SQL mentah diganti test pytest yang mencocokkan nama constraint | `INSERT` posisional rapuh terhadap urutan kolom |
| 13 | Pengecekan "tepat N tag" diganti "tag v0.XX ada" | tidak rapuh terhadap tag lain |
| 14 | `var/` di `.gitignore` tidak lagi dijangkar ke root | `agent/var/raw/` sebelumnya tidak ter-ignore |
| 15 | `auto memory` di `docs/agent-memory/` tidak dipakai | status sesi sudah di `docs/progress.md` |
