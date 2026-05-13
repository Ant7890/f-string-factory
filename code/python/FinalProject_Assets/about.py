"""
I thought it would be cool to split the files, so instead of one long file, we have delegated functions to their 'page.'
I had planned for more than two, this also keeps code length down on each file.
"""
import tkinter as tk
import requests
import io
import threading
from PIL import Image, ImageTk

spin_interval_ms = int(60)
default_frame_ms = int(60)
elevation_row = int(8)
azimuth_steps = int(32)

MODEL_URLS = {
    "Gameboy": "https://raw.githubusercontent.com/Ant7890/f-string-factory/main/code/python/FinalProject_Assets/Gameboy.gif",
    "Monkey": "https://raw.githubusercontent.com/Ant7890/f-string-factory/main/code/python/FinalProject_Assets/Monkey.gif",
    "Python Logo": "https://raw.githubusercontent.com/Ant7890/f-string-factory/main/code/python/FinalProject_Assets/PythonLogo.gif",
    "Alfa Romeo": "https://raw.githubusercontent.com/Ant7890/f-string-factory/main/code/python/FinalProject_Assets/AlfaRomeo.gif",
}

class About(tk.Frame):
    def __init__(self, root, show):
        super().__init__(root, bg="#1a1a1a")
        self._show = show

        self._seek_frames = [] #Stores Python Logo frames for the seek-spin animation, locked to el=8
        self._az = 0
        self._spin_job = None

        self._raw_frames = {} #Stores all 512 frames for each of the 4 models for raw GIF playback
        self._raw_durations = {} #Stores each frame's duration for accurate playback timing
        self._raw_index = {} #Tracks the current frame index for each model's playback
        self._raw_jobs = {}

        self._loaded = False #Tracks whether all four GIFs have been downloaded, prevents re-downloading on subsequent visits since frames stay cached in memory
        self._build_ui()

    def on_show(self):
        root = self.winfo_toplevel()
        root.geometry("600x750")
        if not self._loaded:
            self._dialog = AboutLoader(root, self) #Show the loading dialog while GIFs are downloading
            threading.Thread(target=self._load_all, daemon=True).start() #Sets the loader to another thread; without it, the window looked like it crashed.
        else: #Else resets, say you go back to the menu, it stops the spinning.
            self._az = 0
            self._raw_index = {name: 0 for name in MODEL_URLS}
            self._start_spin()
            self._start_all_raw()

    def on_hide(self): #Stops all gifs
        self._stop_spin() #Stops the spinning so it isn't running in the background if we went back to the menu.
        self._stop_all_raw()

    def _fetch_gif(self, url):
        r = requests.get(url, stream=True, timeout=20)
        r.raise_for_status() #Raises an exception if the download fails e.g. 404
        return b"".join(r.iter_content(chunk_size=8192)) #Download and return raw 8KB chunks, no progress tracking needed unlike Loader

    def _load_all(self): #Downloads and extracts all four GIFs on a background thread, scheduling UI updates back to the main thread via after()
        seek_frames_result = [] #Python Logo frames only, used for the seek-spin animation at el=8
        raw_frames_result = {} #All 512 frames for each of the 4 models for raw GIF playback
        raw_durations_result = {} #Frame durations for each model to preserve original playback timing
        names = list(MODEL_URLS.keys())
        total = len(names) #Used to calculate progress and status updates

        for i, (name, url) in enumerate(MODEL_URLS.items()):
            self.after(0, lambda n=name, i=i, t=total:
                self._dialog.set_status(f"Downloading {n}... ({i+1}/{t})")) #Update dialog status on main thread
            data = self._fetch_gif(url)

            self.after(0, lambda n=name, i=i, t=total:
                self._dialog.set_status(f"Extracting {n}... ({i+1}/{t})"))
            self.after(0, lambda i=i, t=total:
                self._dialog.set_progress((i / t) * 100)) #Update progress bar on main thread

            gif  = Image.open(io.BytesIO(data)) #Load raw bytes into Pillow as a GIF

            raw_f = [] #Temp storage for frames
            raw_d = []

            try:
                while True:
                    duration = gif.info.get("duration", default_frame_ms)
                    if duration == 0:
                        duration = default_frame_ms  #Fall back to default if duration is missing or zero

                    frame_img = gif.copy().convert("RGBA")

                    if name == "Python Logo": #Only store Python Logo frames for seek-spin, resized larger for the spinner
                        sized = frame_img.resize((150, 150), Image.LANCZOS)
                        seek_frames_result.append(ImageTk.PhotoImage(sized))

                    sized_small = frame_img.resize((120, 120), Image.LANCZOS) #All models resized smaller for the 2x2 grid
                    raw_f.append(ImageTk.PhotoImage(sized_small))
                    raw_d.append(duration)

                    gif.seek(gif.tell() + 1) #Advance to the next frame, gif.tell() returns the current frame index

            except EOFError:
                pass

            raw_frames_result[name] = raw_f #Store completed frame list under the model name
            raw_durations_result[name] = raw_d #Store completed duration list under the model name

        self.after(0, lambda: self._on_load_complete( # Schedule completion on main thread since _load_all runs in a background thread
            seek_frames_result, raw_frames_result, raw_durations_result
        ))

    def _on_load_complete(self, seek_frames, raw_frames, raw_durations):
        self._seek_frames = seek_frames
        self._raw_frames = raw_frames
        self._raw_durations = raw_durations
        self._raw_index = {name: 0 for name in MODEL_URLS} #Reset all four models to frame 0 so playback starts clean
        self._loaded = True
        self._az = 0 #Reset azimuth so the seek-spin starts from the beginning
        self._dialog.close() #Dismiss the loader before starting animations so it doesn't block the gifs
        self._start_spin()
        self._start_all_raw()

    def _start_spin(self):
        self._stop_spin()
        self._spin_tick()

    def _stop_spin(self):
        if self._spin_job is not None:
            self.after_cancel(self._spin_job)
            self._spin_job = None

    def _spin_tick(self): #This uses some of the viewer code. But only to lock it to the correct angle for the logo loop.
        if not self._seek_frames:
            return
        frame_index = elevation_row * azimuth_steps + self._az #Index into the flat frame list using 2D grid math (row * width + col)
        self._logo_label.configure(image=self._seek_frames[frame_index]) #Push the calculated frame to the label widget
        self._az = (self._az + 1) % azimuth_steps #Advance azimuth by one, wrapping back to 0 at 32
        self._spin_job = self.after(spin_interval_ms, self._spin_tick) #Create a continuous loop

    def _start_all_raw(self): #Kicks off independent playback loops for all four models simultaneously
        for name in MODEL_URLS:
            self._raw_tick(name)

    def _stop_all_raw(self): #Stops all four models simultaneously
        for name, job in self._raw_jobs.items():
            if job is not None:
                self.after_cancel(job)
        self._raw_jobs = {}

    def _raw_tick(self, name): #Advances each model's GIF one frame using its own timing, looping independently without elevation or azimuth locking
        frames = self._raw_frames.get(name, [])
        durations = self._raw_durations.get(name, [])
        if not frames:
            return
        idx = self._raw_index.get(name, 0)
        self._model_labels[name].configure(image=frames[idx])
        delay = durations[idx] #Use the frame's own duration to preserve original GIF timing
        self._raw_index[name] = (idx + 1) % len(frames) #Advance and wrap back to 0 at the end
        self._raw_jobs[name]  = self.after(delay, lambda n=name: self._raw_tick(n)) #Schedule next tick to keep the loop alive

    def _build_ui(self):
        tk.Button(
            self, text="◀  Back",
            command=lambda: self._show("menu"),
            height=2, font=("Arial", 15, "bold"),
            bg="#1a1a1a", fg="white",
        ).pack(pady=(10, 5), padx=100, fill="x")

        tk.Label(
            self, text="Seek-Spin (az stepping, el=8 locked)",
            font=("Arial", 8), bg="#1a1a1a", fg="#444444",
        ).pack()
        self._logo_label = tk.Label(self, bg="#1a1a1a")
        self._logo_label.pack(pady=(2, 10))

        tk.Frame(self, bg="#333333", height=1).pack(fill="x", padx=60, pady=6)
        tk.Label(self, text="'3D' Turntable Viewer",
                 font=("Arial", 12, "bold"), bg="#1a1a1a", fg="#ffffff").pack()
        tk.Label(self, text="Built with Python + Tkinter + Pillow",
                 font=("Arial", 9), bg="#1a1a1a", fg="#aaaaaa").pack()
        tk.Label(self, text="Rendered in Blender 4.x",
                 font=("Arial", 9), bg="#1a1a1a", fg="#aaaaaa").pack()
        tk.Label(self, text="Cloud assets via GitHub Raw",
                 font=("Arial", 9), bg="#1a1a1a", fg="#aaaaaa").pack()
        tk.Frame(self, bg="#333333", height=1).pack(fill="x", padx=60, pady=6)

        tk.Label(
            self, text="Raw GIF playback (all 512 frames, original timing)",
            font=("Arial", 8), bg="#1a1a1a", fg="#444444",
        ).pack()

        grid_frame = tk.Frame(self, bg="#1a1a1a")
        grid_frame.pack(pady=8)

        self._model_labels = {}
        names = list(MODEL_URLS.keys())
        positions = [(0, 0), (0, 1), (1, 0), (1, 1)]

        for i, name in enumerate(names):
            row, col = positions[i]
            cell = tk.Frame(grid_frame, bg="#1a1a1a")
            cell.grid(row=row, column=col, padx=10, pady=10)
            tk.Label(cell, text=name, font=("Arial", 8),
                     bg="#1a1a1a", fg="#aaaaaa").pack()
            lbl = tk.Label(cell, bg="#1a1a1a")
            lbl.pack()
            self._model_labels[name] = lbl

class AboutLoader(tk.Toplevel):
    def __init__(self, parent, about_frame):
        super().__init__(parent)
        self.title("Loading...")
        self.resizable(False, False)
        self.configure(bg="#1a1a1a")
        self.geometry("300x160")
        self.grab_set()

        self.update_idletasks() #Forces accurate geometry
        px = parent.winfo_rootx() + (parent.winfo_width()  // 2) - 150
        py = parent.winfo_rooty() + (parent.winfo_height() // 2) - 80
        self.geometry(f"300x160+{px}+{py}") #Center the dialog over the parent window

        self._build_ui()
        self.protocol("WM_DELETE_WINDOW", lambda: None) #I noticed I could cause a lot of errors by closing the loader while it was downloading, so I googled how to prevent that and found protocol('WM_DELETE_WINDOW')

    def _build_ui(self):
        tk.Label(
            self, text="Loading About...",
            font=("Arial", 11, "bold"),
            bg="#1a1a1a", fg="#b0bf1a",
        ).pack(pady=(18, 8))

        self._status_var = tk.StringVar(value="Starting...")
        tk.Label(
            self, textvariable=self._status_var,
            font=("Arial", 9), bg="#1a1a1a", fg="#aaaaaa",
        ).pack()

        from tkinter import ttk
        self._progress = ttk.Progressbar(
            self, orient="horizontal", length=240, mode="determinate",
        )
        self._progress.pack(pady=10, padx=20)

    def set_status(self, text):
        self._status_var.set(text)

    def set_progress(self, val):
        self._progress.configure(value=val)

    def close(self):
        self.grab_release()
        self.destroy()