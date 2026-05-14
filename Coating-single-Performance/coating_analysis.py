import os
import numpy as np
import matplotlib.pyplot as plt

def read_txt_file(filepath):
    data = []
    with open(filepath, 'r') as f:
        lines = f.readlines()
        for line in lines[1:]:
            parts = line.strip().split('\t')
            if len(parts) >= 2:
                wavelength = float(parts[0].strip())
                reflectance = float(parts[1].strip())
                data.append([wavelength, reflectance])
    return np.array(data)

def find_threshold_near_target(data, target_reflectance, target_wavelength):
    idx_50 = np.argmin(np.abs(data[:, 1] - target_reflectance))
    candidates_near_50 = data[np.abs(data[:, 1] - target_reflectance) < 1]
    if len(candidates_near_50) == 0:
        return data[idx_50, 0], data[idx_50, 1]
    idx = np.argmin(np.abs(candidates_near_50[:, 0] - target_wavelength))
    return candidates_near_50[idx, 0], candidates_near_50[idx, 1]

def analyze_roi(data, roi_start, roi_end, short_target, long_target):
    roi_mask = (data[:, 0] >= roi_start) & (data[:, 0] <= roi_end)
    roi_data = data[roi_mask]
    
    if len(roi_data) == 0:
        return None
    
    mean_reflectance = np.mean(roi_data[:, 1])
    std_reflectance = np.std(roi_data[:, 1])
    
    short_threshold = find_threshold_near_target(data, 50, short_target)
    long_threshold = find_threshold_near_target(data, 50, long_target)
    
    return {
        'roi_mean': mean_reflectance,
        'roi_std': std_reflectance,
        'short_threshold': short_threshold,
        'long_threshold': long_threshold
    }

def plot_and_save(data, filename, output_dir, roi_info, roi_start, roi_end):
    plt.figure(figsize=(10, 6))
    plt.plot(data[:, 0], data[:, 1], 'b-', linewidth=1.5)
    
    if roi_start > 0 and roi_end > 0:
        roi_mask = (data[:, 0] >= roi_start) & (data[:, 0] <= roi_end)
        roi_data = data[roi_mask]
        if len(roi_data) > 0:
            plt.fill_between(roi_data[:, 0], roi_data[:, 1], alpha=0.3, color='green', label='ROI Range')
    
    if roi_info:
        short_w, short_r = roi_info['short_threshold']
        long_w, long_r = roi_info['long_threshold']
        plt.axvline(x=short_w, color='red', linestyle='--', label=f'Short Threshold: {short_w:.2f}nm')
        plt.axvline(x=long_w, color='orange', linestyle='--', label=f'Long Threshold: {long_w:.2f}nm')
        plt.scatter([short_w, long_w], [short_r, long_r], color='red', s=50, zorder=5)
    
    plt.xlabel('Wavelength (nm)')
    plt.ylabel('Reflectance (%)')
    plt.title(f'{filename} - Reflectance vs Wavelength')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.xlim(data[:, 0].min(), data[:, 0].max())
    plt.ylim(0, 100)
    
    output_path = os.path.join(output_dir, f'{filename}.png')
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()

def main():
    data_dir = r'E:\GIT_Space\Toolkit\Coating-single-Performance\data'
    output_dir = r'E:\GIT_Space\Toolkit\Coating-single-Performance\Output'
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    roi_configs = {
        'UC500': {'roi_start': 500, 'roi_end': 700, 'short_target': 500, 'long_target': 700},
        'UC700': {'roi_start': 700, 'roi_end': 930, 'short_target': 700, 'long_target': 930},
        'UDE450': {'roi_start': 450, 'roi_end': 650, 'short_target': 450, 'long_target': 650}
    }
    
    txt_files = [f for f in os.listdir(data_dir) if f.endswith('.txt')]
    
    for txt_file in txt_files:
        filename = os.path.splitext(txt_file)[0]
        filepath = os.path.join(data_dir, txt_file)
        
        data = read_txt_file(filepath)
        
        config_key = None
        for key in roi_configs.keys():
            if key in filename:
                config_key = key
                break
        
        if config_key:
            config = roi_configs[config_key]
            roi_info = analyze_roi(data, config['roi_start'], config['roi_end'], 
                                   config['short_target'], config['long_target'])
            
            if roi_info:
                print(f'\n===== {filename} =====')
                print(f'ROI Range: {config["roi_start"]}nm - {config["roi_end"]}nm')
                print(f'Short Threshold (50% near {config["short_target"]}nm): {roi_info["short_threshold"][0]:.2f}nm, {roi_info["short_threshold"][1]:.2f}%')
                print(f'Long Threshold (50% near {config["long_target"]}nm): {roi_info["long_threshold"][0]:.2f}nm, {roi_info["long_threshold"][1]:.2f}%')
                print(f'ROI Mean Reflectance: {roi_info["roi_mean"]:.2f}%')
                print(f'ROI Std Reflectance: {roi_info["roi_std"]:.2f}%')
                
                plot_and_save(data, filename, output_dir, roi_info, 
                             config['roi_start'], config['roi_end'])
        else:
            plot_and_save(data, filename, output_dir, None, 0, 0)
            print(f'\n===== {filename} =====')
            print('No ROI configuration found for this file.')

if __name__ == '__main__':
    main()
