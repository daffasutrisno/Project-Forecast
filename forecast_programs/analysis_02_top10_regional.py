"""
ANALYSIS TOP 10 - BY REGIONAL GROWTH
======================================
Menghitung top 10 kabupaten dengan peningkatan traffic tertinggi
berdasarkan growth rate dari forecast regional masing-masing.

Input:
  - forecast_results/02_regional/*.csv (3 files)
  - Traffic_VLR_Java_2024-2025.xlsx

Output:
  - forecast_results/05_analysis/top10_kabupaten_regional.xlsx

Fungsi:
  - Gunakan % peningkatan dari forecast regional untuk proyeksi
  - Ranking berdasarkan % peningkatan tertinggi
  - Pengelompokan berdasarkan regional
"""

import pandas as pd
import numpy as np
from pathlib import Path

def get_regional_growth_rates():
    """Get growth rates dari hasil forecast regional"""
    
    regional_data = {}
    regional_dir = Path("forecast_results/02_regional")
    
    # Load data untuk setiap regional
    regions = ['BALI NUSRA', 'CENTRAL JAVA', 'EAST JAVA']
    
    for region in regions:
        # Load historical
        df = pd.read_excel("Traffic_VLR_Java_2024-2025.xlsx", sheet_name=0)
        df['Date'] = pd.to_datetime(df['Date'])
        
        df_region = df[df['REGION IOH'] == region].copy()
        daily_historical = df_region.groupby('Date')['Traffic_Total(TB)'].sum()
        hist_mean = daily_historical.mean()
        
        # Load forecast
        forecast_file = regional_dir / f"{region.lower().replace(' ', '_')}.csv"
        if forecast_file.exists():
            df_forecast = pd.read_csv(forecast_file)
            fore_mean = df_forecast['Traffic_Total(TB)'].mean()
            
            # Calculate growth rate
            growth_rate = ((fore_mean - hist_mean) / hist_mean) * 100
            
            regional_data[region] = {
                'historical_mean': hist_mean,
                'forecast_mean': fore_mean,
                'growth_rate': growth_rate
            }
            
            print(f"{region:15} : {growth_rate:+.2f}% growth")
    
    return regional_data

def calculate_kabupaten_projections(regional_data):
    """Calculate proyeksi untuk setiap kabupaten berdasarkan regional growth"""
    
    print("\n" + "="*80)
    print("Menghitung proyeksi per kabupaten...")
    print("="*80)
    
    # Load data
    df = pd.read_excel("Traffic_VLR_Java_2024-2025.xlsx", sheet_name=0)
    df['Date'] = pd.to_datetime(df['Date'])
    
    # Calculate historical average per kabupaten
    kabupaten_summary = []
    
    for kabupaten in df['KABUPATEN IOH'].unique():
        df_kab = df[df['KABUPATEN IOH'] == kabupaten].copy()
        
        # Get region
        region = df_kab['REGION IOH'].iloc[0]
        
        # Calculate historical stats
        daily_data = df_kab.groupby('Date')['Traffic_Total(TB)'].sum()
        hist_mean = daily_data.mean()
        hist_total = daily_data.sum()
        
        # Get regional growth rate
        if region in regional_data:
            growth_rate = regional_data[region]['growth_rate']
            
            # Calculate forecast
            fore_mean = hist_mean * (1 + growth_rate / 100)
            change = fore_mean - hist_mean
            
            kabupaten_summary.append({
                'Kabupaten': kabupaten,
                'Region': region,
                'Historical_Avg': hist_mean,
                'Forecast_Avg': fore_mean,
                'Change': change,
                'Growth_Rate': growth_rate,
                'Historical_Total': hist_total
            })
    
    df_summary = pd.DataFrame(kabupaten_summary)
    
    return df_summary

def main():
    """Main function"""
    print("="*80)
    print("  TOP 10 KABUPATEN - PENINGKATAN TRAFFIC TERTINGGI")
    print("="*80)
    print("\nBerdasarkan: Growth rate forecast regional\n")
    
    # Get regional growth rates
    print("📊 Regional Growth Rates:")
    print("-" * 80)
    regional_data = get_regional_growth_rates()
    
    # Calculate per kabupaten
    df_summary = calculate_kabupaten_projections(regional_data)
    
    # Sort by growth rate (descending)
    df_top10 = df_summary.nlargest(10, 'Growth_Rate')
    
    # Display results
    print("\n" + "="*80)
    print("  TOP 10 KABUPATEN DENGAN PENINGKATAN TERTINGGI")
    print("="*80)
    print()
    print(f"{'Rank':<6} {'Kabupaten':<25} {'Region':<15} {'Hist Avg':<12} {'Fore Avg':<12} {'Change':<12} {'Growth %':<10}")
    print("-"*110)
    
    for idx, row in df_top10.iterrows():
        rank = df_top10.index.get_loc(idx) + 1
        print(f"{rank:<6} {row['Kabupaten']:<25} {row['Region']:<15} "
              f"{row['Historical_Avg']:>10,.2f}  {row['Forecast_Avg']:>10,.2f}  "
              f"{row['Change']:>+10,.2f}  {row['Growth_Rate']:>+8.2f}%")
    
    # Save to Excel
    output_file = Path("forecast_results/05_analysis/top10_kabupaten_by_regional_growth.xlsx")
    
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        # Top 10
        df_top10.to_excel(writer, sheet_name='Top 10', index=False)
        
        # All kabupaten sorted
        df_sorted = df_summary.sort_values('Growth_Rate', ascending=False)
        df_sorted.to_excel(writer, sheet_name='All Kabupaten', index=False)
        
        # Regional summary
        regional_df = pd.DataFrame([
            {
                'Region': region,
                'Historical_Mean': data['historical_mean'],
                'Forecast_Mean': data['forecast_mean'],
                'Growth_Rate': data['growth_rate']
            }
            for region, data in regional_data.items()
        ])
        regional_df.to_excel(writer, sheet_name='Regional Growth', index=False)
    
    print("\n" + "="*80)
    print("✅ SELESAI!")
    print("="*80)
    print(f"\nHasil disimpan: {output_file}")
    print("\nSheet yang tersedia:")
    print("  1. Top 10         - 10 kabupaten dengan pertumbuhan tertinggi")
    print("  2. All Kabupaten  - Semua kabupaten terurut")
    print("  3. Regional Growth - Growth rate per regional")
    print("\n" + "="*80)

if __name__ == "__main__":
    main()
