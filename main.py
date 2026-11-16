# main.py
import time

from dijkstra import run_dijkstra
from grid_env import draw_map, get_env
from ucs import run_ucs

# Pemetaan nama algoritma di menu -> fungsi pencarian rute
ALGORITHM_RUNNERS = {
    "Dijkstra": run_dijkstra,
    "UCS (Uniform Cost Search)": run_ucs,
}


def main():
    # 1. User menginput ukuran grid, melukis peta, menentukan Start & Goal,
    #    dan memilih algoritma lewat menu "Algoritma"
    grid, start, goal, algorithm = get_env()

    print(f"\nAlgoritma        : {algorithm}")
    print(f"Titik Awal (Start): {start}")
    print(f"Titik Tujuan (Goal): {goal}")

    runner = ALGORITHM_RUNNERS[algorithm]

    # 2. Menjalankan algoritma yang dipilih
    started_at = time.perf_counter()
    total_battery_cost, optimal_path = runner(grid, start, goal)
    elapsed_ms = (time.perf_counter() - started_at) * 1000

    if optimal_path:
        print("Status: Jalur Berhasil Ditemukan!")
        print(f"Total Konsumsi Baterai: {total_battery_cost}%")
        print(f"Panjang Rute: {len(optimal_path)} petak")
        print(f"Waktu Komputasi: {elapsed_ms:.2f} ms")
        print(f"Koordinat Jalur: {optimal_path}")

        # 3. Menampilkan visualisasi hasil akhir
        draw_map(grid, start, goal, optimal_path, algorithm, total_battery_cost)
    else:
        print("Status: Maaf, tidak ada jalur yang tersedia menuju tujuan (terhalang tembok penuh).")


if __name__ == "__main__":
    main()
