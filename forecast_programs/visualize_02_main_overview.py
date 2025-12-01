"""
VISUALIZE MAIN OVERVIEW
========================
Membuat visualisasi forecast utama (total traffic) dengan format yang sama
dengan regional/provinsi: chart horizontal + statistics + distribution.

Input:
  - forecast_results/01_main/forecast_data.csv
  - Traffic_VLR_Java_2024-2025.xlsx

Output:
  - forecast_results/01_main/00_main_forecast_overview.png

Fungsi:
  - Visualisasi forecast total traffic dengan format regional
  - Layout: chart di atas, statistics kiri bawah, distribution kanan bawah
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from pathlib import Path

def create_main_forecast_visualization():
    """Create visualization untuk forecast utama dengan format regional"""
    
    print("="*80)
    print("  CREATE MAIN FORECAST VISUALIZATION (FORMAT REGIONAL)")
    print("="*80)
    
    # Load historical data
    print("\n📂 Membaca data...")
    df_raw = pd.read_excel("Traffic_VLR_Java_2024-2025.xlsx", sheet_name=0)
    df_raw['Date'] = pd.to_datetime(df_raw['Date'])
    
    # Aggregate daily
    daily_historical = df_raw.groupby('Date')['Traffic_Total(TB)'].sum().reset_index()
    daily_historical.columns = ['Date', 'Traffic_Total(TB)']
    
    # Load forecast data
    forecast_file = Path("forecast_results/01_main/forecast_data.csv")
    if not forecast_file.exists():
        print("❌ Error: File forecast tidak ditemukan!")
        print("💡 Jalankan '1_run_forecast.py' terlebih dahulu")
        return None
    
    df_forecast = pd.read_csv(forecast_file)
    df_forecast['Date'] = pd.to_datetime(df_forecast['Date'])
    
    print(f"  ✓ Historical: {len(daily_historical)} hari")
    print(f"  ✓ Forecast: {len(df_forecast)} hari")
    
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
    ax1.plot(daily_historical['Date'], daily_historical['Traffic_Total(TB)'],
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
    last_date = daily_historical['Date'].iloc[-1]
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
    hist_mean = daily_historical['Traffic_Total(TB)'].mean()
    hist_std = daily_historical['Traffic_Total(TB)'].std()
    hist_min = daily_historical['Traffic_Total(TB)'].min()
    hist_max = daily_historical['Traffic_Total(TB)'].max()

    fore_mean = df_forecast['Traffic_Total(TB)'].mean()
    fore_std = df_forecast['Traffic_Total(TB)'].std()
    fore_min = df_forecast['Traffic_Total(TB)'].min()
    fore_max = df_forecast['Traffic_Total(TB)'].max()

    # Create table data for proper alignment
    table_data = [
        ['HISTORICAL:', ''],
        ['  • Data Points', f': {len(daily_historical)} hari'],
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
    ax3.hist(daily_historical['Traffic_Total(TB)'], bins=30, alpha=0.6, 
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
    output_dir = Path("forecast_results/01_main")
    output_dir.mkdir(parents=True, exist_ok=True)
    filepath = output_dir / "00_main_forecast_overview.png"
    
    plt.savefig(filepath, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    
    print(f"\n✅ Visualisasi disimpan: {filepath}")
    print("="*80)
    
    return filepath

def main():
    """Main function"""
    filepath = create_main_forecast_visualization()
    
    if filepath:
        print("\n📊 File berhasil dibuat!")
        print(f"📁 Lokasi: {filepath}")

if __name__ == "__main__":
    main()
