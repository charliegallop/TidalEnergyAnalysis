from tkinter import *
from PIL import ImageTk, Image
import os

# create window
window = Tk()
window.geometry('1000x1000')

imagesDir = "/home/charlie/Documents/Uni/Exeter - Data Science/MTHM604_Tackling_Sustainability_Challenges/MTHM604_week_2/plots/final"
folder = os.listdir(imagesDir)
print(folder)
# function to display a series of images with a delay of 3seconds between each
def slideshow():
    for i in range(3):
        entry.delete(0, END)
        canvas.delete("all")
        entry.insert(0, str(i))
        path = (imagesDir + "/" + folder[i])
        print(path)
        image = ImageTk.PhotoImage(Image.open(path))
        canvas.create_image(100, 100, anchor=CENTER, image=image)
        canvas.image = image
        canvas.update_idletasks()
        window.after(3000)
    window.mainloop()

# create widgets
buttonDisplayImages = Button(window, width=30, height=15, text='Display Images', command=lambda: slideshow())
entry = Entry(window, width=35, borderwidth=2)
canvas = Canvas(window, width=300, height=300)

buttonDisplayImages.grid(row=2, column=1)
entry.grid(row=1, column=1)
canvas.grid(row=3, column=1)

window.mainloop()