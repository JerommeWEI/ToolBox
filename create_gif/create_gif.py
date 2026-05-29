import os
import re
import sys
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
from PIL import Image


def create_gif(input_folder, output_gif, duration=500, ascending=True):
    """
    Combine PNG images from a folder into an animated GIF, sorted by CRA value.

    Args:
        input_folder (str): Path to folder containing PNG images
        output_gif (str): Path to save the output GIF
        duration (int): Duration for each frame in milliseconds
        ascending (bool): True for ascending order, False for descending
    """
    # Get all PNG files and extract values for sorting
    image_files = []
    for filename in os.listdir(input_folder):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            # Extract number from filename using regex - support multiple formats
            match = None
            # Try different patterns to extract numeric values
            patterns = [
                r'CRA = (-?\d+\.\d+)',    # Format: CRA = 123.45
                r'CRA=(-?\d+\.\d+)',      # Format: CRA=123.45
                r'air = (-?\d+)',           # Format: air = 123
                r'_(\d+)nm',               # Format: _123nm (wavelength)
                r'_(\d+)\.\d+nm',         # Format: _123.45nm (wavelength with decimal)
                r'(\d+)nm_',               # Format: 123nm_ (wavelength at start)
                r'(\d+)\.\d+nm_',         # Format: 123.45nm_ (wavelength with decimal at start)
                r'(\d+)\.\d+',            # Any decimal number
                r'(\d+)',                   # Any integer number
                r'comparison_(\d+)'         # Format: comparison_123 (comparison number)
            ]
            
            for pattern in patterns:
                match = re.search(pattern, filename)
                if match:
                    break
            
            if match:
                try:
                    sort_value = float(match.group(1))
                    image_files.append((sort_value, filename))
                except (ValueError, IndexError):
                    # If extraction fails, use filename as sort key
                    image_files.append((filename, filename))
            else:
                # No numeric pattern found, use filename as sort key
                image_files.append((filename, filename))

    if not image_files:
        print("No valid PNG/JPG images found in the folder!")
        return

    # Sort files based on CRA value
    image_files.sort(reverse=not ascending)

    # Load images in sorted order
    images = []
    for _, filename in image_files:
        file_path = os.path.join(input_folder, filename)
        img = Image.open(file_path)
        # Convert to RGB if image is in RGBA mode
        if img.mode == 'RGBA':
            img = img.convert('RGB')
        images.append(img)

    # Save the first image as GIF with the rest as frames
    images[0].save(
        output_gif,
        save_all=True,
        append_images=images[1:],
        duration=duration,
        loop=0  # 0 means loop forever
    )
    print(f"GIF created successfully: {output_gif}")


if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()

    input_folder = filedialog.askdirectory(title="选择包含图片的文件夹")
    if not input_folder:
        messagebox.showwarning("提示", "未选择文件夹，程序退出")
        sys.exit()

    duration = simpledialog.askinteger(
        "帧间隔", "请输入每帧持续时间（毫秒）：", initialvalue=500, minvalue=50, maxvalue=10000
    )
    if duration is None:
        duration = 500

    ascending = messagebox.askyesno("排序方式", "按数值升序排列？\n\n是 = 升序（小→大）\n否 = 降序（大→小）")

    output_gif = os.path.join(input_folder, "output.gif")
    create_gif(input_folder, output_gif, duration, ascending)
    messagebox.showinfo("完成", f"GIF 已保存至：\n{output_gif}")