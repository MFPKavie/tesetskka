# main.py
import time
import tkinter as tk
from tkinter import messagebox

from bfs import run_bfs
from dfs import run_dfs
from dijkstra import run_dijkstra
from grid_env import draw_multi_results, get_env
from ucs import run_ucs

ALGORITHM_RUNNERS = {
    "UCS (Uniform Cost Search)": run_ucs,
    "BFS (Breadth-First Search)": run_bfs,
    "DFS (Depth-First Search)": run_dfs,
}


def main():
    # 1. Buka konfigurator peta & pilih algoritma (minimal 1)
    grid, start, goal, selected_algorithms = get_env()

    # Jika user menutup jendela konfigurator (tombol X) tanpa klik Start
    if not selected_algorithms:
        print("Simulasi dibatalkan oleh pengguna.")
        return

    print(f"\nTitik Awal (Start) : {start}")
    print(f"Titik Tujuan (Goal): {goal}")
    print("-" * 55)

    results = []
    any_path_found = False

    # 2. Jalankan setiap algoritma yang dipilih secara berurutan
    for algo_name in selected_algorithms:
        runner = ALGORITHM_RUNNERS[algo_name]

        started_at = time.perf_counter()
        total_cost, path, visited_count = runner(grid, start, goal)
        elapsed_ms = (time.perf_counter() - started_at) * 1000

        if path:
            any_path_found = True
            print(f"[{algo_name}]")
            print(f"  Baterai: {total_cost}% | Langkah: {len(path)} | Node: {visited_count} | Waktu: {elapsed_ms:.2f} ms")
        else:
            print(f"[{algo_name}] -> Jalur tidak ditemukan.")

        results.append({
            "name": algo_name,
            "cost": total_cost,
            "path": path,
            "visited": visited_count,
            "time_ms": elapsed_ms,
        })

    print("-" * 55)

    # 3. Tampilkan hasil visual jika minimal satu rute ditemukan
    if any_path_found:
        draw_multi_results(grid, start, goal, results)
    else:
        root = tk.Tk()
        root.withdraw()
        messagebox.showwarning("Jalur Buntu", "Tidak ada rute yang dapat mencapai tujuan (terhalang tembok penuh)!")
        root.destroy()


if __name__ == "__main__":
    main()