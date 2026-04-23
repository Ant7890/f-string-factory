"""
2.3 Tkinter Layout with Frames

Goal:
    Layout a window using Tkinter Frames

    Steps:
        1) Open file called 2.3b_layout_image_for_exercise (you may need to download it)

        2) Examine the layout in the image on that file

        3) Use what you learned about frames to create a layout tht is as similar to the one
           on that image as possible

            NOTE: You don't have to place the text on to your layout unelss you want to.
"""
"""
2.3 Tkinter Layout with Frames

Goal:
    Layout a window using Tkinter Frames

    Steps:
        1) Open file called 2.3b_layout_image_for_exercise (you may need to download it)

        2) Examine the layout in the image on that file

        3) Use what you learned about frames to create a layout tht is as similar to the one
           on that image as possible

            NOTE: You don't have to place the text on to your layout unelss you want to.
"""
import tkinter as tk

root = tk.Tk()
root.title("Layout with Frames")
root.geometry("1280x720")
root.resizable()

# Sidebar on the left
sidebar_frame = tk.Frame(root, bg="#7B3FA0", width=200)
sidebar_frame.pack(side="left", fill="y", padx=5, pady=5)
sidebar_frame.pack_propagate(False)

# Main area fills the rest
main_frame = tk.Frame(root, bg="white")
main_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5, ipadx=10, ipady=10)

# Header across the top
header_frame = tk.Frame(main_frame, bg="#89C4E1", height = 80)
header_frame.pack(side="top", fill="x", pady=(0, 5))
header_frame.pack_propagate(False)

# Middle row for two content boxes
content_row = tk.Frame(main_frame, bg="white")
content_row.pack(side="top", fill="both", expand=True, pady=(0, 5))

content_frame1 = tk.Frame(content_row, bg="#E8DFC8")
content_frame1.pack(side="left", fill="both", expand=True, padx=(0, 3))

content_frame2 = tk.Frame(content_row, bg="#E8DFC8")
content_frame2.pack(side="left", fill="both", expand=True, padx=(3, 0))

# Green frame at the bottom
text_frame = tk.Frame(main_frame, bg="#5B8C5A")
text_frame.pack(side="top", fill="both", expand=True)

root.mainloop()