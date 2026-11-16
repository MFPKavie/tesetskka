# dfs.py


def run_dfs(grid, start, goal):
    rows, cols = len(grid), len(grid[0])
    stack = [(start[0], start[1], 0)]  # (row, col, accumulated_battery_cost)
    
    visited = {start}
    came_from = {start: None}
    
    # Urutan arah memengaruhi pola penelusuran DFS
    directions = [(-1, 0), (0, 1), (1, 0), (0, -1)]

    while stack:
        r, c, current_cost = stack.pop()

        if (r, c) == goal:
            return current_cost, _build_path(came_from, start, goal), len(visited)

        for dr, dc in directions:
            nr, nc = r + dr, c + dc

            if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] != -1:
                if (nr, nc) not in visited:
                    visited.add((nr, nc))
                    came_from[(nr, nc)] = (r, c)
                    new_cost = current_cost + grid[nr][nc]
                    stack.append((nr, nc, new_cost))

    return float('inf'), [], len(visited)


def _build_path(came_from, start, goal):
    path = [goal]
    node = goal
    while node != start:
        node = came_from[node]
        path.append(node)
    path.reverse()
    return path