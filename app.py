from core.logging_config import setup_logging
from ui.main_window import create_main_window


def main() -> None:
    setup_logging()
    app = create_main_window()
    app.mainloop()


if __name__ == "__main__":
    main()
