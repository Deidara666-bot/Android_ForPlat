# Register penyimpangan core

Core `context/*_V3_3` tetap FROZEN. Entri di sini = nilai implementasi yang dipakai berbeda dari core, disetujui user.
Entri menimpa core dan REF untuk butir itu, lintas sesi (CLAUDE.md §1). `§X` = `02_ARSITEKTUR` kecuali disebut lain.

## Batas

- **Implementasi** → cukup entri: konfigurasi container/`.env`, password dev, path, pin versi, nama tabel/rute/enum
  tambahan, urutan kartu.
- **Substansi** → amandemen core, dikumpulkan lalu sekaligus (sebelum BAB III final atau freeze `v0.90.2`): keputusan
  D-x/G-x, invarian CLAUDE.md §3, katalog `event_type`, enum riset, YAML APKF/KB, protokol Tier-2, desain validasi,
  peran lingkungan.
- Uji: mengubah desain atau hasil penelitian → substansi. Hanya mengubah nilai yang dilaporkan → implementasi
  (isi kolom Naskah bila teksnya perlu ikut).

## Zona rawan

§E/§G versi & instalasi · §R compose · §S `.env` · §AF scaffold · §AA nama tabel/kolom · §AB rute ·
contoh kode/YAML ilustratif di luar katalog §Y.3.1a dan `01_BREAKDOWN` §14.2.

## Alur

Temuan saat kartu → berhenti, tanya user → disetujui: perbaiki + tambah entri di commit yang sama.
REF disinkronkan di `/plan-milestone` berikutnya; sampai itu entri ini yang berlaku.

## Entri

| ID | Core | Isi core | Dipakai | Alasan / bukti | Naskah | Disetujui |
|---|---|---|---|---|---|---|
| DEV-01 | §R | mount `postgres_data:/var/lib/postgresql/data` | `postgres_data:/var/lib/postgresql` | image `postgres:18.6` crash-loop pada `/data`; `docs/smoke/v0.05.md` | — | 2026-10-01 |
| DEV-02 | §R vs §AD | `POSTGRES_USER: forensic_app` (jadi superuser) | admin `postgres` + `forensic_app` NOSUPERUSER via `infra/postgres/init/` | §AD: user aplikasi non-superuser | — | 2026-09-26 |
| DEV-03 | §S.1 vs §R | password `DATABASE_URL` = `password` | `local-dev-only` | tidak cocok dengan role §R | — | 2026-09-26 |
| DEV-04 | §E, §G.5 | Platform-Tools `37.0.0` | `37.0.1` | terpasang; `docs/smoke/v0.05.md` | 3.3: versi terpasang | 2026-10-01 |
| DEV-05 | contoh core vs §Y.3.1a | `permission_observed_granted`, `accessibility_service_observed_enabled`, `overlay_permission_observed_active` | katalog §Y.3.1a (REF §EVT) | contoh ilustratif; katalog normatif | — | 2026-09-26 |
| DEV-06 | §R | `ports: "5432:5432"` | `"127.0.0.1:5432:5432"` | PostgreSQL dev (password dev) tidak boleh terbuka ke LAN; review `v0.10` | — | 2026-10-01 |
| DEV-07 | §S.1 | `DATABASE_URL` host `localhost` | host `127.0.0.1` | Windows me-resolve `localhost` ke `::1` dulu; dengan port Postgres hanya IPv4 (DEV-06) koneksi macet. Diverifikasi: `127.0.0.1` terhubung 1 s, `localhost` 5 s, `::1` timeout | — | 2026-10-01 |
