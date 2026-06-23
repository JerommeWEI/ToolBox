import os
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import base64
from io import BytesIO

def get_delimiter(filepath):
    ext = os.path.splitext(filepath)[1].lower()
    if ext == '.csv':
        return ','
    return '\t'

def find_data_file(data_dir, base_name):
    txt_path = os.path.join(data_dir, f'{base_name}.txt')
    if os.path.exists(txt_path):
        return txt_path
    csv_path = os.path.join(data_dir, f'{base_name}.csv')
    if os.path.exists(csv_path):
        return csv_path
    return txt_path

def is_new_format(lines):
    """Detect new data format: first non-comment line (header) contains 'T_mean'."""
    for line in lines:
        s = line.strip()
        if s and not s.startswith('#'):
            return 'T_mean' in s
    return False

def read_single_file(filepath, use_transmittance=False):
    data = []
    delimiter = get_delimiter(filepath)
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    new_format = is_new_format(lines)
    if use_transmittance:
        value_col = 1 if new_format else 2
    else:
        value_col = 1
    for line in lines:
        parts = line.strip().split(delimiter)
        if len(parts) > value_col:
            try:
                wavelength = float(parts[0].strip())
                value = float(parts[value_col].strip())
                data.append([wavelength, value])
            except ValueError:
                continue
    return np.array(data)

def check_curve_validity(data, max_slope_threshold=5.0):
    if len(data) < 3:
        return False, 0
    slopes = []
    for i in range(1, len(data) - 1):
        dw1 = data[i, 0] - data[i-1, 0]
        dw2 = data[i+1, 0] - data[i, 0]
        if dw1 == 0 or dw2 == 0:
            continue
        slope1 = (data[i, 1] - data[i-1, 1]) / dw1
        slope2 = (data[i+1, 1] - data[i, 1]) / dw2
        slope_diff = abs(slope2 - slope1)
        slopes.append(slope_diff)
    if len(slopes) == 0:
        return True, 0
    max_slope_diff = max(slopes)
    return max_slope_diff < max_slope_threshold, max_slope_diff

def read_tolerance_file(filepath, use_transmittance=False, max_slope_threshold=5.0):
    all_curves = []
    delimiter = get_delimiter(filepath)
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        if len(lines) < 2:
            return all_curves
        new_format = is_new_format(lines)
        if new_format:
            # New format: col0=wavelength, then T_mean,T_std,T_min,T_max (4 cols),
            # then T_1..T_N curve columns. Each curve shares the wavelength column.
            header_line = None
            for line in lines:
                s = line.strip()
                if s and not s.startswith('#'):
                    header_line = s
                    break
            if header_line is None:
                return all_curves
            ncols = len(header_line.split(delimiter))
            num_curves = ncols - 5
            if num_curves <= 0:
                return all_curves
            all_curves = [[] for _ in range(num_curves)]
            for line in lines:
                s = line.strip()
                if not s or s.startswith('#'):
                    continue
                parts = s.split(delimiter)
                try:
                    wavelength = float(parts[0].strip())
                except (ValueError, IndexError):
                    continue
                for i in range(num_curves):
                    idx = 5 + i
                    if idx < len(parts):
                        try:
                            value = float(parts[idx].strip())
                            all_curves[i].append([wavelength, value])
                        except ValueError:
                            continue
        else:
            # Old format: interleaved Wavelength-Value column pairs.
            header = lines[0].strip().split(delimiter)
            num_pairs = len(header) // 2
            for i in range(num_pairs):
                all_curves.append([])
            for line in lines[1:]:
                parts = line.strip().split(delimiter)
                for i in range(num_pairs):
                    idx = i * 2
                    if idx + 1 < len(parts):
                        try:
                            wavelength = float(parts[idx].strip())
                            value = float(parts[idx + 1].strip())
                            all_curves[i].append([wavelength, value])
                        except ValueError:
                            continue
    result = []
    invalid_count = 0
    for curve in all_curves:
        if len(curve) > 0:
            curve_array = np.array(curve)
            sort_idx = np.argsort(curve_array[:, 0])
            curve_array = curve_array[sort_idx]
            is_valid, max_slope = check_curve_validity(curve_array, max_slope_threshold)
            if is_valid:
                result.append(curve_array)
            else:
                invalid_count += 1
    if invalid_count > 0:
        print(f"  Filtered {invalid_count} invalid curves due to abnormal slope")
    return result

def find_short_threshold(data, roi_start, target_value=50):
    short_region = data[data[:, 0] < roi_start]
    if len(short_region) == 0:
        return None
    candidates = short_region[np.abs(short_region[:, 1] - target_value) < 1]
    if len(candidates) == 0:
        idx = np.argmin(np.abs(short_region[:, 1] - target_value))
        return short_region[idx, 0], short_region[idx, 1]
    idx = np.argmax(candidates[:, 0])
    return candidates[idx, 0], candidates[idx, 1]

def find_long_threshold(data, roi_end, target_value=50):
    long_region = data[data[:, 0] > roi_end]
    if len(long_region) == 0:
        return None
    candidates = long_region[np.abs(long_region[:, 1] - target_value) < 1]
    if len(candidates) == 0:
        idx = np.argmin(np.abs(long_region[:, 1] - target_value))
        return long_region[idx, 0], long_region[idx, 1]
    idx = np.argmin(candidates[:, 0])
    return candidates[idx, 0], candidates[idx, 1]

def analyze_single_curve(data, roi_start, roi_end, short_target, long_target):
    roi_mask = (data[:, 0] >= roi_start) & (data[:, 0] <= roi_end)
    roi_data = data[roi_mask]
    if len(roi_data) == 0:
        return None
    mean_value = np.mean(roi_data[:, 1])
    short_threshold = find_short_threshold(data, roi_start)
    long_threshold = find_long_threshold(data, roi_end)
    return {
        'roi_mean': mean_value,
        'short_threshold': short_threshold,
        'long_threshold': long_threshold
    }

def analyze_tolerance_curves(curves, roi_start, roi_end, short_target, long_target):
    short_wavelengths = []
    long_wavelengths = []
    roi_means = []
    for curve in curves:
        result = analyze_single_curve(curve, roi_start, roi_end, short_target, long_target)
        if result and result['short_threshold'] and result['long_threshold']:
            short_wavelengths.append(result['short_threshold'][0])
            long_wavelengths.append(result['long_threshold'][0])
            roi_means.append(result['roi_mean'])
    
    roi_min_at_wl = None
    roi_max_at_wl = None
    if len(curves) > 0:
        base_curve = curves[0]
        roi_mask = (base_curve[:, 0] >= roi_start) & (base_curve[:, 0] <= roi_end)
        roi_wavelengths = base_curve[roi_mask, 0]
        for wl in roi_wavelengths:
            values_at_wl = []
            for curve in curves:
                idx = np.argmin(np.abs(curve[:, 0] - wl))
                values_at_wl.append(curve[idx, 1])
            min_val = min(values_at_wl)
            max_val = max(values_at_wl)
            if roi_min_at_wl is None or min_val < roi_min_at_wl:
                roi_min_at_wl = min_val
            if roi_max_at_wl is None or max_val > roi_max_at_wl:
                roi_max_at_wl = max_val
    
    return {
        'short_min': min(short_wavelengths) if short_wavelengths else None,
        'short_max': max(short_wavelengths) if short_wavelengths else None,
        'long_min': min(long_wavelengths) if long_wavelengths else None,
        'long_max': max(long_wavelengths) if long_wavelengths else None,
        'roi_mean_min': min(roi_means) if roi_means else None,
        'roi_mean_max': max(roi_means) if roi_means else None,
        'roi_min_at_wl': roi_min_at_wl,
        'roi_max_at_wl': roi_max_at_wl
    }

def get_value_at_wavelength(data, target_wavelength):
    idx = np.argmin(np.abs(data[:, 0] - target_wavelength))
    return data[idx, 1]

def analyze_umtl_single(data, wavelengths):
    results = {}
    for wl in wavelengths:
        results[wl] = get_value_at_wavelength(data, wl)
    return results

def analyze_umtl_tolerance(curves, wavelengths):
    results = {}
    for wl in wavelengths:
        values = []
        for curve in curves:
            values.append(get_value_at_wavelength(curve, wl))
        results[wl] = {'min': min(values), 'max': max(values)}
    return results

def plot_to_base64(fig):
    buf = BytesIO()
    fig.savefig(buf, format='png', dpi=150, bbox_inches='tight')
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)
    return img_base64

def plot_single_curve(data, filename, roi_start, roi_end, short_threshold, long_threshold):
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(data[:, 0], data[:, 1], 'b-', linewidth=1.5)
    roi_mask = (data[:, 0] >= roi_start) & (data[:, 0] <= roi_end)
    roi_data = data[roi_mask]
    if len(roi_data) > 0:
        ax.fill_between(roi_data[:, 0], roi_data[:, 1], alpha=0.3, color='green', label='ROI Range')
    if short_threshold:
        ax.axvline(x=short_threshold[0], color='red', linestyle='--', label=f'Short 50%: {short_threshold[0]:.2f}nm')
        ax.scatter([short_threshold[0]], [short_threshold[1]], color='red', s=50, zorder=5)
    if long_threshold:
        ax.axvline(x=long_threshold[0], color='orange', linestyle='--', label=f'Long 50%: {long_threshold[0]:.2f}nm')
        ax.scatter([long_threshold[0]], [long_threshold[1]], color='orange', s=50, zorder=5)
    ax.set_xlabel('Wavelength (nm)')
    ax.set_ylabel('Transmittance (%)')
    ax.set_title(f'{filename} - Transmittance vs Wavelength')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_xlim(data[:, 0].min(), data[:, 0].max())
    ax.set_ylim(0, 100)
    return plot_to_base64(fig)

def plot_tolerance_curves(curves, filename, roi_start, roi_end, short_min, short_max, long_min, long_max):
    fig, ax = plt.subplots(figsize=(10, 6))
    for curve in curves:
        ax.plot(curve[:, 0], curve[:, 1], 'b-', linewidth=0.5, alpha=0.3)
    roi_mask = (curves[0][:, 0] >= roi_start) & (curves[0][:, 0] <= roi_end)
    roi_data = curves[0][roi_mask]
    if len(roi_data) > 0:
        ax.fill_between(roi_data[:, 0], roi_data[:, 1], alpha=0.3, color='green', label='ROI Range')
    if short_min and short_max:
        ax.axvline(x=short_min, color='red', linestyle='--', label=f'Short 50% Min: {short_min:.2f}nm')
        ax.axvline(x=short_max, color='darkred', linestyle=':', label=f'Short 50% Max: {short_max:.2f}nm')
    if long_min and long_max:
        ax.axvline(x=long_min, color='orange', linestyle=':', label=f'Long 50% Min: {long_min:.2f}nm')
        ax.axvline(x=long_max, color='darkorange', linestyle='--', label=f'Long 50% Max: {long_max:.2f}nm')
    ax.set_xlabel('Wavelength (nm)')
    ax.set_ylabel('Reflectance (%)')
    ax.set_title(f'{filename} - Tolerance Analysis')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)
    ax.set_xlim(curves[0][:, 0].min(), curves[0][:, 0].max())
    ax.set_ylim(0, 100)
    return plot_to_base64(fig)

def plot_umtl_single(data, filename, wavelengths, transmittance_values):
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(data[:, 0], data[:, 1], 'b-', linewidth=1.5)
    for wl in wavelengths:
        if wl in transmittance_values:
            ax.scatter([wl], [transmittance_values[wl]], color='red', s=50, zorder=5, label=f'{wl}nm: {transmittance_values[wl]:.2f}%')
    ax.set_xlabel('Wavelength (nm)')
    ax.set_ylabel('Transmittance (%)')
    ax.set_title(f'{filename} - Transmittance vs Wavelength')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)
    ax.set_xlim(data[:, 0].min(), data[:, 0].max())
    ax.set_ylim(0, 100)
    return plot_to_base64(fig)

def plot_umtl_tolerance(curves, filename, wavelengths, tolerance_results):
    fig, ax = plt.subplots(figsize=(10, 6))
    for curve in curves:
        ax.plot(curve[:, 0], curve[:, 1], 'b-', linewidth=0.5, alpha=0.3)
    colors = ['red', 'green', 'blue', 'purple', 'orange']
    for i, wl in enumerate(wavelengths):
        if wl in tolerance_results:
            t_min = tolerance_results[wl]['min']
            t_max = tolerance_results[wl]['max']
            ax.scatter([wl], [t_min], color=colors[i % len(colors)], s=50, zorder=5, marker='v')
            ax.scatter([wl], [t_max], color=colors[i % len(colors)], s=50, zorder=5, marker='^')
            ax.errorbar([wl], [(t_min + t_max) / 2], yerr=[(t_max - t_min) / 2], 
                       fmt='none', color=colors[i % len(colors)], capsize=5, label=f'{wl}nm: {t_min:.2f}%-{t_max:.2f}%')
    ax.set_xlabel('Wavelength (nm)')
    ax.set_ylabel('Transmittance (%)')
    ax.set_title(f'{filename} - Tolerance Analysis')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)
    ax.set_xlim(curves[0][:, 0].min(), curves[0][:, 0].max())
    ax.set_ylim(0, 100)
    return plot_to_base64(fig)

def generate_html(output_dir, timestamp):
    data_dir = r'E:\GIT_Space\Toolkit\Coating-single-Performance\data'
    roi_configs = {
        'UC500': {'roi_start': 500, 'roi_end': 700, 'short_target': 500, 'long_target': 700},
        'UC700': {'roi_start': 700, 'roi_end': 930, 'short_target': 700, 'long_target': 930},
        'UDE450': {'roi_start': 450, 'roi_end': 650, 'short_target': 450, 'long_target': 650}
    }
    umtl_wavelengths = [400, 500, 600, 800, 900]
    
    html_content = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Coating Analysis Report - {timestamp}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
        h1 {{ color: #333; border-bottom: 2px solid #333; padding-bottom: 10px; }}
        h2 {{ color: #444; margin-top: 30px; border-left: 4px solid #4CAF50; padding-left: 10px; }}
        h3 {{ color: #555; }}
        table {{ border-collapse: collapse; width: 100%; margin: 20px 0; background-color: white; }}
        th, td {{ border: 1px solid #ddd; padding: 12px; text-align: center; }}
        th {{ background-color: #4CAF50; color: white; }}
        tr:nth-child(even) {{ background-color: #f2f2f2; }}
        tr:hover {{ background-color: #ddd; }}
        .img-container {{ text-align: center; margin: 20px 0; }}
        .img-container img {{ max-width: 100%; height: auto; border: 1px solid #ddd; }}
        .section {{ background-color: white; padding: 20px; margin: 20px 0; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
        .summary-table {{ background-color: #e8f5e9; }}
        .summary-table th {{ background-color: #2e7d32; }}
    </style>
</head>
<body>
    <h1>Coating Analysis Report</h1>
    <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
'''
    
    for series_name in ['UC700', 'UC500', 'UDE450']:
        config = roi_configs[series_name]
        html_content += f'''
    <div class="section">
        <h2>{series_name} Series Analysis</h2>
'''
        
        base_file = os.path.join(data_dir, f'{series_name}.txt')
        thickness_file = os.path.join(data_dir, f'{series_name}-tolerance-thickness.txt')
        nd_file = os.path.join(data_dir, f'{series_name}-tolerance-thickness-nd.txt')
        
        if not os.path.exists(nd_file):
            nd_file = None
        
        base_data = read_single_file(base_file, use_transmittance=True)
        base_result = analyze_single_curve(base_data, config['roi_start'], config['roi_end'], 
                                           config['short_target'], config['long_target'])
        
        img_base = plot_single_curve(base_data, f'{series_name}.txt', config['roi_start'], config['roi_end'],
                                     base_result['short_threshold'], base_result['long_threshold'])
        
        html_content += f'''
        <h3>{series_name}.txt Analysis</h3>
        <div class="img-container">
            <img src="data:image/png;base64,{img_base}" alt="{series_name} Plot">
        </div>
        <table>
            <tr>
                <th>Parameter</th>
                <th>Value</th>
            </tr>
            <tr>
                <td>Short 50% Threshold</td>
                <td>{base_result['short_threshold'][0]:.2f} nm ({base_result['short_threshold'][1]:.2f}%)</td>
            </tr>
            <tr>
                <td>Long 50% Threshold</td>
                <td>{base_result['long_threshold'][0]:.2f} nm ({base_result['long_threshold'][1]:.2f}%)</td>
            </tr>
            <tr>
                <td>ROI Mean Transmittance ({config['roi_start']}-{config['roi_end']}nm)</td>
                <td>{base_result['roi_mean']:.2f}%</td>
            </tr>
        </table>
'''
        
        thickness_curves = read_tolerance_file(thickness_file, use_transmittance=True)
        thickness_result = analyze_tolerance_curves(thickness_curves, config['roi_start'], config['roi_end'],
                                                    config['short_target'], config['long_target'])
        
        img_thickness = plot_tolerance_curves(thickness_curves, f'{series_name}-tolerance-thickness.txt',
                                              config['roi_start'], config['roi_end'],
                                              thickness_result['short_min'], thickness_result['short_max'],
                                              thickness_result['long_min'], thickness_result['long_max'])
        
        html_content += f'''
        <h3>{series_name}-tolerance-thickness.txt Analysis</h3>
        <div class="img-container">
            <img src="data:image/png;base64,{img_thickness}" alt="{series_name} Tolerance Thickness Plot">
        </div>
        <table>
            <tr>
                <th>Parameter</th>
                <th>Min Value</th>
                <th>Max Value</th>
            </tr>
            <tr>
                <td>Short 50% Threshold Wavelength</td>
                <td>{thickness_result['short_min']:.2f} nm</td>
                <td>{thickness_result['short_max']:.2f} nm</td>
            </tr>
            <tr>
                <td>Long 50% Threshold Wavelength</td>
                <td>{thickness_result['long_min']:.2f} nm</td>
                <td>{thickness_result['long_max']:.2f} nm</td>
            </tr>
            <tr>
                <td>ROI Mean Transmittance</td>
                <td>{thickness_result['roi_mean_min']:.2f}%</td>
                <td>{thickness_result['roi_mean_max']:.2f}%</td>
            </tr>
        </table>
'''
        
        if nd_file and os.path.exists(nd_file):
            nd_curves = read_tolerance_file(nd_file, use_transmittance=True)
            nd_result = analyze_tolerance_curves(nd_curves, config['roi_start'], config['roi_end'],
                                                 config['short_target'], config['long_target'])
            
            img_nd = plot_tolerance_curves(nd_curves, f'{series_name}-tolerance-thickness-nd.txt',
                                           config['roi_start'], config['roi_end'],
                                           nd_result['short_min'], nd_result['short_max'],
                                           nd_result['long_min'], nd_result['long_max'])
            
            html_content += f'''
        <h3>{series_name}-tolerance-thickness-nd.txt Analysis</h3>
        <div class="img-container">
            <img src="data:image/png;base64,{img_nd}" alt="{series_name} Tolerance ND Plot">
        </div>
        <table>
            <tr>
                <th>Parameter</th>
                <th>Min Value</th>
                <th>Max Value</th>
            </tr>
            <tr>
                <td>Short 50% Threshold Wavelength</td>
                <td>{nd_result['short_min']:.2f} nm</td>
                <td>{nd_result['short_max']:.2f} nm</td>
            </tr>
            <tr>
                <td>Long 50% Threshold Wavelength</td>
                <td>{nd_result['long_min']:.2f} nm</td>
                <td>{nd_result['long_max']:.2f} nm</td>
            </tr>
            <tr>
                <td>ROI Mean Transmittance</td>
                <td>{nd_result['roi_mean_min']:.2f}%</td>
                <td>{nd_result['roi_mean_max']:.2f}%</td>
            </tr>
        </table>
'''
            
            short_min_all = min(thickness_result['short_min'], nd_result['short_min'])
            short_max_all = max(thickness_result['short_max'], nd_result['short_max'])
            long_min_all = min(thickness_result['long_min'], nd_result['long_min'])
            long_max_all = max(thickness_result['long_max'], nd_result['long_max'])
            roi_mean_min_all = min(thickness_result['roi_mean_min'], nd_result['roi_mean_min'])
            roi_mean_max_all = max(thickness_result['roi_mean_max'], nd_result['roi_mean_max'])
            roi_min_all = min(thickness_result['roi_min_at_wl'], nd_result['roi_min_at_wl']) if thickness_result['roi_min_at_wl'] is not None else None
            roi_max_all = max(thickness_result['roi_max_at_wl'], nd_result['roi_max_at_wl']) if thickness_result['roi_max_at_wl'] is not None else None
        else:
            short_min_all = thickness_result['short_min']
            short_max_all = thickness_result['short_max']
            long_min_all = thickness_result['long_min']
            long_max_all = thickness_result['long_max']
            roi_mean_min_all = thickness_result['roi_mean_min']
            roi_mean_max_all = thickness_result['roi_mean_max']
            roi_min_all = thickness_result['roi_min_at_wl']
            roi_max_all = thickness_result['roi_max_at_wl']
        
        base_short = base_result['short_threshold'][0]
        base_long = base_result['long_threshold'][0]
        base_roi = base_result['roi_mean']
        
        short_min_diff = short_min_all - base_short
        short_max_diff = short_max_all - base_short
        long_min_diff = long_min_all - base_long
        long_max_diff = long_max_all - base_long
        roi_min_diff = roi_min_all - base_roi
        roi_max_diff = roi_max_all - base_roi
        
        html_content += f'''
        <h3>{series_name} Summary Table</h3>
        <table class="summary-table">
            <tr>
                <th>Data Source</th>
                <th>Short 50% Range (nm)</th>
                <th>Long 50% Range (nm)</th>
                <th>ROI Mean Range (%)</th>
            </tr>
            <tr>
                <td>{series_name}.txt</td>
                <td>{base_short:.2f}</td>
                <td>{base_long:.2f}</td>
                <td>{base_roi:.2f}</td>
            </tr>
            <tr>
                <td>Tolerance (thickness + nd)</td>
                <td>{base_short:.2f} {short_min_diff:+.2f} / {short_max_diff:+.2f}</td>
                <td>{base_long:.2f} {long_min_diff:+.2f} / {long_max_diff:+.2f}</td>
                <td>{base_roi:.2f} {roi_min_diff:+.2f} / {roi_max_diff:+.2f}</td>
            </tr>
        </table>
    </div>
'''
    
    html_content += '''
    <div class="section">
        <h2>UMTL450 Series Analysis</h2>
'''
    
    umtl_base_file = os.path.join(data_dir, 'UMTL450.txt')
    umtl_thickness_file = os.path.join(data_dir, 'UMTL450-tolerance-thickness.txt')
    umtl_nd_file = os.path.join(data_dir, 'UMTL450-tolerance-thickness-nd.txt')
    
    umtl_base_data = read_single_file(umtl_base_file, use_transmittance=True)
    umtl_base_result = analyze_umtl_single(umtl_base_data, umtl_wavelengths)
    
    img_umtl_base = plot_umtl_single(umtl_base_data, 'UMTL450.txt', umtl_wavelengths, umtl_base_result)
    
    html_content += f'''
        <h3>UMTL450.txt Analysis</h3>
        <div class="img-container">
            <img src="data:image/png;base64,{img_umtl_base}" alt="UMTL450 Plot">
        </div>
        <table>
            <tr>
                <th>Wavelength (nm)</th>
                <th>Transmittance (%)</th>
            </tr>
'''
    for wl in umtl_wavelengths:
        html_content += f'''
            <tr>
                <td>{wl}</td>
                <td>{umtl_base_result[wl]:.2f}</td>
            </tr>
'''
    html_content += '''        </table>
'''
    
    umtl_thickness_curves = read_tolerance_file(umtl_thickness_file, use_transmittance=True)
    umtl_thickness_result = analyze_umtl_tolerance(umtl_thickness_curves, umtl_wavelengths)
    
    img_umtl_thickness = plot_umtl_tolerance(umtl_thickness_curves, 'UMTL450-tolerance-thickness.txt',
                                             umtl_wavelengths, umtl_thickness_result)
    
    html_content += f'''
        <h3>UMTL450-tolerance-thickness.txt Analysis</h3>
        <div class="img-container">
            <img src="data:image/png;base64,{img_umtl_thickness}" alt="UMTL450 Tolerance Thickness Plot">
        </div>
        <table>
            <tr>
                <th>Wavelength (nm)</th>
                <th>Min Transmittance (%)</th>
                <th>Max Transmittance (%)</th>
            </tr>
'''
    for wl in umtl_wavelengths:
        html_content += f'''
            <tr>
                <td>{wl}</td>
                <td>{umtl_thickness_result[wl]['min']:.2f}</td>
                <td>{umtl_thickness_result[wl]['max']:.2f}</td>
            </tr>
'''
    html_content += '''        </table>
'''
    
    umtl_nd_curves = read_tolerance_file(umtl_nd_file, use_transmittance=True)
    umtl_nd_result = analyze_umtl_tolerance(umtl_nd_curves, umtl_wavelengths)
    
    img_umtl_nd = plot_umtl_tolerance(umtl_nd_curves, 'UMTL450-tolerance-thickness-nd.txt',
                                      umtl_wavelengths, umtl_nd_result)
    
    html_content += f'''
        <h3>UMTL450-tolerance-thickness-nd.txt Analysis</h3>
        <div class="img-container">
            <img src="data:image/png;base64,{img_umtl_nd}" alt="UMTL450 Tolerance ND Plot">
        </div>
        <table>
            <tr>
                <th>Wavelength (nm)</th>
                <th>Min Transmittance (%)</th>
                <th>Max Transmittance (%)</th>
            </tr>
'''
    for wl in umtl_wavelengths:
        html_content += f'''
            <tr>
                <td>{wl}</td>
                <td>{umtl_nd_result[wl]['min']:.2f}</td>
                <td>{umtl_nd_result[wl]['max']:.2f}</td>
            </tr>
'''
    html_content += '''        </table>
'''
    
    html_content += '''
        <h3>UMTL450 Summary Table</h3>
        <table class="summary-table">
            <tr>
                <th>Data Source</th>
'''
    for wl in umtl_wavelengths:
        html_content += f'''                <th>{wl}nm (%)</th>
'''
    html_content += '''            </tr>
            <tr>
                <td>UMTL450.txt</td>
'''
    for wl in umtl_wavelengths:
        html_content += f'''                <td>{umtl_base_result[wl]:.2f}</td>
'''
    html_content += '''            </tr>
            <tr>
                <td>Tolerance Range (thickness + nd)</td>
'''
    for wl in umtl_wavelengths:
        base_val = umtl_base_result[wl]
        min_all = min(umtl_thickness_result[wl]['min'], umtl_nd_result[wl]['min'])
        max_all = max(umtl_thickness_result[wl]['max'], umtl_nd_result[wl]['max'])
        min_diff = min_all - base_val
        max_diff = max_all - base_val
        html_content += f'''                <td>{base_val:.2f} {min_diff:+.2f} / {max_diff:+.2f}</td>
'''
    html_content += '''            </tr>
        </table>
    </div>
'''
    
    html_content += '''
</body>
</html>
'''
    
    html_filename = f'coating_analysis_{timestamp}.html'
    html_path = os.path.join(output_dir, html_filename)
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return html_path

def main():
    data_dir = r'E:\GIT_Space\Toolkit\Coating-single-Performance\data'
    output_dir = r'E:\GIT_Space\Toolkit\Coating-single-Performance\Output'
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    timestamp = datetime.now().strftime('%y%m%d%H')
    html_path = generate_html(output_dir, timestamp)
    print(f'HTML report generated: {html_path}')

if __name__ == '__main__':
    os.system('cls' if os.name == 'nt' else 'clear') 
    main()
