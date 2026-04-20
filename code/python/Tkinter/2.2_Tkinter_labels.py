"""
2.2 Tkinter Labels

Goal:
    Practice using and understanding the different label parameters in Tkinter to display text.

    How:
        1) Choose a song, famous speech, some quotes, or any other piece of text

        2) Create at least SIX unique labels that show pieces of the text.

            - Try to use different parameters, colors, and fonts, across your labels

        Google or AI -
            Feel free to google or use AI to learn more about the different parameters that a label can have.
            You are allowed to incorporate code suggestions given by AI in this code.

        Use the 1_windows_and_text code we wrote in class for examples
"""
import tkinter as tk

root = tk.Tk()
root.title("The Entire Bee Movie Script")

root.geometry("660x560")
root.configure(bg="#f6d800")
# I used AI/google to help find hex color codes that matched a bee color theme
root.resizable(1,1)
root.minsize(200,200)
root.maxsize(1000,1000)

label_1 = tk.Label(root, text="According to all known laws of aviation,", font=("Georgia", 15, "italic"), bg="#f6d800", pady=12)
label_1.pack()
label_2 = tk.Label(root, text="there is no way a bee should be able to fly.", font=("Georgia", 15, "italic"), fg="#1a1a1a", bg="#f6d800")
label_2.pack()
label_3 = tk.Label(root, text="It's wings are too small to get its fat little body\noff the ground.", font=("Courier", 15), fg="#5a3e00", bg="#ffe033", padx=20, pady=10, relief="groove", bd=3, justify="center")
label_3.pack(pady=10) # I asked AI how to emboss. 'Reliefs' do that, makes a sunken border effect
label_4 = tk.Label(root,text="The bee, of course, flies anyway", font=("Helvetica", 14, "bold"), fg="#ffffff", bg="#333300", padx=20, pady=8, relief="solid", bd=2)
label_4.pack(pady=4) # AI explained solid gives a clean flat border, unlike raised or groove
label_5 = tk.Label(root, text="because bees don't care\nwhat humans think is impossible.", font=("Impact", 20), fg="#f6d800", bg="#1a1a1a", padx=25, pady=16, relief="raised", bd=4, justify="center")
label_5.pack(pady=10) # AI showed me raised makes the label look lifted off the screen
rest_label = tk.Label(root, text="[ ...You gotta watch The Bee Movie for the rest... ]", font=("Times New Roman", 10, "italic"), fg="#888800", bg="#f6d800", pady=5)
rest_label.pack()
label_7 = tk.Label(root,text="🐝  Barry B. Benson  🐝\n\"Ya like jazz?\"", font=("Comic Sans MS", 13, "bold"), fg="#5a3e00", bg="#f6d800", justify="center", pady=14, cursor="heart")
label_7.pack(side="bottom") # I googled the emoji, I guess it parses it.

root.mainloop()