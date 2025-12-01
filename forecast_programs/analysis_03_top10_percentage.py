"""
ANALYSIS TOP 10 - PERCENTAGE GROWTH
=====================================
Menghitung top 10 kabupaten dengan peningkatan traffic tertinggi
berdasarkan hasil forecast individual masing-masing kabupaten.

Input:
  - forecast_results/04_kabupaten/[kabupaten]_forecast.csv (119 files)
  - Traffic_VLR_Java_2024-2025.xlsx

Output:
  - forecast_results/05_analysis/top10_kabupaten_individual_forecast.xlsx
  - forecast_results/05_analysis/top10_kabupaten_percentage_summary.png

Fungsi:
  - Gunakan forecast individual per kabupaten
  - Ranking berdasarkan % peningkatan tertinggi
  - Paling akurat karena mempertimbangkan pattern unik setiap kabupaten
  - Analisis top 10, top 20, semua kabupaten, dan regional summary
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
            
            # Calculate changes
            change = fore_mean - hist_mean
            growth_rate = (change / hist_mean) * 100 if hist_mean > 0 else 0
            
            kabupaten_summary.append({
                'Kabupaten': kabupaten_name,
                'Region': region,
                'Province': province,
                'Historical_Avg': hist_mean,
                'Historical_Std': hist_std,
                'Forecast_Avg': fore_mean,
                'Change_Avg': change,
                'Growth_Rate': growth_rate,
                'Historical_Total': hist_total,
                'Forecast_Total': fore_total,
                'Data_Days': len(daily_data)
            })
    
    df_summary = pd.DataFrame(kabupaten_summary)
    
    return df_summary

def create_visualization_top10(df_top10, output_file):
    """Create visualization untuk top 10 kabupaten"""
    
    import matplotlib.pyplot as plt
    
    fig, axes = plt.subplots(2, 2, figsize=(20, 14))
    fig.suptitle('TOP 10 KABUPATEN - PENINGKATAN TRAFFIC TERTINGGI\n(Berdasarkan Forecast Individual)',
                 fontsize=18, fontweight='bold', y=0.98)
    
    plt.subplots_adjust(hspace=0.35, wspace=0.3)
    
    # Plot 1: Growth Rate Comparison
    ax1 = axes[0, 0]
    
    kabupaten_names = [k[:15] + '...' if len(k) > 15 else k for k in df_top10['Kabupaten']]
    colors = plt.cm.RdYlGn(np.linspace(0.5, 0.9, len(df_top10)))
    
    bars = ax1.barh(range(len(df_top10)), df_top10['Growth_Rate'], color=colors, alpha=0.8, edgecolor='black')
    
    # Add value labels
    for i, (bar, val) in enumerate(zip(bars, df_top10['Growth_Rate'])):
        ax1.text(val + 0.2, bar.get_y() + bar.get_height()/2, 
                f'{val:+.2f}%', va='center', fontsize=10, fontweight='bold')
    
    ax1.set_yticks(range(len(df_top10)))
    ax1.set_yticklabels([f"{i+1}. {name}" for i, name in enumerate(kabupaten_names)], fontsize=10)
    ax1.set_xlabel('Growth Rate (%)', fontsize=12, fontweight='bold')
    ax1.set_title('Growth Rate Ranking', fontsize=14, fontweight='bold', pad=15)
    ax1.grid(True, alpha=0.3, axis='x')
    ax1.invert_yaxis()
    
    # Plot 2: Historical vs Forecast Average
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
    ax2.legend(loc='upper right', fontsize=10)
    ax2.grid(True, alpha=0.3, axis='y')
    
    # Plot 3: Change Distribution by Region
    ax3 = axes[1, 0]
    
    region_colors = {'BALI NUSRA': '#06A77D', 'CENTRAL JAVA': '#2E86AB', 'EAST JAVA': '#E63946'}
    
    for region in df_top10['Region'].unique():
        df_region = df_top10[df_top10['Region'] == region]
        ax3.scatter(df_region['Historical_Avg'], df_region['Growth_Rate'],
                   s=200, alpha=0.7, label=region, color=region_colors.get(region, 'gray'),
                   edgecolor='black', linewidth=1.5)
    
    ax3.set_xlabel('Historical Avg (TB/hari)', fontsize=12, fontweight='bold')
    ax3.set_ylabel('Growth Rate (%)', fontsize=12, fontweight='bold')
    ax3.set_title('Growth Rate vs Historical Average', fontsize=14, fontweight='bold', pad=15)
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
            row['Region'],
            f"{row['Historical_Avg']:.1f}",
            f"{row['Forecast_Avg']:.1f}",
            f"{row['Growth_Rate']:+.2f}%"
        ])
    
    col_labels = ['#', 'Kabupaten', 'Region', 'Hist\n(TB)', 'Fore\n(TB)', 'Growth\n(%)']
    
    table = ax4.table(cellText=table_data, colLabels=col_labels,
                     cellLoc='center', loc='center',
                     colWidths=[0.08, 0.28, 0.22, 0.14, 0.14, 0.14],
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
    print("  TOP 10 KABUPATEN - OPSI 3: FORECAST INDIVIDUAL")
    print("="*80)
    print("\nMenggunakan hasil forecast individual per kabupaten")
    print("Metode: Paling akurat dengan pattern unik setiap kabupaten\n")
    
    # Load data
    df_summary = load_kabupaten_forecast_data()
    
    if df_summary is None:
        return
    
    print(f"\n✓ Berhasil memproses {len(df_summary)} kabupaten")
    
    # Sort by growth rate (descending)
    df_sorted = df_summary.sort_values('Growth_Rate', ascending=False)
    df_top10 = df_sorted.head(10)
    
    # Display results
    print("\n" + "="*80)
    print("  TOP 10 KABUPATEN DENGAN PENINGKATAN TERTINGGI")
    print("="*80)
    print()
    print(f"{'Rank':<6} {'Kabupaten':<25} {'Region':<15} {'Hist Avg':<12} {'Fore Avg':<12} {'Change':<12} {'Growth %':<10}")
    print("-"*110)
    
    for idx, (_, row) in enumerate(df_top10.iterrows(), 1):
        print(f"{idx:<6} {row['Kabupaten']:<25} {row['Region']:<15} "
              f"{row['Historical_Avg']:>10,.2f}  {row['Forecast_Avg']:>10,.2f}  "
              f"{row['Change_Avg']:>+10,.2f}  {row['Growth_Rate']:>+8.2f}%")
    
    # Regional distribution
    print("\n" + "="*80)
    print("  DISTRIBUSI PER REGIONAL")
    print("="*80)
    
    regional_count = df_top10['Region'].value_counts()
    for region, count in regional_count.items():
        print(f"  {region:<20} : {count} kabupaten")
    
    # Save to Excel
    output_excel = Path("forecast_results/05_analysis/top10_kabupaten_individual_forecast.xlsx")
    
    with pd.ExcelWriter(output_excel, engine='openpyxl') as writer:
        # Top 10
        df_top10.to_excel(writer, sheet_name='Top 10', index=False)
        
        # Top 20
        df_top20 = df_sorted.head(20)
        df_top20.to_excel(writer, sheet_name='Top 20', index=False)
        
        # All kabupaten sorted
        df_sorted.to_excel(writer, sheet_name='All Kabupaten', index=False)
        
        # Regional summary
        regional_summary = df_summary.groupby('Region').agg({
            'Growth_Rate': ['mean', 'min', 'max'],
            'Kabupaten': 'count'
        }).round(2)
        regional_summary.to_excel(writer, sheet_name='Regional Summary')
    
    print(f"\n✓ Excel disimpan: {output_excel}")
    
    # Create visualization
    output_png = Path("forecast_results/05_analysis/top10_kabupaten_individual_forecast.png")
    create_visualization_top10(df_top10, output_png)
    
    print("\n" + "="*80)
    print("✅ SELESAI!")
    print("="*80)
    print(f"\nFile yang dihasilkan:")
    print(f"  1. {output_excel}")
    print(f"  2. {output_png}")
    print("\nSheet Excel:")
    print("  - Top 10          : 10 kabupaten dengan pertumbuhan tertinggi")
    print("  - Top 20          : 20 kabupaten dengan pertumbuhan tertinggi")
    print("  - All Kabupaten   : Semua kabupaten terurut")
    print("  - Regional Summary: Statistik per regional")
    print("\n" + "="*80)

if __name__ == "__main__":
    main()
