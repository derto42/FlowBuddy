from PIL import Image
import math
import os
import random
import tkinter as tk
from tkinter import filedialog
import svgwrite
import tempfile
import shutil

# Create a Tkinter root window to open the file dialog
root = tk.Tk()
root.withdraw()

# Prompt the user to select input images
filetypes = [("Image files", "*.png;*.jpeg;*.jpg;*.svg")]
input_paths = filedialog.askopenfilenames(title="Select input images", filetypes=filetypes)

# Prompt the user to select the output location and filename
output_path = filedialog.asksaveasfilename(title="Select output location and filename", filetypes=[("PNG files", "*.png"), ("SVG files", "*.svg")], defaultextension=".png")

# Group the input paths by file type
input_paths_by_type = {}
for path in input_paths:
    _, ext = os.path.splitext(path)
    if ext in input_paths_by_type:
        input_paths_by_type[ext].append(path)
    else:
        input_paths_by_type[ext] = [path]

# Set the dimensions of the logos (assumed to be square)
logo_size = 512

# Set the margin between the logos
margin = 10

# Calculate the number of rows and columns needed for the PNG/JPEG images
png_jpg_paths = input_paths_by_type.get('.png', []) + input_paths_by_type.get('.jpg', []) + input_paths_by_type.get('.jpeg', [])
num_logos = len(png_jpg_paths)
side_length = math.ceil(math.sqrt(num_logos))
num_rows = math.ceil(num_logos / side_length)
num_cols = side_length

# Calculate the size of the final image for the PNG/JPEG images
img_size = logo_size * num_cols + margin * (num_cols + 1), logo_size * num_rows + margin * (num_rows + 1)
final_img = Image.new("RGB", img_size, (255, 255, 255))

# Loop through each PNG/JPEG logo and add it to the final image
for i, path in enumerate(png_jpg_paths):
    row = i // num_cols
    col = i % num_cols
    x_offset = margin + (col * (logo_size + margin))
    y_offset = margin + (row * (logo_size + margin))
    logo_img = Image.open(path)
    logo_img = logo_img.resize((logo_size, logo_size))
    final_img.paste(logo_img, (x_offset, y_offset))

# Save the final PNG/JPEG image to the specified output location
if output_path.endswith('.png'):
    final_img.save(output_path)

    # If there are SVG images, create a separate SVG image
    svg_paths = input_paths_by_type.get('.svg', [])
    if svg_paths:
        # Create the SVG image using svgwrite
        dwg = svgwrite.Drawing(filename=os.path.splitext(output_path)[0] + '.svg', size=img_size)
        for i, path in enumerate(svg_paths):
            x = margin + ((i % num_cols) * (logo_size + margin))
            y = margin + ((i // num_cols) * (logo_size + margin))
            svg_elem = svgwrite.image.Image(path, size=(logo_size, logo_size), insert=(x, y))
            dwg.add(svg_elem)
        dwg.save()

# If there are only SVG images, save the SVG file to the specified output location
elif output_path.endswith('.svg'):
    svg_paths = input_paths_by_type.get('.svg', [])
    if svg_paths:
        # Create the SVG image using svgwrite
        dwg = svgwrite.Drawing(filename=output_path, size=img_size)
        for i, path in enumerate(svg_paths):
            x = margin + ((i % num_cols) * (logo_size + margin))
            y = margin + ((i // num_cols) * (logo_size + margin))
            svg_elem = svgwrite.image.Image(path, size=(logo_size, logo_size), insert=(x, y))
            dwg.add(svg_elem)
        dwg.save()

# Print a message indicating where the final image(s) were saved
if svg_paths:
    print(f"Final images saved to {output_path} and {os.path.splitext(output_path)[0]}.svg")
else:
    print(f"Final image saved to {output_path}")


