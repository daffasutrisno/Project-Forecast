"""
FORECAST BY REGIONAL
====================
Membuat forecast traffic untuk masing-masing regional (3 regional)
dengan konsep sama seperti forecast per provinsi.

Input:
  - Traffic_VLR_Java_2024-2025.xlsx

Output:
  - forecast_results/02_regional/bali_nusra.csv
  - forecast_results/02_regional/central_java.csv
  - forecast_results/02_regional/east_java.csv
  - forecast_results/02_regional/[regional]_forecast.png (3 files)

Fungsi:
  - Forecast per regional: Bali Nusra, Central Java, East Java
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

def load_and_prepare_regional_data(region_name):
    """Load data dan aggregate per hari untuk regional tertentu"""
    print(f"  → Loading data untuk {region_name}...")
    
    df = pd.read_excel("Traffic_VLR_Java_2024-2025.xlsx", sheet_name=0)
    df['Date'] = pd.to_datetime(df['Date'])
    
    # Filter by region
    df_region = df[df['REGION IOH'] == region_name].copy()
    
    # Aggregate per hari
    daily_data = df_region.groupby('Date').agg({
        'Traffic_H3I (TB)': 'sum',
        'Traffic_IM3 (TB)': 'sum',
        'Traffic_Total(TB)': 'sum'
    }).reset_index()
    
    daily_data = daily_data.sort_values('Date').reset_index(drop=True)
    
    return daily_data

def analyze_new_year_pattern_regional(daily_data):
    """Analisis pattern Tahun Baru dari data 2025 untuk regional"""
    
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

def create_regional_forecast(daily_data, region_name, days_ahead=75):
    """Create forecast untuk regional menggunakan ensemble method"""
    
    print(f"  → Membuat forecast untuk {region_name}...")
    
    # Analyze New Year pattern from 2025 data
    event_factors = analyze_new_year_pattern_regional(daily_data)
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

def save_regional_forecast(df_forecast, region_name):
    """Save forecast results untuk regional"""
    
    # Create output directory
    output_dir = Path("forecast_results/02_regional")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save CSV
    filename = f"{region_name.lower().replace(' ', '_')}.csv"
    filepath = output_dir / filename
    df_forecast.to_csv(filepath, index=False)
    
    return filepath

def create_visualization(daily_data, df_forecast, region_name):
    """Create visualization untuk regional"""
    
    output_dir = Path("forecast_results/02_regional")
    
    # Prepare data
    last_historical_date = daily_data['Date'].max()
    
    fig = plt.figure(figsize=(20, 10))
    gs = fig.add_gridspec(2, 2, hspace=0.3, wspace=0.25)
    
    # Main title
    fig.suptitle(f'FORECAST TRAFFIC: {region_name.upper()}\n' +
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
    filename = f"{region_name.lower().replace(' ', '_')}_forecast.png"
    filepath = output_dir / filename
    plt.savefig(filepath, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    
    return filepath

def create_summary_comparison(regional_forecasts):
    """Create summary comparison antar regional"""
    
    output_dir = Path("forecast_results/02_regional")
    
    fig, axes = plt.subplots(2, 2, figsize=(18, 12))
    # Slightly lower suptitle to give more room for subplot titles and xlabels
    fig.suptitle('PERBANDINGAN FORECAST TRAFFIC ANTAR REGIONAL',
                 fontsize=16, fontweight='bold', y=0.96)
    # Increase vertical spacing between rows and a bit of horizontal spacing
    plt.subplots_adjust(hspace=0.5, wspace=0.28)
    
    # Plot 1: Forecast Time Series
    ax1 = axes[0, 0]
    colors = ['#2E86AB', '#E63946', '#06A77D']
    
    for idx, (region, data) in enumerate(regional_forecasts.items()):
        ax1.plot(data['forecast']['Date'], data['forecast']['Traffic_Total(TB)'],
                'o-', color=colors[idx], linewidth=2, markersize=3,
                label=region, alpha=0.8)
    
    ax1.set_xlabel('Date', fontsize=11, fontweight='bold')
    ax1.set_ylabel('Traffic (TB)', fontsize=11, fontweight='bold')
    ax1.set_title('Forecast Comparison', fontsize=12, fontweight='bold', pad=10)
    ax1.legend(loc='best', fontsize=9)
    ax1.grid(True, alpha=0.3)
    plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)
    
    # Plot 2: Average Comparison
    ax2 = axes[0, 1]
    
    regions = []
    hist_avgs = []
    fore_avgs = []
    
    for region, data in regional_forecasts.items():
        regions.append(region)
        hist_avgs.append(data['historical']['Traffic_Total(TB)'].mean())
        fore_avgs.append(data['forecast']['Traffic_Total(TB)'].mean())
    
    x = np.arange(len(regions))
    width = 0.35
    
    ax2.bar(x - width/2, hist_avgs, width, label='Historical', color='#2E86AB', alpha=0.8)
    ax2.bar(x + width/2, fore_avgs, width, label='Forecast', color='#E63946', alpha=0.8)
    
    # Add value labels
    for i, (h, f) in enumerate(zip(hist_avgs, fore_avgs)):
        ax2.text(i - width/2, h, f'{h:,.0f}', ha='center', va='bottom', fontsize=8)
        ax2.text(i + width/2, f, f'{f:,.0f}', ha='center', va='bottom', fontsize=8)
    
    ax2.set_xlabel('Regional', fontsize=11, fontweight='bold')
    ax2.set_ylabel('Avg Traffic (TB/hari)', fontsize=11, fontweight='bold')
    # reduce title pad so it doesn't push into the lower panels
    ax2.set_title('Average Traffic Comparison', fontsize=12, fontweight='bold', pad=8)
    ax2.set_xticks(x)
    ax2.set_xticklabels(regions, rotation=12)
    ax2.legend(loc='upper right', fontsize=9)
    ax2.grid(True, alpha=0.3, axis='y')
    
    # Plot 3: Distribution
    ax3 = axes[1, 0]
    
    for idx, (region, data) in enumerate(regional_forecasts.items()):
        ax3.hist(data['forecast']['Traffic_Total(TB)'], bins=20, alpha=0.5,
                color=colors[idx], label=region, edgecolor='black')
    
    ax3.set_xlabel('Traffic (TB)', fontsize=10, fontweight='bold')
    ax3.set_ylabel('Frequency', fontsize=10, fontweight='bold')
    ax3.set_title('Forecast Distribution', fontsize=11, fontweight='bold', pad=12)
    ax3.legend(loc='upper right', fontsize=8)
    ax3.grid(True, alpha=0.3, axis='y')
    ax3.tick_params(axis='both', labelsize=8)
    
    # Plot 4: Summary Table
    ax4 = axes[1, 1]
    ax4.axis('off')
    
    table_data = []
    for region, data in regional_forecasts.items():
        hist_mean = data['historical']['Traffic_Total(TB)'].mean()
        fore_mean = data['forecast']['Traffic_Total(TB)'].mean()
        change = fore_mean - hist_mean
        change_pct = (change / hist_mean) * 100
        
        table_data.append([
            region,
            f"{hist_mean:,.0f}",
            f"{fore_mean:,.0f}",
            f"{change:+,.0f}",
            f"{change_pct:+.2f}%"
        ])
    
    # Add total
    total_hist = sum(hist_avgs)
    total_fore = sum(fore_avgs)
    total_change = total_fore - total_hist
    total_pct = (total_change / total_hist) * 100
    
    table_data.append([
        'TOTAL',
        f"{total_hist:,.0f}",
        f"{total_fore:,.0f}",
        f"{total_change:+,.0f}",
        f"{total_pct:+.2f}%"
    ])
    
    col_labels = ['Regional', 'Historical\nAvg (TB)', 'Forecast\nAvg (TB)', 'Change\n(TB)', 'Change\n(%)']
    
    # Create table with better positioning - adjusted to avoid overlap
    # Move table a bit lower and reduce height so bar chart xlabels and title do not collide
    table = ax4.table(cellText=table_data, colLabels=col_labels,
                     cellLoc='center', loc='center',
                     colWidths=[0.24, 0.19, 0.19, 0.19, 0.19],
                     bbox=[0.05, 0.05, 0.9, 0.82])

    table.auto_set_font_size(False)
    table.set_fontsize(9)
    # Slightly reduce vertical scaling so table fits cleanly
    table.scale(1, 1.9)

    # Style header
    for i in range(len(col_labels)):
        cell = table[(0, i)]
        cell.set_facecolor('#2C3E50')
        cell.set_text_props(weight='bold', color='white', fontsize=9)
        cell.set_height(0.055)

    # Style data rows
    for i in range(1, len(table_data) + 1):
        for j in range(len(col_labels)):
            cell = table[(i, j)]
            cell.set_height(0.048)
            
            # Set alignment: left for regional names, center for numbers
            if j == 0:
                cell.set_text_props(ha='left', fontsize=9)
                # Add left padding for regional names
                cell.PAD = 0.05
            else:
                cell.set_text_props(ha='center', fontsize=9)

            if i == len(table_data):
                cell.set_facecolor('#F39C12')
                cell.set_text_props(weight='bold', fontsize=9)
                if j == 0:
                    cell.set_text_props(ha='left', weight='bold', fontsize=9)
            else:
                cell.set_facecolor('#ECF0F1' if i % 2 == 0 else 'white')
                if j == 0:
                    cell.set_text_props(ha='left', fontsize=9)

    # Move the title closer to the table (smaller pad) so it doesn't overlap with the bar chart
    ax4.set_title('Summary Statistics', fontsize=12, fontweight='bold', pad=10)
    
    # Save
    # tighten layout and reserve small space for suptitle
    fig.tight_layout(rect=[0, 0, 1, 0.94])
    filepath = output_dir / 'summary_comparison_regional.png'
    plt.savefig(filepath, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    
    return filepath

def main():
    """Main function"""
    print("="*80)
    print("  FORECAST TRAFFIC PER REGIONAL")
    print("="*80)
    
    # Load data
    print("\nMembaca data...")
    df = pd.read_excel("Traffic_VLR_Java_2024-2025.xlsx", sheet_name=0)
    
    # Get regions
    regions = sorted(df['REGION IOH'].unique())
    print(f"\nDitemukan {len(regions)} regional:")
    for i, region in enumerate(regions, 1):
        print(f"  {i}. {region}")
    
    print("\n" + "="*80)
    print("  MEMULAI FORECAST PER REGIONAL")
    print("="*80)
    
    regional_forecasts = {}
    
    for idx, region in enumerate(regions, 1):
        print(f"\n[{idx}/{len(regions)}] {region}")
        print("-"*80)
        
        # Load data
        daily_data = load_and_prepare_regional_data(region)
        print(f"  Data points: {len(daily_data)} hari")
        print(f"  Range: {daily_data['Date'].min().date()} s/d {daily_data['Date'].max().date()}")
        print(f"  Traffic mean: {daily_data['Traffic_Total(TB)'].mean():.2f} TB")
        
        # Create forecast
        df_forecast = create_regional_forecast(daily_data, region)
        
        # Save CSV
        csv_path = save_regional_forecast(df_forecast, region)
        print(f"  Tersimpan: {csv_path}")
        
        # Create visualization
        viz_path = create_visualization(daily_data, df_forecast, region)
        print(f"  Visualisasi: {viz_path}")
        
        # Store for summary
        regional_forecasts[region] = {
            'historical': daily_data,
            'forecast': df_forecast
        }
        
        print(f"  SELESAI untuk {region}")
    
    # Create summary comparison
    print("\n" + "="*80)
    print("  MEMBUAT SUMMARY COMPARISON")
    print("="*80)
    
    summary_path = create_summary_comparison(regional_forecasts)
    print(f"\nSummary tersimpan: {summary_path}")
    
    # Print final summary
    print("\n" + "="*80)
    print("  SUMMARY HASIL")
    print("="*80)
    
    print(f"\n{'Regional':<20} {'Hist Avg':<15} {'Fore Avg':<15} {'Change':<15} {'%'}")
    print("-"*80)
    
    for region, data in regional_forecasts.items():
        hist_mean = data['historical']['Traffic_Total(TB)'].mean()
        fore_mean = data['forecast']['Traffic_Total(TB)'].mean()
        change = fore_mean - hist_mean
        change_pct = (change / hist_mean) * 100
        
        print(f"{region:<20} {hist_mean:>13,.2f} {fore_mean:>13,.2f} {change:>+13,.2f} {change_pct:>+6.2f}%")
    
    print("\n" + "="*80)
    print("  SEMUA FORECAST REGIONAL BERHASIL DIBUAT!")
    print("="*80)
    
    print("\nFile yang dihasilkan:")
    print("\n  CSV FILES:")
    for region in regions:
        filename = region.lower().replace(' ', '_')
        print(f"    - forecast_results/forecast_regional/{filename}.csv")
    
    print("\n  PNG FILES:")
    for region in regions:
        filename = region.lower().replace(' ', '_')
        print(f"    - forecast_results/forecast_regional/{filename}_forecast.png")
    
    print("\n  SUMMARY:")
    print("    - forecast_results/forecast_regional/summary_comparison_regional.png")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    main()
