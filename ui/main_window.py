import ttkbootstrap as ttk

from ui.build_panel import BuildPanel
from ui.config_panel import ConfigPanel
from ui.status_panel import StatusPanel


def create_main_window() -> ttk.Window:
    app = ttk.Window(
        title="Second Life Viewer Builder",
        themename="darkly",
        size=(1100, 1400),
    )

    config_panel = ConfigPanel(app)
    config_panel.pack(fill="x", padx=10, pady=10)

    status_panel = StatusPanel(app)
    status_panel.pack(fill="both", expand=True, padx=10, pady=10)

    build_panel = BuildPanel(app, config_panel, status_panel)
    build_panel.pack(fill="x", padx=10, pady=10)

    return app
