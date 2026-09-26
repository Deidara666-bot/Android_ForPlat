---
paths:
  - "**/*.py"
  - "**/pyproject.toml"
  - "**/requirements*.txt"
---

# Gaya kode Python (agen, backend, skrip, pengendali skenario)

Dasar: `02_ARSITEKTUR` §E.1, §K, §L, §Q, §AH.1.

- Target Python **3.13**. Ruff sebagai linter + formatter (`line-length = 100`, `target-version = "py313"`).
  mypy opsional tapi type hint wajib pada fungsi publik.
- Pydantic v2 untuk model data/konfigurasi; `pydantic-settings` untuk `.env`.
- Gunakan `pathlib.Path`, bukan string path; tidak ada path absolut hardcoded (path proyek lokal
  mengandung spasi). Encoding berkas teks eksplisit `utf-8`; bukti mentah dibaca/ditulis sebagai **bytes**.
- Waktu: `datetime` timezone-aware (UTC). ⛔ `datetime.utcnow()` / naive datetime.
- Logging lewat modul logging proyek; ⛔ `print` di kode aplikasi; ⛔ mencatat secret atau isi data sensitif.
- Exception spesifik; ⛔ `except Exception: pass`. Kegagalan akuisisi/parse dicatat sebagai status,
  bukan ditelan.
- Dependency dipin di `requirements.txt` (versi eksak `==`) setelah smoke test; dev tool di
  `requirements-dev.txt`. ⛔ Versi dinamis. Dependency baru → tanya user dulu.
- Selalu jalankan tool lewat interpreter venv: `python -m pytest`, `python -m ruff ...`.
  Windows: `.venv\Scripts\python.exe`; Linux/macOS: `.venv/bin/python`.
- Test di `tests/unit`, `tests/integration`, fixture di `tests/fixtures`. Nama `test_<unit>_<perilaku>`.
  Test tidak boleh bergantung pada jaringan eksternal, perangkat nyata, atau urutan eksekusi.
