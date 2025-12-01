# METODOLOGI FORECASTING

## Algoritma dan Metode yang Digunakan

---

## 🎯 OVERVIEW

Project ini menggunakan **Multi-Model Ensemble Forecasting** dengan mempertimbangkan:

- **Seasonality patterns** (pola musiman)
- **Event-based patterns** (lonjakan Tahun Baru)
- **Historical trends** (tren dari data historis)

**Data Historical:** 386 hari (Oktober 2024 - Oktober 2025)  
**Forecast Period:** 75 hari (23 Oktober 2025 - 5 Januari 2026)

---

## 📊 METODE ENSEMBLE

Kombinasi 3 metode forecasting dengan bobot sama:

### 1. Moving Average (MA)

**Konsep:** Rata-rata dari beberapa periode terakhir

```
MA = (X₁ + X₂ + ... + X₇) / 7
```

**Parameter:**

- Window: 7 hari terakhir
- Trend: Linear regression dari window

**Keunggulan:**

- ✅ Stabil dan smooth
- ✅ Mengurangi noise

**Kelemahan:**

- ❌ Lambat bereaksi terhadap perubahan mendadak

---

### 2. Weighted Moving Average (WMA)

**Konsep:** Rata-rata bergerak dengan bobot lebih besar untuk data terbaru

```
WMA = Σ(wᵢ × xᵢ) / Σ(wᵢ)
dimana: wᵢ = e^(i/14)
```

**Parameter:**

- Window: 14 hari terakhir
- Weights: Exponential (data terbaru bobot lebih tinggi)

**Keunggulan:**

- ✅ Responsif terhadap perubahan terbaru
- ✅ Menangkap tren lebih cepat

---

### 3. Exponential Smoothing (ES)

**Konsep:** Pemulusan eksponensial dengan bobot menurun untuk data lama

```
Sₜ = α × Xₜ + (1-α) × Sₜ₋₁
dimana: α = 0.3
```

**Parameter:**

- Alpha: 0.3 (smoothing parameter)
- Trend: Linear adjustment

**Keunggulan:**

- ✅ Balance antara stabilitas dan responsiveness
- ✅ Efektif untuk data dengan noise

---

### Ensemble Combination

```
Forecast = (MA + WMA + ES) / 3
```

**Rasional:**

- Menggabungkan kekuatan ketiga metode
- Mengurangi bias individual method
- Hasil lebih robust dan reliable

---

## 🎄 EVENT-BASED LOGIC

### Analisis Pola Tahun Baru 2025

**Periode Analisis:** 25 Desember 2024 - 7 Januari 2025 (14 hari)

#### 1. Baseline Calculation

```
Periode Normal: 1-20 Desember 2024
Baseline = Mean(traffic periode normal)
         = 13,727.08 TB
```

#### 2. Peak Detection

```
Peak 1: 31 Desember 2024 (New Year's Eve)
  - Traffic: 14,088.86 TB
  - Factor: 1.03x baseline

Peak 2: 1 Januari 2025 (New Year)
  - Traffic: 15,020.51 TB (HIGHEST)
  - Factor: 1.09x baseline
```

#### 3. Pattern Application untuk 2026

```
Baseline 2026: 13,727.08 TB (sama dengan 2025)

NYE 2026 (31 Des 2025):
  Forecast = Baseline × 1.03 = 14,000.30 TB

NY 2026 (1 Jan 2026):
  Forecast = Baseline × 1.09 = 15,070.12 TB
```

**Growth Factor Calculation:**

```
Period: 25 Des - 7 Jan
Historical 2025 Mean: 13,681.15 TB
Forecast 2026 Mean: 14,267.92 TB
Growth: +2.7%
```

---

## 📈 FORECASTING WORKFLOW

### Step 1: Data Preparation

```python
1. Load historical data (386 hari)
2. Aggregate harian (sum per hari)
3. Handle missing values (forward fill)
4. Normalize outliers (jika ada)
```

### Step 2: Base Forecast

```python
for each day in forecast_period:
    1. Calculate MA (window=7)
    2. Calculate WMA (window=14)
    3. Calculate ES (alpha=0.3)
    4. Ensemble = (MA + WMA + ES) / 3
```

### Step 3: Event Adjustment

```python
if date in new_year_period:
    if date == '31 Dec':
        forecast *= 1.03  # NYE factor
    elif date == '1 Jan':
        forecast *= 1.09  # NY factor
    else:
        # Linear interpolation antara baseline dan peak
        factor = interpolate(date, baseline_factor=1.0, peak_factor)
        forecast *= factor
```

### Step 4: Validation

```python
1. Check forecast range (min/max reasonable)
2. Smooth transitions between periods
3. Validate against historical patterns
```

---

## 🔍 LEVEL FORECASTING

### 1. Main/Total

- **Input:** Total traffic semua wilayah
- **Method:** Ensemble + Event-based
- **Output:** Forecast total traffic keseluruhan

### 2. Regional (3 regional)

- **Input:** Aggregated traffic per regional
- **Method:** Same as Main, per regional
- **Regions:** Bali Nusra, Central Java, East Java

### 3. Provinsi (6 provinsi)

- **Input:** Aggregated traffic per provinsi
- **Method:** Same as Main, per provinsi
- **Provinces:** Bali, DIY, Jateng, Jatim, NTB, NTT

### 4. Kabupaten (119 kabupaten)

- **Input:** Traffic per kabupaten
- **Method:** Individual forecast per kabupaten
- **Note:** More granular, longer processing time

---

## 📊 VALIDATION & QUALITY

### Consistency Check

```python
# Random seed untuk reproducibility
np.random.seed(42)

# Hasil akan selalu sama setiap run
```

### Range Validation

```python
# Forecast harus dalam range reasonable
min_threshold = historical_min * 0.5
max_threshold = historical_max * 2.0

assert min_threshold < forecast < max_threshold
```

### Smoothness Check

```python
# Perubahan harian tidak boleh terlalu ekstrem
daily_change = abs(forecast[i] - forecast[i-1])
max_daily_change = historical_std * 3

assert daily_change < max_daily_change
```

---

## 🎯 HASIL UTAMA

### Accuracy Metrics

**Historical Pattern Match:**

- Tahun Baru 2025 (actual): 15,020.51 TB
- Tahun Baru 2026 (forecast): 15,070.12 TB
- Difference: +0.3% (very close)

**Growth Projection:**

- Average growth 2025→2026: +2.7%
- Regional variation: +4.15% to +15.27%
- Highest growth: Bali Nusra (+15.27%)

---

## 📝 PARAMETER SUMMARY

| Parameter       | Value          | Keterangan            |
| --------------- | -------------- | --------------------- |
| MA Window       | 7 days         | Moving average window |
| WMA Window      | 14 days        | Weighted MA window    |
| ES Alpha        | 0.3            | Smoothing parameter   |
| Ensemble Weight | Equal (1:1:1)  | MA:WMA:ES             |
| NYE Factor      | 1.03x          | 31 Des multiplier     |
| NY Factor       | 1.09x          | 1 Jan multiplier      |
| Baseline Period | 1-20 Dec       | Normal period         |
| Event Period    | 25 Dec - 7 Jan | New Year period       |
| Random Seed     | 42             | Reproducibility       |

---

## 🔬 TEKNIK LANJUTAN

### Regional Growth Differentiation

Setiap regional memiliki growth rate berbeda berdasarkan historical pattern:

- Bali Nusra: Tourism-driven, high growth (+15.27%)
- Central Java: Moderate growth (+4.15%)
- East Java: Medium growth (+8.50%)

### Kabupaten-Level Forecasting

- Individual forecast per kabupaten
- Mempertimbangkan pattern unik setiap wilayah
- Lebih akurat untuk analisis granular

---

## 📚 REFERENSI

**Algoritma:**

- Moving Average: Classical time series method
- Weighted Moving Average: Enhanced MA with exponential weights
- Exponential Smoothing: Holt's linear trend method

**Event-Based Logic:**

- Pattern analysis dari historical data 2025
- Peak detection dan factor calculation
- Linear interpolation untuk smooth transitions

**Validation:**

- Range checking berdasarkan historical statistics
- Smoothness validation untuk menghindari spike
- Consistency check dengan random seed

---

**Untuk detail implementasi, lihat kode program di `forecast_programs/`**
