"""
make_gif.py
===========
Normal Python script — stitches the 512 rendered PNGs into turntable.gif.
Run this AFTER turntable_render.py finishes in Blender.

    pip install pillow
    python make_gif.py
"""

from PIL import Image
import os

# ---------------------------------------------------------------------------
# CONFIG — must match turntable_render.py
# ---------------------------------------------------------------------------

AZIMUTH_STEPS:   int = 32
ELEVATION_STEPS: int = 16
TOTAL_FRAMES:    int = AZIMUTH_STEPS * ELEVATION_STEPS  # 512
GIF_FRAME_MS:    int = 50

FRAMES_DIR: str = os.path.join(os.path.expanduser("~"), "Desktop", "turntable", "frames")
GIF_PATH:   str = os.path.join(os.path.expanduser("~"), "Desktop", "turntable", "turntable.gif")

# ---------------------------------------------------------------------------
# STITCH
# ---------------------------------------------------------------------------

def main():
    if not os.path.isdir(FRAMES_DIR):
        print(f"ERROR: frames folder not found:\n  {FRAMES_DIR}")
        print("Run turntable_render.py in Blender first.")
        return

    print(f"[make_gif] Loading {TOTAL_FRAMES} frames from {FRAMES_DIR} ...")

    pil_frames = []
    for i in range(TOTAL_FRAMES):
        path = os.path.join(FRAMES_DIR, f"frame_{i:04d}.png")
        if not os.path.exists(path):
            print(f"ERROR: missing {path}")
            return

        img = Image.open(path).convert("RGBA")

        # Composite onto white background (GIF doesn't support full alpha)
        bg = Image.new("RGBA", img.size, (255, 255, 255, 255))
        bg.paste(img, mask=img.split()[3])
        pil_frames.append(bg.convert("P", palette=Image.ADAPTIVE, colors=256))

        if (i + 1) % 32 == 0:
            print(f"[make_gif]   {i+1}/{TOTAL_FRAMES} frames loaded ...")

    print(f"[make_gif] Assembling GIF ...")
    pil_frames[0].save(
        GIF_PATH,
        save_all=True,
        append_images=pil_frames[1:],
        optimize=False,
        duration=GIF_FRAME_MS,
        loop=0,
    )

    size_mb = os.path.getsize(GIF_PATH) / (1024 * 1024)
    print(f"[make_gif] Done! -> {GIF_PATH}  ({size_mb:.2f} MB)")
    print(f"\n[make_gif] You can now delete the frames folder if you want:")
    print(f"           {FRAMES_DIR}")

main()