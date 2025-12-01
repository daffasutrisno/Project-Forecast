"""
FORECAST MAIN TOTAL TRAFFIC
============================
Melakukan forecasting total traffic keseluruhan hingga Tahun Baru 2026
menggunakan ensemble forecasting (MA + WMA + ES) dengan event-based logic.

Input:
  - Traffic_VLR_Java_2024-2025.xlsx

Output:
  - forecast_results/01_main/forecast_data.csv
  - forecast_results/01_main/forecast_results.xlsx
  - forecast_results/01_main/comparison_statistics_2025_vs_2026.csv

Fungsi:
  - Forecast total traffic gabungan semua provinsi
  - Analisis perbandingan statistik 2025 vs 2026
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Set random seed untuk hasil yang konsisten
np.random.seed(42)

def load_and_prepare_data(filename):
    """Load dan prepare data untuk forecasting"""
    print("📂 Membaca data...")
    df = pd.read_excel(filename, sheet_name=0)
    df['Date'] = pd.to_datetime(df['Date'])
    
    # Agregasi harian
    daily_data = df.groupby('Date').agg({
        'Traffic_H3I (TB)': 'sum',
        'Traffic_IM3 (TB)': 'sum',
        'Traffic_Total(TB)': 'sum',
        'VLR_3ID_subs': 'sum',
        'VLR_IM3_subs': 'sum'
    }).reset_index()
    
    daily_data = daily_data.sort_values('Date').reset_index(drop=True)
    
    print(f"✓ Data dimuat: {len(daily_data)} hari")
    print(f"  Dari: {daily_data['Date'].min().strftime('%d %B %Y')}")
    print(f"  Sampai: {daily_data['Date'].max().strftime('%d %B %Y')}")
    
    return daily_data

def analyze_new_year_pattern(df):
    """Analisis pola lonjakan di sekitar Tahun Baru 2025"""
    print("\n🎆 Menganalisis pola Tahun Baru 2025 (Range 25 Des - 7 Jan)...")
    
    start_date = pd.Timestamp('2024-12-25')
    end_date = pd.Timestamp('2025-01-07')
    new_year_2025 = pd.Timestamp('2025-01-01')
    
    new_year_data = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)].copy()
    
    if len(new_year_data) > 0:
        # Baseline: rata-rata traffic normal (1-24 Des)
        normal_period_start = pd.Timestamp('2024-12-01')
        normal_period_end = pd.Timestamp('2024-12-24')
        normal_data = df[(df['Date'] >= normal_period_start) & (df['Date'] <= normal_period_end)]
        baseline = normal_data['Traffic_Total(TB)'].mean()
        
        # Analisis per hari
        daily_pattern = {}
        print(f"\n  📊 Baseline Normal (1-24 Des 2024): {baseline:.2f} TB")
        print(f"\n  📅 Detail Traffic per Hari:")
        print(f"  {'Tanggal':<15} {'Traffic (TB)':<15} {'Factor':<10} {'Perubahan':<12}")
        print(f"  {'-'*52}")
        
        for date in pd.date_range(start_date, end_date):
            day_data = new_year_data[new_year_data['Date'] == date]
            if len(day_data) > 0:
                traffic = day_data['Traffic_Total(TB)'].values[0]
                factor = traffic / baseline if baseline > 0 else 1.0
                change = ((factor - 1) * 100)
                
                label = ""
                if date.date() == pd.Timestamp('2024-12-31').date():
                    label = " ⭐⭐ NYE"
                elif date.date() == pd.Timestamp('2025-01-01').date():
                    label = " ⭐⭐⭐ PUNCAK"
                elif date.date() == pd.Timestamp('2024-12-25').date():
                    label = " 🎄 Natal"
                
                print(f"  {date.strftime('%d %b %Y'):<15} {traffic:>12.2f}    {factor:>6.2f}x    {change:>6.1f}%{label}")
                
                daily_pattern[date] = {
                    'traffic': traffic,
                    'factor': factor,
                    'change_pct': change
                }
        
        # Hitung spike ratio untuk key dates
        nye_data = new_year_data[new_year_data['Date'] == pd.Timestamp('2024-12-31')]
        ny_data = new_year_data[new_year_data['Date'] == new_year_2025]
        
        nye_value = nye_data['Traffic_Total(TB)'].values[0] if len(nye_data) > 0 else baseline
        ny_value = ny_data['Traffic_Total(TB)'].values[0] if len(ny_data) > 0 else baseline
        
        nye_ratio = nye_value / baseline if baseline > 0 else 1.0
        ny_ratio = ny_value / baseline if baseline > 0 else 1.0
        
        print(f"\n  ✓ Baseline Normal: {baseline:.2f} TB")
        print(f"  ✓ Traffic 31 Des (NYE): {nye_value:.2f} TB (Factor: {nye_ratio:.2f}x)")
        print(f"  ✓ Traffic 1 Jan (NY): {ny_value:.2f} TB (Factor: {ny_ratio:.2f}x)")
        
        return {
            'baseline': baseline,
            'nye_value': nye_value,
            'nye_ratio': nye_ratio,
            'ny_value': ny_value,
            'ny_ratio': ny_ratio,
            'daily_pattern': daily_pattern,
            'pattern_data': new_year_data,
            'start_date': start_date,
            'end_date': end_date
        }
    
    return {
        'baseline': df['Traffic_Total(TB)'].mean(),
        'nye_ratio': 1.4,
        'ny_ratio': 1.5,
        'nye_value': df['Traffic_Total(TB)'].mean() * 1.4,
        'ny_value': df['Traffic_Total(TB)'].mean() * 1.5,
        'daily_pattern': {},
        'pattern_data': None
    }

def moving_average_forecast(df, window=7):
    """Simple Moving Average dengan trend"""
    recent_data = df.tail(window)['Traffic_Total(TB)'].values
    ma = np.mean(recent_data)
    x = np.arange(len(recent_data))
    coeffs = np.polyfit(x, recent_data, 1)
    trend = coeffs[0]
    return ma, trend

def weighted_moving_average(df, window=14):
    """Weighted Moving Average"""
    recent_data = df.tail(window)['Traffic_Total(TB)'].values
    weights = np.exp(np.linspace(-1, 0, window))
    weights = weights / weights.sum()
    wma = np.sum(recent_data * weights)
    x = np.arange(len(recent_data))
    coeffs = np.polyfit(x, recent_data, 1)
    trend = coeffs[0]
    return wma, trend

def exponential_smoothing(df, alpha=0.3):
    """Exponential Smoothing"""
    data = df['Traffic_Total(TB)'].values
    smoothed = [data[0]]
    for i in range(1, len(data)):
        smoothed.append(alpha * data[i] + (1 - alpha) * smoothed[i-1])
    recent_smooth = smoothed[-30:]
    x = np.arange(len(recent_smooth))
    coeffs = np.polyfit(x, recent_smooth, 1)
    trend = coeffs[0]
    return smoothed[-1], trend

def create_forecast(df, ny_pattern, forecast_days=71):
    """Buat forecast dengan event-based logic"""
    print("\n📊 Membuat forecast dengan New Year Pattern...")
    
    last_date = df['Date'].max()
    forecast_dates = pd.date_range(start=last_date + timedelta(days=1), 
                                   periods=forecast_days, freq='D')
    
    # Ensemble forecasting
    ma_base, ma_trend = moving_average_forecast(df, window=7)
    wma_base, wma_trend = weighted_moving_average(df, window=14)
    es_base, es_trend = exponential_smoothing(df, alpha=0.3)
    
    base_value = (ma_base + wma_base + es_base) / 3
    trend = (ma_trend + wma_trend + es_trend) / 3
    baseline = ny_pattern.get('baseline', base_value)
    
    print(f"  ✓ Base value: {base_value:.2f} TB")
    print(f"  ✓ Baseline normal: {baseline:.2f} TB")
    print(f"  ✓ Trend: {trend:.4f} TB/hari")
    print(f"  ✓ NYE ratio (31 Des): {ny_pattern.get('nye_ratio', 1.03):.2f}x")
    print(f"  ✓ NY ratio (1 Jan): {ny_pattern.get('ny_ratio', 1.09):.2f}x")
    
    # Event Calendar - gunakan faktor dari pattern analysis
    daily_patterns = ny_pattern.get('daily_pattern', {})
    ny_event_factors = {
        pd.Timestamp('2025-12-25'): daily_patterns.get(pd.Timestamp('2024-12-25'), {}).get('factor', 1.01),
        pd.Timestamp('2025-12-26'): daily_patterns.get(pd.Timestamp('2024-12-26'), {}).get('factor', 1.02),
        pd.Timestamp('2025-12-27'): daily_patterns.get(pd.Timestamp('2024-12-27'), {}).get('factor', 1.01),
        pd.Timestamp('2025-12-28'): daily_patterns.get(pd.Timestamp('2024-12-28'), {}).get('factor', 1.04),
        pd.Timestamp('2025-12-29'): daily_patterns.get(pd.Timestamp('2024-12-29'), {}).get('factor', 1.06),
        pd.Timestamp('2025-12-30'): daily_patterns.get(pd.Timestamp('2024-12-30'), {}).get('factor', 1.00),
        pd.Timestamp('2025-12-31'): ny_pattern.get('nye_ratio', 1.03),
        pd.Timestamp('2026-01-01'): ny_pattern.get('ny_ratio', 1.09),
        pd.Timestamp('2026-01-02'): daily_patterns.get(pd.Timestamp('2025-01-02'), {}).get('factor', 0.96),
        pd.Timestamp('2026-01-03'): daily_patterns.get(pd.Timestamp('2025-01-03'), {}).get('factor', 0.95),
        pd.Timestamp('2026-01-04'): daily_patterns.get(pd.Timestamp('2025-01-04'), {}).get('factor', 0.97),
        pd.Timestamp('2026-01-05'): daily_patterns.get(pd.Timestamp('2025-01-05'), {}).get('factor', 0.99),
        pd.Timestamp('2026-01-06'): daily_patterns.get(pd.Timestamp('2025-01-06'), {}).get('factor', 0.91),
        pd.Timestamp('2026-01-07'): daily_patterns.get(pd.Timestamp('2025-01-07'), {}).get('factor', 0.90),
    }
    
    # Generate forecast
    forecast_values = []
    
    for i, date in enumerate(forecast_dates):
        if date in ny_event_factors:
            base_forecast = baseline
        else:
            smoothed_trend = trend * 0.5
            base_forecast = base_value + (smoothed_trend * i)
        
        # Weekly seasonality
        day_of_week = date.dayofweek
        weekly_factor = 1.05 if day_of_week in [4, 5, 6] else 1.0
        
        # Event factor
        ny_factor = ny_event_factors.get(date, 1.0)
        
        # Combine factors
        forecast = base_forecast * weekly_factor * ny_factor
        
        # Add noise (dengan random seed, hasilnya akan konsisten)
        noise_level = 0.01 if ny_factor > 1.0 else 0.02
        noise = np.random.normal(0, base_forecast * noise_level)
        forecast += noise
        forecast = max(forecast, 0)
        
        forecast_values.append(forecast)
    
    # Buat DataFrame
    forecast_df = pd.DataFrame({
        'Date': forecast_dates,
        'Traffic_Total(TB)': forecast_values,
        'Type': 'Forecast'
    })
    
    forecast_df['Lower_Bound'] = forecast_df['Traffic_Total(TB)'] * 0.9
    forecast_df['Upper_Bound'] = forecast_df['Traffic_Total(TB)'] * 1.1
    
    return forecast_df

def create_comparison_statistics(historical_df, forecast_df, ny_pattern, output_folder="forecast_results/01_main"):
    """Buat statistik perbandingan 2025 vs 2026"""
    print("\n📊 Membuat statistik perbandingan 2025 vs 2026...")
    
    # Extract data
    pattern_2025 = historical_df[
        (historical_df['Date'] >= pd.Timestamp('2024-12-25')) & 
        (historical_df['Date'] <= pd.Timestamp('2025-01-07'))
    ].copy()
    
    forecast_2026 = forecast_df[
        (forecast_df['Date'] >= pd.Timestamp('2025-12-25')) & 
        (forecast_df['Date'] <= pd.Timestamp('2026-01-07'))
    ].copy()
    
    if len(pattern_2025) == 0 or len(forecast_2026) == 0:
        print("  ⚠ Data tidak lengkap")
        return None
    
    # Comparison
    comparison_data = []
    baseline = ny_pattern.get('baseline', pattern_2025['Traffic_Total(TB)'].mean())
    
    print(f"\n  {'Tanggal':<12} {'2025 Actual':<15} {'2026 Forecast':<15} {'Selisih':<12} {'% Change':<12}")
    print(f"  {'-'*70}")
    
    for date_2025 in pd.date_range(pd.Timestamp('2024-12-25'), pd.Timestamp('2025-01-07')):
        date_2026 = date_2025 + pd.DateOffset(years=1)
        
        actual_2025_data = pattern_2025[pattern_2025['Date'] == date_2025]
        forecast_2026_data = forecast_2026[forecast_2026['Date'] == date_2026]
        
        if len(actual_2025_data) > 0 and len(forecast_2026_data) > 0:
            actual_2025 = actual_2025_data['Traffic_Total(TB)'].values[0]
            forecast_2026_val = forecast_2026_data['Traffic_Total(TB)'].values[0]
            
            diff = forecast_2026_val - actual_2025
            pct_change = (diff / actual_2025) * 100 if actual_2025 > 0 else 0
            
            label = ""
            if date_2025.date() == pd.Timestamp('2024-12-25').date():
                label = " 🎄 Natal"
            elif date_2025.date() == pd.Timestamp('2024-12-31').date():
                label = " ⭐⭐ NYE"
            elif date_2025.date() == pd.Timestamp('2025-01-01').date():
                label = " ⭐⭐⭐ NY"
            
            print(f"  {date_2025.strftime('%d %b'):<12} {actual_2025:>12.2f}    {forecast_2026_val:>12.2f}    {diff:>10.2f}   {pct_change:>8.1f}%{label}")
            
            comparison_data.append({
                'Date_2025': date_2025,
                'Date_2026': date_2026,
                'Actual_2025': actual_2025,
                'Forecast_2026': forecast_2026_val,
                'Difference': diff,
                'Pct_Change': pct_change,
                'Label': label
            })
    
    comparison_df = pd.DataFrame(comparison_data)
    
    # Summary
    print(f"\n  📈 SUMMARY STATISTICS:")
    print(f"  {'-'*50}")
    print(f"  Baseline Normal: {baseline:.2f} TB")
    print(f"  2025 (Actual): Avg={pattern_2025['Traffic_Total(TB)'].mean():.2f} TB, Peak={pattern_2025['Traffic_Total(TB)'].max():.2f} TB")
    print(f"  2026 (Forecast): Avg={forecast_2026['Traffic_Total(TB)'].mean():.2f} TB, Peak={forecast_2026['Traffic_Total(TB)'].max():.2f} TB")
    print(f"  Comparison: {comparison_df['Difference'].mean():+.2f} TB ({comparison_df['Pct_Change'].mean():+.1f}%)")
    
    # Save
    Path(output_folder).mkdir(exist_ok=True)
    csv_file = f"{output_folder}/comparison_statistics_2025_vs_2026.csv"
    comparison_df.to_csv(csv_file, index=False)
    print(f"\n  ✓ Statistik disimpan: {csv_file}")
    
    return comparison_df

def save_forecast_to_excel(historical_df, forecast_df, ny_pattern, output_folder="forecast_results/01_main"):
    """Save hasil forecast ke Excel"""
    print("\n💾 Menyimpan hasil ke Excel...")
    
    output_file = f"{output_folder}/forecast_results.xlsx"
    
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        # Forecast Results
        forecast_export = forecast_df[['Date', 'Traffic_Total(TB)', 'Lower_Bound', 'Upper_Bound']].copy()
        forecast_export['Date'] = forecast_export['Date'].dt.strftime('%Y-%m-%d')
        forecast_export.to_excel(writer, sheet_name='Forecast', index=False)
        
        # Recent Historical
        recent_hist = historical_df.tail(30)[['Date', 'Traffic_Total(TB)']].copy()
        recent_hist['Date'] = recent_hist['Date'].dt.strftime('%Y-%m-%d')
        recent_hist.to_excel(writer, sheet_name='Recent_Historical', index=False)
        
        # Summary
        summary_data = {
            'Metric': [
                'Periode Forecast', 'Jumlah Hari', 'Tanggal Mulai', 'Tanggal Akhir',
                'Rata-rata Traffic', 'Traffic Tertinggi', 'Traffic Terendah',
                'NYE Ratio (31 Des)', 'NY Ratio (1 Jan)', 'Baseline Normal', 'Confidence Interval'
            ],
            'Value': [
                '23 Okt 2025 - 05 Jan 2026',
                len(forecast_df),
                forecast_df['Date'].min().strftime('%Y-%m-%d'),
                forecast_df['Date'].max().strftime('%Y-%m-%d'),
                f"{forecast_df['Traffic_Total(TB)'].mean():.2f} TB",
                f"{forecast_df['Traffic_Total(TB)'].max():.2f} TB",
                f"{forecast_df['Traffic_Total(TB)'].min():.2f} TB",
                f"{ny_pattern['nye_ratio']:.2f}x",
                f"{ny_pattern['ny_ratio']:.2f}x",
                f"{ny_pattern['baseline']:.2f} TB",
                '±10%'
            ]
        }
        pd.DataFrame(summary_data).to_excel(writer, sheet_name='Summary', index=False)
    
    print(f"  ✓ File disimpan: {output_file}")
    
    # Save forecast data juga sebagai CSV untuk digunakan visualisasi
    forecast_csv = f"{output_folder}/forecast_data.csv"
    forecast_df.to_csv(forecast_csv, index=False)
    print(f"  ✓ Forecast data CSV: {forecast_csv}")

def main():
    """Main function"""
    print("=" * 70)
    print("  PROGRAM 1: TRAFFIC FORECASTING - HINGGA TAHUN BARU 2026")
    print("=" * 70)
    print("\n🎯 Target: Forecast dari 23 Okt 2025 hingga 05 Jan 2026")
    print("🎆 Fokus: Prediksi lonjakan traffic Tahun Baru 2026")
    print("📊 Metode: Multi-model ensemble dengan event-based logic\n")
    
    filename = "Traffic_VLR_Java_2024-2025.xlsx"
    
    if not Path(filename).exists():
        print(f"❌ Error: File '{filename}' tidak ditemukan!")
        return
    
    # Load data
    df = load_and_prepare_data(filename)
    
    # Analyze pattern
    ny_pattern = analyze_new_year_pattern(df)
    
    # Forecast
    last_date = df['Date'].max()
    target_date = pd.Timestamp('2026-01-05')
    forecast_days = (target_date - last_date).days
    
    print(f"\n📅 Periode forecast: {forecast_days} hari")
    print(f"  Dari: {(last_date + timedelta(days=1)).strftime('%d %B %Y')}")
    print(f"  Sampai: {target_date.strftime('%d %B %Y')}")
    
    forecast_df = create_forecast(df, ny_pattern, forecast_days)
    
    # Comparison statistics
    comparison_df = create_comparison_statistics(df, forecast_df, ny_pattern)
    
    # Save results
    save_forecast_to_excel(df, forecast_df, ny_pattern)
    
    # Print summary
    print("\n" + "=" * 70)
    print("✅ FORECAST SELESAI!")
    print("=" * 70)
    
    ny_date = pd.Timestamp('2026-01-01')
    ny_forecast = forecast_df[forecast_df['Date'] == ny_date]
    
    if len(ny_forecast) > 0:
        ny_value = ny_forecast['Traffic_Total(TB)'].values[0]
        avg_value = forecast_df['Traffic_Total(TB)'].mean()
        
        print(f"\n📊 Hasil Prediksi:")
        print(f"  • Rata-rata traffic: {avg_value:.2f} TB/hari")
        print(f"  • Traffic tertinggi: {forecast_df['Traffic_Total(TB)'].max():.2f} TB")
        print(f"  • Traffic pada Tahun Baru 2026: {ny_value:.2f} TB")
        print(f"  • Lonjakan dibanding rata-rata: {((ny_value/avg_value - 1) * 100):.1f}%")
    
    print(f"\n📁 Output Files:")
    print(f"  • forecast_results/01_main/forecast_data.csv")
    print(f"  • forecast_results/01_main/forecast_results.xlsx")
    print(f"  • forecast_results/01_main/comparison_statistics_2025_vs_2026.csv")
    print("\n💡 Jalankan '2_create_visualizations.py' untuk membuat visualisasi")
    print("=" * 70)

if __name__ == "__main__":
    main()
