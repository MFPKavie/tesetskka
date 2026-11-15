# main.py
from grid_env import get_env, draw_map
from dijkstra import run_dijkstra

def main():
    # 1. User menginput ukuran grid, melukis peta, dan menentukan Start & Goal
    grid, start, goal = get_env()
    
    print(f"\nTitik Awal (Start): {start}")
    print(f"Titik Tujuan (Goal): {goal}")
    
    # 2. Menjalankan Algoritma Dijkstra
    total_battery_cost, optimal_path = run_dijkstra(grid, start, goal)
    
    if optimal_path:
        print(f"Status: Jalur Berhasil Ditemukan!")
        print(f"Total Konsumsi Baterai: {total_battery_cost}%")
        print(f"Koordinat Jalur: {optimal_path}")
        
        # 3. Menampilkan visualisasi hasil akhir
        draw_map(grid, start, goal, optimal_path)
    else:
        print("Status: Maaf, tidak ada jalur yang tersedia menuju tujuan (terhalang tembok penuh).")

if __name__ == "__main__":
    main()