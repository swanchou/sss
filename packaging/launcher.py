import sys
import os
import socket
import time
import threading
import webbrowser

def get_base_path():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0

def wait_for_port(port, timeout=15):
    start = time.time()
    while time.time() - start < timeout:
        if is_port_in_use(port):
            return True
        time.sleep(0.3)
    return False

def run_server():
    base_path = get_base_path()
    if base_path not in sys.path:
        sys.path.insert(0, base_path)
    os.chdir(base_path)
    import server
    server.app.run(host='127.0.0.1', port=5001, debug=False)

class App:
    def __init__(self):
        self.base_path = get_base_path()
        self.server_thread = None
        self.running = False

        try:
            import tkinter as tk
            from tkinter import ttk

            self.root = tk.Tk()
            self.root.title('Excel 识别工具')
            self.root.geometry('420x280')
            self.root.resizable(False, False)

            icon_path = os.path.join(self.base_path, 'app_icon.ico')
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)

            self.root.protocol('WM_DELETE_WINDOW', self.on_close)

            main_frame = ttk.Frame(self.root, padding=20)
            main_frame.pack(fill=tk.BOTH, expand=True)

            title_label = ttk.Label(main_frame, text='Excel 识别工具', font=('Microsoft YaHei UI', 16, 'bold'))
            title_label.pack(pady=(0, 5))

            subtitle_label = ttk.Label(main_frame, text='手机号 · SN 自动识别', font=('Microsoft YaHei UI', 10))
            subtitle_label.pack(pady=(0, 20))

            self.status_var = tk.StringVar(value='就绪 - 点击启动按钮开始')
            status_label = ttk.Label(main_frame, textvariable=self.status_var, font=('Microsoft YaHei UI', 9))
            status_label.pack(pady=(0, 15))

            btn_frame = ttk.Frame(main_frame)
            btn_frame.pack(fill=tk.X, pady=10)

            self.start_btn = ttk.Button(btn_frame, text='启动服务', command=self.start_service, width=15)
            self.start_btn.pack(side=tk.LEFT, padx=5)

            self.stop_btn = ttk.Button(btn_frame, text='停止服务', command=self.stop_service, width=15, state=tk.DISABLED)
            self.stop_btn.pack(side=tk.LEFT, padx=5)

            self.open_btn = ttk.Button(btn_frame, text='打开浏览器', command=self.open_browser, width=15, state=tk.DISABLED)
            self.open_btn.pack(side=tk.LEFT, padx=5)

            info_frame = ttk.LabelFrame(main_frame, text='信息', padding=10)
            info_frame.pack(fill=tk.X, pady=(15, 0))

            ttk.Label(info_frame, text='后端地址: http://127.0.0.1:5001', font=('Consolas', 9)).pack(anchor=tk.W)
            ttk.Label(info_frame, text='前端地址: http://127.0.0.1:5001', font=('Consolas', 9)).pack(anchor=tk.W)

        except Exception as e:
            print(f'GUI initialization error: {e}')
            self.start_service_headless()

    def start_service_headless(self):
        self.start_backend()
        if wait_for_port(5001):
            webbrowser.open('http://127.0.0.1:5001')
            print('服务已启动，浏览器已打开')
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                pass

    def start_backend(self):
        if is_port_in_use(5001):
            if hasattr(self, 'status_var'):
                self.status_var.set('端口 5001 已被占用')
                if hasattr(self, 'root'):
                    self.root.update()

        self.server_thread = threading.Thread(target=run_server, daemon=True)
        self.server_thread.start()
        self.running = True

    def start_service(self):
        self.start_btn.config(state='disabled')
        self.status_var.set('正在启动后端服务...')
        self.root.update()

        def do_start():
            try:
                self.start_backend()

                if wait_for_port(5001):
                    self.status_var.set('服务运行中 - http://127.0.0.1:5001')
                    self.stop_btn.config(state='normal')
                    self.open_btn.config(state='normal')

                    self.root.after(500, self.open_browser)
                else:
                    self.status_var.set('启动超时，请检查端口是否被占用')
                    self.start_btn.config(state='normal')
            except Exception as e:
                self.status_var.set(f'启动失败: {e}')
                self.start_btn.config(state='normal')

        threading.Thread(target=do_start, daemon=True).start()

    def stop_service(self):
        self.status_var.set('服务已停止（关闭窗口退出）')
        self.running = False
        self.start_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
        self.open_btn.config(state='disabled')

    def open_browser(self):
        webbrowser.open('http://127.0.0.1:5001')

    def on_close(self):
        if hasattr(self, 'root'):
            self.root.destroy()

    def run(self):
        if hasattr(self, 'root'):
            self.root.mainloop()


def main():
    app = App()
    app.run()


if __name__ == '__main__':
    main()