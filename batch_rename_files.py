import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox

def select_folder():
    root = tk.Tk()
    root.withdraw()
    folder_path = filedialog.askdirectory(title="选择包含需要重命名文件的文件夹")
    return folder_path

def rename_files(folder_path=None):
    if not folder_path:
        folder_path = select_folder()
    
    if not folder_path:
        print("未选择文件夹")
        return
    
    files = [f for f in os.listdir(folder_path) if f.endswith('.txt')]
    if not files:
        print("文件夹中没有.txt文件")
        messagebox.showinfo("提示", "文件夹中没有.txt文件")
        return
    
    renamed_count = 0
    error_count = 0
    
    for file in files:
        try:
            if '-' in file:
                # 获取最后一个"-"后面的部分
                new_name = file.split('-')[-1]
                
                old_path = os.path.join(folder_path, file)
                new_path = os.path.join(folder_path, new_name)
                
                # 如果新文件名已存在，跳过
                if os.path.exists(new_path) and old_path != new_path:
                    print(f"文件已存在，跳过: {new_name}")
                    error_count += 1
                    continue
                
                # 重命名文件
                os.rename(old_path, new_path)
                print(f"重命名: {file} -> {new_name}")
                renamed_count += 1
            else:
                print(f"文件名中没有'-'，跳过: {file}")
        except Exception as e:
            print(f"重命名失败 {file}: {e}")
            error_count += 1
    
    print(f"\n重命名完成！")
    print(f"成功重命名: {renamed_count} 个文件")
    print(f"失败/跳过: {error_count} 个文件")
    
    messagebox.showinfo("完成", f"重命名完成！\n成功: {renamed_count} 个文件\n失败/跳过: {error_count} 个文件")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # 从命令行获取文件夹路径
        rename_files(sys.argv[1])
    else:
        # 使用GUI选择文件夹
        rename_files()
