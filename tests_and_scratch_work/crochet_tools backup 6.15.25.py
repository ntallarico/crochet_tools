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

from os import path, mkdir
import customtkinter as ctk
from tkinter import filedialog
from PIL import Image, ImageTk, ImageEnhance
from tkinter import messagebox
from openpyxl import styles
from openpyxl import Workbook
from openpyxl import load_workbook
from string import ascii_uppercase

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
        update_image_display(image_lvl0, image_lvl0_label)
        update_all_levels()

def reset_sliders():
    if image_lvl0 == None: return
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

# IN: PIL image
# OUT: 2D array with each value containing a rgb tuple
# OUT: 2D array with each value containing an int representing the color map value
def get_colors(image):
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

def get_font_color(cell_color):
	r = cell_color[0]
	g = cell_color[1]
	b = cell_color[2]
	luma = 0.299*r + 0.587*g + 0.114*b
	luma = luma / 255.0 # Account for rgb scale being 0-255 instead of 0-1.0
	if luma > 0.7: # Cell is very bright
		return "00000000" # Black
	else: # Cell is very dark
		return "FFFFFFFF" # White
      
def rgb_to_hex(color):
	# Note: Have color[3] for alpha for future expansion.
	return '%02x%02x%02x' % (color[0], color[1], color[2])

def get_cell_name(x, y):
	col = get_column(x + 1)
	row = get_row(y)

	return col + row

def get_column(num):
	def divmod_excel(n):
		a, b = divmod(n, 26)
		if b == 0:
			return a - 1, b + 26
		return a, b

	chars = []
	while num > 0:
		num, d = divmod_excel(num)
		chars.append(ascii_uppercase[d - 1])
	return ''.join(reversed(chars)).upper()

def get_row(y):
	return str(y + 1)

def get_used_color_palette(colors, color_map):
	used_colors = []
	used_map = []

	## Get list of used colors
	for x in range(0, len(colors)):
		for y in range(0, len(colors[x])):
			color = colors[x][y]
			color_map_value = color_map[x][y]
			if color not in used_colors:
				used_colors.append(color)
				used_map.append(color_map_value)

	return used_colors, used_map

def check_output_directory():
	if not path.isdir(csv_output_directory):
		mkdir(csv_output_directory)

# DESC: Save the workbook as an excel file
# IN: workbook, file path
# OUT: boolean indicating success
def save_wb(wb, output_file_path):
	try:
		wb.save(output_file_path)
		return True
	except Exception as e:
		return False
	
def get_file_name_from_path(file_path):
	return file_path.split("/")[-1]

def export_image_as_excel_pattern(csv_output_directory, include_pixel_numbers = False):
	column_size = 2.8 # this number is about 20 pixels, same as the default height
	cell_fill_type = 'solid'
	legend_buffer = 1
	output_file_name = "output"

	image_to_export = image_lvl3

	if image_to_export == None: return

    # get color grid and map from final image
	colors, color_map = get_colors(image_to_export)

	# create worksheet
	wb = Workbook()
	ws = wb.create_sheet(output_file_name, index=0)

	# fill worksheet with image
	for x in range(0, len(colors)):
		print("Converting - " +  str(x) + "/" + str(len(colors)) + " to Excel")
		#set_progress(x + 1, len(colors))
		for y in range(0, len(colors[x])):
			cell_color = rgb_to_hex(colors[x][y])
			font_color = get_font_color(colors[x][y])
			cell_symbol = color_map[x][y]
			cell_alignment = styles.Alignment(horizontal='center')
			cell_fill = styles.PatternFill(fill_type=cell_fill_type, start_color=cell_color, end_color=cell_color)
			cell_border = styles.Border(left=styles.Side(style='thin'), right=styles.Side(style='thin'), top=styles.Side(style='thin'), bottom=styles.Side(style='thin'))
			cell_font = styles.Font(name='Calibri', bold=False, italic=False, color=font_color)
			cell_name = get_cell_name(x, y)
			ws[cell_name].alignment  = cell_alignment
			if include_pixel_numbers: ws[cell_name].value = cell_symbol
			ws[cell_name].fill = cell_fill
			ws[cell_name].border = cell_border
			ws[cell_name].font = cell_font
		ws.column_dimensions[get_column(x + 1)].width = column_size # set column size
	print("Conversion complete")

	# add legend
	used_colors, used_map = get_used_color_palette(colors, color_map)
	width = len(colors)
	for c in range(-1, len(used_colors)):
		if(c == -1):
			ws[get_cell_name(width + legend_buffer, 0)].value = "Color"
			ws[get_cell_name(width + legend_buffer + 1, 0)].value = "HEX"
			ws[get_cell_name(width + legend_buffer + 2, 0)].value = "Red Value"
			ws[get_cell_name(width + legend_buffer + 3, 0)].value = "Green Value"
			ws[get_cell_name(width + legend_buffer + 4, 0)].value = "Blue Value"
			continue		
		color_rgb = used_colors[c]
		color_symbol = used_map[c]
		color_hex = rgb_to_hex(color_rgb)
		font_color = get_font_color(color_rgb)
		cell_font = styles.Font(color=font_color)
		ws[get_cell_name(width + legend_buffer, c + 1)].fill = styles.PatternFill(fill_type=cell_fill_type, start_color=color_hex, end_color=color_hex)
		if include_pixel_numbers: ws[get_cell_name(width + legend_buffer, c + 1)].value = str(color_symbol)
		ws[get_cell_name(width + legend_buffer, c + 1)].font = cell_font
		ws[get_cell_name(width + legend_buffer + 1, c + 1)].value = str(color_hex)
		ws[get_cell_name(width + legend_buffer + 2, c + 1)].value = str(color_rgb[0])
		ws[get_cell_name(width + legend_buffer + 3, c + 1)].value = str(color_rgb[1])
		ws[get_cell_name(width + legend_buffer + 4, c + 1)].value = str(color_rgb[2])

	# save the file
	check_output_directory()
	output_directory = csv_output_directory
	output_file_path = output_directory + "\\" + output_file_name + ".xlsx"
	save_success = save_wb(wb, output_file_path)
	if save_success:
		print(output_file_name + " created")
		messagebox.showinfo("Success", output_file_name + " created in folder '" + output_directory + "'")
	else:
		print(output_file_name + " save failed")
		messagebox.showinfo(error_box_header, "Error: Save failed. Make sure file '" + get_file_name_from_path(output_file_name) + "' is not already open on computer.")
	#set_progress(0, 1)
	#enable_gui_buttons()









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
image_lvl0_label = ctk.CTkLabel(image_lvl0_frame, text="")
image_lvl0_label.place(relx=0.5, rely=0.5, anchor="center")

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

export_image_as_pattern_button = ctk.CTkButton(app, text="Export Pattern to Excel", command = lambda: export_image_as_excel_pattern(csv_output_directory, include_pixel_numbers = include_cells_var.get()))
export_image_as_pattern_button.pack(pady=5)

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
checkbox = ctk.CTkCheckBox(app, text="Include cell numbers", variable=include_cells_var) #, command = lambda: update_all_levels()
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