import os
import re
import csv


def read_coefficients_csv(csv_path):
    """Read driver board calibration CSV, return a, b lists (4 values each)"""
    a_values = []
    b_values = []
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    in_coefficients = False
    for i, line in enumerate(lines):
        if 'Coefficients' in line:
            in_coefficients = True
            continue
        
        if in_coefficients:
            line = line.strip()
            if line.startswith('a,'):
                parts = line.split(',')
                a_values = [float(parts[j]) for j in range(1, 5)]
            elif line.startswith('b,'):
                parts = line.split(',')
                b_values = [float(parts[j]) for j in range(1, 5)]
                break
    
    return a_values, b_values


def read_lut_csv(csv_path, cwl_targets):
    """Read LUT CSV, return voltage matrix (10 rows x 4 columns)"""
    lut_data = []
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                cwl = float(row['CWL'])
                v1 = float(row['V1'])
                v2 = float(row['V2'])
                v3 = float(row['V3'])
                v4 = float(row['V4'])
                lut_data.append((cwl, v1, v2, v3, v4))
            except (KeyError, ValueError):
                continue
    
    v_matrix = []
    for target_cwl in cwl_targets:
        closest_row = min(lut_data, key=lambda x: abs(x[0] - target_cwl))
        v_matrix.append([closest_row[1], closest_row[2], closest_row[3], closest_row[4]])
    
    return v_matrix


def replace_template_values(template_content, a_values, b_values, v_matrix):
    """Replace values in template while preserving format"""
    result = template_content
    
    pattern_a = r'(double a\[\] = \{ )[^\}]+(\};)'
    a_str = ', '.join(f'{v}' for v in a_values)
    result = re.sub(pattern_a, r'\g<1>' + a_str + r' \g<2>', result)
    
    pattern_b = r'(double b\[\] = \{ )[^\}]+(\};)'
    b_str = ', '.join(f'{v}' for v in b_values)
    result = re.sub(pattern_b, r'\g<1>' + b_str + r' \g<2>', result)
    
    pattern_v = r'(double v\[\]\[4\] = \{)[\s\S]*?(\};)'
    v_lines = []
    for row in v_matrix:
        v_lines.append(f'        {{{row[0]},{row[1]},{row[2]},{row[3]}}}')
    v_str = '\n' + ',\n'.join(v_lines) + '\n    '
    result = re.sub(pattern_v, r'\g<1>' + v_str + r'\g<2>', result)
    
    return result


def process_tfd_setup(tfd_name, criteria_csv_path, lut_csv_path, template_path, output_dir):
    """Main processing function"""
    cwl_targets = [713, 736, 759, 782, 805, 828, 851, 874, 897, 920]
    
    a_values, b_values = read_coefficients_csv(criteria_csv_path)
    v_matrix = read_lut_csv(lut_csv_path, cwl_targets)
    
    with open(template_path, 'r', encoding='utf-8') as f:
        template_content = f.read()
    
    result = replace_template_values(template_content, a_values, b_values, v_matrix)
    
    output_folder = os.path.join(output_dir, tfd_name)
    os.makedirs(output_folder, exist_ok=True)
    
    output_path = os.path.join(output_folder, f'{tfd_name}.txt')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(result)
    
    print(f'Output saved to: {output_path}')


def main():
    criteria_csv_path = r"E:\OneDrive - Unispectral\01_研发\00_应用场景\13-TFD 项目\06-MEMS 驱动板\4套TFD\TFD_1047\board_1047_criteria_0.1_20230625_164210.csv"
    lut_csv_path = r"E:\OneDrive - Unispectral\01_研发\00_应用场景\13-TFD 项目\06-MEMS 驱动板\4套TFD\TFD_1047\ASR_P1s1_W4@47-22_SR#20260316131713_LUT.csv"
    
    tfd_name = "TFD_1047"
    template_path = os.path.join(os.path.dirname(__file__), "Templet.txt")
    output_dir = os.path.dirname(__file__)
    
    process_tfd_setup(tfd_name, criteria_csv_path, lut_csv_path, template_path, output_dir)


if __name__ == "__main__":
    main()