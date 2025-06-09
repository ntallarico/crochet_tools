"""
Copyright (c) 2025 Nicholas Tallarico

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

"""

#################################
#       Crochet Tools              
#            v1.0             
#################################

# ---------- Import Libraries ----------

import customtkinter as ctk
from tkinter import filedialog
from PIL import Image, ImageTk, ImageEnhance
from tkinter import messagebox

# ---------- Global Variables ----------

# Aesthetics
error_box_header = "Error"
window_title = "Crochet Pattern Image Editor"
color_base = "#217346"
window_width = 1600
window_height = 900

# Functionality
csv_output_directory = "input_output"
max_color_input = 32
min_color_input = 1
max_dimension_input = 500
min_dimension_input = 1

# ---------- Global State ----------

image_lvl0 = None # original
image_lvl1 = None
image_lvl2 = None
image_lvl3 = None








# ---------- Functions ----------

# def apply_settings():
#     global image_lvl1
#     if image_lvl0 is None:
#         return

#     try:
#         width = int(width_entry.get())
#         height = int(height_entry.get())
#         num_colors = int(colors_entry.get())
#     except ValueError:
#         print("Invalid width/height/colors")
#         return

#     # create copy of original image
#     image = image_lvl0.copy()

#     # resize
#     image_pixelated = image.resize((width, height))

#     # quantize
#     if num_colors <= 32:
#         pixel_image = image_pixelated.convert("P", palette=Image.ADAPTIVE, colors=num_colors, dither=0).convert("RGB")

#     # update global image_lvl1 var to new processed image
#     image_lvl1 = pixel_image

#     # apply live filters like sliders
#     apply_color_sliders()



def resize_for_display(image, max_size=500):
    if image == None: return
    # Resize image maintaining aspect ratio to fit within max_size x max_size
    ratio = min(max_size/image.width, max_size/image.height)
    new_size = (int(image.width * ratio), int(image.height * ratio))
    return image.resize(new_size, Image.Resampling.NEAREST)

def select_file():
    global image_lvl0, image_lvl1, image_lvl2, image_lvl3
    filepath = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.png *.jpeg")])
    if filepath:
        image_lvl0 = Image.open(filepath).convert("RGB")
        # Display original image
        display_image_lvl0 = resize_for_display(image_lvl0)
        image_lvl0_img_tk = ImageTk.PhotoImage(display_image_lvl0)
        image_lvl0_image_label.configure(image=image_lvl0_img_tk)
        image_lvl0_image_label.image = image_lvl0_img_tk
        
        image_lvl1 = image_lvl0.copy()
        image_lvl2 = image_lvl0.copy()
        image_lvl3 = image_lvl0.copy()

        update_all_levels()

def reset_sliders():
    brightness_slider.set(slider_defaults["brightness"])
    contrast_slider.set(slider_defaults["contrast"])
    saturation_slider.set(slider_defaults["saturation"])
    #apply_color_sliders()
    update_all_levels()


# updates display for a given image. does not update it in memory
def update_image_display(image, image_label):
    if image == None: return

    display_img = resize_for_display(image)
    img_tk_new = ImageTk.PhotoImage(display_img)
    image_label.configure(image=img_tk_new)
    image_label.image = img_tk_new

def process_lvl0_to_lvl1():
    global image_lvl0, image_lvl1, image_lvl1_label
    new_image = image_lvl0.copy()
    # apply color sliders
    new_image = apply_color_sliders(new_image)
    # update image_lvl1 in memory
    image_lvl1 = new_image
    # update image_lvl1 on the UI display
    update_image_display(image_lvl1, image_lvl1_label)

def process_lvl1_to_lvl2():
    global image_lvl1, image_lvl2, image_lvl2_label

    if not dimensions_valid(width_entry.get(), height_entry.get()):
        return None, None
    if not num_colors_valid(colors_entry.get()):
        return None, None
    
    try:
        width = int(width_entry.get())
        height = int(height_entry.get())
        num_colors = int(colors_entry.get())
    except ValueError:
        print("Invalid width/height/colors")
        return
    
    new_image = image_lvl1.copy()
    # pixelate image (resize)
    new_image = pixelate_image(new_image, width, height)
    # quantize (reduce color palette)
    new_image = quantize_image(new_image, num_colors)
    # update image_lvl2 in memory
    image_lvl2 = new_image
    # update image_lvl2 on the UI display
    update_image_display(image_lvl2, image_lvl2_label)

def process_lvl2_to_lvl3():
    global image_lvl2, image_lvl3
    # curently does nothing
    new_image = image_lvl2.copy()
    # update image_lvl3 in memory
    image_lvl3 = new_image
    # update image_lvl3 on the UI display
    #update_image_display(image_lvl3, image_lvl3_label)

def update_all_levels():
    process_lvl0_to_lvl1()
    process_lvl1_to_lvl2()
    process_lvl2_to_lvl3()

def apply_color_sliders(image):
    if image == None: return

    brightness = brightness_slider.get()
    contrast = contrast_slider.get()
    saturation = saturation_slider.get()

    img = image.copy()
    img = ImageEnhance.Brightness(img).enhance(brightness)
    img = ImageEnhance.Contrast(img).enhance(contrast)
    img = ImageEnhance.Color(img).enhance(saturation)

    return img

def pixelate_image(image, width, height):
    if image == None: return
    # TODO: maintain aspect ratio?
    image_pixelated = image.resize((width, height))
    return image_pixelated

def quantize_image(image, num_colors):
    if image == None: return
    if num_colors <= 32:
        quantized_image = image.convert("P", palette=Image.ADAPTIVE, colors=num_colors, dither=0).convert("RGB")
    return quantized_image

# IN: PIL image
# OUT: 2D array with each value containing a rgb tuple
# OUT: 2D array with each value containing an int representing the color map value
# Notes: this takes each pixel and turns it to an rgb tuple
#   we want to reduce the size of the image so that we have one pixel per what we want to be a pixel in this grid
def convert_image_to_rgb_grid(image):
    if image == None: return
    used_colors = []
    colors = []
    color_map = []

    for x in range(0, image.size[0]): # Left column to right column
        column_colors = []
        column_map = []
        for y in range(0, image.size[1]): # Top row to bottom row
            pixel_color = image.getpixel((x,y))
            if(pixel_color not in used_colors):
                used_colors.append(pixel_color)
            pixel_map = used_colors.index(pixel_color)

            column_colors.append(pixel_color)
            column_map.append(pixel_map)
        colors.append(column_colors)
        color_map.append(column_map)

    return colors, color_map

def dimensions_valid(width, height):
	## Check if height and width are numbers
	if not width.isnumeric():
		print("Error: Width contains non-numeric characters.")
		messagebox.showinfo(error_box_header, "Error: Width contains non-numeric characters.")
		return False
	if not height.isnumeric():
		print("Error: Height contains non-numeric characters.")
		messagebox.showinfo(error_box_header, "Error: Height contains non-numeric characters.")
		return False
	## Check if height in width are within the desired range
	width = int(width)
	height = int(height)
	if width < min_dimension_input or width > max_dimension_input:
		print("Error: Width '" + str(width) + "' not valid. Must be between " + str(min_dimension_input) + " and " + str(max_dimension_input) + ".")
		messagebox.showinfo(error_box_header, "Error: Width '" + str(width) + "' not valid. Must be between " + str(min_dimension_input) + " and " + str(max_dimension_input) + ".")
		return False
	if height < min_dimension_input or height > max_dimension_input:
		print("Error: Height '" + str(height) + "' not valid. Must be between " + str(min_dimension_input) + " and " + str(max_dimension_input) + ".")
		messagebox.showinfo(error_box_header, "Error: Height '" + str(height) + "' not valid. Must be " + str(min_dimension_input) + " and " + str(max_dimension_input) + ".")
		return False
	return True

def num_colors_valid(num_colors):
	## Check if number is numeric
	if not num_colors.isnumeric():
		print("Error: Number of Colors contains non-numeric characters.")
		messagebox.showinfo(error_box_header, "Error: Number of Colors contains non-numeric characters.")
		return False
	## Check if in desired range
	num_colors = int(num_colors)
	if num_colors < min_color_input or num_colors > max_color_input:
		print("Error: Number of Colors '" + str(num_colors) + "' not valid. Must be between "  + str(min_color_input) + " and " + str(max_color_input))
		messagebox.showinfo(error_box_header, "Error: Number of Colors '" + str(num_colors) + "' not valid. Must be between "  + str(min_color_input) + " and " + str(max_color_input))
		return False
	return True















# ---------- GUI Setup ----------

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.geometry(f"{window_width}x{window_height}")
app.title(window_title)

# ---------- UI Frames ----------

image_frame = ctk.CTkFrame(app)
image_frame.pack(pady=10)

control_frame = ctk.CTkFrame(app)
control_frame.pack(pady=10)

slider_frame = ctk.CTkFrame(control_frame)
slider_frame.grid(row=0, column=0, padx=10)

entry_frame = ctk.CTkFrame(control_frame)
entry_frame.grid(row=0, column=1, padx=10)

# ---------- Image Display ----------

# image_lvl0 (original) frame for image
image_lvl0_frame = ctk.CTkFrame(image_frame, width=500, height=500)
image_lvl0_frame.grid(row=1, column=0, padx=10)
image_lvl0_frame.grid_propagate(False)
# image_lvl0 (original) frame text label
image_lvl0_label = ctk.CTkLabel(image_frame, text="Original")
image_lvl0_label.grid(row=0, column=0, padx=10)
# image_lvl0 (original) image label
image_lvl0_image_label = ctk.CTkLabel(image_lvl0_frame, text="")
image_lvl0_image_label.place(relx=0.5, rely=0.5, anchor="center")

# image_lvl1 frame for image
image_lvl1_frame = ctk.CTkFrame(image_frame, width=500, height=500)
image_lvl1_frame.grid(row=1, column=1, padx=10)
image_lvl1_frame.grid_propagate(False)
# image_lvl1 frame text label
image_lvl1_label = ctk.CTkLabel(image_frame, text="Process Level 1")
image_lvl1_label.grid(row=0, column=1, padx=10)
# image_lvl1 image label
image_lvl1_label = ctk.CTkLabel(image_lvl1_frame, text="")
image_lvl1_label.place(relx=0.5, rely=0.5, anchor="center")

# image_lvl2 frame for image
image_lvl2_frame = ctk.CTkFrame(image_frame, width=500, height=500)
image_lvl2_frame.grid(row=1, column=2, padx=10)
image_lvl2_frame.grid_propagate(False)
# image_lvl2 frame text label
image_lvl2_label = ctk.CTkLabel(image_frame, text="Process Level 2")
image_lvl2_label.grid(row=0, column=2, padx=10)
# image_lvl2 image label
image_lvl2_label = ctk.CTkLabel(image_lvl2_frame, text="")
image_lvl2_label.place(relx=0.5, rely=0.5, anchor="center")

# ---------- Buttons ----------

reset_button = ctk.CTkButton(app, text="Reset Sliders", command = lambda: reset_sliders())
reset_button.pack(pady=5)

update_button = ctk.CTkButton(app, text="Update", command = lambda: update_all_levels())
update_button.pack(pady=5)

file_button = ctk.CTkButton(app, text="Select Image File", command = lambda: select_file())
file_button.pack(pady=5)

# ---------- Sliders ----------

slider_defaults = {"brightness": 1.0, "contrast": 1.0, "saturation": 1.0}

def create_slider(label_text, var_name, row):
    label = ctk.CTkLabel(slider_frame, text=label_text)
    label.grid(row=row, column=0, sticky="w")
    slider = ctk.CTkSlider(
        slider_frame,
        from_=0.2,
        to=2.0,
        number_of_steps=100,
        #command=lambda v: apply_color_sliders(),
        command = lambda v: update_all_levels(),
    )
    slider.set(slider_defaults[var_name])
    slider.grid(row=row, column=1, pady=5, padx=5)
    return slider

brightness_slider = create_slider("Brightness", "brightness", 0)
contrast_slider   = create_slider("Contrast", "contrast", 1)
saturation_slider = create_slider("Saturation", "saturation", 2)

# ---------- Entry Boxes ----------

def create_entry(label_text, default_text, row):
    lbl = ctk.CTkLabel(entry_frame, text=label_text)
    lbl.grid(row=row, column=0, sticky="w")
    entry = ctk.CTkEntry(entry_frame)
    entry.insert(0, default_text)
    entry.grid(row=row, column=1, pady=5, padx=5)
    entry.bind('<Return>', lambda e: update_all_levels()) # update images when user presses Enter
    entry.bind('<FocusOut>', lambda e: update_all_levels()) # update images when user leaves text box
    return entry

width_entry  = create_entry("Width", "75", 0)
height_entry = create_entry("Height", "75", 1)
colors_entry = create_entry("Number of Colors", "3", 2)

# ---------- Checkbox ----------

include_cells_var = ctk.BooleanVar()
checkbox = ctk.CTkCheckBox(app, text="Include cell numbers", variable=include_cells_var, command = lambda: update_all_levels())
checkbox.pack()

# ---------- Launch ----------
app.mainloop()


'''

globally store
    - original image
    - image lvl1
    - image lvl2
    - image lvl3
    - image lvl4

level update functions
    - process from lvl1 to lvl2
    - process from lvl2 to lvl3
    - process from lvl3 to lvl4
    - update all levels (in order)

image processing funcitons
    - slider color update
    - blur
    - pixelate
    - resize

- level update functions call the image processing functions. that will make it easier to switch around their functionality as desired

- when file is loaded, run the "update all levels" function
- when any button is pressed or value is updated, run "update all levels" function. lets have it run this way until performance tanks lol




'''