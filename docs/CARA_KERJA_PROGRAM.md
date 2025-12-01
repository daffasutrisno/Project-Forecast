# CARA KERJA PROGRAM

Dokumentasi teknis tentang cara kerja dan penjelasan setiap program dalam sistem forecasting traffic.

---

## 1. PROGRAM FORECASTING

### 1.1 forecast_01_main_total.py
**Fungsi:** Forecasting traffic Indonesia secara keseluruhan (total nasional)

**Cara Kerja:**
- Membaca data historis dari `data_traffic_indonesia.xlsx`
- Menggunakan algoritma SARIMA dengan parameter (1,1,1)x(1,1,1,12)
- Mendeteksi dan menangani 2 event besar:
  * Lebaran 2025 (Maret): Traffic naik signifikan
  * Lebaran 2026 (Februari): Traffic naik signifikan
- Menghasilkan forecast 2025-2026 dengan metrik akurasi
- Output: `forecast_results/01_main/forecast_data.csv`

**Parameter Kunci:**
```python
# SARIMA Parameters
order = (1, 1, 1)           # AR=1, I=1, MA=1
seasonal_order = (1, 1, 1, 12)  # Seasonal period = 12 bulan

# Event Detection
event_threshold = 0.40      # 40% growth = event besar
```

---

### 1.2 forecast_02_by_province.py
**Fungsi:** Forecasting per provinsi (7 provinsi Jawa-Bali-Nusra)

**Cara Kerja:**
- Loop untuk setiap provinsi: Bali, Jawa Tengah, Jawa Timur, NTB, NTT, DIY
- Sama seperti main forecast tapi per provinsi
- Deteksi event Lebaran berlaku untuk semua provinsi
- Output: `forecast_results/03_provinsi/[nama_provinsi].csv`

**Provinsi yang Diproses:**
1. Bali
2. Jawa Tengah
3. Jawa Timur
4. Nusa Tenggara Barat
5. Nusa Tenggara Timur
6. Daerah Istimewa Yogyakarta

---

### 1.3 forecast_03_by_regional.py
**Fungsi:** Forecasting per regional (pengelompokan provinsi)

**Cara Kerja:**
- Agregasi provinsi menjadi 3 regional:
  * **Jawa Tengah**: Jawa Tengah + DIY
  * **Jawa Timur**: Jawa Timur
  * **Bali-Nusra**: Bali + NTB + NTT
- Forecast menggunakan SARIMA yang sama
- Output: `forecast_results/02_regional/[regional].csv`

---

### 1.4 forecast_04_by_kabupaten.py
**Fungsi:** Forecasting per kabupaten (119 kabupaten)

**Cara Kerja:**
- Loop untuk semua 119 kabupaten di Excel
- Untuk setiap kabupaten:
  1. Baca data historis 2020-2024
  2. Jalankan SARIMA forecast
  3. Deteksi event Lebaran
  4. Hitung metrik akurasi
  5. Simpan hasil ke CSV
- Output: `forecast_results/04_kabupaten/[nama_kabupaten].csv`

**Catatan Penting:**
- Proses paling lama (119 kabupaten × ~30 detik = ~1 jam)
- Beberapa kabupaten mungkin gagal jika data tidak mencukupi
- Error handling otomatis skip kabupaten bermasalah

---

## 2. PROGRAM VISUALISASI

### 2.1 visualize_01_all_forecasts.py
**Fungsi:** Visualisasi semua level (Total, Regional, Provinsi, Top Kabupaten)

**Cara Kerja:**
- Membuat 4 jenis visualisasi:
  1. **Total Indonesia**: Line chart 2020-2026 dengan event markers
  2. **Regional**: 3 panel untuk Jateng, Jatim, Bali-Nusra
  3. **Provinsi**: 6 panel untuk semua provinsi
  4. **Top 10 Kabupaten**: Bar chart kabupaten dengan traffic tertinggi

**Output:**
- `forecast_results/01_main/forecast_visualization.png`
- `forecast_results/02_regional/regional_forecasts.png`
- `forecast_results/03_provinsi/province_forecasts.png`
- `forecast_results/04_kabupaten/top_kabupaten_forecasts.png`

---

### 2.2 visualize_02_main_overview.py
**Fungsi:** Visualisasi overview main forecast dengan statistik

**Cara Kerja:**
- 1 figure dengan 2 subplots:
  * **Kiri**: Line chart forecast dengan shaded forecast period
  * **Kanan**: Tabel statistik (MAPE, RMSE, Growth Rate)
- Styling profesional dengan grid dan legend
- Output: `forecast_results/01_main/main_forecast_overview.png`

---

### 2.3 visualize_03_province_summary.py
**Fungsi:** Summary table perbandingan total vs provinsi

**Cara Kerja:**
- Membaca data total dan semua provinsi
- Hitung growth rate 2024→2025 untuk setiap provinsi
- Buat comparison table dalam format visual
- Output: `forecast_results/03_provinsi/comparison_total_vs_provinces.csv`

---

## 3. PROGRAM ANALISIS

### 3.1 analysis_01_top10_absolute.py
**Fungsi:** Analisis Top 10 kabupaten berdasarkan **traffic absolut tertinggi**

**Cara Kerja:**
- Loop semua 119 kabupaten
- Baca forecast 2025 dari setiap kabupaten
- Hitung total traffic 2025 (sum 12 bulan)
- Sort descending, ambil top 10
- Output: List + CSV top 10 kabupaten

**Contoh Output:**
```
Top 10 Kabupaten (Absolute Traffic):
1. Badung (Bali) - 12.5M
2. Gianyar (Bali) - 8.3M
3. Tabanan (Bali) - 6.7M
...
```

---

### 3.2 analysis_02_top10_regional.py
**Fungsi:** Analisis Top 10 per regional (Jateng, Jatim, Bali-Nusra)

**Cara Kerja:**
- Sama seperti analysis_01 tapi **per regional**
- Filter kabupaten berdasarkan provinsi regional
- Ambil top 10 dari setiap regional
- Output: 3 lists (Top 10 Jateng, Top 10 Jatim, Top 10 Bali-Nusra)

**Regional Mapping:**
- **Jateng**: Kabupaten di Jawa Tengah + DIY
- **Jatim**: Kabupaten di Jawa Timur
- **Bali-Nusra**: Kabupaten di Bali + NTB + NTT

---

### 3.3 analysis_03_top10_percentage.py
**Fungsi:** Analisis Top 10 kabupaten berdasarkan **growth rate tertinggi**

**Cara Kerja:**
- Loop semua 119 kabupaten
- Hitung growth rate: `(2025 - 2024) / 2024 × 100%`
- Sort descending berdasarkan growth %
- Ambil top 10 dengan pertumbuhan tercepat
- Output: List + CSV top 10 kabupaten dengan growth tertinggi

**Contoh Output:**
```
Top 10 Kabupaten (Highest Growth):
1. Lombok Utara (NTB) - +45.2%
2. Bangli (Bali) - +38.7%
3. Buleleng (Bali) - +32.1%
...
```

---

## 4. MASTER SCRIPT

### run_all_forecasts.py
**Fungsi:** Menjalankan semua program secara berurutan

**Cara Kerja:**
```python
# Urutan Eksekusi:
1. forecast_01_main_total.py          # 1-2 menit
2. forecast_02_by_province.py         # 3-5 menit
3. forecast_03_by_regional.py         # 2-3 menit
4. forecast_04_by_kabupaten.py        # 60-90 menit ⚠️
5. visualize_01_all_forecasts.py      # 1 menit
6. visualize_02_main_overview.py      # 30 detik
7. visualize_03_province_summary.py   # 30 detik
8. analysis_01_top10_absolute.py      # 1 menit
9. analysis_02_top10_regional.py      # 1 menit
10. analysis_03_top10_percentage.py   # 1 menit

Total: ~80 menit
```

---

## 5. ALGORITMA FORECASTING

### SARIMA Model
**Formula:**
```
ARIMA(p,d,q) × (P,D,Q)_s
p=1, d=1, q=1 (non-seasonal)
P=1, D=1, Q=1, s=12 (seasonal)
```

**Interpretasi:**
- **AR(1)**: Nilai bulan ini dipengaruhi 1 bulan sebelumnya
- **I(1)**: Data di-differencing 1x untuk stasioneritas
- **MA(1)**: Error bulan ini dipengaruhi 1 error sebelumnya
- **Seasonal(12)**: Pola berulang setiap 12 bulan (yearly pattern)

### Event Detection
**Metode:**
```python
growth = (current_month - avg_recent_months) / avg_recent_months
if growth > 0.40:  # 40% threshold
    mark_as_event()
```

**Event yang Terdeteksi:**
1. **Lebaran 2025** (Maret 2025)
2. **Lebaran 2026** (Februari 2026)

---

## 6. STRUKTUR DATA

### Input Data
**File:** `data_traffic_indonesia.xlsx`

**Sheets:**
- **Total Indonesia**: Aggregated traffic bulanan
- **[Nama Provinsi]**: Traffic per provinsi
- **[Nama Kabupaten]**: Traffic per kabupaten (119 sheets)

**Format:**
```
Date        | Traffic
------------|----------
2020-01-01  | 1234567
2020-02-01  | 1345678
...
```

### Output Structure
```
forecast_results/
├── 01_main/
│   ├── forecast_data.csv              # Hasil forecast total
│   ├── forecast_visualization.png     # Chart total
│   └── main_forecast_overview.png     # Overview dengan stats
│
├── 02_regional/
│   ├── central_java.csv               # Forecast Jateng
│   ├── east_java.csv                  # Forecast Jatim
│   └── bali_nusra.csv                 # Forecast Bali-Nusra
│
├── 03_provinsi/
│   ├── jawa_tengah.csv                # Forecast per provinsi
│   ├── jawa_timur.csv
│   ├── bali.csv
│   └── ...
│
├── 04_kabupaten/
│   ├── badung.csv                     # Forecast per kabupaten (119 files)
│   ├── gianyar.csv
│   └── ...
│
└── 05_analysis/
    ├── top10_absolute.csv             # Top 10 traffic tertinggi
    ├── top10_regional.csv             # Top 10 per regional
    └── top10_growth.csv               # Top 10 growth tercepat
```

---

## 7. METRIK EVALUASI

### MAPE (Mean Absolute Percentage Error)
```python
MAPE = mean(|actual - forecast| / actual) × 100%
```
**Interpretasi:**
- < 10%: Excellent
- 10-20%: Good
- 20-50%: Acceptable
- > 50%: Poor

### RMSE (Root Mean Square Error)
```python
RMSE = sqrt(mean((actual - forecast)²))
```
**Interpretasi:**
- Nilai absolut (dalam satuan traffic)
- Semakin kecil semakin baik
- Sensitif terhadap outlier

### Growth Rate
```python
Growth = (Traffic_2025 - Traffic_2024) / Traffic_2024 × 100%
```

---

## 8. TROUBLESHOOTING

### Error: "Not enough data"
**Penyebab:** Kabupaten memiliki < 24 bulan data historis  
**Solusi:** Program otomatis skip kabupaten tersebut

### Error: "ARIMA convergence failed"
**Penyebab:** Data terlalu volatile atau ada missing values  
**Solusi:** Check data quality, hapus outlier ekstrem

### Forecast tidak realistis
**Penyebab:** Event detection salah atau parameter SARIMA tidak cocok  
**Solusi:** 
- Adjust `event_threshold` (default 0.40)
- Tuning SARIMA parameters jika perlu

### Program berjalan sangat lambat
**Penyebab:** `forecast_04_by_kabupaten.py` memproses 119 kabupaten  
**Solusi:** 
- Normal (~60-90 menit)
- Bisa paralelize jika perlu speed up

---

## 9. DEPENDENCIES

```python
# Core
pandas >= 1.3.0
numpy >= 1.21.0
openpyxl >= 3.0.0

# Forecasting
statsmodels >= 0.13.0

# Visualization
matplotlib >= 3.4.0
seaborn >= 0.11.0

# PowerPoint
python-pptx >= 0.6.21
```

**Install:**
```bash
pip install pandas numpy openpyxl statsmodels matplotlib seaborn python-pptx
```

---

## 10. BEST PRACTICES

### Sebelum Menjalankan Program:
1. ✅ Pastikan `data_traffic_indonesia.xlsx` ada dan format benar
2. ✅ Buat backup data original
3. ✅ Install semua dependencies
4. ✅ Alokasikan waktu 80-90 menit untuk full run

### Saat Menjalankan:
1. ✅ Jalankan via `run_all_forecasts.py` untuk konsistensi
2. ✅ Monitor console output untuk error
3. ✅ Jangan interrupt saat processing kabupaten

### Setelah Selesai:
1. ✅ Verify output di `forecast_results/`
2. ✅ Check MAPE < 20% untuk quality assurance
3. ✅ Review visualisasi untuk anomali

---

**Update Terakhir:** Desember 2025  
**Sistem:** Python 3.12 + Windows PowerShell
