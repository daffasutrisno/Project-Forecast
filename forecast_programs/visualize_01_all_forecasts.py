"""
VISUALIZE ALL FORECASTS
========================
Membuat visualisasi lengkap dari semua hasil forecast termasuk
main overview, tabel komparasi, dan kombinasi provinsi.

Input:
  - forecast_results/01_main/forecast_data.csv
  - forecast_results/01_main/comparison_statistics_2025_vs_2026.csv
  - forecast_results/03_provinsi/*.csv
  - Traffic_VLR_Java_2024-2025.xlsx

Output:
  - forecast_results/01_main/00_main_forecast_overview.png
  - forecast_results/01_main/01_tabel_komparasi.png
  - forecast_results/01_main/02_summary_dan_chart.png
  - forecast_results/01_main/03_traffic_forecast_lengkap.png
  - forecast_results/03_provinsi/04_combined_province_comparison.png

Fungsi:
  - Visualisasi forecast utama dengan format regional
  - Tabel komparasi statistik 2025 vs 2026
  - Chart kombinasi semua provinsi
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns
from datetime import datetime, timedelta
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Set style
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("husl")

def load_data():
    """Load semua data yang diperlukan"""
    print("📂 Membaca data untuk visualisasi...")
    
    # Load historical data
    df_historical = pd.read_excel("Traffic_VLR_Java_2024-2025.xlsx", sheet_name=0)
    df_historical['Date'] = pd.to_datetime(df_historical['Date'])
    daily_data = df_historical.groupby('Date').agg({
        'Traffic_H3I (TB)': 'sum',
        'Traffic_IM3 (TB)': 'sum',
        'Traffic_Total(TB)': 'sum'
    }).reset_index()
    
    # Load forecast data
    df_forecast = pd.read_csv("forecast_results/01_main/forecast_data.csv")
    df_forecast['Date'] = pd.to_datetime(df_forecast['Date'])
    
    # Load comparison statistics
    df_comparison = pd.read_csv("forecast_results/01_main/comparison_statistics_2025_vs_2026.csv")
    df_comparison['Date_2025'] = pd.to_datetime(df_comparison['Date_2025'])
    df_comparison['Date_2026'] = pd.to_datetime(df_comparison['Date_2026'])
    
    print(f"  ✓ Historical data: {len(daily_data)} hari")
    print(f"  ✓ Forecast data: {len(df_forecast)} hari")
    print(f"  ✓ Comparison data: {len(df_comparison)} hari")
    
    return daily_data, df_forecast, df_comparison

def create_comparison_table(df_comparison):
    """Gambar 1: Tabel Komparasi Detail"""
    print("\n📊 Membuat Gambar 1: Tabel Komparasi Detail...")
    
    fig, ax = plt.subplots(figsize=(20, 12))
    ax.axis('off')
    
    # Prepare table data dengan keterangan event yang lengkap
    table_data = []
    event_descriptions = {
        '25 Dec': 'Natal',
        '26 Dec': 'Post-Natal (H+1)',
        '27 Dec': 'Post-Natal (H+2)',
        '28 Dec': 'Post-Natal (H+3)',
        '29 Dec': 'Persiapan NYE (H-2)',
        '30 Dec': 'Persiapan NYE (H-1)',
        '31 Dec': 'New Year Eve (NYE)',
        '01 Jan': 'Tahun Baru (PUNCAK)',
        '02 Jan': 'Post-NY (H+1)',
        '03 Jan': 'Post-NY (H+2)',
        '04 Jan': 'Post-NY (H+3)',
        '05 Jan': 'Post-NY (H+4)',
        '06 Jan': 'Post-NY (H+5)',
        '07 Jan': 'Post-NY (H+6)'
    }
    
    for idx, row in df_comparison.iterrows():
        date_str = row['Date_2025'].strftime('%d %b')
        actual = f"{row['Actual_2025']:.2f}"
        forecast = f"{row['Forecast_2026']:.2f}"
        diff = f"{row['Difference']:+.2f}"
        pct = f"{row['Pct_Change']:+.1f}%"
        
        # Tanpa emoji untuk perubahan
        pct_display = pct
        
        # Keterangan event yang lengkap
        event_label = event_descriptions.get(date_str, "")
        
        table_data.append([date_str, actual, forecast, diff, pct_display, event_label])
    
    # Create table
    col_labels = ['Tanggal', 'Actual Des 2024\n(TB)', 'Forecast Des 2025\n(TB)', 'Selisih\n(TB)', 'Perubahan\n(%)', 'Event']
    table = ax.table(cellText=table_data, colLabels=col_labels, 
                     cellLoc='center', loc='center',
                     colWidths=[0.10, 0.16, 0.16, 0.14, 0.16, 0.28])
    
    table.auto_set_font_size(False)
    table.set_fontsize(12)
    table.scale(1, 3.5)
    
    # Style header
    for i in range(len(col_labels)):
        cell = table[(0, i)]
        cell.set_facecolor('#2E86AB')
        cell.set_text_props(weight='bold', color='white', fontsize=14)
        cell.set_height(0.08)
    
    # Style data cells
    for i in range(1, len(table_data) + 1):
        for j in range(len(col_labels)):
            cell = table[(i, j)]
            cell.set_height(0.06)
            
            # Zebra stripes
            if i % 2 == 0:
                cell.set_facecolor('#F5F5F5')
            else:
                cell.set_facecolor('white')
            
            # Highlight special events (Natal & Tahun Baru)
            date_str = table_data[i-1][0]
            if date_str in ['25 Dec', '01 Jan']:
                cell.set_facecolor('#FFF9E6')
                cell.set_text_props(weight='bold')
            
            # Color code untuk kolom perubahan (%)
            if j == 4:  # Kolom perubahan %
                pct_val = float(table_data[i-1][4].replace('%', '').replace('+', ''))
                if pct_val > 0:
                    cell.set_text_props(color='#006400', weight='bold')  # Dark green untuk naik
                elif pct_val < 0:
                    cell.set_text_props(color='#8B0000', weight='bold')  # Dark red untuk turun
    
    # Title dengan penjelasan yang jelas
    plt.suptitle('TABEL KOMPARASI TRAFFIC EVENT TAHUN BARU\n' +
                 'Data Actual Desember 2024 vs Forecast Desember 2025 (25 Des - 7 Jan)', 
                 fontsize=18, fontweight='bold', y=0.95)
    
    plt.savefig("forecast_results/01_main/01_tabel_komparasi.png", dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print("  ✓ Disimpan: forecast_results/01_main/01_tabel_komparasi.png")

def create_summary_and_chart(df_comparison):
    """Gambar 2: Summary Statistics & Bar Chart"""
    print("\n📊 Membuat Gambar 2: Summary Statistics & Bar Chart...")
    
    fig = plt.figure(figsize=(24, 14))
    gs = fig.add_gridspec(2, 2, hspace=0.4, wspace=0.25, height_ratios=[1.1, 1.3])
    
    # Calculate statistics
    avg_2025 = df_comparison['Actual_2025'].mean()
    peak_2025 = df_comparison['Actual_2025'].max()
    min_2025 = df_comparison['Actual_2025'].min()
    
    avg_2026 = df_comparison['Forecast_2026'].mean()
    peak_2026 = df_comparison['Forecast_2026'].max()
    min_2026 = df_comparison['Forecast_2026'].min()
    
    avg_diff = df_comparison['Difference'].mean()
    avg_pct = df_comparison['Pct_Change'].mean()
    
    count_increase = len(df_comparison[df_comparison['Pct_Change'] > 0])
    count_decrease = len(df_comparison[df_comparison['Pct_Change'] < 0])
    total_days = len(df_comparison)
    pct_increase = (count_increase / total_days) * 100
    pct_decrease = (count_decrease / total_days) * 100
    
    baseline = 13727.08  # From analysis
    
    # ===== SUMMARY TABLE (TOP LEFT) =====
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.axis('off')
    
    summary_data = [
        ['Metric', '2025 Actual', '2026 Forecast', 'Selisih', '% Change'],
        ['Rata-rata', f'{avg_2025:.2f} TB', f'{avg_2026:.2f} TB', 
         f'{avg_diff:+.2f} TB', f'{avg_pct:+.1f}%'],
        ['Peak (Max)', f'{peak_2025:.2f} TB', f'{peak_2026:.2f} TB', 
         f'{peak_2026-peak_2025:+.2f} TB', f'{((peak_2026-peak_2025)/peak_2025)*100:+.1f}%'],
        ['Minimum', f'{min_2025:.2f} TB', f'{min_2026:.2f} TB', 
         f'{min_2026-min_2025:+.2f} TB', f'{((min_2026-min_2025)/min_2025)*100:+.1f}%'],
        ['Baseline*', f'{baseline:.2f} TB', f'{baseline:.2f} TB', f'0.00 TB', '0.0%'],
        ['Hari Naik', f'{count_increase} hari', f'{count_increase} hari (est.)', f'0 hari', f'{pct_increase:.0f}%'],
        ['Hari Turun', f'{count_decrease} hari', f'{count_decrease} hari (est.)', f'0 hari', f'{pct_decrease:.0f}%']
    ]
    
    summary_table = ax1.table(cellText=summary_data[1:], colLabels=summary_data[0],
                             cellLoc='center', loc='center',
                             colWidths=[0.20, 0.20, 0.20, 0.20, 0.20])
    
    summary_table.auto_set_font_size(False)
    summary_table.set_fontsize(10)
    summary_table.scale(1, 2.8)
    
    # Style header
    for i in range(len(summary_data[0])):
        cell = summary_table[(0, i)]
        cell.set_facecolor('#2E86AB')
        cell.set_text_props(weight='bold', color='white', fontsize=11)
        cell.set_edgecolor('white')
        cell.set_linewidth(1.5)
    
    # Style data rows
    for i in range(1, len(summary_data)):
        for j in range(len(summary_data[0])):
            cell = summary_table[(i, j)]
            if i % 2 == 0:
                cell.set_facecolor('#F0F8FF')
            else:
                cell.set_facecolor('white')
            cell.set_edgecolor('#DDDDDD')
            cell.set_linewidth(0.8)
    
    ax1.set_title('SUMMARY STATISTICS', fontsize=16, fontweight='bold', pad=25, color='#2E86AB')
    
    # ===== KEY INSIGHTS (TOP RIGHT) =====
    ax2 = fig.add_subplot(gs[0, 1])
    ax2.axis('off')
    
    max_increase = df_comparison.loc[df_comparison['Pct_Change'].idxmax()]
    max_decrease = df_comparison.loc[df_comparison['Pct_Change'].idxmin()]
    pattern_similarity = 100 - abs(avg_pct)
    
    nye_data = df_comparison[df_comparison['Date_2025'].dt.day == 31]
    ny_data = df_comparison[df_comparison['Date_2025'].dt.month == 1].iloc[0]
    nye_pct = nye_data['Pct_Change'].values[0] if len(nye_data) > 0 else 0
    
    # Create table data for Key Insights with aligned colons
    insights_data = [
        ['OVERVIEW', ''],
        ['Perubahan Rata-rata', f': {avg_pct:+.2f}% ({avg_diff:+.2f} TB)'],
        ['Pattern Similarity', f': {pattern_similarity:.1f}%'],
        ['Distribusi', f': ↑{count_increase} hari ({pct_increase:.0f}%) | ↓{count_decrease} hari ({pct_decrease:.0f}%)'],
        ['', ''],
        ['EKSTREM', ''],
        ['Kenaikan Tertinggi', f': {max_increase["Date_2025"].strftime("%d %b")} ({max_increase["Pct_Change"]:+.2f}%)'],
        ['Penurunan Tertinggi', f': {max_decrease["Date_2025"].strftime("%d %b")} ({max_decrease["Pct_Change"]:+.2f}%)'],
        ['', ''],
        ['PERIODE KHUSUS', ''],
        ['NYE (31 Des)', f': {nye_pct:+.2f}% vs 2025'],
        ['Tahun Baru (1 Jan)', f': {ny_data["Pct_Change"]:+.2f}% vs 2025'],
        ['', ''],
        ['BASELINE', ''],
        ['Referensi', f': {baseline:.2f} TB (Avg Des 1-24, 2024)'],
    ]
    
    # Create table with proper alignment
    table = ax2.table(cellText=insights_data, cellLoc='left', loc='center',
                     colWidths=[0.48, 0.52],
                     bbox=[0.02, 0.05, 0.96, 0.85])
    
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 2.0)
    
    # Style cells
    for i, row in enumerate(insights_data):
        for j in range(2):
            cell = table[(i, j)]
            cell.set_edgecolor('none')
            
            # Section headers (OVERVIEW, EKSTREM, etc.)
            if row[0] in ['OVERVIEW', 'EKSTREM', 'PERIODE KHUSUS', 'BASELINE']:
                cell.set_facecolor('#2E86AB')
                cell.set_alpha(0.85)
                cell.set_text_props(weight='bold', fontsize=10, color='white')
            # Empty rows
            elif row[0] == '':
                cell.set_facecolor('white')
                cell.set_alpha(0)
            # Data rows
            else:
                cell.set_facecolor('#F0F8FF')
                cell.set_alpha(0.5)
                cell.set_text_props(fontsize=10, family='monospace')
    
    ax2.set_title('KEY INSIGHTS', fontsize=16, fontweight='bold', pad=15, color='#2E86AB')
    
    # ===== BAR CHART (BOTTOM - FULL WIDTH) =====
    ax3 = fig.add_subplot(gs[1, :])
    
    dates = [d.strftime('%d\n%b') for d in df_comparison['Date_2025']]
    colors = ['#4CAF50' if x >= 0 else '#F44336' for x in df_comparison['Pct_Change']]
    
    bars = ax3.bar(range(len(dates)), df_comparison['Pct_Change'], 
                   color=colors, alpha=0.75, edgecolor='black', linewidth=1.2, width=0.75)
    
    # Labels untuk semua bar dengan nilai
    for i, (bar, val) in enumerate(zip(bars, df_comparison['Pct_Change'])):
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height,
                f'{val:+.1f}%', ha='center', 
                va='bottom' if height > 0 else 'top',
                fontsize=9, fontweight='bold',
                color='darkgreen' if val > 0 else 'darkred')
    
    ax3.axhline(y=0, color='black', linestyle='-', linewidth=2.5, alpha=0.8)
    ax3.set_xlabel('Tanggal', fontsize=14, fontweight='bold', labelpad=15)
    ax3.set_ylabel('Perubahan (%)', fontsize=14, fontweight='bold', labelpad=15)
    ax3.set_title('PERSENTASE PERUBAHAN TRAFFIC (2026 vs 2025)', 
                 fontsize=16, fontweight='bold', pad=25, color='#2E86AB')
    ax3.set_xticks(range(len(dates)))
    ax3.set_xticklabels(dates, fontsize=11, fontweight='bold')
    ax3.grid(True, alpha=0.25, linestyle='--', axis='y', linewidth=0.8)
    ax3.set_axisbelow(True)
    
    y_max = max(abs(df_comparison['Pct_Change'].max()), 
                abs(df_comparison['Pct_Change'].min()))
    ax3.set_ylim(-y_max * 1.35, y_max * 1.35)
    
    # Add background color to chart area
    ax3.set_facecolor('#FAFAFA')
    
    # Main title
    fig.suptitle('ANALISIS KOMPARASI TRAFFIC TAHUN BARU 2025 vs 2026', 
                fontsize=22, fontweight='bold', y=0.98, color='#2E86AB')
    
    plt.savefig("forecast_results/01_main/02_summary_dan_chart.png", dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print("  ✓ Disimpan: forecast_results/01_main/02_summary_dan_chart.png")

def create_traffic_forecast_chart(df_historical, df_forecast):
    """Gambar 3: Chart Traffic Forecast Lengkap"""
    print("\n📊 Membuat Gambar 3: Traffic Forecast Lengkap...")
    
    fig, ax = plt.subplots(figsize=(24, 12))
    
    # Forecast H3I dan IM3 berdasarkan proporsi
    avg_h3i_ratio = (df_historical['Traffic_H3I (TB)'] / df_historical['Traffic_Total(TB)']).mean()
    avg_im3_ratio = (df_historical['Traffic_IM3 (TB)'] / df_historical['Traffic_Total(TB)']).mean()
    
    df_forecast['Traffic_H3I (TB)'] = df_forecast['Traffic_Total(TB)'] * avg_h3i_ratio
    df_forecast['Traffic_IM3 (TB)'] = df_forecast['Traffic_Total(TB)'] * avg_im3_ratio
    
    # Plot historical (solid lines)
    ax.plot(df_historical['Date'], df_historical['Traffic_Total(TB)'], 
            marker='o', linewidth=2.5, markersize=2, color='#2E86AB', 
            label='Total Traffic (Historical)', alpha=0.9, zorder=3)
    ax.plot(df_historical['Date'], df_historical['Traffic_H3I (TB)'], 
            marker='s', linewidth=2, markersize=1.5, color='#A23B72', 
            label='H3I Traffic (Historical)', alpha=0.8, zorder=3)
    ax.plot(df_historical['Date'], df_historical['Traffic_IM3 (TB)'], 
            marker='^', linewidth=2, markersize=1.5, color='#F18F01', 
            label='IM3 Traffic (Historical)', alpha=0.8, zorder=3)
    
    # Shaded forecast area
    ax.axvspan(df_forecast['Date'].min(), df_forecast['Date'].max(), 
               alpha=0.15, color='yellow', zorder=1, label='Forecast Period')
    
    # Plot forecast (dashed lines)
    ax.plot(df_forecast['Date'], df_forecast['Traffic_Total(TB)'], 
            marker='o', linewidth=3, markersize=3, color='#E63946', 
            label='Total Traffic (Forecast)', linestyle='--', alpha=0.9, zorder=4)
    ax.plot(df_forecast['Date'], df_forecast['Traffic_H3I (TB)'], 
            marker='s', linewidth=2.5, markersize=2, color='#D81159', 
            label='H3I Traffic (Forecast)', linestyle='--', alpha=0.8, zorder=4)
    ax.plot(df_forecast['Date'], df_forecast['Traffic_IM3 (TB)'], 
            marker='^', linewidth=2.5, markersize=2, color='#FF6B35', 
            label='IM3 Traffic (Forecast)', linestyle='--', alpha=0.8, zorder=4)
    
    # Confidence interval
    ax.fill_between(df_forecast['Date'], 
                    df_forecast['Lower_Bound'], 
                    df_forecast['Upper_Bound'], 
                    alpha=0.2, color='#E63946', zorder=2, label='Confidence Interval (±10%)')
    
    # Highlight Tahun Baru 2025 (Historical)
    ny_2025_date = pd.Timestamp('2025-01-01')
    ax.axvline(x=ny_2025_date, color='gold', linestyle=':', linewidth=4, 
              alpha=0.8, zorder=5)
    
    ny_2025_historical = df_historical[df_historical['Date'] == ny_2025_date]
    if len(ny_2025_historical) > 0:
        ny_2025_value = ny_2025_historical['Traffic_Total(TB)'].values[0]
        ax.scatter([ny_2025_date], [ny_2025_value], color='gold', s=500, 
                  marker='*', edgecolor='red', linewidth=2.5, zorder=6)
    
    # Highlight Tahun Baru 2026 (Forecast)
    ny_2026_date = pd.Timestamp('2026-01-01')
    ax.axvline(x=ny_2026_date, color='gold', linestyle=':', linewidth=4, 
              alpha=0.8, zorder=5, label='Tahun Baru')
    
    ny_2026_forecast = df_forecast[df_forecast['Date'] == ny_2026_date]
    if len(ny_2026_forecast) > 0:
        ny_2026_value = ny_2026_forecast['Traffic_Total(TB)'].values[0]
        ax.scatter([ny_2026_date], [ny_2026_value], color='gold', s=600, 
                  marker='*', edgecolor='red', linewidth=3, zorder=6)
    
    # Styling
    ax.set_xlabel('Tanggal', fontsize=14, fontweight='bold', labelpad=15)
    ax.set_ylabel('Traffic (TB)', fontsize=14, fontweight='bold', labelpad=15)
    ax.set_title('TRAFFIC FORECAST HARIAN: HISTORICAL + FORECAST (H3I + IM3 + TOTAL)\nPeriode: October 2024 - January 2026', 
                fontsize=16, fontweight='bold', pad=25)
    
    ax.legend(loc='upper left', fontsize=11, framealpha=0.95, 
             ncol=2, columnspacing=1, bbox_to_anchor=(0, 1))
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.tick_params(axis='x', rotation=45, labelsize=10)
    ax.tick_params(axis='y', labelsize=11)
    
    plt.tight_layout()
    plt.savefig("forecast_results/01_main/03_traffic_forecast_lengkap.png", dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print("  ✓ Disimpan: forecast_results/01_main/03_traffic_forecast_lengkap.png")

def create_main_forecast_overview(df_historical, df_forecast):
    """Gambar 0: Main Forecast Overview (Format Regional)"""
    print("\n📊 Membuat Gambar 0: Main Forecast Overview (Format Regional)...")
    
    # Create figure with GridSpec (format regional)
    fig = plt.figure(figsize=(20, 10))
    gs = gridspec.GridSpec(2, 2, figure=fig, hspace=0.3, wspace=0.25)
    
    # Main title
    fig.suptitle('FORECAST TRAFFIC: TOTAL JAVA (ALL REGIONS)\n' +
                 'Historical + Forecast (Oct 2024 - Jan 2026)',
                 fontsize=18, fontweight='bold', y=0.98)
    
    # ===== PLOT 1: TIME SERIES (TOP - FULL WIDTH) =====
    ax1 = fig.add_subplot(gs[0, :])
    
    # Plot historical
    ax1.plot(df_historical['Date'], df_historical['Traffic_Total(TB)'],
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
    last_date = df_historical['Date'].iloc[-1]
    ax1.axvline(x=last_date, color='green', linestyle='--', linewidth=2, alpha=0.7,
               label=f'Last Historical: {last_date.strftime("%Y-%m-%d")}')
    
    ax1.set_xlabel('Date', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Traffic (TB)', fontsize=12, fontweight='bold')
    ax1.set_title('Time Series: Historical + Forecast', fontsize=14, fontweight='bold', pad=15)
    ax1.legend(loc='best', fontsize=10)
    ax1.grid(True, alpha=0.3)
    plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)
    
    # ===== PLOT 2: STATISTICS SUMMARY TABLE (BOTTOM LEFT) =====
    ax2 = fig.add_subplot(gs[1, 0])
    ax2.axis('off')
    
    # Calculate statistics
    hist_mean = df_historical['Traffic_Total(TB)'].mean()
    hist_std = df_historical['Traffic_Total(TB)'].std()
    hist_min = df_historical['Traffic_Total(TB)'].min()
    hist_max = df_historical['Traffic_Total(TB)'].max()

    fore_mean = df_forecast['Traffic_Total(TB)'].mean()
    fore_std = df_forecast['Traffic_Total(TB)'].std()
    fore_min = df_forecast['Traffic_Total(TB)'].min()
    fore_max = df_forecast['Traffic_Total(TB)'].max()

    # Create table data for proper alignment
    table_data = [
        ['HISTORICAL:', ''],
        ['  • Data Points', f': {len(df_historical)} hari'],
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
    
    # ===== PLOT 3: DISTRIBUTION HISTOGRAM (BOTTOM RIGHT) =====
    ax3 = fig.add_subplot(gs[1, 1])
    
    # Plot distributions
    ax3.hist(df_historical['Traffic_Total(TB)'], bins=30, alpha=0.6, 
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
    
    # Save
    filepath = "forecast_results/01_main/00_main_forecast_overview.png"
    plt.savefig(filepath, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    
    print(f"  ✓ Disimpan: {filepath}")

def create_combined_province_comparison():
    """Gambar 4: Chart Kombinasi Provinsi (Format Regional)"""
    print("\n📊 Membuat Gambar 4: Chart Kombinasi Provinsi...")
    
    province_forecast_dir = Path("forecast_results/03_provinsi")
    
    if not province_forecast_dir.exists():
        print("  ⚠️  Forecast per provinsi tidak ditemukan!")
        print("  💡 Jalankan '1b_run_forecast_by_province.py' terlebih dahulu")
        return
    
    # Load raw data
    df_raw = pd.read_excel("Traffic_VLR_Java_2024-2025.xlsx", sheet_name=0)
    df_raw['Date'] = pd.to_datetime(df_raw['Date'])
    
    # Get list of provinces
    provinces = sorted(df_raw['PROVINCE'].unique())
    
    province_forecasts = {}
    
    for province in provinces:
        # Filter historical data by province
        df_prov = df_raw[df_raw['PROVINCE'] == province].copy()
        daily_historical = df_prov.groupby('Date')['Traffic_Total(TB)'].sum().reset_index()
        daily_historical.columns = ['Date', 'Traffic_Total(TB)']
        
        # Load individual province forecast
        province_filename = province.lower().replace(' ', '_')
        forecast_file = province_forecast_dir / f"{province_filename}.csv"
        
        if forecast_file.exists():
            df_forecast = pd.read_csv(forecast_file)
            df_forecast['Date'] = pd.to_datetime(df_forecast['Date'])
            
            province_forecasts[province] = {
                'historical': daily_historical,
                'forecast': df_forecast
            }
    
    if not province_forecasts:
        print("  ⚠️  Tidak ada forecast provinsi ditemukan!")
        return
    
    print(f"  ✓ Loaded {len(province_forecasts)} provinsi forecasts")
    
    # Create figure with GridSpec (format sama dengan regional)
    fig = plt.figure(figsize=(20, 14))
    gs = fig.add_gridspec(2, 2, hspace=0.4, wspace=0.28,
                          height_ratios=[1.2, 1], width_ratios=[1.2, 1])
    
    # ===== PLOT 1: TIME SERIES COMPARISON (TOP - FULL WIDTH) =====
    ax1 = fig.add_subplot(gs[0, :])
    
    colors = plt.cm.tab10(np.arange(len(province_forecasts)))
    
    for idx, (province, data) in enumerate(province_forecasts.items()):
        ax1.plot(data['forecast']['Date'], data['forecast']['Traffic_Total(TB)'],
                'o-', color=colors[idx], linewidth=2, markersize=3,
                label=province, alpha=0.8)
    
    ax1.set_xlabel('Date', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Traffic (TB/hari)', fontsize=12, fontweight='bold')
    ax1.set_title('FORECAST COMPARISON: ALL PROVINSI', fontsize=14, fontweight='bold', pad=15)
    ax1.legend(loc='best', fontsize=10, ncol=2)
    ax1.grid(True, alpha=0.3)
    plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)
    
    # ===== PLOT 2: STATISTICS SUMMARY TABLE (BOTTOM LEFT) =====
    ax2 = fig.add_subplot(gs[1, 0])
    ax2.axis('off')
    
    # Prepare table data
    table_data = []
    hist_avgs = []
    fore_avgs = []
    
    for province, data in province_forecasts.items():
        hist_mean = data['historical']['Traffic_Total(TB)'].mean()
        fore_mean = data['forecast']['Traffic_Total(TB)'].mean()
        change = fore_mean - hist_mean
        change_pct = (change / hist_mean) * 100
        
        hist_avgs.append(hist_mean)
        fore_avgs.append(fore_mean)
        
        # Shorten province name if too long
        prov_short = province if len(province) <= 20 else province[:18] + ".."
        
        table_data.append([
            prov_short,
            f"{hist_mean:,.0f}",
            f"{fore_mean:,.0f}",
            f"{change:+,.0f}",
            f"{change_pct:+.2f}%"
        ])
    
    # Add total row
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
    
    col_labels = ['Provinsi', 'Historical\nAvg (TB)', 'Forecast\nAvg (TB)', 'Change\n(TB)', 'Change\n(%)']
    
    # Create table
    table = ax2.table(cellText=table_data, colLabels=col_labels,
                     cellLoc='center', loc='center',
                     colWidths=[0.24, 0.19, 0.19, 0.19, 0.19],
                     bbox=[0.05, 0.05, 0.9, 0.82])
    
    table.auto_set_font_size(False)
    table.set_fontsize(9)
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
            
            if j == 0:  # Province names - left aligned
                cell.set_text_props(ha='left', fontsize=9)
                cell.PAD = 0.05
            else:  # Numbers - center aligned
                cell.set_text_props(ha='center', fontsize=9)
            
            if i == len(table_data):  # Total row
                cell.set_facecolor('#F39C12')
                cell.set_text_props(weight='bold', fontsize=9)
                if j == 0:
                    cell.set_text_props(ha='left', weight='bold', fontsize=9)
            else:
                cell.set_facecolor('#ECF0F1' if i % 2 == 0 else 'white')
    
    ax2.set_title('SUMMARY STATISTICS', fontsize=12, fontweight='bold', pad=10)
    
    # ===== PLOT 3: DISTRIBUTION HISTOGRAM (BOTTOM RIGHT) =====
    ax3 = fig.add_subplot(gs[1, 1])
    
    for idx, (province, data) in enumerate(province_forecasts.items()):
        ax3.hist(data['forecast']['Traffic_Total(TB)'], bins=20, alpha=0.5,
                color=colors[idx], label=province, edgecolor='black')
    
    ax3.set_xlabel('Traffic (TB)', fontsize=11, fontweight='bold')
    ax3.set_ylabel('Frequency', fontsize=11, fontweight='bold')
    ax3.set_title('FORECAST DISTRIBUTION', fontsize=12, fontweight='bold', pad=10)
    ax3.legend(loc='best', fontsize=8, ncol=2)
    ax3.grid(True, alpha=0.3, axis='y')
    
    # Main title
    fig.suptitle('PERBANDINGAN FORECAST TRAFFIC ANTAR PROVINSI',
                fontsize=16, fontweight='bold', y=0.96)
    
    # Save
    filepath = "forecast_results/01_main/04_combined_province_comparison.png"
    plt.savefig(filepath, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    
    print(f"  ✓ Disimpan: {filepath}")

def main():
    """Main function"""
    print("=" * 70)
    print("  PROGRAM 2: CREATE VISUALIZATIONS")
    print("=" * 70)
    print("\n🎨 Membuat visualisasi dari hasil forecast...\n")
    
    # Check input files
    required_files = [
        "forecast_results/01_main/forecast_data.csv",
        "forecast_results/01_main/comparison_statistics_2025_vs_2026.csv",
        "Traffic_VLR_Java_2024-2025.xlsx"
    ]
    
    for file in required_files:
        if not Path(file).exists():
            print(f"❌ Error: File '{file}' tidak ditemukan!")
            print("💡 Jalankan '1_run_forecast.py' terlebih dahulu")
            return
    
    # Load data
    df_historical, df_forecast, df_comparison = load_data()
    
    # Create main forecast overview (format regional)
    create_main_forecast_overview(df_historical, df_forecast)
    
    # Create visualizations (3 gambar terpisah)
    create_comparison_table(df_comparison)
    create_summary_and_chart(df_comparison)
    create_traffic_forecast_chart(df_historical, df_forecast)
    
    # Create combined province comparison chart (format regional)
    create_combined_province_comparison()
    
    # Summary
    print("\n" + "=" * 70)
    print("✅ VISUALISASI SELESAI!")
    print("=" * 70)
    print(f"\n📁 Output Files:")
    print(f"  0. forecast_results/01_main/00_main_forecast_overview.png")
    print(f"     → Overview forecast utama (format regional)")
    print(f"  1. forecast_results/01_main/01_tabel_komparasi.png")
    print(f"     → Tabel komparasi detail 2025 vs 2026")
    print(f"  2. forecast_results/01_main/02_summary_dan_chart.png")
    print(f"     → Summary statistics + bar chart + key insights")
    print(f"  3. forecast_results/01_main/03_traffic_forecast_lengkap.png")
    print(f"     → Chart traffic lengkap (historical + forecast)")
    print(f"  4. forecast_results/01_main/04_combined_province_comparison.png")
    print(f"     → Chart kombinasi provinsi (format regional)")
    print("\n💡 Total 5 gambar: 4 analisis umum + 1 kombinasi provinsi!")
    print(f"💡 Chart provinsi lengkap tersedia di folder 03_provinsi")
    print("=" * 70)

if __name__ == "__main__":
    main()
