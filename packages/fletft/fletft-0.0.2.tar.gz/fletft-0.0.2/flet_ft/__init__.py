from .cli import patch_flet_cli
patch_flet_cli()

from .ft_ui_loader import load_ui, get_by_id
from .screen_menager import ScreenManager

__all__ = ["load_ui", "get_by_id", "ScreenManager"]
