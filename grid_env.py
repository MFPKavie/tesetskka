
import random
import tkinter as tk
from tkinter import messagebox, simpledialog

# Warna dasar petak. Nilai grid tetap sama agar kompatibel dengan algoritma.
COLORS = {
    1: "#E0E0E0",   # Jalan biasa - biaya 1%
    3: "#4A9DF5",   # Tanjakan - biaya 3%
    5: "#FF9999",   # Macet - biaya 5%
    -1: "#303943",  # Tembok - tidak dapat dilewati
}

CELL_SIZE = 50
PADDING = 4

ALGO_STYLES = {
    "UCS (Uniform Cost Search)": {"color": "#00A94F", "offset": (-6, -6)},
    "BFS (Breadth-First Search)": {"color": "#F06A16", "offset": (-6, 6)},
    "DFS (Depth-First Search)": {"color": "#963DCE", "offset": (6, 6)},
}

MIN_WINDOW_WIDTH = 950
MIN_WINDOW_HEIGHT = 720


def draw_tile(canvas, x1, y1, x2, y2, value, outline="#737D89", width=1):
    """Menggambar satu petak dengan tekstur sesuai jenis jalannya."""
    fill = COLORS.get(value, COLORS[1])

    canvas.create_rectangle(
        x1, y1, x2, y2,
        fill=fill,
        outline=outline,
        width=width,
    )

    tile_w = x2 - x1
    tile_h = y2 - y1

    if value == 3:
        # Tanjakan: bidang biru dengan chevron putih.
        canvas.create_polygon(
            x1 + 1, y2 - tile_h * 0.28,
            x2 - 1, y2 - tile_h * 0.48,
            x2 - 1, y2 - 1,
            x1 + 1, y2 - 1,
            fill="#347FCB",
            outline=""
        )

        center_x = (x1 + x2) / 2
        arrow_y = y1 + tile_h * 0.43
        half_w = tile_w * 0.22
        arrow_h = tile_h * 0.19

        for offset in (0, tile_h * 0.23):
            top = arrow_y - offset

            canvas.create_line(
                center_x - half_w, top + arrow_h,
                center_x, top,
                center_x + half_w, top + arrow_h,
                fill="#FFFFFF",
                width=max(2, int(tile_w * 0.075)),
                capstyle=tk.ROUND,
                joinstyle=tk.ROUND
            )

    elif value == -1:
        # Tembok: pola bata dengan garis nat.
        mortar = "#65717D"
        brick_w = tile_w / 2
        brick_h = tile_h / 4

        for row in range(1, 4):
            y = y1 + row * brick_h
            canvas.create_line(
                x1 + 1, y, x2 - 1, y,
                fill=mortar,
                width=1
            )

        for row in range(4):
            y_top = y1 + row * brick_h
            offset = 0 if row % 2 == 0 else brick_w / 2
            x = x1 + offset

            while x < x2:
                if x > x1:
                    canvas.create_line(
                        x, y_top + 1,
                        x, min(y_top + brick_h, y2 - 1),
                        fill=mortar,
                        width=1
                    )
                x += brick_w


def draw_legend(parent):
    """Panel keterangan jenis petak dan bobot konsumsi baterai."""

    frame = tk.Frame(
        parent,
        bg="#F7F9FC",
        relief=tk.GROOVE,
        borderwidth=1,
        padx=12,
        pady=10
    )

    tk.Label(
        frame,
        text="Keterangan Petak",
        bg="#F7F9FC",
        fg="#172B4D",
        font=("Arial", 12, "bold")
    ).pack(anchor="w", pady=(0, 9))

    entries = [
        (1, "Jalan Biasa", "Bobot: 1% baterai", "Kecepatan normal"),
        (3, "Tanjakan", "Bobot: 3% baterai", "Butuh tenaga lebih"),
        (5, "Macet", "Bobot: 5% baterai", "Kecepatan lebih rendah"),
        (-1, "Tembok", "Tidak dapat dilewati", "Menjadi rintangan"),
    ]

    for value, title, weight, description in entries:
        item = tk.Frame(frame, bg="#F7F9FC")
        item.pack(fill=tk.X, pady=5)

        swatch = tk.Canvas(
            item,
            width=48,
            height=48,
            bg="#F7F9FC",
            highlightthickness=0
        )
        swatch.pack(side=tk.LEFT, padx=(0, 10))

        draw_tile(swatch, 3, 3, 45, 45, value, width=1)

        labels = tk.Frame(item, bg="#F7F9FC")
        labels.pack(side=tk.LEFT, fill=tk.X, expand=True)

        tk.Label(
            labels,
            text=title,
            bg="#F7F9FC",
            fg="#172B4D",
            font=("Arial", 10, "bold")
        ).pack(anchor="w")

        tk.Label(
            labels,
            text=weight,
            bg="#F7F9FC",
            fg="#26364D",
            font=("Arial", 9)
        ).pack(anchor="w")

        tk.Label(
            labels,
            text=description,
            bg="#F7F9FC",
            fg="#667085",
            font=("Arial", 8)
        ).pack(anchor="w")

    return frame


class GridConfigurator:

    def __init__(self, root, rows, cols, initial=None):

        self.root = root
        self.root.title("EV Navigation - Custom Grid Configurator")
        self.root.configure(bg="#F4F6F9")

        self.rows = rows
        self.cols = cols

        self.grid = [[1 for _ in range(cols)] for _ in range(rows)]

        self.start_pos = (rows - 1, 0)
        self.goal_pos = (0, cols - 1)

        self.mode = 1

        if initial is not None:
            prev_grid, prev_start, prev_goal, prev_battery = initial

            self.grid = [row[:] for row in prev_grid]
            self.start_pos = prev_start
            self.goal_pos = prev_goal

        else:
            prev_battery = None

        self.battery_var = tk.StringVar(
            value="" if prev_battery is None else str(prev_battery)
        )

        self.battery = 100

        self.algo_vars = {
            name: tk.BooleanVar(
                value=name in [
                    "UCS (Uniform Cost Search)",
                    "BFS (Breadth-First Search)"
                ]
            )
            for name in ALGO_STYLES
        }

        self.selected_algorithms = []

        # BARIS 1: ALAT EDIT
        self.control_frame = tk.Frame(root, bg="#F4F6F9")
        self.control_frame.pack(
            side=tk.TOP,
            fill=tk.X,
            padx=10,
            pady=(10, 5)
        )

        tk.Label(
            self.control_frame,
            text="Alat Edit:",
            bg="#F4F6F9",
            font=("Arial", 10, "bold")
        ).pack(side=tk.LEFT, padx=5)

        self._tool_button("Jalan Biasa (1)", COLORS[1], "#202B3C", 1)
        self._tool_button("▲ Tanjakan (3)", COLORS[3], "white", 3)
        self._tool_button("🚗 Macet (5)", COLORS[5], "#7D2929", 5)
        self._tool_button("▦ Tembok (-1)", COLORS[-1], "white", -1)

        tk.Label(
            self.control_frame,
            text=" | ",
            bg="#F4F6F9"
        ).pack(side=tk.LEFT, padx=3)

        self._tool_button("Set Start (S)", "#DCEBFF", "#174EA6", "S")
        self._tool_button("Set Goal (G)", "#FFE1E1", "#B42318", "G")

        tk.Label(
            self.control_frame,
            text=" | ",
            bg="#F4F6F9"
        ).pack(side=tk.LEFT, padx=3)

        tk.Button(
            self.control_frame,
            text="Acak Grid",
            bg="#FDE68A",
            command=self.randomize_grid
        ).pack(side=tk.LEFT, padx=2)

        tk.Button(
            self.control_frame,
            text="Reset",
            bg="white",
            command=self.reset_grid
        ).pack(side=tk.LEFT, padx=2)

        tk.Label(
            self.control_frame,
            text="Tembok %",
            bg="#F4F6F9"
        ).pack(side=tk.LEFT, padx=(8, 2))

        self.wall_ratio_var = tk.IntVar(value=20)

        tk.Spinbox(
            self.control_frame,
            from_=0,
            to=60,
            width=4,
            textvariable=self.wall_ratio_var
        ).pack(side=tk.LEFT, padx=2)

        # BARIS 2: PILIHAN ALGORITMA
        self.algo_frame = tk.Frame(
            root,
            relief=tk.GROOVE,
            borderwidth=1,
            padx=8,
            pady=6,
            bg="#FFFFFF"
        )

        self.algo_frame.pack(
            side=tk.TOP,
            fill=tk.X,
            padx=10,
            pady=5
        )

        tk.Label(
            self.algo_frame,
            text="Pilih Algoritma (Min. 1):",
            font=("Arial", 10, "bold"),
            bg="#FFFFFF"
        ).pack(side=tk.LEFT, padx=5)

        for name, style in ALGO_STYLES.items():

            cb = tk.Checkbutton(
                self.algo_frame,
                text=name,
                variable=self.algo_vars[name],
                fg=style["color"],
                activeforeground=style["color"],
                font=("Arial", 9, "bold"),
                bg="#FFFFFF",
                activebackground="#FFFFFF"
            )

            cb.pack(side=tk.LEFT, padx=8)

        # BARIS 3: BATERAI
        self.battery_frame = tk.Frame(
            root,
            relief=tk.GROOVE,
            borderwidth=1,
            padx=8,
            pady=6,
            bg="#FFFFFF"
        )

        self.battery_frame.pack(
            side=tk.TOP,
            fill=tk.X,
            padx=10,
            pady=5
        )

        tk.Label(
            self.battery_frame,
            text="Baterai Awal % (penuh = 100):",
            font=("Arial", 10, "bold"),
            bg="#FFFFFF"
        ).pack(side=tk.LEFT, padx=5)

        tk.Entry(
            self.battery_frame,
            textvariable=self.battery_var,
            width=6,
            justify="center"
        ).pack(side=tk.LEFT, padx=5)

        # GRID DAN LEGENDA
        self.map_frame = tk.Frame(root, bg="#F4F6F9")

        self.map_frame.pack(
            side=tk.TOP,
            padx=12,
            pady=10
        )

        canvas_width = cols * CELL_SIZE
        canvas_height = rows * CELL_SIZE

        self.canvas = tk.Canvas(
            self.map_frame,
            width=canvas_width,
            height=canvas_height,
            bg="white",
            highlightthickness=0
        )

        self.canvas.pack(
            side=tk.LEFT,
            padx=(0, 16),
            anchor="n"
        )

        self.canvas.bind("<Button-1>", self.on_cell_click)

        self.legend_frame = draw_legend(self.map_frame)

        self.legend_frame.pack(
            side=tk.LEFT,
            fill=tk.Y,
            anchor="n"
        )

        # TOMBOL START SIMULASI
        self.btn_done = tk.Button(
            root,
            text="▶  Start Simulasi",
            bg="#25A65A",
            fg="white",
            activebackground="#1D8548",
            activeforeground="white",
            font=("Arial", 11, "bold"),
            padx=18,
            pady=6,
            command=self.finish_config
        )

        self.btn_done.pack(side=tk.BOTTOM, pady=10)

        self._setup_window_size()
        self.draw_grid()

    def _tool_button(self, text, bg, fg, mode):

        tk.Button(
            self.control_frame,
            text=text,
            bg=bg,
            fg=fg,
            activebackground=bg,
            activeforeground=fg,
            font=("Arial", 9, "bold"),
            relief=tk.RAISED,
            padx=5,
            pady=3,
            command=lambda m=mode: self.set_mode(m)
        ).pack(side=tk.LEFT, padx=2)

    def _setup_window_size(self):

        self.root.update_idletasks()

        width = max(
            self.root.winfo_reqwidth(),
            MIN_WINDOW_WIDTH
        )

        height = max(
            self.root.winfo_reqheight(),
            MIN_WINDOW_HEIGHT
        )

        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()

        width = min(width, screen_w - 40)
        height = min(height, screen_h - 80)

        x = max((screen_w - width) // 2, 0)
        y = max((screen_h - height) // 3, 0)

        self.root.minsize(
            min(MIN_WINDOW_WIDTH, screen_w - 40),
            min(MIN_WINDOW_HEIGHT, screen_h - 80)
        )

        self.root.geometry(
            f"{width}x{height}+{x}+{y}"
        )

    def set_mode(self, mode):
        self.mode = mode

    def reset_grid(self):

        self.grid = [
            [1 for _ in range(self.cols)]
            for _ in range(self.rows)
        ]

        self.draw_grid()

    def randomize_grid(self, max_attempts=30):

        wall_ratio = max(
            0,
            min(self.wall_ratio_var.get(), 60)
        ) / 100.0

        protected = {
            self.start_pos,
            self.goal_pos
        }

        terrain_pool = [1, 1, 1, 3, 5]

        new_grid = self.grid

        for _ in range(max_attempts):

            new_grid = [
                [1 for _ in range(self.cols)]
                for _ in range(self.rows)
            ]

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

            for dr, dc in (
                (-1, 0),
                (1, 0),
                (0, -1),
                (0, 1)
            ):

                nr = r + dr
                nc = c + dc

                if (
                    0 <= nr < self.rows
                    and 0 <= nc < self.cols
                    and (nr, nc) not in seen
                    and grid[nr][nc] != -1
                ):

                    seen.add((nr, nc))
                    queue.append((nr, nc))

        return False

    def draw_grid(self):

        self.canvas.delete("all")

        for r in range(self.rows):
            for c in range(self.cols):

                value = self.grid[r][c]

                x1 = c * CELL_SIZE + PADDING
                y1 = r * CELL_SIZE + PADDING
                x2 = (c + 1) * CELL_SIZE - PADDING
                y2 = (r + 1) * CELL_SIZE - PADDING

                draw_tile(
                    self.canvas,
                    x1, y1, x2, y2,
                    value
                )

                pos = (r, c)

                if pos == self.start_pos:

                    self.canvas.create_oval(
                        (x1+x2)/2-14,
                        (y1+y2)/2-14,
                        (x1+x2)/2+14,
                        (y1+y2)/2+14,
                        fill="#FFFFFF",
                        outline="#1769E0",
                        width=2
                    )

                    self.canvas.create_text(
                        (x1+x2)/2,
                        (y1+y2)/2,
                        text="S",
                        fill="#1769E0",
                        font=("Arial", 15, "bold")
                    )

                elif pos == self.goal_pos:

                    self.canvas.create_oval(
                        (x1+x2)/2-14,
                        (y1+y2)/2-14,
                        (x1+x2)/2+14,
                        (y1+y2)/2+14,
                        fill="#FFFFFF",
                        outline="#D92D20",
                        width=2
                    )

                    self.canvas.create_text(
                        (x1+x2)/2,
                        (y1+y2)/2,
                        text="G",
                        fill="#D92D20",
                        font=("Arial", 15, "bold")
                    )

    def on_cell_click(self, event):

        c = event.x // CELL_SIZE
        r = event.y // CELL_SIZE

        if 0 <= r < self.rows and 0 <= c < self.cols:

            if self.mode == "S":

                if self.grid[r][c] == -1:
                    messagebox.showerror(
                        "Error",
                        "Titik Start tidak boleh berada di atas Tembok!"
                    )
                    return

                self.start_pos = (r, c)

            elif self.mode == "G":

                if self.grid[r][c] == -1:
                    messagebox.showerror(
                        "Error",
                        "Titik Goal tidak boleh berada di atas Tembok!"
                    )
                    return

                self.goal_pos = (r, c)

            else:

                if (
                    (r, c) in (self.start_pos, self.goal_pos)
                    and self.mode == -1
                ):

                    messagebox.showerror(
                        "Error",
                        "Petak Start atau Goal tidak bisa diubah menjadi Tembok!"
                    )
                    return

                self.grid[r][c] = self.mode

            self.draw_grid()

    def finish_config(self):

        if self.start_pos == self.goal_pos:

            messagebox.showerror(
                "Error",
                "Titik Start dan Goal tidak boleh di koordinat yang sama!"
            )
            return

        chosen = [
            name
            for name, var in self.algo_vars.items()
            if var.get()
        ]

        if not chosen:

            messagebox.showwarning(
                "Peringatan",
                "Pilih minimal satu algoritma sebelum memulai simulasi!"
            )
            return

        raw = self.battery_var.get().strip()

        if raw == "":
            battery = 100

        else:

            try:
                battery = int(raw)

            except ValueError:

                messagebox.showerror(
                    "Error",
                    "Baterai awal harus berupa angka bulat!"
                )
                return

            if not 1 <= battery <= 100:

                messagebox.showerror(
                    "Error",
                    "Baterai awal harus antara 1 sampai 100!"
                )
                return

        self.battery = battery
        self.selected_algorithms = chosen

        self.root.destroy()


def get_env(initial=None):

    """Membuka konfigurator grid."""

    if initial is None:

        root = tk.Tk()
        root.withdraw()

        cols = simpledialog.askinteger(
            "Input Grid",
            "Masukkan jumlah Kolom (lebar, misal: 6-12):",
            initialvalue=8,
            minvalue=3,
            maxvalue=20
        )

        rows = simpledialog.askinteger(
            "Input Grid",
            "Masukkan jumlah Baris (tinggi, misal: 6-12):",
            initialvalue=8,
            minvalue=3,
            maxvalue=20
        )

        if not cols or not rows:
            cols, rows = 8, 8

        root.destroy()

    else:

        rows = len(initial[0])
        cols = len(initial[0][0])

    config_root = tk.Tk()

    app = GridConfigurator(
        config_root,
        rows,
        cols,
        initial
    )

    config_root.mainloop()

    return (
        app.grid,
        app.start_pos,
        app.goal_pos,
        app.selected_algorithms,
        app.battery
    )


def draw_multi_results(grid, start, goal, results):

    """Menampilkan rute algoritma terpilih di atas grid."""

    action = {"value": None}

    def choose(value):
        action["value"] = value
        root.destroy()

    root = tk.Tk()

    root.title("EV Navigation - Hasil Perbandingan Rute")
    root.configure(bg="#F4F6F9")

    main_frame = tk.Frame(
        root,
        bg="#F4F6F9"
    )

    main_frame.pack(padx=15, pady=15)

    rows = len(grid)
    cols = len(grid[0])

    canvas = tk.Canvas(
        main_frame,
        width=cols * CELL_SIZE,
        height=rows * CELL_SIZE,
        bg="white",
        highlightthickness=0
    )

    canvas.pack(
        side=tk.LEFT,
        padx=(0, 15),
        anchor="n"
    )

    # GRID DASAR
    for r in range(rows):
        for c in range(cols):

            value = grid[r][c]

            x1 = c * CELL_SIZE + PADDING
            y1 = r * CELL_SIZE + PADDING
            x2 = (c + 1) * CELL_SIZE - PADDING
            y2 = (r + 1) * CELL_SIZE - PADDING

            draw_tile(
                canvas,
                x1, y1, x2, y2,
                value
            )

    # GAMBAR RUTE ALGORITMA
    for res in results:

        path = res["path"]

        if not path:
            continue

        style = ALGO_STYLES[res["name"]]

        line_color = style["color"]
        ox, oy = style["offset"]

        coords = []

        for r, c in path:

            cx = c * CELL_SIZE + (CELL_SIZE / 2) + ox
            cy = r * CELL_SIZE + (CELL_SIZE / 2) + oy

            coords.extend([cx, cy])

            canvas.create_oval(
                cx - 3.5,
                cy - 3.5,
                cx + 3.5,
                cy + 3.5,
                fill=line_color,
                outline=""
            )

        if len(coords) >= 4:

            canvas.create_line(
                *coords,
                fill=line_color,
                width=3,
                smooth=False
            )

    # LABEL START DAN GOAL
    for pos, label, color in [
        (start, "S", "#1769E0"),
        (goal, "G", "#D92D20")
    ]:

        r, c = pos

        cx = c * CELL_SIZE + CELL_SIZE / 2
        cy = r * CELL_SIZE + CELL_SIZE / 2

        canvas.create_oval(
            cx - 14,
            cy - 14,
            cx + 14,
            cy + 14,
            fill="white",
            outline=color,
            width=2
        )

        canvas.create_text(
            cx,
            cy,
            text=label,
            fill=color,
            font=("Arial", 14, "bold")
        )

    # PANEL HASIL PERBANDINGAN
    legend_frame = tk.Frame(
        main_frame,
        relief=tk.RIDGE,
        borderwidth=1,
        padx=12,
        pady=12,
        bg="#FFFFFF"
    )

    legend_frame.pack(
        side=tk.RIGHT,
        fill=tk.Y,
        anchor="n"
    )

    tk.Label(
        legend_frame,
        text="Hasil & Perbandingan Algoritma",
        font=("Arial", 12, "bold"),
        bg="#FFFFFF"
    ).pack(anchor="w", pady=(0, 10))

    if not any(res["path"] for res in results):

        tk.Label(
            legend_frame,
            text="Tidak ada rute yang dapat mencapai tujuan!",
            fg="white",
            bg="#D32F2F",
            font=("Arial", 10, "bold"),
            justify=tk.LEFT,
            padx=10,
            pady=8
        ).pack(fill=tk.X, pady=(0, 10))

    for res in results:

        name = res["name"]
        color = ALGO_STYLES[name]["color"]

        card = tk.Frame(
            legend_frame,
            pady=6,
            bg="#FFFFFF"
        )

        card.pack(fill=tk.X, anchor="w")

        header = tk.Frame(
            card,
            bg="#FFFFFF"
        )

        header.pack(anchor="w")

        tk.Label(
            header,
            text="●",
            fg=color,
            bg="#FFFFFF",
            font=("Arial", 12, "bold")
        ).pack(side=tk.LEFT)

        tk.Label(
            header,
            text=f" {name}",
            bg="#FFFFFF",
            font=("Arial", 10, "bold")
        ).pack(side=tk.LEFT)

        if res["path"]:

            detail = (
                f"   • Baterai Awal      : {res['battery']}%\n"
                f"   • Konsumsi Baterai  : {res['cost']}%\n"
                f"   • Sisa Baterai      : {res['remaining']}%\n"
                f"   • Panjang Rute      : {len(res['path'])} petak\n"
                f"   • Node Dieksplorasi : {res['visited']} node\n"
                f"   • Waktu             : {res['time_ms']:.2f} ms"
            )

        else:

            detail = "   • Status: Jalur tidak ditemukan"

        tk.Label(
            card,
            text=detail,
            justify=tk.LEFT,
            font=("Consolas", 9),
            bg="#FFFFFF"
        ).pack(anchor="w")

        tk.Frame(
            legend_frame,
            height=1,
            bg="#D9DEE7"
        ).pack(fill=tk.X, pady=4)

        if res["path"] and not res["enough"]:

            tk.Label(
                card,
                text="⚠ Baterai Tidak Cukup! (Sisa 0%)",
                fg="white",
                bg="#D32F2F",
                font=("Arial", 9, "bold"),
                padx=8,
                pady=3
            ).pack(anchor="w", pady=(4, 0))

    # TOMBOL NAVIGASI
    btn_frame = tk.Frame(
        legend_frame,
        bg="#FFFFFF"
    )

    btn_frame.pack(
        side=tk.BOTTOM,
        fill=tk.X,
        pady=(10, 0)
    )

    tk.Button(
        btn_frame,
        text="🔁 Percobaan Baru (Peta Sama)",
        bg="#25A65A",
        fg="white",
        font=("Arial", 10, "bold"),
        command=lambda: choose("same")
    ).pack(fill=tk.X, pady=2)

    tk.Button(
        btn_frame,
        text="🗺 Percobaan Baru (Peta Baru)",
        bg="#2478D4",
        fg="white",
        font=("Arial", 10, "bold"),
        command=lambda: choose("new")
    ).pack(fill=tk.X, pady=2)

    tk.Button(
        btn_frame,
        text="Keluar",
        bg="#D92D20",
        fg="white",
        font=("Arial", 10, "bold"),
        command=lambda: choose(None)
    ).pack(fill=tk.X, pady=2)

    # ATUR UKURAN WINDOW
    root.update_idletasks()

    width = root.winfo_reqwidth() + 40
    height = max(root.winfo_reqheight() + 40, 480)

    screen_w = root.winfo_screenwidth()
    screen_h = root.winfo_screenheight()

    root.geometry(
        f"{min(width, screen_w - 40)}x{min(height, screen_h - 80)}"
    )

    root.mainloop()

    return action["value"]
