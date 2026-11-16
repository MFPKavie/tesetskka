# grid_env.py
import random
import tkinter as tk
from tkinter import messagebox, simpledialog

# Konfigurasi Warna Tema 2D
COLORS = {
    1: "#E0E0E0",   # Normal terrain (Abu-abu muda) - 1% Pwr
    3: "#808080",   # Tanjakan (Abu-abu tua) - 3% Pwr
    5: "#FF9999",   # Macet (Merah muda) - 5% Pwr
    -1: "#333333"   # Tembok / Rintangan (Gelap)
}

CELL_SIZE = 50
PADDING = 4

# Konfigurasi Algoritma: Nama -> (Kode, Warna Garis/Titik, Offset Koordinat agar tidak bertumpuk)
ALGO_STYLES = {
    "UCS (Uniform Cost Search)": {"color": "#00C853", "offset": (-6, -6)},  # Hijau Zamrud   
    "BFS (Breadth-First Search)":{"color": "#FF6D00", "offset": (-6, 6)},   # Oranye
    "DFS (Depth-First Search)":  {"color": "#AA00FF", "offset": (6, 6)},    # Ungu
}

MIN_WINDOW_WIDTH = 950
MIN_WINDOW_HEIGHT = 720


class GridConfigurator:
    def __init__(self, root, rows, cols):
        self.root = root
        self.root.title("EV Navigation - Custom Grid Configurator")

        self.rows = rows
        self.cols = cols

        self.grid = [[1 for _ in range(cols)] for _ in range(rows)]
        self.start_pos = (rows - 1, 0)
        self.goal_pos = (0, cols - 1)
        self.mode = 1

        # Variabel Checkbutton untuk tiap algoritma (Default: UCS & BFS aktif)
        self.algo_vars = {}
        for idx, name in enumerate(ALGO_STYLES.keys()):
            self.algo_vars[name] = tk.BooleanVar(value=(name in ["UCS (Uniform Cost Search)", "BFS (Breadth-First Search)"]))

        self.selected_algorithms = []

        # --- BARIS 1: Kontrol Alat Edit Peta ---
        self.control_frame = tk.Frame(root)
        self.control_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=(10, 5))

        tk.Label(self.control_frame, text="Alat Edit:", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=5)

        tk.Button(self.control_frame, text="Normal (1)", bg=COLORS[1], command=lambda: self.set_mode(1)).pack(side=tk.LEFT, padx=2)
        tk.Button(self.control_frame, text="Tanjakan (3)", bg=COLORS[3], fg="white", command=lambda: self.set_mode(3)).pack(side=tk.LEFT, padx=2)
        tk.Button(self.control_frame, text="Macet (5)", bg=COLORS[5], command=lambda: self.set_mode(5)).pack(side=tk.LEFT, padx=2)
        tk.Button(self.control_frame, text="Tembok (-1)", bg=COLORS[-1], fg="white", command=lambda: self.set_mode(-1)).pack(side=tk.LEFT, padx=2)

        tk.Label(self.control_frame, text=" | ").pack(side=tk.LEFT)

        tk.Button(self.control_frame, text="Set Start (S)", bg="lightblue", command=lambda: self.set_mode('S')).pack(side=tk.LEFT, padx=2)
        tk.Button(self.control_frame, text="Set Goal (G)", bg="lightcoral", command=lambda: self.set_mode('G')).pack(side=tk.LEFT, padx=2)

        tk.Label(self.control_frame, text=" | ").pack(side=tk.LEFT)

        tk.Button(self.control_frame, text="Acak Grid", bg="khaki", command=self.randomize_grid).pack(side=tk.LEFT, padx=2)
        tk.Button(self.control_frame, text="Reset", bg="white", command=self.reset_grid).pack(side=tk.LEFT, padx=2)

        tk.Label(self.control_frame, text="Tembok %:").pack(side=tk.LEFT, padx=(8, 2))
        self.wall_ratio_var = tk.IntVar(value=20)
        tk.Spinbox(self.control_frame, from_=0, to=60, width=4, textvariable=self.wall_ratio_var).pack(side=tk.LEFT, padx=2)

        # --- BARIS 2: Pilihan Multi-Algoritma (Checkbox) ---
        self.algo_frame = tk.Frame(root, relief=tk.GROOVE, borderwidth=1, padx=8, pady=6)
        self.algo_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

        tk.Label(self.algo_frame, text="Pilih Algoritma (Min. 1):", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=5)

        for name, style in ALGO_STYLES.items():
            cb = tk.Checkbutton(
                self.algo_frame,
                text=name,
                variable=self.algo_vars[name],
                fg=style["color"],
                font=("Arial", 9, "bold"),
                activeforeground=style["color"]
            )
            cb.pack(side=tk.LEFT, padx=8)

        # --- CANVAS GRID ---
        self.canvas = tk.Canvas(root, width=cols * CELL_SIZE, height=rows * CELL_SIZE, bg="white")
        self.canvas.pack(padx=10, pady=10)
        self.canvas.bind("<Button-1>", self.on_cell_click)

        # --- TOMBOL START ---
        self.btn_done = tk.Button(
            root,
            text="▶ Start Simulasi",
            bg="#4CAF50",
            fg="white",
            font=("Arial", 11, "bold"),
            padx=15,
            pady=5,
            command=self.finish_config
        )
        self.btn_done.pack(side=tk.BOTTOM, pady=10)

        self._setup_window_size()
        self.draw_grid()

    def _setup_window_size(self):
        self.root.update_idletasks()
        width = max(self.root.winfo_reqwidth(), MIN_WINDOW_WIDTH)
        height = max(self.root.winfo_reqheight(), MIN_WINDOW_HEIGHT)

        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()

        width = min(width, screen_w - 40)
        height = min(height, screen_h - 80)

        x = max((screen_w - width) // 2, 0)
        y = max((screen_h - height) // 3, 0)

        self.root.minsize(MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def set_mode(self, m):
        self.mode = m

    def reset_grid(self):
        self.grid = [[1 for _ in range(self.cols)] for _ in range(self.rows)]
        self.draw_grid()

    def randomize_grid(self, max_attempts=30):
        wall_ratio = max(0, min(self.wall_ratio_var.get(), 60)) / 100.0
        protected = {self.start_pos, self.goal_pos}
        terrain_pool = [1, 1, 1, 3, 5]

        new_grid = self.grid
        for _ in range(max_attempts):
            new_grid = [[1 for _ in range(self.cols)] for _ in range(self.rows)]
            for r in range(self.rows):
                for c in range(self.cols):
                    if (r, c) in protected:
                        continue
                    if random.random() < wall_ratio:
                        new_grid[r][c] = -1
                    else:
                        new_grid[r][c] = random.choice(terrain_pool)

            if self._is_reachable(new_grid):
                break

        self.grid = new_grid
        self.draw_grid()

    def _is_reachable(self, grid):
        from collections import deque
        seen = {self.start_pos}
        queue = deque([self.start_pos])
        while queue:
            r, c = queue.popleft()
            if (r, c) == self.goal_pos:
                return True
            for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                nr, nc = r + dr, c + dc
                if (0 <= nr < self.rows and 0 <= nc < self.cols
                        and (nr, nc) not in seen and grid[nr][nc] != -1):
                    seen.add((nr, nc))
                    queue.append((nr, nc))
        return False

    def draw_grid(self):
        self.canvas.delete("all")
        for r in range(self.rows):
            for c in range(self.cols):
                val = self.grid[r][c]
                color = COLORS.get(val, "#E0E0E0")

                x1 = c * CELL_SIZE + PADDING
                y1 = r * CELL_SIZE + PADDING
                x2 = (c + 1) * CELL_SIZE - PADDING
                y2 = (r + 1) * CELL_SIZE - PADDING

                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="black", width=1)

                pos = (r, c)
                if pos == self.start_pos:
                    self.canvas.create_text((x1+x2)/2, (y1+y2)/2, text="S", fill="blue", font=("Arial", 16, "bold"))
                elif pos == self.goal_pos:
                    self.canvas.create_text((x1+x2)/2, (y1+y2)/2, text="G", fill="red", font=("Arial", 16, "bold"))

    def on_cell_click(self, event):
        c = event.x // CELL_SIZE
        r = event.y // CELL_SIZE

        if 0 <= r < self.rows and 0 <= c < self.cols:
            if self.mode == 'S':
                if self.grid[r][c] == -1:
                    messagebox.showerror("Error", "Titik Start tidak boleh berada di atas Tembok!")
                    return
                self.start_pos = (r, c)
            elif self.mode == 'G':
                if self.grid[r][c] == -1:
                    messagebox.showerror("Error", "Titik Goal tidak boleh berada di atas Tembok!")
                    return
                self.goal_pos = (r, c)
            else:
                if (r, c) == self.start_pos or (r, c) == self.goal_pos:
                    if self.mode == -1:
                        messagebox.showerror("Error", "Petak Start atau Goal tidak bisa diubah menjadi Tembok!")
                        return
                self.grid[r][c] = self.mode

            self.draw_grid()

    def finish_config(self):
        if self.start_pos == self.goal_pos:
            messagebox.showerror("Error", "Titik Start dan Goal tidak boleh di koordinat yang sama!")
            return

        # Validasi: Minimal 1 algoritma harus dipilih
        chosen = [name for name, var in self.algo_vars.items() if var.get()]
        if not chosen:
            messagebox.showwarning("Peringatan", "Pilih minimal satu algoritma sebelum memulai simulasi!")
            return

        self.selected_algorithms = chosen
        self.root.destroy()


def get_env():
    """Meminta input ukuran grid dari user, lalu membuka UI interaktif."""
    root = tk.Tk()
    root.withdraw()

    cols = simpledialog.askinteger("Input Grid", "Masukkan jumlah Kolom (lebar, misal: 6-12):", initialvalue=8, minvalue=3, maxvalue=20)
    rows = simpledialog.askinteger("Input Grid", "Masukkan jumlah Baris (tinggi, misal: 6-12):", initialvalue=8, minvalue=3, maxvalue=20)

    if not cols or not rows:
        cols, rows = 8, 8

    root.destroy()

    config_root = tk.Tk()
    app = GridConfigurator(config_root, rows, cols)
    config_root.mainloop()

    return app.grid, app.start_pos, app.goal_pos, app.selected_algorithms


def draw_multi_results(grid, start, goal, results):
    """
    Menampilkan semua rute dari algoritma yang dipilih pada satu peta 2D
    dengan garis warna berbeda & panel legenda perbandingan.
    
    results: list of dict -> [
        {"name": str, "cost": float, "path": list, "visited": int, "time_ms": float}, ...
    ]
    """
    root = tk.Tk()
    root.title("EV Navigation - Hasil Perbandingan Rute")

    main_frame = tk.Frame(root)
    main_frame.pack(padx=15, pady=15)

    rows, cols = len(grid), len(grid[0])
    canvas = tk.Canvas(main_frame, width=cols * CELL_SIZE, height=rows * CELL_SIZE, bg="white")
    canvas.pack(side=tk.LEFT, padx=(0, 15))

    # 1. Gambar Grid Dasar
    for r in range(rows):
        for c in range(cols):
            val = grid[r][c]
            color = COLORS.get(val, "#E0E0E0")

            x1 = c * CELL_SIZE + PADDING
            y1 = r * CELL_SIZE + PADDING
            x2 = (c + 1) * CELL_SIZE - PADDING
            y2 = (r + 1) * CELL_SIZE - PADDING

            canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="black", width=1)

    # 2. Gambar Garis Rute untuk Masing-Masing Algoritma (dengan sedikit offset)
    for res in results:
        path = res["path"]
        if not path:
            continue

        style = ALGO_STYLES[res["name"]]
        line_color = style["color"]
        ox, oy = style["offset"]

        coords = []
        for (r, c) in path:
            cx = c * CELL_SIZE + (CELL_SIZE / 2) + ox
            cy = r * CELL_SIZE + (CELL_SIZE / 2) + oy
            coords.extend([cx, cy])

            # Titik kecil di tiap langkah
            canvas.create_oval(cx - 3.5, cy - 3.5, cx + 3.5, cy + 3.5, fill=line_color, outline="")

        # Garis penghubung rute
        if len(coords) >= 4:
            canvas.create_line(*coords, fill=line_color, width=3, smooth=False)

    # 3. Gambar Label S dan G di layer paling atas agar tidak tertutup garis
    for pos, label, fg_color in [(start, "S", "blue"), (goal, "G", "red")]:
        r, c = pos
        cx = c * CELL_SIZE + (CELL_SIZE / 2)
        cy = r * CELL_SIZE + (CELL_SIZE / 2)
        canvas.create_oval(cx - 14, cy - 14, cx + 14, cy + 14, fill="white", outline=fg_color, width=2)
        canvas.create_text(cx, cy, text=label, fill=fg_color, font=("Arial", 14, "bold"))

    # 4. Panel Legenda & Tabel Metrik di Sebelah Kanan Peta
    legend_frame = tk.Frame(main_frame, relief=tk.RIDGE, borderwidth=2, padx=12, pady=12)
    legend_frame.pack(side=tk.RIGHT, fill=tk.Y)

    tk.Label(legend_frame, text="Hasil & Perbandingan Algoritma", font=("Arial", 12, "bold")).pack(anchor="w", pady=(0, 10))

    for res in results:
        name = res["name"]
        color = ALGO_STYLES[name]["color"]

        card = tk.Frame(legend_frame, pady=6)
        card.pack(fill=tk.X, anchor="w")

        # Header warna + nama algoritma
        header = tk.Frame(card)
        header.pack(anchor="w")
        tk.Label(header, text="■■", fg=color, font=("Arial", 12, "bold")).pack(side=tk.LEFT)
        tk.Label(header, text=f" {name}", font=("Arial", 10, "bold")).pack(side=tk.LEFT)

        # Detail Statistik
        if res["path"]:
            detail = (
                f"   • Konsumsi Baterai : {res['cost']}%\n"
                f"   • Panjang Rute      : {len(res['path'])} petak\n"
                f"   • Node Dieksplorasi : {res['visited']} node\n"
                f"   • Waktu Komputasi   : {res['time_ms']:.2f} ms"
            )
        else:
            detail = "   • Status: Jalur tidak ditemukan"

        tk.Label(card, text=detail, justify=tk.LEFT, font=("Consolas", 9)).pack(anchor="w")
        tk.Frame(legend_frame, height=1, bg="#CCCCCC").pack(fill=tk.X, pady=4)

    # Atur ukuran window otomatis menyesuaikan konten
    root.update_idletasks()
    width = root.winfo_reqwidth() + 40
    height = max(root.winfo_reqheight() + 40, 480)
    screen_w = root.winfo_screenwidth()
    screen_h = root.winfo_screenheight()
    root.geometry(f"{min(width, screen_w - 40)}x{min(height, screen_h - 80)}")

    root.mainloop()