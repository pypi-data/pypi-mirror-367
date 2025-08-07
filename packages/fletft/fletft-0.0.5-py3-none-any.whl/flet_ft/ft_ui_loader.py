import yaml
import flet

# Rejestr wszystkich kontrolek po id
_id_registry = {}


def get_by_id(cid):
    """Zwraca komponent po jego id (lub None)."""
    return _id_registry.get(cid)

def load_ui_from_file(ui_file, context_globals=None):
    with open(ui_file, "r", encoding="utf-8") as f:
        yaml_data = f.read()
    return load_ui(yaml_data, context_globals=context_globals)


def load_ui(yaml_data, context_globals=None):
    data = yaml.safe_load(yaml_data)
    controls = []

    # lista znanych komponentów Flet
    known_components = {name: getattr(flet, name) for name in dir(flet) if isinstance(getattr(flet, name), type)}

    def get_handler(name):
        if context_globals and name in context_globals:
            return context_globals[name]
        return None

    def parse_node(node):
        """Rekurencyjnie parsuje YAML do komponentów lub wartości."""
        if isinstance(node, dict):
            # jeśli dict ma dokładnie jeden klucz i jest to nazwa komponentu Flet
            if len(node) == 1:
                name, props = next(iter(node.items()))
                if name in known_components:
                    return create_component(name, props)
            # w przeciwnym razie to zwykły słownik atrybutów
            return {k: parse_node(v) for k, v in node.items()}
        elif isinstance(node, list):
            return [parse_node(item) for item in node]
        else:
            return node  # wartość prymitywna

    def create_component(name, props):
        cls = getattr(flet, name, None)
        if cls is None:
            raise ValueError(f"Nieznany komponent: {name}")

        init_args = {}
        comp_id = None

        for key, value in props.items():
            if key == "controls" and isinstance(value, list):
                init_args["controls"] = [parse_node(child) for child in value]
            elif key == "content" and isinstance(value, dict):
                init_args["content"] = parse_node(value)
            elif key == "style" and isinstance(value, dict):
                # Specjalna obsługa stylu przycisku
                init_args["style"] = flet.ButtonStyle(
                    **{k: parse_node(v) for k, v in value.items()}
                )
            elif isinstance(value, dict):
                init_args[key] = parse_node(value)
            elif key.startswith("on_") and isinstance(value, str):
                handler = get_handler(value)
                init_args[key] = handler if callable(handler) else None
            elif key == "id":
                comp_id = value
            else:
                init_args[key] = value

        comp = cls(**init_args)

        if comp_id:
            _id_registry[comp_id] = comp

        return comp

    # główne wejście — zakładam, że w YAML jest "page" z "controls"
    if "page" in data and "controls" in data["page"]:
        for item in data["page"]["controls"]:
            controls.append(parse_node(item))

    return controls
