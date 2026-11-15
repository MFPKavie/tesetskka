# main.py
from grid_env import get_env
from dijkstra import run_dijkstra

def print_map_with_path(grid, path, start, goal):
    """Mencetak peta ke terminal dengan menandai jalur optimal (*)."""
    path_set = set(path)
    
    print("\n--- VISUALISASI PETA & RUTE OPTIMAL ---")
    for r in range(len(grid)):
        row_str = ""
        for c in range(len(grid[0])):
            pos = (r, c)
            if pos == start:
                row_str += " S  "  # Start
            elif pos == goal:
                row_str += " G  "  # Goal
            elif pos in path_set:
                row_str += " *  "  # Rute Optimal
            elif grid[r][c] == -1:
                row_str += " #  "  # Tembok/Rintangan
            else:
                row_str += f" {grid[r][c]}  "  # Bobot sel
        print(row_str)
    print("---------------------------------------\n")

def main():
    grid, start, goal = get_env()
    
    print(f"Titik Awal (Start): {start}")
    print(f"Titik Tujuan (Goal): {goal}")
    
    # Jalankan Dijkstra
    total_battery_cost, optimal_path = run_dijkstra(grid, start, goal)
    
    if optimal_path:
        print(f"Status: Jalur Berhasil Ditemukan!")
        print(f"Total Konsumsi Baterai: {total_battery_cost}%")
        print(f"Koordinat Jalur: {optimal_path}")
        print_map_with_path(grid, optimal_path, start, goal)
    else:
        print("Status: Maaf, tidak ada jalur yang tersedia menuju tujuan.")

if __name__ == "__main__":
    main()
