"""
ANALYSIS TOP 10 - ABSOLUTE CHANGE
===================================
Menghitung top 10 kabupaten dengan peningkatan traffic ABSOLUT tertinggi
(dalam TB) berdasarkan hasil forecast individual per kabupaten.

Input:
  - forecast_results/04_kabupaten/[kabupaten]_forecast.csv (119 files)
  - Traffic_VLR_Java_2024-2025.xlsx

Output:
  - forecast_results/05_analysis/top10_kabupaten_absolute.xlsx
  - forecast_results/05_analysis/top10_kabupaten_absolute_summary.png

Fungsi:
  - Ranking berdasarkan SELISIH ABSOLUT (TB) tertinggi
  - Menunjukkan kabupaten dengan dampak volume traffic terbesar
  - Analisis top 10, top 20, dan semua kabupaten
"""

import pandas as pd
import numpy as np
from pathlib import Path

def load_kabupaten_forecast_data():
    """Load historical dan forecast data untuk setiap kabupaten"""
    
    print("\n📂 Membaca data forecast per kabupaten...")
    
    forecast_dir = Path("forecast_results/04_kabupaten")
    
    if not forecast_dir.exists():
        print("❌ Error: Folder forecast_kabupaten tidak ditemukan!")
        print("💡 Jalankan '1d_run_forecast_by_kabupaten.py' terlebih dahulu")
        return None
    
    # Get all CSV files
    csv_files = list(forecast_dir.glob("*.csv"))
    
    if len(csv_files) == 0:
        print("❌ Error: Tidak ada file forecast ditemukan!")
        print("💡 Jalankan '1d_run_forecast_by_kabupaten.py' terlebih dahulu")
        return None
    
    print(f"✓ Ditemukan {len(csv_files)} file forecast kabupaten")
    
    # Load original data for historical
    df = pd.read_excel("Traffic_VLR_Java_2024-2025.xlsx", sheet_name=0)
    df['Date'] = pd.to_datetime(df['Date'])
    
    kabupaten_summary = []
    
    for csv_file in csv_files:
        kabupaten_name = csv_file.stem.replace('_', ' ').upper()
        
        # Load forecast
        df_forecast = pd.read_csv(csv_file)
        fore_mean = df_forecast['Traffic_Total(TB)'].mean()
        fore_total = df_forecast['Traffic_Total(TB)'].sum()
        
        # Get historical data
        df_kab = df[df['KABUPATEN IOH'] == kabupaten_name].copy()
        
        if len(df_kab) == 0:
            # Try original case
            for kab in df['KABUPATEN IOH'].unique():
                if kab.lower().replace(' ', '_') == csv_file.stem:
                    df_kab = df[df['KABUPATEN IOH'] == kab].copy()
                    kabupaten_name = kab
                    break
        
        if len(df_kab) > 0:
            # Get region and province
            region = df_kab['REGION IOH'].iloc[0]
            province = df_kab['PROVINCE'].iloc[0]
            
            # Calculate historical stats
            daily_data = df_kab.groupby('Date')['Traffic_Total(TB)'].sum()
            hist_mean = daily_data.mean()
            hist_total = daily_data.sum()
            hist_std = daily_data.std()
            
            # Calculate changes (ABSOLUT)
            change_avg = fore_mean - hist_mean
            change_total = fore_total - hist_total
            growth_rate = (change_avg / hist_mean) * 100 if hist_mean > 0 else 0
            
            kabupaten_summary.append({
                'Kabupaten': kabupaten_name,
                'Region': region,
                'Province': province,
                'Historical_Avg': hist_mean,
                'Historical_Total': hist_total,
                'Forecast_Avg': fore_mean,
                'Forecast_Total': fore_total,
                'Change_Avg_TB': change_avg,  # Absolut change per hari
                'Change_Total_TB': change_total,  # Absolut change total
                'Growth_Rate': growth_rate,
                'Data_Days': len(daily_data)
            })
    
    df_summary = pd.DataFrame(kabupaten_summary)
    
    return df_summary

def create_visualization_top10(df_top10, output_file):
    """Create visualization untuk top 10 kabupaten"""
    
    import matplotlib.pyplot as plt
    
    fig, axes = plt.subplots(2, 2, figsize=(20, 14))
    fig.suptitle('TOP 10 KABUPATEN - PENINGKATAN TRAFFIC ABSOLUT TERTINGGI (TB)\n(Berdasarkan Forecast Individual)',
                 fontsize=18, fontweight='bold', y=0.98)
    
    plt.subplots_adjust(hspace=0.35, wspace=0.3)
    
    # Plot 1: Absolute Change Comparison (TB per hari)
    ax1 = axes[0, 0]
    
    kabupaten_names = [k[:15] + '...' if len(k) > 15 else k for k in df_top10['Kabupaten']]
    colors = plt.cm.Blues(np.linspace(0.5, 0.9, len(df_top10)))
    
    bars = ax1.barh(range(len(df_top10)), df_top10['Change_Avg_TB'], color=colors, alpha=0.8, edgecolor='black')
    
    # Add value labels
    for i, (bar, val) in enumerate(zip(bars, df_top10['Change_Avg_TB'])):
        ax1.text(val + 1, bar.get_y() + bar.get_height()/2, 
                f'+{val:.2f} TB', va='center', fontsize=10, fontweight='bold')
    
    ax1.set_yticks(range(len(df_top10)))
    ax1.set_yticklabels([f"{i+1}. {name}" for i, name in enumerate(kabupaten_names)], fontsize=10)
    ax1.set_xlabel('Peningkatan Rata-rata (TB/hari)', fontsize=12, fontweight='bold')
    ax1.set_title('Peningkatan Absolut per Hari', fontsize=14, fontweight='bold', pad=15)
    ax1.grid(True, alpha=0.3, axis='x')
    ax1.invert_yaxis()
    
    # Plot 2: Historical vs Forecast Average (TB)
    ax2 = axes[0, 1]
    
    x = np.arange(len(df_top10))
    width = 0.35
    
    bars1 = ax2.bar(x - width/2, df_top10['Historical_Avg'], width, 
                    label='Historical', color='#2E86AB', alpha=0.8, edgecolor='black')
    bars2 = ax2.bar(x + width/2, df_top10['Forecast_Avg'], width,
                    label='Forecast', color='#E63946', alpha=0.8, edgecolor='black')
    
    # Add value labels
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.1f}', ha='center', va='bottom', fontsize=8)
    
    ax2.set_xlabel('Rank', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Avg Traffic (TB/hari)', fontsize=12, fontweight='bold')
    ax2.set_title('Historical vs Forecast Average', fontsize=14, fontweight='bold', pad=15)
    ax2.set_xticks(x)
    ax2.set_xticklabels([f'{i+1}' for i in range(len(df_top10))], fontsize=10)
    ax2.legend(loc='upper left', fontsize=10)
    ax2.grid(True, alpha=0.3, axis='y')
    
    # Plot 3: Scatter - Change vs Historical Traffic
    ax3 = axes[1, 0]
    
    region_colors = {'BALI NUSRA': '#06A77D', 'CENTRAL JAVA': '#2E86AB', 'EAST JAVA': '#E63946'}
    
    for region in df_top10['Region'].unique():
        df_region = df_top10[df_top10['Region'] == region]
        ax3.scatter(df_region['Historical_Avg'], df_region['Change_Avg_TB'],
                   s=200, alpha=0.7, label=region, color=region_colors.get(region, 'gray'),
                   edgecolor='black', linewidth=1.5)
    
    # Add labels for each point
    for idx, row in df_top10.iterrows():
        ax3.annotate(row['Kabupaten'][:10], 
                    (row['Historical_Avg'], row['Change_Avg_TB']),
                    fontsize=8, ha='center', va='bottom')
    
    ax3.set_xlabel('Historical Avg (TB/hari)', fontsize=12, fontweight='bold')
    ax3.set_ylabel('Peningkatan Absolut (TB/hari)', fontsize=12, fontweight='bold')
    ax3.set_title('Korelasi Historical vs Peningkatan', fontsize=14, fontweight='bold', pad=15)
    ax3.legend(loc='best', fontsize=10)
    ax3.grid(True, alpha=0.3)
    
    # Plot 4: Summary Table
    ax4 = axes[1, 1]
    ax4.axis('off')
    
    table_data = []
    for idx, row in df_top10.iterrows():
        rank = df_top10.index.get_loc(idx) + 1
        kab_short = row['Kabupaten'][:18] if len(row['Kabupaten']) > 18 else row['Kabupaten']
        table_data.append([
            f"{rank}",
            kab_short,
            f"{row['Historical_Avg']:.1f}",
            f"{row['Forecast_Avg']:.1f}",
            f"+{row['Change_Avg_TB']:.2f}",
            f"{row['Growth_Rate']:+.1f}%"
        ])
    
    col_labels = ['#', 'Kabupaten', 'Hist\n(TB)', 'Fore\n(TB)', 'Change\n(TB)', 'Growth\n(%)']
    
    table = ax4.table(cellText=table_data, colLabels=col_labels,
                     cellLoc='center', loc='center',
                     colWidths=[0.08, 0.28, 0.16, 0.16, 0.16, 0.16],
                     bbox=[0.05, 0.1, 0.9, 0.8])
    
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 2.2)
    
    # Style header
    for i in range(len(col_labels)):
        cell = table[(0, i)]
        cell.set_facecolor('#2C3E50')
        cell.set_text_props(weight='bold', color='white', fontsize=10)
    
    # Style data rows
    for i in range(1, len(table_data) + 1):
        for j in range(len(col_labels)):
            cell = table[(i, j)]
            if j == 1:  # Kabupaten name
                cell.set_text_props(ha='left', fontsize=9)
            else:
                cell.set_text_props(ha='center', fontsize=9)
            
            # Alternating colors
            cell.set_facecolor('#ECF0F1' if i % 2 == 0 else 'white')
    
    ax4.set_title('Top 10 Summary', fontsize=14, fontweight='bold', pad=20)
    
    # Save
    plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    
    print(f"✓ Visualisasi disimpan: {output_file}")

def main():
    """Main function"""
    print("="*80)
    print("  TOP 10 KABUPATEN - PENINGKATAN ABSOLUT (TB)")
    print("="*80)
    print("\nMenggunakan hasil forecast individual per kabupaten")
    print("Metode: Ranking berdasarkan PENINGKATAN ABSOLUT (TB), bukan %\n")
    
    # Load data
    df_summary = load_kabupaten_forecast_data()
    
    if df_summary is None:
        return
    
    print(f"\n✓ Berhasil memproses {len(df_summary)} kabupaten")
    
    # Sort by absolute change (descending)
    df_sorted = df_summary.sort_values('Change_Avg_TB', ascending=False)
    df_top10 = df_sorted.head(10)
    
    # Display results
    print("\n" + "="*80)
    print("  TOP 10 KABUPATEN DENGAN PENINGKATAN ABSOLUT TERTINGGI")
    print("="*80)
    print()
    print(f"{'Rank':<6} {'Kabupaten':<25} {'Region':<15} {'Hist Avg':<12} {'Fore Avg':<12} {'Change (TB)':<12} {'Growth %':<10}")
    print("-"*110)
    
    for idx, (_, row) in enumerate(df_top10.iterrows(), 1):
        print(f"{idx:<6} {row['Kabupaten']:<25} {row['Region']:<15} "
              f"{row['Historical_Avg']:>10,.2f}  {row['Forecast_Avg']:>10,.2f}  "
              f"{row['Change_Avg_TB']:>+10,.2f}  {row['Growth_Rate']:>+8.2f}%")
    
    # Total impact
    total_change = df_top10['Change_Avg_TB'].sum()
    total_hist = df_top10['Historical_Avg'].sum()
    total_fore = df_top10['Forecast_Avg'].sum()
    
    print("\n" + "-"*110)
    print(f"{'TOTAL TOP 10':<47} {total_hist:>10,.2f}  {total_fore:>10,.2f}  "
          f"{total_change:>+10,.2f}  {(total_change/total_hist)*100:>+8.2f}%")
    
    # Regional distribution
    print("\n" + "="*80)
    print("  DISTRIBUSI PER REGIONAL")
    print("="*80)
    
    regional_count = df_top10['Region'].value_counts()
    regional_change = df_top10.groupby('Region')['Change_Avg_TB'].sum()
    
    for region in regional_count.index:
        count = regional_count[region]
        change = regional_change[region]
        print(f"  {region:<20} : {count} kabupaten (Total: +{change:.2f} TB/hari)")
    
    # Save to Excel
    output_excel = Path("forecast_results/05_analysis/top10_kabupaten_by_absolute_change.xlsx")
    
    with pd.ExcelWriter(output_excel, engine='openpyxl') as writer:
        # Top 10 by absolute change
        df_top10.to_excel(writer, sheet_name='Top 10 Absolute', index=False)
        
        # Top 20 by absolute change
        df_top20 = df_sorted.head(20)
        df_top20.to_excel(writer, sheet_name='Top 20 Absolute', index=False)
        
        # Top 10 by percentage (for comparison)
        df_top10_pct = df_summary.nlargest(10, 'Growth_Rate')
        df_top10_pct.to_excel(writer, sheet_name='Top 10 Percentage', index=False)
        
        # All kabupaten sorted by absolute change
        df_sorted.to_excel(writer, sheet_name='All Kabupaten', index=False)
        
        # Summary comparison
        comparison_data = []
        
        # Top 10 Absolute
        top10_abs = df_sorted.head(10)
        comparison_data.append({
            'Metric': 'Top 10 by Absolute Change',
            'Total_Change_TB': top10_abs['Change_Avg_TB'].sum(),
            'Avg_Change_TB': top10_abs['Change_Avg_TB'].mean(),
            'Avg_Growth_Rate': top10_abs['Growth_Rate'].mean(),
            'Total_Historical': top10_abs['Historical_Avg'].sum(),
            'Total_Forecast': top10_abs['Forecast_Avg'].sum()
        })
        
        # Top 10 Percentage
        top10_pct = df_summary.nlargest(10, 'Growth_Rate')
        comparison_data.append({
            'Metric': 'Top 10 by Growth Rate %',
            'Total_Change_TB': top10_pct['Change_Avg_TB'].sum(),
            'Avg_Change_TB': top10_pct['Change_Avg_TB'].mean(),
            'Avg_Growth_Rate': top10_pct['Growth_Rate'].mean(),
            'Total_Historical': top10_pct['Historical_Avg'].sum(),
            'Total_Forecast': top10_pct['Forecast_Avg'].sum()
        })
        
        df_comparison = pd.DataFrame(comparison_data)
        df_comparison.to_excel(writer, sheet_name='Comparison', index=False)
    
    print(f"\n✓ Excel disimpan: {output_excel}")
    
    # Create visualization
    output_png = Path("forecast_results/05_analysis/top10_kabupaten_by_absolute_change.png")
    create_visualization_top10(df_top10, output_png)
    
    print("\n" + "="*80)
    print("✅ SELESAI!")
    print("="*80)
    print(f"\nFile yang dihasilkan:")
    print(f"  1. {output_excel}")
    print(f"  2. {output_png}")
    print("\nSheet Excel:")
    print("  - Top 10 Absolute   : 10 kabupaten dengan peningkatan TB tertinggi")
    print("  - Top 20 Absolute   : 20 kabupaten dengan peningkatan TB tertinggi")
    print("  - Top 10 Percentage : 10 kabupaten dengan growth % tertinggi (perbandingan)")
    print("  - All Kabupaten     : Semua kabupaten terurut by absolute change")
    print("  - Comparison        : Perbandingan metrik Top 10 Absolute vs Percentage")
    print("\n" + "="*80)

if __name__ == "__main__":
    main()
