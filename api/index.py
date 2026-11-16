"""Vercel HTTP adapter for the repository's existing route-search algorithms."""

import json
from http.server import BaseHTTPRequestHandler

from bfs import run_bfs
from dfs import run_dfs
from ucs import run_ucs


ALGORITHMS = {"bfs": run_bfs, "dfs": run_dfs, "ucs": run_ucs}
MAX_BODY_BYTES = 100_000
MAX_GRID_SIDE = 100


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self._json(200, {
            "message": "POST a grid, start, goal, and algorithm to find a route.",
            "algorithms": list(ALGORITHMS),
            "example": {
                "grid": [[1, 1], [1, 1]],
                "start": [0, 0],
                "goal": [1, 1],
                "algorithm": "ucs",
            },
        })

    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if not 0 < length <= MAX_BODY_BYTES:
                raise ValueError(f"Request body must be between 1 and {MAX_BODY_BYTES} bytes.")
            data = json.loads(self.rfile.read(length))
            if not isinstance(data, dict):
                raise ValueError("Request body must be a JSON object.")

            grid = data.get("grid")
            start = self._point(data.get("start"), "start")
            goal = self._point(data.get("goal"), "goal")
            algorithm = data.get("algorithm")
            if not isinstance(algorithm, str) or algorithm.lower() not in ALGORITHMS:
                raise ValueError("algorithm must be bfs, dfs, or ucs.")
            algorithm = algorithm.lower()

            if (not isinstance(grid, list) or not grid or
                    len(grid) > MAX_GRID_SIDE or
                    not all(isinstance(row, list) and row for row in grid) or
                    len({len(row) for row in grid}) != 1 or
                    len(grid[0]) > MAX_GRID_SIDE):
                raise ValueError(f"grid must be a non-empty rectangular array (max {MAX_GRID_SIDE}x{MAX_GRID_SIDE}).")
            if any(type(cell) is not int or cell not in (-1, 1, 3, 5)
                   for row in grid for cell in row):
                raise ValueError("grid cells must be -1, 1, 3, or 5.")
            for name, point in (("start", start), ("goal", goal)):
                row, col = point
                if not (0 <= row < len(grid) and 0 <= col < len(grid[0])):
                    raise ValueError(f"{name} must be within the grid.")
                if grid[row][col] == -1:
                    raise ValueError(f"{name} must be on a passable cell.")

            cost, path, visited = ALGORITHMS[algorithm](grid, start, goal)
            self._json(200, {
                "algorithm": algorithm,
                "cost": cost if path else None,
                "path": path,
                "visited": visited,
            })
        except (KeyError, TypeError, ValueError, json.JSONDecodeError) as error:
            self._json(400, {"error": str(error)})

    @staticmethod
    def _point(value, name):
        if (not isinstance(value, list) or len(value) != 2 or
                any(type(coordinate) is not int for coordinate in value)):
            raise ValueError(f"{name} must be [row, column].")
        return tuple(value)

    def _json(self, status, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
