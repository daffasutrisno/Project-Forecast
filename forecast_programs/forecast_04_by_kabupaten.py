"""
FORECAST BY KABUPATEN
======================
Membuat forecast traffic untuk masing-masing kabupaten (119 kabupaten)
dengan konsep sama seperti forecast per regional.

Input:
  - Traffic_VLR_Java_2024-2025.xlsx

Output:
  - forecast_results/04_kabupaten/[nama_kabupaten]_forecast.csv (119 files)
  - forecast_results/04_kabupaten/[nama_kabupaten]_forecast.png (119 files)

Fungsi:
  - Forecast untuk semua 119 kabupaten di Jawa dan Nusa Tenggara
  - Visualisasi dengan chart horizontal + statistics + distribution
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import datetime, timedelta
import warnings

warnings.filterwarnings('ignore')
np.random.seed(42)

def load_and_prepare_kabupaten_data(kabupaten_name):
    """Load data dan aggregate per hari untuk kabupaten tertentu"""
    print(f"  → Loading data untuk {kabupaten_name}...")
    
    df = pd.read_excel("Traffic_VLR_Java_2024-2025.xlsx", sheet_name=0)
    df['Date'] = pd.to_datetime(df['Date'])
    
    # Filter by kabupaten
    df_kabupaten = df[df['KABUPATEN IOH'] == kabupaten_name].copy()
    
    # Aggregate per hari
    daily_data = df_kabupaten.groupby('Date').agg({
        'Traffic_H3I (TB)': 'sum',
        'Traffic_IM3 (TB)': 'sum',
        'Traffic_Total(TB)': 'sum'
    }).reset_index()
    
    daily_data = daily_data.sort_values('Date').reset_index(drop=True)
    
    return daily_data

def analyze_new_year_pattern_kabupaten(daily_data):
    """Analisis pattern Tahun Baru dari data 2025 untuk kabupaten"""
    
    # Get data Dec 25, 2024 - Jan 7, 2025
    start_date = pd.Timestamp('2024-12-25')
    end_date = pd.Timestamp('2025-01-07')
    
    ny_period = daily_data[(daily_data['Date'] >= start_date) & 
                           (daily_data['Date'] <= end_date)].copy()
    
    if len(ny_period) == 0:
        return {}
    
    # Baseline dari Des 1-24
    baseline_start = pd.Timestamp('2024-12-01')
    baseline_end = pd.Timestamp('2024-12-24')
    baseline_period = daily_data[(daily_data['Date'] >= baseline_start) & 
                                  (daily_data['Date'] <= baseline_end)]
    
    if len(baseline_period) == 0:
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

def create_kabupaten_forecast(daily_data, kabupaten_name, days_ahead=75):
    """Create forecast untuk kabupaten menggunakan ensemble method"""
    
    print(f"  → Membuat forecast untuk {kabupaten_name}...")
    
    # Analyze New Year pattern from 2025 data
    event_factors = analyze_new_year_pattern_kabupaten(daily_data)
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

def save_kabupaten_forecast(df_forecast, kabupaten_name):
    """Save forecast results untuk kabupaten"""
    
    # Create output directory
    output_dir = Path("forecast_results/04_kabupaten")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save CSV
    filename = f"{kabupaten_name.lower().replace(' ', '_')}.csv"
    filepath = output_dir / filename
    df_forecast.to_csv(filepath, index=False)
    
    return filepath

def create_visualization(daily_data, df_forecast, kabupaten_name):
    """Create visualization untuk kabupaten"""
    
    output_dir = Path("forecast_results/04_kabupaten")
    
    # Prepare data
    last_historical_date = daily_data['Date'].max()
    
    fig = plt.figure(figsize=(20, 10))
    gs = fig.add_gridspec(2, 2, hspace=0.3, wspace=0.25)
    
    # Main title
    fig.suptitle(f'FORECAST TRAFFIC: {kabupaten_name.upper()}\n' +
                 f'Historical + Forecast (Oct 2025 - Jan 2026)',
                 fontsize=18, fontweight='bold', y=0.98)
    
    # Plot 1: Full Time Series
    ax1 = fig.add_subplot(gs[0, :])
    
    ax1.plot(daily_data['Date'], daily_data['Traffic_Total(TB)'],
            'o-', color='#2E86AB', linewidth=2, markersize=3, label='Historical', alpha=0.8)
    ax1.plot(df_forecast['Date'], df_forecast['Traffic_Total(TB)'],
            'o-', color='#E63946', linewidth=2, markersize=3, label='Forecast', alpha=0.8)
    
    # Confidence interval
    ax1.fill_between(df_forecast['Date'],
                     df_forecast['Lower_Bound'],
                     df_forecast['Upper_Bound'],
                     alpha=0.2, color='#E63946', label='Confidence Interval')
    
    ax1.axvline(last_historical_date, color='green', linestyle='--', linewidth=2, alpha=0.7,
               label=f'Last Historical: {last_historical_date.date()}')
    
    ax1.set_xlabel('Date', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Traffic (TB)', fontsize=12, fontweight='bold')
    ax1.set_title('Time Series: Historical + Forecast', fontsize=14, fontweight='bold', pad=15)
    ax1.legend(loc='best', fontsize=10)
    ax1.grid(True, alpha=0.3)
    plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)
    
    # Plot 2: Statistics - Using table for proper alignment
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
            cell.set_facecolor('wheat' if i == 0 or row[0].startswith('HISTORICAL') or row[0].startswith('FORECAST') or row[0].startswith('COMPARISON') else 'white')
            cell.set_alpha(0.3 if row[0].startswith('HISTORICAL') or row[0].startswith('FORECAST') or row[0].startswith('COMPARISON') else 0)
            
            # Bold for section headers
            if row[0].endswith(':') and not row[0].startswith('  •'):
                cell.set_text_props(weight='bold', fontsize=10)
            else:
                cell.set_text_props(fontsize=9, family='monospace')
    
    # Add title
    ax2.set_title('STATISTICS SUMMARY', fontsize=11, fontweight='bold', pad=10, loc='center')
    
    # Plot 3: Distribution
    ax3 = fig.add_subplot(gs[1, 1])
    
    ax3.hist(daily_data['Traffic_Total(TB)'], bins=30, alpha=0.6,
            color='#2E86AB', label='Historical', edgecolor='black')
    ax3.hist(df_forecast['Traffic_Total(TB)'], bins=20, alpha=0.6,
            color='#E63946', label='Forecast', edgecolor='black')
    
    ax3.axvline(hist_mean, color='#2E86AB', linestyle='--', linewidth=2)
    ax3.axvline(fore_mean, color='#E63946', linestyle='--', linewidth=2)
    
    ax3.set_xlabel('Traffic (TB)', fontsize=11, fontweight='bold')
    ax3.set_ylabel('Frequency', fontsize=11, fontweight='bold')
    ax3.set_title('Distribution: Historical vs Forecast', fontsize=12, fontweight='bold', pad=10)
    ax3.legend(loc='best', fontsize=9)
    ax3.grid(True, alpha=0.3, axis='y')
    
    # Save
    filename = f"{kabupaten_name.lower().replace(' ', '_')}_forecast.png"
    filepath = output_dir / filename
    plt.savefig(filepath, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    
    return filepath

def main():
    """Main function"""
    print("="*80)
    print("  FORECAST TRAFFIC PER KABUPATEN IOH")
    print("="*80)
    
    # Load data
    print("\nMembaca data...")
    df = pd.read_excel("Traffic_VLR_Java_2024-2025.xlsx", sheet_name=0)
    
    # Get kabupaten
    kabupaten_list = sorted(df['KABUPATEN IOH'].unique())
    print(f"\nDitemukan {len(kabupaten_list)} kabupaten")
    
    print("\n" + "="*80)
    print("  MEMULAI FORECAST PER KABUPATEN")
    print("="*80)
    
    for idx, kabupaten in enumerate(kabupaten_list, 1):
        print(f"\n[{idx}/{len(kabupaten_list)}] {kabupaten}")
        print("-"*80)
        
        # Load data
        daily_data = load_and_prepare_kabupaten_data(kabupaten)
        
        # Skip if insufficient data
        if len(daily_data) < 30:
            print(f"  ⚠️  Data terlalu sedikit ({len(daily_data)} hari), skip...")
            continue
        
        print(f"  Data points: {len(daily_data)} hari")
        print(f"  Range: {daily_data['Date'].min().date()} s/d {daily_data['Date'].max().date()}")
        print(f"  Traffic mean: {daily_data['Traffic_Total(TB)'].mean():.2f} TB")
        
        # Create forecast
        df_forecast = create_kabupaten_forecast(daily_data, kabupaten)
        
        # Save CSV
        csv_path = save_kabupaten_forecast(df_forecast, kabupaten)
        print(f"  Tersimpan: {csv_path}")
        
        # Create visualization
        viz_path = create_visualization(daily_data, df_forecast, kabupaten)
        print(f"  Visualisasi: {viz_path}")
        
        print(f"  SELESAI untuk {kabupaten}")
    
    print("\n" + "="*80)
    print("  SEMUA FORECAST KABUPATEN BERHASIL DIBUAT!")
    print("="*80)
    
    print("\nFile yang dihasilkan:")
    print("  - forecast_results/forecast_kabupaten/*.csv (CSV files)")
    print("  - forecast_results/forecast_kabupaten/*.png (Visualizations)")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    main()
