"""
VISUALIZE PROVINCE SUMMARY
===========================
Membuat summary comparison untuk semua provinsi dengan format regional:
chart horizontal + statistics + distribution.

Input:
  - forecast_results/03_provinsi/*.csv
  - Traffic_VLR_Java_2024-2025.xlsx

Output:
  - forecast_results/03_provinsi/summary_comparison_provinsi.png

Fungsi:
  - Perbandingan forecast semua provinsi dalam satu chart
  - Tabel statistik perbandingan antar provinsi
  - Histogram distribusi forecast per provinsi
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from pathlib import Path

def create_provinsi_summary_comparison():
    """Create summary comparison antar provinsi"""
    
    output_dir = Path("forecast_results/03_provinsi")
    
    if not output_dir.exists():
        print("❌ Error: Folder provinsi tidak ditemukan!")
        return
    
    # Load data
    df = pd.read_excel("Traffic_VLR_Java_2024-2025.xlsx", sheet_name=0)
    df['Date'] = pd.to_datetime(df['Date'])
    provinces = sorted(df['PROVINCE'].unique())
    
    provinsi_forecasts = {}
    
    for province in provinces:
        # Load historical
        df_prov = df[df['PROVINCE'] == province].copy()
        daily_historical = df_prov.groupby('Date')['Traffic_Total(TB)'].sum().reset_index()
        daily_historical.columns = ['Date', 'Traffic_Total(TB)']
        
        # Load forecast
        forecast_file = output_dir / f"{province.lower().replace(' ', '_')}.csv"
        
        if forecast_file.exists():
            df_forecast = pd.read_csv(forecast_file)
            df_forecast['Date'] = pd.to_datetime(df_forecast['Date'])
            
            provinsi_forecasts[province] = {
                'historical': daily_historical,
                'forecast': df_forecast
            }
    
    if not provinsi_forecasts:
        print("❌ Error: Tidak ada forecast provinsi ditemukan!")
        return
    
    print(f"✓ Loaded {len(provinsi_forecasts)} provinsi forecasts")
    
    # Create figure with GridSpec
    fig = plt.figure(figsize=(20, 12))
    gs = gridspec.GridSpec(2, 2, figure=fig, hspace=0.35, wspace=0.28,
                          height_ratios=[1, 1], width_ratios=[1.2, 1])
    
    # Plot 1: Time Series Comparison (Top - Full Width)
    ax1 = fig.add_subplot(gs[0, :])
    
    colors = plt.cm.tab10(np.arange(len(provinsi_forecasts)))
    
    for idx, (province, data) in enumerate(provinsi_forecasts.items()):
        ax1.plot(data['forecast']['Date'], data['forecast']['Traffic_Total(TB)'],
                'o-', color=colors[idx], linewidth=2, markersize=3,
                label=province, alpha=0.8)
    
    ax1.set_xlabel('Date', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Traffic (TB/hari)', fontsize=12, fontweight='bold')
    ax1.set_title('Forecast Comparison: All Provinsi', fontsize=14, fontweight='bold', pad=15)
    ax1.legend(loc='best', fontsize=10, ncol=2)
    ax1.grid(True, alpha=0.3)
    plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)
    
    # Plot 2: Statistics Summary Table (Bottom Left)
    ax2 = fig.add_subplot(gs[1, 0])
    ax2.axis('off')
    
    # Prepare table data
    table_data = []
    for province, data in provinsi_forecasts.items():
        hist_mean = data['historical']['Traffic_Total(TB)'].mean()
        fore_mean = data['forecast']['Traffic_Total(TB)'].mean()
        change = fore_mean - hist_mean
        change_pct = (change / hist_mean) * 100
        
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
    total_hist = sum([data['historical']['Traffic_Total(TB)'].mean() for data in provinsi_forecasts.values()])
    total_fore = sum([data['forecast']['Traffic_Total(TB)'].mean() for data in provinsi_forecasts.values()])
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
    
    ax2.set_title('Summary Statistics', fontsize=12, fontweight='bold', pad=10)
    
    # Plot 3: Distribution Histogram (Bottom Right)
    ax3 = fig.add_subplot(gs[1, 1])
    
    for idx, (province, data) in enumerate(provinsi_forecasts.items()):
        ax3.hist(data['forecast']['Traffic_Total(TB)'], bins=20, alpha=0.5,
                color=colors[idx], label=province, edgecolor='black')
    
    ax3.set_xlabel('Traffic (TB)', fontsize=11, fontweight='bold')
    ax3.set_ylabel('Frequency', fontsize=11, fontweight='bold')
    ax3.set_title('Forecast Distribution', fontsize=12, fontweight='bold', pad=10)
    ax3.legend(loc='best', fontsize=8, ncol=2)
    ax3.grid(True, alpha=0.3, axis='y')
    
    # Main title
    fig.suptitle('PERBANDINGAN FORECAST TRAFFIC ANTAR PROVINSI',
                fontsize=16, fontweight='bold', y=0.96)
    
    # Save
    filepath = output_dir / 'summary_comparison_provinsi.png'
    plt.savefig(filepath, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    
    print(f"✓ Summary comparison disimpan: {filepath}")
    
    return filepath

def main():
    print("="*80)
    print("  CREATE PROVINSI SUMMARY COMPARISON")
    print("="*80)
    
    filepath = create_provinsi_summary_comparison()
    
    if filepath:
        print("\n✅ Selesai!")
        print(f"📁 File: {filepath}")
    else:
        print("\n❌ Gagal membuat summary comparison")
    
    print("="*80)

if __name__ == "__main__":
    main()
