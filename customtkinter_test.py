import customtkinter as ctk
from tkinter import filedialog
from PIL import Image, ImageTk, ImageEnhance

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

# Create fixed-size frames for images
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

    # Resize and (optionally) quantize
    img = original.copy().resize((width, height))

    if num_colors < 256:
        img = img.convert("P", palette=Image.ADAPTIVE, colors=num_colors).convert("RGB")

    processed_image = img
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
checkbox = ctk.CTkCheckBox(app, text="Include Cell Numbers?", variable=include_cells_var, command=lambda: apply_live_filters())
checkbox.pack()

# ---------- Launch ----------
app.mainloop()


