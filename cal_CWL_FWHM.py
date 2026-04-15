import tkinter as tk
from tkinter import filedialog
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

def select_csv_file():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(
        title="选择CSV文件",
        filetypes=[("CSV文件", "*.csv"), ("所有文件", "*")]
    )
    return file_path

def read_csv_data(file_path):
    try:
        df = pd.read_csv(file_path)
        return df
    except Exception as e:
        print(f"读取文件失败: {e}")
        return None

def process_data(df):
    if df is None:
        return []
    
    data_sets = []
    num_columns = len(df.columns)
    
    for i in range(0, num_columns, 2):
        if i + 1 < num_columns:
            wavelength = df.iloc[:, i].values
            intensity = df.iloc[:, i + 1].values
            data_sets.append((wavelength, intensity))
    
    return data_sets

def calculate_cwl(wavelength, intensity):
    numerator = np.sum(wavelength * intensity)
    denominator = np.sum(intensity)
    if denominator == 0:
        return 0
    return numerator / denominator

def calculate_fwhm(wavelength, intensity):
    max_intensity = np.max(intensity)
    half_max = max_intensity / 2
    
    indices = np.where(intensity >= half_max)[0]
    if len(indices) < 2:
        return 0
    
    left_idx = indices[0]
    right_idx = indices[-1]
    
    fwhm = wavelength[right_idx] - wavelength[left_idx]
    return fwhm, wavelength[left_idx], wavelength[right_idx]

def plot_spectra(data_sets):
    plt.figure(figsize=(12, 8))
    
    for i, (wavelength, intensity) in enumerate(data_sets):
        plt.plot(wavelength, intensity, label=f"数据集 {i+1}")
        
        cwl = calculate_cwl(wavelength, intensity)
        fwhm, fwhm_left, fwhm_right = calculate_fwhm(wavelength, intensity)
        
        plt.axvline(x=cwl, color='r', linestyle='--', linewidth=2, label=f"CWL: {cwl:.2f} nm")
        plt.axvspan(fwhm_left, fwhm_right, alpha=0.2, color='gray', label=f"FWHM: {fwhm:.2f} nm")
        
        plt.text(
            0.05, 0.9 - i*0.1,
            f"数据集 {i+1}: CWL = {cwl:.2f} nm, FWHM = {fwhm:.2f} nm",
            transform=plt.gca().transAxes,
            fontsize=12,
            bbox=dict(facecolor='white', alpha=0.8)
        )
    
    plt.xlabel('波长 (nm)')
    plt.ylabel('强度')
    plt.title('光谱分析')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def main():
    file_path = select_csv_file()
    if not file_path:
        print("未选择文件")
        return
    
    df = read_csv_data(file_path)
    if df is None:
        return
    
    data_sets = process_data(df)
    if not data_sets:
        print("数据格式不正确")
        return
    
    plot_spectra(data_sets)

if __name__ == "__main__":
    os.system('cls' if os.name == 'nt' else 'clear') 
    plt.rcParams['font.sans-serif'] = (['SimHei', 'Microsoft YaHei', 'SimSun'])
    plt.rcParams['axes.unicode_minus'] = False  
    main()
