"""
RUN ALL FORECAST PROGRAMS
==========================
Script untuk menjalankan semua program forecast secara berurutan.

Urutan eksekusi:
1. Forecast total traffic
2. Forecast per regional
3. Forecast per provinsi
4. Forecast per kabupaten (opsional)
5. Visualisasi semua forecast
6. Analisis top 10 kabupaten
"""

import subprocess
import sys
from pathlib import Path

def print_header(text):
    """Print formatted header"""
    print("\n" + "="*80)
    print(f"  {text}")
    print("="*80)

def print_step(step_num, total_steps, text):
    """Print step information"""
    print(f"\n[STEP {step_num}/{total_steps}] {text}")
    print("-"*80)

def run_script(script_name, description):
    """Run a Python script"""
    print(f"\n▶ Menjalankan: {script_name}")
    print(f"  {description}")
    print()
    
    try:
        # Change to parent directory since scripts expect to be run from root
        root_dir = Path(__file__).parent.parent
        result = subprocess.run(
            [sys.executable, str(Path(__file__).parent / script_name)],
            cwd=root_dir,
            check=True,
            capture_output=False
        )
        print(f"\n✓ {script_name} selesai")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n✗ Error menjalankan {script_name}")
        print(f"  Exit code: {e.returncode}")
        return False
    except FileNotFoundError:
        print(f"\n✗ File tidak ditemukan: {script_name}")
        return False

def main():
    """Main execution"""
    print_header("RUN ALL FORECAST PROGRAMS")
    
    print("\n⚠️  CATATAN:")
    print("  - Forecast kabupaten memakan waktu ~5-10 menit")
    print("  - Jika tidak ingin menjalankan forecast kabupaten, tekan Ctrl+C saat proses tersebut")
    print()
    
    total_steps = 9
    
    # Step 1: Forecast Main Total
    print_step(1, total_steps, "Forecast Total Traffic")
    if not run_script("forecast_01_main_total.py", "Forecast traffic keseluruhan"):
        return
    
    # Step 2: Forecast Regional
    print_step(2, total_steps, "Forecast Regional")
    if not run_script("forecast_03_by_regional.py", "Forecast 3 regional (Bali Nusra, Central Java, East Java)"):
        return
    
    # Step 3: Forecast Provinsi
    print_step(3, total_steps, "Forecast Provinsi")
    if not run_script("forecast_02_by_province.py", "Forecast 6 provinsi"):
        return
    
    # Step 4: Forecast Kabupaten (optional)
    print_step(4, total_steps, "Forecast Kabupaten (⚠️  Proses Lama)")
    if not run_script("forecast_04_by_kabupaten.py", "Forecast 119 kabupaten (~5-10 menit)"):
        print("\n⚠️  Forecast kabupaten gagal atau dibatalkan")
        print("  Program akan lanjut ke tahap visualisasi tanpa data kabupaten")
    
    # Step 5: Visualisasi All Forecasts
    print_step(5, total_steps, "Visualisasi All Forecasts")
    if not run_script("visualize_01_all_forecasts.py", "Visualisasi lengkap semua forecast"):
        return
    
    # Step 6: Visualisasi Main Overview
    print_step(6, total_steps, "Visualisasi Main Overview")
    if not run_script("visualize_02_main_overview.py", "Visualisasi main forecast overview"):
        return
    
    # Step 7: Visualisasi Province Summary
    print_step(7, total_steps, "Visualisasi Province Summary")
    if not run_script("visualize_03_province_summary.py", "Summary comparison provinsi"):
        return
    
    # Step 8: Analysis Top 10 Absolute
    print_step(8, total_steps, "Analysis Top 10 - Absolute Change")
    if not run_script("analysis_01_top10_absolute.py", "Top 10 kabupaten peningkatan absolut"):
        print("\n⚠️  Analysis absolute gagal (mungkin data kabupaten belum ada)")
    
    # Step 9: Analysis Top 10 Percentage
    print_step(9, total_steps, "Analysis Top 10 - Percentage Growth")
    if not run_script("analysis_03_top10_percentage.py", "Top 10 kabupaten persentase pertumbuhan"):
        print("\n⚠️  Analysis percentage gagal (mungkin data kabupaten belum ada)")
    
    print_header("SEMUA PROSES SELESAI!")
    print("\n✓ Forecast dan analisis telah selesai")
    print("✓ Hasil tersimpan di folder forecast_results/")
    print("\nUntuk membuat PowerPoint:")
    print("  python ../generate_ppt_complete.py")
    print("="*80)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Proses dibatalkan oleh user")
        sys.exit(1)
