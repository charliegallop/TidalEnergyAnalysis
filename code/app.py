from tkinter import *
from PIL import Image, ImageTk
import os

imagesDir = "/home/charlie/Documents/Uni/Exeter - Data Science/MTHM604_Tackling_Sustainability_Challenges/MTHM604_week_2/plots/final"

root = Tk()
root.title("Graph viewer")
root.geometry("1000x1000")
root.config(bg="white")
root.resizable(0,0)

def start():
    global i, show
    if i >= (len(images)-1):
        i = 0
        slide_image.config(image = images[i])
    else: 
        i = i + 1
        slide_image.configure(image = images[i])
    show = slide_image.after(500, start)

def stop():
    global show
    slide_image.after_cancel(show)

def resume():
    start()

folder = os.listdir(imagesDir)
images = []
imgIndex = 0

for image in folder:
    img = Image.open(f"{imagesDir}/{image}")
    x = ImageTk.PhotoImage(img)
    images.append(x)

def next():
    global i, show
    if show is None:
        slide_image.config(image = images[i])
        show = slide_image.after(10000, start)
    slide_image.after_cancel(show)
    if i < (len(images) -1):
        i = i + 1
    else:
        i = 0
    slide_image.config(image = images[i])
    show = slide_image.after(500, start)
    slide_image.after_cancel(show)

def prev():
    global i, show
    slide_image.after_cancel(show)
    if i == 0:
        i =(len(images) -1)
    else:
        i = i -1
    slide_image.config(image = images[i])
    show = slide_image.after(500, start)
    slide_image.after_cancel(show)


# def getImgOpen(seq):
#         print('Opening %s' % seq)
#         imgIndex = 0
#         if seq=='ZERO':
#             imgIndex = 0
#         elif (seq == 'prev'):
#             if (imgIndex == 0):
#                 imgIndex = len(images)-1
#             else:
#                 imgIndex -= 1
#         elif(seq == 'next'):
#             if(imgIndex == len(images)-1):
#                 imgIndex = 0
#             else:
#                 imgIndex += 1

#         masterImg = Label(root, image = images[imgIndex]) 
#         root.title(images[imgIndex])
#         #masterImg.thumbnail((400,400))
#         img = ImageTk.PhotoImage(masterImg)
#         lbl['image'] = img
#         return


# prevBtn = Button(root, text='Previous', command=getImgOpen(seq = 'prev'),
#                 bg='blue', fg='red').place(relx=0.85, rely=0.99, anchor=SE)


# nextBtn = Button(root, text='Next', command=getImgOpen('next'),
#                 bg='green', fg='black').place(relx=0.90, rely=0.99, anchor=SE)





i = 0
slide_image = Label(root, image = images[i])
slide_image.pack(pady = 50)

# create buttons
btn1 = Button(root, text="Start", bg='black', fg='gold', width=4, font=('ariel 20 bold'), relief=GROOVE, command=start)
btn1.pack(side=LEFT, padx=60, pady=50)
btn2 = Button(root, text="Pause/Stop", bg='black', fg='gold', width=4, font=('ariel 20 bold'), relief=GROOVE, command=stop)
btn2.pack(side=LEFT, padx=60, pady=50)
btn3 = Button(root, text="Resume", bg='black', fg='gold', width=4, font=('ariel 20 bold'), relief=GROOVE, command=resume)
btn3.pack(side=LEFT, padx=60, pady=50)
btn4 = Button(root, text="Exit", bg='black', fg='gold', width=4, font=('ariel 20 bold'), relief=GROOVE, command=root.destroy)
btn4.pack(side=LEFT, padx=30, pady=50)
btn5 = Button(root, text="Next", bg='black', fg='gold', width=4, font=('ariel 20 bold'), relief=GROOVE, command=next)
btn5.pack(side=LEFT, padx=30, pady=50)
btn5 = Button(root, text="Previous", bg='black', fg='gold', width=4, font=('ariel 20 bold'), relief=GROOVE, command=prev)
btn5.pack(side=LEFT, padx=30, pady=50)

root.mainloop()

