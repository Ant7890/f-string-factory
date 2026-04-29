import tkinter as tk
from PIL import Image, ImageTk ##This library is for image processing so we can resize an image

root = tk.Tk() # Makes the window
root.title('GUI demo') #Makes the title that will appear in the top left
root.config(bg='tan') # Define root color

##Functions to draw shapes onto the canvas when called
def red_circle():
    shape_canvas.delete('all') # Clear the canvas
    shape_canvas.create_oval(20,20,80,80, fill='red', width=5, tags='my_shape') # Create Oval
    color_log.insert(0.0, 'Red\n') # Place text in the box


def green_rectangle():
    shape_canvas.delete('all') # Clear the canvas
    shape_canvas.create_rectangle(20, 20, 80, 80, fill='green', width=5, tags='my_shape')
    color_log.insert('1.0', 'green\n')

def pikachu():
    shape_canvas.delete('all')
    shape_canvas.create_image(-20,0, image=resized, anchor='nw')
    color_log.insert(0.0, 'Pikachu I Choose you!\n')

def blue_triangle():
    shape_canvas.delete('all')
    shape_canvas.create_polygon(50, 15, 10, 85, 90, 85, fill='blue', width=5, outline="black", tags='my_shape')
    color_log.insert('1.0', 'Blue\n') #I was surprised not to see a premade triangle for the canvas system.
#Left Frame and its contents
left_frame = tk.Frame(root, width=200, height=600)
left_frame.grid(row=0, column=0, padx=10, pady=2)


## Create some text
tk.Label(left_frame, text='Instructions').grid(row=0, column=0, padx=10, pady=2)
instructions = tk.Label(left_frame, text='1\n2\n3\n4\n5\n6\n7\n8\n9\n')
instructions.grid(row=1, column=0, padx=10, pady=2)



##Try to open an image in current directory, print message of not found
try:
    img = Image.open('../../2_Tkinter/image.png')
    resized = img.resize((150, 100))

    resized = ImageTk.PhotoImage(resized)

    tk.Label(left_frame, image=resized).grid(row=2, column=0, padx=10, pady=2)

except:
    print("Image not found")


## Right Frame and its contents
right_frame = tk.Frame(root, width=200, height=600)
right_frame.grid(row=0, column=1, padx=10, pady=2)

##Canvas widget for displaying shapes
shape_canvas = tk.Canvas(right_frame, width=100, height=100, bg='white')
shape_canvas.grid(row=0, column=0, padx=10, pady=2)

##A separate frame will hold the buttons to make placement easier
btn_frame = tk.Frame(right_frame, width=200, height=200, bg='white')
btn_frame.grid(row=1, column=0, padx=10, pady=2)

# Buttons
red_button = tk.Button(btn_frame, text='Red', command=red_circle)
red_button.grid(row=0, column=0, padx=10, pady=2)

yellow_button = tk.Button(btn_frame, text='Yellow', command=pikachu) #I had to switch these around lol.
yellow_button.grid(row=0, column=1, padx=10, pady=2)

green_button = tk.Button(btn_frame, text='Green', command=green_rectangle)
green_button.grid(row=0, column=2, padx=10, pady=2)

blue_button = tk.Button(btn_frame, text='Blue', command=blue_triangle)
blue_button.grid(row=0, column=3, padx=10, pady=2)


## Entry box for displaying the color of the shapes
color_log = tk.Text(right_frame, width=30, height=10, bg='white')
color_log.grid(row=2, column=0, padx=10, pady=2)


root.mainloop() #start monitoring and updating the GUI
