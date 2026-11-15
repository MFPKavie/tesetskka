# dijkstra.py
import heapq

def run_dijkstra(grid, start, goal):
    """
    Menjalankan algoritma Dijkstra untuk mencari rute paling hemat baterai.
    """
    rows, cols = len(grid), len(grid[0])
    pq = []
    
    # Priority Queue menyimpan: (total_cost, current_row, current_col, path)
    heapq.heappush(pq, (0, start[0], start[1], [start]))
    
    # Dictionary untuk mencatat cost terendah ke setiap node
    min_costs = {start: 0}
    
    # 4 arah gerakan: Atas, Bawah, Kiri, Kanan
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    
    while pq:
        current_cost, r, c, path = heapq.heappop(pq)
        
        # Jika sampai di tujuan, kembalikan total cost dan jalurnya
        if (r, c) == goal:
            return current_cost, path
            
        # Jika cost saat ini lebih besar dari yang sudah tercatat, lewati
        if current_cost > min_costs.get((r, c), float('inf')):
            continue
            
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            
            # Cek batas grid dan pastikan bukan rintangan (-1)
            if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] != -1:
                weight = grid[nr][nc]
                new_cost = current_cost + weight
                
                # Jika ditemukan jalur yang lebih murah ke tetangga
                if new_cost < min_costs.get((nr, nc), float('inf')):
                    min_costs[(nr, nc)] = new_cost
                    new_path = path + [(nr, nc)]
                    heapq.heappush(pq, (new_cost, nr, nc, new_path))
                    
    return float('inf'), []  # Jika jalur tidak ditemukan
