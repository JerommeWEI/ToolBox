import os
import re
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
    # Example usage
    # input_folder = r"E:\AA_repository\OneDrive - Unispectral Qingdao Microelectronics Co. LTD\01_研发\01-开发相关\10-计算光谱\A01-script\01-sample code\fpi_cs_sim\20260203145236"  # Replace with your folder path
    # input_folder = r"E:\AA_repository\OneDrive - Unispectral Qingdao Microelectronics Co. LTD\01_研发\01-开发相关\10-计算光谱\A01-script\05-MEMS2Macleod\02-Analysis\P1s1_W9@30-48 (AA1175)\MEMS_曲线比较"
    # input_folder = r"E:\AA_repository\OneDrive - Unispectral Qingdao Microelectronics Co. LTD\01_研发\01-开发相关\10-计算光谱\A01-script\05-MEMS2Macleod\02-Analysis\P1s1_W9@30-48 (AA1175)\Same_voltage_Solomon_compare_MEMS"
    # input_folder = r"E:\AA_repository\OneDrive - Unispectral Qingdao Microelectronics Co. LTD\01_研发\00_应用场景\13-TFD 项目\04-应用demo\01-矽赫微\02-显微物镜+Monarch\01-test\cube_20260206_171943\png\Spectra"
    # input_folder = r"E:\AA_repository\OneDrive - Unispectral Qingdao Microelectronics Co. LTD\01_研发\01-开发相关\10-计算光谱\A01-script\01-sample code\fpi_cs_sim\20260226152043"
    # input_folder = r"E:\AA_repository\OneDrive - Unispectral Qingdao Microelectronics Co. LTD\01_研发\01-开发相关\10-计算光谱\A01-script\01-sample code\fpi_cs_sim\20260302134651"
    input_folder = r"F:\05-Jerome Studios\Coating Design\Simulate_Output\spectral-calculation\20260512_181502-202605121644-U450-MEMS-Metal-Coating-Ag-J08-angular\FWHM=9"
    output_gif = os.path.join(input_folder,"output.gif")  # Replace with desired output path
    frame_duration = 1000  # Duration in milliseconds for each frame
    sort_ascending = True  # Set to False for descending order

    create_gif(input_folder, output_gif, frame_duration, sort_ascending)