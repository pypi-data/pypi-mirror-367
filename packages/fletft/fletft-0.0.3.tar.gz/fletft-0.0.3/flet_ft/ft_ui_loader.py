import yaml
import flet

# Rejestr wszystkich kontrolek po id
_id_registry = {}

def get_by_id(cid):
    """Zwraca komponent po jego id (lub None)."""
    return _id_registry.get(cid)

def load_ui(yaml_data, context_globals=None):
    data = yaml.safe_load(yaml_data)
    controls = []

    def get_handler(name):
        if context_globals and name in context_globals:
            return context_globals[name]
        return None

    def create_component(name, props):
        cls = getattr(flet, name, None)
        if cls is None:
            raise ValueError(f"Nieznany komponent: {name}")

        init_args = {}
        comp_id = None

        for key, value in props.items():
            if key == "controls" and isinstance(value, list):
                init_args["controls"] = [parse_node(child) for child in value]
            elif key.startswith("on_") and isinstance(value, str):
                handler = get_handler(value)
                init_args[key] = handler if callable(handler) else None
            elif key == "id":
                comp_id = value
            else:
                init_args[key] = value

        comp = cls(**init_args)

        if comp_id:  # zapisujemy tylko jeśli id jest ustawione
            _id_registry[comp_id] = comp

        return comp

    def parse_node(node):
        if isinstance(node, dict):
            for name, props in node.items():
                if not isinstance(props, dict):
                    raise ValueError(f"Błąd składni komponentu: {name}")
                return create_component(name, props)
        raise ValueError("Nieprawidłowy węzeł YAML")

    if "page" in data and "controls" in data["page"]:
        for item in data["page"]["controls"]:
            controls.append(parse_node(item))

    return controls
