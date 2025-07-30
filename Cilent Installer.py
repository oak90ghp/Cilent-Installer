import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import subprocess
import os
import sys
import re
from threading import Thread
import shutil

class PyInstallerGUI:    
    def __init__(self, root):
        self.root = root
        self.root.title("Cilent Installer")
        self.root.geometry("1000x900")
        self.root.resizable(True, True)

        # 设置中文字体支持
        self.font_config = ('SimHei', 10)
        self.bold_font = ('SimHei', 10, 'bold')

        # 存储用户选择的文件
        self.selected_file = tk.StringVar()
        # 存储pyinstaller参数
        self.pyinstaller_args = {
            'hidden_console': tk.BooleanVar(value=True),
            'onefile': tk.BooleanVar(value=True),
            'name': tk.StringVar(),
            'icon': tk.StringVar(),
            'paths': tk.StringVar(),
            'hidden_imports': tk.StringVar(),
            'excludes': tk.StringVar(),
            'additional_args': tk.StringVar()
        }

        # 创建主界面
        self.create_widgets()

    def create_widgets(self):
        # 创建样式对象
        style = ttk.Style()
        style.configure('TLabel', font=self.font_config)
        style.configure('TCheckbutton', font=self.font_config)
        style.configure('TEntry', font=self.font_config)
        style.configure('TBold.TLabel', font=self.bold_font)

        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 文件选择区域
        file_frame = ttk.LabelFrame(main_frame, text="文件选择", padding="10")
        file_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(file_frame, text="Python源代码文件:", style='TLabel').grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(file_frame, textvariable=self.selected_file, width=60, style='TEntry').grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(file_frame, text="浏览...", command=self.browse_file, width=10).grid(row=0, column=2, padx=5, pady=5)

        # 参数配置区域
        params_frame = ttk.LabelFrame(main_frame, text="PyInstaller参数配置", padding="10")
        params_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # 创建标签页
        notebook = ttk.Notebook(params_frame)
        notebook.pack(fill=tk.BOTH, expand=True)

        # 基本选项标签页
        basic_frame = ttk.Frame(notebook, padding="10")
        notebook.add(basic_frame, text="基本选项")

        # 高级选项标签页
        advanced_frame = ttk.Frame(notebook, padding="10")
        notebook.add(advanced_frame, text="高级选项")

        # 基本选项
        row = 0
        ttk.Label(basic_frame, text="基本设置", style='TBold.TLabel').grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))
        row += 1

        # 隐藏命令行窗口
        ttk.Checkbutton(basic_frame, text="隐藏命令行窗口 (-w)", variable=self.pyinstaller_args['hidden_console'], style='TCheckbutton').grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=2)
        row += 1

        # 单一文件模式
        ttk.Checkbutton(basic_frame, text="单一文件模式 (-F)", variable=self.pyinstaller_args['onefile'], style='TCheckbutton').grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=2)
        row += 1

        # 应用程序名称
        ttk.Label(basic_frame, text="应用程序名称 (-n):", style='TLabel').grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(basic_frame, textvariable=self.pyinstaller_args['name'], width=40, style='TEntry').grid(row=row, column=1, sticky=tk.W, padx=5, pady=5)
        row += 1

        # 图标文件
        ttk.Label(basic_frame, text="图标文件 (-i):", style='TLabel').grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        icon_frame = ttk.Frame(basic_frame)
        icon_frame.grid(row=row, column=1, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(icon_frame, textvariable=self.pyinstaller_args['icon'], width=30, style='TEntry').pack(side=tk.LEFT)
        ttk.Button(icon_frame, text="浏览...", command=self.browse_icon, width=8).pack(side=tk.LEFT, padx=5)
        row += 1

        # 高级选项
        row = 0
        ttk.Label(advanced_frame, text="高级设置", style='TBold.TLabel').grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))
        row += 1

        # 路径设置
        ttk.Label(advanced_frame, text="额外路径 (-p):", style='TLabel').grid(row=row, column=0, sticky=tk.NW, padx=5, pady=5)
        path_frame = ttk.Frame(advanced_frame)
        path_frame.grid(row=row, column=1, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(path_frame, textvariable=self.pyinstaller_args['paths'], width=30, style='TEntry').pack(side=tk.LEFT)
        ttk.Button(path_frame, text="浏览...", command=self.browse_path, width=8).pack(side=tk.LEFT, padx=5)
        ttk.Label(advanced_frame, text="多个路径用分号分隔", style='TLabel').grid(row=row+1, column=1, sticky=tk.W, padx=5)
        row += 2

        # 隐藏导入
        ttk.Label(advanced_frame, text="隐藏导入 (-h):", style='TLabel').grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(advanced_frame, textvariable=self.pyinstaller_args['hidden_imports'], width=40, style='TEntry').grid(row=row, column=1, sticky=tk.W, padx=5, pady=5)
        ttk.Label(advanced_frame, text="多个模块用逗号分隔", style='TLabel').grid(row=row+1, column=1, sticky=tk.W, padx=5)
        row += 2

        # 排除模块
        ttk.Label(advanced_frame, text="排除模块 (-x):", style='TLabel').grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(advanced_frame, textvariable=self.pyinstaller_args['excludes'], width=40, style='TEntry').grid(row=row, column=1, sticky=tk.W, padx=5, pady=5)
        ttk.Label(advanced_frame, text="多个模块用逗号分隔", style='TLabel').grid(row=row+1, column=1, sticky=tk.W, padx=5)
        row += 2

        # 附加参数
        ttk.Label(advanced_frame, text="附加参数:", style='TLabel').grid(row=row, column=0, sticky=tk.NW, padx=5, pady=5)
        ttk.Entry(advanced_frame, textvariable=self.pyinstaller_args['additional_args'], width=50, style='TEntry').grid(row=row, column=1, sticky=tk.W, padx=5, pady=5)
        ttk.Label(advanced_frame, text="直接输入pyinstaller参数，如: --version-file version.txt", style='TLabel').grid(row=row+1, column=1, sticky=tk.W, padx=5)
        row += 2

        # 输出区域
        output_frame = ttk.LabelFrame(main_frame, text="输出日志", padding="10")
        output_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        self.output_text = scrolledtext.ScrolledText(output_frame, wrap=tk.WORD, width=80, height=15, font=('Consolas', 9))
        self.output_text.pack(fill=tk.BOTH, expand=True)
        self.output_text.config(state=tk.DISABLED)

        # 按钮区域
        button_frame = ttk.Frame(main_frame, padding="10")
        button_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Button(button_frame, text="开始打包", command=self.start_packaging, width=15).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="清除日志", command=self.clear_log, width=10).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="退出", command=self.root.quit, width=8).pack(side=tk.RIGHT, padx=5)

    def browse_file(self):
        filename = filedialog.askopenfilename(
            filetypes=[("Python源代码文件", "*.py"), ("任意文件", "*.*")]
        )
        if filename:
            self.selected_file.set(filename)
            # 自动填充应用名称
            if not self.pyinstaller_args['name'].get():
                self.pyinstaller_args['name'].set(os.path.splitext(os.path.basename(filename))[0])

    def browse_icon(self):
        iconfile = filedialog.askopenfilename(
            filetypes=[("Python源代码文件", "*.py"), ("任意文件", "*.*")]
        )
        if iconfile:
            self.pyinstaller_args['icon'].set(iconfile)

    def browse_path(self):
        path = filedialog.askdirectory()
        if path:
            current_paths = self.pyinstaller_args['paths'].get()
            if current_paths:
                self.pyinstaller_args['paths'].set(f"{current_paths};{path}")
            else:
                self.pyinstaller_args['paths'].set(path)

    def log(self, message):
        self.output_text.config(state=tk.NORMAL)
        self.output_text.insert(tk.END, message + '\n')
        self.output_text.see(tk.END)
        self.output_text.config(state=tk.DISABLED)

    def clear_log(self):
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete(1.0, tk.END)
        self.output_text.config(state=tk.DISABLED)

    def build_command(self):
        """构建pyinstaller命令"""
        cmd = ['pyinstaller']

        # 基本参数
        if self.pyinstaller_args['hidden_console'].get():
            cmd.append('-w')
        if self.pyinstaller_args['onefile'].get():
            cmd.append('-F')

        # 应用名称
        name = self.pyinstaller_args['name'].get()
        if name:
            cmd.extend(['-n', name])

        # 图标
        icon = self.pyinstaller_args['icon'].get()
        if icon and os.path.exists(icon):
            cmd.extend(['-i', icon])

        # 路径设置
        paths = self.pyinstaller_args['paths'].get()
        if paths:
            for path in paths.split(';'):
                if path and os.path.exists(path):
                    cmd.extend(['-p', path.strip()])

        # 隐藏导入
        hidden_imports = self.pyinstaller_args['hidden_imports'].get()
        if hidden_imports:
            for imp in hidden_imports.split(','):
                if imp.strip():
                    cmd.extend(['--hidden-import', imp.strip()])

        # 排除模块
        excludes = self.pyinstaller_args['excludes'].get()
        if excludes:
            for exc in excludes.split(','):
                if exc.strip():
                    cmd.extend(['--exclude-module', exc.strip()])

        # 附加参数
        additional_args = self.pyinstaller_args['additional_args'].get()
        if additional_args:
            # 使用shlex解析参数，但要处理中文
            import shlex
            try:
                # 处理带引号的参数
                args = shlex.split(additional_args)
                cmd.extend(args)
            except Exception as e:
                self.log(f"解析附加参数时出错: {str(e)}")
                self.log(f"将直接添加附加参数: {additional_args}")
                cmd.extend(additional_args.split())

        # 添加要打包的文件
        if self.selected_file.get():
            cmd.append(self.selected_file.get())

        return cmd

    def run_command(self, cmd):
        """执行命令并捕获输出"""
        self.log(f"执行命令: {' '.join(cmd)}")

        try:
            # 创建进程
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1,
                encoding='utf-8'
            )

            # 实时输出
            for line in process.stdout:
                self.log(line.strip())

            # 等待进程完成
            process.wait()

            if process.returncode == 0:
                self.log("打包成功完成!")
                # 尝试打开输出目录
                dist_dir = os.path.join(os.path.dirname(self.selected_file.get()), 'dist')
                if os.path.exists(dist_dir):
                    self.log(f"输出目录: {dist_dir}")
                    if sys.platform.startswith('win'):
                        os.startfile(dist_dir)
            else:
                self.log(f"打包失败，返回代码: {process.returncode}")

        except Exception as e:
            self.log(f"执行命令时出错: {str(e)}")

    def start_packaging(self):
        """开始打包过程"""
        # 检查是否选择了文件
        if not self.selected_file.get():
            messagebox.showerror("错误", "请选择要打包的Python文件")
            return

        # 检查文件是否存在
        if not os.path.exists(self.selected_file.get()):
            messagebox.showerror("错误", "选择的文件不存在")
            return

        # 检查pyinstaller是否安装
        if shutil.which('pyinstaller') is None:
            if messagebox.askyesno("PyInstaller未找到", "未找到pyinstaller，是否尝试安装?"):
                self.log("正在安装pyinstaller...")
                install_cmd = [sys.executable, '-m', 'pip', 'install', 'pyinstaller']
                self.run_command(install_cmd)
                # 再次检查
                if shutil.which('pyinstaller') is None:
                    messagebox.showerror("安装失败", "pyinstaller安装失败，请手动安装后重试")
                    return

        # 构建命令
        cmd = self.build_command()

        # 在新线程中执行打包，避免界面冻结
        self.log("开始打包...")
        packaging_thread = Thread(target=self.run_command, args=(cmd,))
        packaging_thread.daemon = True
        packaging_thread.start()

if __name__ == "__main__":
    # 确保中文显示正常
    root = tk.Tk()
    app = PyInstallerGUI(root)
    root.mainloop()