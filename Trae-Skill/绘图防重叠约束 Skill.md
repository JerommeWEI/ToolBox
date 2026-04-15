---
name: matplotlib-seaborn-plotly-no-overlap
description: 强制 Matplotlib、Seaborn、Plotly 绘图时自动处理布局，避免图例、标题、坐标轴、文本等元素重叠，适配所有常见绘图场景
---

# Matplotlib/Seaborn/Plotly 绘图防重叠约束

## 描述
本技能用于约束 Trae 生成 Matplotlib、Seaborn、Plotly 绘图代码时，自动应用对应库的防重叠布局规则，确保图表中所有元素（legend、title、axis、text、colorbar 等）不重叠、布局整洁、可读性强，适配折线图、柱状图、散点图、热力图、多子图、3D图等所有常见场景。

## 使用场景
- 使用 `matplotlib.pyplot`/`plt`、`seaborn`/`sns`、`plotly.express`/`px`/`plotly.graph_objects`/`go` 生成图表的代码
- 数据分析、报告可视化、论文图表、演示图表等对布局整洁度有要求的场景
- 单图、多子图、3D图、热力图等各类绘图场景

## 核心指令（必须严格执行）

### 一、Matplotlib 专属防重叠规则
#### 1. 全局布局（必加）
- 所有绘图代码**最后必须添加**：
  ```python
  plt.tight_layout()  # 自动调整子图与元素间距，核心防重叠配置
  ```
- 多子图场景，优先使用 `fig.tight_layout()` 替代 `plt.tight_layout()`
- 保存图片时，需添加 `bbox_inches="tight"`，避免图例/标题被截断：
  ```python
  plt.savefig("plot.png", dpi=300, bbox_inches="tight")
  ```

#### 2. 图例（legend）防重叠
- 图例默认放在**绘图区外右侧**，避免遮挡数据：
  ```python
  ax.legend(
      loc="upper left",
      bbox_to_anchor=(1.02, 1),  # 图例锚点在轴外右侧，不占用绘图区
      borderaxespad=0,
      frameon=True,  # 显示图例边框，区分背景
      fontsize=10
  )
  ```
- 禁止将图例放在 `center`/`upper center`/`lower center` 等易重叠位置
- 图例过多时，自动分栏：`ncol=2`（两栏）或 `ncol=3`（三栏），避免纵向过长重叠
- 若图例必须在绘图区内，需设置 `bbox_to_anchor` 微调位置，确保不遮挡核心数据

#### 3. 标题与坐标轴防重叠
- 标题、轴标签需增加间距，避免与刻度、图例重叠：
  ```python
  ax.set_title("图表标题", fontsize=14, pad=12)  # pad 控制标题与轴的间距
  ax.set_xlabel("X轴标签", fontsize=12, pad=8)   # pad 控制轴标签与刻度的间距
  ax.set_ylabel("Y轴标签", fontsize=12, pad=8)
  ```
- 坐标轴刻度标签拥挤时（如日期、长文本）：
  - 旋转标签：`ax.tick_params(axis="x", rotation=45, labelsize=10)`（旋转45°，避免横向重叠）
  - 缩小字体：`labelsize=8~10`（根据图表大小调整）
  - 精简刻度：`ax.set_xticks(ax.get_xticks()[::2])`（每隔1个刻度显示1个，减少数量）

#### 4. 文本标注（text/annotate）防重叠
- 标注位置避开数据区、坐标轴、图例和标题
- 自动添加白色半透明背景框，区分标注与背景/数据：
  ```python
  ax.text(
      x, y, "标注内容", 
      bbox=dict(boxstyle="round,pad=0.3", fc="white", alpha=0.8),  # 白色半透明背景
      fontsize=9
  )
  ```
- 使用 `annotate` 标注时，需设置 `arrowprops` 并调整偏移，避免箭头与元素重叠：
  ```python
  ax.annotate(
      "异常点", xy=(x0, y0), xytext=(x0+0.5, y0+0.5),
      arrowprops=dict(arrowstyle="->", color="red", lw=1.5),
      bbox=dict(boxstyle="round,pad=0.3", fc="white", alpha=0.8)
  )
  ```

#### 5. 多子图间距（多图场景必配）
- 手动调整子图间距（备选，优先用 `tight_layout()`）：
  ```python
  plt.subplots_adjust(
      left=0.1,   # 左侧留白
      right=0.85, # 右侧留白（给右侧图例预留空间）
      bottom=0.15,# 底部留白
      top=0.9,    # 顶部留白（给总标题预留空间）
      wspace=0.3, # 子图水平间距
      hspace=0.4  # 子图垂直间距
  )
  ```
- 多子图带总标题时，总标题需与子图顶部留足间距：`plt.suptitle("总标题", y=0.95, fontsize=16)`

### 二、Seaborn 专属防重叠规则（基于 Matplotlib，额外补充）
#### 1. 基础配置（必加）
- Seaborn 绘图后，必须添加：
  ```python
  sns.despine()  # 去除右侧、上侧坐标轴，减少视觉拥挤
  plt.tight_layout()  # 继承 Matplotlib 自动布局，防重叠
  ```
- 若使用 Seaborn 自带的 `FacetGrid`（多子图），需设置 `tight_layout=True`：
  ```python
  g = sns.FacetGrid(df, col="category", tight_layout=True)
  g.map(sns.lineplot, "x", "y")
  ```

#### 2. 图例与标签适配
- Seaborn 自动生成的图例，需按 Matplotlib 规则调整位置（优先外置）：
  ```python
  # 示例：Seaborn 折线图，图例外置
  sns.lineplot(x="x", y="y", hue="category", data=df, ax=ax)
  ax.legend(loc="upper left", bbox_to_anchor=(1.02, 1), borderaxespad=0)
  ```
- 避免使用 Seaborn 默认的 `legend="auto"`，手动指定图例位置，防止重叠
- 热力图（heatmap）需调整 `cbar`（颜色条）位置，避免与坐标轴、标题重叠：
  ```python
  sns.heatmap(
      data, annot=True, cmap="Blues", 
      cbar_kws={"shrink": 0.8, "location": "right"}  # 缩小颜色条，放在右侧
  )
  ```

#### 3. 文本与刻度优化
- 热力图标注（annot=True）时，若文字重叠，调整 `annot_kws={"fontsize": 8}` 缩小字体
- 分类图（如箱线图、小提琴图）的 x 轴标签过长时，旋转刻度：`plt.xticks(rotation=45, ha="right")`

### 三、Plotly 专属防重叠规则（交互式图表，独立配置）
#### 1. 全局布局（必加）
- 所有 Plotly 图表（px 或 go），必须添加 `update_layout` 配置，调整边距和元素位置：
  ```python
  fig.update_layout(
      margin=dict(l=50, r=150, t=50, b=50),  # 上下左右留白，避免元素贴边
      tight_layout=True,  # 自动调整元素间距
      width=1000, height=600  # 合理设置图表尺寸，避免拥挤
  )
  ```

#### 2. 图例防重叠
- 图例默认放在**右侧轴外**，避免遮挡数据：
  ```python
  fig.update_layout(
      legend=dict(
          x=1.02,  # 图例x坐标（轴外右侧）
          y=1,     # 图例y坐标（顶部对齐）
          orientation="v",  # 纵向排列
          title_font=dict(size=12),
          font=dict(size=10)
      )
  )
  ```
- 图例过多时，设置 `legend_traceorder="normal"`，并调整 `x` 坐标，避免超出图表范围
- 禁止将图例放在 `x=0.5, y=0.5`（中心）等易重叠位置

#### 3. 标题与坐标轴防重叠
- 标题与轴标签调整间距，避免与刻度、图例重叠：
  ```python
  fig.update_layout(
      title=dict(
          text="图表标题",
          font=dict(size=14),
          pad=dict(t=12, b=10)  # 标题上下间距
      ),
      xaxis=dict(
          title="X轴标签",
          title_font=dict(size=12),
          title_pad=8,  # 轴标签与刻度间距
          tickangle=45  # 刻度旋转，避免重叠
      ),
      yaxis=dict(
          title="Y轴标签",
          title_font=dict(size=12),
          title_pad=8
      )
  )
  ```
- 3D 图需额外调整视角，避免坐标轴、标题与图形重叠：`fig.update_layout(scene_camera=dict(eye=dict(x=1.2, y=1.2, z=0.8)))`

#### 4. 文本标注（annotations）防重叠
- Plotly 标注需设置 `xref="x", yref="y"`，并调整 `xanchor`/`yanchor` 避免重叠：
  ```python
  fig.add_annotation(
      x=x0, y=y0, text="标注内容",
      xanchor="left", yanchor="top",  # 标注锚点，避免遮挡
      bbox=dict(boxstyle="round,pad=0.3", fc="white", alpha=0.8),
      font=dict(size=9)
  )
  ```
- 多个标注时，使用 `annotation_textangle` 调整角度，或分散放置，禁止重叠

#### 5. 多子图（subplots）防重叠
- 使用 Plotly 多子图时，设置 `subplot_titles` 并调整子图间距：
  ```python
  from plotly.subplots import make_subplots

  fig = make_subplots(rows=2, cols=1, subplot_titles=("子图1", "子图2"))
  fig.update_layout(
      vertical_spacing=0.2,  # 子图垂直间距
      horizontal_spacing=0.1, # 子图水平间距
      title_text="多子图标题",
      title_x=0.5  # 总标题居中
  )
  ```

## 示例（三大库分别示例，必须遵循）

### 示例1：Matplotlib 单图（折线图）
```python
import matplotlib.pyplot as plt
import numpy as np

x = np.linspace(0, 10, 100)
y1, y2 = np.sin(x), np.cos(x)

fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(x, y1, label="sin(x)", linewidth=2)
ax.plot(x, y2, label="cos(x)", linewidth=2)

# 标题与轴标签（带间距）
ax.set_title("Matplotlib 三角函数对比", fontsize=14, pad=12)
ax.set_xlabel("X轴", fontsize=12, pad=8)
ax.set_ylabel("Y轴", fontsize=12, pad=8)

# 图例外置，防重叠
ax.legend(
    loc="upper left",
    bbox_to_anchor=(1.02, 1),
    borderaxespad=0,
    fontsize=10
)

# 刻度旋转，避免重叠
ax.tick_params(axis="x", rotation=30, labelsize=10)

# 核心防重叠配置
plt.tight_layout()
plt.savefig("matplotlib_plot.png", dpi=300, bbox_inches="tight")
plt.show()
```

### 示例2：Seaborn 热力图（多元素防重叠）
```python
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

# 生成模拟数据
data = np.random.rand(10, 10)
labels = [f"类别{i}" for i in range(10)]

# 绘制热力图
plt.figure(figsize=(10, 8))
ax = sns.heatmap(
    data, annot=True, cmap="Blues",
    xticklabels=labels, yticklabels=labels,
    cbar_kws={"shrink": 0.8, "location": "right"}  # 颜色条调整
)

# 标题与标签
ax.set_title("Seaborn 热力图（防重叠）", fontsize=14, pad=12)
ax.set_xlabel("X轴类别", fontsize=12, pad=8)
ax.set_ylabel("Y轴类别", fontsize=12, pad=8)

# 刻度旋转，避免标签重叠
plt.xticks(rotation=45, ha="right")

# Seaborn 专属防重叠配置
sns.despine()
plt.tight_layout()
plt.savefig("seaborn_heatmap.png", dpi=300, bbox_inches="tight")
plt.show()
```

### 示例3：Plotly 交互式多子图
```python
import plotly.express as px
import plotly.subplots as sp
import plotly.graph_objects as go
import pandas as pd

# 生成模拟数据
df = pd.DataFrame({
    "x": np.linspace(0, 10, 100),
    "y1": np.sin(np.linspace(0, 10, 100)),
    "y2": np.cos(np.linspace(0, 10, 100)),
    "category": np.repeat(["A", "B"], 50)
})

# 创建多子图
fig = sp.make_subplots(rows=2, cols=1, subplot_titles=("子图1：sin(x)", "子图2：cos(x)"))

# 添加子图内容
fig.add_trace(go.Scatter(x=df["x"], y=df["y1"], name="sin(x)"), row=1, col=1)
fig.add_trace(go.Scatter(x=df["x"], y=df["y2"], name="cos(x)"), row=2, col=1)

# Plotly 专属防重叠配置
fig.update_layout(
    margin=dict(l=50, r=150, t=50, b=50),
    tight_layout=True,
    width=1000, height=800,
    title=dict(text="Plotly 多子图（防重叠）", fontsize=16, pad=dict(t=12)),
    legend=dict(x=1.02, y=1, font=dict(size=10)),
    vertical_spacing=0.2  # 子图垂直间距
)

# 轴标签与刻度调整
fig.update_xaxes(title="X轴", title_pad=8, tickangle=45, row=1, col=1)
fig.update_xaxes(title="X轴", title_pad=8, tickangle=45, row=2, col=1)
fig.update_yaxes(title="Y轴", title_pad=8, row=1, col=1)
fig.update_yaxes(title="Y轴", title_pad=8, row=2, col=1)

fig.write_image("plotly_subplots.png", scale=3)
fig.show()
```

## 禁止行为（违反即报错）
### 通用禁止行为
- ❌ 禁止省略各库对应的核心防重叠配置（如 Matplotlib 的 `plt.tight_layout()`、Seaborn 的 `sns.despine()`、Plotly 的 `update_layout`）
- ❌ 禁止图例放在绘图区中心、上部等易重叠位置
- ❌ 禁止标题、轴标签无 `pad` 间距（或 Plotly 无 `title_pad`）
- ❌ 禁止文本标注无背景、无避让，导致与其他元素重叠
- ❌ 禁止多子图不设置间距，导致子图、元素相互遮挡

### 各库专属禁止行为
#### Matplotlib 禁止
- ❌ 禁止保存图片时省略 `bbox_inches="tight"`，导致图例/标题被截断
- ❌ 禁止多子图仅用 `plt.subplots_adjust()` 而不使用 `tight_layout()`
- ❌ 禁止刻度标签拥挤时不旋转、不精简

#### Seaborn 禁止
- ❌ 禁止 Seaborn 绘图后不添加 `sns.despine()` 和 `plt.tight_layout()`
- ❌ 禁止热力图 `cbar` 不调整，导致与坐标轴重叠
- ❌ 禁止 `FacetGrid` 不设置 `tight_layout=True`

#### Plotly 禁止
- ❌ 禁止 Plotly 图表不添加 `update_layout` 配置
- ❌ 禁止 3D 图不调整视角，导致元素重叠
- ❌ 禁止多子图不设置 `vertical_spacing`/`horizontal_spacing`