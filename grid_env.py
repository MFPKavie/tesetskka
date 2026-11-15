# grid_env.py
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

class GridConfigurator:
    def __init__(self, root, rows, cols):
        self.root = root
        self.root.title("EV Navigation - Custom Grid Configurator")
        
        self.rows = rows
        self.cols = cols
        
        # Inisialisasi grid default (semua normal / 1)
        self.grid = [[1 for _ in range(cols)] for _ in range(rows)]
        self.start_pos = (rows - 1, 0) # Default pojok kiri bawah
        self.goal_pos = (0, cols - 1)  # Default pojok kanan atas
        
        self.mode = 1  # 1: Normal, 3: Tanjakan, 5: Macet, -1: Tembok, 'S': Start, 'G': Goal
        
        # Frame Kontrol Pilihan
        self.control_frame = tk.Frame(root)
        self.control_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)
        
        tk.Label(self.control_frame, text="Pilih Alat Edit:", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=5)
        
        self.btn_normal = tk.Button(self.control_frame, text="Normal (1)", bg=COLORS[1], command=lambda: self.set_mode(1))
        self.btn_normal.pack(side=tk.LEFT, padx=2)
        
        self.btn_tanjakan = tk.Button(self.control_frame, text="Tanjakan (3)", bg=COLORS[3], fg="white", command=lambda: self.set_mode(3))
        self.btn_tanjakan.pack(side=tk.LEFT, padx=2)
        
        self.btn_macet = tk.Button(self.control_frame, text="Macet (5)", bg=COLORS[5], command=lambda: self.set_mode(5))
        self.btn_macet.pack(side=tk.LEFT, padx=2)
        
        self.btn_tembok = tk.Button(self.control_frame, text="Tembok (-1)", bg=COLORS[-1], fg="white", command=lambda: self.set_mode(-1))
        self.btn_tembok.pack(side=tk.LEFT, padx=2)

        tk.Label(self.control_frame, text=" | ", font=("Arial", 10)).pack(side=tk.LEFT)
        
        self.btn_start = tk.Button(self.control_frame, text="Set Start (S)", bg="lightblue", command=lambda: self.set_mode('S'))
        self.btn_start.pack(side=tk.LEFT, padx=2)
        
        self.btn_goal = tk.Button(self.control_frame, text="Set Goal (G)", bg="lightcoral", command=lambda: self.set_mode('G'))
        self.btn_goal.pack(side=tk.LEFT, padx=2)

        # Canvas untuk Grid
        self.canvas = tk.Canvas(root, width=cols * CELL_SIZE, height=rows * CELL_SIZE, bg="white")
        self.canvas.pack(padx=10, pady=10)
        self.canvas.bind("<Button-1>", self.on_cell_click)
        
        # Tombol Selesai / Submit Konfigurasi
        self.btn_done = tk.Button(root, text="Selesai & Jalankan Simulasi", bg="lightgreen", font=("Arial", 11, "bold"), command=self.finish_config)
        self.btn_done.pack(side=tk.BOTTOM, pady=10)
        
        self.draw_grid()

    def set_mode(self, m):
        self.mode = m

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
                # Ubah terrain, pastikan Start/Goal tidak berubah jadi tembok
                if (r, c) == self.start_pos or (r, c) == self.goal_pos:
                    if self.mode == -1:
                        messagebox.showerror("Error", "Petak Start atau Goal tidak bisa diubah menjadi Tembok!")
                        return
                self.grid[r][c] = self.mode
                
            self.draw_grid()

    def finish_config(self):
        # Validasi akhir
        if self.start_pos == self.goal_pos:
            messagebox.showerror("Error", "Titik Start dan Goal tidak boleh di koordinat yang sama!")
            return
        self.root.destroy()


def get_env():
    """Meminta input ukuran grid dari user, lalu membuka UI interaktif."""
    root = tk.Tk()
    root.withdraw() # Sembunyikan window utama sementara
    
    # Input ukuran grid via Dialog Box (tanpa minwidth & maxwidth)
    cols = simpledialog.askinteger("Input Grid", "Masukkan jumlah Kolom (lebar, misal: 6-10):", initialvalue=8, minvalue=3, maxvalue=20)
    rows = simpledialog.askinteger("Input Grid", "Masukkan jumlah Baris (tinggi, misal: 6-10):", initialvalue=8, minvalue=3, maxvalue=20)
    
    if not cols or not rows:
        cols, rows = 8, 8 # Default aman jika dibatalkan
        
    root.destroy()
    
    # Buka jendela konfigurasi interaktif
    config_root = tk.Tk()
    app = GridConfigurator(config_root, rows, cols)
    config_root.mainloop()
    
    return app.grid, app.start_pos, app.goal_pos


def draw_map(grid, start, goal, optimal_path=[]):
    """Menampilkan hasil akhir rute optimal Dijkstra pada peta 2D."""
    root = tk.Tk()
    root.title("EV Navigation - Hasil Rute Optimal")
    
    rows, cols = len(grid), len(grid[0])
    canvas = tk.Canvas(root, width=cols * CELL_SIZE, height=rows * CELL_SIZE, bg="white")
    canvas.pack(padx=10, pady=10)
    
    path_set = set(optimal_path)

    for r in range(rows):
        for c in range(cols):
            val = grid[r][c]
            color = COLORS.get(val, "#E0E0E0")
                
            x1 = c * CELL_SIZE + PADDING
            y1 = r * CELL_SIZE + PADDING
            x2 = (c + 1) * CELL_SIZE - PADDING
            y2 = (r + 1) * CELL_SIZE - PADDING
            
            canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="black", width=1)
            
            pos = (r, c)
            if pos == start:
                canvas.create_text((x1+x2)/2, (y1+y2)/2, text="S", fill="blue", font=("Arial", 16, "bold"))
            elif pos == goal:
                canvas.create_text((x1+x2)/2, (y1+y2)/2, text="G", fill="red", font=("Arial", 16, "bold"))
            elif pos in path_set:
                canvas.create_text((x1+x2)/2, (y1+y2)/2, text="*", fill="gold", font=("Arial", 22, "bold"))

    root.mainloop()