import json
from http.server import BaseHTTPRequestHandler

from bfs import run_bfs
from dfs import run_dfs
from ucs import run_ucs


ALGORITHMS = {"bfs": run_bfs, "dfs": run_dfs, "ucs": run_ucs}


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if not 0 < length <= 100_000:
                raise ValueError("Request body must be between 1 and 100000 bytes.")

            data = json.loads(self.rfile.read(length))
            if not isinstance(data, dict):
                raise ValueError("Request body must be a JSON object.")
            grid = data["grid"]
            start = tuple(data["start"])
            goal = tuple(data["goal"])
            algorithm = data["algorithm"]
            if not isinstance(algorithm, str):
                raise ValueError("algorithm must be bfs, dfs, or ucs.")
            algorithm = algorithm.lower()

            if (not isinstance(grid, list) or not grid or
                    not all(isinstance(row, list) and row for row in grid) or
                    len({len(row) for row in grid}) != 1 or
                    len(grid) > 100 or len(grid[0]) > 100):
                raise ValueError("grid must be a non-empty rectangular array (max 100x100).")
            if any(not isinstance(cell, int) or cell not in (-1, 1, 3, 5)
                   for row in grid for cell in row):
                raise ValueError("grid cells must be -1, 1, 3, or 5.")
            if algorithm not in ALGORITHMS:
                raise ValueError("algorithm must be bfs, dfs, or ucs.")
            for point in (start, goal):
                if (len(point) != 2 or any(not isinstance(v, int) for v in point) or
                        not 0 <= point[0] < len(grid) or
                        not 0 <= point[1] < len(grid[0]) or
                        grid[point[0]][point[1]] == -1):
                    raise ValueError("start and goal must be passable grid coordinates [row, column].")

            cost, path, visited = ALGORITHMS[algorithm](grid, start, goal)
            result = {"algorithm": algorithm, "cost": cost if path else None,
                      "path": path, "visited": visited}
            self._respond(200, result)
        except (KeyError, TypeError, ValueError, json.JSONDecodeError) as error:
            self._respond(400, {"error": str(error)})

    def _respond(self, status, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
