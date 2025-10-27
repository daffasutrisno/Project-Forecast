"""
Traffic Forecasting - Prediksi Traffic hingga Tahun Baru 2026
Menggunakan berbagai metode forecasting dengan mempertimbangkan seasonality
dan lonjakan pada periode Tahun Baru
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Set style
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("husl")

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
    print("\n🎆 Menganalisis pola Tahun Baru 2025...")
    
    # Ambil data sekitar Tahun Baru 2025 (15 hari sebelum dan sesudah)
    new_year_2025 = pd.Timestamp('2025-01-01')
    start_date = new_year_2025 - timedelta(days=15)
    end_date = new_year_2025 + timedelta(days=15)
    
    new_year_data = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)].copy()
    
    if len(new_year_data) > 0:
        # Hitung rata-rata sebelum dan sesudah
        before_ny = new_year_data[new_year_data['Date'] < new_year_2025]['Traffic_Total(TB)'].mean()
        during_ny = new_year_data[new_year_data['Date'] == new_year_2025]['Traffic_Total(TB)'].values
        after_ny = new_year_data[new_year_data['Date'] > new_year_2025]['Traffic_Total(TB)'].head(7).mean()
        
        if len(during_ny) > 0:
            spike_ratio = during_ny[0] / before_ny if before_ny > 0 else 1.5
            print(f"  ✓ Traffic sebelum TahunBaru: {before_ny:.2f} TB")
            print(f"  ✓ Traffic pada TahunBaru: {during_ny[0]:.2f} TB")
            print(f"  ✓ Rasio lonjakan: {spike_ratio:.2%}")
            
            return {
                'spike_ratio': spike_ratio,
                'baseline_before': before_ny,
                'peak_value': during_ny[0],
                'baseline_after': after_ny,
                'pattern': new_year_data
            }
    
    # Default jika tidak ada data
    print("  ⚠ Menggunakan pola default (lonjakan 50%)")
    return {
        'spike_ratio': 1.5,
        'baseline_before': df['Traffic_Total(TB)'].mean(),
        'peak_value': df['Traffic_Total(TB)'].mean() * 1.5,
        'baseline_after': df['Traffic_Total(TB)'].mean(),
        'pattern': None
    }

def moving_average_forecast(df, periods=71, window=7):
    """Simple Moving Average dengan trend"""
    recent_data = df.tail(window)['Traffic_Total(TB)'].values
    ma = np.mean(recent_data)
    
    # Hitung trend
    x = np.arange(len(recent_data))
    coeffs = np.polyfit(x, recent_data, 1)
    trend = coeffs[0]
    
    return ma, trend

def weighted_moving_average(df, periods=71, window=14):
    """Weighted Moving Average - data terbaru diberi bobot lebih"""
    recent_data = df.tail(window)['Traffic_Total(TB)'].values
    weights = np.exp(np.linspace(-1, 0, window))
    weights = weights / weights.sum()
    wma = np.sum(recent_data * weights)
    
    # Trend
    x = np.arange(len(recent_data))
    coeffs = np.polyfit(x, recent_data, 1)
    trend = coeffs[0]
    
    return wma, trend

def exponential_smoothing(df, alpha=0.3):
    """Exponential Smoothing dengan trend"""
    data = df['Traffic_Total(TB)'].values
    
    # Simple exponential smoothing
    smoothed = [data[0]]
    for i in range(1, len(data)):
        smoothed.append(alpha * data[i] + (1 - alpha) * smoothed[i-1])
    
    # Hitung trend dari data yang sudah di-smooth
    recent_smooth = smoothed[-30:]
    x = np.arange(len(recent_smooth))
    coeffs = np.polyfit(x, recent_smooth, 1)
    trend = coeffs[0]
    
    return smoothed[-1], trend

def create_forecast(df, ny_pattern, forecast_days=71):
    """Buat forecast dengan berbagai metode"""
    print("\n📊 Membuat forecast...")
    
    last_date = df['Date'].max()
    forecast_dates = pd.date_range(start=last_date + timedelta(days=1), 
                                   periods=forecast_days, freq='D')
    
    # Berbagai metode forecasting
    ma_base, ma_trend = moving_average_forecast(df, window=7)
    wma_base, wma_trend = weighted_moving_average(df, window=14)
    es_base, es_trend = exponential_smoothing(df, alpha=0.3)
    
    # Rata-rata metode
    base_value = (ma_base + wma_base + es_base) / 3
    trend = (ma_trend + wma_trend + es_trend) / 3
    
    print(f"  ✓ Base value: {base_value:.2f} TB")
    print(f"  ✓ Trend: {trend:.4f} TB/hari")
    print(f"  ✓ Spike ratio TahunBaru: {ny_pattern['spike_ratio']:.2%}")
    
    # Generate forecast dengan seasonality dan Tahun Baru effect
    forecast_values = []
    new_year_2026 = pd.Timestamp('2026-01-01')
    
    for i, date in enumerate(forecast_dates):
        # Base forecast dengan trend
        base_forecast = base_value + (trend * i)
        
        # Weekly seasonality (weekend biasanya lebih tinggi)
        day_of_week = date.dayofweek
        if day_of_week in [4, 5, 6]:  # Jumat, Sabtu, Minggu
            weekly_factor = 1.1
        else:
            weekly_factor = 1.0
        
        # Tahun Baru effect
        days_to_ny = (new_year_2026 - date).days
        
        if -7 <= days_to_ny <= 7:  # 7 hari sebelum dan sesudah Tahun Baru
            if days_to_ny == 0:  # Tepat Tahun Baru
                ny_factor = ny_pattern['spike_ratio']
            elif days_to_ny > 0:  # Menjelang Tahun Baru
                ny_factor = 1 + (ny_pattern['spike_ratio'] - 1) * (1 - days_to_ny / 7)
            else:  # Setelah Tahun Baru
                ny_factor = 1 + (ny_pattern['spike_ratio'] - 1) * (1 + days_to_ny / 7)
        else:
            ny_factor = 1.0
        
        # Combine all factors
        forecast = base_forecast * weekly_factor * ny_factor
        
        # Add small random variation untuk realisme
        noise = np.random.normal(0, base_forecast * 0.02)
        forecast += noise
        
        # Pastikan tidak negatif
        forecast = max(forecast, 0)
        
        forecast_values.append(forecast)
    
    # Buat DataFrame hasil forecast
    forecast_df = pd.DataFrame({
        'Date': forecast_dates,
        'Traffic_Total(TB)': forecast_values,
        'Type': 'Forecast'
    })
    
    # Tambahkan confidence interval (±10%)
    forecast_df['Lower_Bound'] = forecast_df['Traffic_Total(TB)'] * 0.9
    forecast_df['Upper_Bound'] = forecast_df['Traffic_Total(TB)'] * 1.1
    
    return forecast_df

def create_visualizations(historical_df, forecast_df, ny_pattern, output_folder="forecast_results"):
    """Buat visualisasi forecast"""
    Path(output_folder).mkdir(exist_ok=True)
    
    print("\n📈 Membuat visualisasi...")
    
    # Forecast H3I dan IM3 berdasarkan proporsi historical
    avg_h3i_ratio = (historical_df['Traffic_H3I (TB)'] / historical_df['Traffic_Total(TB)']).mean()
    avg_im3_ratio = (historical_df['Traffic_IM3 (TB)'] / historical_df['Traffic_Total(TB)']).mean()
    
    forecast_df['Traffic_H3I (TB)'] = forecast_df['Traffic_Total(TB)'] * avg_h3i_ratio
    forecast_df['Traffic_IM3 (TB)'] = forecast_df['Traffic_Total(TB)'] * avg_im3_ratio
    
    # Chart Utama: Traffic Harian Total dengan Forecast (H3I + IM3 + Total)
    plt.figure(figsize=(20, 10))
    
    # Plot SEMUA historical data (solid lines)
    plt.plot(historical_df['Date'], historical_df['Traffic_Total(TB)'], 
             marker='o', linewidth=2.5, markersize=2.5, color='#2E86AB', 
             label='Total Traffic', alpha=0.9, zorder=3)
    plt.plot(historical_df['Date'], historical_df['Traffic_H3I (TB)'], 
             marker='s', linewidth=2, markersize=2, color='#A23B72', 
             label='H3I Traffic', alpha=0.8, zorder=3)
    plt.plot(historical_df['Date'], historical_df['Traffic_IM3 (TB)'], 
             marker='^', linewidth=2, markersize=2, color='#F18F01', 
             label='IM3 Traffic', alpha=0.8, zorder=3)
    
    # Background berbayang untuk area forecast
    plt.axvspan(forecast_df['Date'].min(), forecast_df['Date'].max(), 
                alpha=0.15, color='yellow', label='Forecast Period', zorder=0)
    
    # Plot forecast (dashed lines) - melanjutkan dari historical
    plt.plot(forecast_df['Date'], forecast_df['Traffic_Total(TB)'], 
             marker='o', linewidth=2.5, markersize=3, color='#2E86AB', 
             label='Total Traffic (Forecast)', linestyle='--', alpha=0.9, zorder=3)
    plt.plot(forecast_df['Date'], forecast_df['Traffic_H3I (TB)'], 
             marker='s', linewidth=2, markersize=3, color='#A23B72', 
             label='H3I Traffic (Forecast)', linestyle='--', alpha=0.8, zorder=3)
    plt.plot(forecast_df['Date'], forecast_df['Traffic_IM3 (TB)'], 
             marker='^', linewidth=2, markersize=3, color='#F18F01', 
             label='IM3 Traffic (Forecast)', linestyle='--', alpha=0.8, zorder=3)
    
    # Confidence interval untuk Total Traffic
    plt.fill_between(forecast_df['Date'], 
                     forecast_df['Lower_Bound'], 
                     forecast_df['Upper_Bound'], 
                     alpha=0.2, color='#2E86AB', zorder=1)
    
    # Highlight Tahun Baru 2026
    new_year_date = pd.Timestamp('2026-01-01')
    if new_year_date in forecast_df['Date'].values:
        ny_value_total = forecast_df[forecast_df['Date'] == new_year_date]['Traffic_Total(TB)'].values[0]
        ny_value_h3i = forecast_df[forecast_df['Date'] == new_year_date]['Traffic_H3I (TB)'].values[0]
        ny_value_im3 = forecast_df[forecast_df['Date'] == new_year_date]['Traffic_IM3 (TB)'].values[0]
        
        plt.axvline(x=new_year_date, color='gold', linestyle=':', linewidth=4, 
                   label='Tahun Baru 2026', alpha=0.8, zorder=4)
        plt.scatter([new_year_date], [ny_value_total], color='gold', s=400, 
                   marker='*', edgecolor='red', linewidth=2.5, zorder=5)
        plt.scatter([new_year_date], [ny_value_h3i], color='gold', s=250, 
                   marker='*', edgecolor='darkred', linewidth=2, zorder=5)
        plt.scatter([new_year_date], [ny_value_im3], color='gold', s=250, 
                   marker='*', edgecolor='darkred', linewidth=2, zorder=5)
    
    # Highlight Tahun Baru 2025 (historical)
    new_year_2025 = pd.Timestamp('2025-01-01')
    if new_year_2025 in historical_df['Date'].values:
        ny_2025_total = historical_df[historical_df['Date'] == new_year_2025]['Traffic_Total(TB)'].values[0]
        ny_2025_h3i = historical_df[historical_df['Date'] == new_year_2025]['Traffic_H3I (TB)'].values[0]
        ny_2025_im3 = historical_df[historical_df['Date'] == new_year_2025]['Traffic_IM3 (TB)'].values[0]
        
        plt.axvline(x=new_year_2025, color='orange', linestyle=':', linewidth=3, 
                   label='Tahun Baru 2025', alpha=0.6, zorder=4)
        plt.scatter([new_year_2025], [ny_2025_total], color='orange', s=350, 
                   marker='*', edgecolor='darkred', linewidth=2, zorder=5)
        plt.scatter([new_year_2025], [ny_2025_h3i], color='orange', s=200, 
                   marker='*', edgecolor='darkred', linewidth=1.5, zorder=5)
        plt.scatter([new_year_2025], [ny_2025_im3], color='orange', s=200, 
                   marker='*', edgecolor='darkred', linewidth=1.5, zorder=5)
    
    plt.xlabel('Tanggal', fontsize=14, fontweight='bold')
    plt.ylabel('Traffic (TB)', fontsize=14, fontweight='bold')
    plt.title('Tren Traffic Total Harian + Forecast - VLR Java (2024-2026)\nHistorical: 1 Okt 2024 - 22 Okt 2025 | Forecast: 23 Okt 2025 - 5 Jan 2026', 
             fontsize=16, fontweight='bold', pad=20)
    plt.legend(loc='upper left', fontsize=11, framealpha=0.95, ncol=2)
    plt.grid(True, alpha=0.3, linestyle='--')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(f"{output_folder}/01_traffic_harian_total_forecast.png", dpi=300, bbox_inches='tight')
    plt.close()
    print("  ✓ Chart 1: Traffic Harian Total + Forecast (H3I + IM3 + Total)")
    
    # 2. Focus pada periode Tahun Baru
    plt.figure(figsize=(16, 10))
    
    # Data sekitar Tahun Baru (15 hari sebelum dan sesudah)
    ny_date = pd.Timestamp('2026-01-01')
    ny_start = ny_date - timedelta(days=15)
    ny_end = ny_date + timedelta(days=15)
    
    historical_ny = historical_df[historical_df['Date'] >= ny_start].copy()
    forecast_ny = forecast_df[(forecast_df['Date'] >= ny_start) & 
                              (forecast_df['Date'] <= ny_end)].copy()
    
    # Plot
    if len(historical_ny) > 0:
        plt.plot(historical_ny['Date'], historical_ny['Traffic_Total(TB)'], 
                marker='o', linewidth=3, markersize=5, color='#2E86AB', 
                label='Historical Data')
    
    plt.plot(forecast_ny['Date'], forecast_ny['Traffic_Total(TB)'], 
             marker='s', linewidth=3, markersize=5, color='#E63946', 
             label='Forecast', linestyle='--')
    
    plt.fill_between(forecast_ny['Date'], 
                     forecast_ny['Lower_Bound'], 
                     forecast_ny['Upper_Bound'], 
                     alpha=0.25, color='#E63946')
    
    # Highlight Tahun Baru
    plt.axvline(x=ny_date, color='gold', linestyle=':', linewidth=4, 
               label='Tahun Baru 2026', alpha=0.8)
    if ny_date in forecast_ny['Date'].values:
        ny_forecast_value = forecast_ny[forecast_ny['Date'] == ny_date]['Traffic_Total(TB)'].values[0]
        plt.scatter([ny_date], [ny_forecast_value], color='gold', s=500, 
                   marker='*', edgecolor='red', linewidth=3, zorder=5, 
                   label=f'Puncak TahunBaru: {ny_forecast_value:.2f} TB')
    else:
        print("  ⚠ Tahun Baru tidak dalam range forecast_ny")
    
    plt.xlabel('Tanggal', fontsize=14, fontweight='bold')
    plt.ylabel('Traffic Total (TB)', fontsize=14, fontweight='bold')
    plt.title('Forecast Detail - Periode Tahun Baru 2026\nPrediksi Lonjakan Traffic', 
             fontsize=16, fontweight='bold', pad=20)
    plt.legend(loc='best', fontsize=12, framealpha=0.9)
    plt.grid(True, alpha=0.3, linestyle='--')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(f"{output_folder}/02_forecast_tahun_baru_detail.png", dpi=300, bbox_inches='tight')
    plt.close()
    print("  ✓ Chart 2: Detail Tahun Baru")
    
    # 3. Comparison dengan pola Tahun Baru 2025
    if ny_pattern['pattern'] is not None:
        plt.figure(figsize=(16, 10))
        
        # Plot pola Tahun Baru 2025 (historical)
        ny_2025_pattern = ny_pattern['pattern'].copy()
        ny_2025_pattern['Days_from_NY'] = (ny_2025_pattern['Date'] - pd.Timestamp('2025-01-01')).dt.days
        
        plt.subplot(2, 1, 1)
        plt.plot(ny_2025_pattern['Days_from_NY'], ny_2025_pattern['Traffic_Total(TB)'], 
                marker='o', linewidth=3, markersize=5, color='#06A77D', 
                label='Pola Tahun Baru 2025 (Actual)')
        plt.axvline(x=0, color='gold', linestyle=':', linewidth=3, alpha=0.7)
        plt.xlabel('Hari dari Tahun Baru', fontsize=12, fontweight='bold')
        plt.ylabel('Traffic (TB)', fontsize=12, fontweight='bold')
        plt.title('Pola Actual - Tahun Baru 2025', fontsize=14, fontweight='bold')
        plt.legend(fontsize=11)
        plt.grid(True, alpha=0.3)
        
        # Plot forecast Tahun Baru 2026
        plt.subplot(2, 1, 2)
        forecast_ny_full = forecast_df[(forecast_df['Date'] >= ny_date - timedelta(days=15)) & 
                                        (forecast_df['Date'] <= ny_date + timedelta(days=15))].copy()
        forecast_ny_full['Days_from_NY'] = (forecast_ny_full['Date'] - ny_date).dt.days
        
        plt.plot(forecast_ny_full['Days_from_NY'], forecast_ny_full['Traffic_Total(TB)'], 
                marker='s', linewidth=3, markersize=5, color='#E63946', 
                label='Forecast Tahun Baru 2026', linestyle='--')
        plt.fill_between(forecast_ny_full['Days_from_NY'], 
                        forecast_ny_full['Lower_Bound'], 
                        forecast_ny_full['Upper_Bound'], 
                        alpha=0.2, color='#E63946')
        plt.axvline(x=0, color='gold', linestyle=':', linewidth=3, alpha=0.7)
        plt.xlabel('Hari dari Tahun Baru', fontsize=12, fontweight='bold')
        plt.ylabel('Traffic (TB)', fontsize=12, fontweight='bold')
        plt.title('Forecast - Tahun Baru 2026 (Berdasarkan Pola 2025)', fontsize=14, fontweight='bold')
        plt.legend(fontsize=11)
        plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(f"{output_folder}/03_comparison_tahun_baru.png", dpi=300, bbox_inches='tight')
        plt.close()
        print("  ✓ Chart 3: Comparison 2025 vs 2026")
    
    # 4. Weekly aggregation
    plt.figure(figsize=(14, 8))
    
    forecast_df['Week'] = forecast_df['Date'].dt.isocalendar().week
    weekly_forecast = forecast_df.groupby('Week').agg({
        'Traffic_Total(TB)': 'mean',
        'Date': 'first'
    }).reset_index()
    
    plt.bar(range(len(weekly_forecast)), weekly_forecast['Traffic_Total(TB)'], 
           color='steelblue', edgecolor='black', alpha=0.7)
    plt.xlabel('Minggu', fontsize=12, fontweight='bold')
    plt.ylabel('Rata-rata Traffic (TB)', fontsize=12, fontweight='bold')
    plt.title('Forecast Traffic - Rata-rata per Minggu', fontsize=14, fontweight='bold')
    plt.xticks(range(len(weekly_forecast)), 
              [f"Week {w}" for w in weekly_forecast['Week']], rotation=45, ha='right')
    plt.grid(True, alpha=0.3, axis='y')
    plt.tight_layout()
    plt.savefig(f"{output_folder}/04_weekly_forecast.png", dpi=300, bbox_inches='tight')
    plt.close()
    print("  ✓ Chart 4: Weekly aggregation")

def save_forecast_to_excel(historical_df, forecast_df, ny_pattern, output_folder="forecast_results"):
    """Save hasil forecast ke Excel"""
    print("\n💾 Menyimpan hasil ke Excel...")
    
    output_file = f"{output_folder}/forecast_results.xlsx"
    
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        # Sheet 1: Forecast Results
        forecast_export = forecast_df[['Date', 'Traffic_Total(TB)', 'Lower_Bound', 'Upper_Bound']].copy()
        forecast_export['Date'] = forecast_export['Date'].dt.strftime('%Y-%m-%d')
        forecast_export.to_excel(writer, sheet_name='Forecast', index=False)
        
        # Sheet 2: Historical (30 hari terakhir)
        recent_hist = historical_df.tail(30)[['Date', 'Traffic_Total(TB)']].copy()
        recent_hist['Date'] = recent_hist['Date'].dt.strftime('%Y-%m-%d')
        recent_hist.to_excel(writer, sheet_name='Recent_Historical', index=False)
        
        # Sheet 3: Summary Statistics
        summary_data = {
            'Metric': [
                'Periode Forecast',
                'Jumlah Hari Forecast',
                'Tanggal Mulai Forecast',
                'Tanggal Akhir Forecast',
                'Rata-rata Traffic Forecast',
                'Traffic Tertinggi (Tahun Baru)',
                'Traffic Terendah',
                'Spike Ratio Tahun Baru',
                'Confidence Interval',
            ],
            'Value': [
                '23 Okt 2025 - 05 Jan 2026',
                len(forecast_df),
                forecast_df['Date'].min().strftime('%Y-%m-%d'),
                forecast_df['Date'].max().strftime('%Y-%m-%d'),
                f"{forecast_df['Traffic_Total(TB)'].mean():.2f} TB",
                f"{forecast_df['Traffic_Total(TB)'].max():.2f} TB",
                f"{forecast_df['Traffic_Total(TB)'].min():.2f} TB",
                f"{ny_pattern['spike_ratio']:.2%}",
                '±10%'
            ]
        }
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
        # Sheet 4: Daily Statistics
        forecast_stats = forecast_df.copy()
        forecast_stats['Day_of_Week'] = forecast_stats['Date'].dt.day_name()
        forecast_stats['Is_Weekend'] = forecast_stats['Date'].dt.dayofweek.isin([5, 6])
        forecast_stats['Days_to_NewYear'] = (pd.Timestamp('2026-01-01') - forecast_stats['Date']).dt.days
        forecast_stats_export = forecast_stats[['Date', 'Traffic_Total(TB)', 'Day_of_Week', 
                                                'Is_Weekend', 'Days_to_NewYear']].copy()
        forecast_stats_export['Date'] = forecast_stats_export['Date'].dt.strftime('%Y-%m-%d')
        forecast_stats_export.to_excel(writer, sheet_name='Daily_Details', index=False)
    
    print(f"  ✓ File disimpan: {output_file}")

def main():
    """Main function"""
    print("=" * 70)
    print("      TRAFFIC FORECASTING - HINGGA TAHUN BARU 2026")
    print("=" * 70)
    print("\n🎯 Target: Forecast dari 23 Okt 2025 hingga 05 Jan 2026")
    print("🎆 Fokus: Prediksi lonjakan traffic Tahun Baru 2026")
    print("📊 Metode: Multi-model ensemble dengan seasonality\n")
    
    filename = "Traffic_VLR_Java_2024-2025.xlsx"
    
    if not Path(filename).exists():
        print(f"❌ Error: File '{filename}' tidak ditemukan!")
        return
    
    # Load data
    df = load_and_prepare_data(filename)
    
    # Analyze Tahun Baru pattern
    ny_pattern = analyze_new_year_pattern(df)
    
    # Hitung jumlah hari forecast (dari 22 Okt 2025 ke 5 Jan 2026 untuk capture Tahun Baru)
    last_date = df['Date'].max()
    target_date = pd.Timestamp('2026-01-05')  # Extended untuk capture Tahun Baru effect
    forecast_days = (target_date - last_date).days
    
    print(f"\n📅 Periode forecast: {forecast_days} hari")
    print(f"  Dari: {(last_date + timedelta(days=1)).strftime('%d %B %Y')}")
    print(f"  Sampai: {target_date.strftime('%d %B %Y')}")
    
    # Create forecast
    forecast_df = create_forecast(df, ny_pattern, forecast_days)
    
    # Create visualizations
    create_visualizations(df, forecast_df, ny_pattern)
    
    # Save to Excel
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
        print(f"  • Confidence interval: ±10%")
    
    print(f"\n📁 Output:")
    print(f"  • Visualisasi: folder 'forecast_results/'")
    print(f"  • Data Excel: forecast_results/forecast_results.xlsx")
    print("\n" + "=" * 70)

if __name__ == "__main__":
    main()
