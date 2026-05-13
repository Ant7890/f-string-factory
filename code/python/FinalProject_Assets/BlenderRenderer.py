"""
turntable_render.py
===================
Blender-only script — renders 512 PNGs, nothing else.
No Pillow required. Run this inside Blender.

After this finishes, run make_gif.py in normal Python to stitch the GIF.

HOW TO RUN
----------
Blender Scripting tab -> Run Script
or headless:
    blender --background your_scene.blend --python turntable_render.py

"""

import bpy
import math
import os

# ---------------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------------

AZIMUTH_STEPS:   int   = 32
ELEVATION_STEPS: int   = 16
CAMERA_DISTANCE: float = 4.0
RESOLUTION:      int   = 512
RENDER_ENGINE:   str   = "BLENDER_EEVEE_NEXT"
CYCLES_SAMPLES:  int   = 32

# Output folder — frames go here as frame_0000.png ... frame_0511.png
OUTPUT_DIR: str = os.path.join(os.path.expanduser("~"), "Desktop", "turntable", "frames")

# ---------------------------------------------------------------------------
# DERIVED
# ---------------------------------------------------------------------------

AZ_STEP  = 360.0 / AZIMUTH_STEPS
EL_STEP  = 180.0 / ELEVATION_STEPS
EL_START = -90.0 + EL_STEP / 2.0
TOTAL    = AZIMUTH_STEPS * ELEVATION_STEPS  # 512

# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------

def _get_or_create_camera():
    if bpy.context.scene.camera:
        return bpy.context.scene.camera
    cam_data = bpy.data.cameras.new("TurntableCam")
    cam_obj  = bpy.data.objects.new("TurntableCam", cam_data)
    bpy.context.collection.objects.link(cam_obj)
    bpy.context.scene.camera = cam_obj
    return cam_obj

def _configure_render():
    scene  = bpy.context.scene
    render = scene.render
    render.engine                     = RENDER_ENGINE
    render.resolution_x               = RESOLUTION
    render.resolution_y               = RESOLUTION
    render.resolution_percentage      = 100
    render.image_settings.file_format = "PNG"
    render.image_settings.color_mode  = "RGBA"
    if RENDER_ENGINE == "CYCLES":
        scene.cycles.samples = CYCLES_SAMPLES

def _spherical_to_xyz(az_deg, el_deg, r):
    az = math.radians(az_deg)
    el = math.radians(el_deg)
    return (
         r * math.cos(el) * math.sin(az),
         r * math.cos(el) * math.cos(az),
         r * math.sin(el),
    )

def _aim_at_origin(cam):
    import mathutils
    direction = mathutils.Vector((0, 0, 0)) - mathutils.Vector(cam.location)
    cam.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()

# ---------------------------------------------------------------------------
# RENDER LOOP
# ---------------------------------------------------------------------------

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    _configure_render()
    cam = _get_or_create_camera()

    print(f"\n[turntable] Rendering {TOTAL} frames to: {OUTPUT_DIR}\n")

    for el_index in range(ELEVATION_STEPS):
        el_deg = EL_START + EL_STEP * el_index
        for az_index in range(AZIMUTH_STEPS):
            az_deg      = AZ_STEP * az_index
            frame_index = el_index * AZIMUTH_STEPS + az_index

            cam.location = _spherical_to_xyz(az_deg, el_deg, CAMERA_DISTANCE)
            _aim_at_origin(cam)

            out_path = os.path.join(OUTPUT_DIR, f"frame_{frame_index:04d}.png")
            bpy.context.scene.render.filepath = out_path

            print(f"[turntable] {frame_index+1:>4}/{TOTAL}  "
                  f"az[{az_index:>2}]={az_deg:>7.2f}  "
                  f"el[{el_index:>2}]={el_deg:>+7.2f}  "
                  f"-> frame_{frame_index:04d}.png")

            bpy.ops.render.render(write_still=True)

    print(f"\n[turntable] Done! Now run make_gif.py to stitch the GIF.")
    print(f"[turntable] Frames folder: {OUTPUT_DIR}")

main()