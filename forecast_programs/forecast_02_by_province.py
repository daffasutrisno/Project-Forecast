"""
FORECAST BY PROVINCE
====================
Membuat forecast individual untuk setiap provinsi (6 provinsi)
berdasarkan pola data historis masing-masing provinsi.

Input:
  - Traffic_VLR_Java_2024-2025.xlsx

Output:
  - forecast_results/03_provinsi/[nama_provinsi].csv (6 files)
  - forecast_results/03_provinsi/[nama_provinsi]_forecast.png (6 files)
  - forecast_results/03_provinsi/comparison_total_vs_provinces.csv

Fungsi:
  - Forecast per provinsi: Bali, DIY, Jawa Tengah, Jawa Timur, NTB, NTT
  - Visualisasi dengan chart horizontal + statistics + distribution
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from pathlib import Path
from datetime import datetime, timedelta

# Set random seed untuk konsistensi
np.random.seed(42)

def load_and_prepare_province_data(province_name):
    """Load data dan aggregate per hari untuk provinsi tertentu"""
    print(f"  → Loading data untuk {province_name}...")
    
    df = pd.read_excel("Traffic_VLR_Java_2024-2025.xlsx", sheet_name=0)
    df['Date'] = pd.to_datetime(df['Date'])
    
    # Filter by province
    df_province = df[df['PROVINCE'] == province_name].copy()
    
    # Aggregate per hari
    daily_data = df_province.groupby('Date').agg({
        'Traffic_H3I (TB)': 'sum',
        'Traffic_IM3 (TB)': 'sum',
        'Traffic_Total(TB)': 'sum'
    }).reset_index()
    
    daily_data = daily_data.sort_values('Date').reset_index(drop=True)
    
    return daily_data

def analyze_new_year_pattern_province(daily_data):
    """Analisis pattern Tahun Baru dari data 2025 untuk provinsi"""
    
    # Get data Dec 25, 2024 - Jan 7, 2025
    start_date = pd.Timestamp('2024-12-25')
    end_date = pd.Timestamp('2025-01-07')
    
    ny_period = daily_data[(daily_data['Date'] >= start_date) & 
                           (daily_data['Date'] <= end_date)].copy()
    
    if len(ny_period) == 0:
        print("    ⚠️  Tidak ada data periode Tahun Baru, menggunakan baseline")
        return {}
    
    # Baseline dari Des 1-24
    baseline_start = pd.Timestamp('2024-12-01')
    baseline_end = pd.Timestamp('2024-12-24')
    baseline_period = daily_data[(daily_data['Date'] >= baseline_start) & 
                                  (daily_data['Date'] <= baseline_end)]
    
    if len(baseline_period) == 0:
        print("    ⚠️  Tidak ada data baseline, menggunakan rata-rata keseluruhan")
        baseline_avg = daily_data['Traffic_Total(TB)'].mean()
    else:
        baseline_avg = baseline_period['Traffic_Total(TB)'].mean()
    
    # Calculate factors untuk setiap tanggal
    event_factors = {}
    for _, row in ny_period.iterrows():
        date_str = row['Date'].strftime('%Y-%m-%d')
        factor = row['Traffic_Total(TB)'] / baseline_avg if baseline_avg > 0 else 1.0
        event_factors[date_str] = factor
    
    return event_factors

def moving_average_forecast(data, window=7):
    """Simple Moving Average dengan trend"""
    recent_data = data[-window:]
    ma = np.mean(recent_data)
    x = np.arange(len(recent_data))
    coeffs = np.polyfit(x, recent_data, 1)
    trend = coeffs[0]
    return ma, trend

def weighted_moving_average(data, window=14):
    """Weighted Moving Average dengan trend"""
    if len(data) < window:
        window = len(data)
    recent_data = data[-window:]
    weights = np.exp(np.linspace(-1, 0, window))
    weights = weights / weights.sum()
    wma = np.sum(recent_data * weights)
    x = np.arange(len(recent_data))
    coeffs = np.polyfit(x, recent_data, 1)
    trend = coeffs[0]
    return wma, trend

def exponential_smoothing(data, alpha=0.3):
    """Exponential Smoothing dengan trend"""
    smoothed = [data[0]]
    for i in range(1, len(data)):
        smoothed.append(alpha * data[i] + (1 - alpha) * smoothed[i-1])
    recent_smooth = smoothed[-30:]
    x = np.arange(len(recent_smooth))
    coeffs = np.polyfit(x, recent_smooth, 1)
    trend = coeffs[0]
    return smoothed[-1], trend

def create_province_forecast(daily_data, province_name, days_ahead=75):
    """Create forecast untuk provinsi menggunakan ensemble method"""
    
    print(f"  → Membuat forecast untuk {province_name}...")
    
    # Analyze New Year pattern from 2025 data
    event_factors = analyze_new_year_pattern_province(daily_data)
    baseline_avg = daily_data.tail(30)['Traffic_Total(TB)'].mean()
    
    # Prepare forecast
    last_date = daily_data['Date'].max()
    forecast_dates = [last_date + timedelta(days=i) for i in range(1, days_ahead + 1)]
    
    forecasts = []
    traffic_data = daily_data['Traffic_Total(TB)'].values
    
    # Ensemble forecasting dengan trend
    ma_base, ma_trend = moving_average_forecast(traffic_data, window=7)
    wma_base, wma_trend = weighted_moving_average(traffic_data, window=14)
    es_base, es_trend = exponential_smoothing(traffic_data, alpha=0.3)
    
    base_value = (ma_base + wma_base + es_base) / 3
    trend = (ma_trend + wma_trend + es_trend) / 3
    
    # Event calendar dengan daily patterns dari analisis
    daily_patterns = {}
    ny_2026_dates = pd.date_range('2025-12-25', '2026-01-07')
    for date in ny_2026_dates:
        date_2025 = date.replace(year=2024)
        date_str_2025 = date_2025.strftime('%Y-%m-%d')
        if date_str_2025 in event_factors:
            daily_patterns[date] = event_factors[date_str_2025]
    
    # Generate forecast
    for i, forecast_date in enumerate(forecast_dates):
        # Base forecast dengan trend
        if forecast_date in daily_patterns:
            # Untuk event dates, gunakan baseline
            base_forecast = baseline_avg
        else:
            # Untuk normal days, gunakan base + trend
            smoothed_trend = trend * 0.5  # Smooth the trend
            base_forecast = base_value + (smoothed_trend * i)
        
        # Weekly seasonality (weekend effect)
        day_of_week = forecast_date.dayofweek
        weekly_factor = 1.05 if day_of_week in [4, 5, 6] else 1.0  # Fri, Sat, Sun
        
        # Event factor
        ny_factor = daily_patterns.get(forecast_date, 1.0)
        
        # Combine factors
        forecast = base_forecast * weekly_factor * ny_factor
        
        # Add noise for natural variation
        noise_level = 0.01 if ny_factor > 1.0 else 0.02
        noise = np.random.normal(0, base_forecast * noise_level)
        forecast += noise
        forecast = max(forecast, 0)  # Ensure non-negative
        
        forecasts.append(forecast)
        traffic_data = np.append(traffic_data, forecast)
    
    # Create forecast dataframe
    df_forecast = pd.DataFrame({
        'Date': forecast_dates,
        'Traffic_Total(TB)': forecasts
    })
    
    # Add confidence intervals
    df_forecast['Lower_Bound'] = df_forecast['Traffic_Total(TB)'] * 0.9
    df_forecast['Upper_Bound'] = df_forecast['Traffic_Total(TB)'] * 1.1
    
    return df_forecast

def save_province_forecast(df_forecast, province_name):
    """Save forecast results untuk provinsi"""
    
    # Create output directory
    output_dir = Path("forecast_results/03_provinsi")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save CSV
    filename = f"{province_name.lower().replace(' ', '_')}.csv"
    filepath = output_dir / filename
    df_forecast.to_csv(filepath, index=False)
    
    return filepath

def create_visualization(daily_data, df_forecast, province_name):
    """Create visualization dengan statistics summary table"""
    
    # Create figure with GridSpec
    fig = plt.figure(figsize=(20, 12))
    gs = gridspec.GridSpec(2, 2, figure=fig, hspace=0.3, wspace=0.25)
    
    # Plot 1: Time Series (TOP - FULL WIDTH)
    ax1 = fig.add_subplot(gs[0, :])
    
    # Plot historical
    ax1.plot(daily_data['Date'], daily_data['Traffic_Total(TB)'],
            'o-', color='#2E86AB', linewidth=2, markersize=3, 
            label='Historical', alpha=0.8)
    
    # Plot forecast
    ax1.plot(df_forecast['Date'], df_forecast['Traffic_Total(TB)'],
            'o-', color='#E63946', linewidth=2, markersize=3, 
            label='Forecast', alpha=0.8)
    
    # Confidence interval
    ax1.fill_between(df_forecast['Date'],
                    df_forecast['Lower_Bound'],
                    df_forecast['Upper_Bound'],
                    alpha=0.2, color='#E63946', label='Confidence Interval')
    
    # Mark last historical point
    last_date = daily_data['Date'].iloc[-1]
    ax1.axvline(x=last_date, color='green', linestyle='--', linewidth=2, alpha=0.7,
               label=f'Last Historical: {last_date.strftime("%Y-%m-%d")}')
    
    ax1.set_xlabel('Date', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Traffic (TB)', fontsize=12, fontweight='bold')
    ax1.set_title('Time Series: Historical + Forecast', fontsize=14, fontweight='bold', pad=15)
    ax1.legend(loc='best', fontsize=10)
    ax1.grid(True, alpha=0.3)
    plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)
    
    # Plot 2: Statistics Summary Table (BOTTOM LEFT)
    ax2 = fig.add_subplot(gs[1, 0])
    ax2.axis('off')
    
    hist_mean = daily_data['Traffic_Total(TB)'].mean()
    hist_std = daily_data['Traffic_Total(TB)'].std()
    hist_min = daily_data['Traffic_Total(TB)'].min()
    hist_max = daily_data['Traffic_Total(TB)'].max()

    fore_mean = df_forecast['Traffic_Total(TB)'].mean()
    fore_std = df_forecast['Traffic_Total(TB)'].std()
    fore_min = df_forecast['Traffic_Total(TB)'].min()
    fore_max = df_forecast['Traffic_Total(TB)'].max()

    # Create table data for proper alignment
    table_data = [
        ['HISTORICAL:', ''],
        ['  • Data Points', f': {len(daily_data)} hari'],
        ['  • Mean Traffic', f': {hist_mean:,.2f} TB/hari'],
        ['  • Std Deviation', f': {hist_std:,.2f} TB'],
        ['  • Min Traffic', f': {hist_min:,.2f} TB'],
        ['  • Max Traffic', f': {hist_max:,.2f} TB'],
        ['', ''],
        ['FORECAST:', ''],
        ['  • Data Points', f': {len(df_forecast)} hari'],
        ['  • Mean Traffic', f': {fore_mean:,.2f} TB/hari'],
        ['  • Std Deviation', f': {fore_std:,.2f} TB'],
        ['  • Min Traffic', f': {fore_min:,.2f} TB'],
        ['  • Max Traffic', f': {fore_max:,.2f} TB'],
        ['', ''],
        ['COMPARISON:', ''],
        ['  • Mean Change', f': {fore_mean - hist_mean:+,.2f} TB'],
        ['  • Percentage', f': {((fore_mean - hist_mean)/hist_mean)*100:+.2f}%'],
    ]
    
    # Create table
    table = ax2.table(cellText=table_data, cellLoc='left', loc='center',
                     colWidths=[0.45, 0.55],
                     bbox=[0.05, 0.05, 0.9, 0.9])
    
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 1.8)
    
    # Style cells
    for i, row in enumerate(table_data):
        for j in range(2):
            cell = table[(i, j)]
            cell.set_edgecolor('none')
            
            # Section headers
            if row[0] in ['HISTORICAL:', 'FORECAST:', 'COMPARISON:']:
                cell.set_facecolor('wheat')
                cell.set_alpha(0.3)
                cell.set_text_props(weight='bold', fontsize=10)
            # Empty rows
            elif row[0] == '':
                cell.set_facecolor('white')
                cell.set_alpha(0)
            # Data rows
            else:
                cell.set_facecolor('white')
                cell.set_alpha(0)
                cell.set_text_props(fontsize=9, family='monospace')
    
    # Add title
    ax2.set_title('STATISTICS SUMMARY', fontsize=11, fontweight='bold', pad=10, loc='center')
    
    # Plot 3: Distribution Histogram (BOTTOM RIGHT)
    ax3 = fig.add_subplot(gs[1, 1])
    
    # Plot distributions
    ax3.hist(daily_data['Traffic_Total(TB)'], bins=30, alpha=0.6, 
            color='#2E86AB', label='Historical', edgecolor='black')
    ax3.hist(df_forecast['Traffic_Total(TB)'], bins=20, alpha=0.6,
            color='#E63946', label='Forecast', edgecolor='black')
    
    # Add mean lines
    ax3.axvline(hist_mean, color='#2E86AB', linestyle='--', linewidth=2)
    ax3.axvline(fore_mean, color='#E63946', linestyle='--', linewidth=2)
    
    ax3.set_xlabel('Traffic (TB)', fontsize=11, fontweight='bold')
    ax3.set_ylabel('Frequency', fontsize=11, fontweight='bold')
    ax3.set_title('Distribution: Historical vs Forecast', fontsize=12, fontweight='bold', pad=10)
    ax3.legend(loc='best', fontsize=9)
    ax3.grid(True, alpha=0.3, axis='y')
    
    # Main title
    fig.suptitle(f'FORECAST TRAFFIC: {province_name.upper()}\nHistorical + Forecast (Oct 2025 - Jan 2026)',
                fontsize=16, fontweight='bold', y=0.98)
    
    # Save
    output_dir = Path("forecast_results/03_provinsi")
    filename = f"{province_name.lower().replace(' ', '_')}_forecast.png"
    filepath = output_dir / filename
    plt.savefig(filepath, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    
    return filepath

def create_summary_comparison():
    """Create summary comparison: Total vs Sum of Provinces"""
    
    print("\n📊 Membuat Summary Comparison...")
    
    # Load total forecast
    df_total = pd.read_csv("forecast_results/01_main/forecast_data.csv")
    df_total['Date'] = pd.to_datetime(df_total['Date'])
    
    # Load all province forecasts
    province_dir = Path("forecast_results/03_provinsi")
    province_files = [f for f in province_dir.glob("*.csv") if f.name != "comparison_total_vs_provinces.csv"]
    
    # Sum all provinces
    df_sum_provinces = None
    for prov_file in province_files:
        df_prov = pd.read_csv(prov_file)
        df_prov['Date'] = pd.to_datetime(df_prov['Date'])
        
        # Check if column exists
        if 'Traffic_Total(TB)' not in df_prov.columns:
            print(f"  ⚠️  Skipping {prov_file.name} - kolom tidak lengkap")
            continue
        
        if df_sum_provinces is None:
            df_sum_provinces = df_prov[['Date', 'Traffic_Total(TB)']].copy()
            df_sum_provinces.rename(columns={'Traffic_Total(TB)': 'Sum_Provinces'}, inplace=True)
        else:
            df_sum_provinces['Sum_Provinces'] += df_prov['Traffic_Total(TB)'].values
    
    # Merge with total forecast
    df_comparison = df_total[['Date', 'Traffic_Total(TB)']].copy()
    df_comparison.rename(columns={'Traffic_Total(TB)': 'Forecast_Total'}, inplace=True)
    df_comparison = df_comparison.merge(df_sum_provinces, on='Date', how='left')
    
    # Calculate difference
    df_comparison['Difference'] = df_comparison['Sum_Provinces'] - df_comparison['Forecast_Total']
    df_comparison['Pct_Difference'] = (df_comparison['Difference'] / df_comparison['Forecast_Total']) * 100
    
    # Statistics
    avg_diff = df_comparison['Difference'].mean()
    avg_pct = df_comparison['Pct_Difference'].mean()
    max_diff = df_comparison['Difference'].abs().max()
    
    print(f"\n  ✓ Rata-rata selisih  : {avg_diff:+.2f} TB ({avg_pct:+.2f}%)")
    print(f"  ✓ Selisih maksimal   : {max_diff:.2f} TB")
    
    # Save comparison
    comparison_file = Path("forecast_results/03_provinsi/comparison_total_vs_provinces.csv")
    df_comparison.to_csv(comparison_file, index=False)
    print(f"  ✓ Disimpan: {comparison_file}")
    
    return df_comparison

def main():
    """Main function"""
    print("=" * 70)
    print("  PROGRAM 1B: FORECAST PER PROVINSI")
    print("=" * 70)
    print("\n🚀 Memulai forecast individual per provinsi...\n")
    
    # Check if total forecast exists
    if not Path("forecast_results/01_main/forecast_data.csv").exists():
        print("❌ Error: Forecast total tidak ditemukan!")
        print("💡 Jalankan '1_run_forecast.py' terlebih dahulu")
        return
    
    # Load province list
    df = pd.read_excel("Traffic_VLR_Java_2024-2025.xlsx", sheet_name=0)
    provinces = sorted(df['PROVINCE'].unique())
    
    print(f"📍 Ditemukan {len(provinces)} provinsi:")
    for i, prov in enumerate(provinces, 1):
        print(f"   {i}. {prov}")
    
    print(f"\n{'=' * 70}")
    print("📊 MEMULAI FORECAST PER PROVINSI")
    print('=' * 70)
    
    # Process each province
    forecast_summary = []
    
    for idx, province in enumerate(provinces, 1):
        print(f"\n[{idx}/{len(provinces)}] {province}")
        print("-" * 70)
        
        # Load and prepare data
        daily_data = load_and_prepare_province_data(province)
        print(f"  ✓ Loaded {len(daily_data)} hari data")
        
        # Create forecast
        df_forecast = create_province_forecast(daily_data, province)
        
        # Save forecast
        filepath = save_province_forecast(df_forecast, province)
        print(f"  ✓ Disimpan: {filepath}")
        
        # Create visualization
        viz_filepath = create_visualization(daily_data, df_forecast, province)
        print(f"  ✓ Visualisasi: {viz_filepath}")
        
        # Add to summary
        avg_forecast = df_forecast['Traffic_Total(TB)'].mean()
        peak_forecast = df_forecast['Traffic_Total(TB)'].max()
        forecast_summary.append({
            'Province': province,
            'Avg_Historical': daily_data['Traffic_Total(TB)'].mean(),
            'Avg_Forecast': avg_forecast,
            'Peak_Forecast': peak_forecast,
            'Days': len(df_forecast)
        })
    
    # Create summary dataframe
    df_summary = pd.DataFrame(forecast_summary)
    
    # Save summary
    print(f"\n{'=' * 70}")
    print("📄 MENYIMPAN SUMMARY")
    print('=' * 70)
    
    summary_file = Path("forecast_results/03_provinsi/summary_all_provinces.xlsx")
    with pd.ExcelWriter(summary_file, engine='openpyxl') as writer:
        df_summary.to_excel(writer, sheet_name='Summary', index=False)
    
    print(f"  ✓ Disimpan: {summary_file}")
    
    # Create comparison with total forecast
    df_comparison = create_summary_comparison()
    
    # Final summary
    print(f"\n{'=' * 70}")
    print("✅ FORECAST PER PROVINSI SELESAI!")
    print('=' * 70)
    print(f"\n📁 Output Files:")
    print(f"  • forecast_results/03_provinsi/[provinsi].csv (6 files)")
    print(f"  • forecast_results/03_provinsi/summary_all_provinces.xlsx")
    print(f"  • forecast_results/03_provinsi/comparison_total_vs_provinces.csv")
    print(f"\n💡 Summary Statistics:")
    print(f"  • Total Provinsi     : {len(provinces)}")
    print(f"  • Periode Forecast   : {len(df_forecast)} hari")
    print(f"  • Rata-rata Total    : {df_summary['Avg_Forecast'].sum():.2f} TB")
    print('=' * 70)

if __name__ == "__main__":
    main()
