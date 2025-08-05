from typing import Dict, Callable, Tuple

class Router:
    def __init__(self):
        self.routes: Dict[Tuple[str, str], Callable] = {}

    def add_route(self, path: str, method: str, handler: Callable):
        self.routes[(path, method)] = handler

    def get_handler(self, path: str, method: str) -> Callable:
        return self.routes.get((path, method))