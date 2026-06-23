import os
import glob
import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif'] = (['SimHei', 'Microsoft YaHei', 'SimSun'])
plt.rcParams['axes.unicode_minus'] = False 
os.system('cls' if os.name == 'nt' else 'clear') 

data_dir = r"F:\05-Jerome Studios\Coating Design\Coating_data\UC500\26052113-UC500_p_MEMS_RM"
txt_files = glob.glob(os.path.join(data_dir, "*.txt"))

plt.figure(figsize=(12, 8))
colors = plt.cm.tab10(range(len(txt_files)))

for i, file in enumerate(txt_files):
    filename = os.path.basename(file)
    wavelength = []
    transmittance = []
    
    with open(file, 'r') as f:
        lines = f.readlines()
        for line in lines[1:]:
            parts = line.strip().split()
            if len(parts) >= 3:
                wavelength.append(float(parts[0]))
                transmittance.append(float(parts[2]))
    
    plt.plot(wavelength, transmittance, color=colors[i % len(colors)], label=filename, linewidth=1)

plt.xlabel('Wavelength (nm)', fontsize=12)
plt.ylabel('Transmittance (%)', fontsize=12)
plt.title('Transmission Comparison', fontsize=14)
plt.legend(loc='best', fontsize=10)
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('transmission_comparison.png', dpi=150)
plt.show()
