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
├── Trae-Skill/                         # Trae 技能文档
│   └── 绘图防重叠约束 Skill.md
├── TFD-data-Setup/                     # TFD 数据配置工具
│   └── TFD-Voltage-MonarchPCBA-setup.py
└── Coating-single-Performance/         # 镀膜性能分析工具
    └── coating_analysis.py
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

### 6. TFD-data-Setup/ - TFD 数据配置工具

**功能描述：** 读取驱动板校准系数和 LUT 数据，生成 TFD 电压配置文件。

**主要功能：**
- 读取驱动板校准 CSV 文件，提取 a、b 系数
- 读取 LUT CSV 文件，根据目标 CWL 提取电压矩阵
- 基于模板文件生成 TFD 配置文件

**使用方法：**
修改脚本中的 CSV 路径和 TFD 名称后运行：
```bash
python TFD-data-Setup/TFD-Voltage-MonarchPCBA-setup.py
```

**参数说明：**
- `criteria_csv_path`：驱动板校准系数 CSV 文件路径
- `lut_csv_path`：LUT 数据 CSV 文件路径
- `tfd_name`：TFD 名称（用于输出文件命名）

**依赖：**
```bash
pip install numpy
```

---

### 7. Coating-single-Performance/ - 镀膜性能分析工具

**功能描述：** 分析镀膜光谱数据，计算 ROI 区域反射率统计和阈值波长，生成 HTML 分析报告。

**版本：** v2.2

**主要功能：**
- 读取 TXT 格式的光谱数据（单曲线和公差多曲线）
- 计算 ROI 区域平均反射率
- 查找 50% 反射率阈值波长（Short 阈值 < ROI 起始波长，Long 阈值 > ROI 结束波长）
- 分析公差数据（thickness 和 thickness-nd）的阈值波动范围
- 生成包含图表和汇总表格的 HTML 分析报告

**使用方法：**
将光谱数据放入 `data` 文件夹后运行：
```bash
python Coating-single-Performance/coating_analysis.py
```

**数据文件命名规则：**
- `{系列名}.txt` - 基础曲线数据
- `{系列名}-tolerance-thickness.txt` - 公差考虑厚度的数据（多曲线）
- `{系列名}-tolerance-thickness-nd.txt` - 公差考虑厚度和折射率的数据（多曲线）

**支持的配置：**
- UC700：ROI 700-930nm
- UC500：ROI 500-700nm
- UDE450：ROI 450-650nm
- UMTL450：特定波长点分析（400nm、500nm、600nm、800nm、900nm）

**输出内容：**
- HTML 报告文件（命名格式：`coating_analysis_YYMMDDHH.html`）
- 各系列曲线分布图（标记 ROI 范围和 50% 阈值点）
- 公差分析图（标记阈值最大最小波动范围）
- 汇总表格（显示基准值 ± 公差偏差）

**依赖：**
```bash
pip install numpy matplotlib
```

---

## 系统要求

- Python 3.8+
- Windows 10/11（主要测试平台）

## 安装依赖

```bash
pip install pandas numpy matplotlib Pillow pygame
```

## 更新日志

### v2.2 (2026年5月14日)

**新增功能：**
- Coating-single-Performance 工具新增 HTML 报告输出功能
- 新增公差数据分析功能（thickness 和 thickness-nd 多曲线）
- 新增 UMTL450 系列特定波长点分析（400nm、500nm、600nm、800nm、900nm）
- 新增汇总表格，显示基准值 ± 公差偏差

**改进优化：**
- 修正 50% 阈值判断逻辑：Short 阈值必须 < ROI 起始波长，Long 阈值必须 > ROI 结束波长
- 调整分析顺序：UC700 → UC500 → UDE450 → UMTL450
- 图表使用 base64 编码直接嵌入 HTML，无需额外图片文件
- HTML 报告命名添加时间戳（YYMMDDHH 格式）

---

### v2.1 (2026年5月)

**新增功能：**
- 新增 TFD-data-Setup 工具，用于生成 TFD 电压配置文件
- 新增 Coating-single-Performance 工具，用于镀膜光谱性能分析

**改进优化：**
- create_gif 工具更新默认输入路径

---

### v2.0 (2026年5月)

**新增功能：**
- create_gif 工具新增 JPG/JPEG 图片格式支持
- create_gif 工具优化数值提取排序逻辑，支持更多文件名格式
- take_point_from_picture 工具新增清屏功能，方便重新提取数据点

**改进优化：**
- create_gif 工具改进文件名数值识别算法，支持 `CRA = 123.45`、`_123nm`、`comparison_123` 等多种格式
- create_gif 工具增强排序稳定性，无法提取数值时自动按文件名排序
- README 文档完善工具说明和参数描述

---

## 版本信息

- **版本：** 2.2
- **更新日期：** 2026年5月14日
- **作者：** UNS-JeromeWei

## 许可证

MIT License
