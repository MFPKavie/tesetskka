# grid_env.py

# Keterangan Bobot Medan (Konsumsi Baterai):
# 1 = Jalan Datar (Normal)
# 3 = Jalan Menanjak (Berat)
# 5 = Zona Kemacetan (Padat)
# -1 = Tembok / Rintangan (Tidak bisa dilewati)

DEFAULT_GRID = [
    [1, 1, 3, 1, 1],
    [1, -1, 3, -1, 1],
    [1, 1, 5, 1, 1],
    [3, -1, 5, -1, 3],
    [1, 1, 1, 1, 1]
]

START_POS = (0, 0)  # Pojok kiri atas
GOAL_POS = (4, 4)   # Pojok kanan bawah

def get_env():
    """Mengembalikan data grid, titik start, dan titik goal."""
    return DEFAULT_GRID, START_POS, GOAL_POS
