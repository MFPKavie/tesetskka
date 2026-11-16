import heapq


def run_ucs(grid, start, goal):
    """
    Menjalankan algoritma Uniform Cost Search (UCS) untuk mencari rute
    paling hemat baterai.
    """
    rows, cols = len(grid), len(grid[0])

    # Priority Queue
    pq = [(0, start[0], start[1])]

    # Biaya terendah yang diketahui menuju setiap node
    min_costs = {start: 0}
    came_from: dict[tuple, tuple | None] = {start: None}

    # Directions
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    while pq:
        current_cost, r, c = heapq.heappop(pq)

        # Jika sampai di tujuan, rekonstruksi jalur lalu kembalikan
        if (r, c) == goal:
            return current_cost, _build_path(came_from, start, goal), len(min_costs)
        
        # Abaikan entri basi di antrean
        if current_cost > min_costs.get((r, c), float('inf')):
            continue

        for dr, dc in directions:
            nr, nc = r + dr, c + dc

            # Cek batas grid dan pastikan bukan rintangan (-1)
            if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] != -1:
                new_cost = current_cost + grid[nr][nc]

                # Jika ditemukan jalur yang lebih murah ke tetangga
                if new_cost < min_costs.get((nr, nc), float('inf')):
                    min_costs[(nr, nc)] = new_cost
                    came_from[(nr, nc)] = (r, c)
                    heapq.heappush(pq, (new_cost, nr, nc))

    return float('inf'), [], len(min_costs)  # Jika jalur tidak ditemukan  # Jika jalur tidak ditemukan


def _build_path(came_from, start, goal):
    """Merekonstruksi jalur dari start ke goal memakai kamus came_from."""
    path = [goal]
    node = goal
    while node != start:
        node = came_from[node]
        path.append(node)
    path.reverse()
    return path
