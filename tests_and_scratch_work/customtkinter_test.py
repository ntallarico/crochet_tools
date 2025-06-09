import customtkinter as ctk
from tkinter import filedialog
from PIL import Image, ImageTk, ImageEnhance
from tkinter import messagebox


# ---------- Global variables ----------

# Aesthetics
error_box_header = "Error"
window_width = 30
window_title = "Pattern Image Editor"
color_base = "#217346"

# Functionality
csv_output_directory = "input_output"
max_color_input = 32
min_color_input = 1
max_dimension_input = 500
min_dimension_input = 1

# ---------- Setup ----------
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.geometry("1500x1000")
app.title("Crochet Pattern Image Editor")

# ---------- Global State ----------
original = None  # Stores the original loaded image
processed_image = None  # Stores the resized + quantized version
img_tk = None     # For keeping reference to displayed image

# ---------- Image Display ----------
image_frame = ctk.CTkFrame(app)
image_frame.pack(pady=10)

original_frame = ctk.CTkFrame(image_frame, width=500, height=500)
original_frame.grid(row=1, column=0, padx=10)
original_frame.grid_propagate(False)  # Prevent frame from shrinking

original_label = ctk.CTkLabel(image_frame, text="Original")
original_label.grid(row=0, column=0, padx=10)

original_image_label = ctk.CTkLabel(original_frame, text="")
original_image_label.place(relx=0.5, rely=0.5, anchor="center")

processed_frame = ctk.CTkFrame(image_frame, width=500, height=500)
processed_frame.grid(row=1, column=1, padx=10)
processed_frame.grid_propagate(False)  # Prevent frame from shrinking

processed_label = ctk.CTkLabel(image_frame, text="Processed")
processed_label.grid(row=0, column=1, padx=10)

processed_image_label = ctk.CTkLabel(processed_frame, text="")
processed_image_label.place(relx=0.5, rely=0.5, anchor="center")

# ---------- UI Frames ----------
control_frame = ctk.CTkFrame(app)
control_frame.pack(pady=10)

slider_frame = ctk.CTkFrame(control_frame)
slider_frame.grid(row=0, column=0, padx=10)

entry_frame = ctk.CTkFrame(control_frame)
entry_frame.grid(row=0, column=1, padx=10)


# ---------- Processing Functions ----------
def apply_settings():
    global processed_image
    if original is None:
        return

    try:
        width = int(width_entry.get())
        height = int(height_entry.get())
        num_colors = int(colors_entry.get())
    except ValueError:
        print("Invalid width/height/colors")
        return

    # create copy of original image
    image = original.copy()

    # resize
    image_pixelated = image.resize((width, height))

    # quantize
    if num_colors <= 32:
        pixel_image = image_pixelated.convert("P", palette=Image.ADAPTIVE, colors=num_colors, dither=0).convert("RGB")

    # update global processed_image var to new processed image
    processed_image = pixel_image

    # apply live filters like sliders
    apply_live_filters()

def resize_for_display(img, max_size=500):
    """Resize image maintaining aspect ratio to fit within max_size x max_size"""
    ratio = min(max_size/img.width, max_size/img.height)
    new_size = (int(img.width * ratio), int(img.height * ratio))
    return img.resize(new_size, Image.Resampling.NEAREST)

def select_file():
    global original, processed_image, original_img_tk
    filepath = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.png *.jpeg")])
    if filepath:
        original = Image.open(filepath).convert("RGB")
        # Display original image
        display_original = resize_for_display(original)
        original_img_tk = ImageTk.PhotoImage(display_original)
        original_image_label.configure(image=original_img_tk)
        original_image_label.image = original_img_tk
        
        processed_image = original.copy()
        apply_settings()  # First resize
        reset_sliders()   # Then reset filters

def apply_live_filters():
    if processed_image is None:
        return

    brightness = brightness_slider.get()
    contrast = contrast_slider.get()
    saturation = saturation_slider.get()

    img = processed_image.copy()
    img = ImageEnhance.Brightness(img).enhance(brightness)
    img = ImageEnhance.Contrast(img).enhance(contrast)
    img = ImageEnhance.Color(img).enhance(saturation)

    if include_cells_var.get():
        # You could add drawing logic here
        pass

    # Resize for display while maintaining aspect ratio
    display_img = resize_for_display(img)
    img_tk_new = ImageTk.PhotoImage(display_img)
    processed_image_label.configure(image=img_tk_new)
    processed_image_label.image = img_tk_new

def reset_sliders():
    brightness_slider.set(slider_defaults["brightness"])
    contrast_slider.set(slider_defaults["contrast"])
    saturation_slider.set(slider_defaults["saturation"])
    apply_live_filters()



# plan
# currently, we have image processing happening in the apply_settings function.
# I think we should have image processing happening here, and then the "processed" image shows the rgb grid we have, possibly scaled up for visibility
# this will happen once the "update" button is pressed
# to do
    # we need a function that converts rgb grid to an image that tkinter can display, for purposes of showing in the UI
    # have the 'processed image' panel display from the rgb color grid output by this function
    # call this function in apply_settings()

def process_image(width, height, num_colors):
    # Check inputs for errors
    if not dimensions_valid(width, height):
        return None, None
    if not num_colors_valid(num_colors):
        return None, None

    # Init
    width = int(width)
    height = int(height)
    num_colors = int(num_colors)
       
    # create copy of original image
    image = original.copy()
    # pixelate image (resize)
    image = pixelate_image(image, width, height)
    # quantize (reduce color palette)
    image = quantize_image(image, num_colors)
    # convert to rgb color grid
    colors, color_map = convert_image_to_rgb_grid(image)
    # if use_dmc:
    # 	colors = convert_colors_to_dmc(colors, color_map, num_colors)

    return colors, color_map

def pixelate_image(image, width, height):
    image_pixelated = image.resize((width, height))
    return image_pixelated

def quantize_image(image, num_colors):
    if num_colors <= 32:
        quantized_image = image.convert("P", palette=Image.ADAPTIVE, colors=num_colors, dither=0).convert("RGB")
    return quantized_image

# IN: PIL image
# OUT: 2D array with each value containing a rgb tuple
# OUT: 2D array with each value containing an int representing the color map value
# Notes: this takes each pixel and turns it to an rgb tuple
#   we want to reduce the size of the image so that we have one pixel per what we want to be a pixel in this grid
def convert_image_to_rgb_grid(image):
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

def file_path_valid(file_path):
	## Check for empty path
	if file_path == "":
		print("Error: Path file path empty.")
		messagebox.showinfo(error_box_header, "Error: Path file path empty.")
		return False
	## Check file type
	file_extension = file_path[-5:].lower()
	if  ".jpg" not in file_extension.lower() and \
		".png" not in file_extension.lower() and \
		".jpeg" not in file_extension.lower() :
		print("Error: File must be type '.png' or '.jpg'")
		messagebox.showinfo(error_box_header, "Error: File must be type '.png' or '.jpg'")
		return False
	return True

# ---------- Buttons ----------
reset_button = ctk.CTkButton(app, text="Reset Sliders", command=reset_sliders)
reset_button.pack(pady=5)

update_button = ctk.CTkButton(app, text="Update (Apply Resize & Colors)", command=apply_settings)
update_button.pack(pady=5)

file_button = ctk.CTkButton(app, text="Select Image File", command=select_file)
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
        command=lambda v: apply_live_filters(),
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
    return entry

width_entry  = create_entry("Width", "75", 0)
height_entry = create_entry("Height", "75", 1)
colors_entry = create_entry("Number of Colors", "3", 2)

# ---------- Checkbox ----------
include_cells_var = ctk.BooleanVar()
checkbox = ctk.CTkCheckBox(app, text="Include cell numbers", variable=include_cells_var, command=lambda: apply_live_filters())
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

functions
    - process from lvl1 to lvl2
    - process from lvl2 to lvl3
    - process from lvl3 to lvl4
    - update all levels

- when file is loaded, run the "update all levels" function
- when any button is pressed or value is updated, run "update all levels" function. lets have it run this way until performance tanks lol




'''