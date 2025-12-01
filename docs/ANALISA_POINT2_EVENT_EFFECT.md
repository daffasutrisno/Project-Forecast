# 📊 ANALISA POINT 2: PENGARUH EVENT TAHUN BARU TERHADAP KORELASI

**Pertanyaan Spesifik:**  
_"Pada point 2 (korelasi antar provinsi), apakah ada pengaruh yang terjadi pada event Tahun Baru?"_

**Tanggal Analisa:** 5 November 2025  
**Point 2 Mengacu Pada:** Analisa korelasi antar provinsi dalam teori konservasi traffic

---

## 🎯 Jawaban Singkat

### ⚠️ **ADA PENGARUH, TAPI MINIMAL DAN TIDAK MENGUBAH PATTERN FUNDAMENTAL**

**Key Findings:**

- ❌ Korelasi **TETAP POSITIF** saat event (tidak muncul korelasi negatif)
- ✅ **5 pasang korelasi MENGUAT** (+0.10 hingga +0.18)
- ⚠️ Proporsi traffic shift **< 0.5%** (tidak signifikan)
- ✅ **Semua provinsi NAIK** bersamaan saat event (+1% hingga +3%)

**Kesimpulan:** Event Tahun Baru **TIDAK mengubah pattern fundamental** (korelasi tetap positif), hanya **meningkatkan magnitude** (traffic naik lebih tinggi) dan **memperkuat korelasi** antar provinsi tertentu.

---

## 📊 Hasil Analisa Detail

### **PERIODE DATA**

| Kategori          | Jumlah Hari | Persentase | Tanggal                  |
| ----------------- | ----------- | ---------- | ------------------------ |
| **Total**         | 75 hari     | 100%       | 23 Okt 2025 - 5 Jan 2026 |
| **Normal Period** | 63 hari     | 84%        | Non-event days           |
| **Event Period**  | 12 hari     | 16%        | 25 Des 2025 - 7 Jan 2026 |

---

## 1️⃣ **PERUBAHAN KORELASI: Normal vs Event**

### **Correlation Matrix - Normal Period (63 hari)**

|              | Bali      | DI Yogya  | Jateng    | Jatim     | NTB       | NTT       |
| ------------ | --------- | --------- | --------- | --------- | --------- | --------- |
| **Bali**     | 1.000     | **0.834** | **0.799** | **0.713** | **0.819** | **0.813** |
| **DI Yogya** | **0.834** | 1.000     | **0.779** | **0.666** | **0.861** | **0.851** |
| **Jateng**   | **0.799** | **0.779** | 1.000     | **0.844** | **0.790** | **0.766** |
| **Jatim**    | **0.713** | **0.666** | **0.844** | 1.000     | **0.615** | **0.623** |
| **NTB**      | **0.819** | **0.861** | **0.790** | **0.615** | 1.000     | **0.906** |
| **NTT**      | **0.813** | **0.851** | **0.766** | **0.623** | **0.906** | 1.000     |

### **Correlation Matrix - Event Period (12 hari)**

|              | Bali         | DI Yogya       | Jateng         | Jatim        | NTB          | NTT          |
| ------------ | ------------ | -------------- | -------------- | ------------ | ------------ | ------------ |
| **Bali**     | 1.000        | **0.847**      | **0.828**      | **0.884** ⬆️ | **0.856**    | **0.840**    |
| **DI Yogya** | **0.847**    | 1.000          | **0.960** ⬆️⬆️ | **0.747**    | **0.936** ⬆️ | **0.846**    |
| **Jateng**   | **0.828**    | **0.960** ⬆️⬆️ | 1.000          | **0.858**    | **0.914** ⬆️ | **0.873** ⬆️ |
| **Jatim**    | **0.884** ⬆️ | **0.747**      | **0.858**      | 1.000        | **0.760** ⬆️ | **0.633**    |
| **NTB**      | **0.856**    | **0.936** ⬆️   | **0.914** ⬆️   | **0.760** ⬆️ | 1.000        | **0.907**    |
| **NTT**      | **0.840**    | **0.846**      | **0.873** ⬆️   | **0.633**    | **0.907**    | 1.000        |

### **Perubahan Terbesar (Top 5)**

| #   | Pasang Provinsi       | Normal | Event | Change     | Status            |
| --- | --------------------- | ------ | ----- | ---------- | ----------------- |
| 1   | **DI Yogya ↔ Jateng** | 0.779  | 0.960 | **+0.181** | 🔥 Sangat Menguat |
| 2   | **Bali ↔ Jatim**      | 0.713  | 0.884 | **+0.171** | 🔥 Sangat Menguat |
| 3   | **Jatim ↔ NTB**       | 0.615  | 0.760 | **+0.145** | ✅ Menguat        |
| 4   | **Jateng ↔ NTB**      | 0.790  | 0.914 | **+0.123** | ✅ Menguat        |
| 5   | **Jateng ↔ NTT**      | 0.766  | 0.873 | **+0.107** | ✅ Menguat        |

### **Statistik Perubahan**

- **Korelasi Menguat (>+0.1):** 5 pasang (33%)
- **Korelasi Melemah (<-0.1):** 0 pasang (0%)
- **Korelasi Stabil (±0.1):** 10 pasang (67%)

### **🔍 Analisa:**

✅ **SEMUA KORELASI TETAP POSITIF** - Tidak ada yang berubah jadi negatif  
✅ **5 pasang MENGUAT signifikan** - Pattern sinkronisasi lebih kuat  
❌ **TIDAK ADA yang MELEMAH** - Tidak ada bukti perpindahan traffic (inverse)  
⚠️ **Pattern tetap SEARAH** - Provinsi naik/turun bersamaan

**Kesimpulan Point 2:**  
Event Tahun Baru **MEMPERKUAT korelasi** antar provinsi tertentu, tapi **TIDAK mengubah** pattern fundamental dari positif menjadi negatif (yang akan mengindikasikan perpindahan traffic).

---

## 2️⃣ **RATA-RATA TRAFFIC: Normal vs Event**

| Provinsi          | Normal (TB) | Event (TB) | Change     | Change %   |
| ----------------- | ----------- | ---------- | ---------- | ---------- |
| **Bali**          | 1,154.97    | 1,163.42   | 📈 +8.45   | **+0.73%** |
| **DI Yogyakarta** | 980.94      | 998.78     | 📈 +17.84  | **+1.82%** |
| **Jawa Tengah**   | 6,335.90    | 6,526.17   | 📈 +190.27 | **+3.00%** |
| **Jawa Timur**    | 5,711.12    | 5,775.70   | 📈 +64.57  | **+1.13%** |
| **NTB**           | 330.48      | 338.57     | 📈 +8.10   | **+2.45%** |
| **NTT**           | 369.42      | 373.34     | 📈 +3.92   | **+1.06%** |
| **TOTAL**         | 14,882.83   | 15,175.98  | 📈 +293.15 | **+1.97%** |

### **🔍 Analisa:**

✅ **SEMUA PROVINSI NAIK** - Tidak ada yang turun (konfirmasi korelasi positif)  
✅ **Jawa Tengah tertinggi** - +3.00% (provinsi terbesar, paling terpengaruh event)  
✅ **Bali terendah** - +0.73% (provinsi wisata, pola berbeda)  
✅ **Total naik +1.97%** - Event period memang meningkatkan traffic

**Interpretasi:** Semua provinsi bergerak **SEARAH** (naik bersamaan) saat event, bukan berlawanan arah. Ini **mengkonfirmasi korelasi positif**, bukan perpindahan traffic.

---

## 3️⃣ **VOLATILITAS (Variance): Normal vs Event**

| Provinsi          | Normal Std | Event Std | Change      | Status             |
| ----------------- | ---------- | --------- | ----------- | ------------------ |
| **Bali**          | 47.29 TB   | 75.65 TB  | **+28.36**  | 📈 Lebih Volatile  |
| **DI Yogyakarta** | 44.94 TB   | 76.51 TB  | **+31.57**  | 📈 Lebih Volatile  |
| **Jawa Tengah**   | 250.40 TB  | 483.39 TB | **+232.99** | 📈 Sangat Volatile |
| **Jawa Timur**    | 201.69 TB  | 183.20 TB | **-18.50**  | 📉 Lebih Stabil    |
| **NTB**           | 18.57 TB   | 33.04 TB  | **+14.47**  | 📈 Lebih Volatile  |
| **NTT**           | 21.30 TB   | 42.44 TB  | **+21.14**  | 📈 Lebih Volatile  |

### **🔍 Analisa:**

✅ **5 dari 6 provinsi** - Volatilitas MENINGKAT saat event  
⚠️ **Hanya Jawa Timur** - Malah lebih stabil (provinsi terbesar, averaging effect)  
✅ **Jawa Tengah +233 TB std** - Peningkatan volatilitas tertinggi

**Interpretasi:** Event membuat traffic **lebih unpredictable** (volatile) karena pergerakan manusia (traveling, tourism). Tapi volatilitas ini **bersifat uniform** (semua naik), bukan inverse.

---

## 4️⃣ **SHIFT PROPORSI: Normal vs Event**

| Provinsi          | Normal % | Event % | Shift      | Significance |
| ----------------- | -------- | ------- | ---------- | ------------ |
| **Bali**          | 7.76%    | 7.67%   | **-0.09%** | ✅ Stabil    |
| **DI Yogyakarta** | 6.59%    | 6.58%   | **-0.01%** | ✅ Stabil    |
| **Jawa Tengah**   | 42.57%   | 43.00%  | **+0.43%** | ✅ Stabil    |
| **Jawa Timur**    | 38.37%   | 38.06%  | **-0.32%** | ✅ Stabil    |
| **NTB**           | 2.22%    | 2.23%   | **+0.01%** | ✅ Stabil    |
| **NTT**           | 2.48%    | 2.46%   | **-0.02%** | ✅ Stabil    |

**Threshold:** Shift > 0.5% = Signifikan

### **🔍 Analisa:**

✅ **SEMUA PROVINSI STABIL** - Shift < 0.5%  
✅ **Tidak ada perpindahan signifikan** - Proporsi relatif tetap sama  
✅ **Jateng sedikit naik +0.43%** - Masih di bawah threshold

**Kesimpulan:** Meskipun ada event, **proporsi traffic antar provinsi TIDAK berubah signifikan**. Ini membuktikan traffic **naik bersamaan** (proporsi tetap), bukan berpindah (proporsi berubah drastis).

---

## 5️⃣ **KORELASI NEGATIF: Apakah Muncul Saat Event?**

### **Hasil Pencarian:**

| Period            | Korelasi Negatif (<0) | Status        |
| ----------------- | --------------------- | ------------- |
| **Normal Period** | **0 pasang**          | Semua positif |
| **Event Period**  | **0 pasang**          | Semua positif |

### **🔍 Analisa:**

❌ **TIDAK ADA korelasi negatif** di kedua periode  
❌ **Event TIDAK memunculkan** pola inverse  
✅ **Semua korelasi tetap positif** (0.63 - 0.96)

**Interpretasi Krusial:** Jika benar ada perpindahan traffic saat event, seharusnya muncul **korelasi negatif** (provinsi A naik → provinsi B turun). Fakta bahwa **semua tetap positif** membuktikan **TIDAK ada perpindahan sistematis**, hanya **kenaikan uniform**.

---

## 🎯 KESIMPULAN FINAL: Point 2 Event Effect

### **SKOR PENGARUH EVENT: 2/5** ⚠️

| Indikator                      | Hasil                 | Mendukung Perpindahan? |
| ------------------------------ | --------------------- | ---------------------- |
| ❌ **Korelasi Melemah**        | 0 pasang melemah      | TIDAK                  |
| ❌ **Korelasi Negatif Muncul** | 0 pasang negatif      | TIDAK                  |
| ✅ **Proporsi Berubah**        | Shift minimal (<0.5%) | SEDIKIT                |
| ✅ **Variance Meningkat**      | 5/6 provinsi naik     | YA (tapi uniform)      |
| ❌ **Total Traffic Berubah**   | Hanya +1.97%          | TIDAK signifikan       |

---

### **JAWABAN PERTANYAAN:**

## ⚠️ **ADA PENGARUH EVENT, TAPI BUKAN PERPINDAHAN TRAFFIC**

**Yang Terjadi Saat Event Tahun Baru:**

### ✅ **YANG BENAR:**

1. **Korelasi Menguat (5 pasang)**

   - DI Yogya ↔ Jateng: +0.18 (0.78 → 0.96)
   - Bali ↔ Jatim: +0.17 (0.71 → 0.88)
   - Pattern sinkronisasi lebih kuat

2. **Traffic Naik Bersamaan (+1-3%)**

   - Semua provinsi naik, tidak ada yang turun
   - Kenaikan seragam, bukan berlawanan arah

3. **Volatilitas Meningkat**
   - 5 dari 6 provinsi lebih volatile
   - Karena traveling/tourism (temporary movement)

### ❌ **YANG SALAH:**

1. **TIDAK ada korelasi negatif** muncul

   - Semua tetap positif (0.63-0.96)
   - Tidak ada pola inverse (A naik → B turun)

2. **TIDAK ada shift proporsi signifikan**

   - Semua < 0.5%
   - Proporsi relatif tetap sama

3. **TIDAK ada perpindahan sistematis**
   - Pattern tetap searah (naik bersamaan)
   - Bukan zero-sum (5 naik, 1 turun kecil)

---

## 💡 INTERPRETASI

### **Mengapa Korelasi Menguat?**

**Alasan korelasi positif MENGUAT saat event:**

1. **Faktor Eksternal Bersama Lebih Kuat**

   - Event nasional → semua affected bersamaan
   - Hari libur → usage pattern serupa di semua region
   - Media sosial → viral content reach semua provinsi

2. **Synchronization Effect**

   - Event scheduling sama (Natal 25 Des, NY 1 Jan)
   - Peak hours sama (countdown, pagi hari)
   - Behavior pattern sama (video call keluarga, share momen)

3. **Network Effect**
   - Cross-region calls meningkat (antar provinsi)
   - Memperkuat korelasi karena traffic terkait
   - Bukan perpindahan, tapi **saling mempengaruhi**

### **Mengapa BUKAN Perpindahan?**

**Bukti yang menunjukkan BUKAN perpindahan:**

1. **Semua Naik (+)** → Bukan zero-sum
2. **Korelasi Positif** → Bukan inverse
3. **Proporsi Stabil** → Tidak ada shift besar
4. **Pattern Seragam** → Faktor eksternal bersama, bukan migration

**Yang Terjadi Sebenarnya:**

- 🎉 **Event-driven growth** - Semua region experience increased usage
- 📱 **Behavioral change** - More calls, data, video during holiday
- 🌐 **Network activity spike** - Cross-region interactions increase
- ❌ **BUKAN perpindahan fisik** - Traffic naik organik, bukan pindah

---

## 📊 Data Pendukung

### **Files Generated:**

1. ✅ `analyze_event_correlation.py` - Script analisa 6 dimensi event effect
2. ✅ `visualize_event_correlation.py` - Generate comprehensive visualization
3. ✅ `event_correlation_analysis.png` - 7-panel analysis chart

### **Visualization Contents:**

- Panel 1-3: Correlation heatmaps (Normal, Event, Difference)
- Panel 4: Traffic bar chart comparison
- Panel 5: Variance/volatility comparison
- Panel 6: Proportion shift analysis
- Panel 7: Summary conclusion box

---

## 🎓 Kesimpulan Akademik

**Temuan ini konsisten dengan teori:**

1. **Network Theory:**

   - Event nasional → increased cross-region communication
   - Stronger synchronization during peak events
   - Positive correlation natural in connected networks

2. **Behavioral Economics:**

   - Holiday season → increased consumption (including data)
   - Uniform behavioral changes across regions
   - Not zero-sum substitution

3. **Tourism Studies:**
   - Holiday movement → temporary, not permanent
   - Both origin and destination experience traffic changes
   - Net effect: overall increase, not redistribution

---

## ✅ Rekomendasi

### **Untuk Business Strategy:**

1. **Event Planning:**

   - Expect uniform traffic increase across ALL provinces
   - Prepare network capacity everywhere, not just tourist destinations
   - Event effect is **additive**, not **substitutive**

2. **Marketing:**

   - Event promotions should be **nationwide**, not regional
   - Don't assume "stealing" traffic from other regions
   - Focus on **organic growth** during events

3. **Forecasting:**
   - Model event as **multiplier factor** (1.01x - 1.03x)
   - Apply uniformly across regions
   - Don't use migration models for events

---

**Prepared by:** AI Data Analyst  
**Date:** November 5, 2025  
**Analysis Scope:** Point 2 - Event Effect on Correlation  
**Verdict:** ⚠️ Event has MINIMAL effect on correlation pattern
