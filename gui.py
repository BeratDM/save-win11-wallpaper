import os
import sys
import subprocess
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from getwallpaper import save_wallpaper
from config import get_default_folder, set_default_folder


class WallpaperSaverApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Save Windows Wallpaper")
        self.geometry("480x200")
        self.resizable(False, False)
        self.last_saved_path = None
        self.default_folder = get_default_folder()

        # Set window icon
        self._set_icon(self)

        self.dest_var = tk.StringVar(value="Default folder")
        options = ["Default folder", "Current directory", "Specify..."]

        # Header frame with label and settings button
        header_frame = ttk.Frame(self)
        header_frame.pack(fill="x", padx=12, pady=(12, 0))
        ttk.Label(header_frame, text="Destination:").pack(side="left")
        ttk.Button(header_frame, text="⚙ Settings", command=self._show_settings).pack(
            side="right"
        )

        # Destination frame
        frame = ttk.Frame(self)
        frame.pack(fill="x", padx=12, pady=(8, 0))

        self.dest_menu = ttk.OptionMenu(
            frame, self.dest_var, options[0], *options, command=self._on_dest_change
        )
        self.dest_menu.pack(side="left")

        self.custom_entry = ttk.Entry(frame)
        self.custom_entry.pack(side="left", fill="x", expand=True, padx=(8, 0))
        self.custom_entry.insert(0, self.default_folder)
        self.custom_entry.configure(state="disabled")

        ttk.Button(frame, text="Browse", command=self._browse).pack(side="left", padx=8)

        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(self, textvariable=self.status_var).pack(
            anchor="w", padx=12, pady=(8, 0)
        )

        self.save_btn = ttk.Button(self, text="Save Wallpaper", command=self._on_save)
        self.save_btn.pack(pady=12)

        self.open_btn = ttk.Button(self, text="Open Folder", command=self._open_folder)

        self._center_main_window()
        self._on_dest_change()

    def _center_main_window(self):
        """Center main window using actual dimensions."""
        self.update_idletasks()
        w = self.winfo_width()
        h = self.winfo_height()
        ws = self.winfo_screenwidth()
        hs = self.winfo_screenheight()
        x = (ws // 2) - (w // 2)
        y = (hs // 2) - (h // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")

    def _center_and_position_window(self, window, width, height):
        """Generic function to center any window with given dimensions."""
        window.update_idletasks()
        ws = window.winfo_screenwidth()
        hs = window.winfo_screenheight()
        x = (ws // 2) - (width // 2)
        y = (hs // 2) - (height // 2)
        window.geometry(f"{width}x{height}+{x}+{y}")

    def _set_icon(self, window):
        try:
            window.iconbitmap("icon.ico")
        except Exception:
            pass

    def _on_dest_change(self, _=None):
        v = self.dest_var.get()
        if v == "Specify...":
            # user will specify; allow edit
            self.custom_entry.configure(state="normal")
        elif v == "Default folder":
            # ensure we can update the entry even if it's currently disabled
            self.custom_entry.configure(state="normal")
            self.custom_entry.delete(0, tk.END)
            self.custom_entry.insert(0, self.default_folder)
            self.custom_entry.configure(state="disabled")
        elif v == "Current directory":
            self.custom_entry.configure(state="normal")
            self.custom_entry.delete(0, tk.END)
            self.custom_entry.insert(0, os.getcwd())
            self.custom_entry.configure(state="disabled")

    def _browse(self):
        path = filedialog.askdirectory()
        if path:
            # when browsing, switch to Specify... and allow editing
            self.dest_var.set("Specify...")
            # run handler to update entry state
            self._on_dest_change()
            self.custom_entry.delete(0, tk.END)
            self.custom_entry.insert(0, path)

    def _on_save(self):
        dest_type = self.dest_var.get()
        if dest_type == "Current directory":
            path = os.getcwd()
        elif dest_type == "Default folder":
            path = self.default_folder
        else:
            path = self.custom_entry.get()

        if not os.path.exists(path):
            messagebox.showerror("Error", "Destination path does not exist")
            return

        self.save_btn.configure(state="disabled")
        self.status_var.set("Saving...")

        def worker():
            success, msg, new_file = save_wallpaper(path)
            self.after(0, lambda: self._on_worker_done(success, msg, new_file, path))

        threading.Thread(target=worker, daemon=True).start()

    def _on_worker_done(self, success, msg, new_file, dest_path):
        self.status_var.set(msg + (f"\n{new_file}" if new_file else ""))
        self.save_btn.configure(state="normal")

        # If save succeeded, show open button for the saved file
        if success and new_file:
            self.last_saved_path = new_file
        else:
            # If the image already exists, save_wallpaper returns a message like
            # "image already exists as: wp-YY-MM-DD-...png". Make the Open button
            # available for that existing file.
            marker = "image already exists as:"
            if isinstance(msg, str) and marker in msg:
                filename = msg.split(marker, 1)[1].strip()
                if filename:
                    existing_path = os.path.join(dest_path, filename)
                    if os.path.exists(existing_path):
                        self.last_saved_path = existing_path

        # show the open button if we have a valid path and it's not visible yet
        if self.last_saved_path and os.path.exists(self.last_saved_path):
            if not self.open_btn.winfo_ismapped():
                self.open_btn.pack(pady=(0, 8))

    def _open_folder(self):
        if self.last_saved_path and os.path.exists(self.last_saved_path):
            try:
                # open Explorer and select the file
                subprocess.run(
                    ["explorer", "/select,", os.path.normpath(self.last_saved_path)]
                )
            except Exception:
                messagebox.showerror("Error", "Unable to open folder")

    def _show_settings(self):
        """Open settings dialog to change default folder."""
        settings_win = tk.Toplevel(self)
        settings_win.title("Settings")
        settings_win.resizable(False, False)
        settings_win.grab_set()

        self._set_icon(settings_win)

        ttk.Label(
            settings_win, text="Default Wallpaper Folder:", font=("", 10, "bold")
        ).pack(anchor="w", padx=12, pady=(12, 0))

        frame = ttk.Frame(settings_win)
        frame.pack(fill="x", padx=12, pady=8)

        entry = ttk.Entry(frame)
        entry.pack(side="left", fill="x", expand=True)
        entry.insert(0, self.default_folder)

        def browse_folder():
            path = filedialog.askdirectory(initialdir=self.default_folder)
            if path:
                entry.delete(0, tk.END)
                entry.insert(0, path)

        ttk.Button(frame, text="Browse", command=browse_folder).pack(
            side="left", padx=(8, 0)
        )

        button_frame = ttk.Frame(settings_win)
        button_frame.pack(pady=12)

        def save_settings():
            new_path = entry.get().strip()
            if not new_path:
                messagebox.showerror("Error", "Path cannot be empty")
                return
            if not os.path.exists(new_path):
                messagebox.showerror("Error", "Path does not exist")
                return
            if set_default_folder(new_path):
                self.default_folder = new_path
                messagebox.showinfo("Success", "Default folder updated!")
                settings_win.destroy()
            else:
                messagebox.showerror("Error", "Failed to save settings")

        ttk.Button(button_frame, text="Save", command=save_settings).pack(
            side="left", padx=4
        )
        ttk.Button(button_frame, text="Cancel", command=settings_win.destroy).pack(
            side="left", padx=4
        )

        # Center settings window using generic function
        self._center_and_position_window(settings_win, 500, 150)
