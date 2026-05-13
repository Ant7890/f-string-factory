"""
3D Turntable Viewer — main file.

The idea came from Sketchfab, I wanted to recreate that drag-to-rotate
3D preview in Python. PyOpenGL turned out to be too much; shaders,
matrix math, depth buffers — just to render a cube. So I went a different
direction: pre-render the object from every angle in Blender, store all
the frames in a GIF, and display the right one based on user input.

The Blender render script (AI-assisted) sets up a camera that orbits the
object and captures 512 frames — 32 horizontal angles by 16 vertical angles.
That gives us a flat list we can index into with a formula:

    frame_index = elevation * 32 + azimuth
                    Row * Width + Column

The renderer sweeps all 32 azimuths across each elevation row before moving
to the next, so the formula reads them back in the same order they were written.
Seeking to any frame instantly fakes the 3D rotation effect.

AI was also used to understand threading, io, and PIL in the loader, winfo things for tkinter specifically, and for
specific bug fixes encountered during development.

This file contains the main menu, the loader dialog, and the viewer.
The about page lives in about.py and is imported here.
"""

import tkinter as tk
from tkinter import ttk
import requests
import threading #Loaded so the program didn't freeze when requesting files.
import io #Used to manage the GIFs into memory.
from PIL import Image, ImageTk
from about import About

# The models pull straight from my GitHub repository.
MODELS = {
    "Gameboy": "https://raw.githubusercontent.com/Ant7890/f-string-factory/main/code/python/FinalProject_Assets/Gameboy.gif",
    "Monkey": "https://raw.githubusercontent.com/Ant7890/f-string-factory/main/code/python/FinalProject_Assets/Monkey.gif",
    "Python Logo": "https://raw.githubusercontent.com/Ant7890/f-string-factory/main/code/python/FinalProject_Assets/PythonLogo.gif",
    "Alfa Romeo": "https://raw.githubusercontent.com/Ant7890/f-string-factory/main/code/python/FinalProject_Assets/AlfaRomeo.gif",
}

azimuth_steps = int(32)
elevation_steps = int(16)
frame_size = int(400)
default_az = int(16)
default_el = int(8)
spin_el = int(8)
spin_ms = int(60)

root = tk.Tk()
root.title("3D Turntable Viewer")
root.geometry("600x600")
root.resizable(False, False)
root.configure(bg="#1a1a1a")

menubar = tk.Menu(root)
root.configure(menu=menubar)

filemenu = tk.Menu(
    menubar, tearoff=0,
    bg="#222222", fg="#aaaaaa",
    activebackground="#333333", activeforeground="#ffffff",
)
menubar.add_cascade(label="Options", menu=filemenu) # I added this just for fun, everything is a placeholder except for Quit.

filemenu.add_command(label="Preferences", command=lambda: None)
filemenu.add_command(label="Import Model...", command=lambda: None)
filemenu.add_command(label="Export Frames...", command=lambda: None)
filemenu.add_separator()
filemenu.add_command(label="Quit", command=root.destroy)

class Loader(tk.Toplevel): # This is the popup for the loader, it brings up a small dialog box, on the first load, it uses a combobox for user input
    def __init__(self, parent, models, initial_name, on_complete, show_combo=True):
        super().__init__(parent)
        self.title("Load Model")
        self.resizable(False, False)
        self.configure(bg="#1a1a1a")
        self.grab_set() #Sets focus on the loader dialog box; without it, you could create multiple loader dialogs.

        self._models = models
        self._on_complete = on_complete
        self._cancelled = False
        self._loading = False
        self._show_combo = show_combo
        self._selected = tk.StringVar(value=initial_name)

        h = 220 if show_combo else 180 #On the second model load, the extra space is unneeded with the combobox missing.
        self.geometry(f"320x{h}")

        self.update_idletasks() #Forces layout, for centering pop up in the parent frame.
        px = parent.winfo_rootx() + (parent.winfo_width() // 2) - 160
        py = parent.winfo_rooty() + (parent.winfo_height() // 2) - (h // 2)
        self.geometry(f"320x{h}+{px}+{py}")

        self._build_ui()
        self.protocol("WM_DELETE_WINDOW", self._cancel)

    def _build_ui(self): #Builds the loader dialog, combobox shown on the first load only.
        tk.Label(
            self, text="Load Model",
            font=("Arial", 12, "bold"),
            bg="#1a1a1a", fg="#b0bf1a",
        ).pack(pady=(16, 8))

        if self._show_combo:
            row = tk.Frame(self, bg="#1a1a1a")
            row.pack(pady=(0, 8))
            tk.Label(
                row, text="Model:",
                font=("Arial", 9), bg="#1a1a1a", fg="#aaaaaa",
            ).pack(side="left", padx=(0, 8))
            self._combo = ttk.Combobox( #Initial way for a user to select a model to download.
                row,
                textvariable=self._selected,
                values=list(self._models.keys()),
                state="readonly",
                width=16,
                font=("Arial", 10),
            )
            self._combo.pack(side="left")
        else: #On the second load, the combobox is not needed, so the radio-selected model is shown to be downloaded directly.
            tk.Label(
                self, text=self._selected.get(),
                font=("Arial", 11, "bold"),
                bg="#1a1a1a", fg="#ffffff",
            ).pack(pady=(0, 8))

        self._status_var = tk.StringVar(value="Ready.")
        tk.Label(
            self, textvariable=self._status_var,
            font=("Arial", 9), bg="#1a1a1a", fg="#aaaaaa",
        ).pack()

        self._progress = ttk.Progressbar(
            self, orient="horizontal", length=260, mode="determinate",
        )
        self._progress.pack(pady=8, padx=20)

        btn_row = tk.Frame(self, bg="#1a1a1a")
        btn_row.pack()

        self._load_btn = tk.Button(btn_row, text="Load", command=self._on_load_clicked, font=("Arial", 10, "bold"),
        bg="#b0bf1a", fg="white", activebackground="#8a9a10", relief="flat", cursor="hand2", bd=0, padx=14, pady=6)
        self._load_btn.pack(side="left", padx=8)

        tk.Button(
            btn_row, text="Cancel",
            command=self._cancel,
            font=("Arial", 9),
            bg="#1a1a1a", fg="#ff4444",
            activeforeground="#ff0000",
            relief="flat", cursor="hand2", bd=0, padx=14, pady=6,
        ).pack(side="left", padx=8)

    def _set_status(self, text):
        if self.winfo_exists():
            self.after(0, lambda: self._status_var.set(text))

    def _set_progress(self, val):
        if self.winfo_exists():
            self.after(0, lambda: self._progress.configure(value=val))

    def _on_load_clicked(self):
        if self._loading:
            return
        self._loading = True
        if self._show_combo:
            self._combo.configure(state="disabled")
        self._load_btn.configure(state="disabled", bg="#555555")
        threading.Thread(target=self._load, daemon=True).start() #daemon=True ensures the thread is killed automatically when the main window closes, preventing the program from hanging

    def _load(self): #A lot of this code, I used AI to understand, as IO and PIL each have significant documentation and different ways to do things.
        try:
            name = self._selected.get()
            url = self._models[name] #Look up the URL from the models dict using the selected name

            self._set_status("Connecting...")
            r = requests.get(url, stream=True, timeout=20) #Opens a streaming connection so the file can be downloaded in chunks, enabling progress tracking via content-length header
            r.raise_for_status() #Raises an exception if the download fails e.g. 404

            total = int(r.headers.get("content-length", 0)) #Get total file size in bytes from the response header, 0 if unavailable
            data = bytearray()
            self._set_status("Downloading...")

            for chunk in r.iter_content(chunk_size=8192): #Download in 8192 byte chunks to give measurable progress
                if self._cancelled:
                    return
                data.extend(chunk) #Append each chunk to the byte array
                if total:
                    self._set_progress(len(data) / total * 70) #Cap at 70% — the remaining 30% is frame extraction

            self._set_status("Extracting frames...")
            gif = Image.open(io.BytesIO(data)) #Load the raw bytes into Pillow as a GIF
            frames = []

            try:
                while True:
                    if self._cancelled:
                        return
                    frame = gif.copy().convert("RGBA") #Convert each frame to RGBA for consistent color handling
                    frame = frame.resize((frame_size, frame_size), Image.LANCZOS) #Resize to display size
                    frames.append(ImageTk.PhotoImage(frame)) #Convert to Tkinter compatible image and store
                    gif.seek(gif.tell() + 1) #Advance to the next frame
                    pct = 70 + len(frames) / 512 * 30
                    self._set_progress(min(pct, 99)) #Cap at 99% until fully complete
            except EOFError: #Pillow raises EOFError when there are no more frames, exit the loop cleanly
                pass

            self._set_progress(100) #Updates the progress bar.
            self._set_status(f"{len(frames)} frames ready.") #Updates the status label.

            if not self._cancelled:
                self.after(0, lambda: self._finish(name, frames))  #Schedule _finish on the main thread since _load runs in a background thread

        except Exception as e:
            if not self._cancelled: #Only show the error if the user didn't cancel, cancelling also triggers an exception
                self._set_status(f"Error: {e}") #Display the error in the dialog
                print(f"[loader] {e}") #Also print to console for debugging

    def _finish(self, name, frames):
        self._on_complete(name, frames) #Hand the loaded frames back to Viewer via the callback
        self.destroy() #Close the loader dialog

    def _cancel(self):
        self._cancelled = True #Signal the download thread to stop
        self.destroy() #Close the loader dialog

class Viewer(tk.Frame):
    def __init__(self, root, show):
        super().__init__(root, bg="#1a1a1a")
        self._show = show
        self._frames = []
        self._loaded_name = None
        self._selected_model = tk.StringVar(value=list(MODELS.keys())[0])
        self._az = default_az
        self._el = default_el

        self._autospin_var = tk.BooleanVar(value=False)
        self._spin_job = None

        self._drag_x = None
        self._drag_y = None
        self._drag_az_start = None
        self._drag_el_start = None

        self._build_state1()

    def _seek(self, az, el):
        az = az % azimuth_steps #This wraps azimuth around, if az goes past 31 it loops back to 0, This is what give the seamless rotation.
        el = max(0, min(elevation_steps - 1, el)) #This clamps the elevation, there are no frames to show above or below, so it just stops at the edges instead of looping.
        self._az = az
        self._el = el
        if not self._frames: #Exit early if no model is loaded yet, prevents IndexError on empty list
            return
        frame_index = el * azimuth_steps + az
        self._img_label.configure(image=self._frames[frame_index])
        self._az_slider.set(az) #Keep sliders in sync with current position so they move during drag and autospin
        self._el_slider.set(el)
        az_deg = (360.0 / azimuth_steps) * az
        el_deg = -90.0 + (180.0 / elevation_steps) / 2.0 + (180.0 / elevation_steps) * el
        self._info_var.set(
            f"frame {frame_index:>4}  |  az={az_deg:>7.2f}°  el={el_deg:>+7.2f}°  |  x={az}  y={el}"
        ) #Convert raw grid coordinates to degrees for the info bar, purely cosmetic

    def on_hide(self):
        self._stop_spin() #Stop the spin loop when leaving the viewer so it doesn't run in the background, frames stay in memory

    def _on_load_complete(self, name, frames): # Callback passed to Loader, called when download and frame extraction are complete
        self._frames = frames
        self._loaded_name = name
        self._selected_model.set(name)
        self._enter_state3()
        self._seek(default_az, default_el)
        self._on_radio_change()
        self._autospin_var.set(True)
        self._start_spin()

    def _build_state1(self): #Builds the initial viewer UI, sidebar widgets that reveal in state 3 are built here but not packed
        self._sidebar = tk.Frame(self, bg="#111111", width=160)
        self._sidebar.pack(side="left", fill="y")
        self._sidebar.pack_propagate(False) #Prevent the sidebar from shrinking to fit its children, keeps it at width=160

        tk.Label(
            self._sidebar, text="Viewer",
            font=("Arial", 10, "bold"), bg="#111111", fg="#b0bf1a",
        ).pack(pady=(20, 10))
        tk.Frame(self._sidebar, bg="#333333", height=1).pack(fill="x", padx=10, pady=(0, 10))

        self._load_btn = tk.Button(
            self._sidebar, text="▶  Load Model",
            height=2, font=("Arial", 10, "bold"),
            bg="#b0bf1a", fg="white",
            command=self._open_loader,
        )
        self._load_btn.pack(fill="x", padx=12, pady=8)

        self._status_label = tk.Label(
            self._sidebar, text="",
            font=("Arial", 8), bg="#111111", fg="#555555",
        ) #Not packed yet, revealed in _enter_state3

        self._radio_frame = tk.Frame(self._sidebar, bg="#111111")
        for name in MODELS:
            tk.Radiobutton(
                self._radio_frame,
                text=name,
                variable=self._selected_model,
                value=name,
                command=self._on_radio_change,
                font=("Arial", 9),
                bg="#111111", fg="#cccccc",
                activebackground="#111111",
                selectcolor="#111111",
                anchor="w",
            ).pack(fill="x", pady=2)
        #Not packed yet, revealed in _enter_state3

        self._autospin_cb = tk.Checkbutton(
            self._sidebar, text="Auto-Spin",
            variable=self._autospin_var,
            command=self._on_autospin_toggle,
            font=("Arial", 9),
            bg="#111111", fg="#aaaaaa",
            activebackground="#111111",
            activeforeground="#b0bf1a",
            selectcolor="#111111",
            anchor="w", cursor="hand2",
        )
        #Not packed yet, revealed in _enter_state3

        self._divider = tk.Frame(self._sidebar, bg="#333333", height=1) #Added this because it would unpack on each model load.
        #Not packed yet, revealed in _enter_state3

        tk.Button(
            self._sidebar, text="◀  Back",
            command=lambda: self._show("menu"),
            font=("Arial", 10), bg="#1a1a1a", fg="white",
        ).pack(side="bottom", fill="x", padx=12, pady=12) # Pinned to the bottom of the sidebar

        self._main = tk.Frame(self, bg="#1a1a1a")
        self._main.pack(side="left", fill="both", expand=True)
        tk.Label(
            self._main, text="No model loaded.",
            font=("Arial", 12), bg="#1a1a1a", fg="#555555",
        ).pack(expand=True) #Placeholder, destroyed in _enter_state3 when a model loads

    def _open_loader(self):
        show_combo = self._loaded_name is None
        Loader(self, MODELS, self._selected_model.get(), self._on_load_complete, show_combo) #Show combobox on first load, hide it on subsequent loads since radio button already made the selection

    def _on_radio_change(self):
        if self._selected_model.get() == self._loaded_name:
            self._load_btn.configure(state="disabled", bg="#555555", cursor="arrow") #Gray out load button, no point reloading the same model
        else:
            self._load_btn.configure(state="normal", bg="#b0bf1a", cursor="hand2") #Re-enable load button if a different model is selected

    def _on_drag_start(self, event):
        if self._autospin_var.get(): #Don't allow manual orbit while auto-spin is active
            return
        self._drag_x = event.x
        self._drag_y = event.y
        self._drag_az_start = self._az #Anchor the starting az/el so drag is relative to current position, once clicked.
        self._drag_el_start = self._el

    def _on_drag_move(self, event):
        if self._drag_x is None or self._autospin_var.get():
            return
        sensitivity = 8 #Slows mouse input down so small movements don't jump too many frames
        az = self._drag_az_start + (event.x - self._drag_x) // sensitivity
        el = self._drag_el_start + (event.y - self._drag_y) // sensitivity
        self._seek(az, el)

    def _on_autospin_toggle(self):
        if self._autospin_var.get():
            self._seek(self._az, spin_el) #Lock elevation to spin_el when auto-spin is enabled
            self._el_slider.configure(state="disabled") #Disable elevation slider during auto-spin
            self._start_spin()
        else:
            self._stop_spin()
            self._el_slider.configure(state="normal") #Re-enable elevation slider when auto-spin is off

    def _start_spin(self):
        self._stop_spin() #Cancel any existing spin loop before starting a new one to prevent duplicates
        self._spin_tick()

    def _stop_spin(self):
        if self._spin_job:
            self.after_cancel(self._spin_job) #Cancel the scheduled callback using its stored ID
            self._spin_job = None

    def _spin_tick(self):
        self._seek(self._az + 1, spin_el) #Advance one azimuth step per tick (spin_ms = int(60) ~16-17 frames per second.)
        self._spin_job = self.after(spin_ms, self._spin_tick) #Schedule next tick, creating a continuous loop

    def _enter_state3(self): #I named it state 3, I had originaly planned to use another frame/py file for loader. (State 2 is the loader dialog box)
        self._status_label.config(text=f"Loaded: {self._loaded_name}")
        self._status_label.pack(padx=12, pady=(0, 4)) #Reveal the loaded model name in the sidebar
        self._radio_frame.pack(fill="x", padx=12) #Reveal the model selection radio buttons
        self._divider.pack(fill="x", padx=10, pady=(8, 0)) # Divider
        self._autospin_cb.pack(fill="x", padx=12, pady=(6, 4)) #Reveal the auto-spin checkbox

        for widget in self._main.winfo_children(): #Clear the "No model loaded." placeholder before building the viewer UI
            widget.destroy()

        self._img_label = tk.Label(self._main, bg="#1a1a1a", cursor="fleur")
        self._img_label.pack(pady=20)
        self._img_label.bind("<ButtonPress-1>", self._on_drag_start) #Bind click to start drag orbit
        self._img_label.bind("<B1-Motion>", self._on_drag_move) #Bind mouse movement to drag orbit

        tk.Label(self._main, text="<- Spin ->", font=("Arial", 9),
                 bg="#1a1a1a", fg="#aaaaaa").pack()
        self._az_slider = tk.Scale(
            self._main, from_=0, to=azimuth_steps - 1,
            orient="horizontal", length=400,
            command=lambda v: self._seek(int(v), self._el),
            bg="#1a1a1a", fg="#b0bf1a", troughcolor="#333333", highlightthickness=0,
        )
        self._az_slider.pack(pady=4)

        tk.Label(self._main, text="Tilt", font=("Arial", 9),
                 bg="#1a1a1a", fg="#aaaaaa").pack()
        self._el_slider = tk.Scale(
            self._main, from_=0, to=elevation_steps - 1,
            orient="horizontal", length=400,
            command=lambda v: self._seek(self._az, int(v)),
            bg="#1a1a1a", fg="#b0bf1a", troughcolor="#333333", highlightthickness=0,
        )
        self._el_slider.pack(pady=4)

        self._info_var = tk.StringVar(value="")
        tk.Label(
            self._main, textvariable=self._info_var,
            font=("Arial", 9), fg="#555555", bg="#1a1a1a",
        ).pack(pady=(0, 8))

        root.geometry("900x600") #Expand window to make room for the full viewer UI

class Menu(tk.Frame):
    def __init__(self, root):
        super().__init__(root, bg="#1a1a1a")

        tk.Label(self, text="'3D' Turntable", font=("Arial", 35, "bold"),
                 bg="#1a1a1a", fg="#b0bf1a").pack(pady=(35, 0))
        tk.Label(self, text="Viewer", font=("Arial", 35, "bold"),
                 bg="#1a1a1a", fg="#b0bf1a").pack(pady=(0, 35))
        #All three buttons share _onClick to keep navigation clean and avoid redundant methods
        tk.Button(self, text="▶  Start", command=lambda: self._onClick("Start"),
                  height=2, font=("Arial", 15, "bold"), bg="#b0bf1a", fg="white").pack(pady=2, padx=100, fill="x")
        tk.Button(self, text="◉  About", command=lambda: self._onClick("About"),
                  height=2, font=("Arial", 15, "bold"), bg="#1a1a1a", fg="white").pack(pady=2, padx=100, fill="x")
        tk.Button(self, text="✕  Exit", command=lambda: self._onClick("Exit"),
                  height=2, font=("Arial", 15, "bold"), bg="#1a1a1a", fg="#ff4444").pack(pady=2, padx=100, fill="x")

    def _onClick(self, text):
        if text == "Start":
            show("viewer")
        elif text == "About":
            show("about")
        elif text == "Exit":
            root.destroy()

def show(name):
    for frame in frames.values():
        frame.pack_forget() #Hide all frames without destroying them, preserving their state
    frames[name].pack(fill="both", expand=True)
    if hasattr(frames[name], "on_show"): #Not all frames have on_show (Menu doesn't)
        frames[name].on_show()
    for n, f in frames.items():
        if n != name and hasattr(f, "on_hide"): # Not all frames have on_hide (Menu doesn't), Menu has no state to clean up, which is also why the window size doesn't reset when returning to it
            f.on_hide()

frames = {} #Stores each frame in a dictionary, allowing show() to look up and iterate over frame objects, enabling hasattr checks and method calls like on_show/on_hide.
frames["menu"] = Menu(root)
frames["viewer"] = Viewer(root, show)
frames["about"] = About(root, show)

show("menu")
root.mainloop()