import flet as ft


class ScreenManager:
    def __init__(self, page: ft.Page):
        self.page = page
        self.screens = {}  # dict nazwa -> (ft.View, route)
        self._current = None
        self.page.on_route_change = self._on_route_change

    def add_screen(self, name: str, view: ft.Control, route: str = None):
        # Jeśli route nie podano, generujemy z nazwy: "screen1" -> "/screen1"
        if route is None:
            route = f"/{name}"
        # Jeśli view to nie View, zamieniamy na View z automatycznym route
        if not isinstance(view, ft.View):
            view = ft.View(route, [view])
        else:
            # Nadpisujemy route wewnątrz View
            view.route = route
        self.screens[name] = (view, route)

    def set_current(self, name: str):
        if name not in self.screens:
            raise ValueError(f"Screen '{name}' not found")
        view, route = self.screens[name]
        self._current = name
        self.page.views.clear()
        self.page.views.append(view)
        self.page.go(route)
        self.page.update()

    def _on_route_change(self, route):
        route = route or "/"
        # Szukamy ekranu z takim route
        for name, (view, r) in self.screens.items():
            if r == route and name != self._current:
                self._current = name
                self.page.views.clear()
                self.page.views.append(view)
                self.page.update()
                break
