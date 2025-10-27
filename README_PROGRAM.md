# 📊 DOKUMENTASI PROGRAM ANALISIS TRAFFIC VLR JAVA

## 🎯 Deskripsi Project

Project ini berisi program-program Python untuk menganalisis dan memprediksi traffic VLR (Visitor Location Register) di wilayah Java, khususnya untuk data traffic Indosat (H3I dan IM3) dari Oktober 2024 hingga Oktober 2025, dengan forecast hingga Tahun Baru 2026.

---

## 📁 Struktur Project

```
Project 3/
│
├── 📄 Traffic_VLR_Java_2024-2025.xlsx    # Data source (45,932 records)
│
├── 🐍 line_chart_visualization.py         # Program visualisasi line chart
├── 🐍 forecast_traffic_tahun_baru.py     # Program forecasting
│
├── 📘 README_ALGORITMA_FORECAST.md        # Dokumentasi algoritma
├── 📘 README_PROGRAM.md                   # Dokumentasi program (file ini)
│
├── 📁 line_charts/                        # Output visualisasi line chart
│   ├── 01_traffic_harian_total.png
│   ├── 02_vlr_subscribers_harian.png
│   ├── 03_traffic_per_provinsi_top5.png
│   ├── 04_traffic_per_region_top5.png
│   ├── 05_traffic_bulanan_average.png
│   ├── 06_comparison_h3i_vs_im3.png
│   ├── 07_traffic_mingguan_average.png
│   └── 08_traffic_per_kabupaten_top10.png
│
├── 📁 forecast_results/                   # Output forecasting
│   ├── 01_traffic_harian_total_forecast.png
│   ├── 02_forecast_tahun_baru_detail.png
│   ├── 03_comparison_tahun_baru.png
│   ├── 04_weekly_forecast.png
│   └── forecast_results.xlsx
│
└── 📁 .venv/                              # Virtual environment Python
```

---

## 📊 DATA SOURCE

### File: `Traffic_VLR_Java_2024-2025.xlsx`

**Spesifikasi:**

- **Total Records**: 45,932 baris
- **Periode**: 1 Oktober 2024 - 22 Oktober 2025 (386 hari)
- **Coverage**: 99.7% lengkap (386 dari 387 hari)

**Kolom Data:**

| Kolom             | Tipe     | Deskripsi                  |
| ----------------- | -------- | -------------------------- |
| Date              | datetime | Tanggal data               |
| KABUPATEN IOH     | string   | Nama kabupaten             |
| BRANCH IOH        | string   | Nama branch                |
| REGION IOH        | string   | Nama region                |
| CIRCLE IOH        | string   | Nama circle                |
| PROVINCE          | string   | Nama provinsi              |
| Traffic_H3I (TB)  | float    | Traffic H3I dalam Terabyte |
| Traffic_IM3 (TB)  | float    | Traffic IM3 dalam Terabyte |
| Traffic_Total(TB) | float    | Total traffic (H3I + IM3)  |
| VLR_3ID_subs      | int      | Jumlah subscribers 3ID     |
| VLR_IM3_subs      | int      | Jumlah subscribers IM3     |

**Statistik Data:**

```
Traffic per Hari: ~118 records (berbeda lokasi)
Rata-rata Traffic Total: 36.44 TB/record
Min Traffic: 0.00 TB
Max Traffic: 403.50 TB
```

---

## 🐍 PROGRAM 1: LINE CHART VISUALIZATION

### File: `line_chart_visualization.py`

### 📋 Deskripsi

Program untuk membuat visualisasi line chart dari data historical traffic VLR Java.

### 🎯 Fitur

1. **Traffic Total Harian** (H3I + IM3 + Total)

   - Agregasi harian dari semua lokasi
   - Tren traffic dari waktu ke waktu
   - 3 line berbeda untuk Total, H3I, dan IM3

2. **VLR Subscribers Harian** (3ID + IM3 + Total)

   - Jumlah pelanggan per hari
   - Analisis pertumbuhan subscriber

3. **Traffic per Provinsi** (Top 5)

   - Perbandingan 5 provinsi dengan traffic tertinggi
   - Tren per provinsi

4. **Traffic per Region** (Top 5)

   - Perbandingan 5 region terbaik
   - Analisis performa regional

5. **Traffic Rata-rata Bulanan**

   - Agregasi per bulan
   - Identifikasi tren musiman

6. **Perbandingan H3I vs IM3** (Dual Axis)

   - Visualisasi dengan 2 sumbu Y
   - Perbandingan langsung kedua operator

7. **Traffic Rata-rata Mingguan**

   - Tren per minggu
   - Pattern mingguan

8. **Traffic per Kabupaten** (Top 10)
   - Detail 10 kabupaten tertinggi
   - Analisis geografis detail

### 📥 Input

```python
Filename: "Traffic_VLR_Java_2024-2025.xlsx"
Sheet: "Traffic_VLR" (sheet pertama)
```

### 📤 Output

```
Folder: line_charts/
Format: PNG (300 DPI)
Total Files: 8 chart
Size: ~2-3 MB per file
```

### 🚀 Cara Menjalankan

```bash
# Via terminal
python line_chart_visualization.py

# Via virtual environment
.venv/Scripts/python.exe line_chart_visualization.py
```

### ⏱️ Waktu Eksekusi

```
Load Data: ~2-3 detik
Generate Charts: ~15-20 detik
Total: ~20-25 detik
```

### 📊 Library yang Digunakan

| Library    | Version  | Fungsi            |
| ---------- | -------- | ----------------- |
| pandas     | Latest   | Manipulasi data   |
| matplotlib | Latest   | Visualisasi chart |
| seaborn    | Latest   | Styling chart     |
| numpy      | Latest   | Operasi numerik   |
| pathlib    | Built-in | Manajemen file    |

---

## 🐍 PROGRAM 2: TRAFFIC FORECASTING

### File: `forecast_traffic_tahun_baru.py`

### 📋 Deskripsi

Program untuk memprediksi traffic dari 23 Oktober 2025 hingga 5 Januari 2026, dengan fokus khusus pada prediksi lonjakan traffic Tahun Baru 2026.

### 🎯 Fitur

#### 1. Analisis Pola Tahun Baru 2025

- Menganalisis data ±15 hari dari Tahun Baru 2025
- Menghitung spike ratio (rasio lonjakan)
- Baseline before/after comparison

#### 2. Multi-Model Forecasting

- **Moving Average** (7 hari)
- **Weighted Moving Average** (14 hari)
- **Exponential Smoothing** (alpha=0.3)
- Ensemble dari ketiga metode

#### 3. Seasonality Factors

- **Weekly**: Weekend lebih tinggi 10%
- **Event-based**: Lonjakan Tahun Baru 8.13%

#### 4. Visualisasi Forecast

- Full historical + forecast (semua data)
- Detail periode Tahun Baru
- Comparison 2025 vs 2026
- Weekly aggregation

#### 5. Export ke Excel

- Forecast values dengan confidence interval
- Historical data (30 hari terakhir)
- Summary statistics
- Daily details

### 📥 Input

```python
Filename: "Traffic_VLR_Java_2024-2025.xlsx"
Period: 1 Okt 2024 - 22 Okt 2025 (386 hari)
```

### 📤 Output

#### Visualisasi (PNG, 300 DPI):

```
📁 forecast_results/
├── 01_traffic_harian_total_forecast.png    # Chart utama
├── 02_forecast_tahun_baru_detail.png       # Zoom Tahun Baru
├── 03_comparison_tahun_baru.png            # 2025 vs 2026
└── 04_weekly_forecast.png                  # Per minggu
```

#### Data (Excel):

```
📄 forecast_results/forecast_results.xlsx
Sheets:
- Forecast: Data forecast lengkap
- Recent_Historical: 30 hari terakhir
- Summary: Statistik ringkasan
- Daily_Details: Detail harian dengan info tambahan
```

### 🧮 Algoritma

Lihat detail di: **README_ALGORITMA_FORECAST.md**

**Formula Singkat:**

```
Forecast(t) = [(MA + WMA + ES)/3 + trend×t] × weekly_factor × ny_factor + noise
```

**Parameters:**

- Base Value: 15,043 TB
- Trend: -31.57 TB/hari
- Spike Ratio (NY): 108.13%
- Confidence Interval: ±10%

### 🚀 Cara Menjalankan

```bash
# Via terminal
python forecast_traffic_tahun_baru.py

# Via virtual environment
.venv/Scripts/python.exe forecast_traffic_tahun_baru.py
```

### ⏱️ Waktu Eksekusi

```
Load Data: ~2-3 detik
Analyze NY Pattern: ~1 detik
Generate Forecast: ~2 detik
Create Charts: ~20-25 detik
Save Excel: ~2-3 detik
Total: ~30-35 detik
```

### 📊 Hasil Prediksi

**Key Metrics:**

```
Periode Forecast: 75 hari (23 Okt 2025 - 5 Jan 2026)
Rata-rata Traffic: ~14,600 TB/hari
Traffic Tertinggi: ~17,000 TB (sekitar Tahun Baru)
Traffic Tahun Baru 2026: ~13,500-14,000 TB
Lonjakan: ~8% dari baseline
```

---

## ⚙️ INSTALASI & SETUP

### 1. Requirements

```bash
Python: 3.8 atau lebih tinggi
OS: Windows/Linux/MacOS
RAM: Minimum 4 GB
Storage: ~500 MB untuk data + output
```

### 2. Install Dependencies

```bash
# Buat virtual environment (opsional tapi recommended)
python -m venv .venv

# Aktifkan virtual environment
# Windows:
.venv\Scripts\activate

# Linux/Mac:
source .venv/bin/activate

# Install packages
pip install pandas matplotlib seaborn openpyxl numpy
```

### 3. Package Versions

```
pandas>=1.5.0
matplotlib>=3.6.0
seaborn>=0.12.0
openpyxl>=3.0.0
numpy>=1.23.0
```

---

## 🎨 VISUALISASI

### Style & Theme

**Color Palette:**

```python
Total Traffic: #2E86AB (Biru)
H3I Traffic:   #A23B72 (Ungu)
IM3 Traffic:   #F18F01 (Orange)
Forecast Area: Yellow (Alpha=0.15)
Tahun Baru:    Gold dengan bintang
```

**Chart Settings:**

- Style: seaborn-v0_8-whitegrid
- Figure Size: 16-20 inch (width) × 8-10 inch (height)
- DPI: 300 (high resolution)
- Grid: Alpha=0.3, Linestyle='--'
- Font: Default (dapat disesuaikan)

### Chart Components

**Historical Data:**

- Line: Solid, linewidth=2-2.5
- Markers: o (Total), s (H3I), ^ (IM3)
- Marker Size: 2-3 points

**Forecast Data:**

- Line: Dashed (--), linewidth=2-2.5
- Markers: Same as historical
- Background: Yellow shading

**Highlights:**

- Tahun Baru 2026: Gold star (★, size=400)
- Tahun Baru 2025: Orange star (★, size=300)
- Vertical lines: Dotted (:), linewidth=3-4

---

## 🔧 TROUBLESHOOTING

### Error: File not found

```bash
Solusi: Pastikan file "Traffic_VLR_Java_2024-2025.xlsx" ada di folder yang sama
```

### Error: Module not found

```bash
Solusi: Install package yang kurang
pip install <package_name>
```

### Error: Memory error

```bash
Solusi: Tutup aplikasi lain, atau gunakan komputer dengan RAM lebih besar
```

### Chart tidak muncul

```bash
Solusi: Cek folder output (line_charts/ atau forecast_results/)
        File disimpan otomatis, tidak ditampilkan di layar
```

### Forecast tidak akurat

```bash
Catatan: Forecast memiliki confidence interval ±10%
         Actual value bisa berbeda, ini adalah estimasi
```

---

## 📈 USE CASES

### 1. Business Intelligence

- Monitoring traffic trends
- Capacity planning
- Resource allocation

### 2. Network Planning

- Prediksi kebutuhan bandwidth
- Identifikasi peak hours
- Optimasi infrastruktur

### 3. Marketing Analysis

- Seasonal campaign planning
- Event impact analysis
- Regional performance comparison

### 4. Executive Reporting

- High-quality charts untuk presentasi
- Summary statistics
- Trend analysis

---

## 🔄 WORKFLOW PENGGUNAAN

### Scenario 1: Analisis Bulanan

```
1. Run: line_chart_visualization.py
2. Lihat: 05_traffic_bulanan_average.png
3. Analisis tren per bulan
4. Identifikasi pattern musiman
```

### Scenario 2: Prediksi Traffic

```
1. Run: forecast_traffic_tahun_baru.py
2. Lihat: 01_traffic_harian_total_forecast.png
3. Export: forecast_results.xlsx untuk Excel
4. Presentasi hasil ke management
```

### Scenario 3: Regional Analysis

```
1. Run: line_chart_visualization.py
2. Lihat: 03_traffic_per_provinsi_top5.png
        04_traffic_per_region_top5.png
        08_traffic_per_kabupaten_top10.png
3. Identifikasi area dengan performa tinggi
4. Resource allocation planning
```

---

## 📝 CATATAN PENTING

### Data Quality

- ✅ Data 99.7% lengkap (386/387 hari)
- ✅ Tidak ada missing values signifikan
- ✅ Outliers sudah dianalisis dan valid

### Forecast Limitations

- ⚠️ Akurasi ±10% (normal untuk time series)
- ⚠️ Tidak memperhitungkan event eksternal (bencana, pandemi, dll)
- ⚠️ Asumsi: Pola Tahun Baru 2026 mirip dengan 2025

### Chart Quality

- ✅ 300 DPI - Print quality
- ✅ Format PNG - Universal compatibility
- ✅ Size optimal untuk presentasi (16-20 inch wide)

---

## 🚀 FUTURE ENHANCEMENTS

### Potential Improvements:

1. **Advanced Forecasting**

   - ARIMA model
   - LSTM neural network
   - Prophet by Facebook

2. **Interactive Dashboards**

   - Plotly/Dash integration
   - Real-time monitoring
   - Filter by location/operator

3. **Automated Reporting**

   - PDF report generation
   - Email notifications
   - Scheduled runs

4. **Machine Learning**
   - Anomaly detection
   - Predictive maintenance
   - Churn prediction

---

## 👥 SUPPORT

### Pertanyaan & Masalah

Jika ada pertanyaan atau masalah:

1. Cek dokumentasi ini terlebih dahulu
2. Lihat README_ALGORITMA_FORECAST.md untuk detail algoritma
3. Cek error message di terminal
4. Pastikan semua dependencies ter-install

### Kontak

- Developer: Traffic Analysis Team
- Date: October 2025
- Version: 1.0

---

## 📄 LICENSE & USAGE

**Internal Use Only**

- Data bersifat confidential
- Tidak untuk distribusi publik
- Untuk keperluan analisis internal perusahaan

---

## ✅ CHECKLIST SEBELUM RUNNING

- [ ] Python 3.8+ ter-install
- [ ] Virtual environment aktif (recommended)
- [ ] All packages ter-install (pandas, matplotlib, dll)
- [ ] File Excel ada di folder yang benar
- [ ] Folder output tidak read-only
- [ ] RAM tersedia minimum 2 GB
- [ ] Disk space tersedia minimum 100 MB

---

## 📚 REFERENCES

### Documentation:

- Pandas: https://pandas.pydata.org/docs/
- Matplotlib: https://matplotlib.org/stable/contents.html
- Seaborn: https://seaborn.pydata.org/

### Tutorials:

- Time Series Analysis with Python
- Forecasting Methods and Principles
- Data Visualization Best Practices

---

_Happy Analyzing! 📊_

**Last Updated:** October 27, 2025  
**Version:** 1.0  
**Author:** Traffic Analysis Team
