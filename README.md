# Traffic Forecasting System - Indonesia

Sistem forecasting traffic untuk Indonesia dengan fokus pada wilayah Jawa, Bali, dan Nusa Tenggara.

---

## Cara Menjalankan Program

### 1. Install Dependencies

```bash
pip install pandas numpy openpyxl statsmodels matplotlib seaborn python-pptx
```

### 2. Jalankan Forecasting Lengkap

```bash
cd forecast_programs
python run_all_forecasts.py
```

_Estimasi waktu: 80-90 menit (termasuk 119 kabupaten)_

### 3. Jalankan Program Individual (Opsional)

```bash
# Forecast total Indonesia saja (2 menit)
python forecast_01_main_total.py

# Forecast per provinsi (5 menit)
python forecast_02_by_province.py

# Visualisasi semua hasil
python visualize_01_all_forecasts.py

# Analisis top 10 kabupaten
python analysis_01_top10_absolute.py
```

### 4. Generate PowerPoint Presentation

```bash
# Presentasi lengkap (139 slides)
python generate_ppt_complete.py

# Presentasi summary (33 slides)
python generate_ppt.py
```

---

## Hasil Forecasting

Semua hasil tersimpan di folder `forecast_results/`:

```
forecast_results/
├── 01_main/           → Forecast total Indonesia + visualisasi
├── 02_regional/       → Forecast Jateng, Jatim, Bali-Nusra
├── 03_provinsi/       → Forecast 6 provinsi
├── 04_kabupaten/      → Forecast 119 kabupaten
└── 05_analysis/       → Top 10 kabupaten (absolute & growth)
```

| Level           | Jumlah | MAPE    | Growth 2024→2025 |
| --------------- | ------ | ------- | ---------------- |
| Total Indonesia | 1      | ~12-15% | ~18-22%          |
| Regional        | 3      | ~15-18% | ~20-25%          |
| Provinsi        | 6      | ~18-22% | ~15-30%          |
| Kabupaten       | 119    | ~20-30% | Varies           |

**Event Besar:** Lebaran 2025 (Maret) & 2026 (Februari) → +40-50% traffic spike

---

## Dokumentasi

Untuk penjelasan lengkap, lihat folder **`docs/`**:

- **CARA_KERJA_PROGRAM.md** - Penjelasan teknis semua program
- **METODOLOGI.md** - Algoritma SARIMA & event detection
- **HASIL_ANALISIS.md** - Analisis mendalam hasil forecasting

Lihat **`docs/README.md`** untuk navigasi lengkap dokumentasi.
