from tkinter import *
from pyautogui import position,screenshot
from pynput import mouse
from time import sleep

from PIL import Image, ImageTk, ImageGrab
import numpy as np
import cv2


class main:
    def __init__(self) -> None:
        self.root = Tk()
        self.root.geometry('270x180')
        self.root.title('Auto Sketcher')

        def button(self, x,y, text, command):
            Button(self.root, text=text, bg='gray85', font=('Consolas', 8), command=command).place(x=x,y=y)


        self.corner1_pos = [-1,-1]
        self.corner2_pos = [-1,-1]
        self.input_img = None
        self.raw_sketch = None

        stats = StringVar()
        Label(self.root, textvariable=stats, font=('Consolas', 10)).place(x=-195,y=-15)


        def loop():
            pos = position()
            self.current_pos = [pos[0], pos[1]]
            stats.set(f'''
                      ({self.current_pos[0]}, {self.current_pos[1]})
                      ------------
                      ({self.corner1_pos[0]}, {self.corner1_pos[1]})
                      ({self.corner2_pos[0]}, {self.corner2_pos[1]})
                      ''')
        
            self.root.after(100, loop)
        loop()

        def show_selected_area():
            if -1 in self.corner1_pos or -1 in self.corner2_pos: return

            topleft_pos = [min([self.corner1_pos[0],self.corner2_pos[0]]), min([self.corner1_pos[1],self.corner2_pos[1]])]
            topright_pos = [max([self.corner1_pos[0],self.corner2_pos[0]]), max([self.corner1_pos[1],self.corner2_pos[1]])]

            ss_area = np.array(screenshot())[topleft_pos[1]:topright_pos[1], topleft_pos[0]:topright_pos[0]]
            img = ImageTk.PhotoImage(image=Image.fromarray(ss_area))

            area = Toplevel(self.root)
            area.title('Selected Area')
            imgbg = Canvas(area, width=np.shape(ss_area)[1], height=np.shape(ss_area)[0])
            imgbg.pack()
            imgbg.create_image(0,0, anchor='nw', image=img)

            area.mainloop()
        button(self, 125,8, 'show selected area', command=show_selected_area)
        
        def set_corner1():
            def on_click(x, y, button, pressed):
                if button == mouse.Button.left:
                    self.corner1_pos = [x,y]
                    return False
            listener = mouse.Listener(on_click=on_click)
            listener.start()
            listener.join()

            stats.set(f'''
                      ({self.current_pos[0]}, {self.current_pos[1]})
                      ------------
                      ({self.corner1_pos[0]}, {self.corner1_pos[1]})
                      ({self.corner2_pos[0]}, {self.corner2_pos[1]})
                      ''')
        button(self, 125,42, 'set corner 1', set_corner1)

        def set_corner2():
            def on_click(x, y, button, pressed):
                if button == mouse.Button.left:
                    self.corner2_pos = [x,y]
                    return False
            listener = mouse.Listener(on_click=on_click)
            listener.start()
            listener.join()

            stats.set(f'''
                      ({self.current_pos[0]}, {self.current_pos[1]})
                      ------------
                      ({self.corner1_pos[0]}, {self.corner1_pos[1]})
                      ({self.corner2_pos[0]}, {self.corner2_pos[1]})
                      ''')
        button(self, 125,68, 'set corner 2', set_corner2)

        Label(self.root, text='----------------------------', font=('Consolas Bold', 10)).place(x=5, y=94)

        img_canvas = Canvas(self.root, width=0, height=0)
        def input_image():
            self.root.geometry('270x180')
            self.raw_input_img = ImageGrab.grabclipboard()
            if not self.raw_input_img: return False
            self.input_img = ImageTk.PhotoImage(image=self.raw_input_img)


            self.img_w, self.img_h = np.shape(np.array(self.raw_input_img))[1], np.shape(np.array(self.raw_input_img))[0]
            img_canvas.config(width=self.img_w, height=self.img_h)


            img = np.array(self.raw_input_img, dtype='uint8')
            self.grey_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            invert = cv2.bitwise_not(self.grey_img)
            blur = cv2.GaussianBlur(invert, (21, 21), 0)
            self.invertedblur = cv2.bitwise_not(blur)

            self.raw_sketch = cv2.divide(self.grey_img, self.invertedblur, scale=256.0)
            
            try: thres = int(self.input_thres.get('1.0', END).strip('\n'))
            except ValueError: thres = 220
            ind = np.argwhere(self.raw_sketch > thres)
            self.raw_sketch[ind[:,0], ind[:,1]] = 255
            ind = np.argwhere(self.raw_sketch <= thres)
            self.raw_sketch[ind[:,0], ind[:,1]] = 0

            self.sketch = ImageTk.PhotoImage(master=self.root, image=Image.fromarray(self.raw_sketch))
        button(self, 15,115, 'input ', input_image)

        def delete_image():
            self.input_img = None
            self.img_w, self.img_h = 0, 0
            self.root.geometry('270x180')
            img_canvas.delete('all')
        button(self, 15,145, 'delete', delete_image)
        
        def show_image():
            if not self.input_img: return
            img_canvas.delete('all')

            temp_img_w = 260 if self.img_w <= 270 else self.img_w+10
            self.root.geometry(f'{temp_img_w+10}x{self.img_h+180+10}')
            img_canvas.place(x=10, y=180)
            img_canvas.create_image(0,0, anchor='nw', image=self.input_img)
        button(self, 75,115, 'show image ', show_image)

        def show_sketch():
            if not self.input_img: return
            img_canvas.delete('all')
            

            self.raw_sketch = cv2.divide(self.grey_img, self.invertedblur, scale=256.0)
            try: thres = int(self.input_thres.get('1.0', END).strip('\n'))
            except ValueError: thres = 220
            ind = np.argwhere(self.raw_sketch > thres)
            self.raw_sketch[ind[:,0], ind[:,1]] = 255
            ind = np.argwhere(self.raw_sketch <= thres)
            self.raw_sketch[ind[:,0], ind[:,1]] = 0

            self.sketch = ImageTk.PhotoImage(master=self.root, image=Image.fromarray(self.raw_sketch))


            temp_img_w = 260 if self.img_w <= 270 else self.img_w+10
            self.root.geometry(f'{temp_img_w+10}x{self.img_h+180+10}')
            img_canvas.place(x=10, y=180)

            img_canvas.create_image(0,0, anchor='nw', image=self.sketch)
        button(self, 75,145, 'show sketch', show_sketch)

        self.input_thres = Text(self.root, width=4,height=1, bg='white', font=('Consolas', 10))
        self.input_thres.place(x=195, y=115)

        def draw():
            if not self.input_img: return False
            if -1 in self.corner1_pos or -1 in self.corner2_pos: return

            topleft_pos = [min([self.corner1_pos[0],self.corner2_pos[0]]), min([self.corner1_pos[1],self.corner2_pos[1]])]
            topright_pos = [max([self.corner1_pos[0],self.corner2_pos[0]]), max([self.corner1_pos[1],self.corner2_pos[1]])]
            dimension = [topright_pos[0]-topleft_pos[0], topright_pos[1]-topleft_pos[1]]

            img = cv2.resize(self.raw_sketch, dimension)

            controller = mouse.Controller()
            for y,x in np.argwhere(img == 0):
                controller.position = (x+topleft_pos[0], y+topleft_pos[1])
                controller.press(mouse.Button.left)
                controller.release(mouse.Button.left)
                sleep(.005)
        button(self, 195,145, 'draw', draw)


        self.root.mainloop()


main()
