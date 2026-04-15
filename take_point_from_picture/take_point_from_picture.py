import pygame
from PIL import Image
import tkinter as tk
from tkinter import filedialog, simpledialog
import numpy as np
import pandas as pd
import math

# 全局变量
FPS = 60
WIDTH, HEIGHT = 1500, 1000  # 窗口尺寸
PLOT_WIDTH, PLOT_HEIGHT = 1200, 800  # 新窗口绘图区域（80%）
screen = None
image_surface = None
points = {"x_min": None, "x_max": None, "y_min": None, "y_max": None}
values = {"x_min": None, "x_max": None, "y_min": None, "y_max": None}
discrete_points = []  # 存储离散点（像素坐标）
discrete_values = []  # 存储离散点的值
discrete_count = 0
current_discrete_index = 0
current_selection = "x_min"
font = None
running = True
input_x_done = False
input_y_done = False
input_discrete_done = False
scale_x = None
scale_y = None
interp_data = []  # 存储插值数据


def select_image_path():
    """使用tkinter选择图片路径"""
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(
        title="Select Image File",
        filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.gif")]
    )
    root.destroy()
    return file_path


def get_user_input(prompt, input_type="float"):
    """使用tkinter获取用户输入"""
    root = tk.Tk()
    root.withdraw()
    if input_type == "float":
        value = simpledialog.askfloat("Input", prompt, parent=root)
    else:
        value = simpledialog.askinteger("Input", prompt, parent=root)
    root.destroy()
    return value


def save_to_csv(interp_data):
    """使用tkinter另存为对话框保存插值数据到CSV"""
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.asksaveasfilename(
        title="Save Interpolation Data",
        defaultextension=".csv",
        filetypes=[("CSV files", "*.csv")]
    )
    root.destroy()
    if file_path:
        df = pd.DataFrame(interp_data, columns=["x", "y"])
        df.to_csv(file_path, index=False)
        print(f"Interpolation data saved to {file_path}")
    else:
        print("No file selected for saving CSV.")


def load_image(file_path):
    """加载图片并缩放铺满窗口"""
    try:
        pil_image = Image.open(file_path)
        pil_image = pil_image.convert("RGB")
        img_width, img_height = pil_image.size
        scale = max(WIDTH / img_width, HEIGHT / img_height)
        new_size = (int(img_width * scale), int(img_height * scale))
        pil_image = pil_image.resize(new_size, Image.Resampling.LANCZOS)
        mode = pil_image.mode
        size = pil_image.size
        data = pil_image.tobytes()
        return pygame.image.fromstring(data, size, mode)
    except Exception as e:
        print(f"Error loading image: {e}")
        return pygame.Surface((WIDTH, HEIGHT))


def setup(image_path):
    """初始化Pygame和窗口"""
    global screen, image_surface, font
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Image Boundary Selector")
    image_surface = load_image(image_path)
    font = pygame.font.Font(None, 36)
    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_CROSSHAIR)


def calculate_scales():
    """计算x和y方向比例尺"""
    global scale_x, scale_y
    if points["x_min"] and points["x_max"] and values["x_min"] is not None and values["x_max"] is not None:
        scale_x = (values["x_max"] - values["x_min"]) / (points["x_max"][0] - points["x_min"][0])
    if points["y_min"] and points["y_max"] and values["y_min"] is not None and values["y_max"] is not None:
        scale_y = (values["y_max"] - values["y_min"]) / (points["y_min"][1] - points["y_max"][1])


def pixel_to_value(pixel_x, pixel_y):
    """像素坐标转换为值"""
    if scale_x is None or scale_y is None:
        return None, None
    vx = values["x_min"] + (pixel_x - points["x_min"][0]) * scale_x
    vy = values["y_min"] + (points["y_min"][1] - pixel_y) * scale_y
    return vx, vy


def interpolate_discrete_points():
    """对离散点进行线性插值"""
    if not discrete_values:
        return []

    # 提取x和y值
    x_vals = [v[0] for v in discrete_values]
    y_vals = [v[1] for v in discrete_values]

    # 对x值进行排序
    sorted_indices = np.argsort(x_vals)
    sorted_x = np.array(x_vals)[sorted_indices]
    sorted_y = np.array(y_vals)[sorted_indices]

    # 计算插值范围：大于第一个点的最小整数到小于最后一个点的最大整数
    x_min_val = math.ceil(sorted_x[0])
    x_max_val = math.floor(sorted_x[-1])

    if x_min_val > x_max_val:
        return []

    # 生成插值点
    x_interp = np.arange(x_min_val, x_max_val + 1, 1)
    y_interp = np.interp(x_interp, sorted_x, sorted_y)

    return list(zip(x_interp, y_interp))


def draw():
    """绘制图片、点、连接线和提示信息"""
    screen.fill((255, 255, 255))
    image_rect = image_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    screen.blit(image_surface, image_rect)

    for key, point in points.items():
        if point:
            color = (255, 0, 0) if key.startswith("x") else (0, 0, 255)
            pygame.draw.circle(screen, color, point, 5)
            label = font.render(f"{key}: {values[key]}", True, color)
            screen.blit(label, (point[0] + 10, point[1] - 10))

    if points["x_min"] and points["x_max"]:
        pygame.draw.line(screen, (255, 0, 0), points["x_min"], points["x_max"], 2)
    if points["y_min"] and points["y_max"]:
        pygame.draw.line(screen, (0, 0, 255), points["y_min"], points["y_max"], 2)

    for i, point in enumerate(discrete_points):
        pygame.draw.circle(screen, (0, 255, 0), point, 5)
        label = font.render(f"P{i + 1}", True, (0, 255, 0))
        screen.blit(label, (point[0] + 10, point[1] - 10))
        if i > 0:
            pygame.draw.line(screen, (0, 255, 0), discrete_points[i - 1], point, 2)

    instruction = f"Click to set {current_selection.replace('_', ' ')}"
    if current_selection.startswith("discrete"):
        instruction = f"Click to set discrete point {current_discrete_index + 1}/{discrete_count}"
    text = font.render(instruction, True, (0, 0, 0))
    screen.blit(text, (10, 10))

    pygame.display.flip()


def draw_new_figure():
    """在新窗口中绘制离散点和网格，占据80%窗口"""
    global interp_data
    new_screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Discrete Points with Grid")

    x_range = values["x_max"] - values["x_min"]
    y_range = values["y_max"] - values["y_min"]

    margin_x = (WIDTH - PLOT_WIDTH) // 2  # 水平边距
    margin_y = (HEIGHT - PLOT_HEIGHT) // 2  # 垂直边距
    x_scale = PLOT_WIDTH / x_range
    y_scale = PLOT_HEIGHT / y_range

    # 线性插值
    interp_data = interpolate_discrete_points()

    # 创建新的Pygame表面
    plot_surface = pygame.Surface((WIDTH, HEIGHT))
    plot_surface.fill((255, 255, 255))

    # 绘制网格
    grid_color = (200, 200, 200)
    num_grid_x = 10
    num_grid_y = 10
    for i in range(num_grid_x + 1):
        x_val = values["x_min"] + (i / num_grid_x) * x_range
        x_pixel = margin_x + i * (PLOT_WIDTH / num_grid_x)
        pygame.draw.line(plot_surface, grid_color, (x_pixel, margin_y), (x_pixel, margin_y + PLOT_HEIGHT), 1)
        label = font.render(f"{x_val:.2f}", True, (0, 0, 0))
        plot_surface.blit(label, (x_pixel - 20, margin_y + PLOT_HEIGHT + 10))
    for i in range(num_grid_y + 1):
        y_val = values["y_min"] + (i / num_grid_y) * y_range
        y_pixel = margin_y + PLOT_HEIGHT - i * (PLOT_HEIGHT / num_grid_y)
        pygame.draw.line(plot_surface, grid_color, (margin_x, y_pixel), (margin_x + PLOT_WIDTH, y_pixel), 1)
        label = font.render(f"{y_val:.2f}", True, (0, 0, 0))
        plot_surface.blit(label, (margin_x - 50, y_pixel - 10))

    # 绘制坐标轴标签
    x_label = font.render("X Axis", True, (0, 0, 0))
    plot_surface.blit(x_label, (WIDTH // 2 - 50, HEIGHT - 30))
    y_label = font.render("Y Axis", True, (0, 0, 0))
    plot_surface.blit(y_label, (10, HEIGHT // 2 - 50))

    # 绘制离散点
    pixel_points = []
    for i, (vx, vy) in enumerate(discrete_values):
        px = margin_x + (vx - values["x_min"]) * x_scale
        py = margin_y + PLOT_HEIGHT - (vy - values["y_min"]) * y_scale
        pixel_points.append((px, py))
        pygame.draw.circle(plot_surface, (0, 0, 255), (px, py), 8)  # 蓝色点表示原始离散点
        label = font.render(f"P{i + 1} ({vx:.2f}, {vy:.2f})", True, (0, 0, 255))
        plot_surface.blit(label, (px + 10, py - 10))

    # 绘制原始离散点连线（按点击顺序）
    for i in range(1, len(pixel_points)):
        pygame.draw.line(plot_surface, (0, 0, 255), pixel_points[i - 1], pixel_points[i], 3)

    # 绘制插值点
    if interp_data:
        interp_pixel_points = []
        for x, y in interp_data:
            px = margin_x + (x - values["x_min"]) * x_scale
            py = margin_y + PLOT_HEIGHT - (y - values["y_min"]) * y_scale
            interp_pixel_points.append((px, py))

        # 绘制插值曲线（红色）
        for i in range(1, len(interp_pixel_points)):
            pygame.draw.line(plot_surface, (255, 0, 0), interp_pixel_points[i - 1], interp_pixel_points[i], 2)

    # 绘制图例
    pygame.draw.line(plot_surface, (0, 0, 255), (WIDTH - 250, 30), (WIDTH - 200, 30), 3)
    plot_surface.blit(font.render("Original Points", True, (0, 0, 255)), (WIDTH - 190, 25))

    if interp_data:
        pygame.draw.line(plot_surface, (255, 0, 0), (WIDTH - 250, 60), (WIDTH - 200, 60), 2)
        plot_surface.blit(font.render("Interpolation", True, (255, 0, 0)), (WIDTH - 190, 55))

    # 绘制标题
    title = font.render("Discrete Points and Linear Interpolation", True, (0, 0, 0))
    plot_surface.blit(title, (WIDTH // 2 - title.get_width() // 2, 10))

    # 显示绘图
    new_screen.blit(plot_surface, (0, 0))
    pygame.display.flip()

    # 等待用户关闭窗口
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                waiting = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    waiting = False

    # 用户关闭窗口后保存CSV
    if interp_data:
        save_to_csv(interp_data)


def handle_events():
    """处理用户输入"""
    global current_selection, running, input_x_done, input_y_done, input_discrete_done, current_discrete_index, discrete_values
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if not input_x_done and current_selection in ["x_min", "x_max"]:
                return
            if not input_y_done and current_selection in ["y_min", "y_max"]:
                return
            if not input_discrete_done and current_selection.startswith("discrete"):
                return
            pos = event.pos
            if current_selection.startswith("discrete"):
                discrete_points.append(pos)
                vx, vy = pixel_to_value(pos[0], pos[1])
                discrete_values.append((vx, vy))
                current_discrete_index += 1
                if current_discrete_index >= discrete_count:
                    print("Selected points, values, and discrete points:", points, values, discrete_values)
                    running = False
                    draw_new_figure()
                else:
                    current_selection = f"discrete_{current_discrete_index + 1}"
            else:
                points[current_selection] = pos
                if current_selection == "x_max" or current_selection == "y_max":
                    calculate_scales()
                if current_selection == "x_min":
                    current_selection = "x_max"
                elif current_selection == "x_max":
                    current_selection = "y_min"
                elif current_selection == "y_min":
                    current_selection = "y_max"
                elif current_selection == "y_max":
                    current_selection = "discrete_1"
                    current_discrete_index = 0


def main():
    """主循环"""
    image_path = select_image_path()
    if not image_path:
        print("No image selected. Exiting...")
        return

    setup(image_path)

    global running, input_x_done, input_y_done, input_discrete_done, discrete_count
    clock = pygame.time.Clock()

    draw()
    pygame.display.flip()

    values["x_min"] = get_user_input("Enter value for x_min:")
    if values["x_min"] is None:
        print("No x_min value provided. Exiting...")
        return
    values["x_max"] = get_user_input("Enter value for x_max:")
    if values["x_max"] is None:
        print("No x_max value provided. Exiting...")
        return
    input_x_done = True

    while running:
        handle_events()
        draw()

        if current_selection == "y_min" and not input_y_done:
            values["y_min"] = get_user_input("Enter value for y_min:")
            if values["y_min"] is None:
                print("No y_min value provided. Exiting...")
                running = False
                break
            values["y_max"] = get_user_input("Enter value for y_max:")
            if values["y_max"] is None:
                print("No y_max value provided. Exiting...")
                running = False
                break
            input_y_done = True

        if current_selection == "discrete_1" and not input_discrete_done:
            discrete_count = get_user_input("Enter number of discrete points:", input_type="int")
            if discrete_count is None or discrete_count <= 0:
                print("Invalid or no discrete point count provided. Exiting...")
                running = False
                break
            input_discrete_done = True

        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()