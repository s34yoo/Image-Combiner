import os
import tkinter.ttk as ttk
import tkinter.messagebox as msgbox
from tkinter import * # __all__
from tkinter import filedialog
from PIL import Image

root = Tk()
root.title("Mark GUI")

# add source image file
def add_file():
    files = filedialog.askopenfilenames(title="Choose image file", \
        filetypes=(("PNG file", "*.png"), ("All file", "*.*")))
    
    # choosed image files
    for file in files:
        list_file.insert(END, file)

# delete image source
def del_file():
    #print(list_file.curselection())
    for index in reversed(list_file.curselection()):
        list_file.delete(index)

# merged image saving path
def browse_dest_path():
    folder_selected = filedialog.askdirectory()
    if folder_selected == "": 
        return
    #print(folder_selected)
    txt_dest_path.delete(0, END)
    txt_dest_path.insert(0, folder_selected)

# merge image
def merge_image():
    try:
        # option 1 image width
        img_width = cmb_width.get()
        if img_width == "Same size":
            img_width = -1 # -1 if orginal width
        else:
            img_width = int(img_width)

        # option 2 image spacing
        img_space = cmb_space.get()
        if img_space == "small":
            img_space = 30
        elif img_space == "medium":
            img_space = 60
        elif img_space == "large":
            img_space = 90
        else: 
            img_space = 0

        # option 3 image format
        img_format = cmb_format.get().lower() # PNG, JPG, BMP into lowercase

        # option 4 image type
        img_type = cmb_type.get()

        #####################################
        # get images from list_file
        images = [Image.open(x) for x in list_file.get(0, END)]    

        # fix image size by option 1
        image_sizes = [] # [(width1, height1), (width2, height2), ...]
        if img_width > -1:
            # fix width and height by the ratio  
            # size[1] is height, size[0] is width
            image_sizes = [(int(img_width), int(img_width * x.size[1] / x.size[0])) for x in images]
        else:
            # use original image size
            image_sizes = [(x.size[0], x.size[1]) for x in images]

        widths, heights = zip(*(image_sizes)) # unzip to get a list of width and a list of height

        # calculate merged image width and height
        if img_type == "Slide":
            total_width, total_height = max(widths), sum(heights)
        elif img_type == "Film":
            total_width, total_height = sum(widths), max(heights)
        else:
            paired_widths = []
            total_height = 0
            for i in range(0, len(widths)):
                if i % 2 == 0:
                    if i + 1 < len(widths):
                        paired_widths.append(widths[i] + widths[i+1])
                        total_height += max(heights[i], heights[i+1])
                    else:
                        paired_widths.append(widths[i])
                        total_height += heights[i]
            
            total_width = max(paired_widths)
            


        
        # draw sketchbook
        if img_space > 0: 
            if img_type == "Slide":
                total_height += (img_space * (len(images) - 1))
            elif img_type == "Film":
                total_width += (img_space * (len(images) - 1))
            elif img_type == "Cartoon":
                total_width += img_space
                total_height += (img_space * int((len(images) - 1) / 2))

        result_img = Image.new("RGB", (total_width, total_height), (255, 255, 255)) 
        y_offset = 0
        x_offset = 0

        # place images on the sketchbook regarding all the options
        if img_type == "Slide":
            for idx, img in enumerate(images):
                if img_width > -1:
                    img = img.resize(image_sizes[idx])

                result_img.paste(img, (0, y_offset))
                y_offset += (img.size[1] + img_space) 

                progress = (idx + 1) / len(images) * 100 # calculate progress percentage
                p_var.set(progress)
                progress_bar.update()
        elif img_type == "Film":
            for idx, img in enumerate(images):
                if img_width > -1:
                    img = img.resize(image_sizes[idx])

                result_img.paste(img, (x_offset, 0))
                x_offset += (img.size[0] + img_space) 

                progress = (idx + 1) / len(images) * 100 
                p_var.set(progress)
                progress_bar.update()
        elif img_type == "Cartoon":
            for idx, img in enumerate(images):
                if img_width > -1:
                    img = img.resize(image_sizes[idx])

                if idx % 2 == 0:
                    x_offset = 0
                    result_img.paste(img, (x_offset, y_offset))
                    x_offset = (img.size[0] + img_space)
                    left_height = img.size[1]
                else:
                    result_img.paste(img, (x_offset, y_offset))
                    right_height = img.size[1]
                    y_offset += (max(left_height, right_height) + img_space)

                progress = (idx + 1) / len(images) * 100 # calculate progress percentage
                p_var.set(progress)
                progress_bar.update()
        

        # Reset progress var
        p_var.set(0)

        # create image
        file_name = txt_name.get() + "." + img_format
        dest_path = os.path.join(txt_dest_path.get(), file_name)
        result_img.save(dest_path)
        msgbox.showinfo("Alert", "Your work has been saved.")
    except Exception as err: 
        msgbox.showerror("Error", err)

# start button
def start():

    # Throw error message when image files are not added 
    if list_file.size() == 0:
        msgbox.showwarning("Warning", "Please select image files")
        return

    # Throw error when no saving path has been given
    if len(txt_dest_path.get()) == 0:
        msgbox.showwarning("Warning", "Please choose the saving path")
        return

    # Throw error when no name is given
    if len(txt_name.get()) == 0:
        msgbox.showwarning("Warning", "Please type in name")
        return

    # else combine images
    merge_image()

# file frame
file_frame = Frame(root)
file_frame.pack(fill="x", padx=5, pady=5) 

btn_add_file = Button(file_frame, padx=5, pady=5, width=12, text="Add File", command=add_file)
btn_add_file.pack(side="left")

btn_del_file = Button(file_frame, padx=5, pady=5, width=12, text="Remove File", command=del_file)
btn_del_file.pack(side="right")

# list frame
list_frame = Frame(root)
list_frame.pack(fill="both", padx=5, pady=5)

scrollbar = Scrollbar(list_frame)
scrollbar.pack(side="right", fill="y")

list_file = Listbox(list_frame, selectmode="extended", height=15, yscrollcommand=scrollbar.set)
list_file.pack(side="left", fill="both", expand=True)
scrollbar.config(command=list_file.yview)

# saving path frame
path_frame = LabelFrame(root, text="Saving Path")
path_frame.pack(fill="x", padx=5, pady=5, ipady=5)

txt_dest_path = Entry(path_frame)
txt_dest_path.pack(side="left", fill="x", expand=True, padx=5, pady=5, ipady=4) 

btn_dest_path = Button(path_frame, text="Find Path", width=10, command=browse_dest_path)
btn_dest_path.pack(side="right", padx=5, pady=5)

# saving name frame
name_frame = LabelFrame(root, text="Image Name")
name_frame.pack(fill="x", padx=5, pady=5, ipady=5)

txt_name = Entry(name_frame)
txt_name.insert(0, "Untitled")
txt_name.pack(fill="x", expand=True ,padx=5, pady=5, ipady=4)

# option frame
frame_option = LabelFrame(root, text="options")
frame_option.pack(padx=5, pady=5, ipady=5)

# option 1 Width
lbl_width = Label(frame_option, text="Width", width=8)
lbl_width.pack(side="left", padx=5, pady=5)

opt_width = ["Same size", "1024", "800", "640"]
cmb_width = ttk.Combobox(frame_option, state="readonly", values=opt_width, width=10)
cmb_width.current(0) # set default to be "Same size"
cmb_width.pack(side="left", padx=5, pady=5)

# option 2 image spacing
lbl_space = Label(frame_option, text="Spacing", width=8)
lbl_space.pack(side="left", padx=5, pady=5)

opt_space = ["No space", "small", "medium", "large"]
cmb_space = ttk.Combobox(frame_option, state="readonly", values=opt_space, width=10)
cmb_space.current(0) # set default to be "No space"
cmb_space.pack(side="left", padx=5, pady=5)

# option 3 file format
lbl_format = Label(frame_option, text="Format", width=8)
lbl_format.pack(side="left", padx=5, pady=5)

opt_format = ["PNG", "JPG", "BMP"]
cmb_format = ttk.Combobox(frame_option, state="readonly", values=opt_format, width=10)
cmb_format.current(0) # set default to be "PNG"
cmb_format.pack(side="left", padx=5, pady=5)

# option 4 image type
lbl_type = Label(frame_option, text="Type", width=8)
lbl_type.pack(side="left", padx=5, pady=5)

opt_type = ["Slide","Film", "Cartoon"]
cmb_type = ttk.Combobox(frame_option, state="readonly", values=opt_type, width=10)
cmb_type.current(0)
cmb_type.pack(side="left", padx=5, pady=5)


# Progress Bar
frame_progress = LabelFrame(root, text="Progress")
frame_progress.pack(fill="x", padx=5, pady=5, ipady=5)

p_var = DoubleVar()
progress_bar = ttk.Progressbar(frame_progress, maximum=100, variable=p_var)
progress_bar.pack(fill="x", padx=5, pady=5)

# Run frame
frame_run = Frame(root)
frame_run.pack(fill="x", padx=5, pady=5)

btn_close = Button(frame_run, padx=5, pady=5, text="Close", width=12, command=root.quit)
btn_close.pack(side="right", padx=5, pady=5)

btn_start = Button(frame_run, padx=5, pady=5, text="Run", width=12, command=start)
btn_start.pack(side="right", padx=5, pady=5)

root.resizable(False, False)
root.mainloop()