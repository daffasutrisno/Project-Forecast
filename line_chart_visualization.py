"""
Traffic VLR Data - Line Chart Visualization
Fokus pada visualisasi line chart untuk analisis tren traffic
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import numpy as np

# Set style untuk grafik yang lebih menarik
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("husl")

def load_data(filename):
    """Load data dari file Excel"""
    try:
        df = pd.read_excel(filename, sheet_name=0)
        print(f"✓ Data berhasil dimuat: {df.shape[0]} baris, {df.shape[1]} kolom")
        return df
    except Exception as e:
        print(f"Error loading data: {e}")
        return None

def create_line_charts(df, output_folder="line_charts"):
    """Membuat berbagai jenis line chart"""
    Path(output_folder).mkdir(exist_ok=True)
    
    # Pastikan kolom Date dalam format datetime
    df['Date'] = pd.to_datetime(df['Date'])
    
    # 1. LINE CHART - Traffic Total per Hari (Agregat)
    print("\n📈 Membuat Line Chart 1: Traffic Total Harian...")
    daily_traffic = df.groupby('Date').agg({
        'Traffic_H3I (TB)': 'sum',
        'Traffic_IM3 (TB)': 'sum',
        'Traffic_Total(TB)': 'sum'
    }).reset_index()
    
    plt.figure(figsize=(16, 8))
    plt.plot(daily_traffic['Date'], daily_traffic['Traffic_Total(TB)'], 
             marker='o', linewidth=2.5, markersize=4, color='#2E86AB', label='Total Traffic')
    plt.plot(daily_traffic['Date'], daily_traffic['Traffic_H3I (TB)'], 
             marker='s', linewidth=2, markersize=3, color='#A23B72', label='H3I Traffic', alpha=0.8)
    plt.plot(daily_traffic['Date'], daily_traffic['Traffic_IM3 (TB)'], 
             marker='^', linewidth=2, markersize=3, color='#F18F01', label='IM3 Traffic', alpha=0.8)
    
    plt.xlabel('Tanggal', fontsize=14, fontweight='bold')
    plt.ylabel('Traffic (TB)', fontsize=14, fontweight='bold')
    plt.title('Tren Traffic Total Harian - VLR Java (2024-2025)', fontsize=16, fontweight='bold', pad=20)
    plt.legend(loc='best', fontsize=12, framealpha=0.9)
    plt.grid(True, alpha=0.3, linestyle='--')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(f"{output_folder}/01_traffic_harian_total.png", dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ Line Chart 1 selesai")
    
    # 2. LINE CHART - VLR Subscribers per Hari
    print("📈 Membuat Line Chart 2: VLR Subscribers Harian...")
    daily_vlr = df.groupby('Date').agg({
        'VLR_3ID_subs': 'sum',
        'VLR_IM3_subs': 'sum'
    }).reset_index()
    daily_vlr['VLR_Total'] = daily_vlr['VLR_3ID_subs'] + daily_vlr['VLR_IM3_subs']
    
    plt.figure(figsize=(16, 8))
    plt.plot(daily_vlr['Date'], daily_vlr['VLR_Total'], 
             marker='o', linewidth=3, markersize=4, color='#06A77D', label='Total Subscribers')
    plt.plot(daily_vlr['Date'], daily_vlr['VLR_3ID_subs'], 
             marker='D', linewidth=2, markersize=3, color='#005E7C', label='3ID Subscribers', alpha=0.8)
    plt.plot(daily_vlr['Date'], daily_vlr['VLR_IM3_subs'], 
             marker='v', linewidth=2, markersize=3, color='#D62246', label='IM3 Subscribers', alpha=0.8)
    
    plt.xlabel('Tanggal', fontsize=14, fontweight='bold')
    plt.ylabel('Jumlah Subscribers', fontsize=14, fontweight='bold')
    plt.title('Tren VLR Subscribers Harian - VLR Java (2024-2025)', fontsize=16, fontweight='bold', pad=20)
    plt.legend(loc='best', fontsize=12, framealpha=0.9)
    plt.grid(True, alpha=0.3, linestyle='--')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(f"{output_folder}/02_vlr_subscribers_harian.png", dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ Line Chart 2 selesai")
    
    # 3. LINE CHART - Traffic per Province (Top 5)
    print("📈 Membuat Line Chart 3: Traffic per Provinsi (Top 5)...")
    top_provinces = df.groupby('PROVINCE')['Traffic_Total(TB)'].sum().nlargest(5).index
    province_daily = df[df['PROVINCE'].isin(top_provinces)].groupby(['Date', 'PROVINCE'])['Traffic_Total(TB)'].sum().reset_index()
    
    plt.figure(figsize=(16, 8))
    colors = ['#E63946', '#F77F00', '#06A77D', '#4361EE', '#7209B7']
    for i, province in enumerate(top_provinces):
        province_data = province_daily[province_daily['PROVINCE'] == province]
        plt.plot(province_data['Date'], province_data['Traffic_Total(TB)'], 
                marker='o', linewidth=2.5, markersize=3, label=province, color=colors[i])
    
    plt.xlabel('Tanggal', fontsize=14, fontweight='bold')
    plt.ylabel('Traffic Total (TB)', fontsize=14, fontweight='bold')
    plt.title('Tren Traffic per Provinsi (Top 5) - VLR Java', fontsize=16, fontweight='bold', pad=20)
    plt.legend(loc='best', fontsize=11, framealpha=0.9)
    plt.grid(True, alpha=0.3, linestyle='--')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(f"{output_folder}/03_traffic_per_provinsi_top5.png", dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ Line Chart 3 selesai")
    
    # 4. LINE CHART - Traffic per Region (Top 5)
    print("📈 Membuat Line Chart 4: Traffic per Region...")
    top_regions = df.groupby('REGION IOH')['Traffic_Total(TB)'].sum().nlargest(5).index
    region_daily = df[df['REGION IOH'].isin(top_regions)].groupby(['Date', 'REGION IOH'])['Traffic_Total(TB)'].sum().reset_index()
    
    plt.figure(figsize=(16, 8))
    for region in top_regions:
        region_data = region_daily[region_daily['REGION IOH'] == region]
        plt.plot(region_data['Date'], region_data['Traffic_Total(TB)'], 
                marker='o', linewidth=2.5, markersize=3, label=region)
    
    plt.xlabel('Tanggal', fontsize=14, fontweight='bold')
    plt.ylabel('Traffic Total (TB)', fontsize=14, fontweight='bold')
    plt.title('Tren Traffic per Region (Top 5) - VLR Java', fontsize=16, fontweight='bold', pad=20)
    plt.legend(loc='best', fontsize=11, framealpha=0.9)
    plt.grid(True, alpha=0.3, linestyle='--')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(f"{output_folder}/04_traffic_per_region_top5.png", dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ Line Chart 4 selesai")
    
    # 5. LINE CHART - Monthly Average Traffic
    print("📈 Membuat Line Chart 5: Traffic Rata-rata Bulanan...")
    df['Month'] = df['Date'].dt.to_period('M')
    monthly_traffic = df.groupby('Month').agg({
        'Traffic_H3I (TB)': 'mean',
        'Traffic_IM3 (TB)': 'mean',
        'Traffic_Total(TB)': 'mean'
    }).reset_index()
    monthly_traffic['Month'] = monthly_traffic['Month'].astype(str)
    
    plt.figure(figsize=(14, 8))
    x = range(len(monthly_traffic))
    plt.plot(x, monthly_traffic['Traffic_Total(TB)'], 
             marker='o', linewidth=3, markersize=8, color='#2E86AB', label='Total Traffic (Avg)')
    plt.plot(x, monthly_traffic['Traffic_H3I (TB)'], 
             marker='s', linewidth=2.5, markersize=6, color='#A23B72', label='H3I Traffic (Avg)', alpha=0.8)
    plt.plot(x, monthly_traffic['Traffic_IM3 (TB)'], 
             marker='^', linewidth=2.5, markersize=6, color='#F18F01', label='IM3 Traffic (Avg)', alpha=0.8)
    
    plt.xlabel('Bulan', fontsize=14, fontweight='bold')
    plt.ylabel('Traffic Rata-rata (TB)', fontsize=14, fontweight='bold')
    plt.title('Tren Traffic Rata-rata Bulanan - VLR Java', fontsize=16, fontweight='bold', pad=20)
    plt.legend(loc='best', fontsize=12, framealpha=0.9)
    plt.xticks(x, monthly_traffic['Month'], rotation=45, ha='right')
    plt.grid(True, alpha=0.3, linestyle='--')
    plt.tight_layout()
    plt.savefig(f"{output_folder}/05_traffic_bulanan_average.png", dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ Line Chart 5 selesai")
    
    # 6. LINE CHART - Traffic Comparison H3I vs IM3 dengan dual axis
    print("📈 Membuat Line Chart 6: Perbandingan H3I vs IM3...")
    fig, ax1 = plt.subplots(figsize=(16, 8))
    
    ax1.plot(daily_traffic['Date'], daily_traffic['Traffic_H3I (TB)'], 
             marker='o', linewidth=2.5, markersize=4, color='#A23B72', label='H3I Traffic')
    ax1.set_xlabel('Tanggal', fontsize=14, fontweight='bold')
    ax1.set_ylabel('H3I Traffic (TB)', fontsize=14, fontweight='bold', color='#A23B72')
    ax1.tick_params(axis='y', labelcolor='#A23B72')
    ax1.grid(True, alpha=0.3, linestyle='--')
    
    ax2 = ax1.twinx()
    ax2.plot(daily_traffic['Date'], daily_traffic['Traffic_IM3 (TB)'], 
             marker='^', linewidth=2.5, markersize=4, color='#F18F01', label='IM3 Traffic')
    ax2.set_ylabel('IM3 Traffic (TB)', fontsize=14, fontweight='bold', color='#F18F01')
    ax2.tick_params(axis='y', labelcolor='#F18F01')
    
    plt.title('Perbandingan Traffic H3I vs IM3 (Dual Axis)', fontsize=16, fontweight='bold', pad=20)
    fig.legend(loc='upper left', bbox_to_anchor=(0.12, 0.88), fontsize=12, framealpha=0.9)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(f"{output_folder}/06_comparison_h3i_vs_im3.png", dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ Line Chart 6 selesai")
    
    # 7. LINE CHART - Weekly Average Traffic
    print("📈 Membuat Line Chart 7: Traffic Rata-rata Mingguan...")
    df['Week'] = df['Date'].dt.to_period('W')
    weekly_traffic = df.groupby('Week').agg({
        'Traffic_Total(TB)': 'mean',
        'VLR_3ID_subs': 'mean',
        'VLR_IM3_subs': 'mean'
    }).reset_index()
    weekly_traffic['Week'] = weekly_traffic['Week'].astype(str)
    
    fig, ax1 = plt.subplots(figsize=(16, 8))
    x = range(len(weekly_traffic))
    
    ax1.plot(x, weekly_traffic['Traffic_Total(TB)'], 
             marker='o', linewidth=2.5, markersize=4, color='#2E86AB', label='Traffic Total (Avg)')
    ax1.set_xlabel('Minggu', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Traffic (TB)', fontsize=14, fontweight='bold', color='#2E86AB')
    ax1.tick_params(axis='y', labelcolor='#2E86AB')
    ax1.grid(True, alpha=0.3, linestyle='--')
    
    plt.title('Tren Traffic Mingguan - VLR Java', fontsize=16, fontweight='bold', pad=20)
    plt.xticks(x[::4], weekly_traffic['Week'][::4], rotation=45, ha='right')  # Show every 4th week
    plt.tight_layout()
    plt.savefig(f"{output_folder}/07_traffic_mingguan_average.png", dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ Line Chart 7 selesai")
    
    # 8. LINE CHART - Top 10 Kabupaten dengan traffic tertinggi
    print("📈 Membuat Line Chart 8: Traffic per Kabupaten (Top 10)...")
    top_kabupaten = df.groupby('KABUPATEN IOH')['Traffic_Total(TB)'].sum().nlargest(10).index
    kabupaten_daily = df[df['KABUPATEN IOH'].isin(top_kabupaten)].groupby(['Date', 'KABUPATEN IOH'])['Traffic_Total(TB)'].sum().reset_index()
    
    plt.figure(figsize=(18, 10))
    for kabupaten in top_kabupaten:
        kabupaten_data = kabupaten_daily[kabupaten_daily['KABUPATEN IOH'] == kabupaten]
        plt.plot(kabupaten_data['Date'], kabupaten_data['Traffic_Total(TB)'], 
                marker='o', linewidth=2, markersize=2, label=kabupaten, alpha=0.8)
    
    plt.xlabel('Tanggal', fontsize=14, fontweight='bold')
    plt.ylabel('Traffic Total (TB)', fontsize=14, fontweight='bold')
    plt.title('Tren Traffic per Kabupaten (Top 10) - VLR Java', fontsize=16, fontweight='bold', pad=20)
    plt.legend(loc='best', fontsize=10, framealpha=0.9, ncol=2)
    plt.grid(True, alpha=0.3, linestyle='--')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(f"{output_folder}/08_traffic_per_kabupaten_top10.png", dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ Line Chart 8 selesai")

def main():
    """Main function"""
    print("=" * 70)
    print("      VISUALISASI LINE CHART - TRAFFIC VLR JAVA 2024-2025")
    print("=" * 70)
    
    filename = "Traffic_VLR_Java_2024-2025.xlsx"
    
    if not Path(filename).exists():
        print(f"❌ Error: File '{filename}' tidak ditemukan!")
        return
    
    print(f"\n📂 Membaca file: {filename}")
    df = load_data(filename)
    
    if df is not None:
        print("\n" + "=" * 70)
        print("Membuat Line Charts...")
        print("=" * 70)
        
        create_line_charts(df)
        
        print("\n" + "=" * 70)
        print("✅ SELESAI! Semua line chart berhasil dibuat")
        print("=" * 70)
        print("\n📁 Lokasi: folder 'line_charts'")
        print("\n📊 Total 8 line chart yang dibuat:")
        print("   1. Traffic Total Harian (H3I + IM3 + Total)")
        print("   2. VLR Subscribers Harian (3ID + IM3 + Total)")
        print("   3. Traffic per Provinsi (Top 5)")
        print("   4. Traffic per Region (Top 5)")
        print("   5. Traffic Rata-rata Bulanan")
        print("   6. Perbandingan H3I vs IM3 (Dual Axis)")
        print("   7. Traffic Rata-rata Mingguan")
        print("   8. Traffic per Kabupaten (Top 10)")
        print("\n" + "=" * 70)
    else:
        print("❌ Gagal memuat data!")

if __name__ == "__main__":
    main()
