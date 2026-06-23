# Toolkit 工具集

Python 工具集，用于数据处理、分析和可视化。

## 目录结构

```
Toolkit/
├── batch_rename_files.py               # 批量重命名工具
├── cal_CWL_FWHM.py                     # 光谱分析工具
├── create_gif/                         # GIF 动画生成
├── take_point_from_picture/            # 图片坐标提取
├── Trae-Skill/                         # Trae 技能文档
├── TFD-data-Setup/                     # TFD 数据配置
├── Coating-single-Performance/         # 镀膜性能分析
├── Asc2CSV/                            # ASC 光谱数据转 CSV
└── Transmission-compare/               # 透射率曲线对比
```

## 工具说明

| 工具 | 功能 |
|------|------|
| batch_rename_files.py | 批量重命名，删除文件名中最后一个"-"前的内容 |
| cal_CWL_FWHM.py | 计算光谱中心波长(CWL)和半高全宽(FWHM) |
| create_gif/ | 图片按数值排序生成GIF动画，提供独立exe（双击即用） |
| take_point_from_picture/ | 图片交互式提取坐标，导出CSV |
| Trae-Skill/ | Matplotlib/Seaborn/Plotly绘图防重叠规范 |
| TFD-data-Setup/ | 读取校准系数和LUT，生成TFD电压配置 |
| Coating-single-Performance/ | 镀膜光谱分析，计算ROI反射率和阈值波长，生成HTML报告 |
| Asc2CSV/ | 批量解析ASC光谱文件，导出波长/透射率CSV数据 |
| Transmission-compare/ | 批量读取透射率TXT数据，绘制多曲线对比图 |

## 更新日志

### v2.5 (2026年6月23日)

**新增工具：**
- 新增 Asc2CSV，支持批量将 ASC 光谱数据转换为 CSV
- ASC 解析支持 `#DATA` 数据段识别，缺失时自动提取最长连续数值块
- 新增 Transmission-compare，用于批量绘制透射率曲线对比图

**Coating-single-Performance 改进：**
- 兼容包含 `T_mean`、`T_std`、`T_min`、`T_max`、`T_1...T_N` 的新格式数据
- TXT/CSV 数据读取改为 UTF-8 编码，提升中文路径和表头兼容性

---

### v2.4 (2026年5月29日)

**create_gif 改进：**
- 新增独立 exe 可执行文件（18MB，双击即用，无需安装 Python）
- 入口改为 GUI 交互：文件夹选择对话框、帧间隔设置、排序方式选择
- 移除硬编码路径，开箱即用

---

### v2.3 (2026年5月21日)

**Coating-single-Performance 改进：**
- 支持透射率分析（原为反射率）
- 支持 CSV 格式数据文件
- 新增曲线有效性检测，过滤异常斜率曲线
- 新增 ROI 区域逐波长最小/最大值统计
- thickness-nd 文件可选，缺失时跳过分析

**create_gif 改进：**
- 更新默认输入路径

---

### v2.2 (2026年5月14日)

- Coating-single-Performance 新增 HTML 报告输出
- 新增公差数据分析功能
- 新增 UMTL450 系列特定波长点分析
- 修正 50% 阈值判断逻辑

---

### v2.1 (2026年5月)

- 新增 TFD-data-Setup 工具
- 新增 Coating-single-Performance 工具

---

### v2.0 (2026年5月)

- create_gif 支持 JPG/JPEG 格式
- take_point_from_picture 新增清屏功能

## 版本信息

- **版本：** 2.5
- **更新日期：** 2026年6月23日
- **作者：** UNS-JeromeWei

## 许可证

MIT License
