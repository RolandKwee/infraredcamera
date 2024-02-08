#!/usr/bin/env python3

import tkinter as tk #supports png, but not jpg (use PIL for jpg)
import tkinter.scrolledtext as scrolledtext
from tkinter import messagebox # for the about dialog
from tkinter import filedialog
import datetime # for the timestamp
import traceback # for printing exception
#
from PIL import ImageTk, Image
#from tkinter import filedialog
import os
#import os.path
#from pathlib import Path
# my own classes:
from Pbm import Pbm
from Hist import Hist
from Palette import Palette
from Ansi import Ansi

'''
Gui app for the IR camera plus normal camera.
The camera's are on Raspberry Pi.
This app is developed on linux, but may perhaps also run on RPi.
Roland Kwee, okt-2022, apr-2023
'''

#IR camera with WxH = 32x24 pixels

#_APP_VERSION = 'v-0.1, 2023-04-10 by Roland Kwee ©'
#_APP_VERSION = 'v-1.0, 2023-12-03 by Roland Kwee ©' # capture folders, prev/next buttons
#_APP_VERSION = 'v-1.1, 2023-12-04 by Roland Kwee ©' # fixed bug with backslash in windows paths
_APP_VERSION = 'v-1.2x, 2024-02-08 by Roland Kwee ©' # new menu option json; better app title 
# 2023-12-08 renamed from ir_cam.py to ir_viewer.py
# todo: remove old capture file names
# when selecting a folder without pictures but with sub-folders, descend to the newest subfolder until pictures found
# show in log or title bar how many sibling folders are found
# BUGS:
# 20240206rk: buttons.py: first recording after reboot gets date-time from previous shutdown
# 20240206rk: buttons.py: exception when converting negative temperatures to json file
# 20240208: TODO: read temperatures from ansi log file and write to new json log file
    
class Gui:
    'The gui is the top-level of the entire app'

    # the main gui object
    root = None

    entry_capture_folder = None
    stringvar_capture_folder = None

    canvas_img1 = None
    #label_png = None
    #label_pgm = None
    filename_json = ''

    thePalette = None
    stringvar_irtype = None # could be eliminated

    canvas_ir_image = None
    canvas_palette = None

    ir_pixel_loc_prev = (-1, -1)

    # a second pointer, to show on the photo at the same (x,y) as where the mouse is hovering over the IR
    # or otherwise around
    # https://stackoverflow.com/questions/55643747/is-there-a-function-to-display-an-image-in-tkinter-that-is-any-file-type-and-d
    canvas_photopointer = None

    canvastext_pixeltemperature = None

    dict_t = {}
    
    # scrollable text window for logging messages
    txtLog = None

    def __init__(self):
        'create all widgets'
        # create the gui object
        self.root = tk.Tk()
        self.root.title('Viewer for captures from the Raspberry Pi Infrared Camera')
        #root.geometry('1400x600+150+150')
        self.root.resizable(width=True, height=True)
        #
        self.gui_menu() # add a menu bar
        #
        # frame with path of input file(s)
        f = tk.Frame(self.root)
        f.pack(side=tk.TOP, anchor='w')
        tk.Label(f, text='capture:').pack(side=tk.LEFT)
        self.stringvar_capture_folder = tk.StringVar()
        self.entry_capture_folder = tk.Entry(f, width=40, textvariable=self.stringvar_capture_folder)
        self.entry_capture_folder.pack(side=tk.LEFT)
        tk.Button(f, text='browse', command=self.browse_capture_folder).pack(side=tk.LEFT)
        #
        tk.Button(f, text='< Prev', command=self.capture_folder_prev).pack(side=tk.LEFT)
        tk.Button(f, text='Next >', command=self.capture_folder_next).pack(side=tk.LEFT)
        #
        # type of IR display
        tk.Label(f, text='warm=').pack(side=tk.LEFT, padx=(20,0))
        self.stringvar_irtype = tk.StringVar()
        self.thePalette = Palette()
        self.thePalette.size = 10
        self.stringvar_irtype.set(self.thePalette.types[0]) # default value
        type_of_ir = tk.OptionMenu(f, self.stringvar_irtype, *self.thePalette.types, command=self.select_palette_type)
        type_of_ir.pack(side=tk.LEFT)
        self.thePalette.type = self.stringvar_irtype.get()
        #
        f_images = tk.Frame(self.root)
        f_images.pack(side=tk.TOP, anchor='w')
        #
        # canvas for visible light photo
        self.canvas_img1 = tk.Canvas(f_images, width=640, height=480, bg='green')
        self.canvas_img1.pack(side=tk.LEFT)
        # see: https://stackoverflow.com/questions/43009527/how-to-insert-an-image-in-a-canvas-item
        # place photoimage on canvas.
        # then, place small rectangle item on some (x,y) under control of event callback on IR image

        
        # 2 labels for images, you cannot set the pixel size of Label, do that on Frame
        #f_img1 = tk.Frame(f_images, width=640, height=480, bg='green')
        #f_img1.pack_propagate(0) #needed for enforcing w/h when frame is empty
        #f_img1.pack(side=tk.LEFT)
        #self.label_png = tk.Label(f_img1)
        #self.label_png.pack(side=tk.LEFT)
        #
        self.canvas_ir_image = tk.Canvas(f_images, width=640, height=480)
        self.canvas_ir_image.pack(side=tk.LEFT)
        #self.canvas_photopointer = tk.Canvas(f_images) # UNDER CONSTRUCTION
        #
        #f_img2 = tk.Frame(f_images, width=640, height=480, bg='blue')
        #f_img2.pack_propagate(0) #needed for enforcing w/h when frame is empty
        #f_img2.pack(side=tk.LEFT)
        #self.label_pgm = tk.Label(f_img2)
        #self.label_pgm.pack(side=tk.LEFT)
        #
        #show_photo(root, 'test.png', 1) #good
        #show_photo(root, 'ir.png', int(640/32)) #good
        #show_photo(root, 'ir_raw.pgm', 20)#good
        #show_photo(root, 'lenna.png')
        #show_photo(root, 'lenna.gif')
        #
        self.canvas_palette = tk.Canvas(f_images, width=100, height=480)
        self.canvas_palette.pack(side=tk.LEFT)
        #self.canvas_palette.bind('<Enter>', self.mouse_pixel_enter)
        #self.canvas_palette.bind('<Leave>', self.mouse_pixel_leave)
        #
        # space for log messages
        self.txtLog = scrolledtext.ScrolledText(f_images, undo=True) # vertical scrollbar
        self.txtLog.pack(side=tk.LEFT, expand=True, fill='both')
        return

    def run(self):
        'process initial data and start the main loop'
        # initial data
        self.stringvar_capture_folder.set(os.path.join('testphotos', 'candle_tea'))
        self.showimages()
        #
        # keep main process alive while gui is running as a sub-process
        self.root.mainloop() # runs until root.destroy() or root.quit()
        return

    def gui_menu(self):
        'add menubar with menus to the gui'
        # It's essential to put the following line in your application
        # before you start creating menus.
        # Menubar:
        self.root.option_add('*tearOff', tk.FALSE)
        menubar = tk.Menu(self.root)
        self.root['menu'] = menubar
        # File menu:
        menu_file = tk.Menu(menubar)
        menubar.add_cascade(menu=menu_file, label='File')
        menu_file.add_command(label='Close', command=self.root.destroy) # or: root.quit
        # Tools menu:
        menu_tools = tk.Menu(menubar)
        menubar.add_cascade(menu=menu_tools, label='Tools')
        menu_tools.add_command(label='pgm', command=self.menuoption_makepgm)
        menu_tools.add_command(label='json', command=self.menuoption_makejson)
        #menu_tools.add_command(label='test exception', command=self.menuoption_tool_test_exception)
        #menu_tools.add_command(label='test scrollbar', command=self.menuoption_tool_test_scrollbar)
        # Help menu:
        menu_help = tk.Menu(menubar)
        menubar.add_cascade(menu=menu_help, label='Help')
        menu_help.add_command(label='About', command=self.menuoption_About)
        return

    def menuoption_About(self):
        'show messagebox with general info about this app'
        messagebox.showinfo('About IR app',
                            f'This app shows the infrared photo together with a normal photo. Version: {_APP_VERSION}')
        # Summary of message box options:
        #messagebox.showinfo("Information","Informative message")
        #messagebox.showerror("Error", "Error message")
        #messagebox.showwarning("Warning","Warning message")
        # see: https://docs.python.org/3/library/tkinter.messagebox.html
        #answer=messagebox.askyesnocancel('Question', 'Proceed?', **options) # tk.Ok/Yes/No/None/True/False
        #messagebox.askquestion/askokcancel/askretrycancel/askyesno/askyesnocancel
        return

    def menuoption_makepgm(self):
        'read log.json, write ir.pgm'
        self.log_ts('makepgm start: read log.json, write ir.pgm')
        pbm = Pbm('testphotos/candle_tea')
        pbm.json_read()
        pbm.make_pgm()
        self.log_ts('makepgm done')
        return

    def menuoption_makejson(self):
        'read the ansi logfile and create the json logfile'
        # to recover from the bug that json could not be created in the Buttons app on the RPi
        folder_path = self.stringvar_capture_folder.get()
        ansi = Ansi(folder_path)
        self.log(f'Make JSON msg: {ansi.msg}')
        ansi.make_json()
        self.log(f'Make JSON done: {ansi.msg}')
        return
   
    def log_clear(self):
        'clear the text window'
        self.txtLog.delete(1.0, tk.END)
        return

    def log_ts(self, txt):
        'write a txt to the text window with timestamp'
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        self.log(f'{timestamp} {txt}')
        return

    def log(self, txt):
        'write txt to the text window'
        self.txtLog.insert(tk.END, f'{txt}\n')
        return

    def log_exception(self, exc):
        'write to text window the exception message including traceback'
        s_tb = ''.join(traceback.format_exception(exc))
        self.log_ts(f'Exception: {exc}\n{s_tb}')
        return

    def browse_capture_folder(self):
        #self.log_ts('browse input file is not yet supported')
        filepath = tk.filedialog.askdirectory(
            parent=self.root,
            title='select photo capture folder',
            initialdir=self.stringvar_capture_folder.get(),
            mustexist=True)
        if filepath != None:
            self.stringvar_capture_folder.set(filepath)
            self.entry_capture_folder.xview("end") #scroll to end, handy if path is longer than input box
            self.showimages()
        return
    
    def capture_folder_prev(self):
        self.capture_folder_prev_next(True)
        return
    
    def capture_folder_next(self):
        self.capture_folder_prev_next(False)
        return

    def capture_folder_prev_next(self, prev_notnext):
        # On Windows, os.path.join added a backslash while parent path has forward slashes
        folder_path = self.stringvar_capture_folder.get().replace("\\","/")
        parent, folder_name = os.path.split(folder_path)
        names = sorted(os.listdir(parent), reverse=prev_notnext)
        found = False
        filepath = None
        path = None
        for name in names:
            path = os.path.join(parent, name).replace("\\","/")
            if os.path.isdir(path): # skip files found by listdir
                if found:
                    filepath = path
                    break
                if path == folder_path:
                    found = True # next iteration will find the 'next' folder
        # end for
        if filepath == None:
            # The backslash bug is fixed, but this log would have shown that problem
            self.log(f'BUG: prev_notnext={prev_notnext}, nr names = {len(names)}, folder_path={folder_path}, last path={path}')
        else:
            self.stringvar_capture_folder.set(filepath)
            self.entry_capture_folder.xview("end") #scroll to end, handy if path is longer than input box
            self.showimages()
        return

    def browse_inputfileXXXX(self): #replaced by browse_capture_folder()
        #self.log_ts('browse input file is not yet supported')
        r = tk.filedialog.askopenfile(
            parent=self.root,
            title='select photo image input file',
            filetypes=[('png', '*.png')],
            multiple=False)
        if r != None:
            self.stringvar_inputfile.set(r.name)
            self.entry_inputfile.xview("end") #scroll to end, handy if path is longer than input box
            self.showimages()
        return
    
    def fill_palette_canvas(self, bin_t, bin_n, avg, warm_type):
        'fill in the list of palette colors and show the temperature max values of each bin'
        # size of canvas is h x w = 100 x 480 pixels
        #self.canvas_palette.create_rectangle(10, 10, 90, 470, fill='yellow')
        block_h = 20
        self.canvas_palette.delete('palette') # clear all texts with this tag
        self.canvas_palette.create_text(55, 0, text='t<', anchor='ne', tag='palette')
        self.canvas_palette.create_text(90, 0, text='n',  anchor='ne', tag='palette')
        #print(f'fill_palette_canvas bin_t={bin_t}')
        for i in range(10):
            y = block_h * (i + 1)
            #t = f'{p.greyscale(10, i):>03}'
            c = self.thePalette.greyscale_rgb(i)
            self.canvas_palette.create_rectangle(10, y, 30, y + block_h, fill=c, outline='', tag='palette')
            self.canvas_palette.create_text(55, y, text=f'{bin_t[i]}', anchor='ne', tag='palette')
            self.canvas_palette.create_text(90, y, text=f'{bin_n[i]}', anchor='ne', tag='palette')
        #endfor
        # average
        y = block_h * 10
        self.canvas_palette.create_text(10, y+30, text=f'avg: {avg} °C', anchor='nw', tag='palette')
        # text with temperature of mouse-over pixel
        y = block_h * 11
        self.canvastext_pixeltemperature = \
          self.canvas_palette.create_text(10, y+30, text='? °C', font=('Arial', 20, 'bold'), anchor='nw', tag='palette')
        return

    def mouse_pixel_enter(self, event):
        'mouse enters another pixel in the IR canvas, show its actual temperature'
        bs = 20 # blocksize in pixel
        x = int(event.x / bs) # 0..31
        y = int(event.y / bs) # 0..23
        if (x, y) == self.ir_pixel_loc_prev:
            self.log(f'same IR pixel: ({x},{y}) for ({event.x},{event.y})')
        else:
            if event.x < 1 or event.y < 1:
                self.log(f'zero border: (x,y)={event.x},{event.y}=({x},{y})') #never below zero
            if x > 31:
                self.log(f'x overflow (x,y)={event.x},{event.y}=({x},{y})') # up to 641
            elif y > 23:
                self.log(f'y overflow (x,y)={event.x},{event.y}=({x},{y})') # up to 481
            else:
                t = self.dict_t[x, y]
                #self.log(f'enter (x,y)={event.x},{event.y}={x},{y} t={t}')
                self.canvas_palette.itemconfig(self.canvastext_pixeltemperature, text=f'{t} °C') #f'{event.x},{event.y}')
                #
                self.canvas_img1.delete('ptr1')
                self.canvas_img1.create_rectangle(x*bs, y*bs, (x+1)*bs, (y+1)*bs, fill='red', outline='', tag='ptr1')
        return

    def mouse_pixel_leave(self, event):
        'mouse leaves the IR canvas'
        #self.log_ts(f'mouse_pixel_leave event={event}')
        self.canvas_palette.itemconfig(self.canvastext_pixeltemperature, text='')
        #self.canvastext_pixeltemperature['text'] = 'leave'
        #
        self.canvas_img1.delete('ptr1')
        return

    def fill_ir_image(self, h):
        'fill the canvas with palette blocks to get the entire IR image, h is Hist object'
        frame = h.frame
        bs = 20 # blocksize in pixel
        self.canvas_ir_image.bind('<Leave>', self.mouse_pixel_leave)
        self.dict_t = {}
        for f in frame:
            px = f['x'] # 0..31
            py = f['y'] # 0..23
            x = px * bs # 0..640
            y = py * bs # 0..480
            t = f['t']
            self.dict_t[px, py] = t
            b = h.get_bin(t)
            c = self.thePalette.greyscale_rgb(b)
            pixel = self.canvas_ir_image.create_rectangle(x, y, x+bs, y+bs, fill=c, outline='', tags=('pixel', f't{t}'))
            self.canvas_ir_image.tag_bind(pixel, '<Enter>', self.mouse_pixel_enter)
        #end for
        self.log(f'size of dict_t: {len(self.dict_t)}')
        self.log(f'dict_t(3, 5) = {self.dict_t[(3, 5)]}')
        return

    def select_palette_type(self, warm_type):
        'change the ir display type and re-render the ir display: read and process the json file'
        #self.log_ts(f'selecting another IR display type is not yet supported: {v}')
        self.thePalette.type = warm_type
        h = Hist(self.filename_json, self.log)
        print(f'select_irtype bin_t={h.bin_t} {self.filename_json} warm={warm_type}')
        self.fill_palette_canvas(h.bin_t, h.bin_n, h.avg, warm_type)
        self.fill_ir_image(h)
        return

    def showimages(self):
        'show the images for the selected input file, plus palette, histogram, IR picture'
        # add image to frame (TODO: change to class methods depending on entry widget)
        folder_path = self.stringvar_capture_folder.get()
        path_xxx, folder_name = os.path.split(folder_path)
        pngfile = os.path.join(folder_path, f'{folder_name}.png')
        if not os.path.isfile(pngfile):
            pngfile = os.path.join(folder_path, 'test.png')
        if os.path.isfile(pngfile):
            self.change_photo(pngfile)
        else:
            self.log(f'PNG missing: {folder_name}.png or test.png')
            self.canvas_img1.delete('img1')
        # process the json
        path_file, ext = os.path.splitext(pngfile)
        self.filename_json = os.path.join(folder_path, f'{folder_name}.json')
        if not os.path.isfile(self.filename_json):            
            self.filename_json = os.path.join(folder_path, 'log.json')
        #pgmfile = f'{path_file}.pgm'
        if os.path.isfile(self.filename_json):
            warm_type = self.stringvar_irtype.get()
            self.select_palette_type(warm_type) # FILL IN THE SELECTED IR-TYPE. done.
        else:
            self.log(f'JSON missing: {folder_name}.json or log.json')
            self.canvas_ir_image.delete('pixel')
            self.canvas_palette.delete('palette')
        #self.change_photo(self.label_pgm, pgmfile) #TO BE REPLACED BY CANVAS WIDGET
        #
        # try out placing some icon at x,y
        # notabene: do NOT COMBINE place and pack !!!!
        #self.label_png...
        #tk.Label(window, image=photo_image).place(x=300, y=400, width=200, height=50)
        return

    def change_photo(self, filename, zoom=1):
        'replace photo with filename, and attach to the label, remove photo if filename does not exist'
        if os.path.isfile(filename):
            #img = tk.PhotoImage(file=filename)#tk does not support PGM images
            pil_img = Image.open(filename) #PIL supports PGM-raw P5
            if zoom !=1:
                #tkimage = tkimage.zoom(zoom, zoom) #ik
                pil_img = pil_img.resize((640, 480))
            tkimage= ImageTk.PhotoImage(pil_img)
            #
            self.canvas_img1.delete('img1')
            self.canvas_img1.create_image(0, 0, anchor='nw', image=tkimage, tag='img1')
            self.canvas_img1.x1 = tkimage #keep img in scope
        else:
            label.configure(image='')
        return

if __name__ == "__main__":
    gui = Gui()
    gui.log_ts('start app')
    print('starting mainloop')
    gui.run()
    print('bye')
