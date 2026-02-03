from cli import handle_cli
from gui import WallpaperSaverApp


if __name__ == "__main__":
    # Check if CLI commands were used
    if handle_cli():
        exit()  # CLI handled, exit

    # Otherwise launch GUI
    app = WallpaperSaverApp()
    app.mainloop()
