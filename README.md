# Toolkit 工具集

这是一个包含多个实用 Python 工具的工具集，用于日常数据处理、分析和可视化任务。

## 目录结构

```
Toolkit/
├── README.md                           # 本说明文档
├── batch_rename_files.py               # 批量重命名工具
├── cal_CWL_FWHM.py                     # 光谱分析工具
├── create_gif/                         # GIF 动画生成工具
│   └── create_gif.py
├── take_point_from_picture/            # 图片坐标提取工具
│   ├── take_point_from_picture.py      # Python 脚本
│   ├── 使用说明SOP.md                  # 使用说明文档
│   └── exe/                            # 可执行文件目录
│       └── take_point_from_picture.exe
└── Trae-Skill/                         # Trae 技能文档
    └── 绘图防重叠约束 Skill.md
```

## 工具说明

### 1. batch_rename_files.py - 批量重命名工具

**功能描述：** 批量重命名指定文件夹中的 `.txt` 文件，删除文件名中最后一个 "-" 之前的所有内容。

**使用方法：**
```bash
# 方式1：直接运行，弹出文件夹选择对话框
python batch_rename_files.py

# 方式2：命令行指定文件夹路径
python batch_rename_files.py "C:\path\to\folder"
```

**示例：**
- 原文件名：`2024-01-15-data.txt` → 新文件名：`data.txt`
- 原文件名：`project-v1.0-config.txt` → 新文件名：`v1.0-config.txt`

**依赖：** 无需额外安装，使用 Python 标准库

---

### 2. cal_CWL_FWHM.py - 光谱分析工具

**功能描述：** 计算光谱数据的中心波长 (CWL) 和半高全宽 (FWHM)，并可视化显示结果。

**主要功能：**
- 读取 CSV 格式的光谱数据
- 计算中心波长 (CWL)：加权平均波长
- 计算半高全宽 (FWHM)：峰值半高处的波长宽度
- 绘制光谱曲线并标注 CWL 和 FWHM

**使用方法：**
```bash
python cal_CWL_FWHM.py
```
运行后弹出文件选择对话框，选择包含光谱数据的 CSV 文件。

**CSV 文件格式要求：**
- 成对列格式：第一列为波长，第二列为强度，可包含多组数据
- 示例：
  ```csv
  wavelength1,intensity1,wavelength2,intensity2
  400,0.1,500,0.2
  410,0.3,510,0.4
  ...
  ```

**依赖：**
```bash
pip install pandas numpy matplotlib
```

---

### 3. create_gif/ - GIF 动画生成工具

**功能描述：** 将文件夹中的 PNG/JPG/JPEG 图片按文件名中的数值排序，合并生成 GIF 动画。

**主要功能：**
- 支持 PNG、JPG、JPEG 多种图片格式
- 自动识别文件名中的数值（支持多种格式）
- 按数值升序或降序排列图片
- 无法提取数值时自动按文件名排序
- 可自定义帧间隔时间
- 支持多种命名格式：`CRA = 123.45`、`_123nm`、`comparison_123` 等

**使用方法：**
修改脚本中的 `input_folder`、`output_gif`、`frame_duration` 参数后运行：
```bash
python create_gif/create_gif.py
```

**参数说明：**
- `input_folder`：包含 PNG 图片的文件夹路径
- `output_gif`：输出的 GIF 文件路径
- `frame_duration`：每帧显示时间（毫秒）
- `sort_ascending`：排序方式（True 升序，False 降序）

**依赖：**
```bash
pip install Pillow
```

---

### 4. take_point_from_picture/ - 图片坐标提取工具

**功能描述：** 从图片中交互式提取数据点坐标，建立坐标系并进行线性插值，导出为 CSV 文件。

**主要功能：**
- 在图片上点击设置 X/Y 轴参考点
- 输入实际坐标值建立坐标系
- 点击提取离散数据点
- 线性插值生成整数 X 坐标对应的 Y 值
- 导出结果到 CSV 文件

**使用方法：**

方式1：运行 Python 脚本
```bash
python take_point_from_picture/take_point_from_picture.py
```

方式2：直接运行 EXE 文件（无需 Python 环境）
```bash
take_point_from_picture/exe/take_point_from_picture.exe
```

详细使用说明请参阅：[take_point_from_picture/使用说明SOP.md](take_point_from_picture/使用说明SOP.md)

**依赖：**
```bash
pip install pygame pillow numpy pandas matplotlib
```

---

### 5. Trae-Skill/ - Trae 技能文档

**内容描述：** Matplotlib、Seaborn、Plotly 绘图防重叠约束规范，用于指导 AI 生成规范的绘图代码。

**主要内容包括：**
- 各绘图库的防重叠布局规则
- 图例、标题、坐标轴的布局规范
- 多子图间距设置
- 代码示例和禁止行为清单

---

## 系统要求

- Python 3.8+
- Windows 10/11（主要测试平台）

## 安装依赖

```bash
pip install pandas numpy matplotlib Pillow pygame
```

## 版本信息

- **版本：** 1.0
- **更新日期：** 2026年4月
- **作者：** UNS-JeromeWei

## 许可证

MIT License
