import tkinter as tk
from tkinter import filedialog
from fontTools.ttLib.woff2 import compress
import os

# create a Tkinter root window (it will not be displayed)
root = tk.Tk()
root.withdraw()

# open a file dialog to select the input font file
input_file_path = filedialog.askopenfilename(
    title="Select the input font file",
    filetypes=[("Font files", "*.otf *.ttf"), ("All files", "*.*")]
)

if not input_file_path:
    print("No input file selected. Exiting...")
    exit()

# determine the output file path based on the input file path
input_file_dir, input_file_name = os.path.split(input_file_path)
input_file_name_base, input_file_extension = os.path.splitext(input_file_name)
output_file_path = os.path.join(input_file_dir, input_file_name_base + ".woff2")

# compress the font
compress(input_file_path, output_file_path)

print(f"Font compressed and saved as {output_file_path}")
